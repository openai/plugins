# Render Deployment Error Patterns

Comprehensive catalog of common deployment errors on Render, their causes, and fixes. Organized by frequency and category.

## MCP Quick Detection

Use these MCP queries to quickly detect each error pattern:

| Error Type | MCP Detection Query |
|------------|-------------------|
| Missing Env Var | `list_logs(resource: ["<id>"], text: ["KeyError", "not defined", "undefined"], limit: 50)` |
| Port Binding | `list_logs(resource: ["<id>"], text: ["EADDRINUSE", "address already in use"], limit: 20)` |
| Missing Dependency | `list_logs(resource: ["<id>"], text: ["Cannot find module", "ModuleNotFoundError"], limit: 50)` |
| Database Connection | `list_logs(resource: ["<id>"], text: ["ECONNREFUSED", "could not connect"], limit: 50)` |
| Health Check | `list_logs(resource: ["<id>"], text: ["Health check", "failed to become healthy"], limit: 20)` |
| OOM | `list_logs(resource: ["<id>"], text: ["heap out of memory", "OOMKilled", "exit code 137"], limit: 20)` |
| Build Failure | `list_logs(resource: ["<id>"], type: ["build"], text: ["error", "failed"], limit: 100)` |

---

## Most Common Errors

### 1. MISSING_ENV_VAR (Most Common)

**Description:** Application crashes because required environment variable is not set.

**MCP Detection:**
```
list_logs(
  resource: ["<service-id>"],
  text: ["KeyError", "not defined", "undefined", "Missing required environment"],
  limit: 50
)
```

**Patterns to Match:**
- `ReferenceError: DATABASE_URL is not defined`
- `TypeError: Cannot read property 'DATABASE_URL' of undefined`
- `KeyError: 'API_KEY'`
- `KeyError: 'JWT_SECRET'`
- `Environment variable not found: DATABASE_URL`
- `Missing required environment variable`
- `process.env.DATABASE_URL is undefined`
- `os.environ['DATABASE_URL'] KeyError`

**Common Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - Authentication secret
- `API_KEY` - Third-party API keys
- `SECRET_KEY` - Django secret key
- `NEXTAUTH_SECRET` - NextAuth.js secret
- `SESSION_SECRET` - Session encryption key

**Root Causes:**
1. Variable not declared in render.yaml
2. Variable marked with `sync: false` but user didn't fill in Dashboard
3. Typo in variable name (case-sensitive!)
4. Variable added to code but not to render.yaml

**Fix Strategy:**

**Step 1:** Add to render.yaml
```yaml
envVars:
  # For database connections
  - key: DATABASE_URL
    fromDatabase:
      name: postgres
      property: connectionString

  # For secrets (user fills in Dashboard)
  - key: JWT_SECRET
    sync: false
  - key: API_KEY
    sync: false

  # For generated secrets
  - key: SESSION_SECRET
    generateValue: true

  # For hardcoded config
  - key: NODE_ENV
    value: production
```

**Step 2:** For existing services, use MCP to add env vars directly:
```
update_environment_variables(
  serviceId: "<service-id>",
  envVars: [
    {"key": "DATABASE_URL", "value": "<connection-string>"},
    {"key": "JWT_SECRET", "value": "<secret-value>"}
  ]
)
```

**Step 3:** Commit and push (for Blueprint-managed services):
```bash
git add render.yaml
git commit -m "Add missing environment variables"
git push origin main
```

**Step 4:** If `sync: false` is used, remind user to fill values in Dashboard at:
`https://dashboard.render.com/web/[service-name]/env`

**Prevention:**
- Always declare ALL env vars in render.yaml
- Use `sync: false` for secrets
- Double-check variable names (case-sensitive)
- Test locally with `.env` file first

---

### 2. PORT_BINDING_ERROR (Second Most Common)

**MCP Detection:**
```
list_logs(
  resource: ["<service-id>"],
  text: ["EADDRINUSE", "address already in use", "cannot assign requested address"],
  limit: 20
)
```

**Description:** Application not binding to correct port or host.

**Patterns to Match:**
- `EADDRINUSE: address already in use`
- `Error: listen EADDRINUSE: address already in use 0.0.0.0:3000`
- `Address already in use (os error 48)`
- `Failed to bind to 0.0.0.0:3000`
- `Health check timeout` (often caused by wrong port)
- `cannot assign requested address`

**Root Causes:**
1. App hardcodes port instead of using `$PORT` environment variable
2. App binds to `localhost` or `127.0.0.1` instead of `0.0.0.0`
3. Multiple services trying to use same port
4. App doesn't read PORT environment variable

**Fix Strategy:**

**Node.js / Express:**
```javascript
// Before (WRONG)
app.listen(3000);
app.listen(3000, 'localhost');

// After (CORRECT)
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

**Python / Flask:**
```python
# Before (WRONG)
app.run(port=5000)
app.run(host='localhost', port=5000)

# After (CORRECT)
import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

**Python / Django (gunicorn):**
```yaml
# In render.yaml startCommand
startCommand: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

**Go:**
```go
// Before (WRONG)
http.ListenAndServe(":3000", handler)

// After (CORRECT)
port := os.Getenv("PORT")
if port == "" {
    port = "3000"
}
http.ListenAndServe(":"+port, handler)
```

**Prevention:**
- Always use `process.env.PORT` (or equivalent)
- Always bind to `0.0.0.0`
- Test with PORT=10000 locally

---

### 3. MISSING_DEPENDENCY

**MCP Detection:**
```
list_logs(
  resource: ["<service-id>"],
  text: ["Cannot find module", "ModuleNotFoundError", "ImportError", "package not found"],
  limit: 50
)
```

**Description:** Required package or module not installed.

**Patterns to Match:**
- `Cannot find module 'express'`
- `Error: Cannot find module './config'`
- `ModuleNotFoundError: No module named 'django'`
- `ImportError: No module named flask`
- `package not found: github.com/gin-gonic/gin`
- `error: could not find `tokio` in the list of imported crates`

**Root Causes:**
1. Dependency not in package.json/requirements.txt/go.mod
2. Wrong build command
3. Build cache issues
4. Dependency only in devDependencies

**Fix Strategy:**

**Node.js:**
```json
// Add to package.json
{
  "dependencies": {
    "express": "^4.18.0",
    "pg": "^8.11.0"
  }
}
```

**Python:**
```
# Add to requirements.txt
django==4.2.0
psycopg2-binary==2.9.5
```

**Go:**
```bash
# Update go.mod
go get github.com/gin-gonic/gin
```

**Prevention:**
- Keep dependencies in sync with code
- Use lock files (package-lock.json, Pipfile.lock)
- Test build locally first

---

## Configuration Errors

### 4. DATABASE_CONNECTION_FAILED

**MCP Detection:**
```
list_logs(
  resource: ["<service-id>"],
  text: ["ECONNREFUSED", "could not connect to server", "connection refused", "ETIMEDOUT"],
  limit: 50
)
```

**MCP Investigation:**
```
# Check database status
list_postgres_instances()

# Check connection metrics
get_metrics(
  resourceId: "<postgres-id>",
  metricTypes: ["active_connections"]
)

# Query database directly
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT count(*) FROM pg_stat_activity"
)
```

**Description:** Cannot connect to database.

**Patterns to Match:**
- `ECONNREFUSED 127.0.0.1:5432`
- `could not connect to server: Connection refused`
- `FATAL: password authentication failed`
- `connect ETIMEDOUT`
- `Redis connection to 127.0.0.1:6379 failed`
- `SSL SYSCALL error: EOF detected`

**Root Causes:**
1. DATABASE_URL not set
2. Wrong connection string format
3. Database not provisioned
4. SSL settings incorrect
5. Connection timeout too short

**Fix Strategy:**

**Step 1:** Verify DATABASE_URL is set in render.yaml
```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: postgres
      property: connectionString
```

**Step 2:** Enable SSL if needed (Node.js example)
```javascript
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? {
    rejectUnauthorized: false
  } : false
});
```

**Step 3:** Check database provisioned
```bash
render services -o json
# Verify database exists and is active
```

---

### 5. INVALID_BUILD_COMMAND

**Description:** Build command fails.

**Patterns to Match:**
- `npm ERR! missing script: build`
- `sh: line 1: webpack: command not found`
- `error: failed to compile`
- `SyntaxError: Unexpected token`
- `Error: Command failed with exit code 1`

**Root Causes:**
1. Wrong build script name
2. Build tools not installed
3. Syntax errors in code
4. Build script doesn't exist

**Fix Strategy:**

**Node.js - Check package.json:**
```json
{
  "scripts": {
    "build": "tsc",  // or webpack, vite, etc.
    "start": "node dist/index.js"
  }
}
```

**Render.yaml:**
```yaml
buildCommand: npm ci && npm run build
```

**Python - No build step needed:**
```yaml
buildCommand: pip install -r requirements.txt
```

---

## Runtime Errors

### 6. HEALTH_CHECK_TIMEOUT

**MCP Detection:**
```
list_logs(
  resource: ["<service-id>"],
  text: ["Health check", "failed to become healthy", "timeout"],
  limit: 30
)
```

**MCP Investigation:**
```
# Check if service is binding correctly
list_logs(
  resource: ["<service-id>"],
  text: ["listening", "started", "running on port"],
  limit: 20
)

# Check CPU/Memory during startup
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage", "memory_usage"]
)
```

**Description:** Service doesn't respond to health checks within timeout period.

**Patterns to Match:**
- `Health check timeout`
- `failed to become healthy within 300 seconds`
- `Service did not pass health check`
- `GET / returned status 404`

**Root Causes:**
1. No health check endpoint implemented
2. App not binding to correct port
3. Slow application startup
4. Health check path incorrect
5. Application crashes during startup

**Fix Strategy:**

**Step 1:** Add health check endpoint

**Node.js:**
```javascript
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: Date.now() });
});
```

**Python / Flask:**
```python
@app.route('/health')
def health():
    return {'status': 'ok'}, 200
```

**Step 2:** Configure in render.yaml
```yaml
healthCheckPath: /health
```

**Step 3:** Ensure fast startup
- Move slow initialization to after server start
- Use lazy loading for heavy operations

---

### 7. OUT_OF_MEMORY (OOM)

**MCP Detection:**
```
list_logs(
  resource: ["<service-id>"],
  text: ["heap out of memory", "Killed", "OOMKilled", "exit code 137", "cannot allocate memory"],
  limit: 30
)
```

**MCP Investigation:**
```
# Check memory usage trend
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["memory_usage", "memory_limit"]
)

# Check if memory usage spiked
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["memory_usage"],
  startTime: "<before-crash-time>"
)
```

**Description:** Application exceeds available memory.

**Patterns to Match:**
- `JavaScript heap out of memory`
- `FATAL ERROR: Reached heap limit Allocation failed`
- `Killed` (exit code 137)
- `OOMKilled`
- `cannot allocate memory`

**Root Causes:**
1. Memory leak in application
2. Processing too much data at once
3. Free tier limit (512 MB) exceeded
4. Large dependency tree
5. No garbage collection optimization

**Fix Strategy:**

**Short-term fixes:**

**Node.js - Increase heap size (if on paid plan):**
```yaml
envVars:
  - key: NODE_OPTIONS
    value: --max-old-space-size=2048
```

**Python - Optimize memory:**
```python
# Process data in chunks
for chunk in pd.read_csv('large_file.csv', chunksize=1000):
    process(chunk)
```

**Long-term fixes:**
1. Profile memory usage
2. Fix memory leaks
3. Optimize data structures
4. Upgrade to higher plan with more RAM

---

### 8. UNCAUGHT_EXCEPTION

**Description:** Unhandled error crashes the application.

**Patterns to Match:**
- `UnhandledPromiseRejectionWarning`
- `Uncaught Error:`
- `Traceback (most recent call last):`
- `panic: runtime error:`
- `Fatal error:`

**Root Causes:**
1. Missing error handling
2. Async errors not caught
3. Null pointer exceptions
4. Division by zero

**Fix Strategy:**

**Node.js - Add error handlers:**
```javascript
// Catch all errors
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
  process.exit(1);
});

// Express error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});
```

**Python - Add try/catch:**
```python
try:
    # Your code
    result = risky_operation()
except Exception as e:
    logger.error(f"Error: {e}")
    # Handle gracefully
```

---

## Build Errors

### 9. BUILD_TIMEOUT

**Description:** Build takes longer than allowed time.

**Patterns to Match:**
- `Build timed out after 15 minutes`
- `Command timed out`
- `Build exceeded time limit`

**Root Causes:**
1. Too many dependencies
2. Large dependency compilation (native modules)
3. Slow build scripts
4. Network issues downloading packages

**Fix Strategy:**

**Optimize dependencies:**
```json
// Remove unused dependencies
{
  "dependencies": {
    // Only what you actually use
  }
}
```

**Use faster build commands:**
```yaml
buildCommand: npm ci --prefer-offline && npm run build
```

**Consider upgrading:**
- Free tier: 15 minute build timeout
- Paid tiers: Longer timeouts available

---

### 10. DOCKER_BUILD_FAILED

**Description:** Docker image build fails.

**Patterns to Match:**
- `failed to solve with frontend dockerfile.v0`
- `ERROR [internal] load metadata for`
- `failed to compute cache key`
- `COPY failed:`
- `RUN returned a non-zero code`

**Root Causes:**
1. Invalid Dockerfile syntax
2. Base image not found
3. COPY source doesn't exist
4. RUN command fails
5. Build context too large

**Fix Strategy:**

**Check Dockerfile:**
```dockerfile
# Use valid base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY package*.json ./
RUN npm ci

# Then copy source
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 10000

# Start
CMD ["npm", "start"]
```

**Add .dockerignore:**
```
node_modules
.git
.env
*.log
```

---

## Database Errors

### 11. DATABASE_MIGRATION_FAILED

**Description:** Database migration fails during build.

**Patterns to Match:**
- `ProgrammingError: relation "users" already exists`
- `django.db.migrations.exceptions.InconsistentMigrationHistory`
- `Prisma migration failed`
- `Migration failed to apply`

**Root Causes:**
1. Migration conflicts
2. Database already has schema
3. Migration dependencies missing
4. Database locked

**Fix Strategy:**

**Django:**
```bash
# Check migration status
python manage.py showmigrations

# Fake initial migration if schema exists
python manage.py migrate --fake-initial
```

**Rails:**
```bash
# Check schema exists
bundle exec rails db:migrate:status

# Reset if needed (CAUTION: data loss)
bundle exec rails db:reset
```

**Prisma:**
```bash
# Deploy migrations
npx prisma migrate deploy

# Or generate client only
npx prisma generate
```

---

## Security & Permission Errors

### 12. PERMISSION_DENIED

**Description:** Application doesn't have permission to access resource.

**Patterns to Match:**
- `EACCES: permission denied`
- `Error: EPERM: operation not permitted`
- `PermissionError: [Errno 13] Permission denied`

**Root Causes:**
1. Trying to write to read-only filesystem
2. Wrong file permissions
3. Trying to bind to privileged port (<1024)

**Fix Strategy:**

**Use allowed directories:**
- `/tmp` - writable temporary storage
- `/var` - avoid, not writable
- Use environment variables for file paths

**Use correct port:**
```yaml
envVars:
  - key: PORT
    value: 10000  # Use 10000, not 80 or 443
```

---

## Dependency Version Errors

### 13. VERSION_MISMATCH

**Description:** Incompatible dependency versions.

**Patterns to Match:**
- `npm ERR! peer dep missing`
- `npm ERR! ERESOLVE unable to resolve dependency tree`
- `Requires: Python >=3.8, but current version is 3.7`
- `requires Go version 1.20 or later`

**Fix Strategy:**

**Node.js - Fix peer dependencies:**
```bash
npm install --legacy-peer-deps
```

Or update package.json:
```json
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
```

**Python - Specify version:**
```
# runtime.txt
python-3.11.5
```

**Go - Update go.mod:**
```go
go 1.21
```

---

## Resource Errors

### 14. DISK_SPACE_EXCEEDED

**Description:** Running out of disk space during build or runtime.

**Patterns to Match:**
- `No space left on device`
- `ENOSPC: no space left on device`
- `Disk quota exceeded`

**Root Causes:**
1. Large build artifacts
2. Log files growing too large
3. Too many dependencies

**Fix Strategy:**

**Clean build artifacts:**
```yaml
buildCommand: npm ci && npm run build && npm prune --production
```

**Remove unnecessary files:**
```bash
# In build command
rm -rf .git tests/ docs/
```

---

## Networking Errors

### 15. EXTERNAL_API_TIMEOUT

**Description:** External API calls timing out.

**Patterns to Match:**
- `ETIMEDOUT`
- `ESOCKETTIMEDOUT`
- `Request timeout`
- `connect ETIMEDOUT`

**Root Causes:**
1. API endpoint down
2. Network issues
3. Timeout too short
4. Rate limiting

**Fix Strategy:**

**Add retries and timeout:**
```javascript
const axios = require('axios');

const api = axios.create({
  timeout: 10000,
  retry: {
    retries: 3,
    retryDelay: (retryCount) => retryCount * 1000
  }
});
```

---

## Quick Reference Matrix

| Error Pattern | Frequency | Severity | Typical Fix Time |
|---------------|-----------|----------|------------------|
| MISSING_ENV_VAR | Very High | High | 5 minutes |
| PORT_BINDING_ERROR | High | High | 10 minutes |
| MISSING_DEPENDENCY | High | Medium | 5 minutes |
| DATABASE_CONNECTION | Medium | High | 15 minutes |
| HEALTH_CHECK_TIMEOUT | Medium | Medium | 15 minutes |
| OUT_OF_MEMORY | Medium | Medium | 30+ minutes |
| BUILD_TIMEOUT | Low | Medium | 30+ minutes |
| UNCAUGHT_EXCEPTION | Medium | High | Varies |

## Debugging Priority Order

1. **Check environment variables first** (Most common)
2. **Verify port binding** (Second most common)
3. **Check build logs for errors**
4. **Verify database connections**
5. **Check for missing dependencies**
6. **Review application logs**
7. **Check resource usage**

## Exit Code Reference

Common exit codes and their meanings:

| Exit Code | Signal | Meaning | Common Cause |
|-----------|--------|---------|--------------|
| 0 | - | Success | Normal termination |
| 1 | - | General error | Application error, uncaught exception |
| 2 | - | Misuse | Invalid arguments, bad command usage |
| 126 | - | Cannot execute | Permission denied |
| 127 | - | Not found | Command or binary not found |
| 128+N | Signal N | Killed by signal | See signal codes below |
| 130 | SIGINT (2) | Interrupted | Ctrl+C, manual interrupt |
| 137 | SIGKILL (9) | Killed | Out of memory (OOM), forced kill |
| 139 | SIGSEGV (11) | Segmentation fault | Memory access violation |
| 143 | SIGTERM (15) | Terminated | Graceful shutdown request |

**Note:** Exit codes 128+N indicate the process was terminated by signal N. For example, 137 = 128 + 9 (SIGKILL).

## Next Steps

After identifying error pattern:
1. Review [troubleshooting.md](troubleshooting.md) for detailed fix procedures
2. Review [log-analysis.md](log-analysis.md) for log reading tips
3. Apply fix and monitor deployment
