# Manual Scaffolding (Fallback)

Use this path only if `render workflows init` is not available. Follow these steps in order.

## Contents

- Step 1: Detect language
- Step 2: Create the `workflows/` directory
- Step 3: Install dependencies
- Step 4: Verify setup

> **IMPORTANT:** Do NOT modify the project's root `package.json` or `requirements.txt`. Do NOT run `npm install <package>` or `pip install <package>` at the project root. The `workflows/` directory is a self-contained service with its own dependency files.

> **The official starter templates have likely changed since this skill was written.**
> Always check the real template before scaffolding:
> - **Python:** [render-examples/workflows-template-python](https://github.com/render-examples/workflows-template-python)
>
> If the user already has the SDK installed, inspect it for up-to-date signatures:
> ```bash
> # Python: check SDK source
> SDK_ROOT=$(pip show render_sdk | grep Location | cut -d' ' -f2)/render_sdk
> head -40 "$SDK_ROOT/__init__.py"
>
> # TypeScript: check type definitions
> grep -r "export.*task\|export.*Render" node_modules/@renderinc/sdk/
> ```
>
> **Official examples:** [Python](https://github.com/render-oss/sdk/tree/main/python/example) | [TypeScript](https://github.com/render-oss/sdk/tree/main/typescript/examples)
>
> The inline snippets in this skill are a fallback. The official repos are the source of truth.

## Step 1: Detect Language

**Principle:** If the user named the language in their prompt, use it directly. Auto-detect from config files next. Only ask if genuinely ambiguous.

Check the project for language indicators:

| Indicator | Language |
|-----------|----------|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `*.py` | Python |
| `package.json`, `tsconfig.json`, `*.ts` | TypeScript |

If both are present or neither is found, ask the user which language to use.

## Step 2: Create the `workflows/` Directory

Use the official Render starter templates as the source of truth for file structure and contents:

- **Python:** [render-examples/workflows-template-python](https://github.com/render-examples/workflows-template-python)
- **TypeScript:** [render-examples/workflows-template-ts](https://github.com/render-examples/workflows-template-ts)

Fetch the template contents (clone, download, or read from the repo) and place them in a `workflows/` directory at the project root. At minimum, the directory should contain:

**Python:** `main.py`, `requirements.txt`
**TypeScript:** `index.ts` (or `main.ts`), `package.json`, `tsconfig.json`

Key patterns to follow from the templates:

**Python entry point** (`main.py`):
```python
from render_sdk import Workflows, Retry

app = Workflows(
    default_retry=Retry(max_retries=3, wait_duration_ms=1000, backoff_scaling=2.0),
)

@app.task
def ping() -> str:
    return "pong"

if __name__ == "__main__":
    app.start()
```

**TypeScript entry point** (`index.ts`):
```typescript
import { task } from "@renderinc/sdk/workflows";

task(
  {
    name: "ping",
    retry: { maxRetries: 3, waitDurationMs: 1000, backoffScaling: 2.0 },
  },
  function ping(): string {
    return "pong";
  },
);
```

Each template includes a zero-argument `ping` task so the user can immediately verify the setup works.

## Step 3: Install Dependencies

After all files from Step 2 are created, install dependencies.

**Python:**
```bash
pip install -r workflows/requirements.txt
```

**TypeScript:**
```bash
npm install --prefix workflows
```

## Step 4: Verify Setup

Check that setup succeeded before handing off:

- [ ] `workflows/` directory exists with the expected files
- [ ] Dependencies installed without errors

Then present the user with these verification commands to run in their own terminal:

**Verification checklist:**

- [ ] Start the local task server:
  - Python: `render workflows dev -- python workflows/main.py`
  - TypeScript: `render workflows dev -- npx tsx workflows/main.ts`
- [ ] In a second terminal: `render workflows tasks list --local`
- [ ] Select `ping`, choose `run`, enter `[]` as input
- [ ] Verify the result is `"pong"`

Do NOT start the dev server or run test commands yourself. Present the checklist for the user to run.

**If verification fails:**
- **Task server won't start:** check CLI version (`render --version`, needs 2.11.0+) and start command. See [Troubleshooting > Task Server Issues](troubleshooting.md#task-server-issues).
- **`ping` task not listed:** ensure the entry point imports the task file. See [Task Registration Issues](troubleshooting.md#task-registration-issues).
- **Dependency install errors:** confirm you ran install inside `workflows/`, not the project root.
