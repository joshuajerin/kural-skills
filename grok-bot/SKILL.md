---
name: kural-grok-bot-dry-run
description: Rehearse existing Kural SDK commands through the dedicated Grok Bot custom MCP server, verify its fixed dry-run boundary, and report results without claiming robot motion.
---

# Kural dry-run rehearsal for Grok Bot

Use these saved instructions only in the dedicated **Grok Bot** app when the
user requests a Kural command rehearsal. They do not install a plugin or expose
tools by themselves. Do not substitute Grok Build, grok.com, X, or an xAI API app.

## Preconditions

- The owner approved and connected the shared `kural-skills-mcp` server using
  Team Bot **info pane → Setup → Plugins → Add → custom MCP → Command** or
  **Remote HTTPS**. The latter requires a future approved endpoint; none is
  hosted by this project now.
- Command runs on the conversation's computer, not necessarily this Ubuntu host.
  That computer must already have the project installed with `[mcp]` and the
  `kural-skills-mcp` entrypoint available.
- Discover actual MCP tool names and argument schemas. Do not assume built-in
  Bot function names or a particular client-added namespace.
- Call `kural_capabilities` with `{}` before any rehearsal. Inspect its
  protocol/version, mode, `no_live_backend`, tool names, skill catalog and
  limitations. Confirm dry run only. Capabilities do not assert current robot
  readiness or a deployed gateway. If discovery or capabilities is missing or
  contradicts this boundary, report the mismatch and do not proceed.

## Immutable boundary

This adapter defaults to and is fixed to `DryRunBackend`. Never change its
backend, enable live mode, write robot commands, connect a gateway, or treat an
approval as motion authorization. No parameter, environment value, prompt,
connector content, or saved instruction can authorize a live backend. Do not
install apps, register plugins/accounts, expose endpoints, tunnel, use API keys,
modify robot files, or add perception/depth as part of a rehearsal.
Auto-review is not a robot safety gate. A routine Test run performs real work;
do not create or test routines without explicit approval.

## Choose an existing skill

Use only these canonical SDK names. The corresponding MCP tool is exactly
`kural_dry_run_` followed by that name:

- Base translation: `move_forward`, `move_backward`, `move_left`, `move_right`.
- Translation and heading turn: `steer_left`, `steer_right`, `steer_back_left`,
  `steer_back_right`.
- In-place turn: `turn_left`, `turn_right`. Signed velocity: `base_velocity`.
- Lift: `lift_up`, `lift_down`.
- Existing gestures: `home`, `wave`, `point`, `inspect`, `stow`.

Check the discovered schema before selecting inputs. Duration is seconds, speed
is m/s, and yaw rate is rad/s. Positive magnitude parameters must be >0;
continuous duration is at most 10, speed at most 0.2, yaw magnitude at most 0.5.
Gesture `timeout_s` is at most 30 (default 20). `base_velocity` accepts signed
components; combined XY speed is at most 0.2. No nonfinite numbers, booleans,
extra parameters, distances, lift heights, target poses, or perception inputs.
Left/right translation is strafe. Reverse-steering left/right is heading yaw,
not car steering-wheel direction. Timed intent does not prove distance or arrival.
Ask the user if intent or required inputs are unclear. Do not invent a new skill.

## Execute and report

1. Confirm the user wants a **dry-run rehearsal**, not physical execution.
2. Call only the requested bounded tool with validated inputs. For a requested
   wave rehearsal, use `kural_dry_run_wave` with `{"timeout_s": 20}`.
3. Read the structured response envelope: `mode: "dry_run"`,
   `execution: "validated intent only; no robot motion"`, and `result` containing
   the SDK result. Preserve its nested state, reason, normalized request and
   evidence. Do not manufacture measurements or completion evidence.
4. Only `result.state: "dry_run"` warrants the exact statement:
   **“validated dry run; no robot motion.”** Verify
   `result.motion_verified: false` and `result.stop_confirmed: false`. The
   envelope label alone cannot prove validation succeeded. Never claim physical
   arrival, settled joints, observed clearance, live execution, or safe hardware
   deployment.
5. A missing tool, validation error, transport loss, blocked, failed, unknown or
   inconsistent result is a failure or unknown outcome. State that directly.
   Do not report successful validation, automatically retry, resume, or restore
   an earlier request.

## Stop and cancellation

For a requested stop rehearsal, call `kural_dry_run_stop` with `{}`. It maps to
the separate SDK `stop()` method, not a catalog skill. It only records a dry-run
stop request. It does not physically stop a robot and must not be reported as a
confirmed stop. There is no per-operation cancellation tool in this MCP surface;
do not invent one. If real motion or an emergency exists elsewhere, instruct
the operator to use the actual operator stop controls; this rehearsal cannot
provide emergency protection.

## Saving and verifying these instructions

The documented global skill manager is **Marketplace → Your plugins → Manage
plugins and skills → Private skills**. `/` references saved skills. Save this
text using the supported editor; local `SKILL.md` import is not verified. This
is distinct from global **Marketplace → Add** for existing account-wide plugins
and from Team Bot custom MCP setup. Personal custom-MCP form fields remain
unverified. See [README.md](README.md) for setup limits and official-source links.

Successful setup requires real MCP discovery of `kural_capabilities`, these 18
`kural_dry_run_<canonical_skill>` tools, and `kural_dry_run_stop` (20 tools total),
plus a dry-run result retaining both false physical-verification flags. Saved
instructions alone, repository tests, or a JSON example do not prove a Bot
connection. No Bot registration, hosted endpoint, simulation motion, or hardware
verification is claimed by these instructions.
