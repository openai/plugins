# Local Development

Run workflow tasks locally for faster development and testing.

## Contents

- Prerequisites
- Starting the local task server
- Triggering task runs (CLI and application code)
- Viewing results
- Limitations

## Prerequisites

- **Render CLI 2.11.0+**: `render --version`
  - macOS: `brew install render`
  - Linux/macOS: `curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh | sh`
  - Windows: download the executable from the [CLI releases page](https://github.com/render-oss/cli/releases/)
- A workflow project with registered tasks

## Starting the Local Task Server

From your project directory:

```bash
# Python
render workflows dev -- python workflows/main.py

# TypeScript
render workflows dev -- npx tsx workflows/main.ts
```

The local server starts on port `8120`. Customize with `--port`:

```bash
render workflows dev --port 8121 -- python workflows/main.py
```

The server picks up code changes automatically as you iterate.

## Triggering Task Runs

### From the CLI

List and run tasks interactively:

```bash
render workflows tasks list --local
```

**The `--local` flag is required.** Without it, the CLI lists deployed (remote) tasks.

The interactive menu lets you:
1. Select a task
2. Choose `run`
3. Provide input as a JSON array (e.g., `[5]` or `[]`)
4. View live logs

### From Application Code

Configure your app to target the local task server.

**Python:**

Set environment variables:
```bash
RENDER_USE_LOCAL_DEV=true
```

Or for a custom port:
```bash
RENDER_USE_LOCAL_DEV=true
RENDER_LOCAL_DEV_URL=http://localhost:8121
```

The SDK clients (`Render()` and `RenderAsync()`) automatically detect these and route requests to the local server.

**TypeScript:**

Same environment variables:
```bash
RENDER_USE_LOCAL_DEV=true
```

Or pass configuration directly:
```typescript
import { Render } from "@renderinc/sdk";

const render = new Render({
  useLocalDev: true,
  localDevUrl: "http://localhost:8120",
});
```

**Render API (any language):**

Swap the base URL for task endpoints:
```
http://localhost:8120
```

The local task server only simulates task-related endpoints. Other Render API endpoints are not supported locally.

## Viewing Results

After running a task via the CLI:
1. Press **Esc** to go back to the command menu
2. Select `runs` to see task runs
3. Select a run and choose `results` to see output

## Limitations

- Logs and results are stored **in memory** and lost on server shutdown
- High volume of runs can increase memory usage; restart the server periodically
- Task and run IDs are random UUIDs, not matching deployed identifiers
- Subtasks run locally in the same server process
