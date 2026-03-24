---
name: sign-in-with-vercel
description: Sign in with Vercel guidance — OAuth 2.0/OIDC identity provider for user authentication via Vercel accounts. Use when implementing user login with Vercel as the identity provider.
metadata:
  priority: 6
  docs:
    - "https://vercel.com/docs/sign-in-with-vercel"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns: 
    - 'app/api/auth/**'
    - 'app/login/**'
    - 'src/app/api/auth/**'
    - 'src/app/login/**'
    - 'pages/api/auth/**'
  bashPatterns: []
retrieval:
  aliases:
    - vercel oauth
    - vercel login
    - vercel identity
    - oauth provider
  intents:
    - add vercel login
    - implement oauth with vercel
    - use vercel as identity provider
  entities:
    - OAuth 2.0
    - OIDC
    - Sign in with Vercel
    - identity provider
chainTo:
  -
    pattern: 'next-auth|NextAuth|from\s+[''"]next-auth[''""]|from\s+[''"]@auth/[''""]'
    targetSkill: auth
    message: 'NextAuth/Auth.js detected alongside Vercel OAuth — loading Auth guidance for proper integration patterns, middleware setup, and provider configuration.'
    skipIfFileContains: 'clerkMiddleware|@clerk/|from\s+[''"]@descope/'
  -
    pattern: 'VERCEL_CLIENT_ID|VERCEL_CLIENT_SECRET'
    targetSkill: env-vars
    message: 'Vercel OAuth environment variables detected — loading Env Vars guidance for secure configuration and vercel env management.'
    skipIfFileContains: 'vercel\s+env\s+pull|process\.env\.VERCEL_CLIENT_ID'

---

# Sign in with Vercel

You are an expert in Sign in with Vercel — Vercel's OAuth 2.0 / OpenID Connect identity provider.

## What It Is

Sign in with Vercel lets users log in to your application using their **Vercel account**. Your app does not need to handle passwords, create accounts, or manage user sessions — Vercel acts as the identity provider (IdP).

## OAuth 2.0 Authorization Code Flow

```
1. User clicks "Sign in with Vercel"
2. Redirect to Vercel authorization URL
3. User grants consent on Vercel's consent page
4. Vercel redirects back with authorization code
5. Exchange code for tokens (ID Token + Access Token + Refresh Token)
```

## Tokens

| Token | Lifetime | Purpose |
|-------|----------|---------|
| **ID Token** | Signed JWT | Proves user identity (name, email, avatar) |
| **Access Token** | 1 hour | Bearer token for Vercel REST API calls |
| **Refresh Token** | 30 days | Silent re-authentication (rotates on use) |

## Configuration

1. Register your app at `https://vercel.com/dashboard/{team}/integrations/console` (the Integrations Console). Click **Create Integration** → fill in the OAuth details → note the Client ID and Client Secret.
2. Configure redirect URIs and scopes
3. Use any standard OAuth 2.0 client library (no Vercel-specific SDK required)

## When to Use

- Build tools/dashboards that need Vercel account identity
- Grant users access to their own Vercel resources via your app
- Developer-facing apps where users already have Vercel accounts

## When NOT to Use

- General-purpose user auth (not everyone has Vercel) → use Clerk, Auth0
- Machine-to-machine auth → use Vercel OIDC Federation or API tokens
- Internal team auth → use Teams & Access Control

## References

- 📖 docs: https://vercel.com/docs/sign-in-with-vercel
