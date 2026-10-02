"""Dry-run-only MCP server for the Kural Phase 1 skills over stdio."""
from __future__ import annotations

import argparse
import asyncio
from copy import deepcopy
import json
from typing import Any

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .backends import DryRunBackend
from .catalog import CATALOG
from .sdk import KuralSkills

SERVER_NAME = "kural-skills-dry-run"
CAPABILITIES_TOOL = "kural_capabilities"
STOP_TOOL = "kural_dry_run_stop"
DRY_RUN_PREFIX = "kural_dry_run_"


def _empty_schema() -> dict[str, Any]:
    return {"type": "object", "properties": {}, "additionalProperties": False}


def _action_annotations() -> types.ToolAnnotations:
    # Calls add a record to the in-process dry-run backend, so they are not
    # read-only.  They never affect a robot, simulator, or external system.
    return types.ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    )


def _capabilities_annotations() -> types.ToolAnnotations:
    return types.ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )


def _tool_definitions() -> list[types.Tool]:
    """Build the allowlist from the same catalog used by ``SkillRequest``."""
    tools = [
        types.Tool(
            name=CAPABILITIES_TOOL,
            description="Read the Kural dry-run-only MCP capabilities.",
            inputSchema=_empty_schema(),
            annotations=_capabilities_annotations(),
        )
    ]
    for skill, definition in CATALOG.items():
        # ``definition.parameters`` is the schema consumed by SkillRequest,
        # including the defaults and parameter bounds.  Copy it so the MCP
        # library or a caller cannot alter the catalog.
        schema = deepcopy(definition.parameters)
        schema["additionalProperties"] = False
        tools.append(
            types.Tool(
                name=f"{DRY_RUN_PREFIX}{skill}",
                description=(
                    f"Dry-run only: validate and record the {skill!r} request. "
                    "No robot motion is sent."
                ),
                inputSchema=schema,
                annotations=_action_annotations(),
            )
        )
    tools.append(
        types.Tool(
            name=STOP_TOOL,
            description="Dry-run only: record a stop request. No physical stop is sent.",
            inputSchema=_empty_schema(),
            annotations=_action_annotations(),
        )
    )
    return tools


def _text_result(result: dict[str, Any], *, stop: bool = False) -> types.CallToolResult:
    envelope = {
        "mode": "dry_run",
        "execution": "validated intent only; no robot motion",
        "result": result,
    }
    prefix = "Dry-run only. No robot motion was sent. motion_verified=false."
    if stop:
        prefix = "Dry-run only. No physical stop was sent. motion_verified=false."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"{prefix}\n{json.dumps(envelope, allow_nan=False, sort_keys=True)}")],
        structuredContent=envelope,
        isError=False,
    )


def _error_result(error: Exception) -> types.CallToolResult:
    envelope = {"mode": "dry_run", "error": str(error)}
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Dry-run MCP tool error: {error}")],
        structuredContent=envelope,
        isError=True,
    )


def create_server() -> Server:
    """Create an MCP server with a new, unconditional dry-run backend.

    There is deliberately no backend argument.  This server never accepts a
    backend selection and cannot connect a skill request to a robot.
    """
    robot = KuralSkills(DryRunBackend())
    server = Server(
        SERVER_NAME,
        instructions="This server is dry-run only. It records validated requests and never moves a robot.",
    )
    tools = _tool_definitions()
    action_names = {f"{DRY_RUN_PREFIX}{name}": name for name in CATALOG}

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return deepcopy(tools)

    @server.call_tool(validate_input=True)
    async def call_tool(name: str, arguments: dict[str, Any]) -> types.CallToolResult:
        try:
            # The MCP SDK normally validates this first.  Keep this guard for
            # direct/provider calls that bypass schema validation.
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be an object")
            if name == CAPABILITIES_TOOL:
                if arguments:
                    raise ValueError("kural_capabilities accepts no arguments")
                result = {
                    "protocol": "kural.skills.mcp.v1",
                    "version": "0.1.0",
                    "mode": "dry_run",
                    "no_live_backend": True,
                    "tools": [tool.name for tool in tools],
                    "skills": robot.list_skills(),
                    "limitations": [
                        "Dry-run only; no runtime is connected.",
                        "No robot motion is sent or verified.",
                        "The dry-run stop tool does not send a physical stop.",
                    ],
                }
                return types.CallToolResult(
                    content=[types.TextContent(
                        type="text",
                        text=("Dry-run capabilities only. No robot motion is sent or verified.\n" +
                              json.dumps(result, allow_nan=False, sort_keys=True)),
                    )],
                    structuredContent=result,
                    isError=False,
                )
            if name == STOP_TOOL:
                if arguments:
                    raise ValueError("kural_dry_run_stop accepts no arguments")
                return _text_result(robot.stop().as_dict(), stop=True)
            skill = action_names.get(name)
            if skill is None:
                raise ValueError("Unknown MCP tool")
            # SkillRequest.create, reached through call(), rejects unknown
            # fields, booleans, non-finite values, and invalid bounds.
            return _text_result(robot.call(skill, **arguments).as_dict())
        except Exception as exc:
            # Provider or malformed-input failures are MCP results, not
            # uncaught exceptions that terminate the server session.
            return _error_result(exc)

    # Useful to embedding hosts that need deterministic shutdown.  This is not
    # an alternate backend injection point.
    setattr(server, "close_kural_skills", robot.close)
    return server


async def run_stdio(server: Server | None = None) -> None:
    """Serve MCP over stdio until the client closes the session."""
    server = server or create_server()
    close = getattr(server, "close_kural_skills", None)
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    finally:
        if close is not None:
            close()


def _parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Kural MCP server over stdio. Dry-run only; it never moves a robot."
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the intentionally argument-free stdio entry point."""
    return _parser().parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    parse_args(argv)
    asyncio.run(run_stdio())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
