# Kural dry runs in the dedicated Grok Bot app

This folder targets **Grok Bot**, not Grok Build, grok.com chat, X, or an xAI
API application. It contains saved instructions and a command example. It is
not a registered Bot plugin or a verified Bot package manifest.

The root package supplies the shared genuine MCP adapter:
`kural-skills-mcp`. It defaults to dry run and is **fixed to
DryRunBackend**. No tool, argument, environment variable, saved instruction, or
approval may select a live backend. There is no live-mode switch in this adapter.
It cannot move Kural, observe the room, confirm arrival, or confirm physical stop.

## Files and prerequisites

- [SKILL.md](SKILL.md): saved instruction text for a bounded dry-run workflow.
  A saved skill guides the Bot; it does not install or connect an MCP server.
- [command.example.json](command.example.json): plain command/args example.
  This is **not an assumed Bot manifest schema**, `mcp.json`, or a plugin bundle.
- [Official integration research](../docs/GROK-TOOLS-INTEGRATIONS.md): sources,
  product distinctions, and account-level limits.

The **conversation computer** needs Python 3.11+, a checkout or installation of
this project with the **`mcp` extra**, and the entrypoint on its command PATH.
The project installation command, from that checkout, is:

```sh
uv pip install -e '.[mcp]'
```

Run it in the intended Python environment. For the root project's `.venv`, use
`uv pip install --python .venv/bin/python -e '.[mcp]'` and make that environment's
executables available to the conversation's command runner. Do not perform an
installation, account connection, or deployment without approval. The command
example assumes an already installed entrypoint on PATH; it has no Ubuntu-host
absolute paths and does not copy project source to the conversation computer.

Installing on this Ubuntu machine does **not** connect the Bot's persistent
cloud computer to it. Command mode runs on whichever computer the conversation
uses. Linux local-command execution is not verified by the Bot docs, even though
a Linux Bot app exists. Select and verify the actual computer before setup.

## Exact documented Team Bot custom MCP setup

The current official flow is **New chat → Create new Team Bot**. In the Team
Bot's info pane, open **Setup → Plugins → Add**, then use custom MCP with one
of the documented modes. Only the owner changes shared setup.

### Command

1. Confirm the package with `[mcp]` and entrypoint are installed on the
   conversation computer.
2. In **Setup → Plugins → Add**, choose custom MCP **Command**.
3. Supply command `kural-skills-mcp` with no arguments. Its transport is stdio.
   [The JSON example](command.example.json) records the command and empty args.
   Map them into the fields actually presented; do not assume this JSON imports
   into the app. The official Bot docs do not publish the full form field schema.
4. Connect through the app only after approval. Inspect actual MCP tool discovery
   and follow the verification checklist below before using saved instructions.

No secrets are needed for this dry-run server. Never put credentials into its
command or arguments. Team Bot docs say a Command server needing
credential-like arguments or environment secrets runs only in the owner's chat;
they recommend Remote HTTPS for custom servers needing secrets.

### Remote HTTPS

Use **Setup → Plugins → Add → custom MCP → Remote HTTPS** only after an approved
MCP deployment exists. The documented mode supports a Bot credential or each
person's OAuth sign-in. Confirm the endpoint, authentication, transport and
actual form with the owner. This repository has **no hosted endpoint now**.
There is no remote URL configuration here. Do not paste a placeholder URL or
use the stdio command as a URL. A future approved HTTPS endpoint must serve the
same immutable dry-run tools, not silently substitute a live robot backend.
No server was deployed, exposed, or tunneled as part of this folder.

### Not the global Marketplace flow

**Marketplace → Add → authenticate** installs existing catalog connectors.
Connectors are account-wide; `@` attaches a connector to a task. That global
Marketplace flow is different from the Team Bot's shared custom MCP setup above.
No Kural or Exa Bot Marketplace listing is verified here.

**Marketplace → Your plugins → Manage plugins and skills → Private skills** is
the documented place to manage saved instruction skills. `/` references saved
skills. Use the supported skill editor to save the instructions from `SKILL.md`;
do not assume local Markdown file import or discovery works in Bot. Saved
instructions are shared across Bots, not callable SDK tools.

The personal custom-MCP form, all its fields, and local file-based plugin loading
remain unverified. Do not invent personal setup clicks or use Grok Build
`grok mcp add`, `.grok/config.toml`, or API keys as a Bot installation substitute.
Cursor Agent Plugins and Cursor IDE distribution are documented separately;
their presence alone does not prove Bot package import compatibility. No
portable Agent Plugins MCP schema was verified for this deliverable, so it
contains no claimed reusable plugin manifest.

## Exact expected MCP tools

The shared adapter exposes **20 tools**: `kural_capabilities`, the 18 dry-run
catalog tools below, and `kural_dry_run_stop`. Tool argument schemas must come
from SDK catalog discovery, not from guessed Bot built-in names.

| Canonical SDK skill | MCP tool |
| --- | --- |
| `move_forward` | `kural_dry_run_move_forward` |
| `move_backward` | `kural_dry_run_move_backward` |
| `move_left` | `kural_dry_run_move_left` |
| `move_right` | `kural_dry_run_move_right` |
| `steer_left` | `kural_dry_run_steer_left` |
| `steer_right` | `kural_dry_run_steer_right` |
| `steer_back_left` | `kural_dry_run_steer_back_left` |
| `steer_back_right` | `kural_dry_run_steer_back_right` |
| `turn_left` | `kural_dry_run_turn_left` |
| `turn_right` | `kural_dry_run_turn_right` |
| `base_velocity` | `kural_dry_run_base_velocity` |
| `lift_up` | `kural_dry_run_lift_up` |
| `lift_down` | `kural_dry_run_lift_down` |
| `home` | `kural_dry_run_home` |
| `wave` | `kural_dry_run_wave` |
| `point` | `kural_dry_run_point` |
| `inspect` | `kural_dry_run_inspect` |
| `stow` | `kural_dry_run_stow` |

SDK dispatch is `KuralSkills(DryRunBackend()).call(canonical_name, **parameters)`;
stop is the separate SDK `stop()` method, not a nineteenth catalog skill.
Capabilities and stop take no skill parameters. A client's displayed namespace
may differ; inspect discovery rather than inventing a Grok Bot prefix.

- Translation: `duration_s` >0 to 10, default 1; `speed_m_s` >0 to 0.2,
  default 0.1.
- Steering: translation parameters plus `yaw_rate_rad_s` >0 to 0.5, default 0.3.
- Turns: `duration_s` and positive `yaw_rate_rad_s`.
- `base_velocity`: `duration_s`, signed `vx_m_s`/`vy_m_s` within ±0.2 and
  `yaw_rate_rad_s` within ±0.5; velocity defaults 0. Combined XY speed ≤0.2.
- Lift: `duration_s` only. Gestures: `timeout_s` >0 to 30, default 20.

All numbers must be finite and not booleans. Extra parameters are rejected.
Directions are robot-local: +X forward, +Y left, +yaw heading-left. Left/right
translation is strafe. Reverse steering names specify heading yaw, not car
steering-wheel direction. Duration is not a distance or arrival goal.

## Dry-run workflow and verification

1. Discover MCP tools. Check the exact 20-tool inventory and SDK-derived schemas.
2. Call `kural_capabilities` with `{}`. Inspect its protocol/version, mode,
   `no_live_backend`, tool names, skill catalog and limitations. These describe
   the adapter, not current robot readiness or a deployed gateway. Check the
   dry-run-only boundary. If missing, inconsistent, or live-capable, stop the
   workflow and report it.
3. With an explicit requested rehearsal, call `kural_dry_run_wave` with
   `{"timeout_s": 20}`. The structured response envelope contains
   `mode: "dry_run"`, `execution: "validated intent only; no robot motion"`, and
   `result` holding the SDK `SkillResult.as_dict()` output. Read the nested
   `result` state, reason, request and evidence, not just the envelope's label.
4. Only a nested `result.state` of `dry_run` warrants **“validated dry run; no
   robot motion.”** `result.motion_verified` and `result.stop_confirmed` must
   both remain false. An error or unknown result is not validated intent.
5. A stop rehearsal calls `kural_dry_run_stop` with `{}`. This records a dry-run
   stop request, not a physical stop. Do not claim emergency protection.
6. On invalid parameters, missing tools, transport loss, blocked/failed/unknown
   results or inconsistent evidence, report the actual failure. Never claim
   successful validation or automatically retry/resume uncertain work.

Bot **Settings → General → Auto-review** rules can ask for approval, but model
review is not a hard robot safety gate. Routine **Test run performs real work**;
do not run routines or treat Test run as a universal sandbox. The adapter's fixed
backend, not UI approval or saved instructions, enforces the no-motion boundary.
If a physical emergency exists, use the real operator stop controls separately.
Do not start live hardware, alter robot files, perception/depth or clearance,
register accounts, install apps, or create network deployment from this workflow.

## Evidence and limits

Setup wording and product distinctions follow the official sources cited in
`docs/GROK-TOOLS-INTEGRATIONS.md`, checked 2026-10-02. These files specify an
integration workflow; they are not evidence of Bot installation or execution.
The root project's native suite passed 46 tests, including real MCP stdio
verification of the 20-tool inventory and forced dry-run behavior. This is local
adapter evidence, not a Bot installation test. An actual Bot account connection,
Command execution on its conversation computer, Remote HTTPS hosting,
Marketplace publication, and robot motion remain unverified here.
