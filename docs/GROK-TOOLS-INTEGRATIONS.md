# Exact Grok tools and integrations

Checked: 2026-10-02T03:51:16.705134+00:00. Official sources only. Documentation research, not an account-level or runtime test. xAI OpenAPI reports version **1.0.0**; current guide examples use **`grok-4.7`**. Bot/Build/consumer pages do not publish a version number.

## Which product?

**Grok Bot is a real, separate product. It is not another name for the xAI API.** Current official docs describe named Bots on a persistent cloud computer and a Cursor account [B1–B3]. Earlier “consumer integration unverified” claims in `AI-AGENT-INTEGRATIONS.md` are superseded for **grok.com custom MCP** and **Grok Bot custom MCP** by the sources below. That older file was not edited in this research.

| Product | Documented built-in capability | User-defined tools? | Exact integration surface / limit |
| --- | --- | --- | --- |
| **Grok Bot desktop/mobile** | Persistent browser, filesystem, command line; connectors; saved instruction skills; routines; inter-Bot coordination [B1–B5]. | **Yes: custom MCP servers**, explicitly documented for Team Bots with **Remote HTTPS** and **Command** modes [B3]. Plugins and private skills are distinct. | Sidebar **Marketplace → Add → browser authentication → `@` connector**. Team Bot **info pane → Setup → Plugins → Add**; custom MCP modes are documented, but full custom-server form fields/personal-server add flow are not specified in the fetched Bot docs. Do not invent those clicks. Commands normally run on the conversation's cloud computer, not this Ubuntu host. |
| **Grok at grok.com** | Chat, Imagine images/video, voice, uploaded files, connectors [C1]. | **Yes: Custom MCP connectors**, including custom schemas and logic [C2]. | **grok.com/connectors → New Connector → Custom → MCP server URL → authentication**. URL must be publicly reachable; localhost/private IPs rejected [C3]. |
| **Grok iOS/Android consumer apps** | Conversations/settings/subscription sync with web [C1]. | Custom MCP documented for Grok; **mobile connector-add UI and exact parity not established**. | Official registration instructions point to **grok.com/connectors**, not a mobile-specific dialog. Do not infer mobile availability from sync. |
| **Grok within X / @grok replies** | Not inventoried here: official X help fetch returned HTTP 403. | **No custom registration path verified for the X surface.** | Do not transfer grok.com, Bot, Build, or API setup to X. A blocked fetch is not proof the feature is absent. |
| **Grok Build CLI** | Coding agent, built-in tools, project rules, skills, plugins, hooks, subagents [D1–D3]. | **Yes: local stdio and remote HTTP MCP**, plus plugin bundles. | `grok mcp add` / `.grok/config.toml`; built-in external-tool names are `<server>__<tool>` [D1]. This CLI is not Grok Bot. |
| **xAI developer API** | Server-side search/browsing, Python code execution, images, collection search [A1]. | **Yes: application-executed functions and server-executed remote MCP** [A2–A3]. | `POST https://api.x.ai/v1/responses`; functions return to your application; MCP is reached by xAI. This builds an API application, not an installed Bot plugin. |

### Source freshness: cached snippets versus live docs

Exa search snippets captured older UI wording: **Settings → Plugins → Browse → Add**, and **Settings → Plugins → Yours** for private skills. Direct HTTP 200 fetches of the current official `.md` pages instead say **Marketplace → Add**, and **Marketplace → Your plugins → Manage plugins and skills → Private skills** [B4/B5/B8]. B5 explicitly says **“Plugins are not a settings section.”** Use these live-page steps for this research; verify the installed app version before acting. This does not change the separate **Team Bot info pane → Setup → Plugins → Add** flow [B3]. The authenticated personal custom-MCP form remains unverified.

### Grok Bot: exact supported setup and controls

1. Get the dedicated app from **https://x.ai/bot**. Official docs include Ubuntu-compatible `.deb`, `.rpm`, and AppImage Linux builds, plus macOS/Windows/mobile [B2]. Sign in with **Cursor**. Eligible paid Cursor or linked individual SuperGrok plan required; cloud data storage required.
2. Create a focused Bot. For an existing catalog plugin: **Marketplace → Add → authenticate**, then type **`@`** to attach a connector to a task. Connectors are account-wide [B4]. A current Bot Marketplace connector-name catalog was not available from these docs; do not claim Exa, Kural, or any particular plugin is listed there.
3. For **Team Bot** setup: **New chat → Create new Team Bot**. The info pane's **Setup** has **Plugins, Secrets, Skills, Files**, each with **Add**. Only the owner changes shared setup [B3]. The official custom MCP mode names are **Remote HTTPS** and **Command**. The exact personal custom-MCP form and its transport/header fields remain **not documented in the fetched Bot pages**, not “unsupported.”
4. **Remote HTTPS** uses a Bot credential or each person's OAuth sign-in. **Command** runs on whichever computer the conversation uses. A Command server that needs environment-variable secrets or credential-like arguments runs only in the owner's chat; docs recommend **Remote HTTPS** for a custom server needing secrets [B3]. Never place credentials in command/arguments.
5. **Marketplace → Your plugins → Manage plugins and skills** lists **Installed** plugins and **Private skills**. Current direct-fetch docs explicitly say **“Plugins are not a settings section”** [B5]; cached search snippets showing **Settings → Plugins** do not override this current page. Individual plugin tools can be enabled/disabled [B5]. **`/`** references saved instruction skills; this does not create a callable SDK tool.
6. **Settings → General → Auto-review** supports **Ask first** and **Allow automatically** rules; **Ask first** wins. Auto Review is model-based, not a hard robot safety gate [B6]. Team connector policy lives at **https://cursor.com/dashboard/plugins**; Enterprise MCP allowlist is a separate control [B7].
7. Local command execution is separate from the cloud computer. Docs describe Mac/Windows local execution with **Ask every time / Always allow / Never allow**. The UI moves to **Settings → Computer → Computers** once computers are registered [B6]. **Linux local-command execution is not verified** merely because the Linux Bot app exists.
8. Saved skills are shared across Bots. Teaching can record up to **10 minutes**, no microphone audio. One Bot has up to **50 routines**, with **20 recent run records** each. A routine **Test run performs real work** [B8]. Each Bot has one screen and one computer-use task on that screen at a time [B1/B4].

**Exact Bot internal tool names and argument schemas:** the inspected Bot documentation describes browser, shell, files and plugin calls but does **not** publish an exhaustive built-in function registry or input schemas. Do not label API `browse_page`, `code_execution`, etc. as Bot-callable functions. MCP tool names/schemas come from the actual installed MCP server. API names below are for the API only.

### Plugin packaging / distribution: do not mix clients

Grok Bot explicitly inherits Cursor team connector policy and Marketplace [B7]. The first-party Cursor plugin docs [P1–P2] document portable **Agent Plugins** (`plugin.json` root, schema `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`, skills and MCP) and **Cursor Plugins** (`.cursor-plugin/plugin.json`, extra Cursor components). MCP definitions are in root **`mcp.json`**. Cursor plugin `variables` declare configuration names; values are set in dashboard **Plugins → Configure**, never committed.

Public Cursor plugin publication: host in a public Git repository, submit repository at **https://cursor.com/marketplace/publish**, undergo manual review. Team distribution: **Dashboard → Plugins & MCPs → Team Marketplaces → Add Marketplace → Import from Repo** [P1–P2]. **These general Cursor IDE packaging/testing instructions are not evidence that every component or local path works in Grok Bot.** The Bot docs establish connectors-as-plugins and custom MCP, not a full standalone Bot package manifest/submission specification. Confirm a Kural package appears and works in the actual Bot Marketplace before claiming compatibility. No plugin was built or submitted here.

## Grok consumer connectors: exact inventory

xAI lists these built-in OAuth connectors [C2]:

- **Gmail & Google Calendar**
- **Google Drive**
- **OneDrive**
- **Outlook Mail & Calendar**
- **Microsoft Teams**
- **SharePoint**
- **Salesforce**

The separate third-party catalog is at **https://grok.com/connectors**. No exhaustive current catalog or individual connector tool schemas were extracted. Business/Enterprise admins provision connectors in their cloud console first [C2/C4]. Consumer **Custom** registration accepts your own MCP URL and required authentication. Public reachability is required. The official tunneling page documents ngrok and Cloudflare; quick Cloudflare tunnels do **not** support SSE, but do support Streamable HTTP [C3]. No tunnel was started, and no network exposure is proposed without approval.

## xAI API: exact tool inventory (not Bot tools)

Current examples use **Responses `/v1/responses`** and `model="grok-4.7"`. Do not claim the same inventory exists in legacy Chat Completions or every model. API keys/usage are separate from installing a Bot connector. OpenAI-compatible syntax does not guarantee OpenAI features.

| Category | Responses `tools[].type` / native xAI SDK name | Configuration and support limits |
| --- | --- | --- |
| Built-in web search + page browsing [A4] | `web_search` / `web_search()` | `allowed_domains` or `excluded_domains` (**mutually exclusive**, max **5**); Responses examples put these under `filters`. `enable_image_understanding`, `enable_image_search`. No separate browser-install registration required. OpenAPI marks `external_web_access`, `search_context_size`, `user_location` rejected when set [A10]. |
| Built-in X search [A5] | `x_search` / `x_search()` | `allowed_x_handles` or `excluded_x_handles` (**mutually exclusive**); guide says max **20**, current OpenAPI says **10**: official-source conflict; use ≤10 pending validation. `from_date`, `to_date` are **YYYY-MM-DD**, inclusive; full datetimes do not apply as dates. `enable_image_understanding`, `enable_video_understanding`. |
| Built-in Python execution [A6] | `code_interpreter` / `code_execution()` | Server-side sandbox, not shell execution on Kural. Guide passes only tool type. OpenAPI says `container` is rejected when set [A10]. No documented Bot-machine, filesystem or robot access from this tool. |
| Built-in image creation/editing [A7] | `image_generation` / `image_generation()` | Optional `action`: `auto` (default), `generate`, `edit`. Tool uses latest Imagine (`grok-imagine-image-2.0` in current guide); no size/format configuration. Model selects aspect ratio; direct image endpoints are separate. |
| Built-in collection RAG [A8] | `file_search` / `collections_search()` | Responses `vector_store_ids` (actual xAI collection IDs, OpenAPI max **10**), optional `max_num_results` (minimum 1); native SDK `collection_ids`. OpenAPI marks `filters` and `ranking_options` rejected when set. |
| Custom application functions [A2/A10] | `function` / `xai_sdk.chat.tool(...)` | Responses flat `name`, optional `description`, `parameters` JSON Schema. Root object or `anyOf`/`oneOf` of objects; invalid root yields 400. Max **350 tools/request**. Model returns `function_call`; app executes and returns `function_call_output` with `call_id`. OpenAPI says **`strict` unsupported**, and parameter-schema adherence is not enforced; always validate locally. |
| External server tools [A3] | `mcp` / `mcp(...)` | Required `server_url`, `server_label`; optional `server_description`, `allowed_tools` (native `allowed_tool_names`), `authorization`, `headers` (native `extra_headers`). **Streaming HTTP and SSE only**, not local stdio. Missing/empty allowlist enables all server tools. **`require_approval` and `connector_id` explicitly unsupported**. Native SDK, Responses, and Speech to Speech documented. |
| Tool discovery (**OpenAPI-schema evidence only**) [A10] | `tool_search` | Optional `execution`: only `server` or unset. Function/MCP `defer_loading=true` hides definitions until discovery; definitions remain callable. No dedicated guide/runtime test established here. |
| Local shell (**OpenAPI-schema evidence only**) [A10] | `shell` | Required `environment`, with `type: "local"`; optional `skills`. Returns `shell_call`, app sends `shell_call_output`. This is a client-executed schema, **not server-side Python** and not a documented Bot integration path. No runtime support/model coverage verified; not proposed for Kural. |

Documented API internal function names [A9], **not separately registered top-level tools**:

- Web: `web_search`, `web_search_with_snippets`, `browse_page`, `open_page`, `open_page_with_find`.
- Images: `search_images`, `view_image` (enabled by relevant search settings).
- X: `x_user_search`, `x_keyword_search`, `x_semantic_search`, `x_thread_fetch`, `view_x_video`.
- Code/RAG: `code_execution`, `collections_search`.
- MCP: `{server_label}.{tool_name}` when label provided.

The usage guide names these internal calls but does not publish complete argument schemas for each. Do not invent their arguments or advertise them as independent API `tools[].type` values.

API control settings:

- `tool_choice`: `auto` (default), `required`, `none`, or force a named function. The Responses OpenAPI shape is **`{"type":"function","name":"wave"}`**; the function guide also shows nested Chat Completions-style `function.name`. Use the shape for the chosen endpoint, not blindly copied syntax [A2/A10].
- `parallel_tool_calls: false`: disable parallel model calls; application still serializes dispatch [A2].
- `max_turns`: bounds assistant/tool turns per request, **not individual calls**. Multiple tools may run in one turn. A client-side tool handoff resets the counter for the follow-up request. Enforce total call/time/spend bounds outside the API [A9/A11].
- Streaming custom function arguments arrive whole in one chunk, per current guide [A2].
- `max_output_tokens` includes reasoning and output. `include`/`verbose_streaming` expose tool decisions/citations, not a clearance or action certificate [A9/A10].
- **Official docs disagree:** Responses reference prose says “only functions and web search” while its `ModelTool` schema and dedicated guides document X/code/image/RAG/MCP. Use dedicated guides and schema; exact runtime acceptance remains untested. X handle count also conflicts (above). Compatibility schema presence alone is not proof a parameter is supported: the MCP guide explicitly rejects approval/connector parameters despite their presence in OpenAPI.

## Grok Build: exact external-tool registration (separate product)

Official MCP examples [D1]:

```text
grok mcp add <name> -- <actual stdio server command and args>
grok mcp add --transport http <name> <actual HTTPS MCP URL>
grok mcp add --transport http <name> <URL> --header "Authorization: Bearer ${TOKEN}"
grok mcp list
grok mcp doctor <name>
```

`--header` repeatable; HTTP OAuth handled automatically. `--scope project` writes `.grok/config.toml`; user scope is `~/.grok/config.toml`. Config keys: `command`, `args`, `env` or `url`, `headers`, `startup_timeout_sec` (default **30**), `tool_timeout_sec` (default **6000**). OAuth tokens: `~/.grok/mcp_credentials.json`. UI `/mcps`: Space toggle, `r` refresh, `i` OAuth, `a` add, `x` remove. Plugins bundle skills/agents/hooks/MCP/LSP; project/user `.grok/plugins/` and `.grok/skills/` are Build paths [D2]. These are **not Bot configuration paths**.

Exa's own official documentation separately names **Grok Build** marketplace setup at **https://exa.ai/docs/get-started/exa-mcp**: `/marketplace`, select `exa`, press `i`; `/mcp`, select `exa`, press `i` to sign in. This does **not** establish an Exa Grok Bot Marketplace listing. Exa setup in the current agent environment is handled separately by the parent agent; this research did not install or configure Exa.

## Exact Kural path: supported protocol, not installed integration

Read-only repository review: `KuralSkills.tools()` emits **18 nested function schemas**; `KuralSkills.call(name, **parameters)` dispatches through `DryRunBackend` by default. Existing JSON-lines CLI `serve` is **not MCP**. No Grok plugin, genuine MCP adapter, hosted endpoint or live robot binding exists here.

Existing function names, not Grok-specific inventions:

| Existing Kural names | Existing inputs / bounds |
| --- | --- |
| `move_forward`, `move_backward`, `move_left`, `move_right` | `duration_s`: >0 to 10, default 1; `speed_m_s`: >0 to .2, default .1. |
| `steer_left`, `steer_right`, `steer_back_left`, `steer_back_right` | Above inputs plus `yaw_rate_rad_s`: >0 to .5, default .3. |
| `turn_left`, `turn_right` | `duration_s`, positive `yaw_rate_rad_s` with above bounds. |
| `base_velocity` | `duration_s`; `vx_m_s`, `vy_m_s`: −.2 to .2; `yaw_rate_rad_s`: −.5 to .5; velocity defaults 0. |
| `lift_up`, `lift_down` | `duration_s`: >0 to 10, default 1. |
| `home`, `wave`, `point`, `inspect`, `stow` | `timeout_s`: >0 to 30, default 20. |

These are requested values, **not measured motion/arrival**. Catalog schemas reject additional properties; local SDK validation remains authoritative. `stop()` is a separate SDK method, not one of these 18 catalog schemas.

**For the actual Grok Bot:** after explicit user approval, use its documented **custom MCP**, not an API replacement. The minimal callable path would be a genuine MCP adapter exposing only an existing allowlisted function such as **`wave(timeout_s)`** and routing it to **`KuralSkills(DryRunBackend()).call("wave", timeout_s=...).as_dict()`**. Its MCP `inputSchema` should come from `KuralSkills.describe("wave")["parameters"]`. Install/register through the actual Bot custom-server flow; Team Bot's documented entry is **Setup → Plugins → Add**, with **Remote HTTPS** or **Command**. Remote needs an approved authenticated reachable endpoint; Command needs the adapter installed on the conversation computer, not just on this Ubuntu host. Exact personal form still needs an account check. This adapter is a **proposal**, not an existing tool; obtain approval before building it, deploying it or connecting accounts. A saved instruction skill can describe the dry-run workflow but cannot itself connect the SDK.

**If the user means grok.com:** use the separately documented **New Connector → Custom** flow with that actual authenticated MCP adapter URL. Never offer the existing JSON-lines CLI as the URL/protocol.

**Only if the user chooses the API:** convert the existing nested schema to the flat Responses shape: `{"type":"function", **entry["function"]}`. Offer only `wave`, set `parallel_tool_calls=false`, validate/approve locally, dispatch to dry run, and return the actual `function_call_output`. This is **not Grok Bot installation**.

Successful dry-run results must state **“validated dry run; no robot motion.”** Failed validation or unknown outcomes must report the actual failure and must not claim validation succeeded. No API/connector approval grants robot ownership, estop clearance or motion authorization. Do not expose velocity streaming, change physics/controllers/perception, or pretend dry-run results are live execution.

**Clarifying question:** Do you mean the dedicated **Grok Bot app**, **Grok at grok.com**, **Grok Build CLI**, or **Grok inside X**?

## Official evidence and fetch status

All numbered docs below returned **HTTP 200** during this check. Small verbatim support excerpts:

- [B1] “Each Bot works on a persistent cloud computer with a browser, filesystem, and terminal”.
- [B3] “Custom MCP server, **Remote HTTPS**”; “Custom MCP server, **Command**”.
- [B4] “Connectors are installed as plugins from **Marketplace**.”
- [C2] “Define your own tools with custom schemas and logic.”
- [C3] “Grok will reject these URLs” (localhost/private-network addresses).
- [A2] “The model requests the call, you execute it locally, and return the result.”
- [A3] “The `require_approval` and `connector_id` parameters in the OpenAI Responses API are not currently supported.”
- [A10] `strict`: “Not supported. Only maintained for compatibility reasons.”
- [D1] “namespaced as `<server>__<tool>`”.

Exact official URLs:

| Ref | URL |
| --- | --- |
| B1 | https://docs.x.ai/grok-bot/overview.md |
| B2 | https://docs.x.ai/grok-bot/get-started.md |
| B3 | https://docs.x.ai/grok-bot/team-bots.md |
| B4 | https://docs.x.ai/grok-bot/computer-and-apps.md |
| B5 | https://docs.x.ai/grok-bot/settings-and-notifications.md |
| B6 | https://docs.x.ai/grok-bot/approvals-security-and-privacy.md |
| B7 | https://docs.x.ai/grok-bot/teams-and-enterprises.md |
| B8 | https://docs.x.ai/grok-bot/skills-routines-and-automations.md |
| C1 | https://docs.x.ai/grok/overview.md |
| C2 | https://docs.x.ai/grok/connectors.md |
| C3 | https://docs.x.ai/grok/connectors/custom-mcp-tunneling.md |
| C4 | https://docs.x.ai/grok/connector-management.md |
| D1 | https://docs.x.ai/build/features/mcp-servers.md |
| D2 | https://docs.x.ai/build/features/skills-plugins-marketplaces.md |
| D3 | https://docs.x.ai/build/overview.md |
| P1 | https://cursor.com/docs/plugins |
| P2 | https://cursor.com/docs/reference/plugins |
| A1 | https://docs.x.ai/developers/tools/overview.md |
| A2 | https://docs.x.ai/developers/tools/function-calling.md |
| A3 | https://docs.x.ai/developers/tools/remote-mcp.md |
| A4 | https://docs.x.ai/developers/tools/web-search.md |
| A5 | https://docs.x.ai/developers/tools/x-search.md |
| A6 | https://docs.x.ai/developers/tools/code-execution.md |
| A7 | https://docs.x.ai/developers/tools/image-generation.md |
| A8 | https://docs.x.ai/developers/tools/collections-search.md |
| A9 | https://docs.x.ai/developers/tools/tool-usage-details.md |
| A10 | https://docs.x.ai/openapi.json (OpenAPI `info.version=1.0.0`, `ModelTool`, `FunctionDefinition`, `ModelToolChoice`, `ShellEnvironment`) |
| A11 | https://docs.x.ai/developers/tools/advanced-usage.md |
| Index | https://docs.x.ai/llms.txt |
| Responses | https://docs.x.ai/developers/rest-api-reference/inference/responses.md |
| Models | https://docs.x.ai/developers/models.md |
| Exa Build setup | https://exa.ai/docs/get-started/exa-mcp (official Exa source; HTTP 200) |

Fetch failures / limits: **https://help.x.com/en/using-x/about-grok** returned **403**. Guessed **https://cursor.com/help/grok-bot/plugins**, **https://cursor.com/help/grok-bot/marketplace**, **https://cursor.com/docs/plugins/mcp-servers** returned **404**; these guesses are not sources and do not prove absence. **https://cursor.com/docs/plugins/building** redirected to the successful P2 URL. **https://grok.com/connectors** returned 200 as a public page, but no authenticated account tool listing or setup was tested. No credentials, inference requests, installations, deployment, or robot execution occurred in this research.
