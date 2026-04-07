---
name: netlify-cli-and-deploy
description: Guide for using the Netlify CLI and deploying sites. Use when installing the CLI, linking sites, deploying (Git-based or manual), managing environment variables, or running local development. Covers netlify dev, netlify deploy, Git vs non-Git workflows, and environment variable management.
---

# Netlify CLI and Deployment

## Installation

```bash
npm install -g netlify-cli    # Global (for local dev)
npm install netlify-cli -D    # Local (for CI)
```

Requires Node.js 18.14.0+.

## Authentication

```bash
netlify login       # Opens browser for OAuth
netlify status      # Check auth + linked site status
```

For CI, set `NETLIFY_AUTH_TOKEN` environment variable instead.

## Linking a Site

Check if already linked with `netlify status`. If not:

```bash
# Interactive
netlify link

# By Git remote (if using Git)
netlify link --git-remote-url https://github.com/org/repo

# Create new site
netlify init           # With Git CI/CD setup
netlify init --manual  # Without Git CI/CD
```

Site ID is stored in `.netlify/state.json`. Add `.netlify` to `.gitignore`.

## Deploying

### Git-Based Deploys (Continuous Deployment)

Set up with `netlify init`. Automatic deploys trigger on push/PR:
- Push to production branch → production deploy
- Open PR → deploy preview with unique URL
- Push to other branches → branch deploy

Build runs on Netlify's servers. Configure build settings in `netlify.toml`.

### Manual / Local Deploys (No Git Required)

Build locally, then upload:

```bash
netlify deploy          # Draft deploy (preview URL)
netlify deploy --prod   # Production deploy
netlify deploy --dir=dist  # Specify output directory
```

This works without Git — useful for prototypes, local-only projects, or CI pipelines.

## Local Development

### Option 1: netlify dev

```bash
netlify dev
```

Wraps your framework's dev server and provides:
- Environment variable injection
- Functions and edge functions
- Redirects and headers processing

### Option 2: Netlify Vite Plugin (Vite-based projects)

For projects using Vite (React SPA, TanStack Start, SvelteKit, Remix), the Vite plugin provides Netlify platform primitives directly in the framework's dev server:

```bash
npm install @netlify/vite-plugin
```

```typescript
// vite.config.ts
import netlify from "@netlify/vite-plugin";
export default defineConfig({ plugins: [netlify()] });
```

Then run your normal dev command (`npm run dev`) — no `netlify dev` wrapper needed. This gives you access to Blobs, DB, Functions, and environment variables during development.

See the **netlify-frameworks** skill for framework-specific local dev guidance.

## Environment Variables

### CLI Management

```bash
# Set
netlify env:set API_KEY "value"
netlify env:set API_KEY "value" --secret              # Hidden from logs
netlify env:set API_KEY "value" --context production   # Context-specific

# Get
netlify env:get API_KEY

# List
netlify env:list
netlify env:list --plain > .env                        # Export to file

# Import from file
netlify env:import .env

# Delete
netlify env:unset API_KEY
```

### Context Scoping

Variables can be scoped to deploy contexts:

```bash
netlify env:set API_URL "https://api.prod.com" --context production
netlify env:set API_URL "https://api.staging.com" --context deploy-preview
netlify env:set DEBUG "true" --context branch:feature-x
```

### Accessing in Code

- **Server-side (Functions)**: Use `Netlify.env.get("VAR")` (preferred) or `process.env.VAR`
- **Client-side (Vite)**: Only `VITE_`-prefixed vars via `import.meta.env.VITE_VAR`
- **Client-side (Astro)**: Only `PUBLIC_`-prefixed vars via `import.meta.env.PUBLIC_VAR`

**Never use `VITE_` or `PUBLIC_` prefix for secrets** — these are exposed to the browser.

## Useful Commands

| Command | Description |
|---|---|
| `netlify status` | Auth and site link status |
| `netlify dev` | Start local dev server |
| `netlify build` | Run build locally (mimics Netlify environment) |
| `netlify deploy` | Draft deploy |
| `netlify deploy --prod` | Production deploy |
| `netlify dev:exec <cmd>` | Run command with Netlify environment loaded |
| `netlify env:list` | List environment variables |
| `netlify clone org/repo` | Clone, link, and set up in one step |
