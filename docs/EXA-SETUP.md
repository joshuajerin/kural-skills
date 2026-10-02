# Exa setup in the agent environment

Verified on 2026-10-02. This setup is for research in Prime Agent, not the robot.

## Configuration

Registered the official hosted HTTP MCP server:

```sh
prime-agent mcp add exa --url https://mcp.exa.ai/mcp
prime-agent mcp list
```

The server is registered as `exa` in the user's Prime Agent MCP configuration.
No repository dependency, API key, OAuth login, browser, or paid tool was added.
Existing sessions may need to rediscover the configured server; registration
alone is not a verified tool call.

## Live verification

An MCP client completed initialization, live tool discovery, and a real search
for official Grok Bot documentation. The search returned source URLs/content
with `isError: false`.

- Server: `exa-search-server`, title `Exa`, version `3.2.1`.
- Actual available tools: **`web_search_exa`**, **`web_fetch_exa`**.
- Keyless mode: free rate-limited usage. Paid `agent_run` is not available or
  enabled in this connection. No authenticated account usage was configured.
- Verification artifacts: `/tmp/kural-exa-mcp-verification.json` and
  `/tmp/kural-exa-mcp-verification.log`. These are local temporary evidence,
  not committed credentials or durable repository assets.

The verification used the installed MCP client through the agent environment.
The current Python kernel did not provide the generic catalog connection
facade described by its MCP skill. That missing facade was not reported as a
failed Exa service: the native user-server configuration and real MCP protocol
call were independently verified.

## Research rule

Discover live tool schemas before calling. Search snippets can be cached:
Exa returned older Grok Bot `Settings → Plugins` labels while current direct
official Markdown uses **Marketplace**. Prefer current direct primary docs
for exact UI steps; keep product-specific Team Bot setup distinct.

Official setup/auth/tool reference:
https://exa.ai/docs/get-started/exa-mcp

Exa documents keyless MCP at the URL above; OAuth/API keys are separate optional
modes. Broader authentication or paid usage needs separate user approval.
