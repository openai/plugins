---
name: render-debug
description: Debug failed Render deployments by analyzing logs, metrics, and database state. Identifies errors (missing env vars, port binding, OOM, etc.) and suggests fixes. Use when deployments fail, services won't start, or users mention errors, logs, or debugging.
license: MIT
compatibility: Requires Render MCP tools or CLI
metadata:
  author: Render
  version: "1.1.0"
  category: debugging
---

# Debug Render Deployments

Analyze deployment failures using logs, metrics, and database queries. Identify root causes and apply fixes.

## When to Use This Skill

Activate this skill when:
- Deployment fails on Render
- Service won't start or keeps crashing
- User mentions errors, logs, or debugging
- Health checks are timing out
- Application errors in production
- Performance issues (slow responses)
- Database connection problems

## Prerequisites

**MCP tools (preferred):** Test with `list_services()` - provides structured data

**CLI (fallback):** `render --version` - use if MCP tools unavailable

**Authentication:** For MCP, use an API key (set in the MCP config or via the `RENDER_API_KEY` env var, depending on tool). For CLI, verify with `render whoami -o json`.

**Workspace:** `get_selected_workspace()` or `render workspace current -o json`

> **Note:** MCP tools require the Render MCP server. If unavailable, use the CLI for logs and deploy status; metrics and structured database queries require MCP.

## MCP Setup

If `list_services()` fails, set up the Render MCP server. For detailed per-tool walkthroughs, see **render-mcp**.

**Quick setup:** Add the Render MCP server to your AI tool's MCP config:
- **URL:** `https://mcp.render.com/mcp`
- **Auth header:** `Authorization: Bearer <YOUR_API_KEY>`
- **API key:** `https://dashboard.render.com/u/*/settings#api-keys`

After configuring, restart your tool and retry `list_services()`. Then set your workspace with `list_workspaces()` / `get_selected_workspace()`.

---

## Debugging Workflow

### Step 1: Identify Failed Service

```
list_services()
```

If MCP isn't configured, ask whether to set it up (preferred) or continue with CLI. Then proceed.

Look for services with failed status. Get details:

```
get_service(serviceId: "<id>")
```

### Step 2: Retrieve Logs

**Build/Deploy Logs (most failures):**
```
list_logs(resource: ["<service-id>"], type: ["build"], limit: 200)
```

**Runtime Error Logs:**
```
list_logs(resource: ["<service-id>"], level: ["error"], limit: 100)
```

**Search for Specific Errors:**
```
list_logs(resource: ["<service-id>"], text: ["KeyError", "ECONNREFUSED"], limit: 50)
```

**HTTP Error Logs:**
```
list_logs(resource: ["<service-id>"], statusCode: ["500", "502", "503"], limit: 50)
```

### Step 3: Analyze Error Patterns

Match log errors against known patterns:

| Error | Log Pattern | Common Fix |
|-------|-------------|------------|
| **MISSING_ENV_VAR** | `KeyError`, `not defined` | Add to render.yaml or `update_environment_variables` |
| **PORT_BINDING** | `EADDRINUSE` | Use `0.0.0.0:$PORT` |
| **MISSING_DEPENDENCY** | `Cannot find module` | Add to package.json/requirements.txt |
| **DATABASE_CONNECTION** | `ECONNREFUSED :5432` | Check DATABASE_URL, DB status |
| **HEALTH_CHECK** | `Health check timeout` | Add /health endpoint, check port binding |
| **OUT_OF_MEMORY** | `heap out of memory`, exit 137 | Optimize memory or upgrade plan |
| **BUILD_FAILURE** | `Command failed` | Fix build command or dependencies |

Full error catalog: [references/error-patterns.md](references/error-patterns.md)

**If errors repeat across deploys:** Switch from incremental fixes to a broader sweep. Scan the codebase/config for all likely causes in that error class (related env vars, build config, dependencies, or type errors) and address them together before the next redeploy.

### Step 4: Check Metrics (Performance Issues)

For crashes, slow responses, or resource issues:

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage", "memory_usage", "memory_limit"]
)
```

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_latency"],
  httpLatencyQuantile: 0.95
)
```

Detailed metrics guide: [references/metrics-debugging.md](references/metrics-debugging.md)

### Step 5: Debug Database Issues

For database-related errors:

```
# Check database status
list_postgres_instances()

# Check connections
get_metrics(resourceId: "<postgres-id>", metricTypes: ["active_connections"])

# Query directly
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT state, count(*) FROM pg_stat_activity GROUP BY state"
)
```

Detailed database guide: [references/database-debugging.md](references/database-debugging.md)

### Step 6: Apply Fix

**For environment variables:**
```
update_environment_variables(
  serviceId: "<service-id>",
  envVars: [{"key": "MISSING_VAR", "value": "value"}]
)
```

**For code changes:**
1. Edit the source file
2. Commit and push
3. Deploy triggers automatically (if auto-deploy enabled)

### Step 7: Verify Fix

```
# Check deploy status
list_deploys(serviceId: "<service-id>", limit: 1)

# Check for new errors
list_logs(resource: ["<service-id>"], level: ["error"], limit: 20)

# Check metrics
get_metrics(resourceId: "<service-id>", metricTypes: ["http_request_count"])
```

---

## Quick Workflows

Pre-built debugging sequences for common scenarios:

| Scenario | Workflow |
|----------|----------|
| Deploy failed | `list_deploys` → `list_logs(type: build)` → fix → redeploy |
| App crashing | `list_logs(level: error)` → `get_metrics(memory)` → fix |
| App slow | `get_metrics(http_latency)` → `get_metrics(cpu)` → `query_postgres` |
| DB connection | `list_postgres` → `get_metrics(connections)` → `query_postgres` |
| Post-deploy check | `list_deploys` → `list_logs(error)` → `get_metrics` |

Detailed workflows: [references/quick-workflows.md](references/quick-workflows.md)

---

## Quick Reference

### MCP Tools

```
# Service Discovery
list_services()
get_service(serviceId: "<id>")
list_postgres_instances()

# Logs
list_logs(resource: ["<id>"], level: ["error"], limit: 100)
list_logs(resource: ["<id>"], type: ["build"], limit: 200)
list_logs(resource: ["<id>"], text: ["search"], limit: 50)

# Metrics
get_metrics(resourceId: "<id>", metricTypes: ["cpu_usage", "memory_usage"])
get_metrics(resourceId: "<id>", metricTypes: ["http_latency"], httpLatencyQuantile: 0.95)

# Database
query_render_postgres(postgresId: "<id>", sql: "SELECT ...")

# Deployments
list_deploys(serviceId: "<id>", limit: 5)

# Environment Variables
update_environment_variables(serviceId: "<id>", envVars: [{key, value}])
```

### CLI Commands (Fallback)

```bash
render services -o json
render logs -r <service-id> --level error -o json
render logs -r <service-id> --tail -o text
render deploys create <service-id> --wait
```

---

## References

- **Error patterns:** [references/error-patterns.md](references/error-patterns.md)
- **Metrics debugging:** [references/metrics-debugging.md](references/metrics-debugging.md)
- **Database debugging:** [references/database-debugging.md](references/database-debugging.md)
- **Quick workflows:** [references/quick-workflows.md](references/quick-workflows.md)
- **Log analysis:** [references/log-analysis.md](references/log-analysis.md)
- **Troubleshooting:** [references/troubleshooting.md](references/troubleshooting.md)

## Related Skills

- **render-deploy** — Deploy new applications to Render
- **render-monitor** — Ongoing service health monitoring
- **render-mcp** — MCP server setup and tool catalog
