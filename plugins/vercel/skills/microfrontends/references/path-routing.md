# Path Routing Reference

Vercel handles routing to microfrontends directly in its network infrastructure. When a request arrives at a domain using microfrontends, the `microfrontends.json` file from the live deployment determines which microfrontend handles it.

## Adding a New Path

Modify the `routing` section for the target application in `microfrontends.json`:

```json
{
  "$schema": "https://openapi.vercel.sh/microfrontends.json",
  "applications": {
    "web": {
      "development": {
        "fallback": "web.vercel.app"
      }
    },
    "docs": {
      "routing": [
        {
          "paths": ["/docs/:path*", "/new-path-to-route"]
        }
      ]
    }
  }
}
```

The routing change takes effect when the deployment is live. Test in Preview first.

> **Important:** Changes to separate microfrontends are not rolled out in lockstep. Ensure the target application can handle the requests before merging the config change. Use [flags](#flag-controlled-routing) to control rollout safely.

Use [Instant Rollback](https://vercel.com/docs/instant-rollback) to revert routing changes.

## Supported Path Expressions

| Expression | Description | Example Match |
|---|---|---|
| `/path` | Constant path | `/path` |
| `/:path` | Single path segment wildcard | `/anything` |
| `/:path/suffix` | Single segment with suffix | `/anything/suffix` |
| `/prefix/:path*` | Zero or more segments | `/prefix`, `/prefix/a`, `/prefix/a/b` |
| `/prefix/:path+` | One or more segments | `/prefix/a`, `/prefix/a/b` |
| `/\\(a\\)` | Escaped special characters | `/(a)` |
| `/:path(a\|b)` | Alternation | `/a` or `/b` |
| `/:path(a\|\\(b\\))` | Alternation with escaped chars | `/a` or `/(b)` |
| `/:path((?!a\|b).*)` | Negative lookahead | Any single segment except `/a` or `/b` |
| `/prefix-:path-suffix` | Inline wildcard with prefix/suffix | `/prefix-anything-suffix` |

### Not Supported

- Conflicting or overlapping paths (paths must uniquely map to one microfrontend)
- Regular expressions beyond the patterns listed above
- Wildcards matching multiple segments (`+`, `*`) that don't come at the end of the expression

Use the [`validateRouting` test utility](https://vercel.com/docs/microfrontends/troubleshooting#validaterouting) to verify path expressions resolve to the correct microfrontend.

## Asset Prefix

An asset prefix is a unique path prefix for static assets (JS, CSS, images) to prevent URL collisions between microfrontends.

### Auto-generated (default)

When using `withMicrofrontends`, a default prefix of `vc-ap-<hash>` is generated automatically (obfuscated hash of the project name).

### Custom asset prefix

Set `assetPrefix` in `microfrontends.json`:

```json
"your-application": {
  "assetPrefix": "marketing-assets",
  "routing": [
    {
      "paths": ["/marketing/:path*", "/marketing-assets/:path*"]
    }
  ]
}
```

> **Warning:** Changing the asset prefix after deployment is not guaranteed to be backwards compatible. Route the new prefix in production before updating the `assetPrefix` field.

### Next.js asset notes

JavaScript and CSS URLs are automatically prefixed, but content in the `public/` directory must be manually moved to a subdirectory named with the asset prefix.

## Setting a Default Route

Microfrontend child app deployments may not serve content at `/`. Set a default route in the dashboard so links point to a valid path:

1. Open **Settings** → **Microfrontends** for your project
2. Find **Default Route**
3. Enter a path like `/docs` and save

## Routing to External Applications

For microfrontends not yet on Vercel, create a Vercel project that rewrites requests to the external host, then use that project in `microfrontends.json`.

## Flag-Controlled Routing

> **Note:** Only compatible with Next.js.

Use flags to dynamically control routing. Instead of automatic routing, requests go to the default app which decides via middleware whether to route to the microfrontend.

### Step 1: Add flag to config

```json
{
  "applications": {
    "web": {
      "development": {
        "fallback": "web.vercel.app"
      }
    },
    "docs": {
      "routing": [
        {
          "flag": "name-of-feature-flag",
          "paths": ["/flagged-path"]
        }
      ]
    }
  }
}
```

### Step 2: Add middleware in the default app

```ts
// middleware.ts
import type { NextRequest } from 'next/server';
import { runMicrofrontendsMiddleware } from '@vercel/microfrontends/next/middleware';

export async function middleware(request: NextRequest) {
  const response = await runMicrofrontendsMiddleware({
    request,
    flagValues: {
      'name-of-feature-flag': async () => {
        // Return true to route to the microfrontend, false to keep on default app
        return true;
      },
    },
  });
  if (response) return response;
}

export const config = {
  matcher: [
    '/.well-known/vercel/microfrontends/client-config',
    '/flagged-path',
  ],
};
```

**Key points:**
- The middleware matcher **must** include `/.well-known/vercel/microfrontends/client-config` (used for prefetch optimizations on flagged paths)
- All flagged paths must be listed in the matcher
- Compatible with the [Flags SDK](https://flags-sdk.dev) or any custom implementation
- If using the Flags SDK, share the same `FLAGS_SECRET` across all microfrontends in the group
- Any `async () => boolean` function works as a flag implementation

## Domain Routing Rules

### Production domains

Always route to each project's current production deployment.

### Custom environment domains

Route to custom environments with the same name, or fallback per the fallback environment configuration.

### Branch URLs

Route to the latest deployment for the project on the branch. Fallback if no deployment exists.

### Deployment URLs

Fixed to point-in-time: routes to deployments created for the same commit, or previous commits from the branch.

## Identifying Which Microfrontend Serves a Path

**Dashboard:** Go to the default app project → Deployment → Deployment Summary → Microfrontends accordion.

**Vercel Toolbar:** Open toolbar on any page → Microfrontends Panel → Directory.
