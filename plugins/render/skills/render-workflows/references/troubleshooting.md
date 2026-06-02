# Troubleshooting

Common issues and fixes when developing with Render Workflows, sourced from the SDK source code and official docs.

## Contents

- Task server issues
- Task registration issues
- Task execution issues
- Client issues
- Connection and networking
- Local development gotchas
- Limits reference

## Task Server Issues

### Task server won't start

**Symptom:** `render workflows dev` fails or hangs.

| Cause | Fix |
|-------|-----|
| CLI version < 2.11.0 | Run `render --version` to check. Upgrade: `brew upgrade render` (macOS) or reinstall via the install script. |
| Wrong start command | Python: `render workflows dev -- python workflows/main.py`. TypeScript: `render workflows dev -- npx tsx workflows/main.ts`. |
| Missing `app.start()` (Python) | Add `if __name__ == "__main__": app.start()` at the bottom of your entry point. |
| Port already in use | Use `--port` flag: `render workflows dev --port 8121 -- ...` |

### `app.start()` fails with `ValueError` (Python)

**Symptom:** `ValueError` about missing `RENDER_SDK_MODE` or `RENDER_SDK_SOCKET_PATH`.

**Cause:** `app.start()` expects env vars that the Render CLI sets automatically. Running `python main.py` directly (without the CLI) triggers this.

**Fix:** Always start via the CLI: `render workflows dev -- python workflows/main.py`. The CLI sets the required env vars.

### Auto-start crashes with `process.exit(1)` (TypeScript)

**Symptom:** Process exits immediately with no useful error message.

**Cause:** The SDK auto-starts the task server via `setImmediate` when `RENDER_SDK_SOCKET_PATH` is set. If `startTaskServer()` throws, the SDK calls `process.exit(1)` with only a `console.error`.

**Fix:** Check that `RENDER_SDK_SOCKET_PATH` points to a valid, writable path. Use the Render CLI for local dev. Set `RENDER_SDK_AUTO_START=false` to disable auto-start and start manually if needed.

## Task Registration Issues

### "Task not found" in CLI

**Symptom:** `render workflows tasks list --local` shows no tasks or is missing expected tasks.

| Cause | Fix |
|-------|-----|
| Module not imported (Python) | Ensure your entry point imports all task files or uses `Workflows.from_workflows()`. |
| Module not imported (TypeScript) | Add `import './your-task-file'` to your `index.ts` entry point. |
| Server not running | Start the local task server first, then run `list --local` in a second terminal. |
| Missing `--local` flag | Without `--local`, the CLI lists deployed (remote) tasks, not local ones. |

### Late registration after auto-start (TypeScript)

**Symptom:** Dynamically imported tasks are not available for execution; a warning appears in logs.

**Cause:** The SDK auto-starts via `setImmediate` after synchronous module loading. Tasks registered after that (e.g., via dynamic `import()`) miss the registration window.

**Fix:** Define all tasks at module scope using synchronous `import './module'` statements. Avoid dynamic imports for task files.

### Duplicate task names

**Symptom:** Python raises `ValueError("Task '{name}' already registered")`. TypeScript silently overwrites the previous task.

**Cause:** Two tasks registered with the same `name`.

**Fix:** Use unique names for every task. When using `Workflows.from_workflows()` in Python, a `ValueError` is raised if any imported apps share a task name.

### Empty task name (TypeScript)

**Symptom:** `Error: Task function must have a name or name must be provided`.

**Fix:** Always pass `name` in the options object: `task({ name: "myTask" }, function myTask() { ... })`.

## Task Execution Issues

### Subtask hangs forever

**Symptom:** A task that calls other tasks never completes.

| Cause | Fix |
|-------|-----|
| Missing `await` | Subtask calls return a `TaskInstance` (Python) or `Promise` (TypeScript), not the result. You must `await` them. |
| Missing `async` keyword | Python: chaining tasks must be declared `async def`. TypeScript: must use `async function`. |
| Sequential instead of parallel | If you `await` each subtask individually, they run serially. Use `asyncio.gather()` (Python) or `Promise.all()` (TypeScript) for parallel execution. |

### Calling subtask outside a task context (Python)

**Symptom:** `RuntimeError` about running a subtask outside task execution context.

**Cause:** Task functions that are decorated with `@app.task` can only trigger subtask runs when called from within another executing task. Calling them from regular code (e.g., a script or REPL) fails because the internal `_current_client` context is not set.

**Fix:** To trigger tasks from outside a task, use the SDK client (`Render()` or `RenderAsync()`) with `start_task()` or `run_task()`. Subtask syntax is only for task-to-task chaining.

### Mixed positional and keyword arguments (Python)

**Symptom:** `ValueError` about not mixing positional and keyword arguments.

**Cause:** The Python SDK does not allow calling a subtask with both `*args` and `**kwargs` simultaneously.

**Fix:** Use either positional args or keyword args, not both: `await my_task(1, 2)` or `await my_task(a=1, b=2)`.

### "Not JSON serializable" error

**Symptom:** Task fails with a serialization error.

| Cause | Fix |
|-------|-----|
| Non-serializable arguments | Task args must be JSON-serializable: dicts/objects, lists/arrays, strings, numbers, booleans, None/null. No class instances, functions, dates, sets, bytes, or `BigInt`. |
| Non-serializable return value | Same rule applies to return values. Convert complex objects to dicts/plain objects before returning. |
| Non-serializable default values (Python) | Default parameter values that aren't JSON-serializable are silently dropped. The API metadata won't reflect them. Use only JSON-serializable defaults. |

### Task run fails silently

**Symptom:** Task run shows `failed` status with no useful error.

| Cause | Fix |
|-------|-----|
| Unhandled exception | Add logging inside your task. Wrap risky code in try/except (Python) or try/catch (TypeScript). |
| No retry config | Add retry configuration so transient failures are retried automatically. |
| Timeout exceeded | Default timeout is 2 hours. Set `timeout_seconds` (Python) or `timeoutSeconds` (TypeScript) per task if you need more. Max: 24 hours. |
| All retries exhausted | After `max_retries + 1` total attempts, the run is marked failed. Inspect `TaskRunDetails.attempts` for per-attempt error details. |

### Timeout value rejected by API

**Symptom:** Task registration or run fails with a validation error.

**Cause:** The SDK does not validate `timeout_seconds`/`timeoutSeconds` client-side. Out-of-range values (outside 30–86,400) are sent to the API, which rejects them.

**Fix:** Keep timeout values between 30 seconds and 86,400 seconds (24 hours).

## Client Issues

### `Render()` with `await` fails (Python)

**Symptom:** `TypeError` or unexpected behavior when using `await` with `Render()`.

**Fix:** `Render()` is the synchronous client. Use `RenderAsync()` for async contexts:

```python
# Synchronous (Flask, Django, scripts)
from render_sdk import Render
render = Render()
result = render.workflows.run_task("my-workflow/task", [42])

# Asynchronous (FastAPI, async scripts)
from render_sdk import RenderAsync
render = RenderAsync()
result = await render.workflows.run_task("my-workflow/task", [42])
```

### "Invalid API key" or "Unauthorized"

| Cause | Fix |
|-------|-----|
| Missing `RENDER_API_KEY` | Set the environment variable: `export RENDER_API_KEY=rnd_...` |
| Wrong key | Generate a new key at `https://dashboard.render.com/u/*/settings#api-keys` |
| Key doesn't match workspace | Ensure the key belongs to the workspace that owns the workflow |
| No key and no token passed | Both `Render()` and `RenderAsync()` raise `ValueError` if no token is available |

### Argument too large

**Symptom:** Request rejected with a size error.

**Fix:** Task arguments cannot exceed 4 MB total per invocation. Reduce payload size or pass references (URLs, IDs) instead of raw data.

### SSE stream ends without event

**Symptom:** `RenderError("Task run completed with no event")` (Python) or unhandled stream error (TypeScript).

**Cause:** The SSE connection closed before a terminal event (`completed`, `failed`, `canceled`) was received.

**Fix:** This is typically a transient network issue. The SDK retries internally (up to 5 attempts with exponential backoff). If it persists, check network connectivity and try again. You can also poll with `get_task_run()` as a fallback.

### AbortSignal does not cancel remote task (TypeScript)

**Symptom:** After aborting, the task run continues executing on Render.

**Cause:** `AbortSignal` only cancels the local SDK wait (the HTTP request or SSE stream). The remote task run keeps running.

**Fix:** To actually cancel a running task, explicitly call `render.workflows.cancelTaskRun(taskRunId)` after aborting.

### Rate limiting (429)

**Symptom:** `RateLimitError` (Python) or `ClientError` with 429 status (TypeScript).

**Fix:** Reduce request frequency. The SDK retries rate-limited requests internally for UDS calls (up to 15 attempts), but client-to-API rate limits require you to back off.

## Connection & Networking

### UDS retries exhausted

**Symptom:** Error after approximately 2.5 minutes of retries during task execution.

**Cause:** The internal Unix Domain Socket client retries transient errors (5xx, timeouts, rate limits) up to 15 times with exponential backoff (250ms initial, 2x factor, 16s cap). After 15 failures, the last error is thrown.

**Fix:** This usually indicates the task server is unhealthy or overwhelmed. Check server logs, restart the task server, and ensure the socket path is valid.

### Runs queued at concurrency limit

**Symptom:** New task runs stay in `pending` status for a long time.

**Cause:** Your workspace has hit its concurrent run limit. New runs are queued (not rejected) until another run completes.

**Fix:** Wait for in-progress runs to finish, cancel unnecessary runs, or purchase additional concurrency in your workspace settings. Creating multiple workflow services does not increase the limit.

## Local Development Gotchas

| Gotcha | Details |
|--------|---------|
| Local IDs don't match production | Task and run IDs in local dev are random UUIDs. They won't match deployed identifiers. |
| Data is in-memory only | Logs and results are lost when the local server shuts down. |
| Memory grows with many runs | Restart the local server periodically during heavy testing. |
| Only task endpoints are simulated | Other Render API endpoints are not available on the local server. |
| Cross-workflow calls not tracked | Calls between workflows via the SDK client are not shown as chained runs in the Dashboard. |

## Limits Reference

| Limit | Value |
|-------|-------|
| Max task definitions per workflow | 500 |
| Max argument size per run | 4 MB |
| Concurrent runs (Hobby) | 20 base, up to 200 |
| Concurrent runs (Professional) | 50 base, up to 200 |
| Concurrent runs (Org/Enterprise) | 100 base, up to 300 |
| Run timeout range | 30 seconds – 24 hours |
| Default run timeout | 2 hours |
| UDS internal retries | 15 attempts over ~2.5 minutes |
| SSE wait retries | 5 attempts with exponential backoff |
