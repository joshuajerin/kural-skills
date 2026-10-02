# Kural dry-run plugin for ChatGPT and Codex

This folder is a **new OpenAI Plugins** package using portable Agent Plugins
1.0.0. It is not custom GPT Actions, the retired `ai-plugin.json` beta, a UI,
or a deployed robot integration.

## Status and contents

- `plugin.json`: portable identity at the package root.
- `mcp.json`: one local stdio server, `kural-skills-mcp`, with no arguments.
- `skills/kural-dry-run/SKILL.md`: request-planning and dry-run instructions.
- `package.py`: optional deterministic ZIP builder; standard library only.
- `validation/`: official HTTPS schema snapshots and local validation evidence.

**Local adapter verified; platform installation remains unverified.** The shared
adapter belongs in the repository root Python package, not this plugin folder.
Its argument-free entrypoint, `kural-skills-mcp`, passed local stdio MCP discovery
and call tests with 20 forced-dry-run tools. The root native suite passed all
46 tests. Stdio is the only transport; no HTTP transport is provided. That evidence does not verify a
ChatGPT/Codex client, account, tunnel, hosted endpoint, or robot connection.

## Verified local adapter interface

The shared adapter forces `DryRunBackend`; there is no live mode, gateway
selection, robot connection, or environment switch that enables robot control.
Its locally verified MCP tools are:

- `kural_capabilities`: dry-run mode, honest capability limits and SDK catalog.
- `kural_dry_run_<canonical_skill>` for each of these 18 skills:
  `move_forward`, `move_backward`, `move_left`, `move_right`, `steer_left`,
  `steer_right`, `steer_back_left`, `steer_back_right`, `turn_left`, `turn_right`,
  `base_velocity`, `lift_up`, `lift_down`, `home`, `wave`, `point`, `inspect`, `stow`.
- `kural_dry_run_stop`: immediate SDK dry-run stop result. It sends no robot STOP,
  confirms no physical stop, and is not an emergency-stop control.

Primitive tool inputs must come from the current SDK catalog. Discover schemas
rather than guessing parameters. `kural_capabilities` returns a standalone
object with `protocol`, `version`, `mode`, `no_live_backend`, `tools`, `skills`
and `limitations`. Successful primitive and stop calls return `structuredContent`
with `mode: "dry_run"`, `execution: "validated intent only; no robot motion"`
and `result` containing the SDK's `SkillResult.as_dict()`. `execution` is a string,
not an object. Tool errors are not successful result envelopes.
The nested SDK result identifies the operation, skill, state, reason, normalized
request and available evidence. Physical
verification flags remain false. Say **“validated dry run; no robot motion”**
only when the actual result supports that statement. A validation error is not
an accepted dry run. No asynchronous start/status/cancel/resume, network retry
idempotency, autonomous velocity loop, or live lifecycle contract is offered.

`kural-skills serve` is the native JSON-lines session. **It is not MCP**, even
though MCP stdio also uses JSON messages. Do not put it in this MCP configuration.

## Local installation: future manual steps

Use Python 3.11 or newer. From the `kural-skills` repository root, after the
adapter has passed its local tests:

```sh
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -e '.[mcp]'
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/kural-skills-mcp --help
```

This installs the SDK and its optional official MCP dependency. No OpenAI API
key is required for local dry-run execution. These commands have not been run
as a plugin installation. Do not reinstall over an active environment without
reviewing its current dependencies.

In a **local compatible plugin client** with Agent Plugins and stdio support,
install/import this folder using that client's local-package or local-marketplace
flow. Point its plugin source at `chatgpt/`, not the repository root. Put the
repository's `.venv/bin` on **that client's process PATH** before starting it;
`mcp.json` resolves the executable token `kural-skills-mcp` through that PATH.
A terminal PATH change does not change an already running desktop client's PATH.
If the client cannot resolve the token, configure its process launch environment
explicitly. No machine-specific absolute path is embedded in the portable package.

Client support and account/workspace policy must be checked separately. Merely
copying a package folder does not install it or prove tool execution. Test MCP
initialization, discovery, capabilities, one bounded dry-run request, invalid
parameters and the dry-run stop tool. Confirm there is no robot process involved.

## ChatGPT web: separate private access approval required

**ChatGPT web cannot be assumed to launch this local executable.** The stdio
manifest is for local compatible clients, not a hosted endpoint. For a private
ChatGPT test, separately approve and configure **Secure MCP Tunnel** to the
installed, tested MCP adapter. Check current account/workspace eligibility and
the tunnel client's documented stdio support. No tunnel command, credentials,
auth server, hosted service, endpoint or ChatGPT plugin has been configured here.

The documented personal flow is Settings → Security and login → Developer mode,
then ChatGPT Plugins → plus → Tunnel (or an actual approved MCP URL). Current UI
labels and availability need an account check. After a successful personal
connection, use ChatGPT Work and `@` to invoke the plugin. These are future steps,
not a claim of account access or end-to-end compatibility. Do not submit the
local executable token as an MCP URL. There is no placeholder remote URL in
`mcp.json` and no deployable remote configuration in this package.

Private tunnel access is not public hosting, public directory acceptance,
authorization for robot movement, or a safety boundary. Any remote/auth setup
requires a separate review; the package supplies no credentials or auth policy.

## Deterministic packaging

From the repository root:

```sh
.venv/bin/python chatgpt/package.py --output /tmp/kural-dry-run-plugin.zip
```

The ZIP places `plugin.json`, `mcp.json`, `README.md` and the skill at its root
(no enclosing `chatgpt/` folder). The script writes only to the chosen path,
which must be outside this folder. Its fixed allowlist excludes schema reports,
source code, scripts, credentials, virtual environments, robot assets and meshes.
Packaging does not install the Python adapter or launch a client. Repeated builds
of unchanged files produce identical bytes.

A local ZIP is not a public-directory-ready deployment. Official public submission
requires a stable public HTTPS MCP endpoint and review; a private tunnel or local
stdio package does not meet that requirement. This package has no hooks, UI,
`.app.json`, registered connector, or public submission. Obtain separate approval
before changing transport or attempting publication.

## Validation and limits

See `validation/report.json` for fetched schema URLs, SHA-256 values and checks.
Manifest validation proves document shape, not MCP interoperability or installation.
SDK validation limits are not calibrated robot safety limits. This package does
not test obstacles, geometry, clearance, measured movement, mechanical stopping,
simulation or hardware. It does not add controllers, depth or perception code.
Only Kural's authoritative robot package may define robot assets and controls.

Official references, checked over HTTPS:

- [Agent Plugins manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)
- [Agent Plugins MCP schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json)
- [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [ChatGPT connection and private testing](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [Plugin submission](https://developers.openai.com/plugins/deploy/submission)

The repository's research is in
[`docs/AI-AGENT-INTEGRATIONS.md`](../docs/AI-AGENT-INTEGRATIONS.md); that relative
link applies to the source checkout, not a standalone distributed ZIP.
