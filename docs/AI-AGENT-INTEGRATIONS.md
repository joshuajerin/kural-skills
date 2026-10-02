# AI agent integrations for Kural skills

## Scope and evidence

Research checked on 2026-10-02 UTC. This document interprets “chatgpt dot” as
**ChatGPT**; it does not identify a separate product by that name. Confirm the
intended surface before implementing an adapter.

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

## Recommendation

Start with **API function calling and the existing local dry-run SDK**. Use
OpenAI or xAI as the language model, but let a local application validate and
execute the requested function. This needs no inbound public robot endpoint,
MCP server, custom GPT, or new control framework. A future paid provider request
still needs separately approved credentials and a supported model.

Then choose the user interface:

- **ChatGPT custom GPT:** authenticated HTTPS REST adapter plus OpenAPI Actions.
- **ChatGPT app/MCP:** real MCP adapter, when ChatGPT-native tool discovery or
  reuse across MCP hosts is needed. Custom graphical UI is optional.
- **Grok:** verified path is an application using the **xAI API**, with local
  function calling first; remote MCP is an optional later path.
- **Consumer Grok in X/grok.com:** arbitrary third-party robot-tool installation
  was not verified. Do not present API support as consumer Grok bot support.

None of these interfaces makes live Kural execution safe or available.

## Official capability comparison

| Surface | Verified official support | Kural adapter needed | Limits / uncertainty |
| --- | --- | --- | --- |
| OpenAI API function calling | Model returns named calls with JSON arguments; your application executes them and returns outputs [O1]. | Small local allowlisted dispatcher to `KuralSkills`; provider schema conversion. | Not an installation inside consumer ChatGPT. Model/API/schema support must be tested. |
| OpenAI Agents SDK | Python function tools and MCP integrations, including local stdio, SSE and Streamable HTTP [O2, O3]. | Wrap existing SDK methods, or connect a real MCP server. | Optional orchestration; not needed for the first demo. Not a robot safety owner. |
| ChatGPT custom GPT Actions | REST API calls described with OpenAPI; None, API key or OAuth authentication [O4–O7]. | HTTPS REST service with OpenAPI and operation lifecycle routes. | 45-second request timeout; TLS 1.2+ on port 443 with valid public certificate; no custom headers [O7]. Account/workspace availability must be checked. |
| ChatGPT apps / MCP | Developer mode supports read and write MCP tools; SSE and streaming HTTP [O8]. SDK documentation describes controlled MCP actions and optional UI [O9]. | Actual MCP initialization, tool listing/calling, transport, auth and structured results. | Developer mode docs list Pro, Plus, Business, Enterprise and Education on web; workspace policy can restrict access [O8, O10]. No Kural adapter is implemented or tested. |
| OpenAI Responses remote MCP | Hosted MCP tool calls, `allowed_tools`, authorization and approval controls; current docs also describe Secure MCP Tunnel for private servers [O11]. | Reachable actual MCP server, or a supported private tunnel. | Local Agents SDK stdio is different from hosted remote access. Tunnel/product/workspace compatibility requires a separate check. |
| xAI API function calling | Native xAI SDK and OpenAI-compatible API examples; application executes custom calls [X1, X2]. | Same local Kural dispatcher, with xAI request/output formatting. | Disable parallel calls and validate locally. “OpenAI-compatible” does not mean every OpenAI feature is supported. |
| xAI API remote MCP | Native SDK, OpenAI-compatible Responses and Speech to Speech support; Streaming HTTP and SSE; tool allowlists, authorization and headers [X3]. | Reachable actual MCP server plus server-side authorization and approval. | **`require_approval` and `connector_id` are explicitly unsupported** in the OpenAI Responses compatibility path [X3]. Do not depend on OpenAI approval behavior. No xAI private-tunnel equivalent was verified. |
| Consumer Grok bot | No arbitrary user-installed robot Actions/MCP path verified in accessible official material. | Unknown; use an explicitly identified API-based application instead. | Consumer documentation fetches were blocked; absence of verification is not proof that no feature exists. |

### Important naming/version note

Do not assume the old ChatGPT plugin beta is available. The historical retirement
Help Center article could not be fetched (403). Also, on this research date,
OpenAI's `/apps-sdk/` URLs **redirected to `/plugins/`**, whose current landing
page describes a universal plugin directory for ChatGPT and Codex [O12]. The
current developer-mode documentation still uses “apps” and “MCP,” while some
connection instructions use “ChatGPT Plugins” [O8, O10]. This is evidence of the
current documentation surface, **not evidence that the legacy plugin beta has
returned**. Recheck the actual account UI and current publication requirements
before selecting an app/plugin packaging route. Do not promise store acceptance.

## Easiest first demo: a local, dry-run API tool call

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

### ChatGPT custom GPT Actions: HTTP/OpenAPI

Use this when the goal is a custom GPT in the ChatGPT interface and a small REST
API is sufficient. Proposed routes, **not currently implemented**, are:

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

### ChatGPT apps/MCP, or OpenAI Agents SDK MCP

Use MCP when several hosts should discover the same tools, or when a
ChatGPT-native app connection is wanted. Implement a thin **real** MCP server
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

### Grok through xAI

Start with a local xAI API application calling the existing Python SDK. This
can present a human CLI or another explicitly agreed application interface. It
is not a feature installed in the consumer Grok bot. No extra agent framework
is required for this first integration.

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

1. **Select surface:** confirm whether the user wants ChatGPT custom GPT,
   ChatGPT app/MCP, an OpenAI API application, an xAI API application, or an
   explicitly identified consumer Grok feature. Confirm local/private access and
   single versus multiple users. Do not build competing adapters first.
2. **Offline dry-run rehearsal:** inspect schemas and exercise SDK validation,
   action status, unknown IDs, refusal, cancel and STOP without provider access.
   All responses must explicitly indicate no runtime and no physical action.
3. **One-provider dry-run function call:** after API approval, run the one-tool
   flow above; test negative prompts, duplicate/parallel requests, timeouts and
   honest narration. Evidence is tool selection/validation, not robot movement.
4. **Approved transport demo:** implement only the selected thin OpenAPI or MCP
   adapter, still forced dry-run. Test auth, permissions, expiry, disconnects,
   approval, unknown operations and uncertain outcomes. Public hosting, tunnel
   setup, dependencies and credentials each need explicit approval.
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

All successful sources below were fetched over HTTPS with HTTP 200. These verify
published API/product contracts, not this repository's interoperability.
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

No unavailable page was treated as evidence of compatibility. Consumer Grok
integration, the user's account entitlements, store publication and actual
Kural/provider end-to-end execution remain unverified.
