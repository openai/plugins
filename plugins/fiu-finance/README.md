# FIU Finance for Codex

This Codex plugin connects to the FIU read-only Streamable HTTP MCP service at
`https://ai.szfiu.com/api/mcp/v2`.

## Setup

1. Request an FIU API key at <https://ai.szfiu.com>.
2. Set `FIU_API_KEY` in the environment available to Codex before installing or restarting the plugin.
3. Install the `fiu-finance` plugin from the Codex official marketplace.

The plugin sends the key only as an `Authorization: Bearer ...` HTTP header. It does not put the key in tool arguments or prompts.

## Capabilities

The bundled `fiu-data-query` skill covers read-only quotes, K-lines, company information, financial statements, holdings, funds, bonds, IPOs, news, calendars and macroeconomic data. Use `describe_tool` before calling an unfamiliar endpoint.

The service does not place orders, transfer funds or manage brokerage accounts.

## Service documents

- Privacy policy: <https://github.com/fiu-ai/mcp-server/blob/main/PRIVACY.md>
- Terms of service: <https://github.com/fiu-ai/mcp-server/blob/main/TERMS.md>
- API documentation: <https://github.com/fiu-ai/mcp-server>
