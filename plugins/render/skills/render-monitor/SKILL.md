---
name: render-monitor
description: Monitor Render services in real-time. Check health, performance metrics, logs, and resource usage. Use when users want to check service status, view metrics, monitor performance, or verify deployments are healthy.
license: MIT
compatibility: Requires Render MCP tools or CLI
metadata:
  author: Render
  version: "1.0.0"
  category: monitoring
---

# Monitor Render Services

Real-time monitoring of Render services including health checks, performance metrics, and logs.

## When to Use This Skill

Activate this skill when users want to:
- Check if services are healthy
- View performance metrics
- Monitor logs
- Verify a deployment is working
- Investigate slow performance
- Check database health

## Prerequisites

**MCP tools (preferred):** Test with `list_services()` - provides structured data

**CLI (fallback):** `render --version` - use if MCP tools unavailable

**Authentication:** For MCP, use an API key (set in the MCP config or via the `RENDER_API_KEY` env var, depending on tool). For CLI, verify with `render whoami -o json`.

**Workspace:** `get_selected_workspace()` or `render workspace current -o json`

> **Note:** MCP tools require the Render MCP server. If unavailable, use the CLI for status and logs; metrics and database queries require MCP.

## MCP Setup (Per Tool)

If `list_services()` fails because MCP isn't configured, guide the user to set up the hosted Render MCP server. Ask which AI tool they're using, then provide the matching instructions below. Always use their API key.

### Cursor

Walk the user through these steps:

1) Get a Render API key:
```
https://dashboard.render.com/u/*/settings#api-keys
```

2) Add this to `~/.cursor/mcp.json` (replace `<YOUR_API_KEY>`):
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

3) Restart Cursor, then retry `list_services()`.

### Claude Code

Walk the user through these steps:

1) Get a Render API key:
```
https://dashboard.render.com/u/*/settings#api-keys
```

2) Add the MCP server with Claude Code (replace `<YOUR_API_KEY>`):
```bash
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer <YOUR_API_KEY>"
```

3) Restart Claude Code, then retry `list_services()`.

### Codex

Walk the user through these steps:

1) Get a Render API key:
```
https://dashboard.render.com/u/*/settings#api-keys
```

2) Set it in their shell:
```bash
export RENDER_API_KEY="<YOUR_API_KEY>"
```

3) Add the MCP server with the Codex CLI:
```bash
codex mcp add render --url https://mcp.render.com/mcp --bearer-token-env-var RENDER_API_KEY
```

4) Restart Codex, then retry `list_services()`.

### Other Tools

If the user is on another AI app, direct them to the Render MCP docs for that tool's setup steps and install method.

### Workspace Selection

After MCP is configured, have the user set the active Render workspace with a prompt like:

```
Set my Render workspace to [WORKSPACE_NAME]
```

---

## Quick Health Check

Run these 5 checks to assess service health:

```
# 1. Check service status
list_services()

# 2. Check latest deploy
list_deploys(serviceId: "<service-id>", limit: 1)

# 3. Check for errors
list_logs(resource: ["<service-id>"], level: ["error"], limit: 20)

# 4. Check resource usage
get_metrics(resourceId: "<service-id>", metricTypes: ["cpu_usage", "memory_usage"])

# 5. Check latency
get_metrics(resourceId: "<service-id>", metricTypes: ["http_latency"], httpLatencyQuantile: 0.95)
```

---

## Service Health

### Check Status

```
list_services()
```

```
get_service(serviceId: "<id>")
```

### Check Deployments

```
list_deploys(serviceId: "<service-id>", limit: 5)
```

| Status | Meaning |
|--------|---------|
| `live` | Deployment successful |
| `build_in_progress` | Building |
| `build_failed` | Build failed |
| `deactivated` | Replaced by newer deploy |

### Check Errors

```
list_logs(resource: ["<service-id>"], level: ["error"], limit: 50)
```

```
list_logs(resource: ["<service-id>"], statusCode: ["500", "502", "503"], limit: 50)
```

---

## Performance Metrics

### CPU & Memory

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage", "memory_usage", "cpu_limit", "memory_limit"]
)
```

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| CPU | <70% | 70-85% | >85% |
| Memory | <80% | 80-90% | >90% |

### HTTP Latency

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_latency"],
  httpLatencyQuantile: 0.95
)
```

| p95 Latency | Status |
|-------------|--------|
| <200ms | Excellent |
| 200-500ms | Good |
| 500ms-1s | Concerning |
| >1s | Problem |

### Request Count

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_request_count"]
)
```

### Filter by Endpoint

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_latency"],
  httpPath: "/api/users"
)
```

Detailed metrics guide: [references/metrics-guide.md](references/metrics-guide.md)

---

## Database Monitoring

### PostgreSQL Status

```
list_postgres_instances()
get_postgres(postgresId: "<postgres-id>")
```

### Connection Count

```
get_metrics(resourceId: "<postgres-id>", metricTypes: ["active_connections"])
```

### Query Database

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT state, count(*) FROM pg_stat_activity GROUP BY state"
)
```

### Find Slow Queries

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"
)
```

### Key-Value Store

```
list_key_value()
get_key_value(keyValueId: "<kv-id>")
```

---

## Log Monitoring

### Recent Logs

```
list_logs(resource: ["<service-id>"], limit: 100)
```

### Error Logs

```
list_logs(resource: ["<service-id>"], level: ["error"], limit: 50)
```

### Search Logs

```
list_logs(resource: ["<service-id>"], text: ["timeout", "error"], limit: 50)
```

### Filter by Time

```
list_logs(
  resource: ["<service-id>"],
  startTime: "2024-01-15T10:00:00Z",
  endTime: "2024-01-15T11:00:00Z"
)
```

### Stream Logs (CLI)

```bash
render logs -r <service-id> --tail -o text
```

---

## Quick Reference

### MCP Tools

```
# Services
list_services()
get_service(serviceId: "<id>")
list_deploys(serviceId: "<id>", limit: 5)

# Logs
list_logs(resource: ["<id>"], level: ["error"], limit: 100)
list_logs(resource: ["<id>"], text: ["search"], limit: 50)

# Metrics
get_metrics(resourceId: "<id>", metricTypes: ["cpu_usage", "memory_usage"])
get_metrics(resourceId: "<id>", metricTypes: ["http_latency"], httpLatencyQuantile: 0.95)
get_metrics(resourceId: "<id>", metricTypes: ["http_request_count"])

# Database
list_postgres_instances()
get_postgres(postgresId: "<id>")
query_render_postgres(postgresId: "<id>", sql: "SELECT ...")
get_metrics(resourceId: "<postgres-id>", metricTypes: ["active_connections"])

# Key-Value
list_key_value()
get_key_value(keyValueId: "<id>")
```

### CLI Commands (Fallback)

Use these if MCP tools are unavailable:

```bash
# Service status
render services -o json
render services instances <service-id>

# Deployments
render deploys list <service-id> -o json

# Logs
render logs -r <service-id> --tail -o text          # Stream logs
render logs -r <service-id> --level error -o json   # Error logs
render logs -r <service-id> --type deploy -o json   # Build logs

# Database
render psql <database-id>                           # Connect to PostgreSQL

# SSH for live debugging
render ssh <service-id>
```

### Healthy Service Indicators

| Indicator | Healthy | Warning | Critical |
|-----------|---------|---------|----------|
| Deploy Status | `live` | `update_in_progress` | `build_failed` |
| Error Rate | <0.1% | 0.1-1% | >1% |
| p95 Latency | <500ms | 500ms-2s | >2s |
| CPU Usage | <70% | 70-90% | >90% |
| Memory Usage | <80% | 80-95% | >95% |

---

## References

- **Metrics guide:** [references/metrics-guide.md](references/metrics-guide.md)

## Related Skills

- **deploy:** Deploy new applications to Render
- **debug:** Diagnose and fix deployment failures
