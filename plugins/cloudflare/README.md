# Cloudflare Skills

A collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) for building on Cloudflare, Workers, the Agents SDK, and the wider Cloudflare Developer Platform.

## Installing

These skills work with any agent that supports the Agent Skills standard, including OpenAI Codex, OpenCode, and Pi.

### Cursor

Install from the Cursor Marketplace or add manually via **Settings > Rules > Add Rule > Remote Rule (Github)** with `cloudflare/skills`.

### npx skills

Install using the [`npx skills`](https://skills.sh) CLI:

```
npx skills add https://github.com/cloudflare/skills
```

### Clone / Copy

Clone this repo and copy the skill folders into the appropriate directory for your agent:

| Agent | Skill Directory | Docs |
|-------|-----------------|------|
| Cursor | `~/.cursor/skills/` | [docs](https://cursor.com/docs/context/skills) |
| OpenCode | `~/.config/opencode/skills/` | [docs](https://opencode.ai/docs/skills/) |
| OpenAI Codex | `~/.codex/skills/` | [docs](https://developers.openai.com/codex/skills/) |
| Pi | `~/.pi/agent/skills/` | [docs](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#skills) |

## Commands

Commands are user-invocable slash commands that you explicitly call.

| Command | Description |
|---------|-------------|
| `/cloudflare:build-agent` | Build an AI agent on Cloudflare using the Agents SDK |
| `/cloudflare:build-mcp` | Build an MCP server on Cloudflare |

## Skills

Skills are contextual and auto-loaded based on your conversation. When a request matches a skill's triggers, the agent loads and applies the relevant skill to provide accurate, up-to-date guidance.

| Skill | Useful for |
|-------|------------|
| cloudflare | Comprehensive platform skill covering Workers, Pages, storage (KV, D1, R2), AI (Workers AI, Vectorize, Agents SDK), networking (Tunnel, Spectrum), security (WAF, DDoS), and IaC (Terraform, Pulumi) |
| agents-sdk | Building stateful AI agents with state, scheduling, RPC, MCP servers, email, and streaming chat |
| durable-objects | Stateful coordination (chat rooms, games, booking), RPC, SQLite, alarms, WebSockets |
| sandbox-sdk | Secure code execution for AI code execution, code interpreters, CI/CD systems, and interactive dev environments |
| wrangler | Deploying and managing Workers, KV, R2, D1, Vectorize, Queues, Workflows |
| web-perf | Auditing Core Web Vitals (FCP, LCP, TBT, CLS), render-blocking resources, network chains |
| building-mcp-server-on-cloudflare | Building remote MCP servers with tools, OAuth, and deployment |
| building-ai-agent-on-cloudflare | Building AI agents with state, WebSockets, and tool integration |

## MCP Server

This plugin includes the [Cloudflare API MCP server](https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/) for enhanced functionality:

| Server | Purpose |
|--------|---------|
| cloudflare-api | Token-efficient access to the Cloudflare API via `search()` and `execute()` |

## Resources

- [Cloudflare Agents Documentation](https://developers.cloudflare.com/agents/)
- [Cloudflare MCP Guide](https://developers.cloudflare.com/agents/model-context-protocol/)
- [Agents SDK Repository](https://github.com/cloudflare/agents)
- [Agents Starter Template](https://github.com/cloudflare/agents-starter)
