# Workflows SDK Quick Reference

This is an **approximate** API surface map -- not a substitute for the real SDK.
Always verify signatures against the installed package before generating code.

## Contents

- Where to find the real SDK source
- API surface map (defining tasks, task options, triggering runs, error types)
- Instance types
- Retry defaults
- Environment variables

## Where to find the real SDK source

### Python

```bash
SDK_ROOT=$(pip show render_sdk | grep Location | cut -d' ' -f2)/render_sdk

# Signatures and source
#   $SDK_ROOT/__init__.py              — exports + usage examples in docstring
#   $SDK_ROOT/workflows/app.py         — Workflows class, @app.task, Retry, from_workflows()
#   $SDK_ROOT/workflows/task.py        — task internals, Options dataclass
#   $SDK_ROOT/client/workflows_sync.py — sync client methods (Render().workflows.*)
#   $SDK_ROOT/client/workflows.py      — async client methods (RenderAsync().workflows.*)
#   $SDK_ROOT/client/errors.py         — error hierarchy
#   $SDK_ROOT/client/types.py          — TaskRun, TaskRunDetails, etc.
```

### TypeScript

```bash
TS_ROOT=node_modules/@renderinc/sdk

# Signatures and types
#   $TS_ROOT/dist/workflows.d.ts   — task() function, task options types
#   $TS_ROOT/dist/client.d.ts      — Render class, startTask, runTask, etc.
#   $TS_ROOT/dist/index.d.ts       — top-level exports
#   $TS_ROOT/README.md             — usage examples (if present)
```

## API surface map

### Defining tasks

| Concept | Python | TypeScript |
|---------|--------|------------|
| Entry point | `from render_sdk import Workflows` | `import { task } from "@renderinc/sdk/workflows"` |
| Define a task | `@app.task` decorator | `task(options, fn)` |
| Start server | `app.start()` in `__main__` | Auto-starts via `RENDER_SDK_SOCKET_PATH` |
| Merge multi-file tasks | `Workflows.from_workflows(app1, app2)` | Side-effect imports in `index.ts` |
| Retry config | `Retry(max_retries, wait_duration_ms, backoff_scaling)` | `{ maxRetries, waitDurationMs, backoffScaling }` |

### Task options

| Option | Python (`@app.task` kwarg) | TypeScript (`task()` first arg) |
|--------|---------------------------|--------------------------------|
| Name | `name` | `name` (required) |
| Retry | `retry` (Retry instance) | `retry` (object) |
| Timeout | `timeout_seconds` | `timeoutSeconds` |
| Instance type | `plan` | `plan` |

Workflow-level defaults: `Workflows(default_retry=..., default_timeout=..., default_plan=...)`.

### Triggering runs (client SDK)

| Concept | Python sync (`Render`) | Python async (`RenderAsync`) | TypeScript (`Render`) |
|---------|----------------------|----------------------------|----------------------|
| Fire-and-forget | `start_task()` | `await start_task()` | `await startTask()` |
| Start + wait | `run_task()` | `await run_task()` | `await runTask()` |
| Get run details | `get_task_run()` | `await get_task_run()` | `await getTaskRun()` |
| List runs | `list_task_runs()` | `await list_task_runs()` | `await listTaskRuns()` |
| Cancel run | `cancel_task_run()` | `await cancel_task_run()` | `await cancelTaskRun()` |
| Stream events (SSE) | `task_run_events()` | `task_run_events()` | `taskRunEvents()` |

Task identifier format: `{workflow-slug}/{task-name}`.

### Error types

| Python | TypeScript | Notes |
|--------|------------|-------|
| `RenderError` | `RenderError` | Base class |
| `ClientError` | `ClientError` | 400-level |
| `RateLimitError` | — | 429 (subclass of ClientError) |
| `ServerError` | `ServerError` | 500-level |
| `TimeoutError` | — | Request timeout |
| `TaskRunError` | — | Task run failed |
| — | `AbortError` | Request aborted via AbortSignal |

Import paths -- Python: `render_sdk.client.errors`, TypeScript: `@renderinc/sdk`.

### Instance types

| Plan | Specs |
|------|-------|
| `starter` | 0.5 CPU / 512 MB |
| `standard` (default) | 1 CPU / 2 GB |
| `pro` | 2 CPU / 4 GB |
| `pro_plus` | 4 CPU / 8 GB |
| `pro_max` | 8 CPU / 16 GB |
| `pro_ultra` | 16 CPU / 32 GB |

`pro_plus`, `pro_max`, `pro_ultra` require requesting access.

### Retry defaults

| Scenario | `backoff_scaling` default |
|----------|--------------------------|
| Explicit retry config provided, field omitted | 1.5 |
| No retry config (built-in defaults) | 2.0 |

### Environment variables

| Variable | Purpose |
|----------|---------|
| `RENDER_API_KEY` | API authentication |
| `RENDER_SDK_SOCKET_PATH` | Unix socket (set by Render) |
| `RENDER_SDK_MODE` | `"run"` or `"register"` (set by Render) |
| `RENDER_SDK_AUTO_START` | TS only: `"false"` to disable |
| `RENDER_USE_LOCAL_DEV` | `"true"` for local task server |
| `RENDER_LOCAL_DEV_URL` | Custom local server URL |
