---
name: auth
description: Authentication integration guidance — Clerk (native Vercel Marketplace), Descope, and Auth0 setup for Next.js applications. Covers middleware auth patterns, sign-in/sign-up flows, and Marketplace provisioning. Use when implementing user authentication.
metadata:
  priority: 6
  docs:
    - "https://authjs.dev/getting-started"
    - "https://nextjs.org/docs/app/building-your-application/authentication"
  sitemap: "https://authjs.dev/sitemap.xml"
  pathPatterns:
    - 'middleware.ts'
    - 'middleware.js'
    - 'src/middleware.ts'
    - 'src/middleware.js'
    - 'clerk.config.*'
    - 'app/sign-in/**'
    - 'app/sign-up/**'
    - 'src/app/sign-in/**'
    - 'src/app/sign-up/**'
    - 'app/(auth)/**'
    - 'src/app/(auth)/**'
    - 'auth.config.*'
    - 'auth.ts'
    - 'auth.js'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*@clerk/nextjs\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@clerk/nextjs\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@clerk/nextjs\b'
    - '\byarn\s+add\s+[^\n]*@clerk/nextjs\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@descope/nextjs-sdk\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@descope/nextjs-sdk\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@descope/nextjs-sdk\b'
    - '\byarn\s+add\s+[^\n]*@descope/nextjs-sdk\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@auth0/nextjs-auth0\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@auth0/nextjs-auth0\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@auth0/nextjs-auth0\b'
    - '\byarn\s+add\s+[^\n]*@auth0/nextjs-auth0\b'
validate:
  -
    pattern: 'VERCEL_CLIENT_(ID|SECRET)|vercel\.com/oauth/(authorize|access_token|token)'
    message: 'Hand-rolled Vercel OAuth detected. Use the dedicated Sign in with Vercel skill for OIDC-based Vercel identity.'
    severity: recommended
    upgradeToSkill: sign-in-with-vercel
    upgradeWhy: 'Replace manual Vercel OAuth token exchange with the Sign in with Vercel OIDC provider.'
    skipIfFileContains: 'signInWithVercel|@vercel/auth'
retrieval:
  aliases:
    - authentication
    - login system
    - sign in
    - auth flow
  intents:
    - add auth
    - protect routes
    - manage sessions
    - implement login
    - secure api endpoints
  entities:
    - NextAuth
    - Auth.js
    - JWT
    - OAuth
    - session
    - middleware
    - getServerSession
  examples:
    - add login to my app
    - protect this route with auth
    - set up NextAuth
chainTo:
  -
    pattern: 'VERCEL_CLIENT_(ID|SECRET)|vercel\.com/oauth/(authorize|access_token|token)'
    targetSkill: sign-in-with-vercel
    message: 'Hand-rolled Vercel OAuth detected — loading Sign in with Vercel OIDC guidance.'
  -
    pattern: 'export\s+(default\s+)?function\s+middleware'
    targetSkill: routing-middleware
    message: 'Auth logic in middleware.ts — loading Routing Middleware guidance for proxy.ts migration in Next.js 16.'
  -
    pattern: 'from\s+[''\"](jsonwebtoken)[''"]|require\s*\(\s*[''\"](jsonwebtoken)[''"]|jwt\.sign\s*\('
    targetSkill: auth
    message: 'Manual JWT handling with jsonwebtoken detected — use Clerk or Auth.js for managed auth with built-in JWT session handling, CSRF protection, and token rotation.'
  -
    pattern: 'from\s+[''\"](next-auth)[''"]|NextAuthOptions|authOptions\s*:'
    targetSkill: auth
    message: 'Legacy next-auth (v4) pattern detected — loading auth guidance for Auth.js v5 migration with the new universal auth() helper.'
  -
    pattern: "from\\s+['\"]@clerk/nextjs['\"]"
    targetSkill: auth
    message: 'Clerk import detected — loading Auth guidance for Clerk v7 patterns, middleware setup, organization handling, and Vercel Marketplace integration.'
    skipIfFileContains: 'clerkMiddleware|ClerkProvider'
  -
    pattern: "bcrypt|argon2"
    targetSkill: auth
    message: 'Manual password hashing detected (bcrypt/argon2) — use Clerk or Auth0 for managed authentication with built-in password hashing, rate limiting, and breach detection.'
    skipIfFileContains: "@clerk|@auth0"
---

# Authentication Integrations

You are an expert in authentication for Vercel-deployed applications — covering Clerk (native Vercel Marketplace integration), Descope, and Auth0.

## Clerk (Recommended — Native Marketplace Integration)

Clerk is a native Vercel Marketplace integration with auto-provisioned environment variables and unified billing. Current SDK: `@clerk/nextjs` v7 (Core 3, March 2026).

### Install via Marketplace

```bash
# Install Clerk from Vercel Marketplace (auto-provisions env vars)
vercel integration add clerk
```

Auto-provisioned environment variables:
- `CLERK_SECRET_KEY` — server-side API key
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` — client-side publishable key

### SDK Setup

```bash
# Install the Clerk Next.js SDK
npm install @clerk/nextjs
```

### Middleware Configuration

```ts
// middleware.ts
import { clerkMiddleware } from "@clerk/nextjs/server";

export default clerkMiddleware();

export const config = {
  matcher: [
    // Skip Next.js internals and static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
```

### Protect Routes

```ts
// middleware.ts — protect specific routes
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher(["/dashboard(.*)", "/api(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});
```

### Frontend API Proxy (Core 3)

Proxy Clerk's Frontend API through your own domain to avoid third-party requests:

```ts
// middleware.ts
export default clerkMiddleware({
  frontendApiProxy: { enabled: true },
});
```

### Provider Setup

```tsx
// app/layout.tsx
import { ClerkProvider } from "@clerk/nextjs";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

### Sign-In and Sign-Up Pages

```tsx
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from "@clerk/nextjs";

export default function Page() {
  return <SignIn />;
}
```

```tsx
// app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from "@clerk/nextjs";

export default function Page() {
  return <SignUp />;
}
```

Add routing env vars to `.env.local`:

```env
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

### Access User Data

```tsx
// Server component
import { currentUser } from "@clerk/nextjs/server";

export default async function Page() {
  const user = await currentUser();
  return <p>Hello, {user?.firstName}</p>;
}
```

```tsx
// Client component
"use client";
import { useUser } from "@clerk/nextjs";

export default function UserGreeting() {
  const { user, isLoaded } = useUser();
  if (!isLoaded) return null;
  return <p>Hello, {user?.firstName}</p>;
}
```

### API Route Protection

```ts
// app/api/protected/route.ts
import { auth } from "@clerk/nextjs/server";

export async function GET() {
  const { userId } = await auth();
  if (!userId) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  return Response.json({ userId });
}
```

## Descope

Descope is available on the Vercel Marketplace with native integration support.

### Install via Marketplace

```bash
vercel integration add descope
```

### SDK Setup

```bash
npm install @descope/nextjs-sdk
```

### Provider and Middleware

```tsx
// app/layout.tsx
import { AuthProvider } from "@descope/nextjs-sdk";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider projectId={process.env.NEXT_PUBLIC_DESCOPE_PROJECT_ID!}>
      <html lang="en">
        <body>{children}</body>
      </html>
    </AuthProvider>
  );
}
```

```ts
// middleware.ts
import { authMiddleware } from "@descope/nextjs-sdk/server";

export default authMiddleware({
  projectId: process.env.DESCOPE_PROJECT_ID!,
  publicRoutes: ["/", "/sign-in"],
});
```

### Sign-In Flow

```tsx
"use client";
import { Descope } from "@descope/nextjs-sdk";

export default function SignInPage() {
  return <Descope flowId="sign-up-or-in" />;
}
```

## Auth0

Auth0 provides a mature authentication platform with extensive identity provider support.

### SDK Setup

```bash
npm install @auth0/nextjs-auth0
```

### Configuration

```ts
// lib/auth0.ts
import { Auth0Client } from "@auth0/nextjs-auth0/server";

export const auth0 = new Auth0Client();
```

Required environment variables:

```env
AUTH0_SECRET=<random-secret>
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://your-tenant.auth0.com
AUTH0_CLIENT_ID=<client-id>
AUTH0_CLIENT_SECRET=<client-secret>
```

### Middleware

```ts
// middleware.ts
import { auth0 } from "@/lib/auth0";
import { NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  return await auth0.middleware(request);
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)",
  ],
};
```

### Access Session Data

```tsx
// Server component
import { auth0 } from "@/lib/auth0";

export default async function Page() {
  const session = await auth0.getSession();
  return session ? (
    <p>Hello, {session.user.name}</p>
  ) : (
    <a href="/auth/login">Log in</a>
  );
}
```

## Decision Matrix

| Need | Recommended | Why |
|------|------------|-----|
| Fastest setup on Vercel | Clerk | Native Marketplace, auto-provisioned env vars |
| Passwordless / social login flows | Descope | Visual flow builder, Marketplace native |
| Enterprise SSO / SAML / multi-tenant | Auth0 | Deep enterprise identity support |
| Pre-built UI components | Clerk | Drop-in `<SignIn />`, `<UserButton />` |
| Vercel unified billing | Clerk or Descope | Both are native Marketplace integrations |

## Clerk Core 3 Breaking Changes (March 2026)

Clerk provides an upgrade CLI that scans your codebase and applies codemods: `npx @clerk/upgrade`. Requires **Node.js 20.9.0+**.

- **`auth()` is async** — always use `const { userId } = await auth()`, not synchronous
- **`auth.protect()` moved** — use `await auth.protect()` directly, not from the return value of `auth()`
- **`clerkClient()` is async** — use `await clerkClient()` in middleware handlers
- **`authMiddleware()` removed** — migrate to `clerkMiddleware()`
- **`@clerk/types` deprecated** — import types from SDK subpath exports: `import type { UserResource } from '@clerk/react/types'` (works from any SDK package)
- **`ClerkProvider` no longer forces dynamic rendering** — pass the `dynamic` prop if needed
- **Cache components** — when using Next.js cache components, place `<ClerkProvider>` inside `<body>`, not wrapping `<html>`
- **Satellite domains** — new `satelliteAutoSync` option skips handshake redirects when no session cookies exist
- **Smaller bundles** — React is now shared across framework SDKs (~50KB gzipped savings)
- **Better offline handling** — `getToken()` now correctly distinguishes signed-out from offline states

## Cross-References

- **Marketplace install and env var provisioning** → `⤳ skill: marketplace`
- **Middleware routing patterns** → `⤳ skill: routing-middleware`
- **Environment variable management** → `⤳ skill: env-vars`
- **Vercel OAuth (Sign in with Vercel)** → `⤳ skill: sign-in-with-vercel`

## Official Documentation

- [Clerk + Vercel Marketplace](https://clerk.com/docs/deployments/vercel)
- [Clerk Next.js Quickstart](https://clerk.com/docs/quickstarts/nextjs)
- [Descope Next.js SDK](https://docs.descope.com/getting-started/nextjs)
- [Auth0 Next.js SDK](https://auth0.com/docs/quickstart/webapp/nextjs)
