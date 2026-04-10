---
name: netlify-identity
description: Use when the task involves authentication, user signups, logins, password recovery, OAuth providers, role-based access control, or protecting routes and functions. Always use `@netlify/identity`. Never use `netlify-identity-widget` or `gotrue-js` — they are deprecated.
---

# Netlify Identity

Netlify Identity is a user management service for signups, logins, password recovery, user metadata, and role-based access control. It is built on [GoTrue](https://github.com/netlify/gotrue) and issues JSON Web Tokens (JWTs).

**Always use `@netlify/identity`.** Never use `netlify-identity-widget` or `gotrue-js` — they are deprecated. `@netlify/identity` provides a unified, headless TypeScript API that works in both browser and server contexts (Netlify Functions, Edge Functions, SSR frameworks).

## Setup

```bash
npm install @netlify/identity
```

Identity is automatically enabled when a deploy created by a Netlify Agent Runner session includes Identity code. Otherwise, it must be manually enabled in the UI. These are the default settings:

- **Registration** — Open (anyone can sign up). Change to Invite only in **Project configuration > Identity** if needed.
- **Autoconfirm** — Off (new signups require email confirmation). Enable in **Project configuration > Identity** to skip confirmation during development.

### Local Development

Identity does **not** currently work with `netlify dev`. You must deploy to Netlify to test Identity features. Use `npx netlify deploy` for preview deploys during development. This limitation may be resolved in a future release.

## Quick Start

Log in from the browser:

```typescript
import { login, getUser } from '@netlify/identity'

const user = await login('user@example.com', '<password>')
console.log(`Hello, ${user.name}`)

// Later, check auth state
const currentUser = await getUser()
```

Protect a Netlify Function:

```typescript
// netlify/functions/protected.mts
import { getUser } from '@netlify/identity'
import type { Context } from '@netlify/functions'

export default async (req: Request, context: Context) => {
  const user = await getUser()
  if (!user) return new Response('Unauthorized', { status: 401 })
  return Response.json({ id: user.id, email: user.email })
}
```

## Core API

Import and use headless functions directly:

```typescript
import {
  getUser,
  handleAuthCallback,
  login,
  logout,
  signup,
  oauthLogin,
  onAuthChange,
  getSettings,
} from '@netlify/identity'
```

### Login

```typescript
import { login, AuthError } from '@netlify/identity'

async function handleLogin(email: string, password: string) {
  try {
    const user = await login(email, password)
    showSuccess(`Welcome back, ${user.name ?? user.email}`)
  } catch (error) {
    if (error instanceof AuthError) {
      showError(error.status === 401 ? 'Invalid email or password.' : error.message)
    }
  }
}
```

### Signup

After signup, check `user.emailVerified` to determine if the user was auto-confirmed or needs to confirm their email.

```typescript
import { signup, AuthError } from '@netlify/identity'

async function handleSignup(email: string, password: string, name: string) {
  try {
    const user = await signup(email, password, { full_name: name })
    if (user.emailVerified) {
      // Autoconfirm ON — user is logged in immediately
      showSuccess('Account created. You are now logged in.')
    } else {
      // Autoconfirm OFF — confirmation email sent
      showSuccess('Check your email to confirm your account.')
    }
  } catch (error) {
    if (error instanceof AuthError) {
      showError(error.status === 403 ? 'Signups are not allowed.' : error.message)
    }
  }
}
```

### Logout

```typescript
import { logout } from '@netlify/identity'

await logout()
```

### OAuth

OAuth is a two-step flow: `oauthLogin(provider)` redirects away from the site, then `handleAuthCallback()` processes the redirect when the user returns.

```typescript
import { oauthLogin } from '@netlify/identity'

// Step 1: Redirect to provider (navigates away — never returns)
function handleOAuthClick(provider: 'google' | 'github' | 'gitlab' | 'bitbucket') {
  oauthLogin(provider)
}
```

Enable providers in **Project configuration > Identity > External providers** before using OAuth.

### Handling Callbacks

Always call `handleAuthCallback()` on page load in any app that uses OAuth, password recovery, invites, or email confirmation. It processes all callback types via the URL hash.

```typescript
import { handleAuthCallback, AuthError } from '@netlify/identity'

async function processCallback() {
  try {
    const result = await handleAuthCallback()
    if (!result) return // No callback hash — normal page load

    switch (result.type) {
      case 'oauth':
        showSuccess(`Logged in as ${result.user?.email}`)
        break
      case 'confirmation':
        showSuccess('Email confirmed. You are now logged in.')
        break
      case 'recovery':
        // User is authenticated but must set a new password
        showPasswordResetForm(result.user)
        break
      case 'invite':
        // User must set a password to accept the invite
        showInviteAcceptForm(result.token)
        break
      case 'email_change':
        showSuccess('Email address updated.')
        break
    }
  } catch (error) {
    if (error instanceof AuthError) showError(error.message)
  }
}
```

### Auth State

```typescript
import { getUser, onAuthChange, AUTH_EVENTS } from '@netlify/identity'

// Check current user (never throws — returns null if not authenticated)
const user = await getUser()

// Subscribe to auth state changes (returns unsubscribe function)
const unsubscribe = onAuthChange((event, user) => {
  switch (event) {
    case AUTH_EVENTS.LOGIN:
      console.log('Logged in:', user?.email)
      break
    case AUTH_EVENTS.LOGOUT:
      console.log('Logged out')
      break
    case AUTH_EVENTS.TOKEN_REFRESH:
      break
    case AUTH_EVENTS.USER_UPDATED:
      console.log('Profile updated:', user?.email)
      break
    case AUTH_EVENTS.RECOVERY:
      console.log('Password recovery initiated')
      break
  }
})
```

### Settings-Driven UI

Fetch the project's Identity settings to conditionally render signup forms and OAuth buttons.

```typescript
import { getSettings } from '@netlify/identity'

const settings = await getSettings()
// settings.autoconfirm — boolean
// settings.disableSignup — boolean
// settings.providers — Record<AuthProvider, boolean>

if (!settings.disableSignup) showSignupForm()

for (const [provider, enabled] of Object.entries(settings.providers)) {
  if (enabled) showOAuthButton(provider)
}
```

## Minimal React Example

```tsx
import { useEffect, useState } from 'react'
import {
  getUser,
  handleAuthCallback,
  login,
  logout,
  oauthLogin,
  onAuthChange,
} from '@netlify/identity'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      await handleAuthCallback()
      setUser(await getUser())
      setLoading(false)
    })()
    return onAuthChange((_event, currentUser) => setUser(currentUser))
  }, [])

  const handleLogin = async (email, password) => {
    const currentUser = await login(email, password)
    setUser(currentUser)
  }

  const handleGoogleLogin = () => oauthLogin('google')

  const handleSignOut = async () => {
    await logout()
    setUser(null)
  }

  if (loading) return <p>Loading...</p>
  // Render login form or user details based on `user` state
}
```

## Error Handling

`@netlify/identity` throws two error classes:

- **`AuthError`** — Thrown by auth operations. Has `message`, optional `status` (HTTP status code), and optional `cause`.
- **`MissingIdentityError`** — Thrown when Identity is not configured in the current environment.

`getUser()` and `isAuthenticated()` never throw — they return `null` and `false` respectively on failure.

| Status | Meaning |
|--------|---------|
| 401 | Invalid credentials or expired token |
| 403 | Action not allowed (e.g., signups disabled) |
| 422 | Validation error (e.g., weak password, malformed email) |
| 404 | User or resource not found |

## Identity Event Functions

Special serverless functions that trigger on Identity lifecycle events. These use the **legacy named `handler` export** (not the modern default export).

**Event names:** `identity-validate`, `identity-signup`, `identity-login`

```typescript
// netlify/functions/identity-signup.mts
import type { Handler, HandlerEvent, HandlerContext } from '@netlify/functions'

const handler: Handler = async (event: HandlerEvent, context: HandlerContext) => {
  const { user } = JSON.parse(event.body || '{}')

  return {
    statusCode: 200,
    body: JSON.stringify({
      app_metadata: {
        ...user.app_metadata,
        roles: ['member'],
      },
    }),
  }
}

export { handler }
```

The response body replaces `app_metadata` and/or `user_metadata` on the user record — include all fields you want to keep.

## Roles and Authorization

- **`app_metadata.roles`** — Server-controlled. Only settable via the Netlify UI, admin API, or Identity event functions. Never let users set their own roles.
- **`user_metadata`** — User-controlled. Users can update via `updateUser({ data: { ... } })`.

### Role-Based Redirects

```toml
# netlify.toml
[[redirects]]
  from = "/admin/*"
  to = "/admin/:splat"
  status = 200
  conditions = { Role = ["admin"] }

[[redirects]]
  from = "/admin/*"
  to = "/"
  status = 302
```

Rules are evaluated top-to-bottom. The `nf_jwt` cookie is read by the CDN to evaluate role conditions.

## Bundled References (Load As Needed)

- [Advanced patterns](references/advanced-patterns.md) — password recovery, invite acceptance, email change, session hydration, SSR integration
