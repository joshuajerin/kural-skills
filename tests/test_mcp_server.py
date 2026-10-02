"""MCP contract tests for the dry-run-only server."""
import math
import subprocess
import sys
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import patch

from mcp import types

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from kural_skills.catalog import CATALOG
from kural_skills.mcp_server import (
    CAPABILITIES_TOOL,
    DRY_RUN_PREFIX,
    STOP_TOOL,
    create_server,
    parse_args,
)


@asynccontextmanager
async def connected_session():
    params = StdioServerParameters(command=sys.executable, args=["-m", "kural_skills.mcp_server"])
    async with stdio_client(params) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            yield session


class MCPServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_exact_allowlist_and_catalog_schemas(self):
        async with connected_session() as session:
            listed = await session.list_tools()
            tools = {tool.name: tool for tool in listed.tools}
            expected = {CAPABILITIES_TOOL, STOP_TOOL} | {DRY_RUN_PREFIX + name for name in CATALOG}
            self.assertEqual(set(tools), expected)
            self.assertEqual(len(tools), 20)
            self.assertTrue(tools[CAPABILITIES_TOOL].annotations.readOnlyHint)
            for name in expected - {CAPABILITIES_TOOL}:
                self.assertFalse(tools[name].annotations.readOnlyHint)
                self.assertFalse(tools[name].annotations.destructiveHint)
                self.assertFalse(tools[name].inputSchema["additionalProperties"])
            for skill, definition in CATALOG.items():
                self.assertEqual(tools[DRY_RUN_PREFIX + skill].inputSchema, definition.parameters)

    async def test_capabilities_wave_and_stop_are_truthful(self):
        async with connected_session() as session:
            caps = await session.call_tool(CAPABILITIES_TOOL, {})
            self.assertFalse(caps.isError)
            self.assertEqual(caps.structuredContent["protocol"], "kural.skills.mcp.v1")
            self.assertEqual(caps.structuredContent["version"], "0.1.0")
            self.assertTrue(caps.structuredContent["no_live_backend"])
            self.assertEqual(len(caps.structuredContent["tools"]), 20)
            self.assertEqual(len(caps.structuredContent["skills"]), 18)
            self.assertTrue(caps.structuredContent["limitations"])
            self.assertEqual(caps.structuredContent["mode"], "dry_run")

            wave = await session.call_tool(DRY_RUN_PREFIX + "wave", {"timeout_s": 2})
            self.assertFalse(wave.isError)
            self.assertEqual(wave.structuredContent["mode"], "dry_run")
            self.assertEqual(
                wave.structuredContent["execution"],
                "validated intent only; no robot motion",
            )
            self.assertEqual(set(wave.structuredContent), {"mode", "execution", "result"})
            self.assertEqual(wave.structuredContent["result"]["skill"], "wave")
            self.assertEqual(wave.structuredContent["result"]["state"], "dry_run")
            self.assertFalse(wave.structuredContent["result"]["motion_verified"])
            self.assertIn("No robot motion", wave.content[0].text)

            stop = await session.call_tool(STOP_TOOL, {})
            self.assertFalse(stop.isError)
            self.assertEqual(stop.structuredContent["result"]["skill"], "stop")
            self.assertFalse(stop.structuredContent["result"]["stop_confirmed"])
            self.assertIn("No physical stop", stop.content[0].text)

    async def test_bad_arguments_are_tool_errors_and_server_continues(self):
        async with connected_session() as session:
            extra = await session.call_tool(DRY_RUN_PREFIX + "wave", {"extra": 1})
            self.assertTrue(extra.isError)
            nonfinite = await session.call_tool(DRY_RUN_PREFIX + "wave", {"timeout_s": math.nan})
            self.assertTrue(nonfinite.isError)
            # The valid call after errors demonstrates that argument errors do not
            # terminate the MCP server session.
            valid = await session.call_tool(DRY_RUN_PREFIX + "wave", {})
            self.assertFalse(valid.isError)
            self.assertEqual(valid.structuredContent["result"]["state"], "dry_run")


    async def test_provider_exception_is_an_error_result_and_handler_continues(self):
        server = create_server()
        request = types.CallToolRequest(
            params=types.CallToolRequestParams(name=DRY_RUN_PREFIX + "wave", arguments={})
        )
        handler = server.request_handlers[types.CallToolRequest]
        with patch("kural_skills.mcp_server.KuralSkills.call", side_effect=KeyError("provider deviation")):
            failed = (await handler(request)).root
        self.assertTrue(failed.isError)
        self.assertIn("provider deviation", failed.content[0].text)
        recovered = (await handler(request)).root
        self.assertFalse(recovered.isError)
        self.assertEqual(recovered.structuredContent["result"]["state"], "dry_run")

    async def test_protocol_list_schema_copy_cannot_mutate_catalog(self):
        server = create_server()
        handler = server.request_handlers[types.ListToolsRequest]
        first = (await handler(types.ListToolsRequest())).root.tools
        wave = next(tool for tool in first if tool.name == DRY_RUN_PREFIX + "wave")
        wave.inputSchema["properties"].clear()
        second = (await handler(types.ListToolsRequest())).root.tools
        restored = next(tool for tool in second if tool.name == DRY_RUN_PREFIX + "wave")
        self.assertEqual(set(restored.inputSchema["properties"]), {"timeout_s"})
        self.assertEqual(set(CATALOG["wave"].parameters["properties"]), {"timeout_s"})


class FactoryAndCliTests(unittest.TestCase):
    def test_factory_is_dry_run_only_and_schemas_are_isolated(self):
        first = create_server()
        second = create_server()
        self.assertIsNot(first, second)
        # The listed tool factory must not mutate the catalog schema.
        tools = __import__("kural_skills.mcp_server", fromlist=["_tool_definitions"])._tool_definitions()
        tools[1].inputSchema["properties"].clear()
        self.assertEqual(set(CATALOG["move_forward"].parameters["properties"]), {"duration_s", "speed_m_s"})

    def test_cli_is_argument_free_stdio_and_help_does_not_start_a_listener(self):
        self.assertIsNotNone(parse_args([]))
        for forbidden in (["--backend", "gateway"], ["--transport", "streamable-http"], ["--host", "127.0.0.1"]):
            with self.assertRaises(SystemExit):
                parse_args(forbidden)
        entrypoint = Path(sys.executable).with_name("kural-skills-mcp")
        self.assertTrue(entrypoint.is_file())
        help_result = subprocess.run(
            [str(entrypoint), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("stdio", help_result.stdout)
        self.assertNotIn("streamable-http", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
