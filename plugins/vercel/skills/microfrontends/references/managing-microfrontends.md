# Managing Microfrontends Reference

## Inspecting a Group

Use `vercel microfrontends inspect-group` to retrieve metadata about a microfrontends group and its projects. This is useful for setup automation and scripts — it provides the project names, frameworks, git repos, and root directories needed to generate `microfrontends.json` and wire up framework integrations.

```bash
vercel microfrontends inspect-group [options]
```

If you omit `--group`, the command is interactive and lets you select a group. In non-interactive environments, pass `--group`.

### Options

| Option | Description |
|---|---|
| `--group` | Name, slug, or ID of the microfrontends group to inspect |
| `--config-file-name` | Custom microfrontends config file path/name relative to the default app root (must end with `.json` or `.jsonc`) |
| `--format` | Output format. Use `json` for machine-readable output |

### Examples

```bash
# Interactive selection
vercel microfrontends inspect-group

# JSON output for scripting/agents
vercel mf inspect-group --group="My Group" --format=json

# With a custom config filename
vercel mf inspect-group --group="My Group" --config-file-name=microfrontends.jsonc --format=json
```

> **Tip for agents:** After the user creates a group, run `vercel mf inspect-group --group="<name>" --format=json` to get the project metadata needed to automate the remaining setup (generating `microfrontends.json`, installing `@vercel/microfrontends`, and adding framework integrations).

## Adding Microfrontends

**CLI:** run from the project directory and follow the prompts:

```bash
vercel microfrontends add-to-group
# or with flags:
vercel mf add-to-group --group="My Group" --default-route=/docs
```

**Dashboard:** Settings → Microfrontends → find the group → **Add to Group**.

Changes take effect on the next deployment.

## Removing Microfrontends

**CLI:** run from the project directory and follow the prompts:

```bash
vercel microfrontends remove-from-group
```

After removal, update `microfrontends.json` in the default app to remove the project's entry — the CLI will warn you if it's still referenced but won't block the removal.

**Dashboard:**
1. Remove the microfrontend from `microfrontends.json` in the default app
2. Visit **Settings** for the project
3. Click **Microfrontends** → **Remove from Group**

> The default application can only be removed after all other projects in the group are removed.

## Deleting a Group

This action is not reversible. You can delete a group even with projects still in it — all projects will be removed from the group automatically.

**CLI:** run from the project directory and follow the prompts:

```bash
vercel microfrontends delete-group
# or pre-select the group with a flag:
vercel mf delete-group --group="My Group"
```

**Dashboard:** Go to the group's settings in **Settings** → **Microfrontends** and delete the group.

## Fallback Environment

Controls where requests are routed when a microfrontend isn't built for a specific commit. This applies to Preview and Custom environments only — production always routes to each project's production deployment.

### Options

| Setting | Behavior |
|---|---|
| `Same Environment` | Falls back to a deployment in the same environment for the other project. Vercel auto-generates Preview deployments on the production branch. |
| `Production` | Falls back to the promoted Production deployment of the other project. |
| Custom environment name | Falls back to a deployment in the specified custom environment. |

### Fallback behavior matrix

| Current Environment | Fallback Setting | Built for Commit | Not Built for Commit |
|---|---|---|---|
| Preview | Same Environment | Preview | Preview |
| Preview | Production | Preview | Production |
| Preview | `staging` | Preview | `staging` |
| `staging` | Same Environment | `staging` | `staging` |
| `staging` | Production | `staging` | Production |

Configure in **Settings** → Microfrontends group → **Fallback Environment**.

> If using Same Environment or Custom Environment, ensure those environments have deployments to fall back to. Missing fallbacks cause `MICROFRONTENDS_MISSING_FALLBACK_ERROR`.

### Branch domain fallbacks

If a project has a domain assigned to a Git branch and fallback is set to Same Environment, deployments on that branch use the branch's project domain as fallback instead of the production branch. Add the branch domain to every project in the group.

## Sharing Settings

Use the [Vercel Terraform Provider](https://registry.terraform.io/providers/vercel/vercel/latest/docs) to synchronize settings across projects:

- [Microfrontend group resource](https://registry.terraform.io/providers/vercel/vercel/latest/docs/resources/microfrontend_group)
- [Microfrontend group membership resource](https://registry.terraform.io/providers/vercel/vercel/latest/docs/resources/microfrontend_group_membership)

### Sharing environment variables

Use [Shared Environment Variables](https://vercel.com/docs/environment-variables/shared-environment-variables) to manage secrets across projects.

For same-name variables with different values per group, create a shared var with a unique name (e.g., `FLAG_SECRET_X`) then map it: `FLAG_SECRET=$FLAG_SECRET_X` in `.env` or build command.

## Optimizing Navigations

> **Note:** Currently only supported for Next.js.

Navigations between top-level microfrontends cause hard navigations. Vercel optimizes these by prefetching and prerendering cross-zone links.

### Setup for Next.js App Router

Add `PrefetchCrossZoneLinks` to your root layout in **all** microfrontend apps:

```tsx
// app/layout.tsx
import { PrefetchCrossZoneLinks } from '@vercel/microfrontends/next/client';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <PrefetchCrossZoneLinks />
      </body>
    </html>
  );
}
```

`PrefetchCrossZoneLinks` accepts an optional `prerenderEagerness` prop (`'immediate' | 'eager' | 'moderate' | 'conservative'`, default `'conservative'`) that controls how aggressively cross-zone pages are prerendered in the background.

### Setup for Next.js Pages Router

Add `PrefetchCrossZoneLinks` to `_app.tsx`:

```tsx
// pages/_app.tsx
import { PrefetchCrossZoneLinks } from '@vercel/microfrontends/next/client';

export default function App({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <PrefetchCrossZoneLinks />
    </>
  );
}
```

### Using the Link component

Use the microfrontends `Link` component instead of regular anchors for cross-zone links:

```tsx
import { Link } from '@vercel/microfrontends/next/client';

export function Navigation() {
  return (
    <nav>
      <Link href="/docs">Docs</Link>
      <Link href="/blog">Blog</Link>
    </nav>
  );
}
```

> **Note:** All paths from `microfrontends.json` become visible on the client side when using this feature.

## Observability Data Routing

By default, Speed Insights and Analytics data routes to the default application.

To route a project's data to its own Vercel project page:

1. Update dependencies:
   - `@vercel/speed-insights` ≥ `1.2.0`
   - `@vercel/analytics` ≥ `1.5.0`
2. Go to **Settings** → **Microfrontends** for the project
3. Find **Observability Routing** and enable it
4. Takes effect on the next production deployment

> Toggling does not move historical data.

If using Turborepo with `--env-mode=strict`, add `ROUTE_OBSERVABILITY_TO_THIS_PROJECT` and `NEXT_PUBLIC_VERCEL_OBSERVABILITY_BASEPATH` to allowed env vars, or use `--env-mode=loose`.
