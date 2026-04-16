# Quick Debugging Workflows

Step-by-step MCP tool sequences for common debugging scenarios.

## Deploy Failures

### "Why did my deploy fail?"

```
# 1. Find the failed deploy
list_deploys(serviceId: "<service-id>", limit: 5)
# Look for status: build_failed, update_failed, or canceled

# 2. Get deploy details
get_deploy(serviceId: "<service-id>", deployId: "<deploy-id>")
# Check finishedAt, status, and any error messages

# 3. Check build logs
list_logs(
  resource: ["<service-id>"],
  type: ["build"],
  limit: 200
)
# Look for error messages, failed commands, missing dependencies

# 4. Search for specific errors
list_logs(
  resource: ["<service-id>"],
  text: ["error", "failed", "not found"],
  limit: 100
)
```

**Common causes:**
- Missing dependencies in package.json/requirements.txt
- Build command syntax errors
- Missing environment variables during build
- Build timeout (>15 min on free tier)

---

## Runtime Crashes

### "Why is my app crashing?"

```
# 1. Get runtime error logs
list_logs(
  resource: ["<service-id>"],
  level: ["error"],
  limit: 100
)

# 2. Check for missing env vars (most common)
list_logs(
  resource: ["<service-id>"],
  text: ["KeyError", "undefined", "not defined"],
  limit: 50
)

# 3. Check memory usage (OOM crashes)
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["memory_usage", "memory_limit"]
)

# 4. Get service config to review
get_service(serviceId: "<service-id>")
# Check envVars, startCommand, healthCheckPath
```

**Common causes:**
- Missing environment variables
- Port binding to localhost instead of 0.0.0.0
- Unhandled exceptions
- Out of memory (exit code 137)

---

## Performance Issues

### "Why is my app slow?"

```
# 1. Check HTTP latency (p95)
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_latency"],
  httpLatencyQuantile: 0.95
)
# >500ms p95 indicates performance issues

# 2. Check CPU usage (might be compute-bound)
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage", "cpu_limit"]
)
# >80% sustained CPU = upgrade or optimize

# 3. Check for slow endpoints (5xx errors often indicate timeouts)
list_logs(
  resource: ["<service-id>"],
  statusCode: ["500", "502", "503", "504"],
  limit: 50
)

# 4. If database-related, check slow queries
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"
)
```

**Common causes:**
- Slow database queries (missing indexes)
- External API timeouts
- CPU-intensive operations
- Memory pressure causing GC pauses

---

## Database Issues

### "Why can't my app connect to the database?"

```
# 1. Check for connection errors in logs
list_logs(
  resource: ["<service-id>"],
  text: ["ECONNREFUSED", "connection refused", "ETIMEDOUT"],
  limit: 50
)

# 2. Verify database exists and is running
list_postgres_instances()
# Check status is active

# 3. Check database connection count
get_metrics(
  resourceId: "<postgres-id>",
  metricTypes: ["active_connections"]
)
# Near max = connection pool exhaustion

# 4. Query connection status directly
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT state, count(*) FROM pg_stat_activity GROUP BY state"
)

# 5. Verify DATABASE_URL is set in service
get_service(serviceId: "<service-id>")
# Check envVars includes DATABASE_URL
```

**Common causes:**
- DATABASE_URL not set or incorrect
- Connection pool exhaustion
- Database not provisioned yet
- SSL configuration issues

---

## Health Verification

### "Is my app healthy after deploy?"

```
# 1. Check deploy status
list_deploys(serviceId: "<service-id>", limit: 1)
# Should show status: "live"

# 2. Wait 2-3 min, then check for errors
list_logs(
  resource: ["<service-id>"],
  level: ["error"],
  limit: 20
)
# Should be empty or only expected errors

# 3. Check HTTP requests are coming through
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_request_count"]
)
# Should see requests if service is being used

# 4. Check resource usage is normal
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage", "memory_usage"]
)
# CPU <70%, Memory <80% of limit
```

---

## Specific Error Patterns

### Missing Environment Variable

```
# 1. Identify missing variable from logs
list_logs(
  resource: ["<service-id>"],
  text: ["KeyError", "undefined", "not defined"],
  limit: 20
)

# 2. Check current service config
get_service(serviceId: "<service-id>")

# 3. Add missing variable
update_environment_variables(
  serviceId: "<service-id>",
  envVars: [{"key": "MISSING_VAR", "value": "value"}]
)

# 4. Redeploy happens automatically, verify
list_deploys(serviceId: "<service-id>", limit: 1)
```

### Port Binding Error

```
# 1. Check for port errors
list_logs(
  resource: ["<service-id>"],
  text: ["EADDRINUSE", "address already in use"],
  limit: 20
)

# 2. Check service configuration
get_service(serviceId: "<service-id>")
# Verify startCommand uses $PORT

# 3. Fix requires code change:
# - Read PORT from environment
# - Bind to 0.0.0.0, not localhost
# - Push fix and redeploy
```

### Out of Memory

```
# 1. Confirm OOM from logs
list_logs(
  resource: ["<service-id>"],
  text: ["heap out of memory", "Killed", "OOMKilled"],
  limit: 20
)

# 2. Check memory trend before crash
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["memory_usage", "memory_limit"],
  startTime: "<1-hour-before-crash>"
)

# 3. If steady growth = memory leak
# If sudden spike = large request/data

# 4. Options:
# - Optimize memory usage in code
# - Process data in streams/chunks
# - Upgrade to higher plan
```

### Health Check Timeout

```
# 1. Check for health check errors
list_logs(
  resource: ["<service-id>"],
  text: ["Health check", "failed to become healthy"],
  limit: 20
)

# 2. Check if app started successfully
list_logs(
  resource: ["<service-id>"],
  text: ["listening", "started", "running"],
  limit: 20
)

# 3. Check startup time via CPU
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage"]
)
# High sustained CPU during startup = slow initialization

# 4. Verify:
# - App binds to 0.0.0.0:$PORT
# - Health check endpoint exists
# - App starts within timeout (300s default)
```
