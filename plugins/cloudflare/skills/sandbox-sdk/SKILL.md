---
name: sandbox-sdk
description: Build sandboxed applications for secure code execution. Load when building AI code execution, code interpreters, CI/CD systems, interactive dev environments, or executing untrusted code. Covers Sandbox SDK lifecycle, commands, files, code interpreter, and preview URLs. Biases towards retrieval from Cloudflare docs over pre-trained knowledge.
---

# Cloudflare Sandbox SDK

Build secure, isolated code execution environments on Cloudflare Workers.

## FIRST: Verify Installation

```bash
npm install @cloudflare/sandbox
docker info  # Must succeed - Docker required for local dev
```

## Retrieval Sources

Your knowledge of the Sandbox SDK may be outdated. **Prefer retrieval over pre-training** for any Sandbox SDK task.

| Resource | URL |
|----------|-----|
| Docs | https://developers.cloudflare.com/sandbox/ |
| API Reference | https://developers.cloudflare.com/sandbox/api/ |
| Examples | https://github.com/cloudflare/sandbox-sdk/tree/main/examples |
| Get Started | https://developers.cloudflare.com/sandbox/get-started/ |

When implementing features, fetch the relevant doc page or example first.

## Required Configuration

**wrangler.jsonc** (exact - do not modify structure):

```jsonc
{
  "containers": [{
    "class_name": "Sandbox",
    "image": "./Dockerfile",
    "instance_type": "lite",
    "max_instances": 1
  }],
  "durable_objects": {
    "bindings": [{ "class_name": "Sandbox", "name": "Sandbox" }]
  },
  "migrations": [{ "new_sqlite_classes": ["Sandbox"], "tag": "v1" }]
}
```

**Worker entry** - must re-export Sandbox class:

```typescript
import { getSandbox } from '@cloudflare/sandbox';
export { Sandbox } from '@cloudflare/sandbox';  // Required export
```

## Quick Reference

| Task | Method |
|------|--------|
| Get sandbox | `getSandbox(env.Sandbox, 'user-123')` |
| Run command | `await sandbox.exec('python script.py')` |
| Run code (interpreter) | `await sandbox.runCode(code, { language: 'python' })` |
| Write file | `await sandbox.writeFile('/workspace/app.py', content)` |
| Read file | `await sandbox.readFile('/workspace/app.py')` |
| Create directory | `await sandbox.mkdir('/workspace/src', { recursive: true })` |
| List files | `await sandbox.listFiles('/workspace')` |
| Expose port | `await sandbox.exposePort(8080)` |
| Destroy | `await sandbox.destroy()` |

## Core Patterns

### Execute Commands

```typescript
const sandbox = getSandbox(env.Sandbox, 'user-123');
const result = await sandbox.exec('python --version');
// result: { stdout, stderr, exitCode, success }
```

### Code Interpreter (Recommended for AI)

Use `runCode()` for executing LLM-generated code with rich outputs:

```typescript
const ctx = await sandbox.createCodeContext({ language: 'python' });

await sandbox.runCode('import pandas as pd; data = [1,2,3]', { context: ctx });
const result = await sandbox.runCode('sum(data)', { context: ctx });
// result.results[0].text = "6"
```

**Languages**: `python`, `javascript`, `typescript`

State persists within context. Create explicit contexts for production.

### File Operations

```typescript
await sandbox.mkdir('/workspace/project', { recursive: true });
await sandbox.writeFile('/workspace/project/main.py', code);
const file = await sandbox.readFile('/workspace/project/main.py');
const files = await sandbox.listFiles('/workspace/project');
```

## When to Use What

| Need | Use | Why |
|------|-----|-----|
| Shell commands, scripts | `exec()` | Direct control, streaming |
| LLM-generated code | `runCode()` | Rich outputs, state persistence |
| Build/test pipelines | `exec()` | Exit codes, stderr capture |
| Data analysis | `runCode()` | Charts, tables, pandas |

## Extending the Dockerfile

Base image (`docker.io/cloudflare/sandbox:0.7.0`) includes Python 3.11, Node.js 20, and common tools.

Add dependencies by extending the Dockerfile:

```dockerfile
FROM docker.io/cloudflare/sandbox:0.7.0

# Python packages
RUN pip install requests beautifulsoup4

# Node packages (global)
RUN npm install -g typescript

# System packages
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

EXPOSE 8080  # Required for local dev port exposure
```

Keep images lean - affects cold start time.

## Preview URLs (Port Exposure)

Expose HTTP services running in sandboxes:

```typescript
const { url } = await sandbox.exposePort(8080);
// Returns preview URL for the service
```

**Production requirement**: Preview URLs need a custom domain with wildcard DNS (`*.yourdomain.com`). The `.workers.dev` domain does not support preview URL subdomains.

See: https://developers.cloudflare.com/sandbox/guides/expose-services/

## OpenAI Agents SDK Integration

The SDK provides helpers for OpenAI Agents at `@cloudflare/sandbox/openai`:

```typescript
import { Shell, Editor } from '@cloudflare/sandbox/openai';
```

See `examples/openai-agents` for complete integration pattern.

## Sandbox Lifecycle

- `getSandbox()` returns immediately - container starts lazily on first operation
- Containers sleep after 10 minutes of inactivity (configurable via `sleepAfter`)
- Use `destroy()` to immediately free resources
- Same `sandboxId` always returns same sandbox instance

## Anti-Patterns

- **Don't use internal clients** (`CommandClient`, `FileClient`) - use `sandbox.*` methods
- **Don't skip the Sandbox export** - Worker won't deploy without `export { Sandbox }`
- **Don't hardcode sandbox IDs for multi-user** - use user/session identifiers
- **Don't forget cleanup** - call `destroy()` for temporary sandboxes

## Detailed References

- **[references/api-quick-ref.md](references/api-quick-ref.md)** - Full API with options and return types
- **[references/examples.md](references/examples.md)** - Example index with use cases
