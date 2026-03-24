---
name: nextjs
description: Next.js App Router expert guidance. Use when building, debugging, or architecting Next.js applications — routing, Server Components, Server Actions, Cache Components, layouts, middleware/proxy, data fetching, rendering strategies, and deployment on Vercel.
metadata:
  priority: 5
  docs:
    - "https://nextjs.org/docs"
    - "https://nextjs.org/docs/app"
  sitemap: "https://nextjs.org/sitemap.xml"
  pathPatterns:
    - 'next.config.*'
    - 'next-env.d.ts'
    - 'app/**'
    - 'pages/**'
    - 'src/app/**'
    - 'src/pages/**'
    - 'tailwind.config.*'
    - 'postcss.config.*'
    - 'tsconfig.json'
    - 'tsconfig.*.json'
    - 'apps/*/app/**'
    - 'apps/*/pages/**'
    - 'apps/*/src/app/**'
    - 'apps/*/src/pages/**'
    - 'apps/*/next.config.*'
  bashPatterns:
    - '\bnext\s+(dev|build|start|lint)\b'
    - '\bnext\s+experimental-analyze\b'
    - '\bnpx\s+create-next-app\b'
    - '\bbunx\s+create-next-app\b'
    - '\bnpm\s+run\s+(dev|build|start)\b'
    - '\bpnpm\s+(dev|build)\b'
    - '\bbun\s+run\s+(dev|build)\b'
  promptSignals:
    phrases:
      - "next.js"
      - "nextjs"
      - "app router"
      - "server component"
      - "server action"
    allOf:
      - [middleware, next]
      - [layout, route]
    anyOf:
      - "pages router"
      - "getserversideprops"
      - "use server"
    noneOf: []
    minScore: 6
validate:
  -
    pattern: export.*getServerSideProps
    message: 'getServerSideProps is removed in App Router — use server components or route handlers'
    severity: error
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from Pages Router getServerSideProps to App Router server components with async data fetching.'
  -
    pattern: getServerSideProps
    message: 'getServerSideProps is a Pages Router pattern — migrate to App Router server components'
    severity: warn
  -
    pattern: export.*getStaticProps
    message: 'getStaticProps is removed in App Router — use generateStaticParams + server components instead'
    severity: error
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from Pages Router getStaticProps to App Router generateStaticParams with server components.'
  -
    pattern: getStaticProps
    message: 'getStaticProps is a Pages Router pattern — migrate to App Router generateStaticParams + server components'
    severity: warn
  -
    pattern: from\s+['"]next/router['"]
    message: 'next/router is Pages Router only — use next/navigation for App Router'
    severity: error
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from next/router to next/navigation with useRouter, usePathname, useSearchParams hooks.'
  -
    pattern: (useState|useEffect)
    message: 'React hooks require "use client" directive — add it at the top of client components'
    severity: warn
    skipIfFileContains: "^['\"]use client['\"]"
  -
    pattern: from\s+['"]next/head['"]
    message: 'next/head is Pages Router — use export const metadata or generateMetadata() in App Router. Run Skill(nextjs) for metadata API guidance.'
    severity: error
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from next/head to the App Router metadata API (export const metadata / generateMetadata()).'
    skipIfFileContains: export\s+(const\s+)?metadata|generateMetadata
  -
    pattern: export\s+(default\s+)?function\s+middleware
    message: 'middleware() is renamed to proxy() in Next.js 16 — rename the function and the file to proxy.ts. Run Skill(routing-middleware) for proxy.ts migration guidance.'
    severity: recommended
    upgradeToSkill: routing-middleware
    upgradeWhy: 'Guides migration from middleware.ts to proxy.ts with correct file placement, runtime config, and request interception patterns.'
  -
    pattern: revalidateTag\(\s*['"][^'"]+['"]\s*\)
    message: 'Single-arg revalidateTag(tag) is deprecated in Next.js 16 — pass a cacheLife profile: revalidateTag(tag, "max")'
    severity: recommended
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from single-arg revalidateTag to the Next.js 16 two-arg API with cacheLife profiles.'
  -
    pattern: '\bcacheHandler\s*:'
    message: 'Singular cacheHandler is deprecated in Next.js 16 — use cacheHandlers (plural) with per-type handlers'
    severity: recommended
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from singular cacheHandler to Next.js 16 cacheHandlers (plural) with per-type handler config.'
  -
    pattern: useRef\(\s*\)
    message: 'useRef() requires an initial value in React 19 — use useRef(null) or useRef(0)'
    severity: error
  -
    pattern: next\s+export
    message: 'next export was removed — use output: "export" in next.config.js for static export'
    severity: error
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from next export CLI command to output: "export" in next.config for static site generation.'
  -
    pattern: (?<!await )\bcookies\(\s*\)
    message: 'cookies() is async in Next.js 16 — add await: const cookieStore = await cookies()'
    severity: error
    skipIfFileContains: "^['\"]use client['\"]"
  -
    pattern: (?<!await )\bheaders\(\s*\)
    message: 'headers() is async in Next.js 16 — add await: const headersList = await headers()'
    severity: error
    skipIfFileContains: "^['\"]use client['\"]"
  -
    pattern: =\s*(?!await\b)params\b
    message: 'params is async in Next.js 16 — add await: const { slug } = await params'
    severity: recommended
    skipIfFileContains: "^['\"]use client['\"]"
  -
    pattern: =\s*(?!await\b)searchParams\b
    message: 'searchParams is async in Next.js 16 — add await: const { query } = await searchParams'
    severity: recommended
    skipIfFileContains: "^['\"]use client['\"]"
  -
    pattern: 'from\s+[''""](next-auth|@auth/core)[''""]|NextAuth\(|getServerSession\('
    message: 'Legacy auth pattern detected. Modern Vercel apps should use Clerk, Descope, or Auth0 for managed authentication.'
    severity: recommended
    upgradeToSkill: auth
    upgradeWhy: 'Migrate from next-auth/manual JWT to a managed auth provider (Clerk, Descope, Auth0) for better Vercel integration.'
    skipIfFileContains: '@clerk/|@descope/|@auth0/'
  -
    pattern: 'NextApiRequest|NextApiResponse|export\s+default\s+function\s+handler'
    message: 'Pages Router API handler detected. Use App Router route handlers with named HTTP exports instead.'
    severity: recommended
    upgradeToSkill: vercel-functions
    upgradeWhy: 'Migrate from Pages Router API routes to App Router route handlers with Web Request/Response API.'
    skipIfFileContains: 'export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)'
  -
    pattern: 'from\s+[''""](lru-cache|node-cache|memory-cache)[''""]|new\s+(LRUCache|NodeCache)\('
    message: 'In-process cache detected. Serverless deployments lose process memory between invocations.'
    severity: recommended
    upgradeToSkill: runtime-cache
    upgradeWhy: 'Replace process-memory caches with Vercel Runtime Cache for shared, region-aware caching.'
  -
    pattern: 'from\s+[''""](express|fastify|koa|hapi)[''""]|require\s*\(\s*[''""](express|fastify|koa|hapi)[''""]'
    message: 'Express/Fastify/Koa/Hapi server framework detected in a Next.js project. Use Next.js route handlers or proxy.ts for request handling instead.'
    severity: recommended
    upgradeToSkill: routing-middleware
    upgradeWhy: 'Replace custom server frameworks with Next.js proxy.ts for request interception and route handlers for API endpoints.'
    skipIfFileContains: 'proxy\.ts|from\s+[''""](next/server)[''""]|@vercel/functions'
  -
    pattern: 'from\s+[''""](typeorm|sequelize|mikro-orm|objection|bookshelf|knex)[''""]|require\s*\(\s*[''""](typeorm|sequelize|mikro-orm|objection|bookshelf|knex)[''""]'
    message: 'Heavy ORM detected. Consider using lightweight serverless-native alternatives like Drizzle, Prisma, or direct Neon for better cold start performance.'
    severity: recommended
    upgradeToSkill: vercel-storage
    upgradeWhy: 'Migrate from heavy ORMs to serverless-native database clients (Drizzle + Neon, Prisma, or @neondatabase/serverless) for faster cold starts.'
    skipIfFileContains: 'from\s+[''""](drizzle-orm|@neondatabase|@prisma/client|prisma)[''""]'
  -
    pattern: 'fonts\.googleapis\.com|from\s+[''""](fontsource|@fontsource)[''""]|<link[^>]*fonts\.googleapis'
    message: 'External font loader detected. Use next/font for zero-CLS, self-hosted font loading with automatic optimization.'
    severity: recommended
    upgradeToSkill: nextjs
    upgradeWhy: 'Guides migration from external font loaders to next/font with Geist Sans/Mono for zero-CLS font optimization.'
    skipIfFileContains: 'next/font'
chainTo:
  -
    pattern: 'export\s+(default\s+)?function\s+middleware'
    targetSkill: routing-middleware
    message: 'middleware() is renamed to proxy() in Next.js 16 — loading Routing Middleware guidance for proxy.ts migration.'
  -
    pattern: "from\\s+['\"]@vercel/(postgres|kv)['\"]"
    targetSkill: vercel-storage
    message: 'Sunset storage package detected — loading Vercel Storage guidance for Neon/Upstash migration.'
  -
    pattern: "from\\s+['\"]@ai-sdk/(anthropic|openai)['\"]"
    targetSkill: ai-gateway
    message: 'Direct AI provider SDK import — loading AI Gateway guidance for unified model routing with failover and cost tracking.'
  -
    pattern: 'from\s+[''""](next-auth|@auth/core)[''""]|NextAuth\(|getServerSession\('
    targetSkill: auth
    message: 'Legacy auth pattern detected — loading managed authentication guidance (Clerk, Descope, Auth0).'
  -
    pattern: 'NextApiRequest|NextApiResponse|export\s+default\s+function\s+handler'
    targetSkill: vercel-functions
    message: 'Pages Router API handler detected — loading Vercel Functions guidance for App Router migration.'
  -
    pattern: 'from\s+[''""](lru-cache|node-cache|memory-cache)[''""]|new\s+(LRUCache|NodeCache)\('
    targetSkill: runtime-cache
    message: 'In-process cache detected — loading Runtime Cache guidance for serverless-compatible caching.'
  -
    pattern: 'fetch\s*\(\s*[''""](https?://)?(api\.openai\.com|api\.anthropic\.com|api\.cohere\.ai)'
    targetSkill: ai-gateway
    message: 'Raw AI provider fetch URL detected — loading AI Gateway guidance for unified routing, failover, and OIDC auth.'
    skipIfFileContains: '@ai-sdk/|from\s+[''""](ai)[''""]|ai-gateway|gateway\('
  -
    pattern: 'jwt\.(sign|verify|decode)\(|from\s+[''""](jsonwebtoken)[''""]|new\s+SignJWT\(|jwtVerify\('
    targetSkill: auth
    message: 'Manual JWT token handling detected — loading Auth guidance for managed authentication (Clerk, Descope, Auth0).'
    skipIfFileContains: 'clerkMiddleware|@clerk/|@auth0/|@descope/|from\s+[''""](next-auth)[''""]'
  -
    pattern: 'from\s+[''"]@/components/ui/|from\s+[''"]@/components/ui[''""]'
    targetSkill: shadcn
    message: 'shadcn/ui component imports detected — loading shadcn guidance for component composition, theming, and registry patterns.'
    skipIfFileContains: 'shadcn|components\.json'
  -
    pattern: 'from\s+[''""](styled-components|@emotion/(react|styled)|@mui/material)[''""]'
    targetSkill: shadcn
    message: 'CSS-in-JS library detected — loading shadcn/ui guidance for Tailwind CSS + Radix UI component patterns (Vercel recommended).'
    skipIfFileContains: '@/components/ui|shadcn'
  -
    pattern: 'getInitialProps'
    targetSkill: nextjs
    message: 'getInitialProps is a legacy Pages Router pattern — loading Next.js guidance for App Router migration with server components and async data fetching.'
    skipIfFileContains: 'app/.*page\.|generateStaticParams|use cache'
  -
    pattern: 'export.*getServerSideProps|getServerSideProps\s*\('
    targetSkill: nextjs
    message: 'getServerSideProps is a Pages Router pattern — loading Next.js guidance for App Router migration with server components and async data fetching.'
    skipIfFileContains: 'generateStaticParams|use cache|app/.*page\.'
  -
    pattern: 'export.*getStaticProps|getStaticProps\s*\('
    targetSkill: nextjs
    message: 'getStaticProps is a Pages Router pattern — loading Next.js guidance for App Router migration with generateStaticParams and server components.'
    skipIfFileContains: 'generateStaticParams|use cache|app/.*page\.'
  -
    pattern: '_app\.(tsx?|jsx?)'
    targetSkill: nextjs
    message: '_app.tsx is a Pages Router pattern — loading Next.js guidance for App Router layout.tsx migration.'
    skipIfFileContains: 'app/layout\.|app/.*layout\.'
  -
    pattern: '_document\.(tsx?|jsx?)'
    targetSkill: nextjs
    message: '_document.tsx is a Pages Router pattern — loading Next.js guidance for App Router layout.tsx with metadata API migration.'
    skipIfFileContains: 'app/layout\.|app/.*layout\.'
  -
    pattern: "from\\s+['\"]next/document['\"]"
    targetSkill: nextjs
    message: 'next/document is Pages Router only — loading Next.js guidance for App Router layout.tsx with html/body structure.'
    skipIfFileContains: 'app/layout\.|app/.*layout\.'
  -
    pattern: 'pages/api/'
    targetSkill: vercel-functions
    message: 'Pages Router API route (pages/api/) detected — loading Vercel Functions guidance for App Router route handlers with named HTTP exports.'
    skipIfFileContains: 'export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)'
  -
    pattern: "from\\s+['\"]react-dom/server['\"]|renderToString\\s*\\("
    targetSkill: satori
    message: 'react-dom/server renderToString detected — for OG image generation, use Satori (@vercel/og) which converts JSX to SVG/PNG without a full React DOM render. Loading Satori guidance.'
    skipIfFileContains: '@vercel/og|ImageResponse|satori'
retrieval:
  aliases:
    - next.js
    - nextjs app
    - react framework
    - app router
  intents:
    - set up routing and layouts in a Next.js app
    - choose between server and client components for a feature
    - configure data fetching or caching in App Router
    - add middleware or proxy logic to handle requests
    - set up server rendering for React pages
    - add a new page with dynamic route segments
  entities:
    - App Router
    - Server Components
    - Server Actions
    - generateMetadata
    - layout
    - proxy
    - next.config
  examples:
    - add a new page with dynamic routing
    - should this be a server or client component
    - set up middleware for auth redirects
    - configure caching for this data fetch
    - set up server rendering for my pages

---

# Next.js (v16+) — App Router

You are an expert in Next.js 16 with the App Router. Always prefer the App Router over the legacy Pages Router unless the user's project explicitly uses Pages Router.

## Critical Pattern: Lazy Initialization for Build-Safe Modules

Never initialize database clients (Neon, Drizzle), Redis (Upstash), or service SDKs (Resend, Slack) at module scope.

During `next build`, static generation can evaluate modules before runtime env vars are present, which causes startup crashes. Always initialize these clients lazily inside getter functions.

```ts
import { drizzle } from 'drizzle-orm/neon-http'
import { neon } from '@neondatabase/serverless'

let _db: ReturnType<typeof drizzle> | null = null

export function getDb() {
  if (!_db) _db = drizzle(neon(process.env.DATABASE_URL!))
  return _db
}
```

Apply the same lazy singleton pattern to Redis and SDK clients (`getRedis()`, `getResend()`, `getSlackClient()`) instead of creating them at import time.

## Scaffolding

When running `create-next-app`, **always** pass `--yes` to skip interactive prompts (React Compiler, import alias) that hang in non-interactive shells:

```bash
npx create-next-app@latest my-app --yes --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --turbopack --use-npm
```

**If the target directory contains ANY non-Next.js files** (`.git/`, config files, etc.), you **MUST** add `--force`. Without it, `create-next-app` will fail with "The directory contains files that could conflict" and block scaffolding. **Check the directory first** — if it has anything in it, use `--force`:

```bash
npx create-next-app@latest . --yes --force --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --turbopack --use-npm
```

### Geist Font Fix (Tailwind v4 + shadcn)

`shadcn init` rewrites `globals.css` with `--font-sans: var(--font-sans)` in `@theme inline` — a circular reference that falls back to Times/serif. Even `var(--font-geist-sans)` doesn't work because Tailwind v4's `@theme inline` resolves at **CSS parse time**, not runtime.

**Two fixes required after `create-next-app` + `shadcn init`:**

1. **Use literal font names in `globals.css`** (not CSS variable references):

```css
@theme inline {
  /* CORRECT — literal names that @theme can resolve at parse time */
  --font-sans: "Geist", "Geist Fallback", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "Geist Mono", "Geist Mono Fallback", ui-monospace, monospace;
}
```

2. **Move font variable classNames from `<body>` to `<html>`** in layout.tsx:

```tsx
// app/layout.tsx — CORRECT
<html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
  <body className="antialiased">
```

```tsx
// app/layout.tsx — WRONG (default scaffold output)
<html lang="en">
  <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
```

**Always apply both fixes** after running `create-next-app` + `shadcn init` with Tailwind v4.

## UI Defaults for App Router Pages

When building pages, layouts, and route-level UI in this stack, default to shadcn/ui + Geist instead of raw Tailwind scaffolding.
- Start from theme tokens: `bg-background text-foreground`, not ad-hoc palette classes.
- Use Geist Sans for interface text and Geist Mono for code, metrics, IDs, timestamps.
- Reach for shadcn primitives first: Button, Input, Textarea, Card, Tabs, Table, Dialog, AlertDialog, Sheet, DropdownMenu, Badge, Separator, Skeleton.
- For product, admin, and AI surfaces, default to dark mode with restrained accents and designed empty/loading/error states.
- Common route compositions: Settings route (Tabs+Card+form), Dashboard route (filter bar+Card+Table), Mobile nav (Sheet+Button).

## Key Architecture

Next.js 16 uses React 19.2 features and the App Router (file-system routing under `app/`). Ensure React **19.2.4+** for security patches (see CVE section below).

### File Conventions
- `layout.tsx` — Persistent wrapper, preserves state across navigations
- `page.tsx` — Unique UI for a route, makes route publicly accessible
- `loading.tsx` — Suspense fallback shown while segment loads
- `error.tsx` — Error boundary for a segment
- `not-found.tsx` — 404 UI for a segment
- `route.ts` — API endpoint (Route Handler)
- `template.tsx` — Like layout but re-mounts on navigation
- `default.tsx` — Fallback for parallel routes

### Routing
- Dynamic segments: `[id]`, catch-all: `[...slug]`, optional catch-all: `[[...slug]]`
- Route groups: `(group)` — organize without affecting URL
- Parallel routes: `@slot` — render multiple pages in same layout
- Intercepting routes: `(.)`, `(..)`, `(...)`, `(..)(..)` — modal patterns

## Server Components (Default)

All components in the App Router are Server Components by default. They:
- Run on the server only, ship zero JavaScript to the client
- Can directly `await` data (fetch, DB queries, file system)
- Cannot use `useState`, `useEffect`, or browser APIs
- Cannot use event handlers (`onClick`, `onChange`)

```tsx
// app/users/page.tsx — Server Component (default)
export default async function UsersPage() {
  const users = await db.query('SELECT * FROM users')
  return <UserList users={users} />
}
```

## Client Components

Add `'use client'` at the top of the file when you need interactivity or browser APIs.

```tsx
'use client'
import { useState } from 'react'

export function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

**Rule**: Push `'use client'` as far down the component tree as possible. Keep data fetching in Server Components and pass data down as props.

## Server Actions / Server Functions

Async functions marked with `'use server'` that run on the server. Use for mutations.

```tsx
// app/actions.ts
'use server'

export async function createUser(formData: FormData) {
  const name = formData.get('name') as string
  await db.insert('users', { name })
  revalidatePath('/users')
}
```

Use Server Actions for:
- Form submissions and data mutations
- In-app mutations with `revalidatePath` / `revalidateTag`

Use Route Handlers (`route.ts`) for:
- Public APIs consumed by external clients
- Webhooks
- Large file uploads
- Streaming responses

## Cache Components (Next.js 16)

The `'use cache'` directive enables component and function-level caching.

```tsx
'use cache'

export async function CachedUserList() {
  cacheLife('hours') // Configure cache duration
  cacheTag('users')  // Tag for on-demand invalidation
  const users = await db.query('SELECT * FROM users')
  return <UserList users={users} />
}
```

### Cache Scope Variants

`'use cache'` supports scope modifiers that control where cached data is stored:

```tsx
// Default — cached in the deployment's local data cache
'use cache'

// Remote cache — shared across all deployments and regions (Vercel only)
'use cache: remote'

// Private cache — per-request cache, never shared between users
'use cache: private'
```

| Variant | Shared across deployments? | Shared across users? | Use case |
|---------|---------------------------|---------------------|----------|
| `'use cache'` | No (per-deployment) | Yes | Default, most use cases |
| `'use cache: remote'` | Yes | Yes | Expensive computations shared globally |
| `'use cache: private'` | No | No | User-specific cached data (e.g., profile) |

### Cache Handler Configuration

Next.js 16 uses `cacheHandlers` (plural) to configure separate handlers for different cache types:

```ts
// next.config.ts
const nextConfig = {
  cacheHandlers: {
    default: require.resolve('./cache-handler-default.mjs'),
    remote: require.resolve('./cache-handler-remote.mjs'),
    fetch: require.resolve('./cache-handler-fetch.mjs'),
  },
}
```

**Important**: `cacheHandlers` (plural, Next.js 16+) replaces `cacheHandler` (singular, Next.js 15). The singular form configured one handler for all cache types. The plural form allows per-type handlers (`default`, `remote`, `fetch`). Using the old singular `cacheHandler` in Next.js 16 triggers a deprecation warning.

### Cache Invalidation

Invalidate with `updateTag('users')` from a Server Action (immediate expiration, Server Actions only) or `revalidateTag('users', 'max')` for stale-while-revalidate from Server Actions or Route Handlers.

**Important**: The single-argument `revalidateTag(tag)` is deprecated in Next.js 16. Always pass a `cacheLife` profile as the second argument (e.g., `'max'`, `'hours'`, `'days'`).

| Function | Context | Behavior |
|----------|---------|----------|
| `updateTag(tag)` | Server Actions only | Immediate expiration, read-your-own-writes |
| `revalidateTag(tag, 'max')` | Server Actions + Route Handlers | Stale-while-revalidate (recommended) |
| `revalidateTag(tag, { expire: 0 })` | Route Handlers (webhooks) | Immediate expiration from external triggers |

## Proxy (formerly Middleware)

In Next.js 16, `middleware.ts` is renamed to `proxy.ts`. It runs **exclusively on the Node.js runtime** — the Edge runtime is not supported in proxy and cannot be configured.

**File location**: Place `proxy.ts` at the same level as your `app/` directory:
- Standard project: `proxy.ts` at project root
- With `--src-dir` (or `srcDir: true`): `src/proxy.ts` (inside `src/`, alongside `app/`)

If you place `proxy.ts` in the wrong location, Next.js will silently ignore it and no request interception will occur.

**Constraints**:
- Proxy can only **rewrite**, **redirect**, or **modify headers** — it cannot return full response bodies. Use Route Handlers for that.
- Config flags are renamed: `skipMiddlewareUrlNormalize` → `skipProxyUrlNormalize`.
- Keep it light: use for high-level traffic control (e.g., redirecting users without a session cookie). Detailed auth should live in Server Components or Server Actions.
- **OpenNext note**: OpenNext doesn't support `proxy.ts` yet — keep using `middleware.ts` if self-hosting with OpenNext.

```ts
// proxy.ts (or src/proxy.ts if using src directory)
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  // Rewrite, redirect, set headers, etc.
}

export const config = { matcher: ['/dashboard/:path*'] }
```

## Upgrading

Use the built-in upgrade command (available since 16.1.0):

```bash
pnpm next upgrade        # or npm/yarn/bun equivalent
```

For versions before 16.1.0: `npx @next/codemod@canary upgrade latest`

If your AI coding assistant supports MCP, the **Next.js DevTools MCP** can automate upgrade and migration tasks.

## What's New in Next.js 16.1

Next.js 16.1 (December 2025, latest stable patch: 16.1.6) builds on 16.0 with developer experience improvements:

1. **Turbopack File System Caching (Stable)** — Compiler artifacts are now cached on disk between `next dev` restarts, delivering up to 14× faster startup on large projects. Enabled by default, no config needed. File system caching for `next build` is planned next.
2. **Bundle Analyzer (Experimental)** — New built-in bundle analyzer works with Turbopack. Offers route-specific filtering, import tracing, and RSC boundary analysis to identify bloated dependencies in both server and client bundles. Enable with `experimental.bundleAnalyzer: true` in `next.config`.
3. **`next dev --inspect`** — Debug your dev server without global `NODE_OPTIONS=--inspect`. Applies the inspector only to the relevant process.
4. **`next upgrade` command** — New CLI command to simplify version upgrades: `npx @next/codemod@canary upgrade latest`.
5. **Transitive External Dependencies** — Turbopack correctly resolves and externalizes transitive deps in `serverExternalPackages` without extra config.
6. **20 MB smaller installs** — Streamlined Turbopack caching layer reduces `node_modules` footprint.

## React 19.2 Features

Next.js 16+ uses React 19.2. These features are available in App Router applications:

### `useEffectEvent` Hook

Creates a stable function that always accesses the latest props and state without triggering effect re-runs. Use when your effect needs to read a value but shouldn't re-run when that value changes:

```tsx
'use client'
import { useEffect, useEffectEvent } from 'react'

function ChatRoom({ roomId, theme }: { roomId: string; theme: string }) {
  const onConnected = useEffectEvent(() => {
    showNotification(`Connected to ${roomId}`, theme) // reads latest theme
  })

  useEffect(() => {
    const connection = createConnection(roomId)
    connection.on('connected', onConnected)
    connection.connect()
    return () => connection.disconnect()
  }, [roomId]) // theme is NOT a dependency — onConnected reads it via useEffectEvent
}
```

Common use cases: logging with current state, notifications using current theme, callbacks that need fresh values but aren't the trigger for the effect.

### `<Activity>` Component

Preserves component state when hiding and showing UI, without unmounting. Solves the classic tradeoff between unmounting (loses state) and CSS `display:none` (effects keep running):

```tsx
'use client'
import { Activity, useState } from 'react'

function TabContainer() {
  const [activeTab, setActiveTab] = useState('inbox')

  return (
    <div>
      <nav>
        <button onClick={() => setActiveTab('inbox')}>Inbox</button>
        <button onClick={() => setActiveTab('drafts')}>Drafts</button>
      </nav>
      <Activity mode={activeTab === 'inbox' ? 'visible' : 'hidden'}>
        <InboxPanel />
      </Activity>
      <Activity mode={activeTab === 'drafts' ? 'visible' : 'hidden'}>
        <DraftsPanel />
      </Activity>
    </div>
  )
}
```

Use for: tabbed interfaces, modals, sidebars, background tasks — anywhere you need to maintain component state without keeping everything actively rendered. When `mode="hidden"`, effects are suspended (not running in the background).

### View Transitions API

React 19.2 supports the browser View Transitions API for animating elements across navigations. Next.js 16 has built-in support — elements can animate between route changes without manual transition logic.

Key change: `useId` now generates IDs with `_r_` prefix (instead of `:r:`) to be valid for `view-transition-name` and XML 1.0 names.

## Layout Deduplication During Prefetching

Next.js 16 deduplicates shared layouts during prefetching. When multiple `<Link>` components point to routes with a shared layout, the layout is downloaded **once** instead of separately for each link.

**Impact**: A page with 50 product links that share a layout downloads ~198KB instead of ~2.4MB — a 92% reduction in prefetch network transfer.

Combined with **incremental prefetching**, Next.js only fetches route segments not already in cache, cancels prefetch requests when links leave the viewport, re-prefetches on hover or viewport re-entry, and re-prefetches when data is invalidated.

## Bundle Analyzer (`next experimental-analyze`)

Built-in bundle analyzer that works with Turbopack (available since Next.js 16.1):

```bash
# Analyze and serve results in browser
next experimental-analyze --serve

# Analyze with custom port
next experimental-analyze --serve --port 4001

# Write analysis to .next/diagnostics/analyze (no server)
next experimental-analyze
```

Features:
- Route-specific filtering between client and server bundles
- Full import chain tracing — see exactly why a module is included
- Traces imports across RSC boundaries and dynamic imports
- No application build required — analyzes module graph directly

Save output for comparison: `cp -r .next/diagnostics/analyze ./analyze-before-refactor`

**Legacy**: For projects not using Turbopack, use `@next/bundle-analyzer` with `ANALYZE=true npm run build`.

## Next.js 16.2 (Canary)

Next.js 16.2 is currently in canary (latest: 16.2.0-canary.84, March 2026). Key areas in development:

1. **Turbopack File System Caching for `next build`** — Extending the stable `next dev` FS cache to production builds for faster CI.
2. **Proxy refinements** — Continued iteration on `proxy.ts` (the Node.js-runtime replacement for `middleware.ts` introduced in 16.0). The proxy API is stabilizing with improved request context and streaming support.
3. **React Compiler optimizations** — Further automatic memoization improvements building on the stable React Compiler in 16.0.

> **Note**: Canary releases are not recommended for production. Track progress at the [Next.js Changelog](https://next-changelog.vercel.app/) or [GitHub Releases](https://github.com/vercel/next.js/releases).

## DevTools MCP

Next.js 16 includes **Next.js DevTools MCP**, a Model Context Protocol integration for AI-assisted debugging. It enables AI agents to diagnose issues, explain behavior, and suggest fixes within your development workflow. If your AI coding assistant supports MCP, DevTools MCP can also automate upgrade and migration tasks.

## Breaking Changes in Next.js 16

1. **Async Request APIs**: `cookies()`, `headers()`, `params`, `searchParams` are all async — must `await` them
2. **Proxy replaces Middleware**: Rename `middleware.ts` → `proxy.ts`, runs on Node.js only (Edge not supported)
3. **Turbopack is top-level config**: Move from `experimental.turbopack` to `turbopack` in `next.config`
4. **View Transitions**: Built-in support for animating elements across navigations
5. **Node.js 20.9+ required**: Dropped support for Node 18
6. **TypeScript 5.1+ required**

## React 19 Gotchas

### `useRef()` Requires an Initial Value

React 19 strict mode enforces that `useRef()` must be called with an explicit initial value. Omitting it causes a type error or runtime warning:

```tsx
// WRONG — React 19 strict mode complains
const ref = useRef()       // ❌ missing initial value
const ref = useRef<HTMLDivElement>()  // ❌ still missing

// CORRECT
const ref = useRef<HTMLDivElement>(null)  // ✅
const ref = useRef(0)                     // ✅
```

This affects all `useRef` calls in client components. The fix is always to pass an explicit initial value (usually `null` for DOM refs).

## Security: Critical CVEs

Multiple vulnerabilities affect **all Next.js App Router applications** (13.4+, 14.x, 15.x, 16.x). Upgrade immediately.

### CVE-2025-66478 / CVE-2025-55182 — Remote Code Execution (CVSS 10.0, Critical)

A deserialization vulnerability in the React Server Components (RSC) "Flight" protocol allows unauthenticated remote code execution via crafted HTTP requests. Near-100% exploit reliability against default configurations. **Actively exploited in the wild.** No workaround — upgrade is required. Rotate all application secrets after patching.

- Affects: Next.js App Router applications (15.x, 16.x, 14.3.0-canary.77+)
- Does NOT affect: Pages Router apps, Edge Runtime, Next.js 13.x, stable Next.js 14.x

### CVE-2025-55184 — Denial of Service (CVSS 7.5, High)

Specially crafted HTTP requests cause the server process to hang indefinitely, consuming CPU and blocking legitimate users. No authentication required, low attack complexity.

### CVE-2025-55183 — Source Code Exposure (CVSS 5.3, Medium)

Malformed HTTP requests can trick Server Actions into returning their compiled source code instead of the expected response. Environment variables are not exposed, but any hardcoded secrets in Server Action code can leak.

### CVE-2026-23864 — Denial of Service via Memory Exhaustion (CVSS 7.5, High)

Disclosed January 26, 2026. The original DoS fix for CVE-2025-55184 was incomplete — additional vectors allow specially crafted HTTP requests to Server Function endpoints to crash the server via out-of-memory exceptions or excessive CPU usage. No authentication required.

### CVE-2025-29927 — Middleware Authorization Bypass (CVSS 9.1, Critical)

An attacker can bypass middleware-based authorization by sending a crafted `x-middleware-subrequest` header, skipping all middleware logic. This affects any Next.js application that relies on `middleware.ts` (or `proxy.ts` in 16+) as the **sole** authorization gate. Patched in Next.js 14.2.25, 15.2.3, and all 16.x releases.

**Mitigation**: Never rely on middleware/proxy as the only auth layer. Always re-validate authorization in Server Components, Server Actions, or Route Handlers. If you cannot patch immediately, block `x-middleware-subrequest` at your reverse proxy or WAF.

### Patched Versions

| Release Line | Minimum Safe Version (all CVEs) |
|---|---|
| 14.x | `next@14.2.35` |
| 15.0.x | `next@15.0.5` |
| 15.1.x | `next@15.1.9` |
| 15.2.x | `next@15.2.6` |
| 15.3.x | `next@15.3.6` |
| 15.4.x | `next@15.4.8` |
| 15.5.x | `next@15.5.7` |
| 16.0.x | `next@16.0.11` |
| 16.1.x | `next@16.1.5` |

Upgrade React to at least **19.0.1** / **19.1.2** / **19.2.1** for the RCE fix (CVE-2025-55182), and **19.2.4+** to fully address all DoS vectors (CVE-2025-55184, CVE-2025-67779, CVE-2026-23864).

```bash
# Upgrade to latest patched versions
npm install next@latest react@latest react-dom@latest
```

Vercel deployed WAF rules automatically for hosted projects, but **WAF is defense-in-depth, not a substitute for patching**.

## Rendering Strategy Decision

| Strategy | When to Use |
|----------|-------------|
| SSG (`generateStaticParams`) | Content rarely changes, maximum performance |
| ISR (`revalidate: N`) | Content changes periodically, acceptable staleness |
| SSR (Server Components) | Per-request fresh data, personalized content |
| Cache Components (`'use cache'`) | Mix static shell with dynamic parts |
| Client Components | Interactive UI, browser APIs needed |
| Streaming (Suspense) | Show content progressively as data loads |

### Rendering Strategy Guidance

```
Choosing a rendering strategy?
├─ Content changes less than once per day?
│  ├─ Same for all users? → SSG (`generateStaticParams`)
│  └─ Personalized? → SSG shell + client fetch for personalized parts
│
├─ Content changes frequently but can be slightly stale?
│  ├─ Revalidate on schedule? → ISR with `revalidate: N` seconds
│  └─ Revalidate on demand? → `revalidateTag()` or `revalidatePath()`
│
├─ Content must be fresh on every request?
│  ├─ Cacheable per-request? → Cache Components (`'use cache'` + `cacheLife`)
│  ├─ Personalized per-user? → SSR with Streaming (Suspense boundaries)
│  └─ Real-time? → Client-side with SWR/React Query + SSR for initial load
│
└─ Mostly static with one dynamic section?
   └─ Partial Prerendering: static shell + Suspense for dynamic island
```

### Caching Strategy Matrix

| Data Type | Strategy | Implementation |
|-----------|----------|----------------|
| Static assets (JS, CSS, images) | Immutable cache | Automatic with Vercel (hashed filenames) |
| API responses (shared) | Cache Components | `'use cache'` + `cacheLife('hours')` |
| API responses (per-user) | No cache or short TTL | `cacheLife({ revalidate: 60 })` with user-scoped key |
| Configuration data | Edge Config | `@vercel/edge-config` (< 5ms reads) |
| Database queries | ISR + on-demand | `revalidateTag('products')` on write |
| Full pages | SSG / ISR | `generateStaticParams` + `revalidate` |
| Search results | Client-side + SWR | `useSWR` with stale-while-revalidate |

### Image Optimization Pattern

```tsx
// BEFORE: Unoptimized, causes LCP & CLS issues
<img src="/hero.jpg" />

// AFTER: Optimized with next/image
import Image from 'next/image';
<Image src="/hero.jpg" width={1200} height={600} priority alt="Hero" />
```

### Font Loading Pattern

```tsx
// BEFORE: External font causes CLS
<link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet" />

// AFTER: Zero-CLS with next/font
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'] });
```

### Cache Components Pattern

```tsx
// BEFORE: Re-fetches on every request
async function ProductList() {
  const products = await db.query('SELECT * FROM products');
  return <ul>{products.map(p => <li key={p.id}>{p.name}</li>)}</ul>;
}

// AFTER: Cached with automatic revalidation
'use cache';
import { cacheLife } from 'next/cache';

async function ProductList() {
  cacheLife('hours');
  const products = await db.query('SELECT * FROM products');
  return <ul>{products.map(p => <li key={p.id}>{p.name}</li>)}</ul>;
}
```

### Optimistic UI Pattern

```tsx
// Instant feedback while Server Action processes
'use client';
import { useOptimistic } from 'react';

function LikeButton({ count, onLike }) {
  const [optimisticCount, addOptimistic] = useOptimistic(count);
  return (
    <button onClick={() => { addOptimistic(count + 1); onLike(); }}>
      {optimisticCount} likes
    </button>
  );
}
```

## OG Image Generation

Next.js supports file-based OG image generation via `opengraph-image.tsx` and `twitter-image.tsx` special files. These use `@vercel/og` (built on Satori) to render JSX to images at the Edge runtime.

### File Convention

Place an `opengraph-image.tsx` (or `twitter-image.tsx`) in any route segment to auto-generate social images for that route:

```tsx
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'Blog post'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default async function Image({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await fetch(`https://api.example.com/posts/${slug}`).then(r => r.json())

  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 48,
          background: 'linear-gradient(to bottom, #000, #111)',
          color: 'white',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 48,
        }}
      >
        {post.title}
      </div>
    ),
    { ...size }
  )
}
```

### Key Points

- **`ImageResponse`** — Import from `next/og` (re-exports `@vercel/og`). Renders JSX to PNG/SVG images.
- **Edge runtime** — OG image routes run on the Edge runtime by default. Export `runtime = 'edge'` explicitly for clarity.
- **Exports** — `alt`, `size`, and `contentType` configure the generated `<meta>` tags automatically.
- **Static or dynamic** — Without params, the image is generated at build time. With dynamic segments, it generates per-request.
- **Supported CSS** — Satori supports a Flexbox subset. Use inline `style` objects (no Tailwind). `display: 'flex'` is required on containers.
- **Fonts** — Load custom fonts via `fetch` and pass to `ImageResponse` options: `{ fonts: [{ name, data, style, weight }] }`.
- **Twitter fallback** — If no `twitter-image.tsx` exists, `opengraph-image.tsx` is used for Twitter cards too.

### When to Use

| Approach | When |
|----------|------|
| `opengraph-image.tsx` file | Dynamic per-route OG images with data fetching |
| Static `opengraph-image.png` file | Same image for every page in a segment |
| `generateMetadata` with `openGraph.images` | Point to an external image URL |

## Deployment on Vercel

- Zero-config: Vercel auto-detects Next.js and optimizes
- `vercel dev` for local development with Vercel features
- Server Components → Serverless/Edge Functions automatically
- Image optimization via `next/image` (automatic on Vercel)
- Font optimization via `next/font` (automatic on Vercel)

## Common Patterns

### Data Fetching in Server Components
```tsx
// Parallel data fetching
const [users, posts] = await Promise.all([
  getUsers(),
  getPosts(),
])
```

### Streaming with Suspense
```tsx
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<Skeleton />}>
        <SlowDataComponent />
      </Suspense>
    </div>
  )
}
```

### Error Handling
```tsx
// app/dashboard/error.tsx
'use client'

export default function Error({ error, reset }: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

## Official Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [App Router](https://nextjs.org/docs/app/getting-started)
- [Routing](https://nextjs.org/docs/app/building-your-application/routing)
- [Data Fetching](https://nextjs.org/docs/app/building-your-application/data-fetching)
- [Rendering](https://nextjs.org/docs/app/building-your-application/rendering)
- [Caching](https://nextjs.org/docs/app/building-your-application/caching)
- [Deploying](https://nextjs.org/docs/app/getting-started/deploying)
- [Upgrading](https://nextjs.org/docs/app/guides/upgrading)
- [GitHub: Next.js](https://github.com/vercel/next.js)
