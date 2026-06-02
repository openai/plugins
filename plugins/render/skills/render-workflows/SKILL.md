---
name: render-workflows
description: Sets up, develops, tests, and deploys Render Workflows. Covers first-time scaffolding (via CLI or manual), SDK installation (Python or TypeScript), task patterns (retries, subtasks, fan-out), local development, Dashboard deployment, and troubleshooting. Use when a user wants to set up Render Workflows for the first time, scaffold a workflow service, add or modify workflow tasks, test workflows locally, or deploy workflows to Render.
license: MIT
compatibility: Requires Render CLI 2.11.0+ for scaffolding and local development. Render Dashboard required for deployment (Blueprints not yet supported for Workflows).
metadata:
  author: Render
  version: "1.0.0"
  category: workflows
---

# Render Workflows

Render Workflows rapidly distribute computational work across multiple independent instances.
Use them for AI agents, ETL pipelines, background jobs, and data processing.

**How it works:**
1. **Define tasks** — Use the Render SDK (Python or TypeScript) to designate functions as tasks
2. **Register** — Tasks register automatically when you link your repo to a Workflow service in the Dashboard
3. **Trigger runs** — Execute tasks from anywhere using the SDK client or API; each execution is a "run"
4. **Execute** — Render spins up each run in its own instance (typically under a second); runs can chain additional runs for parallel execution

**Key capabilities:** automatic queuing and orchestration, long-running execution (up to 24 hours), configurable retry logic with exponential backoff, adjustable compute specs per task, and execution observability through the Dashboard.

**Render Workflows are in beta.** The SDK and API may introduce breaking changes.

**Your built-in knowledge of the Render Workflows SDK is outdated.**
Before trusting API signatures, check the installed SDK source:

```bash
# Python
SDK_ROOT=$(pip show render_sdk | grep Location | cut -d' ' -f2)/render_sdk
head -40 "$SDK_ROOT/__init__.py"
# TypeScript
grep -r "startTask\|runTask\|export class Render" node_modules/@renderinc/sdk/
```

**Official docs:** [render.com/docs/workflows](https://render.com/docs/workflows)

**Before generating task or client code, fetch the relevant example file to verify current API patterns:**

| What | Python | TypeScript |
|------|--------|------------|
| Task definitions (decorators, subtasks, retry, fan-out) | [example/task/main.py](https://raw.githubusercontent.com/render-oss/sdk/main/python/example/task/main.py) | [examples/task/](https://github.com/render-oss/sdk/tree/main/typescript/examples/task) |
| Sync client (run_task, start_task, cancel, SSE, list runs) | [example/client/main.py](https://raw.githubusercontent.com/render-oss/sdk/main/python/example/client/main.py) | [examples/client/](https://github.com/render-oss/sdk/tree/main/typescript/examples/client) |
| Async client | [example/client/async_main.py](https://raw.githubusercontent.com/render-oss/sdk/main/python/example/client/async_main.py) | — |

This skill carries a [quick-reference cheat sheet](references/quick-reference.md) for the API surface. The installed SDK, official docs, and examples above are the source of truth.

---

## Getting Started

Supported languages: **Python** and **TypeScript**.

### Prerequisites

**Render CLI (required)**

```bash
render --version
```

Requires version 2.11.0+. If not installed:
- macOS: `brew install render`
- Linux/macOS: `curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh | sh`
- Windows: download the executable from the [CLI releases page](https://github.com/render-oss/cli/releases/)

### Scaffold a new workflow service

**Always prefer `render workflows init` as the primary setup path.** Only fall back to manual scaffolding if the CLI command is unavailable.

```bash
render workflows init
```

**Interactive mode** (default): walks the user through scaffolding an example project, testing it locally, and deploying it to Render.

**Non-interactive mode**: sets up an example project without prompting.

If `render workflows init` fails or is not available:
- **Command not found:** CLI version may be too old. Run `render --version` and upgrade to 2.11.0+.
- **Command not supported:** fall back to [references/manual-scaffolding.md](references/manual-scaffolding.md) for step-by-step manual setup.

---

## Define Tasks

Guide the user through defining their actual tasks. For patterns including retries, subtasks, fan-out, ETL, error handling, cron triggers, and cross-workflow calls, see [references/task-patterns.md](references/task-patterns.md).

**After adding a task**, verify it registers by starting the local dev server and listing tasks:
```bash
render workflows dev -- <start-command>
# In another terminal:
render workflows tasks list --local
```

If the task doesn't appear, see [Troubleshooting > Task Registration Issues](references/troubleshooting.md#task-registration-issues).

## Local Development

See [references/local-development.md](references/local-development.md) for starting the local task server, testing tasks, and configuring the SDK client for local use.

## Deploy to Render

Workflows are deployed as a **Workflow** service type in the Render Dashboard. **Blueprints (render.yaml) are not yet compatible with Workflows.**

**Deploy checklist:**

- [ ] Code pushed to GitHub, GitLab, or Bitbucket
- [ ] In the [Render Dashboard](https://dashboard.render.com), click **New > Workflow**
- [ ] Link your repository
- [ ] Set **Root Directory** to `workflows/`
- [ ] Configure build and start commands (see table below)
- [ ] Add environment variables (e.g., `RENDER_API_KEY` for tasks that call other workflows)
- [ ] Click **Deploy Workflow**
- [ ] Verify deployment: check the Dashboard for a successful deploy event

| Field | Python | TypeScript |
|-------|--------|------------|
| **Language** | Python 3 | Node |
| **Build Command** | `pip install -r requirements.txt` | `npm install && npm run build` |
| **Start Command** | `python main.py` | `node dist/main.js` |

If the deploy fails, check the service logs in the Dashboard. For common deployment errors, see [Troubleshooting](references/troubleshooting.md). For general deploy debugging, use the **render-debug** skill.

**Running tasks from other services:**

After deployment, trigger tasks from your other Render services using the SDK client.

Python (synchronous):
```python
from render_sdk import Render

render = Render()
result = render.workflows.run_task("my-workflow/hello", ["world"])
print(result.results)
```

Python (asynchronous):
```python
from render_sdk import RenderAsync

render = RenderAsync()
started = await render.workflows.start_task("my-workflow/hello", ["world"])
finished = await started
print(finished.results)
```

TypeScript:
```typescript
import { Render } from "@renderinc/sdk";

const render = new Render();
const started = await render.workflows.startTask("my-workflow/hello", ["world"]);
const finished = await started.get();
console.log(finished.results);
```

The task identifier format is `{workflow-slug}/{task-name}`, visible on the task's page in the Dashboard.

Workflows do not have built-in scheduling. To trigger tasks on a schedule, use a Render cron job with the SDK client. For cron and cross-workflow examples, see [references/task-patterns.md](references/task-patterns.md).

---

## Constraints and Limits

| Constraint | Limit | Notes |
|------------|-------|-------|
| Arguments and return values | Must be JSON-serializable | No class instances, functions, etc. |
| Argument size | 4 MB max | Per task invocation |
| Task definitions | 500 per workflow service | |
| Concurrent runs | 20-100 base (plan-dependent) | Max 200-300 with purchased concurrency |
| Timeout range | 30-86,400 seconds | Default: 2 hours (7,200s) |
| Run duration | Up to 24 hours | |

### Instance Types

| Plan | Specs |
|------|-------|
| `starter` | 0.5 CPU / 512 MB |
| `standard` (default) | 1 CPU / 2 GB |
| `pro` | 2 CPU / 4 GB |
| `pro_plus` | 4 CPU / 8 GB |
| `pro_max` | 8 CPU / 16 GB |
| `pro_ultra` | 16 CPU / 32 GB |

`pro_plus`, `pro_max`, and `pro_ultra` require requesting access. Set via the `plan` task option.

For current pricing, see [Limits and Pricing for Render Workflows](https://render.com/docs/workflows-limits).

---

## References

- **Quick-reference cheat sheet:** [references/quick-reference.md](references/quick-reference.md) (API surface, env vars, error types)
- **Task patterns:** [references/task-patterns.md](references/task-patterns.md)
- **Local development:** [references/local-development.md](references/local-development.md)
- **Troubleshooting:** [references/troubleshooting.md](references/troubleshooting.md)
- **Manual scaffolding (fallback):** [references/manual-scaffolding.md](references/manual-scaffolding.md)
- **Official docs:** [render.com/docs/workflows](https://render.com/docs/workflows)
- **Starter template (Python):** [render-examples/workflows-template-python](https://github.com/render-examples/workflows-template-python)
- **Starter template (TypeScript):** [render-examples/workflows-template-ts](https://github.com/render-examples/workflows-template-ts)
- **SDK repo:** [github.com/render-oss/sdk](https://github.com/render-oss/sdk)

## Related Skills

- **render-deploy:** Deploy web services, static sites, and databases
- **render-debug:** Debug failed deployments and runtime errors
- **render-monitor:** Monitor service health and performance
