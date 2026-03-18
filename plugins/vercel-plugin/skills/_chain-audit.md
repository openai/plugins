# Chain Audit — `chainTo` + `validate` Rule Coverage

> Generated 2026-03-11 · Iteration 9 of autoloop implementation

This audit catalogues every skill's chain targets, validate rules, and the Bash install detection hook. All 46 skills now have at least one `chainTo` rule, plus comprehensive `validate` rules on high-traffic skills.

---

## Legend

| Column | Meaning |
|--------|---------|
| **Skill** | Skill slug |
| **Priority** | Injection priority (higher = injected first) |
| **chainTo targets** | `chainTo[].targetSkill` values |
| **Rule count** | Number of `chainTo` rules |

---

## A. Skills with ZERO `chainTo` rules (0 skills)

All skills now have chainTo rules. This section is empty.

---

## B. All skills — chainTo coverage

| # | Skill | Priority | chainTo targets | Rule count |
|---|-------|----------|----------------|------------|
| 1 | **agent-browser** | 3 | agent-browser-verify, nextjs | 2 |
| 2 | **agent-browser-verify** | 2 | investigation-mode, agent-browser | 2 |
| 3 | **ai-elements** | 6 | ai-sdk (×2), ai-elements | 3 |
| 4 | **ai-gateway** | 7 | ai-sdk (×3), observability, ai-sdk (gpt-4o), ai-sdk (DALL-E), ai-sdk (gemini-2.x) | 6 |
| 5 | **ai-generation-persistence** | 6 | ai-gateway, vercel-storage | 2 |
| 6 | **ai-sdk** | 8 | ai-gateway, ai-elements (×5), json-render, observability, workflow, ai-gateway | 10 |
| 7 | **auth** | 6 | sign-in-with-vercel, routing-middleware, auth (×2) | 4 |
| 8 | **bootstrap** | 5 | vercel-storage, auth, env-vars | 3 |
| 9 | **chat-sdk** | 5 | ai-sdk, chat-sdk (×2), workflow, ai-gateway | 5 |
| 10 | **cms** | 4 | nextjs, runtime-cache | 2 |
| 11 | **cron-jobs** | 5 | vercel-functions, workflow, cron-jobs | 3 |
| 12 | **deployments-cicd** | 5 | cron-jobs | 1 |
| 13 | **email** | 5 | email, workflow (×3) | 4 |
| 14 | **env-vars** | 6 | ai-gateway | 1 |
| 15 | **geist** | 4 | nextjs, shadcn | 2 |
| 16 | **geistdocs** | 4 | nextjs | 1 |
| 17 | **investigation-mode** | 8 | workflow, deployments-cicd, observability | 3 |
| 18 | **json-render** | 5 | ai-sdk, ai-elements | 2 |
| 19 | **marketplace** | 3 | vercel-storage, auth, cms | 3 |
| 20 | **micro** | 4 | vercel-functions | 1 |
| 21 | **ncc** | 4 | vercel-functions, deployments-cicd | 2 |
| 22 | **next-forge** | 6 | routing-middleware, auth, payments, email | 4 |
| 23 | **nextjs** | 7 | routing-middleware, vercel-storage, ai-gateway (×2), auth (×2), vercel-functions, runtime-cache, shadcn (×2), nextjs (getInitialProps) | 11 |
| 24 | **observability** | 6 | investigation-mode, vercel-functions | 2 |
| 25 | **payments** | 5 | workflow (×2), payments | 3 |
| 26 | **react-best-practices** | 3 | swr (×2), shadcn | 3 |
| 27 | **routing-middleware** | 6 | vercel-firewall, auth (×2), nextjs, vercel-flags | 5 |
| 28 | **runtime-cache** | 5 | vercel-storage (×2) | 2 |
| 29 | **satori** | 4 | vercel-functions (×2) | 2 |
| 30 | **shadcn** | 6 | ai-elements (×2) | 2 |
| 31 | **sign-in-with-vercel** | 6 | auth, env-vars | 2 |
| 32 | **swr** | 4 | ai-sdk, vercel-storage, swr (×2) | 4 |
| 33 | **turbopack** | 4 | nextjs (×2) | 2 |
| 34 | **turborepo** | 5 | vercel-storage | 1 |
| 35 | **v0-dev** | 5 | shadcn, ai-sdk, nextjs | 3 |
| 36 | **vercel-agent** | 4 | deployments-cicd, vercel-api | 2 |
| 37 | **vercel-api** | 7 | deployments-cicd, ai-sdk | 2 |
| 38 | **vercel-cli** | 4 | cron-jobs, vercel-functions, routing-middleware | 3 |
| 39 | **vercel-firewall** | 6 | routing-middleware (×2) | 2 |
| 40 | **vercel-flags** | 5 | vercel-storage, vercel-flags | 2 |
| 41 | **vercel-functions** | 6 | ai-sdk (×2), workflow (×2), vercel-storage (×2), vercel-functions (Express) | 7 |
| 42 | **vercel-queues** | 5 | workflow (×2), vercel-queues | 3 |
| 43 | **vercel-sandbox** | 4 | vercel-sandbox, ai-sdk | 2 |
| 44 | **vercel-storage** | 5 | nextjs (×2), vercel-storage (×4) | 6 |
| 45 | **verification** | 7 | env-vars, routing-middleware, ai-sdk | 3 |
| 46 | **workflow** | 6 | ai-sdk, ai-elements, ai-gateway, vercel-functions | 4 |

---

## C. Validate rules with `upgradeToSkill`

These validate rules detect antipatterns in written files and suggest loading a different skill.

| # | Skill | Validate rules | Rules with upgradeToSkill | Key upgrade targets |
|---|-------|---------------|--------------------------|---------------------|
| 1 | **ai-sdk** | 12 | 10 | ai-gateway (×3), ai-sdk (×6), ai-gateway (×1) |
| 2 | **ai-gateway** | 7 | 1 | (OIDC recommendation) |
| 3 | **nextjs** | 19 | 14 | nextjs (×5), routing-middleware (×2), auth (×1), vercel-functions (×1), runtime-cache (×1), vercel-storage (×2), nextjs (×2) |
| 4 | **vercel-functions** | 9 | 8 | ai-sdk (×1), workflow (×2), vercel-storage (×1), observability (×1), runtime-cache (×1), workflow (×1), vercel-functions (Express) |
| 5 | **vercel-storage** | 2 | 2 | vercel-storage (×2) |
| 6 | **turborepo** | 1 | 1 | turborepo |
| 7 | **routing-middleware** | 2 | — | — |
| 8 | **shadcn** | 1 | — | — |

---

## D. Summary statistics

| Metric | Count |
|--------|-------|
| Total skills audited | 46 |
| Skills with 0 chainTo rules | **0** |
| Skills with chainTo rules | **46** |
| Total chainTo rules | **~143** |
| Average rules per skill | ~3.1 |
| Max rules (ai-sdk, nextjs) | 10-11 |
| Min rules (deployments-cicd, env-vars, geistdocs, micro, turborepo) | 1 |
| Skills with validate rules | **~8** |
| Total validate rules | **~53** |
| Validate rules with upgradeToSkill | **~36** |

---

## E. High-impact chains (top 10 by expected frequency)

| Rank | Source Skill | → Target | Trigger Pattern | Why high-impact |
|------|-------------|----------|----------------|-----------------|
| 1 | **nextjs** | `shadcn` | `@/components/ui` imports | Nearly every Next.js app uses shadcn/ui |
| 2 | **ai-sdk** | `ai-elements` | `handleSubmit`, `useChat({ api })`, `toDataStreamResponse`, `generateObject`, `maxSteps` | v5→v6 migration catches 5 deprecated patterns |
| 3 | **ai-gateway** | `ai-sdk` | `gpt-4o`, `dall-e`, `gemini-2.x`, provider API keys, direct SDKs | Model deprecation + API key detection |
| 4 | **v0-dev** | `shadcn` | v0 component output | v0 always generates shadcn components |
| 5 | **ai-sdk** | `workflow` | `DurableAgent` / `'use workflow'` | AI agents increasingly use WDK |
| 6 | **marketplace** | `vercel-storage` | `vercel integration add.*neon` | Most common marketplace install |
| 7 | **vercel-functions** | `ai-sdk` | `from 'openai'`, `generateObject`, `toDataStreamResponse` | Direct SDK + v5 API detection in route handlers |
| 8 | **nextjs** | `auth` | `next-auth`, `getServerSession`, JWT handling | Legacy auth detection |
| 9 | **vercel-cli** | `routing-middleware` | `vercel.json` redirects/rewrites | Very frequent config pattern |
| 10 | **nextjs** | `ai-gateway` | `@ai-sdk/(openai|anthropic)`, raw AI fetch URLs | Direct provider SDK bypass |

---

## F. PostToolUse Bash Chain Hook

A dedicated `posttooluse-bash-chain.mts` hook matches the `Bash` tool and detects package installation commands (`npm install`, `yarn add`, `pnpm add`, `bun add`). This catches antipatterns at install time rather than after code is written.

### Package → Skill Map (30 entries)

| Package | Target Skill | Message |
|---------|-------------|---------|
| `express` | vercel-functions | Express → Vercel Functions Web API |
| `fastify` | vercel-functions | Fastify → Vercel Functions |
| `koa` | vercel-functions | Koa → Vercel Functions |
| `bullmq` | vercel-queues | BullMQ → Vercel Queues |
| `bull` | vercel-queues | Bull → Vercel Queues |
| `mongoose` | vercel-storage | Mongoose → Marketplace Neon/Upstash |
| `prisma` | vercel-storage | Prisma → Neon Postgres (recommended) |
| `@libsql/client` | vercel-storage | libSQL → Marketplace alternatives |
| `@vercel/postgres` | vercel-storage | Sunset package → Neon migration |
| `@vercel/kv` | vercel-storage | Sunset package → Upstash migration |
| `openai` | ai-gateway | Direct OpenAI SDK → AI Gateway |
| `@anthropic-ai/sdk` | ai-gateway | Direct Anthropic SDK → AI Gateway |
| `@google/generative-ai` | ai-gateway | Direct Google AI → AI Gateway |
| `langchain` | ai-sdk | LangChain → AI SDK v6 |
| `@langchain/core` | ai-sdk | LangChain Core → AI SDK v6 |
| `next-auth` | auth | next-auth → managed auth (Clerk) |
| `@clerk/nextjs` | auth | Clerk Next.js integration guidance |
| `@sanity/client` | cms | Sanity → Marketplace integration |
| `contentful` | cms | Contentful → CMS integration |
| `resend` | email | Resend → Marketplace email integration |
| `@slack/bolt` | chat-sdk | Slack Bolt → Chat SDK |
| `@slack/web-api` | chat-sdk | Slack Web API → Chat SDK |
| `discord.js` | chat-sdk | Discord.js → Chat SDK |
| `telegraf` | chat-sdk | Telegraf → Chat SDK |
| `grammy` | chat-sdk | Grammy → Chat SDK |
| `stripe` | payments | Stripe → Marketplace integration |
| `helmet` | vercel-firewall | Helmet → Vercel Firewall |
| `cors` | routing-middleware | cors → Routing Middleware |
| `dotenv` | env-vars | dotenv → Vercel env management |
| `workflow` | workflow | Workflow DevKit guidance |
| `ai` | ai-sdk | AI SDK guidance |
| `@ai-sdk/react` | ai-sdk | AI SDK React hooks guidance |
| `@vercel/flags` | vercel-flags | Feature flags guidance |
| `swr` | swr | SWR data-fetching guidance |
| `node-cron` | cron-jobs | node-cron → Vercel Cron Jobs |
| `cron` | cron-jobs | cron → Vercel Cron Jobs |

### Hook Properties

- **Matcher**: `Bash` (PostToolUse)
- **Budget**: 18KB
- **Cap**: 2 skills per invocation (configurable via `VERCEL_PLUGIN_CHAIN_CAP`)
- **Dedup**: Respects `VERCEL_PLUGIN_SEEN_SKILLS` contract
- **Parse logic**: Extracts package names from `npm i|install`, `yarn add`, `pnpm add`, `bun add`; strips version specifiers and flags

---

## G. Conflict registry

Only 2 soft conflicts found — both are non-blocking because they originate from different source skills and trigger on different patterns.

| Pattern area | Skill A → Target | Skill B → Target | Resolution |
|-------------|-----------------|-----------------|------------|
| env-vars chain | vercel-cli → env-vars (removed) | env-vars → ai-gateway | No longer bidirectional |
| ai-sdk chain | ai-elements → ai-sdk | ai-generation-persistence → ai-gateway | Different trigger patterns (UI hooks vs persistence); no conflict |

---

## H. Test coverage

Test file: `tests/posttooluse-chain.test.ts` (~4200 lines)

### Test categories

| Category | Test count | Description |
|----------|-----------|-------------|
| Unit: `runChainInjection` | 12 | Core chain logic: match, dedup, cap, budget, invalid regex, loop prevention |
| Real-world: chainTo scenarios | ~70 | Every skill's chainTo rules exercised with realistic file content |
| Real-world: validate + upgradeToSkill | ~10 | AI SDK v6 migration, model deprecation, sunset packages |
| Real-world: skipIfFileContains | ~25 | False positive prevention for every major chain rule |
| Real-world: negative tests | 3 | Clean files that should NOT trigger chains |
| `formatOutput` with chains | 3 | Chain-only, mixed violations+chains, empty output |
| Integration (process spawn) | 3 | Full hook execution with temp files |
| Bash chain: `parseInstallCommand` | 12 | Package manager parsing, version stripping, flag filtering |
| Bash chain: `runBashChainInjection` | 9 | Package→skill mapping, dedup, cap, budget |
| Bash chain: `formatBashChainOutput` | 2 | Output formatting |
| Bash chain: `parseBashInput` | 5 | Input parsing |
| Chain cap enforcement | 3 | Default cap of 2, configurable cap, >2 matches |

---

## I. Implementation status

All phases are **complete**:

### Phase 1 — Quick wins (8 skills) — DONE
All formerly-zero skills now have chainTo rules: vercel-cli, marketplace, v0-dev, cms, ai-generation-persistence, investigation-mode, verification, sign-in-with-vercel.

### Phase 2 — Existing skill enrichment (10 skills) — DONE
Enriched: ai-sdk, next-forge, nextjs, routing-middleware, workflow, chat-sdk, bootstrap, shadcn, vercel-storage, auth.

### Phase 3 — Lower-traffic skills (8 skills) — DONE
Added chainTo rules to: observability, turbopack, geist, ncc, vercel-agent, vercel-api, agent-browser, agent-browser-verify.

### Phase 4 — High-leverage new rules — DONE
- AI SDK v5→v6 migration chains (5 new chainTo rules in ai-sdk)
- Model deprecation chains (3 new chainTo rules in ai-gateway: gpt-4o, DALL-E, gemini-2.x)
- Direct API key detection chain (1 new chainTo in ai-gateway)
- Express.js detection (chainTo + validate rule in vercel-functions)
- Pages Router comprehensive detection (getInitialProps chainTo in nextjs)
- Expanded sunset package patterns (createPool, sql template literal in vercel-storage)

### Phase 5 — PostToolUse Bash hook — DONE
New `posttooluse-bash-chain.mts` hook that matches `Bash` tool, parses install commands, maps 30 packages to skills, respects dedup/budget/cap.

**100% coverage achieved.** All 46 skills have at least one chainTo rule (~143 rules total). 30 npm packages mapped for install-time detection.
