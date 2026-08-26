# Configuration Reference

The `microfrontends.json` file is the single source of truth for microfrontend routing. It must be deployed with the default application.

## Getting Started

1. **Create a microfrontends group** using the CLI (`vercel microfrontends create-group`) or the Vercel Dashboard: Settings → Microfrontends → Create Group.
2. **Inspect the group** (optional but recommended for automation): `vercel mf inspect-group --group="<name>" --format=json` returns project names, frameworks, git repos, and root directories needed for the remaining steps.
3. **Add `microfrontends.json`** at the root of the default application (see [Full Schema](#full-schema) and [Example Configurations](#example-configurations)).
4. **Install** in every microfrontend: `pnpm i @vercel/microfrontends`
5. **Integrate with your framework** — add `withMicrofrontends` (Next.js/SvelteKit) or the `microfrontends()` Vite plugin to each app's config (see [Framework Setup](#framework-setup)).
6. **Deploy** — push to Vercel. Config takes effect once `microfrontends.json` is deployed to production.

> **Note:** If the user has already created the group (step 1), the immediate next steps are to set up `microfrontends.json` (step 3), install `@vercel/microfrontends` (step 4), and add the framework integration (step 5) in each project. Do not skip these — the group alone does nothing without the config and framework wiring.

## Framework Setup

### Next.js

```ts
// next.config.ts
import { withMicrofrontends } from '@vercel/microfrontends/next/config';
export default withMicrofrontends(nextConfig);
```

For Pages Router support:

```ts
export default withMicrofrontends(nextConfig, { supportPagesRouter: true });
```

### SvelteKit

Wrap the SvelteKit config with `withMicrofrontends` from `@vercel/microfrontends/experimental/sveltekit` and add the `microfrontends()` Vite plugin from `@vercel/microfrontends/experimental/vite`.

### React Router / Vite

Add the `microfrontends()` Vite plugin from `@vercel/microfrontends/experimental/vite`.

## Full Schema

```json
{
  "$schema": "https://openapi.vercel.sh/microfrontends.json",
  "version": "1",
  "applications": {
    "<default-app-name>": {
      "packageName": "<optional: name from package.json if different>",
      "development": {
        "fallback": "<required: production URL for fallback>",
        "local": "<optional: port number or host for local dev>",
        "task": "<optional: dev script name, default 'dev'>"
      }
    },
    "<child-app-name>": {
      "packageName": "<optional: name from package.json if different>",
      "assetPrefix": "<optional: custom asset prefix>",
      "routing": [
        {
          "group": "<optional: group name>",
          "flag": "<optional: feature flag name>",
          "paths": ["/path/:path*"]
        }
      ],
      "development": {
        "local": "<optional: port or host>",
        "task": "<optional: dev script name>",
        "fallback": "<optional: overrides default app fallback>"
      }
    }
  },
  "options": {
    "localProxyPort": 3024,
    "disableOverrides": false
  }
}
```

## Field Details

### `applications` (required)

A map of Vercel project names to their configurations. Keys must match the Vercel project name.

**One application must be the default app** — identified by not having a `routing` field. There must be exactly one.

### Default Application

| Field | Type | Required | Description |
|---|---|---|---|
| `development.fallback` | `string` | Yes | Production URL used as fallback for apps not running locally. Include host only (e.g., `myapp.vercel.app`). Protocol defaults to HTTPS. |
| `development.local` | `number \| string` | No | Port or host for local dev. Default: auto-assigned based on app name. |
| `development.task` | `string` | No | Script name from `package.json` to run for dev. Default: `"dev"`. |
| `packageName` | `string` | No | Set if Vercel project name differs from `package.json` `name` field. |

### Child Application

| Field | Type | Required | Description |
|---|---|---|---|
| `routing` | `PathGroup[]` | Yes | Array of path groups that route to this app. |
| `assetPrefix` | `string` | No | Custom asset prefix. Default: auto-generated `vc-ap-<hash>`. |
| `development.local` | `number \| string` | No | Port or host for local dev. |
| `development.task` | `string` | No | Dev script name. |
| `development.fallback` | `string` | No | Override fallback URL. Defaults to the default app's fallback. |
| `packageName` | `string` | No | Set if project name differs from `package.json` `name`. |

### PathGroup

| Field | Type | Required | Description |
|---|---|---|---|
| `paths` | `string[]` | Yes | Path expressions routed to this app. |
| `group` | `string` | No | Descriptive group name. |
| `flag` | `string` | No | Feature flag name controlling routing for this group. |

### `options`

| Field | Type | Default | Description |
|---|---|---|---|
| `localProxyPort` | `number` | `3024` | Port for the local development proxy. |
| `disableOverrides` | `boolean` | `false` | Disable routing overrides in the Vercel Toolbar. |

## Application Naming

Application keys in `microfrontends.json` must match Vercel project names. If the project name differs from the `name` field in the app's `package.json`, set `packageName`:

```json
{
  "applications": {
    "docs": {
      "packageName": "my-docs-package",
      "routing": [
        { "paths": ["/docs/:path*"] }
      ]
    }
  }
}
```

## File Naming

- Default names: `microfrontends.json` or `microfrontends.jsonc`
- Custom name via env var: `VC_MICROFRONTENDS_CONFIG_FILE_NAME`
  - Must end with `.json` or `.jsonc`
  - May include a path: `/path/to/microfrontends.json`
  - Path is relative to the root directory of the default application
  - Add this env var to **all projects** in the microfrontends group

Using a custom file name allows the same repository to support multiple microfrontends groups.

**With Turborepo:** Define the env var outside the Turbo invocation:

```bash
VC_MICROFRONTENDS_CONFIG_FILE_NAME="microfrontends-dev.json" turbo dev
```

## Example Configurations

### Minimal (two Next.js apps)

```json
{
  "$schema": "https://openapi.vercel.sh/microfrontends.json",
  "applications": {
    "web": {
      "development": {
        "fallback": "web-production.vercel.app"
      }
    },
    "docs": {
      "routing": [
        { "paths": ["/docs/:path*"] }
      ]
    }
  }
}
```

### With custom ports, flags, and asset prefix

```json
{
  "$schema": "https://openapi.vercel.sh/microfrontends.json",
  "applications": {
    "marketing": {
      "development": {
        "local": 3000,
        "fallback": "marketing.vercel.app"
      }
    },
    "docs": {
      "assetPrefix": "docs-assets",
      "development": { "local": 3001 },
      "routing": [
        {
          "group": "docs",
          "paths": ["/docs/:path*", "/docs-assets/:path*"]
        },
        {
          "group": "flagged-docs",
          "flag": "enable-new-docs",
          "paths": ["/new-docs/:path*"]
        }
      ]
    }
  }
}
```

## JSON Schema Validation

Use the schema URL for editor autocompletion and validation:

```json
{
  "$schema": "https://openapi.vercel.sh/microfrontends.json"
}
```
