# Vercel Ecosystem — Relational Knowledge Graph (as of Mar 4, 2026)

> This document is the master reference for understanding the entire Vercel ecosystem.
> It maps every product, library, CLI, API, and service — how they relate, when to use each,
> and which bundled skills provide deeper guidance.

---

## Legend

- **[PRODUCT]** — A Vercel product or service
- **→ depends on** — Runtime or build-time dependency
- **↔ integrates with** — Bidirectional integration
- **⇢ alternative to** — Can substitute for
- **⊃ contains** — Parent/child relationship
- **⤳ skill:** — Link to a bundled skill for detailed guidance
- **📖 docs:** — Link to official documentation

---

## 1. Core Platform

```
VERCEL PLATFORM                            📖 docs: https://vercel.com/docs
├── Deployment Engine (CI/CD, Preview URLs, Production)
│   → Git Provider (GitHub, GitLab, Bitbucket)
│   → Build System (Turbopack or framework-native)
│   ↔ Vercel CLI
│   ↔ Vercel REST API / @vercel/sdk
│   ⤳ skill: vercel-cli
│   ⤳ skill: deployments-cicd
│
├── Edge Network (Global CDN, ~300ms propagation)
│   ⊃ Edge Functions (V8 isolates, Web Standard APIs)
│   ⊃ Serverless Functions (Node.js, Python, Go, Ruby)
│   ⊃ Fluid Compute (unified execution model)
│   ⊃ Routing Middleware (request interception before cache, any framework)
│   ⊃ Runtime Cache (per-region key-value, tag-based invalidation)
│   ⊃ Cron Jobs (scheduled function invocation → see § Functions decision matrix)
│   ⤳ skill: cron-jobs
│   ⤳ skill: vercel-functions
│   ⤳ skill: routing-middleware
│   ⤳ skill: runtime-cache
│
├── Services API (multiple services in one project)
│   ⊃ experimentalServices in vercel.json
│   ⊃ Multiple backends and frontends deployed to the same domain
│   → Deployment Engine (services deployed as one application)
│   ↔ Vercel CLI (vercel dev auto-detects and runs all services)
│   ⤳ skill: vercel-services  📖 docs: https://vercel.com/docs/services
│
├── Domains & DNS
│   → Deployment Engine
│   ↔ Vercel Firewall
│   ⤳ skill: vercel-cli  (vercel domains, vercel dns, vercel certs)
│
├── Environment Variables                        ⤳ skill: env-vars
│   → Deployment Engine
│   ↔ Vercel CLI (vercel env)
│   ↔ Marketplace Integrations (auto-provisioned)
│   ⤳ skill:bootstrap
│
├── Secure Compute (isolated infrastructure for compliance workloads)
│   → Deployment Engine (opt-in per project)
│   ↔ Vercel Functions (dedicated execution environment)
│   ↔ Vercel Firewall (network-level isolation)
│
├── OIDC Federation (deploy without long-lived tokens)
│   → Deployment Engine (CI/CD token exchange)
│   ↔ Teams & Access Control (identity-based auth)
│   ↔ GitHub Actions, GitLab CI (short-lived OIDC tokens)
│
├── Preview Comments (collaborate on preview deployments)
│   → Deployment Engine (preview URLs)
│   ↔ Vercel Toolbar (embedded comment UI)
│   ↔ Teams & Access Control (team-scoped threads)
│
├── Vercel Toolbar (developer toolbar for preview deployments)
│   → Deployment Engine (preview URLs)
│   ↔ Preview Comments (inline annotation)
│   ↔ Vercel Analytics (performance overlay)
│   ↔ Edge Config (feature flag toggles)
│
├── Vercel Templates (starter kits and example repos)
│   → Deployment Engine (one-click deploy)
│   ↔ Vercel Marketplace (pre-configured integrations)
│   ↔ Next.js, AI SDK, v0 (framework starters)
│   ⊃ next-forge (production SaaS monorepo starter)    ⤳ skill: next-forge
│       → Turborepo, Clerk, Prisma/Neon, Stripe, Resend, shadcn/ui, Sentry, PostHog
│       → 7 apps (app, web, api, email, docs, studio, storybook)
│       → 20 @repo/* workspace packages
│
├── Vercel Queues (durable event streaming)
│   ⊃ Topics, consumer groups, delayed delivery
│   ⊃ At-least-once delivery, 3-AZ durability
│   → Vercel Functions (consumers run as functions)
│   ↔ Workflow DevKit (Queues powers WDK under the hood)
│   ⤳ skill: vercel-queues
│
├── Vercel Flags (feature flags platform)
│   ⊃ Unified dashboard, Flags Explorer
│   ⊃ Gradual rollouts, A/B testing
│   ⊃ Provider adapters (LaunchDarkly, Statsig, Hypertune)
│   ↔ Edge Config (flag storage at the edge)
│   ↔ Vercel Toolbar (flag toggles in preview)
│   ⤳ skill: vercel-flags
│
└── Teams & Access Control
    ↔ Vercel REST API
    ↔ Vercel Dashboard
```

---

## 2. Frameworks

```
NEXT.JS (v16+)                           ⤳ skill: nextjs  📖 docs: https://nextjs.org/docs
├── App Router (file-system routing)
│   ⊃ Server Components (default, zero client JS)
│   ⊃ Client Components ('use client')
│   ⊃ Server Actions / Server Functions ('use server')
│   ⊃ Route Handlers (API endpoints)
│   ⊃ Middleware → renamed to Proxy in v16
│   ⊃ Cache Components ('use cache')
│   ⊃ Layouts, Loading, Error boundaries
│   ⊃ Parallel & Intercepting Routes
│   ⊃ Dynamic Segments ([id], [...slug], [[...slug]])
│
├── Rendering Strategies
│   ⊃ SSR (Server-Side Rendering)
│   ⊃ SSG (Static Site Generation)
│   ⊃ ISR (Incremental Static Regeneration)
│   ⊃ PPR (Partial Prerendering) → evolving to Cache Components
│   ⊃ Streaming (React Suspense boundaries)
│
├── Build System
│   → Turbopack (default bundler in v16)
│   → Webpack (legacy, still supported)
│
├── Key Integrations
│   ↔ Vercel AI SDK (chat UIs, streaming, tool calling)
│   ↔ Vercel Analytics / Speed Insights           ⤳ skill: observability
│   ↔ Vercel Image Optimization (next/image)      ⤳ skill: nextjs
│   ↔ Satori / @vercel/og (dynamic OG images)     ⤳ skill: satori
│   ↔ Vercel Font Optimization (next/font)
│   ↔ Vercel Functions (automatic from route handlers / server actions)
│
└── Deployment
    → Vercel Platform (optimized, zero-config)
    ↔ Vercel CLI (vercel dev, vercel build)

SHADCN/UI                                ⤳ skill: shadcn  📖 docs: https://ui.shadcn.com
├── CLI (npx shadcn@latest init/add/build/search)
│   ⊃ Component source code copied to your project
│   ⊃ Radix UI primitives + Tailwind CSS
│   ⊃ CSS variable theming (oklch)
│   ⊃ Custom registry system (build + host your own)
│   ⊃ Namespaced registries (@v0, @acme, @ai-elements)
│
├── Key Patterns
│   ⊃ cn() utility (clsx + tailwind-merge)
│   ⊃ Dark mode via className="dark" on <html>
│   ⊃ TooltipProvider at layout root
│   ⊃ Components are source code — fully customizable
│
└── Integrations
    ↔ Next.js (primary framework)
    ↔ AI Elements (AI components built on shadcn)     ⤳ skill: ai-elements
    ↔ v0 (generates shadcn/ui components)             ⤳ skill: v0-dev
    ↔ Vite, Remix, Astro, Laravel (all supported)

OTHER SUPPORTED FRAMEWORKS
├── Astro          ↔ Vercel Adapter
├── SvelteKit      ↔ Vercel Adapter
├── Nuxt           ↔ Vercel Adapter
├── Remix          ↔ Vercel Adapter
├── Angular        ↔ Vercel Adapter
├── Solid          ↔ Vercel Adapter
└── Static HTML/JS → Direct deploy
```

---

## 3. AI Products

```
AI SDK (v6, TypeScript)                    ⤳ skill: ai-sdk  📖 docs: https://sdk.vercel.ai/docs
├── Core
│   ⊃ generateText / streamText
│   ⊃ generateText / streamText with Output.object() (structured output)
│   ⊃ generateImage / editImage (image-only models)
│   ⊃ Image generation via multimodal LLMs (generateText → result.files)
│   ⊃ embed / embedMany (vector embeddings)
│   ⊃ rerank (relevance reordering)
│   ⊃ Language Model Middleware (RAG, guardrails)
│   ⊃ Tool Calling (inputSchema/outputSchema, MCP-aligned)
│   ⊃ Dynamic Tools (runtime-defined, MCP integration)
│   ⊃ Agent class (agent.generate / agent.stream, stopWhen, prepareStep)
│   ⊃ Subagents
│   ⊃ Tool Execution Approval
│   ⊃ DevTools (npx @ai-sdk/devtools)
│
├── UI Layer (@ai-sdk/react, @ai-sdk/svelte, @ai-sdk/vue)
│   ⊃ useChat (chat interface hook)
│   ⊃ useCompletion (text completion hook)
│   ⊃ useObject (structured streaming hook)
│   ⊃ UIMessage / ModelMessage types
│   ↔ AI Elements (pre-built chat UI components)       ⤳ skill: ai-elements
│
├── AI Elements (ai-elements) — MANDATORY UI FOR ALL AI TEXT  ⤳ skill: ai-elements
│   ⊃ 40+ React components for AI interfaces
│   ⊃ Message (chat with useChat), MessageResponse (any AI markdown)
│   ⊃ Conversation, Tool, Reasoning, CodeBlock
│   ⊃ Built on shadcn/ui (custom registry)
│   ⊃ Handles UIMessage parts, streaming, markdown
│   ⊃ MessageResponse = universal renderer for AI text (chat, workflows, reports, notifications)
│   ⊃ Never render AI text as raw {text} or <p>{content}</p> — use AI Elements
│   → AI SDK UI hooks (useChat, useCompletion)
│   → shadcn/ui (component primitives)                 ⤳ skill: shadcn
│
│
├── MCP Integration (@ai-sdk/mcp)
│   ⊃ MCP Client (connect to any MCP server)
│   ⊃ OAuth authentication for remote MCP servers
│   ⊃ Resources, Prompts, Elicitation
│   ⊃ mcp-to-ai-sdk CLI (static tool generation for security)
│
├── Providers (Global Provider System: "provider/model")
│   ⊃ @ai-sdk/openai (GPT-5.x, o-series)
│   ⊃ @ai-sdk/anthropic (Claude 4.x)
│   ⊃ @ai-sdk/google (Gemini)
│   ⊃ @ai-sdk/amazon-bedrock
│   ⊃ @ai-sdk/azure
│   ⊃ @ai-sdk/mistral
│   ⊃ @ai-sdk/cohere
│   ⊃ @ai-sdk/xai (Grok)
│   ⊃ @ai-sdk/deepseek
│   ⊃ @ai-sdk/gateway (Vercel AI Gateway routing)
│   └── ... 20+ providers
│
├── Streaming Protocol
│   ⊃ SSE-based (Server-Sent Events)
│   → Vercel Functions (streaming support)
│   ↔ Next.js Route Handlers / Server Actions
│   ↔ AI Elements (render streaming responses)          ⤳ skill: ai-elements
│
└── Key Patterns
    ↔ Next.js (chat apps, AI features in web apps)
    ↔ Workflow DevKit (durable agents)
    ↔ AI Gateway (model routing, cost tracking)
    ↔ Generation Persistence (IDs, URLs, cost tracking) ⤳ skill: ai-generation-persistence
    ↔ v0 (AI-generated UI components)
    ↔ AI Elements (production chat UI components)      ⤳ skill: ai-elements
    ↔ shadcn/ui (component foundation)                 ⤳ skill: shadcn

AI GATEWAY                                 ⤳ skill: ai-gateway  📖 docs: https://vercel.com/docs/ai-gateway
├── Unified API ("creator/model-name" format)
│   → @ai-sdk/gateway package
│   ↔ AI SDK (automatic when using model strings)
│
├── Authentication
│   ⊃ OIDC (default — auto-provisioned via `vercel env pull`)
│   ⊃ AI_GATEWAY_API_KEY (alternative — manual key)
│   ⊃ VERCEL_OIDC_TOKEN (short-lived JWT, auto-refreshed on deploy)
│   → @vercel/oidc (reads VERCEL_OIDC_TOKEN from env)
│   → Vercel CLI (`vercel env pull` provisions OIDC token)
│
├── Features
│   ⊃ Provider Routing (order, only, fallback models)
│   ⊃ Automatic Retries & Failover
│   ⊃ Cost Tracking & Usage Attribution (tags, user tracking)
│   ⊃ <20ms routing latency
│   ⊃ Bring Your Own Key (0% markup)
│   ⊃ Built-in Observability
│
├── Image Generation (gateway-native)
│   ⊃ Multimodal LLMs: model: 'google/gemini-3.1-flash-image-preview' + generateText → result.files
│   ⊃ Image-only models: experimental_generateImage (Imagen 4.0, Flux 2, Grok Imagine)
│   ⊃ Default model: google/gemini-3.1-flash-image-preview
│   ⊃ DALL-E, gemini-2.x image models are outdated — use Gemini 3.1 Flash Image Preview
│
├── Supported Providers
│   ⊃ OpenAI, Anthropic, Google, Meta, xAI, Mistral
│   ⊃ DeepSeek, Amazon Bedrock, Cohere, Perplexity, Alibaba
│   └── 100+ models total
│
└── Multimodal
    ⊃ Text, Image, Video generation
    ↔ AI SDK (unified interface)

WORKFLOW DEVKIT (WDK)                      ⤳ skill: workflow  📖 docs: https://vercel.com/docs/workflow
├── Core Concepts
│   ⊃ 'use workflow' directive
│   ⊃ 'use step' directive
│   ⊃ Durable execution (survives deploys, crashes)
│   ⊃ Deterministic replay
│   ⊃ Pause/resume (minutes to months)
│   ⊃ Hooks (defineHook → human-in-the-loop approval, pause/resume)
│   ⊃ AI Gateway OIDC required (vercel link + vercel env pull before dev)
│
├── Worlds (Execution Environments)
│   ⊃ Local World (JSON files on disk)
│   ⊃ Vercel World (managed, zero-config on Vercel)
│   ⊃ Self-hosted (Postgres, Redis, custom)
│
├── AI Integration
│   ⊃ DurableAgent (@workflow/ai/agent)
│   → AI SDK Agent class (wrapped with durability)
│   → AI SDK tool calling (each tool = retryable step)
│   → AI Gateway (OIDC auth for model strings in workflow steps)
│
├── Key Properties
│   ⊃ Open source, no vendor lock-in
│   ⊃ TypeScript-native (async/await, no YAML)
│   ⊃ Observable (step-level visibility)
│   ⊃ Retryable (automatic retry on failure)
│
└── Integrations
    ↔ AI SDK 6 (DurableAgent)
    ↔ Vercel Functions (automatic step isolation)
    ↔ Next.js (API routes as workflow endpoints)

v0 (AI Development Agent)                  ⤳ skill: v0-dev  📖 docs: https://v0.dev/docs
├── Capabilities
│   ⊃ Natural language → production React/Next.js code
│   ⊃ Visual input (Figma, screenshots, sketches)
│   ⊃ Multi-framework output (React, Vue, Svelte, HTML)
│   ⊃ Agentic intelligence (research, plan, debug, iterate)
│
├── Integration Features
│   ⊃ GitHub Integration (branches, PRs, deploy on merge)
│   ⊃ One-click Vercel deployment
│   ⊃ Environment variable import from Vercel
│   ⊃ shadcn/ui + Tailwind CSS defaults
│
└── Ecosystem Position
    → Next.js (primary output framework)
    → Vercel Platform (deployment target)
    ↔ AI SDK (AI features in generated apps)
    ↔ Vercel Marketplace (integrations in generated apps)

CHAT SDK (TypeScript)                       ⤳ skill: chat-sdk  📖 docs: https://chat-sdk.dev
├── Core
│   ⊃ Chat class (event routing, adapter coordination)
│   ⊃ Thread & Message (normalized cross-platform models)
│   ⊃ Postable interface (shared by Thread and Channel: post, postEphemeral, mentionUser, startTyping)
│   ⊃ openDM / channel (out-of-thread message routing)
│   ⊃ Serialization (registerSingleton, reviver for JSON deserialization)
│   ⊃ Cards (JSX → Slack Block Kit, Teams Adaptive Cards, Discord Embeds)
│   ⊃ Modals (Slack-only form dialogs)
│   ⊃ Streaming (native on Slack, post+edit fallback elsewhere)
│   ⊃ Emoji system (cross-platform placeholders)
│
├── Platform Adapters
│   ⊃ @chat-adapter/slack (single + multi-workspace, OAuth, native streaming)
│   ⊃ @chat-adapter/teams (Microsoft Teams, Adaptive Cards)
│   ⊃ @chat-adapter/discord (HTTP Interactions + Gateway, Ed25519)
│   ⊃ @chat-adapter/telegram (Telegram Bot API, webhook verification)
│   ⊃ @chat-adapter/gchat (Google Chat, Spaces)
│   ⊃ @chat-adapter/github (Issues/PRs as threads)
│   ⊃ @chat-adapter/linear (Issue comment threads)
│
├── State Adapters
│   ⊃ @chat-adapter/state-redis (production, distributed locking)
│   ⊃ @chat-adapter/state-ioredis (Redis Cluster/Sentinel)
│   ⊃ @chat-adapter/state-memory (dev/testing only)
│
├── Event Handlers
│   ⊃ onNewMention, onSubscribedMessage, onNewMessage
│   ⊃ onReaction, onAction, onSlashCommand
│   ⊃ onModalSubmit, onModalClose
│   ⊃ onAssistantThreadStarted, onAssistantContextChanged
│   ⊃ onAppHomeOpened
│   ⊃ onMemberJoinedChannel
│
├── Key Patterns
│   ↔ AI SDK (streaming AI responses via thread.post(textStream))
│   ↔ Workflow DevKit (registerSingleton/reviver for durable serialization)
│   ↔ Vercel Functions (webhook handlers, waitUntil)
│   ↔ Next.js (API routes for webhooks)
│   ↔ Upstash Redis (state adapter backend)
│
└── Testing
    ⊃ Replay framework (record real webhooks, replay in tests)
    ⊃ Test context factories (createSlackTestContext, etc.)
    ⊃ Assertion helpers (expectValidMention, expectSentMessage)

VERCEL AGENT                               ⤳ skill: vercel-agent  📖 docs: https://vercel.com/docs/workflow/agent
├── Capabilities
│   ⊃ Automated code review (PR analysis, security, logic errors)
│   ⊃ Incident investigation (anomaly debugging)
│   ⊃ SDK installation assistance
│   ⊃ Vercel Sandbox (secure patch validation)   ⤳ skill: vercel-sandbox
│
└── Integrations
    ↔ GitHub (PR triggers, @vercel mentions)
    ↔ Vercel Sandbox (isolated code execution)
    ↔ AI SDK (underlying AI capabilities)
```

---

## 4. Build Tools

```
TURBOREPO                                  ⤳ skill: turborepo  📖 docs: https://turbo.build/repo/docs
├── Purpose: Monorepo build orchestration
│   ⊃ Task caching (local + remote)
│   ⊃ Parallel execution (all cores)
│   ⊃ Incremental builds (content-aware hashing)
│   ⊃ --affected flag (changed packages only)
│   ⊃ Pruned subsets (deploy only what's needed)
│   ⊃ Rust-powered core
│
├── Remote Caching
│   → Vercel Account (free tier available)
│   ↔ CI/CD pipelines (shared cache across machines)
│
├── Conformance (code quality + best-practice checks for monorepos)
│   ⊃ Automated rule enforcement (ESLint, TypeScript, import boundaries)
│   ↔ Turborepo (runs as part of task pipeline)
│   ↔ Vercel Platform (enforced on deploy)
│   ⤳ skill: turborepo  (Conformance is configured within Turborepo)
│
└── Integrations
    ↔ Next.js (monorepo with multiple Next.js apps)
    ↔ Vercel Platform (auto-detected, optimized builds)
    ↔ Turbopack (per-app bundling)

TURBOPACK                                  ⤳ skill: turbopack  📖 docs: https://turbo.build/pack/docs
├── Purpose: JavaScript/TypeScript bundler
│   ⊃ Instant HMR (doesn't degrade with app size)
│   ⊃ Multi-environment builds (Browser, Server, Edge, SSR, RSC)
│   ⊃ TypeScript, JSX, CSS, CSS Modules, WebAssembly
│   ⊃ React Server Components (native support)
│
├── Status: Default bundler in Next.js 16
│   → Next.js (top-level turbopack config)
│   ⇢ alternative to: Webpack
│
└── Architecture
    ⊃ Rust-powered
    ⊃ Incremental computation engine
    ⊃ Lives in the Next.js monorepo
```

AGENT BROWSER                              ⤳ skill: agent-browser
├── Purpose: Browser automation for dev-server testing
│   ⊃ Snapshot-driven interaction with localhost
│   ⊃ Works with next dev, vite, nuxt dev, vercel dev
│
└── Use When: Verifying UI behavior, form testing, e2e workflows

AGENT BROWSER VERIFY                       ⤳ skill: agent-browser-verify
├── Purpose: Automated dev-server verification checklist
│   ⊃ Triggers on dev-server start (next dev, vite, etc.)
│   ⊃ Runs visual gut-check: page loads, no errors, key UI renders
│
└── Use When: After starting a dev server, before continuing development

VERIFICATION                                   ⤳ skill: verification
├── Purpose: Full-story verification orchestrator
│   ⊃ Infers the user story from recent edits and project structure
│   ⊃ Verifies end-to-end: browser → API → data → response
│   ⊃ Coordinates agent-browser-verify, investigation-mode, observability
│
└── Use When: Dev server starts, user says "something's off", or verifying a feature works end-to-end

REACT BEST PRACTICES                       ⤳ skill: react-best-practices
├── Purpose: TSX/JSX quality review checklist
│   ⊃ Component structure, hooks, a11y, performance, TypeScript
│   ⊃ Triggers when editing component files
│
└── Use When: After editing multiple TSX components, before shipping

SWR (v2, React Hooks)                      ⤳ skill: swr  📖 docs: https://swr.vercel.app
├── Purpose: Client-side data fetching with stale-while-revalidate caching
│   ⊃ useSWR (data fetching with auto-revalidation)
│   ⊃ useSWRMutation (remote mutations, optimistic UI)
│   ⊃ useSWRInfinite (pagination & infinite loading)
│   ⊃ SWRConfig (global configuration provider)
│
├── Key Features
│   ⊃ Request deduplication
│   ⊃ Revalidation on focus, reconnect, interval
│   ⊃ Built-in cache with shared keys
│   ⊃ Middleware support
│
└── Integrations
    ↔ Next.js (App Router & Pages Router)
    ↔ React (any React framework)

NCC (Node.js Compiler Collection)          ⤳ skill: ncc  📖 docs: https://github.com/vercel/ncc
├── Purpose: Compile Node.js modules into a single file with all dependencies
│   ⊃ Serverless function bundling
│   ⊃ CLI tool distribution
│   ⊃ GitHub Actions bundling
│   ⊃ TypeScript compilation (uses project tsconfig.json)
│   ⊃ External module exclusion
│
└── Use When: Single-file deployment, reducing node_modules, bundling serverless functions

MICRO (HTTP Microservices)                 ⤳ skill: micro  📖 docs: https://github.com/vercel/micro
├── Purpose: Lightweight async HTTP microservices framework
│   ⊃ Single-endpoint HTTP servers
│   ⊃ JSON/text/buffer body parsing
│   ⊃ Composable handler middleware
│   ⊃ micro-dev for hot-reloading development
│
└── Use When: Minimal HTTP services, single-purpose API endpoints

GEIST (Font Family)                        ⤳ skill: geist  📖 docs: https://github.com/vercel/geist-font
├── Purpose: Vercel's open-source font family for Next.js
│   ⊃ Geist Sans (modern sans-serif for UI)
│   ⊃ Geist Mono (monospace for code)
│   ⊃ next/font integration (zero layout shift)
│   ⊃ CSS variables (--font-geist-sans, --font-geist-mono)
│   ⊃ Variable font (all weights 100–900)
│
└── Use When: Typography setup in Next.js, Vercel design system styling

GEISTDOCS (Documentation Template)         ⤳ skill: geistdocs  📖 docs: https://preview.geistdocs.com/docs
├── Purpose: Production-ready documentation template for Vercel microsites
│   ⊃ Next.js 16 + Fumadocs framework
│   ⊃ MDX authoring with auto-routing (content/docs/)
│   ⊃ AI-powered chat (Ask AI, llms.txt, Open in Chat)
│   ⊃ i18n, feedback widget, RSS, Edit on GitHub
│   ⊃ geistdocs.tsx config (Logo, nav, title, prompt, translations)
│
└── Use When: Building documentation sites, docs microsites, developer docs

---

## 5. Storage & Data

```
VERCEL BLOB (active, first-party)          ⤳ skill: vercel-storage  📖 docs: https://vercel.com/docs/storage/vercel-blob
├── Purpose: File storage for unstructured data
│   ⊃ Client uploads (up to 5 TB)
│   ⊃ Conditional gets with ETags
│   ⊃ @vercel/blob package
│
└── Use When: Media files, user uploads, large assets

VERCEL EDGE CONFIG (active, first-party)   ⤳ skill: vercel-storage  📖 docs: https://vercel.com/docs/storage/edge-config
├── Purpose: Global low-latency key-value for config
│   ⊃ Feature flags
│   ⊃ A/B testing configuration
│   ⊃ Dynamic routing rules
│   ⊃ @vercel/edge-config package (supports Next.js 16 cacheComponents)
│
└── Use When: Config that must be read at the edge instantly

MARKETPLACE STORAGE (partner-provided)     ⤳ skill: vercel-storage
├── Neon Postgres (replaces @vercel/postgres)
│   ⊃ @neondatabase/serverless
│   ⊃ Branching, auto-scaling
│   ⇢ alternative to: @vercel/postgres (sunset)
│
├── Upstash Redis (replaces @vercel/kv)
│   ⊃ @upstash/redis
│   ⊃ Same Vercel billing integration
│   ⇢ alternative to: @vercel/kv (sunset)
│
└── Other: MongoDB, PlanetScale, Supabase, etc.
    ↔ Vercel Marketplace (one-click install, auto env vars)
```

**IMPORTANT**: `@vercel/postgres` and `@vercel/kv` are **sunset**. Use Neon and Upstash respectively.

---

## 6. Security

```
VERCEL FIREWALL                            ⤳ skill: vercel-firewall  📖 docs: https://vercel.com/docs/security/vercel-firewall
├── DDoS Protection (automatic, all plans)
│   ⊃ Layer 3/4 mitigation
│   ⊃ Layer 7 protection
│   ⊃ 40x faster with stream processing
│
├── Web Application Firewall (WAF)
│   ⊃ Custom rules engine (path, user-agent, IP, geo, JA4)
│   ⊃ Framework-aware rules (no regex needed)
│   ⊃ Managed rulesets (OWASP Top 10, Enterprise)
│   ⊃ Rate limiting
│   ⊃ Bot Filter (public beta, all plans)
│   ⊃ Attack Challenge Mode
│   ⊃ Persistent Actions (block repeat offenders)
│   ⊃ Firewall API (programmatic control)
│   ⊃ 300ms global propagation
│
└── Integrations
    ↔ Edge Network (embedded in request lifecycle)
    ↔ Vercel Observability (linked logs)
    ↔ Vercel REST API (Firewall API)

SIGN IN WITH VERCEL                        ⤳ skill: sign-in-with-vercel  📖 docs: https://vercel.com/docs/security/sign-in-with-vercel
├── OAuth 2.0 / OIDC Identity Provider
│   ⊃ Authorization Code flow
│   ⊃ ID tokens with user profile claims
│   ⊃ Access tokens for Vercel API calls
│
└── Integrations
    ↔ Teams & Access Control (team-scoped auth)
    ↔ Vercel REST API (token exchange)
    ↔ Next.js (auth route handlers)

AUTHENTICATION INTEGRATIONS                ⤳ skill: auth
├── Clerk (native Vercel Marketplace)
│   ⊃ Auto-provisioned env vars
│   ⊃ Middleware auth patterns
│   ⊃ Pre-built UI components
│
├── Descope (Vercel Marketplace)
│   ⊃ Passwordless / social login flows
│   ⊃ Visual flow builder
│
├── Auth0
│   ⊃ Enterprise SSO / SAML
│   ⊃ Multi-tenant identity
│
└── Integrations
    ↔ Vercel Marketplace (provisioning)
    ↔ Next.js Middleware (route protection)
    ↔ Sign in with Vercel (Vercel OAuth)
```

---

## 7. Observability

```
VERCEL OBSERVABILITY                        ⤳ skill: observability  📖 docs: https://vercel.com/docs/analytics
├── Web Analytics
│   ⊃ First-party, privacy-friendly
│   ⊃ Custom events (Pro/Enterprise)
│   ⊃ UTM parameters (Analytics Plus)
│   ↔ Next.js (@vercel/analytics)
│
├── Speed Insights
│   ⊃ Real user performance data
│   ⊃ Core Web Vitals
│   ↔ Next.js (@vercel/speed-insights)
│
├── Monitoring & Logs
│   ⊃ Real-time infrastructure logs
│   ⊃ Function runtime logs
│   ⊃ Custom queries and visualizations
│   ⤳ skill: investigation-mode
│
├── Vercel Drains (export observability data)
│   ⊃ OpenTelemetry-compatible traces
│   ⊃ Web analytics events
│   ⊃ Speed Insights metrics
│   → Datadog, Honeycomb, Grafana Tempo, New Relic
│
└── Integrations
    ↔ Vercel Firewall (security event logs)
    ↔ Vercel Functions (automatic tracing)
    ↔ Next.js (automatic instrumentation)
```

---

## 8. CLI & API

```
VERCEL CLI (vercel / vc)                   ⤳ skill: vercel-cli  📖 docs: https://vercel.com/docs/cli
├── Deployment
│   ⊃ vercel / vercel deploy (preview deployment)
│   ⊃ vercel --prod (production deployment)
│   ⊃ vercel build (local build)
│   ⊃ vercel deploy --prebuilt (deploy build output only)
│   ⊃ vercel promote / vercel rollback
│
├── Development
│   ⊃ vercel dev (local dev server)
│   ⊃ vercel link (connect to Vercel project)
│   ⊃ vercel pull (pull env vars and project settings)
│
├── Environment Variables
│   ⊃ vercel env ls / add / rm / pull
│   ⊃ Branch-scoped variables
│   ⊃ Sensitive variables (write-only)
│
├── Marketplace Integrations
│   ⊃ vercel integration add (install integration)
│   ⊃ vercel integration list (list installed)
│   ⊃ vercel integration open (open dashboard)
│   ⊃ vercel integration remove (uninstall)
│
├── Other
│   ⊃ vercel logs (view function logs)
│   ⊃ vercel inspect (deployment details)
│   ⊃ vercel domains (manage domains)
│   ⊃ vercel certs (SSL certificates)
│   ⊃ vercel dns (DNS records)
│   ⊃ vercel teams (team management)
│
└── CI/CD Integration
    ⊃ VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
    ↔ Any CI provider (GitHub Actions, Azure DevOps, etc.)

VERCEL MCP SERVER (Official)                ⤳ skill: vercel-api  📖 docs: https://vercel.com/docs/mcp
├── URL: https://mcp.vercel.com
│   ⊃ Streamable HTTP transport
│   ⊃ OAuth 2.1 authentication (automatic)
│   ⊃ Read-only in initial release (Beta)
│
├── MCP Tools
│   ⊃ Search & navigate Vercel / Next.js / AI SDK docs
│   ⊃ List & inspect projects and deployments
│   ⊃ Query build logs and function invocation logs
│   ⊃ List domains and environment variables
│   ⊃ View team members and settings
│
├── Supported AI Clients
│   ⊃ Claude Code (`claude mcp add --transport http vercel https://mcp.vercel.com`)
│   ⊃ Cursor, VS Code (reviewed and approved clients)
│
└── Relationship to REST API
    → Uses Vercel REST API under the hood
    ↔ AI SDK MCP Client (@ai-sdk/mcp)

VERCEL REST API / @vercel/sdk               ⤳ skill: vercel-api  📖 docs: https://vercel.com/docs/rest-api
├── Endpoint Categories
│   ⊃ /v1/deployments — Create, list, inspect, cancel
│   ⊃ /v1/projects — CRUD, environment variables, domains
│   ⊃ /v1/teams — Members, billing, settings
│   ⊃ /v1/domains — Register, configure, transfer
│   ⊃ /v1/dns — Record management
│   ⊃ /v1/certs — SSL certificate management
│   ⊃ /v1/secrets — Secret management
│   ⊃ /v1/integrations — Marketplace integration management
│   ⊃ /v1/edge-config — Edge Config management
│   ⊃ /v1/firewall — WAF rule management
│
├── SDK (@vercel/sdk)
│   ⊃ TypeScript SDK for all API endpoints
│   ⊃ vercel.deployments, vercel.projects, etc.
│
└── Authentication
    ⊃ Bearer Token (personal or team)
    ⊃ OAuth (for integrations)
```

---

## 9. Marketplace

```
VERCEL MARKETPLACE                          ⤳ skill: marketplace  📖 docs: https://vercel.com/marketplace
├── Categories
│   ⊃ Databases (Neon, MongoDB, Supabase, PlanetScale)
│   ⊃ CMS (Sanity, Contentful, Storyblok)      ⤳ skill: cms
│   ⊃ Auth (Clerk, Auth0)
│   ⊃ Payments (Stripe)                       ⤳ skill: payments
│   ⊃ Email (Resend)                          ⤳ skill: email
│   ⊃ Feature Flags (LaunchDarkly, Statsig)
│   ⊃ AI Agents (CodeRabbit, Corridor, Sourcery, Parallel)
│   ⊃ Storage (Upstash Redis, Cloudinary)
│   ⊃ Monitoring (Datadog, Sentry)
│
├── Features
│   ⊃ Unified billing
│   ⊃ One-click install
│   ⊃ Auto-provisioned environment variables
│   ⊃ CLI management (vercel integration add/list/open/remove)
│
└── Integration
    ↔ Vercel CLI (agent-friendly discovery)
    ↔ Vercel REST API (programmatic management)
    ↔ Environment Variables (auto-injected)
```

---

## 10. Decision Matrix — When to Use What

### Rendering Strategy
| Need | Use | Why |
|------|-----|-----|
| Static content, rarely changes | SSG (`generateStaticParams`) | Fastest, cached at edge |
| Static with periodic updates | ISR (`revalidate`) | Fresh enough, still fast |
| Per-request dynamic data | SSR (Server Components) | Always fresh, streamed |
| Mix of static shell + dynamic parts | Cache Components (`'use cache'`) | Best of both worlds |
| Real-time interactive UI | Client Components | Full browser API access |

### Data Mutations
| Need | Use | Why |
|------|-----|-----|
| Form submissions, in-app mutations | Server Actions | Integrated with caching, progressive enhancement |
| Public API, webhooks, large uploads | Route Handlers | REST semantics, streaming support |
| Scheduled tasks | Cron Jobs + Serverless Functions | Reliable scheduling |

### AI Features
| Need | Use | Why |
|------|-----|-----|
| **Any AI feature (default)** | **AI Gateway** (`model: 'provider/model'`) | **Failover, cost tracking, observability — no provider API keys needed on Vercel** |
| **Any streaming AI UI (default)** | **AI Elements** (`npx ai-elements`) + AI SDK `useChat` | **Handles UIMessage parts, streaming markdown, tool calls, reasoning — no manual rendering** |
| **Any AI-generated text (mandatory)** | **AI Elements `<MessageResponse>`** | **Universal markdown renderer — never render AI text as raw `{text}`. Use for chat, workflows, reports, notifications** |
| Chat interface | AI SDK `useChat` + `streamText` + AI Gateway + AI Elements | Streaming UI, provider-agnostic |
| Chat UI components (messages, tools, reasoning) | AI Elements (`npx ai-elements`) | Pre-built, handles UIMessage parts |
| Custom chat rendering (no AI Elements) | Manual `message.parts` iteration | Full control, see ⤳ skill: json-render |
| Image generation (default) | AI Gateway `model: 'google/gemini-3.1-flash-image-preview'` + `generateText` → `result.files` | Multimodal LLM, best quality, gateway-native |
| Image generation (image-only models) | `experimental_generateImage` (Imagen 4.0, Flux 2) | Only for dedicated image models, not multimodal LLMs |
| Structured data extraction | AI SDK `generateText` + `Output.object()` + AI Gateway | Type-safe, schema-validated |
| Multi-step agent | AI SDK `Agent` class + AI Gateway | Loop control, tool calling |
| Production agent (must not lose state) | Workflow DevKit `DurableAgent` | Survives crashes, observable |
| Provider-specific features (e.g., computer use) | Direct provider SDK (`@ai-sdk/anthropic`) | Only when gateway doesn't expose the feature |
| Connect to external tools | AI SDK MCP Client | Standard protocol, OAuth |
| Agent needs live Vercel state | Vercel MCP Server | Read projects, deployments, logs via MCP |
| Multi-platform chat bot (Slack, Teams, Discord, Telegram, etc.) | Chat SDK (`chat` + `@chat-adapter/*`) | Single codebase, unified API, cards, streaming |
| Chat bot with AI responses | Chat SDK + AI SDK (`thread.post(textStream)`) | Streaming AI across all platforms |
| UI generation from prompts | v0 | Visual output, GitHub integration |

**IMPORTANT**: Default to AI Gateway for all AI features. Only use direct provider SDKs (`@ai-sdk/anthropic`, `@ai-sdk/openai`, etc.) when you need provider-specific features not exposed through the gateway.

### Storage
| Need | Use | Why |
|------|-----|-----|
| File uploads, media | Vercel Blob | First-party, up to 5TB |
| Feature flags, A/B config | Edge Config | Ultra-low latency at edge |
| Relational database | Neon (via Marketplace) | Serverless Postgres, branching |
| Key-value cache | Upstash Redis (via Marketplace) | Serverless Redis, same billing |

### Build & Monorepo
| Need | Use | Why |
|------|-----|-----|
| Single Next.js app | Turbopack (default) | Fastest HMR, built-in |
| Monorepo with multiple apps/packages | Turborepo | Caching, parallelism, affected |
| Code quality enforcement in monorepo | Conformance | Automated best-practice checks |
| Non-Next.js framework | Framework-native bundler | Vercel adapters handle deploy |

### Security
| Need | Use | Why |
|------|-----|-----|
| DDoS protection | Vercel Firewall (automatic) | Always on, all plans |
| Custom traffic rules | WAF rules engine | Framework-aware, 300ms propagation |
| Bot blocking | Bot Filter | One-click, public beta |
| Rate limiting | WAF rate limiting | Per-endpoint control |
| OWASP protection | Managed rulesets (Enterprise) | Industry-standard rules |
| Compliance isolation (SOC2, HIPAA) | Secure Compute | Dedicated infrastructure, no shared tenancy |
| Tokenless CI/CD deployments | OIDC Federation | Short-lived tokens, no secrets to rotate |

### Functions
| Need | Use | Why |
|------|-----|-----|
| Standard server logic | Serverless Functions (Node.js) | Full Node.js, up to 14min (paid) |
| Ultra-low latency, simple logic | Edge Functions | <1ms cold start, global |
| Long-running with I/O waits | Fluid Compute | Shared instances, waitUntil |
| AI streaming responses | Streaming Functions | SSE, zero config |
| Scheduled execution | Cron Jobs | vercel.json schedule config |

### Disambiguation: Interception Compute

These three mechanisms all intercept or handle requests before your application logic runs.
Choose based on **where** the interception happens and **what** you need to do.

| Mechanism | Layer | Runtime | Use When | Avoid When |
|-----------|-------|---------|----------|------------|
| **Routing Middleware** (`middleware.ts` / platform-level) | Edge Network, before cache | V8 isolates (Web Standard APIs) | Auth checks, geo-redirects, A/B routing, header rewriting — any framework | You need Node.js APIs, heavy computation, or database access |
| **`proxy.ts`** (Next.js 16+) | Application layer, replaces `middleware.ts` | Node.js | Same use cases as Routing Middleware but you need `node:*` modules, ORM calls, or full Node.js compat | You're not on Next.js 16+; prefer Routing Middleware for non-Next.js frameworks |
| **Edge Functions** | Edge Network, handles the full request | V8 isolates (Web Standard APIs) | Ultra-low-latency API endpoints, simple compute at the edge, streaming responses | You need Node.js runtime, long execution times, or large dependencies |

> **Key distinction**: Routing Middleware and `proxy.ts` are *interceptors* — they rewrite, redirect, or annotate requests before the handler runs. Edge Functions *are* the handler — they produce the response. If you previously used Next.js `middleware.ts` and are upgrading to Next.js 16, rename to `proxy.ts` (see § Migration Awareness).

⤳ skill: routing-middleware — Platform-level request interception
⤳ skill: vercel-functions — Edge Functions and Serverless Functions
⤳ skill: nextjs — `proxy.ts` in Next.js 16

### Disambiguation: Caching Layers

Three distinct caching systems serve different purposes. They can be used independently or layered together.

| Mechanism | Scope | Invalidation | Use When | Avoid When |
|-----------|-------|-------------|----------|------------|
| **Next.js Cache** (`'use cache'`, `revalidate`, `revalidatePath/Tag`) | Per-route or per-component, framework-managed | Time-based (`revalidate: N`), on-demand (`revalidateTag()`, `revalidatePath()`) | Caching rendered pages, component trees, or data fetches within a Next.js app | You need caching outside Next.js, or need to cache arbitrary key-value data |
| **Runtime Cache** (Vercel platform, per-region KV) | Per-region key-value store, any framework | Tag-based (`purgeByTag()`), key-based (`delete()`) | Caching expensive computations, API responses, or shared data across functions — works with any framework on Vercel | You only need page-level caching (use Next.js Cache instead); you need global consistency (Runtime Cache is per-region) |
| **CDN Cache + Purge-by-Tag** (Edge Network, `Cache-Control` + `Cache-Tag` headers) | Global CDN edge, HTTP-level | `Cache-Control` TTL, on-demand purge via Vercel API (`POST /v1/edge-config/purge`) | Static assets, ISR pages, any HTTP response you want cached globally at the edge | Dynamic per-user content, responses that must never be stale |

> **Layering pattern**: A typical Next.js app uses all three — Next.js Cache for component/route-level freshness, Runtime Cache for shared cross-request data (e.g., product catalog), and CDN Cache for static assets and ISR pages. Each layer has its own invalidation strategy; tag-based invalidation can cascade across layers when configured.

⤳ skill: runtime-cache — Per-region key-value caching with tag-based invalidation
⤳ skill: nextjs — `'use cache'`, `revalidatePath`, `revalidateTag`

---

## 11. Common Cross-Product Workflows

### 1. Build an AI Chatbot
```
1. vercel link (or create project in dashboard)
2. Enable AI Gateway in Vercel dashboard → auto-provisions OIDC credentials
3. vercel env pull (pulls VERCEL_OIDC_TOKEN + gateway env vars to .env.local)
4. npm install ai @ai-sdk/react (core SDK + React hooks — `@ai-sdk/react` is required for `useChat`)
5. npx ai-elements (install chat UI components — Message, Conversation, PromptInput)
6. Code: model: 'anthropic/claude-sonnet-4.6' (plain string routes through AI Gateway automatically)
7. Server: convertToModelMessages(messages) → streamText → toUIMessageStreamResponse()
8. Client: useChat({ transport: new DefaultChatTransport({ api: '/api/chat' }) })
9. Next.js (App Router) → AI SDK + AI Elements → AI Gateway (OIDC auth)
                        → Vercel Functions (streaming) → vercel deploy
```

**OIDC Authentication (default):** When you run `vercel env pull`, it provisions a `VERCEL_OIDC_TOKEN` — a short-lived JWT that the AI Gateway uses automatically. No manual API keys needed. The `@ai-sdk/gateway` package reads `VERCEL_OIDC_TOKEN` from the environment via `@vercel/oidc`. On Vercel deployments, OIDC tokens are auto-refreshed. For local dev, re-run `vercel env pull` if the token expires (~24h).
```

### 2. Build a Multi-Platform Chat Bot
```
1. npm install chat @chat-adapter/slack @chat-adapter/telegram @chat-adapter/state-redis
2. Create lib/bot.ts → new Chat({ adapters: { slack, telegram }, state: createRedisState() })
3. Register handlers: onNewMention, onSubscribedMessage, onAction
4. Create webhook routes (for example app/api/bot/slack/route.ts and app/api/bot/telegram/route.ts)
   → bot.webhooks.<platform>(req, { waitUntil })
5. For AI responses: npm install ai → thread.post(result.textStream)
6. For rich messages: use Card JSX → renders to each platform's native card format
7. Deploy to Vercel → configure SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, TELEGRAM_BOT_TOKEN, REDIS_URL
8. Add more platforms: npm install @chat-adapter/discord @chat-adapter/teams @chat-adapter/telegram
   → add to adapters map → one webhook route per platform
```

### 3. Build a Durable AI Agent
```
1. vercel link → enable AI Gateway → vercel env pull (OIDC credentials required)
2. Next.js (API Route) → Workflow DevKit (DurableAgent) → AI SDK (tool calling)
                       → AI Gateway (OIDC auth for model strings in workflow steps)
                       → Neon Postgres (state) → Vercel Functions (step execution)
3. For human-in-the-loop: defineHook() + getWritable() token emission + resumeHook() route
4. For AI text in workflow events: use <MessageResponse> from AI Elements (not raw text)
```

### 4. Full-Stack SaaS App
```
Next.js (App Router) → Neon Postgres (data) → Clerk (auth, via Marketplace)
                     → Stripe (payments, via Marketplace) → Vercel Blob (uploads)
                     → Edge Config (feature flags) → Vercel Analytics
```

**Starter kit**: Use `npx next-forge@latest init` to scaffold a production-ready SaaS monorepo with all of the above pre-wired (plus email, observability, security, AI, i18n, and more). ⤳ skill: next-forge

**Clerk integration gotchas**:
- `vercel integration add clerk` requires terms acceptance in the terminal (AI agents are blocked — user must run it manually)
- After CLI install, the user must complete setup in the Vercel Dashboard to connect Clerk to the project
- Clerk auto-provisions `CLERK_SECRET_KEY` and `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, but you must manually set `NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in` and `NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up`
- **Organization flow**: After sign-in, if the user has no organization, `auth()` returns `{ userId, orgSlug: null }`. Handle this explicitly — redirect to an org creation page or show `<CreateOrganization />`. Without this, the app will loop back to the landing page endlessly.
- The `proxy.ts` (or `middleware.ts`) must call `clerkMiddleware()` for `auth()` to work in Server Components. If proxy is in the wrong location, you get: `Clerk: auth() was called without Clerk middleware`

### 5. Monorepo with Multiple Apps
```
Turborepo (orchestration) → Next.js App A → Vercel Platform (deploy)
                          → Next.js App B → Vercel Platform (deploy)
                          → Shared packages → Turbopack (bundling)
                          → Remote Cache → Vercel (shared across CI)
```

### 6. Deploy with Custom CI
```
Git Push → CI Pipeline → vercel build → vercel deploy --prebuilt
        → VERCEL_TOKEN auth → Preview URL → vercel promote (production)
```

---

## 12. Migration Awareness

| Deprecated | Replacement | Migration Path |
|-----------|-------------|----------------|
| `@vercel/postgres` | `@neondatabase/serverless` | Use `@neondatabase/vercel-postgres-compat` for drop-in |
| `@vercel/kv` | `@upstash/redis` | Same billing, direct replacement |
| `middleware.ts` (Next.js 16) | `proxy.ts` | Rename file, Node.js runtime only |
| `experimental.turbopack` | `turbopack` (top-level) | Move config in next.config |
| Sync Request APIs (Next.js 16) | Async Request APIs | `await cookies()`, `await headers()`, etc. |
| PPR (Next.js 15 canary) | Cache Components | Follow Vercel migration guide |
| AI SDK 5 | AI SDK 6 | Run `npx @ai-sdk/codemod v6` |
| `generateObject` / `streamObject` | `generateText` / `streamText` + `Output.object()` | Unified structured output API |
| `parameters` (AI SDK tools) | `inputSchema` | Aligned with MCP spec |
| `result` (AI SDK tools) | `output` | Aligned with MCP spec |
| `maxSteps` (AI SDK) | `stopWhen: stepCountIs(N)` | Import `stepCountIs` from `ai` |
| `CoreMessage` | `ModelMessage` | Use `convertToModelMessages()` |
| `Experimental_Agent` | `ToolLoopAgent` | `system` → `instructions` |
| `useChat({ api })` | `useChat({ transport: new DefaultChatTransport({ api }) })` | v6 transport pattern |
| `handleSubmit` / `input` | `sendMessage({ text })` / own state | v6 chat hook API |
| `toDataStreamResponse()` | `toUIMessageStreamResponse()` | For chat UIs with useChat |
| `message.content` | `message.parts` iteration | UIMessage format (text, tool-*, reasoning) |
| Manual API keys (`ANTHROPIC_API_KEY`) | OIDC via `vercel env pull` | Auto-provisioned, no secrets to manage |
| `agent.generateText()` | `agent.generate()` | Simplified Agent API |
| `agent.streamText()` | `agent.stream()` | Simplified Agent API |
| `isLoading` (useChat) | `status === "streaming" \|\| status === "submitted"` | v6 status enum |
| `onResponse()` callback | Transport configuration | Removed in v6 |
| `body` option (useChat) | Pass data through transport | v6 transport pattern |
| DALL-E 2/3 | `model: 'google/gemini-3.1-flash-image-preview'` | Better quality, faster, cheaper |
| `gemini-2.0-flash-exp-image-generation` | `gemini-3.1-flash-image-preview` | Dramatically better quality |
| `gpt-4o` | `gpt-5.4` | Better, cheaper, faster |
| `experimental_createWorkflow` | `createWorkflow()` (stable) | WDK API stabilized |
| `"pipeline"` (turbo.json) | `"tasks"` | Turborepo v2 rename |
| `next/head` | `metadata` / `generateMetadata()` | App Router pattern (Pages Router only) |
| `next export` | `output: "export"` in next.config | CLI command removed |
| `cacheHandler` (singular) | `cacheHandlers` (plural) | Next.js 16 config rename |

---

## Conventions

### UI Design Defaults

- For application UI, default to **shadcn/ui + Geist**. Do not build core controls from raw HTML plus ad-hoc Tailwind when design-system primitives exist.
- Default to **dark mode** for dashboards, AI products, internal tools, and developer surfaces. Use light mode when the product is clearly content-first or editorial.
- Favor **zinc/neutral/slate tokens**, one accent color, and clear borders over scattered rainbow accents, heavy gradients, and random glassmorphism.
- Let **type, spacing, and composition** create hierarchy: Tabs + Card + Form for settings, Card + Table + Filters for dashboards, Sheet for mobile navigation, AlertDialog for destructive confirmation.
- Use **Geist Sans** for interface text and **Geist Mono** for code, metrics, IDs, timestamps, and commands.
- Avoid generic UI output: raw buttons, clickable divs, repeated bordered card grids, inconsistent radii, and forgotten empty/loading/error states.

### Next.js 16

- Default to Server Components. Only add `'use client'` when you need interactivity or browser APIs.
- Push `'use client'` boundaries as far down the component tree as possible.
- Use Server Actions (`'use server'`) for data mutations, not Route Handlers (unless building a public API).
- All request APIs are async in Next.js 16: `await cookies()`, `await headers()`, `await params`, `await searchParams`.
- Use `proxy.ts` instead of `middleware.ts` (Next.js 16 rename). Proxy runs on Node.js runtime only. **Location**: place `proxy.ts` at the same level as `app/` — at project root normally, or inside `src/` if using `--src-dir`.
- Turbopack config is top-level in `next.config.ts`, not under `experimental.turbopack`.
- Use Cache Components (`'use cache'`) instead of PPR for mixing static and dynamic content.
- Prefer `next/image` for images and `next/font` for fonts — both optimize automatically on Vercel.
- `@vercel/postgres` and `@vercel/kv` are sunset — use `@neondatabase/serverless` and `@upstash/redis`.

### AI SDK v6

- **Default to AI Gateway** — pass `"provider/model"` strings directly (e.g., `model: 'anthropic/claude-sonnet-4.6'`) — they route through the AI Gateway automatically. The `gateway()` wrapper from `'ai'` is optional and only needed when using `providerOptions.gateway` for routing/failover/tags. Do NOT install or import direct provider SDKs (`@ai-sdk/anthropic`, `@ai-sdk/openai`, etc.) unless you need provider-specific features not exposed through the gateway.
- **Install `@ai-sdk/react` for React hooks** — `useChat`, `useCompletion`, and `useObject` live in `@ai-sdk/react` (not `ai`). Always `npm install ai @ai-sdk/react` together for React/Next.js projects.
- **OIDC is the default auth for AI Gateway** — when you run `vercel env pull`, it provisions `VERCEL_OIDC_TOKEN` which the `@ai-sdk/gateway` package reads automatically via `@vercel/oidc`. No `AI_GATEWAY_API_KEY` or provider-specific API keys needed. On Vercel deployments, OIDC tokens are auto-refreshed. For local dev, re-run `vercel env pull` if the token expires (~24h).
- **For AI projects, set up a Vercel project first** — run `vercel link` (or create via dashboard) → enable AI Gateway in dashboard → `vercel env pull` to get OIDC credentials locally. Do NOT manually create `.env.local` with provider-specific API keys like `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`.
- **AI Elements is MANDATORY for all AI-generated text** — `npx ai-elements@latest` must be installed immediately after scaffolding. Never render AI text as raw `{text}` or `<p>{content}</p>` — it shows ugly `**`, `##`, `---`. Use `<Message>` for chat with `useChat`, and `<MessageResponse>` (from `@/components/ai-elements/message`) for any other AI markdown (workflow events, reports, briefings, notifications, email previews). `<MessageResponse>` wraps Streamdown with code highlighting, math, mermaid, and CJK plugins.
- **Server-side: use `convertToModelMessages()` (async) + `toUIMessageStreamResponse()`** — not `toDataStreamResponse()`. Client-side: use `DefaultChatTransport` with `useChat`, not the v5 `api` parameter.
- Use `inputSchema` (not `parameters`) and `output`/`outputSchema` (not `result`) for tool definitions — aligned with MCP spec.
- Always stream for user-facing AI: use `streamText` + `useChat`, not `generateText`.
- `generateObject` and `streamObject` are removed in v6 — use `generateText` / `streamText` with `Output.object()` instead.
- **`maxSteps` was removed** — use `stopWhen: stepCountIs(N)` (import `stepCountIs` from `ai`) for multi-step tool calling in both `streamText` and the `Agent` class.
- Use the `Agent` class for multi-step reasoning instead of manual tool-calling loops. Agent methods are `agent.generate()` and `agent.stream()` (not `agent.generateText()` / `agent.streamText()`).
- Use `DurableAgent` from `@workflow/ai/agent` for production agents that must survive crashes.
- **Image generation is gateway-native** — use `model: 'google/gemini-3.1-flash-image-preview'` with `generateText()` for best results (images in `result.files`). Use `experimental_generateImage` only for image-only models (Imagen 4.0, Flux 2). Do NOT use DALL-E or older Gemini 2.x image models — they are outdated.
- **Outdated models**: `gpt-4o` → use `gpt-5.4`; `gemini-2.0-flash-exp-image-generation` → use `gemini-3.1-flash-image-preview`; DALL-E 2/3 → use Gemini 3.1 Flash Image Preview.
- Use `@ai-sdk/mcp` (stable, not experimental) for MCP server connections.
- Use `mcp-to-ai-sdk` CLI to generate static tool definitions from MCP servers for security.
- Use AI SDK DevTools (`npx @ai-sdk/devtools`) during development for debugging.

### Vercel Platform

- Never hardcode secrets — use environment variables via `vercel env` or Marketplace auto-provisioning.
- Add `.env*.local` to `.gitignore` — these files contain pulled secrets.
- Use Fluid Compute for long-running functions — extends max duration to 800s on paid plans.
- Use `waitUntil` (or `after` in Next.js) for background work after sending a response.
- Configure cron jobs in `vercel.json` and verify with `CRON_SECRET` header.
- Use `vercel deploy --prebuilt` in CI for fastest deploys (separate build from deploy).
- For monorepos, use Turborepo with remote caching and `--affected` for efficient CI.
