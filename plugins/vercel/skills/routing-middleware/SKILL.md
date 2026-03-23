---
name: routing-middleware
description: Vercel Routing Middleware guidance — request interception before cache, rewrites, redirects, personalization. Works with any framework. Supports Edge, Node.js, and Bun runtimes. Use when intercepting requests at the platform level.
metadata:
  priority: 6
  docs:
    - "https://nextjs.org/docs/app/building-your-application/routing/middleware"
    - "https://vercel.com/docs/routing-middleware"
  sitemap: "https://nextjs.org/sitemap.xml"
  pathPatterns: 
    - 'middleware.ts'
    - 'middleware.js'
    - 'middleware.mts'
    - 'middleware.mjs'
    - 'proxy.ts'
    - 'proxy.js'
    - 'proxy.mts'
    - 'proxy.mjs'
    - 'src/middleware.ts'
    - 'src/middleware.js'
    - 'src/middleware.mts'
    - 'src/middleware.mjs'
    - 'src/proxy.ts'
    - 'src/proxy.js'
    - 'src/proxy.mts'
    - 'src/proxy.mjs'
    - 'vercel.json'
    - 'apps/*/vercel.json'
    - 'vercel.ts'
    - 'vercel.mts'
  bashPatterns:
    - '\bnpx\s+@vercel/config\b'
validate:
  -
    pattern: 'const\s+(blockedIps|denylist|allowlist)\s*=\s*\[|from\s+[''"](rate-limiter-flexible)[''"]|rateLimit'
    message: 'App-layer rate limiting or IP blocking in middleware. Use Vercel Firewall/WAF for platform-level protection.'
    severity: recommended
    upgradeToSkill: vercel-firewall
    upgradeWhy: 'Move IP blocking and rate limiting from middleware code to Vercel Firewall/WAF for better performance and maintainability.'
    skipIfFileContains: '@vercel/firewall|vercel\.json.*firewall'
  -
    pattern: 'NextResponse.*from\s+[''"]next/server[''"]|from\s+[''"]next/server[''"].*NextResponse'
    message: 'Next.js middleware.ts is renamed to proxy.ts in Next.js 16 — rename the file and use the Node.js runtime. Run Skill(nextjs) for proxy.ts migration guidance.'
    severity: recommended
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from middleware.ts to proxy.ts with correct file placement, Node.js runtime, and Next.js 16 patterns.'
    skipIfFileContains: 'proxy\.ts|runtime.*nodejs'
retrieval:
  aliases:
    - request interceptor
    - middleware
    - rewrite rules
    - redirect rules
  intents:
    - intercept requests
    - add middleware
    - configure rewrites
    - set up redirects
  entities:
    - middleware
    - rewrite
    - redirect
    - personalization
    - Edge
chainTo:
  -
    pattern: 'const\s+(blockedIps|denylist|allowlist)\s*=\s*\[|from\s+[''\"](rate-limiter-flexible)[''"]|rateLimit'
    targetSkill: vercel-firewall
    message: 'App-layer rate limiting or IP blocking in middleware — loading Vercel Firewall guidance for platform-level protection.'
  -
    pattern: 'from\s+[''""]next-auth[''""]'
    targetSkill: auth
    message: 'Auth logic in middleware — loading Auth guidance for Clerk/Auth0 integration patterns.'
  -
    pattern: 'NextResponse.*from\s+[''"]next/server[''"]|from\s+[''"]next/server[''"].*NextResponse'
    targetSkill: nextjs
    message: 'middleware.ts with next/server imports detected — loading Next.js guidance for proxy.ts migration (Next.js 16 renames middleware.ts to proxy.ts with Node.js runtime).'
    skipIfFileContains: 'proxy\.ts|runtime.*nodejs'
  -
    pattern: 'from\s+[''""](cookie|cookies-next)[''""]|req\.cookies\.get\s*\(|NextResponse\.next\(\s*\{.*headers'
    targetSkill: vercel-flags
    message: 'Cookie-based routing in middleware — loading Vercel Flags guidance for managed feature flags with Edge Config storage.'
    skipIfFileContains: '@vercel/flags|@vercel/edge-config'
  -
    pattern: 'from\s+[''""](jsonwebtoken)[''""]|jwt\.(verify|decode)\('
    targetSkill: auth
    message: 'Manual JWT verification in middleware — loading Auth guidance for managed auth middleware patterns (Clerk, Descope).'
    skipIfFileContains: 'clerkMiddleware|@clerk/|@auth0/'

---

# Vercel Routing Middleware

You are an expert in Vercel Routing Middleware — the platform-level request interception layer.

## What It Is

Routing Middleware runs **before the cache** on every request matching its config. It is a **Vercel platform** feature (not framework-specific) that works with Next.js, SvelteKit, Astro, Nuxt, or any deployed framework. Built on Fluid Compute.

- **File**: `middleware.ts` or `middleware.js` at the project root
- **Default export required** (function name can be anything)
- **Runtimes**: Edge (default), Node.js (`runtime: 'nodejs'`), Bun (Node.js + `bunVersion` in vercel.json)

## CRITICAL: Middleware Disambiguation

There are THREE "middleware" concepts in the Vercel ecosystem:

| Concept | File | Runtime | Scope | When to Use |
|---------|------|---------|-------|-------------|
| **Vercel Routing Middleware** | `middleware.ts` (root) | Edge/Node/Bun | Any framework, platform-level | Request interception before cache: rewrites, redirects, geo, A/B |
| **Next.js 16 Proxy** | `proxy.ts` (root, or `src/proxy.ts` if using `--src-dir`) | Node.js only | Next.js 16+ only | Network-boundary proxy needing full Node APIs. NOT for auth. |
| **Edge Functions** | Any function file | V8 isolates | General-purpose | Standalone edge compute endpoints, not an interception layer |

**Why the rename in Next.js 16**: `middleware.ts` → `proxy.ts` clarifies it sits at the network boundary (not general-purpose middleware). Partly motivated by CVE-2025-29927 (middleware auth bypass via `x-middleware-subrequest` header). The exported function must also be renamed from `middleware` to `proxy`. Migration codemod: `npx @next/codemod@latest middleware-to-proxy`

**Deprecation**: Next.js 16 still accepts `middleware.ts` but treats it as deprecated and logs a warning. It will be removed in a future version.

## Bun Runtime

To run Routing Middleware (and all Vercel Functions) on Bun, add `bunVersion` to `vercel.json`:

```json
{
  "bunVersion": "1.x"
}
```

Set the middleware runtime to `nodejs` — Bun replaces the Node.js runtime transparently:

```ts
export const config = {
  runtime: 'nodejs', // Bun swaps in when bunVersion is set
};
```

Bun reduces average latency by ~28% in CPU-bound workloads. Currently in Public Beta — supports Next.js, Express, Hono, and Nitro.

## Basic Example

```ts
// middleware.ts (project root)
import { geolocation, rewrite } from '@vercel/functions';

export default function middleware(request: Request) {
  const { country } = geolocation(request);
  const url = new URL(request.url);
  url.pathname = country === 'US' ? '/us' + url.pathname : '/intl' + url.pathname;
  return rewrite(url);
}

export const config = {
  runtime: 'edge', // 'edge' (default) | 'nodejs'
};
```

## Helper Methods (`@vercel/functions`)

For non-Next.js frameworks, import from `@vercel/functions`:

| Helper | Purpose |
|--------|---------|
| `next()` | Continue middleware chain (optionally modify headers) |
| `rewrite(url)` | Transparently serve content from a different URL |
| `geolocation(request)` | Get `city`, `country`, `latitude`, `longitude`, `region` |
| `ipAddress(request)` | Get client IP address |
| `waitUntil(promise)` | Keep function running after response is sent |

For Next.js, equivalent helpers are on `NextResponse` (`next()`, `rewrite()`, `redirect()`) and `NextRequest` (`request.geo`, `request.ip`).

## Matcher Configuration

Middleware runs on **every route** by default. Use `config.matcher` to scope it:

```ts
// Single path
export const config = { matcher: '/dashboard/:path*' };

// Multiple paths
export const config = { matcher: ['/dashboard/:path*', '/api/:path*'] };

// Regex: exclude static files
export const config = {
  matcher: ['/((?!_next/static|favicon.ico).*)'],
};
```

**Tip**: Using `matcher` is preferred — unmatched paths skip middleware invocation entirely (saves compute).

## Common Patterns

### IP-Based Header Injection

```ts
import { ipAddress, next } from '@vercel/functions';

export default function middleware(request: Request) {
  return next({ headers: { 'x-real-ip': ipAddress(request) || 'unknown' } });
}
```

### A/B Testing via Edge Config

```ts
import { get } from '@vercel/edge-config';
import { rewrite } from '@vercel/functions';

export default async function middleware(request: Request) {
  const variant = await get('experiment-homepage'); // <1ms read
  const url = new URL(request.url);
  url.pathname = variant === 'B' ? '/home-b' : '/home-a';
  return rewrite(url);
}
```

### Background Processing

```ts
import type { RequestContext } from '@vercel/functions';

export default function middleware(request: Request, context: RequestContext) {
  context.waitUntil(
    fetch('https://analytics.example.com/log', { method: 'POST', body: request.url })
  );
  return new Response('OK');
}
```

## Request Limits

| Limit | Value |
|-------|-------|
| Max URL length | 14 KB |
| Max request body | 4 MB |
| Max request headers | 64 headers / 16 KB total |

## Three CDN Routing Mechanisms

Vercel's CDN supports three routing mechanisms, evaluated in this order:

| Order | Mechanism | Scope | Deploy Required | How to Configure |
|-------|-----------|-------|-----------------|------------------|
| 1 | **Bulk Redirects** | Up to 1M static path→path redirects | No (runtime via Dashboard/API/CLI) | Dashboard, CSV upload, REST API |
| 2 | **Project-Level Routes** | Headers, rewrites, redirects | No (instant publish) | Dashboard, API, CLI, Vercel SDK |
| 3 | **Deployment Config Routes** | Full routing rules | Yes (deploy) | `vercel.json`, `vercel.ts`, `next.config.ts` |

**Project-level routes** (added March 2026) let you update routing rules — response headers, rewrites to external APIs — without triggering a new deployment. They run after bulk redirects and before deployment config routes. Available on all plans.

### Project-Level Routes — Configuration Methods

Project-level routes take effect instantly (no deploy required). Four ways to manage them:

| Method | How |
|--------|-----|
| **Dashboard** | Project → CDN → Routing tab. Live map of global traffic, cache management, and route editor in one view. |
| **REST API** | `GET/POST/PATCH/DELETE /v1/projects/{projectId}/routes` — 8 dedicated endpoints for CRUD on project routes. |
| **Vercel CLI** | Managed via `vercel.ts` / `@vercel/config` commands (`compile`, `validate`, `generate`). |
| **Vercel SDK** | `@vercel/config` helpers: `routes.redirect()`, `routes.rewrite()`, `routes.header()`, plus `has`/`missing` conditions and transforms. |

Use project-level routes for operational changes (CORS headers, API proxy rewrites, A/B redirects) that shouldn't require a full redeploy.

## Programmatic Configuration with `vercel.ts`

Instead of static `vercel.json`, you can use `vercel.ts` (or `.js`, `.mjs`, `.cjs`, `.mts`) with the `@vercel/config` package for type-safe, dynamic routing configuration:

```ts
// vercel.ts
import { defineConfig } from '@vercel/config';

export default defineConfig({
  rewrites: [
    { source: '/api/:path*', destination: 'https://backend.example.com/:path*' },
  ],
  headers: [
    { source: '/(.*)', headers: [{ key: 'X-Frame-Options', value: 'DENY' }] },
  ],
});
```

CLI commands:
- `npx @vercel/config compile` — compile to JSON (stdout)
- `npx @vercel/config validate` — validate and show summary
- `npx @vercel/config generate` — generate `vercel.json` locally for development

**Constraint**: Only one config file per project — `vercel.json` or `vercel.ts`, not both.

## When to Use

- Geo-personalization of static pages (runs before cache)
- A/B testing rewrites with Edge Config
- Custom redirects based on request properties
- Header injection (CSP, CORS, custom headers)
- Lightweight auth checks (defense-in-depth only — not sole auth layer)
- Project-level routes for headers/rewrites without redeploying

## When NOT to Use

- Need full Node.js APIs in Next.js → use `proxy.ts`
- General compute at the edge → use Edge Functions
- Heavy business logic or database queries → use server-side framework features
- Auth as sole protection → use Layouts, Server Components, or Route Handlers
- Thousands of static redirects → use Bulk Redirects (up to 1M per project)

## References

- 📖 docs: https://vercel.com/docs/routing-middleware
- 📖 API reference: https://vercel.com/docs/routing-middleware/api
- 📖 getting started: https://vercel.com/docs/routing-middleware/getting-started
