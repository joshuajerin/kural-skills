# AI agent integrations for Kural skills

## Scope and evidence

Research checked on 2026-10-02 UTC. The requested OpenAI surface is the
**current Plugins platform for ChatGPT and Codex**, confirmed from the current
`/plugins` documentation. It is not the retired ChatGPT plugin beta or custom
GPT Actions. The earlier Actions-first/API-first recommendation did not match
this request; those paths remain optional background, not the proposed setup.

This is a proposal based on official HTTPS documentation and a read-only review
of this repository. No provider API inference request, credentials, dependency
installation, public endpoint, robot connection, controller change, depth or
perception work, simulation motion, or hardware test was performed.

**Current Kural status:** the callable layer exists, not a deployed robot-control
integration. `KuralSkills` defaults to `DryRunBackend`. The catalog has 18
primitive function schemas. The installed CLI is dry-run only. `serve` is a
custom JSON-lines session, **not an MCP server**. `GatewayBackend` requires an
externally supplied future gateway; it is not an existing DIMOS bridge.
Read [README](../README.md) and [RUNTIME-CONTRACT](RUNTIME-CONTRACT.md).

## Recommendation: current OpenAI Plugins

Use **Plugins**, the current installable package and universal directory shared
by ChatGPT and Codex [O12, O14]. A plugin can contain skills, an MCP server, or
both. Custom UI is optional. The official quickstart connects an MCP server as
a personal plugin and invokes it with `@` in **ChatGPT Work** on the web [O15].
Availability still depends on the user's account and workspace policy [O10].

For Kural, propose one small **dry-run-only skill plus a thin real MCP adapter**
using the existing SDK. Do not build a replacement SDK, custom GPT Actions, or
an unrelated API application instead. Start with a skills-only package if the
agreed first goal is explaining/planning requests, not executing the SDK. A
skills-only plugin does not by itself connect ChatGPT to the local robot or
Python SDK. Obtain approval before any adapter, installation, tunnel or hosting.

For the actual Grok Bot, use its documented custom MCP integration, not an xAI
API replacement. Team Bots document Setup → Plugins → Add with Remote HTTPS or
Command modes. General connector discovery is through Marketplace. Grok at
grok.com separately documents custom MCP connectors. See the sourced
[exact Grok tools and integrations](GROK-TOOLS-INTEGRATIONS.md) for those distinct
products, exact steps, and remaining account-level limits.

None of these interfaces makes live Kural execution safe or available.

## Official capability comparison

| Surface | Verified official support | Kural adapter needed | Limits / uncertainty |
| --- | --- | --- | --- |
| OpenAI API function calling | Model returns named calls with JSON arguments; your application executes them and returns outputs [O1]. | Small local allowlisted dispatcher to `KuralSkills`; provider schema conversion. | Not an installation inside consumer ChatGPT. Model/API/schema support must be tested. |
| OpenAI Agents SDK | Python function tools and MCP integrations, including local stdio, SSE and Streamable HTTP [O2, O3]. | Wrap existing SDK methods, or connect a real MCP server. | Optional orchestration; not needed for the first demo. Not a robot safety owner. |
| ChatGPT custom GPT Actions (**optional, not requested**) | REST API calls described with OpenAPI; None, API key or OAuth authentication [O4–O7]. | HTTPS REST service with OpenAPI and operation lifecycle routes. | 45-second request timeout; TLS 1.2+ on port 443 with valid public certificate; no custom headers [O7]. Account/workspace availability must be checked. |
| **Current OpenAI Plugins (requested)** | Shared ChatGPT/Codex directory; skills, optional MCP server/tools and optional MCP Apps UI [O12, O14–O19]. | Root `plugin.json`, focused `skills/.../SKILL.md`; real SDK-backed MCP adapter and `mcp.json` only when callable tools are needed. | Personal/local/workspace and public distribution differ. Public MCP requires HTTPS and review. Account/workspace availability and Kural compatibility untested. |
| OpenAI Responses remote MCP | Hosted MCP tool calls, `allowed_tools`, authorization and approval controls; current docs also describe Secure MCP Tunnel for private servers [O11]. | Reachable actual MCP server, or a supported private tunnel. | Local Agents SDK stdio is different from hosted remote access. Tunnel/product/workspace compatibility requires a separate check. |
| xAI API function calling | Native xAI SDK and OpenAI-compatible API examples; application executes custom calls [X1, X2]. | Same local Kural dispatcher, with xAI request/output formatting. | Disable parallel calls and validate locally. “OpenAI-compatible” does not mean every OpenAI feature is supported. |
| xAI API remote MCP | Native SDK, OpenAI-compatible Responses and Speech to Speech support; Streaming HTTP and SSE; tool allowlists, authorization and headers [X3]. | Reachable actual MCP server plus server-side authorization and approval. | **`require_approval` and `connector_id` are explicitly unsupported** in the OpenAI Responses compatibility path [X3]. Do not depend on OpenAI approval behavior. No xAI private-tunnel equivalent was verified. |
| **Grok Bot (requested)** | Dedicated Bot docs verify custom MCP servers: Remote HTTPS and Command. Marketplace connectors, private skills, and routines are distinct. | A real SDK-backed MCP adapter, then actual Bot registration. | Team Bot Setup → Plugins → Add is documented. Personal custom-server form details and Kural account compatibility remain untested. See [exact Grok report](GROK-TOOLS-INTEGRATIONS.md). |
| Grok at grok.com (separate surface) | Custom MCP connectors are documented. | Authenticated reachable MCP URL. | grok.com/connectors → New Connector → Custom. This is not the Bot or X setup. |

## Verified current plugin building blocks

- **Skill:** a folder with YAML-frontmatter `SKILL.md` (`name`, `description`),
  workflow instructions and optional `references/`, `scripts/` and `assets/`.
  Skill metadata guides discovery; the full instructions load when relevant.
  These OpenAI instruction skills are not automatically the 18 callable Kural
  robot primitives. A skill explains the workflow; a server enforces actions
  and authorization [O14, O16].
- **MCP:** optional server exposes tools with input/output schemas, resources,
  prompts and initialization instructions. Tools return text and/or
  `structuredContent`. Production guidance is stable HTTPS with Streamable
  HTTP. Official Python/TypeScript MCP SDKs are linked by the docs [O17].
  Kural's existing JSON-lines `serve` command is not this protocol.
- **Optional UI:** MCP Apps resources associated by `_meta.ui.resourceUri`;
  iframe communicates by the `ui/*` JSON-RPC `postMessage` bridge. ChatGPT
  `window.openai` extensions and `@openai/apps-sdk-ui` are optional, not an
  execution or safety requirement [O18]. Do not add a robot dashboard by default.
- **Package:** new packages use root `plugin.json` with Agent Plugins 1.0.0
  `$schema`; fixed `skills/` and optional `mcp.json` paths. OpenAI presentation
  settings go under `extensions.com.openai`. Compatibility packages using
  `.codex-plugin/plugin.json`, `.mcp.json` and `.app.json` remain supported.
  `.app.json` maps an already registered MCP connection/connector ID; it is not
  the portable MCP configuration or an OpenAPI Actions spec [O19].
- **Hooks:** optional lifecycle commands exist, but scripts must already exist
  in the execution environment and non-managed hooks require explicit trust.
  A web install does not deploy scripts. Kural needs no hooks [O14, O19].

The old `/apps-sdk/` entry redirects to `/plugins`; some official GitHub/UI
libraries retain Apps SDK names [O12, O21]. This is not a return of the retired
ChatGPT plugin beta. The current portable manifest is `plugin.json`, not a
legacy `ai-plugin.json`, and this is not a custom GPT configured with OpenAPI
Actions. Actions cannot substitute for the requested installable skill/MCP
package or its shared directory.

The plugin changelog records **2026-03-25** distribution guidance: approved Apps
SDK integrations could become Codex plugins; at that launch plugins were
Codex-only [O22]. Today's landing, architecture and quickstart explicitly say
ChatGPT **and** Codex. This research does not establish the exact later launch
date of the shared ChatGPT directory. Use current docs, not that older limit.
The linked `openai/plugins` repository currently demonstrates the compatibility
layout, including Figma/Notion skills and `.app.json`/`.mcp.json` connections;
its older examples do not override the newer portable-package guidance [O20].

## Proposed minimal Kural plugin (not created)

```text
kural-dry-run/
├── plugin.json
├── skills/
│   └── kural-dry-run/
│       ├── SKILL.md
│       └── references/        # reviewed catalog and dry-run/safety limits
└── mcp.json                  # optional; only for a real approved MCP adapter
```

Minimal portable identity, not an implemented package:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "kural-dry-run",
  "version": "0.1.0",
  "description": "Validate bounded Kural skill requests in dry-run mode only"
}
```

For a future remote adapter, `mcp.json` would declare its **actual** endpoint:
`{"$schema":"https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
"mcpServers":{"kural":{"type":"streamable-http","url":"<approved HTTPS MCP endpoint>"}}}`.
The placeholder is not a deployable endpoint. The portable schema also defines
stdio and legacy SSE shapes [O23], but this does not mean ChatGPT web can launch
local commands or use the existing JSON-lines CLI as an MCP server.

Proposed first MCP tools are `kural_capabilities` (honest dry-run mode/catalog)
and `kural_dry_run_wave` (one allowlisted SDK call). These names and wrappers
are proposals, not existing exports. The adapter must force `DryRunBackend`,
validate inputs through the current SDK and return the actual operation result
with **“validated dry run; no robot motion”**. Skill instructions teach tool
order, ask for missing parameters, reject live/control-stream requests and
never infer movement from an accepted dry run. Unsupported lifecycle methods
must not be advertised as implemented. MCP/UI confirmation does not grant a
robot owner lease, operator consent or clearance.

No hooks, UI, autonomous velocity stream, gateway or live motion tool is needed
for this first scope. A skills-only first package omits `mcp.json` and may teach
catalog use/request planning; it must not claim it ran the SDK. Confirm the
user's desired first workflow before implementing either shape.

## Installation, auth, private access and publication

1. **Personal MCP testing:** current developer-mode flow is Settings → Security
   and login → Developer mode; ChatGPT Plugins → plus → MCP URL or Tunnel.
   The quickstart installs the personal plugin, switches Chat to Work and uses
   `@` to invoke it [O10, O15]. Current labels and account eligibility need a
   real account check; this research did not perform one.
2. **Private testing:** Secure MCP Tunnel can reach a private stdio/HTTP MCP
   server without exposing it publicly [O10]. The tunnel still connects an
   OpenAI host to that private service; it is not an offline-only setup or a
   safety boundary. No tunnel/client/credential installation was performed.
3. **Local/team package distribution:** documented repo/personal
   `.agents/plugins/marketplace.json` catalogs support local/Git sources and
   selected local clients, including Codex and the ChatGPT desktop app. These
   are not the public directory, and local filesystem execution support must
   not be assumed for ChatGPT web. Workspace admins can publish personal
   plugins to selected roles; these remain inside that workspace [O19].
4. **Authenticated MCP:** writes and private data require OAuth 2.1 per MCP
   authorization, protected-resource/auth-server discovery, authorization code
   + PKCE S256, appropriate client registration and token checks for issuer,
   audience, expiry and scopes on every request. Prefer an established identity
   provider. API-key auth from Actions is not transferable: this plugin guide
   says ChatGPT cannot present custom API keys or machine-to-machine OAuth
   grants. Client mTLS does not replace end-user OAuth or local approval [O13].
5. **Public directory:** verified developer identity and publishing permission;
   upload ZIP, resolve scans, connect/domain-verify MCP, review, then manually
   publish the approved version. A stable public HTTPS MCP endpoint is required;
   private tunnel testing does not meet this publication requirement [O10, O24].
   Current submission supports only **one connected MCP server per plugin**,
   rejects ZIPs containing `.app.json` app references or hooks, and does not
   support adding MCP to an existing skills-only plugin. Include MCP
   in the initial submission if that is the intended public shape. MCP review
   asks for five positive and three negative cases, an accessible walkthrough
   and a dedicated test account when needed. Published MCP tool updates are
   scanned automatically; metadata/skills updates require a new ZIP/review.

No public hosting, package install, credentials, review acceptance or Kural
provider end-to-end execution is verified. Live robot access is separately
blocked by the owner/gateway and safety gaps below; publishing a plugin cannot
remove those gaps.

## Optional API alternative: a local, dry-run function call (not requested)

Proposed flow, not a demo run in this research:

1. Choose OpenAI **or** xAI and a currently accessible function-capable model.
   Obtain separate approval for API usage, credentials, cost and data sent out.
2. Keep one local `KuralSkills()` instance using its default dry-run backend.
   Offer one existing tool, for example `wave`, not all motion tools.
3. Ask the model to request that tool. Parse the returned JSON only after the
   complete call is available. Match its name against the local allowlist.
4. Show the proposed skill and parameters to the human. Validate with the SDK;
   reject unknown names, extra fields, invalid numbers and out-of-bound inputs.
5. Execute `robot.call("wave", timeout_s=20.0)` only after approval. Return its
   actual `as_dict()` result using the provider's tool-call ID.
6. Require the assistant to say **“validated dry run; no robot motion”**. Record
   model/version, requested arguments, approval, operation ID and output.
7. Test unknown tools, malformed JSON, refused approval, invalid duration,
   duplicate requests, unavailable provider and attempts to ask for live motion.
   Keep call-count, total runtime and spend limits. End the session cleanly.

For a zero-provider rehearsal, the existing CLI can validate a request without
model access. Example command below is illustrative and was not executed here:

```sh
.venv/bin/kural-skills call wave --params '{"timeout_s": 20}'
```

### Schema compatibility is real adapter work

`KuralSkills.tools()` emits the nested Chat Completions-style shape:
`{"type":"function","function":{"name":...,"parameters":...}}`.
OpenAI Responses and xAI Responses examples instead place `name`, `description`
and `parameters` directly on the function tool [O1, X1]. Convert the wrapper
for the selected API; do not claim unchanged interoperability.

The catalog currently has optional properties and defaults, and no `required`
array. OpenAI `strict: true` requires every property to be required and every
object to have `additionalProperties: false`; optional values need a nullable
schema and local normalization [O1]. For the first one-tool demo, make the
existing numeric parameter explicit and required in the provider schema.
Alternatively select non-strict mode explicitly and rely on local validation.
Test provider acceptance of schema keywords/defaults; do not silently weaken the
SDK limits. Nullable provider values must be normalized before SDK dispatch.
No xAI equivalent of OpenAI strict-mode guarantees was verified in [X1].

Both providers document `parallel_tool_calls: false` [O1, X1]. Set it, and still
serialize local execution. A provider setting and a per-instance SDK lock do not
arbitrate the robot's native UI or other processes. Do not expose `base_velocity`
in the first demo. An LLM must not generate a repeated velocity stream or own a
heartbeat loop. It selects bounded intent from approved skills; a future local
driver must enforce execution and safety independently.

## Deployment paths after separate approval

### Optional, not requested: custom GPT Actions / HTTP / OpenAPI

This is a different product path, retained only for reference. Do not implement
it for the current Plugins request. It is useful only if the user separately
chooses a custom GPT and a small REST API. Proposed routes, **not currently implemented**, are:

- Catalog/capabilities: identify dry-run/live mode and supported skills.
- Start: submit an allowlisted bounded skill and return an operation ID quickly.
- Status: fetch that operation's state and evidence.
- Cancel: request revocation of that operation, with honest confirmation status.
- Global STOP: request a latched stop, separate from cancel and from resume.

Generate OpenAPI from the reviewed catalog rather than maintaining independent
robot parameter limits. Configure API key authentication for a narrow private
demo, or per-user OAuth for multiple users [O5]. Do not use anonymous write
endpoints. Mark motion submission as `x-openai-isConsequential: true` so ChatGPT
always asks for confirmation [O7]. This UI confirmation is additional to local
operator approval, not a safety grant.

Use short start/status requests instead of holding an HTTP call open until a
long gesture finishes. Published egress ranges can supplement an authenticated
allowlist [O7]. ChatGPT cannot simply call a developer's `localhost`: provide a
reachable HTTPS service only after explicit deployment approval. No built-in
private Actions tunnel was verified. Do not expose the native robot process or
its control streams directly.

### Requested Plugins tool layer: thin MCP adapter

Use MCP when the selected Kural plugin needs callable SDK-backed tools. The
package and installation path are described above. Agents SDK MCP remains a
separate optional API-hosted orchestration path, not the ChatGPT plugin setup. Implement a thin **real** MCP server
around the existing SDK, not a replacement SDK. The JSON-lines CLI cannot be
registered as an MCP stdio server without a protocol adapter.

For local API orchestration, the Agents SDK can run an actual MCP stdio server
without a public endpoint [O3]. For ChatGPT developer mode, current docs offer
public HTTPS or Secure MCP Tunnel for private-server testing [O10]. Tunnel
setup is not authorized or performed by this research. Current submission docs
say a public HTTPS endpoint is required; testing access is not publication.

Use OAuth 2.1/MCP authorization for authenticated app servers [O13]. Label true
read-only tools with `readOnlyHint: true`; motion, cancellation and stop mutate
state and must not be labeled read-only. Use truthful destructive/open-world
annotations [O9]. Developer-mode write tools default to confirmation, but a
user can remember approvals for a conversation [O8]. Therefore enforce local
operator consent independently. OpenAI Responses remote MCP also has explicit
approval requests [O11]; leave approval required for consequential operations.

### Optional xAI API path (not the requested Grok Bot)

Only if the user separately chooses an API application, a local xAI application
can call the existing Python SDK. This is not the requested Grok Bot plugin
integration. Use the [exact Grok Bot MCP path](GROK-TOOLS-INTEGRATIONS.md) for
that product; do not replace it with API function calling.

Later, a shared remote MCP adapter could serve xAI and OpenAI. xAI accepts
`allowed_tools` in its Responses interface (`allowed_tool_names` in its native
SDK); an empty list allows all tools [X3]. Use a positive allowlist and enforce
the same allowlist on the server. Use the authorization field or supported
headers, never tokens in URLs or prompts. Since xAI does not support
`require_approval`, the server/local application must refuse execution until an
independent authenticated operator approves the exact bounded request. Model
text saying “confirmed” is not operator consent. No consumer-Grok, private
network or app-store compatibility claim follows from these API docs.

## Shared action and safety contract

Agents and humans must call the same validated skill dispatcher. A transport
adapter must not gain a more powerful robot interface than the human SDK.

- **Admission:** validate identity, scope, skill allowlist, parameters, mode,
  target namespace and operation freshness. Bind operator approval to exact
  parameters, expiry and execution mode. Revalidate after approval.
- **Actions:** use `start` plus operation `status` for asynchronous interfaces;
  `call` remains suitable for the immediate dry-run demo. Keep a session-scoped
  operation registry and authenticate status/cancel access. The current primitive
  catalog does not expose lifecycle methods as provider tools; these need thin
  separately reviewed wrappers if offered to an agent.
- **Outputs:** preserve `operation_id`, `skill`, `state`, `reason`, bounded request
  and available evidence. Show backend/mode explicitly. `dry_run` means recorded
  intent; acceptance or command completion is not measured arrival. No fabricated
  `motion_verified`, `stop_confirmed` or successful hardware result.
- **Uncertainty:** after an ambiguous submit or timeout, return `outcome_unknown`.
  Do not automatically retry movement. A future adapter needs admission
  deduplication/idempotency before enabling network retries; provider call IDs
  alone do not implement this, and it is not a current SDK feature.
- **Cancel:** revoke only the matching operation through an approved runtime
  route. Stopping a local wait is not robot cancellation. Reliable gesture-only
  cancellation is missing in the reviewed runtime; reject it or use an explicitly
  agreed global-stop policy. Dry-run status/cancel tests prove no robot behavior.
- **Global STOP:** offer a clear human STOP path and a separate structured stop
  action. It must preempt queued/running intent, latch the approved global stop,
  and report acknowledgment or uncertainty. Do not make STOP wait for model
  inference or a new motion-approval dialog. Remote STOP is best-effort, not a
  substitute for native/local operator STOP. Only explicit operator resume may
  unlatch; do not expose automatic agent resume.
- **Trust:** provider keys stay in the local application; service tokens stay in
  authorization fields. Use least privilege, TLS, short-lived credentials,
  rate/call limits and redacted audit logs. Treat chat text, tool descriptions
  and tool outputs as untrusted inputs. Prompt instructions and MCP annotations
  do not enforce authorization or protect against prompt injection.

### Network latency cannot be the motion clock

The reviewed runtime has approximately 250 ms command/heartbeat timeouts.
Cloud inference, approval and network round trips cannot reliably maintain
those loops. A future approved local gateway must own the monotonic deadline,
client-liveness checks, atomic owner lease, per-cycle safety checks and serialized
outputs. The model selects one bounded request; local runtime owns its execution.
Do not send cloud-derived periodic velocities or add an agent heartbeat that
masks failure of the native operator UI.

Owner grants must include client/request identity, scene namespace, episode epoch
and geometry/safety identity. Native takeover, STOP, focus loss, missing client
liveness, expired deadline, reset, lost ownership or a safety-gate failure must
terminate intent locally even when the cloud cannot send cancel. Reject expired
queued requests rather than executing them after a delayed response. Network
latency must not refresh old safety evidence.

## Live integration remains blocked

The exact requirements and source limitations are in
[RUNTIME-CONTRACT](RUNTIME-CONTRACT.md), not in provider documentation.

- Native UI idle messages and planner watchdog zeros can race independent skill
  publishers. There is no reviewed atomic per-client owner/lease boundary.
- Autonomous base execution requires real fresh swept-volume evidence and an
  approved command-path guard. The reviewed runtime has unavailable clearance.
- Runtime acceptance, cancellation, gesture completion and STOP acknowledgment
  are not yet a deployed per-operation gateway contract.

No adapter may bypass these limits by publishing directly to motion/authorized
arm streams, calling private controllers, injecting keyboard events, changing
physics state, using manual intent for agent commands, fabricating evidence,
disabling gates, or treating a static map as approval. This research neither
changes nor proposes depth/perception work. Keep blocked skills blocked.

## Staged plan and exit criteria

1. **Select plugin workflow:** current OpenAI Plugins is the requested surface,
   not Actions or a generic API application. Confirm skills-only planning versus
   one callable dry-run MCP tool, target ChatGPT Work/web or desktop/Codex,
   account policy, single-user versus workspace, and allowed private access.
   For the requested Grok Bot, use its documented custom MCP setup and the same
   reviewed adapter; do not substitute Grok Build or a generic xAI application.
2. **Offline dry-run rehearsal:** inspect SDK schemas and exercise validation,
   status, unknown IDs, refusal and supported lifecycle behavior without provider
   access. All responses must explicitly indicate no runtime or physical action.
3. **Approved package/adapter:** create only the agreed plugin shape. For MCP,
   force dry-run mode, expose the smallest catalog/tool set and test initialization,
   discovery, schemas and actual structured results. Do not rename the JSON-lines
   CLI as MCP or advertise hypothetical lifecycle wrappers as working.
4. **Approved plugin test:** after separate installation, transport and credential
   approval, install personally/locally; evaluate skill activation, tool selection,
   negative prompts, parallel/duplicate requests, expiry, permissions, disconnects
   and honest results in the selected ChatGPT/Codex surface. A tunnel, public
   hosting or directory submission needs separate approval. Evidence is dry-run
   selection/validation, not robot movement or publication acceptance.
5. **Separate runtime design review:** approve a single-owner gateway and local
   lifecycle contract without bypassing existing gates. Block any unsupported
   skill. This stage is not authorized by the present research.
6. **Separate simulation acceptance:** only after permission and prerequisites,
   test owner races, planner conflict, native takeover, disconnects, deadlines,
   reset epochs, cancellation/STOP ordering and late outputs. Measure pacing
   with rendering active. Until then, report integration as unverified.
7. **Hardware:** requires a separate risk review, calibration and physical tests.
   No simulation or API test warrants a hardware capability or safety claim.

## Official sources and access failures

The cited OpenAI plugin guides, raw GitHub files and Agent Plugins schemas were
fetched directly over HTTPS with HTTP 200. SDK and MCP Apps reference links are
also listed as linked upstream resources, not separately tested implementations.
These verify published product contracts, not this repository's interoperability.
Model names, plan eligibility, UI labels and transports can change; pin and test
the chosen versions before deployment.

- **[O1]** OpenAI function calling:
  https://developers.openai.com/api/docs/guides/function-calling
- **[O2]** OpenAI Agents Python SDK tools:
  https://openai.github.io/openai-agents-python/tools/
- **[O3]** Agents SDK MCP transports:
  https://openai.github.io/openai-agents-python/mcp/
- **[O4]** GPT Actions introduction:
  https://developers.openai.com/api/docs/actions/introduction
- **[O5]** GPT Actions authentication:
  https://developers.openai.com/api/docs/actions/authentication
- **[O6]** GPT Actions OpenAPI setup:
  https://developers.openai.com/api/docs/actions/getting-started
- **[O7]** GPT Actions production constraints and consequential actions:
  https://developers.openai.com/api/docs/actions/production
- **[O8]** ChatGPT developer mode, eligibility, protocols and confirmations:
  https://developers.openai.com/api/docs/guides/developer-mode
- **[O9]** Current app/plugin MCP server guide (redirected from Apps SDK):
  https://developers.openai.com/plugins/build/mcp-server
- **[O10]** Current connection/testing and private access guide:
  https://developers.openai.com/plugins/deploy/connect-chatgpt
- **[O11]** OpenAI Responses MCP, approvals and Secure MCP Tunnel:
  https://developers.openai.com/api/docs/guides/tools-connectors-mcp
- **[O12]** Current Apps SDK entry point redirect:
  https://developers.openai.com/apps-sdk/ → https://developers.openai.com/plugins
- **[O13]** Current app/plugin MCP OAuth authorization:
  https://developers.openai.com/plugins/build/auth
- **[O14]** Current plugin architecture (skills, optional MCP/UI/hooks):
  https://developers.openai.com/plugins/concepts/plugins
- **[O15]** Current quickstart (personal plugin, ChatGPT Work and `@` invocation):
  https://developers.openai.com/plugins/quickstart
- **[O16]** Skill folders, metadata and workflow/tool boundary:
  https://developers.openai.com/plugins/concepts/skills
  https://developers.openai.com/plugins/build/skills
- **[O17]** MCP concepts and linked official Python/TypeScript SDKs:
  https://developers.openai.com/plugins/concepts/mcp-server
  https://github.com/modelcontextprotocol/python-sdk
  https://github.com/modelcontextprotocol/typescript-sdk
- **[O18]** Optional MCP Apps UI and ChatGPT extensions:
  https://developers.openai.com/plugins/build/chatgpt-ui
  https://modelcontextprotocol.io/docs/extensions/apps
- **[O19]** Current portable packaging, compatibility, marketplaces and workspace publishing:
  https://developers.openai.com/plugins/build/plugins
- **[O20]** Official plugin repository (read via raw GitHub HTTPS):
  https://github.com/openai/plugins
  https://raw.githubusercontent.com/openai/plugins/main/README.md
  https://raw.githubusercontent.com/openai/plugins/main/plugins/figma/.codex-plugin/plugin.json
  https://raw.githubusercontent.com/openai/plugins/main/plugins/figma/.app.json
  https://raw.githubusercontent.com/openai/plugins/main/plugins/notion/.codex-plugin/plugin.json
- **[O21]** Official MCP/UI examples (retains Apps SDK naming):
  https://developers.openai.com/plugins/build/examples
  https://raw.githubusercontent.com/openai/openai-apps-sdk-examples/main/README.md
- **[O22]** Official plugin UI changelog (2026-03-25 Codex-only launch note):
  https://developers.openai.com/plugins/changelog
- **[O23]** Agent Plugins 1.0.0 schemas linked from OpenAI packaging docs:
  https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
  https://agent-plugins.org/schemas/1.0.0/mcp.schema.json
- **[O24]** Current upload/review/publication constraints and update flow:
  https://developers.openai.com/plugins/deploy/submission
- **[X1]** xAI custom function calling:
  https://docs.x.ai/developers/tools/function-calling
- **[X2]** xAI tools overview:
  https://docs.x.ai/developers/tools/overview
- **[X3]** xAI remote MCP, transports and unsupported approval parameter:
  https://docs.x.ai/developers/tools/remote-mcp

Unavailable evidence:

- Web search skill: **no Serper API key configured**. No key was requested or
  configured; direct official HTTPS documentation was sufficient for API research.
- https://help.x.com/en/using-x/about-grok — **HTTP 403**.
- https://x.ai/grok — **HTTP 403**.
- https://docs.x.ai/docs/key-information/faq — redirected to
  https://docs.x.ai/developers/key-information/faq, **HTTP 404**.
- https://help.openai.com/en/articles/8988022-winding-down-the-chatgpt-plugins-beta
  — **HTTP 403**; legacy retirement details were not independently fetched.
- https://openai.com/index/introducing-gpts/ — **HTTP 403**.

The blocked legacy consumer URLs did not establish the available Grok Bot
feature set. Later research used the official `https://docs.x.ai/llms.txt` index
and dedicated Bot/consumer Markdown pages; it verified actual custom MCP paths.
See [the exact Grok report](GROK-TOOLS-INTEGRATIONS.md). The user's account
entitlements, Kural installation, store publication and actual end-to-end
execution remain unverified.
