---
name: render-mcp
description: >-
  Connects and configures the Render MCP server for AI coding tools—setup per
  tool (Cursor, Claude Code, Codex), authentication, workspace selection, tool
  catalog, and troubleshooting. Use when MCP is not configured, list_services()
  fails, the user asks about Render MCP setup, or an action skill needs MCP
  but it's not connected yet.
  Trigger terms: MCP, Render MCP, list_services, MCP setup, MCP server,
  API key, Bearer token, mcp.render.com, workspace selection.
license: MIT
compatibility: Render MCP server (hosted at mcp.render.com)
metadata:
  author: Render
  version: "1.0.0"
  category: operations
---

# Render MCP Server

The Render MCP server lets AI coding tools manage Render services, databases, deploys, logs, and metrics directly. This skill covers **setup**, **authentication**, **workspace selection**, the **tool catalog**, and **troubleshooting**.

Action skills (render-deploy, render-debug, render-monitor) use MCP tools for their workflows. If MCP is not connected, set it up using this skill first.

## When to Use

- `list_services()` fails or MCP tools are unavailable
- First-time Render MCP setup for any AI tool
- User asks how to connect their AI tool to Render
- Switching workspaces or troubleshooting auth errors
- Discovering which MCP tools exist and what they do

## Connection Details

| Property | Value |
|----------|-------|
| URL | `https://mcp.render.com/mcp` |
| Transport | HTTP (streamable) |
| Auth | Bearer token (Render API key) |
| API key page | `https://dashboard.render.com/u/*/settings#api-keys` |
| Docs | `https://render.com/docs/mcp-server` |

## Setup by Tool

### Cursor

1. Get an API key from the [Render Dashboard](https://dashboard.render.com/u/*/settings#api-keys)

2. Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_API_KEY>"
      }
    }
  }
}
```

3. Restart Cursor, then verify with `list_services()`

### Claude Code

1. Get an API key from the [Render Dashboard](https://dashboard.render.com/u/*/settings#api-keys)

2. Add the MCP server:

```bash
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer <YOUR_API_KEY>"
```

3. Restart Claude Code, then verify with `list_services()`

### Codex

1. Get an API key from the [Render Dashboard](https://dashboard.render.com/u/*/settings#api-keys)

2. Set the key in your shell:

```bash
export RENDER_API_KEY="<YOUR_API_KEY>"
```

3. Add the MCP server:

```bash
codex mcp add render --url https://mcp.render.com/mcp --bearer-token-env-var RENDER_API_KEY
```

4. Restart Codex, then verify with `list_services()`

### Other Tools

For tools not listed above, use the generic HTTP MCP configuration:

- **URL:** `https://mcp.render.com/mcp`
- **Auth header:** `Authorization: Bearer <YOUR_API_KEY>`
- **Transport:** HTTP (streamable HTTP, not SSE)

See [Render MCP docs](https://render.com/docs/mcp-server) for tool-specific instructions.

## Workspace Selection

After MCP is connected, set the active workspace:

```
Set my Render workspace to [WORKSPACE_NAME]
```

Or programmatically:

```
get_selected_workspace()   # Check current
list_workspaces()          # List available
```

All MCP operations run against the active workspace.

## Tool Catalog

### Service management

| Tool | Purpose |
|------|---------|
| `list_services()` | List all services and datastores |
| `get_service(serviceId)` | Get service details |
| `create_web_service(...)` | Create a web service from Git repo |
| `create_static_site(...)` | Create a static site from Git repo |
| `update_service(serviceId, ...)` | Update service configuration |
| `restart_service(serviceId)` | Restart a service |

### Deploys

| Tool | Purpose |
|------|---------|
| `list_deploys(serviceId, limit)` | List deploys for a service |
| `trigger_deploy(serviceId)` | Trigger a new deploy |

### Logs

| Tool | Purpose |
|------|---------|
| `list_logs(resource, level, type, text, statusCode, limit)` | Query logs with filters |

Key filters: `level` (error, warn, info), `type` (build, deploy), `text` (search string), `statusCode` (HTTP codes).

### Metrics

| Tool | Purpose |
|------|---------|
| `get_metrics(resourceId, metricTypes, ...)` | Get service or database metrics |

Metric types: `cpu_usage`, `memory_usage`, `cpu_limit`, `memory_limit`, `http_latency`, `http_request_count`, `active_connections`.

Optional: `httpLatencyQuantile` (0.5, 0.95, 0.99), `httpPath` (filter by endpoint).

### Databases

| Tool | Purpose |
|------|---------|
| `list_postgres_instances()` | List Postgres databases |
| `get_postgres(postgresId)` | Get database details |
| `query_render_postgres(postgresId, sql)` | Run SQL query |

### Key Value

| Tool | Purpose |
|------|---------|
| `list_key_value()` | List Key Value instances |
| `get_key_value(keyValueId)` | Get Key Value details |

### Environment Variables

| Tool | Purpose |
|------|---------|
| `update_environment_variables(serviceId, envVars)` | Set env vars on a service |

### Workspace

| Tool | Purpose |
|------|---------|
| `list_workspaces()` | List available workspaces |
| `get_selected_workspace()` | Get the active workspace |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Wrong URL (using SSE endpoint) | Use `https://mcp.render.com/mcp` (not `/sse`) |
| Expired or invalid API key | Generate a new key from Dashboard > Account Settings > API Keys |
| Wrong workspace selected | Run `list_workspaces()` and switch to the correct one |
| Using MCP to create image-backed services | Not supported — use Dashboard or API for prebuilt Docker images |
| Missing `Bearer` prefix in auth header | Header must be `Authorization: Bearer <key>` |

## Troubleshooting

See `references/troubleshooting.md` for connection errors, auth failures, timeout issues, and tool-specific quirks.

## References

| Document | Contents |
|----------|----------|
| `references/troubleshooting.md` | Connection errors, auth failures, tool-specific issues, timeout handling |

## Related Skills

- **render-deploy** — Deploy flows using MCP tools
- **render-debug** — Debug failures using MCP logs and metrics
- **render-monitor** — Monitor health using MCP metrics
- **render-cli** — CLI alternative when MCP is unavailable
