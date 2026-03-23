# vercel

This directory packages the upstream [vercel/vercel-plugin](https://github.com/vercel/vercel-plugin) runtime content for the `openai/plugins` marketplace. Skills are discovered by Codex via SKILL.md frontmatter metadata.

## What is included

- `skills/` from the upstream plugin (47 skills with retrieval metadata for Codex discovery)
- `hooks.json` no-op placeholder to match the pinned plugin-creator manifest shape
- `.mcp.json` for the official Vercel MCP server
- `.app.json` for the existing Vercel connector wiring
- `vercel.md` ecosystem reference graph
- `agents/` specialist agent definitions
- `commands/` slash command definitions
- Plugin assets

## Codex compatibility notes

- The upstream repo ships `.plugin/plugin.json`; this import uses `.codex-plugin/plugin.json`.
- Skills use frontmatter metadata (`retrieval.aliases`, `intents`, `entities`, `pathPatterns`, `bashPatterns`) for Codex-native discovery — no hooks required.
- `hooks.json` is intentionally empty; it is present only to keep the manifest aligned with the pinned `plugin-creator` sample.
- The bundled `agents/` and `commands/` content is included from upstream for source parity.

## Upstream source

- Repo: [vercel/vercel-plugin](https://github.com/vercel/vercel-plugin)
- Imported version: `0.21.0`
- Local plugin id: `vercel`

## Components

### Ecosystem Graph (`vercel.md`)

A text-form relational graph covering:
- All Vercel products and their relationships
- Decision matrices for choosing the right tool
- Common cross-product workflows
- Migration awareness for sunset products

### Selected Skills

| Skill | Covers |
|-------|--------|
| `agent-browser` | Browser automation CLI — dev server verification, page interaction, screenshots, form filling |
| `ai-elements` | Pre-built React components for AI interfaces — chat UIs, tool call rendering, streaming responses |
| `ai-gateway` | Unified model API, provider routing, failover, cost tracking, 100+ models |
| `ai-sdk` | AI SDK v6 — text/object generation, streaming, tool calling, agents, MCP, providers, embeddings |
| `auth` | Authentication integrations — Clerk, Descope, Auth0 setup for Next.js with Marketplace provisioning |
| `bootstrap` | Project bootstrapping orchestrator — linking, env provisioning, db setup, first-run commands |
| `chat-sdk` | Multi-platform chat bots — Slack, Telegram, Teams, Discord, Google Chat, GitHub, Linear |
| `cms` | Headless CMS integrations — Sanity, Contentful, DatoCMS, Storyblok, Builder.io, Visual Editing |
| `cron-jobs` | Vercel Cron Jobs configuration, scheduling, and best practices |
| `deployments-cicd` | Deployment and CI/CD — deploy, promote, rollback, --prebuilt, CI workflow files |
| `email` | Email sending — Resend with React Email templates, domain verification, transactional emails |
| `env-vars` | Environment variable management — .env files, vercel env commands, OIDC tokens |
| `json-render` | AI chat response rendering — UIMessage parts, tool call displays, streaming states |
| `marketplace` | Integration discovery, installation, auto-provisioned env vars, unified billing |
| `nextjs` | App Router, Server Components, Server Actions, Cache Components, routing, rendering strategies |
| `observability` | Web Analytics, Speed Insights, runtime logs, Log Drains, OpenTelemetry, monitoring |
| `payments` | Stripe payments — Marketplace setup, checkout sessions, webhooks, subscription billing |
| `routing-middleware` | Request interception before cache, rewrites, redirects, personalization — Edge/Node.js/Bun runtimes |
| `runtime-cache` | Ephemeral per-region key-value cache, tag-based invalidation, shared across Functions/Middleware/Builds |
| `shadcn` | shadcn/ui — CLI, component installation, custom registries, theming, Tailwind CSS integration |
| `sign-in-with-vercel` | OAuth 2.0/OIDC identity provider, user authentication via Vercel accounts |
| `turbopack` | Next.js bundler, HMR, configuration, Turbopack vs Webpack |
| `turborepo` | Monorepo orchestration, caching, remote caching, --affected, pruned subsets |
| `v0-dev` | AI code generation, agentic intelligence, GitHub integration |
| `vercel-agent` | AI-powered code review, incident investigation, SDK installation, PR analysis |
| `vercel-api` | Vercel MCP Server and REST API — projects, deployments, env vars, domains, logs |
| `vercel-cli` | All CLI commands — deploy, env, dev, domains, cache management, MCP integration, marketplace |
| `vercel-firewall` | DDoS, WAF, rate limiting, bot filter, custom rules |
| `vercel-flags` | Feature flags, Flags Explorer, gradual rollouts, A/B testing, provider adapters |
| `vercel-functions` | Serverless, Edge, Fluid Compute, streaming, Cron Jobs, configuration |
| `vercel-queues` | Durable event streaming, topics, consumer groups, retries, delayed delivery |
| `vercel-sandbox` | Ephemeral Firecracker microVMs for running untrusted/AI-generated code safely |
| `vercel-storage` | Blob, Edge Config, Neon Postgres, Upstash Redis, migration from sunset packages |
| `workflow` | Workflow DevKit — durable execution, DurableAgent, steps, Worlds, pause/resume |

### Agents (3 specialists)

| Agent | Expertise |
|-------|-----------|
| `deployment-expert` | CI/CD pipelines, deploy strategies, troubleshooting, environment variables |
| `performance-optimizer` | Core Web Vitals, rendering strategies, caching, asset optimization |
| `ai-architect` | AI application design, model selection, streaming architecture, MCP integration |

### Commands (5 commands)

| Command | Purpose |
|---------|---------|
| `/vercel:bootstrap` | Bootstrap project — linking, env provisioning, db setup |
| `/vercel:deploy` | Deploy to Vercel (preview or production) |
| `/vercel:env` | Manage environment variables |
| `/vercel:status` | Project status overview |
| `/vercel:marketplace` | Discover and install marketplace integrations |

## Usage

After installing, skills are discovered automatically via Codex's metadata-based matching. You can also invoke skills directly via slash commands:

```text
/vercel:nextjs
/vercel:ai-sdk
/vercel:deploy prod
```

## Architecture

```text
vercel/
├── .codex-plugin/plugin.json       # Plugin manifest
├── vercel.md                        # Ecosystem graph + conventions
├── skills/                          # 47 skills discovered via SKILL.md metadata
│   ├── agent-browser/
│   ├── ai-elements/
│   ├── ai-gateway/
│   ├── ai-sdk/
│   ├── auth/
│   ├── bootstrap/
│   ├── chat-sdk/
│   ├── cms/
│   ├── cron-jobs/
│   ├── deployments-cicd/
│   ├── email/
│   ├── env-vars/
│   ├── json-render/
│   ├── marketplace/
│   ├── nextjs/
│   ├── observability/
│   ├── payments/
│   ├── routing-middleware/
│   ├── runtime-cache/
│   ├── shadcn/
│   ├── sign-in-with-vercel/
│   ├── turbopack/
│   ├── turborepo/
│   ├── v0-dev/
│   ├── vercel-agent/
│   ├── vercel-api/
│   ├── vercel-cli/
│   ├── vercel-firewall/
│   ├── vercel-flags/
│   ├── vercel-functions/
│   ├── vercel-queues/
│   ├── vercel-sandbox/
│   ├── vercel-storage/
│   └── workflow/
├── agents/                          # 3 specialist agents
└── commands/                        # 5 slash commands
```

## Ecosystem Coverage (March 2026)

- Next.js 16 (App Router, Cache Components, Proxy, View Transitions)
- AI SDK v6 (Agents, MCP, DevTools, Reranking, Image Editing)
- AI Elements (pre-built React components for AI interfaces)
- Chat SDK (multi-platform chat bots — Slack, Telegram, Teams, Discord)
- Workflow DevKit (DurableAgent, Worlds, open source)
- AI Gateway (100+ models, provider routing, cost tracking)
- Vercel Functions (Fluid Compute, streaming, Cron Jobs)
- Storage (Blob, Edge Config, Neon Postgres, Upstash Redis)
- Routing Middleware (request interception, Edge/Node.js/Bun runtimes)
- Runtime Cache API (per-region KV cache, tag-based invalidation)
- Vercel Flags (feature flags, Flags Explorer, gradual rollouts, A/B testing)
- Vercel Queues (durable event streaming, topics, consumer groups, retries)
- Vercel Agent (AI code review, incident investigation)
- Vercel Sandbox (Firecracker microVMs for untrusted code)
- Sign in with Vercel (OAuth 2.0/OIDC identity provider)
- Auth integrations (Clerk, Descope, Auth0)
- CMS integrations (Sanity, Contentful, DatoCMS, Storyblok, Builder.io)
- Email (Resend with React Email templates)
- Payments (Stripe via Vercel Marketplace)
- shadcn/ui (CLI, component installation, custom registries, theming)
- Turborepo (--affected, remote caching, Rust core)
- Turbopack (default bundler in Next.js 16)
- Microfrontends (multi-app composition, independent deploys)
- OG Image Generation (@vercel/og, dynamic social images at the edge)
- v0 (agentic intelligence, GitHub integration)
- Vercel Firewall (DDoS, WAF, Bot Filter)
- Vercel CLI (cache management, MCP integration, marketplace discovery)
- Vercel Observability (Analytics, Speed Insights, Drains)
- Vercel Marketplace (one-click integrations, unified billing)
- Agent Browser (browser automation for dev server verification and testing)

## Reporting Issues

If you hit an issue with the upstream content itself, file it in [vercel/vercel-plugin](https://github.com/vercel/vercel-plugin/issues). If the issue is specific to this marketplace packaging or the local `vercel` plugin identity, fix it here in `openai/plugins`.
