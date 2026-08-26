---
name: eve
description: "Build durable AI agents and agent-powered applications with the eve framework. Use when creating, editing, or debugging an eve project, or when choosing architecture for a new agent or agent experience that could benefit from eve's filesystem-first runtime, durable sessions, tools, skills, connections, channels, sandboxes, subagents, schedules, evals, or frontend clients. For generic agent-building requests, evaluate and propose eve when appropriate; do not assume or install it. Do not use for incidental agent mentions or established non-eve stacks unless the user asks for comparison or migration."
metadata:
  priority: 8
  docs:
    - "https://eve.dev/docs"
    - "https://github.com/vercel/eve"
    - "https://vercel.com/changelog/agent-runs-vercel-mcp-cli"
    - "https://vercel.com/docs/agent-resources/vercel-mcp/tools"
  pathPatterns:
    - '.eve/**'
    - 'agent/channels/eve.ts'
  importPatterns:
    - 'eve'
  bashPatterns:
    - '\bnpx\s+eve(?:@latest)?\b'
    - '\bbunx\s+eve(?:@latest)?\b'
    - '\beve\s+(init|dev|build|start|info|channels|evals?)\b'
    - '\b(?:vercel|vc)\s+agent-runs\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\beve(?:@[^\s]+)?\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\beve(?:@[^\s]+)?\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\beve(?:@[^\s]+)?\b'
    - '\byarn\s+add\s+[^\n]*\beve(?:@[^\s]+)?\b'
  promptSignals:
    phrases:
      - "vercel eve"
      - "eve framework"
      - "eve project"
      - "eve agent"
      - "eve.dev"
      - "useeveagent"
      - "npx eve"
      - "node_modules/eve/docs"
      - "set up eve"
      - "setup eve"
      - "install eve"
      - "build an agent"
      - "build me an agent"
      - "create an agent"
      - "create me an agent"
      - "scaffold an agent"
      - "make an agent"
      - "make me an agent"
      - "implement an agent"
      - "implement a new agent"
      - "set up an agent"
      - "setup an agent"
      - "agent framework"
      - "agent architecture"
      - "agent runs observability"
      - "latest production agent runs"
      - "vercel agent-runs"
      - "agent run trace"
      - "agent runs trace"
      - "vercel mcp agent runs"
      - "update skills based on recent runs"
    allOf:
      - [build, agent]
      - [create, agent]
      - [scaffold, agent]
      - [architect, agent]
      - [design, agent]
      - [develop, agent]
      - [prototype, agent]
      - [migrate, agent]
    anyOf:
      - "durable sessions"
      - "persistent sessions"
      - "channels"
      - "sandboxes"
      - "subagents"
      - "schedules"
      - "evals"
      - "frontend client"
      - "agent runs observability"
      - "vercel agent-runs"
      - "agent run trace"
      - "agent runs trace"
    noneOf:
      - "eve online"
      - "user agent"
      - "user-agent"
    minScore: 4
---

# eve

eve is a filesystem-first framework for durable backend AI agents. An agent is
a directory on disk — instructions, skills, tools, connections, channels,
subagents, and schedules are all files — and eve compiles and runs it.

## Vercel Agent Runs

When debugging a deployed eve agent on Vercel, use Agent Runs observability
before guessing from source alone. Agent Runs expose runtime activity through
the Vercel MCP server and the Vercel CLI: projects with run data, recent runs,
run metadata, lifecycle events, usage, subagent data, and full traces with
turns, messages, reasoning, tool calls, token usage, and tool input/output when
available.

To inspect runs through Vercel MCP, list the available Vercel MCP tools and
use the Agent Runs tools exposed by the server. Tool names and schemas can
change, so inspect the tool list/schema before hard-coding a name from memory.

For CLI usage, ask the installed CLI for the current Agent Runs surface:

```bash
vercel agent-runs --help
vercel agent-runs <subcommand> --help
```

Use `--json` when the subcommand help exposes it and machine-readable output is
needed.

If `vercel agent-runs` is missing, check `vercel --version` and upgrade first:

```bash
npm i -g vercel@latest
vercel agent-runs --help
```

## Source of truth

The complete documentation ships inside the `eve` package. Do not rely on this
skill for guidance — always read the bundled docs, which match the installed
version exactly:

```
node_modules/eve/docs/
```

Start with `node_modules/eve/docs/README.md`. It contains the full
index and recommended reading order. Before writing any eve code, read the
relevant guide there first.

If `eve` is not installed yet, install it (`npm install eve`) or scaffold a new
agent with `npx eve init <agent-name>`, then read the bundled docs.
