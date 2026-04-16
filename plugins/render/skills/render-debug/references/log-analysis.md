# Render Log Analysis Guide

How to read, interpret, and analyze Render logs to identify deployment and runtime issues.

## Understanding Render Logs

### Log Types

Render provides different log types for different purposes:

1. **Deploy Logs** - Build and deployment process
2. **Runtime Logs** - Application output after deployment
3. **System Logs** - Render platform events

### Log Levels

Logs are categorized by severity:

- **error** - Critical errors requiring attention
- **warn** - Warning messages (potential issues)
- **info** - Informational messages
- **debug** - Detailed debugging information

## CLI Commands for Logs

### Basic Log Retrieval

**Get deploy logs (build/deployment phase):**
```bash
render logs -r <service-id> --type deploy -o json
```

**Get runtime logs (after service starts):**
```bash
render logs -r <service-id> -o json
```

**Get error logs only:**
```bash
render logs -r <service-id> --level error -o json
```

**Get recent logs (limit output):**
```bash
render logs -r <service-id> --limit 200 -o json
```

**Stream logs in real-time:**
```bash
render logs -r <service-id> --tail -o text
```

### Advanced Filtering

**Combine filters:**
```bash
render logs -r <service-id> --type deploy --level error --limit 100 -o json
```

**Output formats:**
- `-o json` - JSON format (easier to parse)
- `-o text` - Plain text (human-readable)
- `-o yaml` - YAML format

## Reading Deploy Logs

Deploy logs show the build and deployment process. Read them **sequentially** from top to bottom.

### Typical Deploy Log Structure

```
1. Repository cloning
   → Cloning repository from git remote

2. Environment setup
   → Setting up build environment
   → Installing runtime (node, python, etc.)

3. Build phase
   → Running buildCommand
   → Installing dependencies
   → Compiling code

4. Pre-deploy checks
   → Validating configuration
   → Checking for required files

5. Deploy phase
   → Running startCommand
   → Starting service

6. Health checks
   → Waiting for service to respond
   → Verifying health check endpoint

7. Success or failure
   → Deploy succeeded
   → OR: Deploy failed with error
```

### Key Sections to Check

**1. Build Command Execution:**
```
==> Running 'npm ci'
npm WARN deprecated package@1.0.0
added 250 packages in 15s
```

Look for:
- `npm ERR!` - npm errors
- `error: ` - compilation errors
- `FATAL:` - critical build errors

**2. Start Command Execution:**
```
==> Running 'npm start'
> app@1.0.0 start
> node server.js

Server listening on port 10000
```

Look for:
- Server startup messages
- Port binding confirmation
- Error messages during startup

**3. Health Check Results:**
```
==> Checking service health at https://myapp.onrender.com/
Health check passed
Deploy succeeded
```

Look for:
- `Health check timeout` - Service not responding
- `Health check failed` - Service responding with error
- `Health check passed` - Success

## Reading Runtime Logs

Runtime logs show application output after successful deployment.

### Understanding Runtime Log Entries

Each log entry typically contains:
```json
{
  "timestamp": "2024-01-24T10:30:45.123Z",
  "level": "error",
  "message": "Database connection failed",
  "service": "web-app",
  "instance": "srv-abc123-instance-1"
}
```

### Common Runtime Log Patterns

**1. Application Startup:**
```
Server started successfully
Listening on port 10000
Database connected
```

**2. Request Handling:**
```
GET /api/users 200 - 45ms
POST /api/auth 401 - 12ms
```

**3. Errors:**
```
Error: Cannot find module 'express'
UnhandledPromiseRejectionWarning: Error: Connection timeout
TypeError: Cannot read property 'id' of undefined
```

**4. Database Operations:**
```
Connected to PostgreSQL
Query executed: SELECT * FROM users
Database connection pool: 5/20 active
```

## Identifying Error Location

### Finding the Error Line

**Look for these keywords:**
- `Error:`
- `Exception:`
- `FATAL:`
- `failed`
- `crashed`
- `timeout`
- `refused`

**Error message structure:**
```
Error: Cannot find module 'express'
    at Function.Module._resolveFilename (internal/modules/cjs/loader.js:880:15)
    at Function.Module._load (internal/modules/cjs/loader.js:725:27)
    at Module.require (internal/modules/cjs/loader.js:952:19)
    at require (internal/modules/cjs/helpers.js:88:18)
    at Object.<anonymous> (/app/server.js:1:17)  ← YOUR CODE
```

The first line with `/app/` is usually your code.

### Stack Trace Analysis

**Reading stack traces:**

1. **Error message** - Top line describes the error
2. **Stack frames** - Lines below show call path
3. **File locations** - Look for paths starting with `/app/`
4. **Line numbers** - Shows exact line in your code

**Example:**
```
ReferenceError: DATABASE_URL is not defined
    at connectDatabase (/app/database.js:15:23)  ← Error on line 15
    at startup (/app/server.js:10:5)             ← Called from line 10
    at Object.<anonymous> (/app/server.js:50:1)  ← App entry point
```

**Action:** Open `/app/database.js` line 15 to see the issue.

## Common Log Patterns by Error Type

### Missing Environment Variable

```
Error: DATABASE_URL is not defined
    at /app/config.js:12:45

ReferenceError: process.env.API_KEY is undefined

KeyError: 'JWT_SECRET'
```

**Action:** Add to render.yaml envVars

### Port Binding Error

```
Error: listen EADDRINUSE: address already in use 0.0.0.0:3000
    at Server.setupListenHandle [as _listen2] (net.js:1313:16)

Address already in use (os error 48)
```

**Action:** Update code to use `process.env.PORT`

### Database Connection Error

```
Error: connect ECONNREFUSED 127.0.0.1:5432
    at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1145:16)

could not connect to server: Connection refused
	Is the server running on host "127.0.0.1" and accepting
	TCP/IP connections on port 5432?
```

**Action:** Verify DATABASE_URL and database status

### Health Check Timeout

```
==> Checking service health at https://myapp.onrender.com/
Health check timeout after 300 seconds
Deploy failed
```

**Action:** Check port binding and add /health endpoint

### Out of Memory

```
<--- Last few GCs --->

FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
```

**Action:** Optimize memory usage or upgrade plan

## Filtering Relevant Logs

### What to Focus On

**For Build Failures:**
1. Look at build command output
2. Find first error in build logs
3. Check dependency installation section
4. Review compilation errors

**For Runtime Failures:**
1. Look at start command output
2. Check first few seconds of runtime logs
3. Look for startup errors
4. Check health check section

### What to Ignore (Usually)

- Deprecation warnings (unless they cause errors)
- Info-level messages
- Successful operation logs
- Normal request logs (200 responses)

## Tips for Efficient Log Analysis

### 1. Start with Error-Level Logs

```bash
render logs -r <service-id> --level error -o json
```

This filters out noise and shows only critical issues.

### 2. Use JSON Output for Parsing

JSON format is easier to search and parse programmatically:

```bash
render logs -r <service-id> -o json | grep "DATABASE_URL"
```

### 3. Limit Output

Don't retrieve all logs at once:

```bash
render logs -r <service-id> --limit 200 -o json
```

Most errors appear in recent logs.

### 4. Focus on Deployment Logs First

If deployment failed, deploy logs contain the error:

```bash
render logs -r <service-id> --type deploy --level error -o json
```

### 5. Use Real-Time Streaming

Watch logs as deployment happens:

```bash
render logs -r <service-id> --tail -o text
```

### 6. Search for Specific Patterns

Look for common error keywords:
- "Error:"
- "Exception"
- "failed"
- "timeout"
- "refused"
- "undefined"
- "not found"

## Troubleshooting Workflow

**Step 1:** Get error-level logs
```bash
render logs -r <service-id> --level error -o json --limit 100
```

**Step 2:** Identify error type
- Missing env var?
- Port binding issue?
- Build failure?
- Database connection?

**Step 3:** Get context
```bash
render logs -r <service-id> --limit 500 -o json
```

Read logs around the error for context.

**Step 4:** Match to error pattern
Refer to [error-patterns.md](error-patterns.md) for known patterns.

**Step 5:** Apply fix
Refer to [troubleshooting.md](troubleshooting.md) for fix procedures.

## Log Examples

### Example 1: Successful Deployment

```
==> Cloning from https://github.com/user/repo...
==> Running build command 'npm ci'
added 250 packages in 15s
==> Running start command 'npm start'
Server listening on port 10000
==> Health check passed
Deploy succeeded
```

### Example 2: Missing Environment Variable

```
==> Running start command 'npm start'
Server starting...
ReferenceError: DATABASE_URL is not defined
    at connectDatabase (/app/database.js:15:23)
Process exited with code 1
Deploy failed
```

### Example 3: Port Binding Error

```
==> Running start command 'npm start'
Server starting on port 3000...
Error: listen EADDRINUSE: address already in use 0.0.0.0:3000
Process exited with code 1
Deploy failed
```

### Example 4: Health Check Timeout

```
==> Running start command 'npm start'
Server started
==> Checking service health at https://myapp.onrender.com/
Health check timeout after 300 seconds
Deploy failed
```

## Quick Reference

### Log Commands Cheat Sheet

```bash
# Error logs only
render logs -r <id> --level error -o json

# Deploy logs
render logs -r <id> --type deploy -o json

# Stream logs
render logs -r <id> --tail -o text

# Recent logs
render logs -r <id> --limit 200 -o json

# All options combined
render logs -r <id> --type deploy --level error --limit 100 -o json
```

### Error Keywords to Search For

- `Error:`
- `Exception`
- `FATAL`
- `failed`
- `timeout`
- `refused`
- `undefined`
- `not found`
- `cannot`
- `invalid`

## Next Steps

After analyzing logs:
1. Identify error pattern in [error-patterns.md](error-patterns.md)
2. Follow fix procedure in [troubleshooting.md](troubleshooting.md)
3. Apply fix and redeploy
4. Monitor logs during next deployment
