---
name: microfrontends
description: Guide for building, configuring, and deploying microfrontends on Vercel. Use this skill when the user mentions microfrontends, multi-zones, splitting an app across teams, independent deployments, cross-app routing, incremental migration, composing multiple frontends under one domain, microfrontends.json, @vercel/microfrontends, the microfrontends local proxy, or path-based routing between Vercel projects. Also use when the user asks about shared layouts across projects, navigation between microfrontends, fallback environments, asset prefixes, or feature flag controlled routing.
metadata:
  priority: 7
  docs:
    - "https://vercel.com/docs/microfrontends"
  pathPatterns:
    - 'microfrontends.json'
    - 'microfrontends.jsonc'
    - 'apps/*/microfrontends.json'
    - 'apps/*/microfrontends.jsonc'
  bashPatterns:
    - '\bvercel\s+microfrontends\b'
    - '\bvercel\s+mf\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/microfrontends\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/microfrontends\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/microfrontends\b'
    - '\byarn\s+add\s+[^\n]*@vercel/microfrontends\b'
  importPatterns:
    - '@vercel/microfrontends'
---

# Vercel Microfrontends
Split a large application into independently deployable units that render as one cohesive app. Vercel handles routing on its global network using `microfrontends.json`.

**Core concepts:** default app (has `microfrontends.json`, serves unmatched requests) · child apps (have `routing` path patterns) · asset prefix (prevents static-asset collisions) · independent deployments.

**Frameworks:** Next.js (App Router + Pages Router), SvelteKit, React Router, Vite — all via `@vercel/microfrontends`.

**CLI (`vercel microfrontends` / `vercel mf`):**
- `create-group` — create a new group; interactive by default, or fully non-interactive with `--non-interactive` (options: `--name`, `--project` (repeatable), `--default-app`, `--default-route`, `--project-default-route` (repeatable, format: `<project>=<route>`, required for each non-default project in non-interactive mode), `--yes` to skip confirmation prompt); note: `--non-interactive` is blocked if adding the projects would exceed the free tier limit — the user must confirm billing changes interactively
- `add-to-group` — add the current project to an existing group; requires interactive terminal (options: `--group`, `--default-route`)
- `remove-from-group` — remove the current project from its group; requires interactive terminal (option: `--yes` skips project-link prompt only)
- `delete-group` — delete a group and all its settings, irreversible; requires interactive terminal (option: `--group` to pre-select group)
- `inspect-group` — retrieve group metadata (project names, frameworks, git repos, root dirs); useful for automating setup (options: `--group`, `--format=json`, `--config-file-name`)
- `pull` — pull remote `microfrontends.json` for local development (option: `--dpl`)
- `microfrontends proxy` — local dev proxy · `microfrontends port` — print auto-assigned port

## Finding Detailed Information

This skill includes detailed reference docs in the `references/` directory. **Do not read all references upfront.** Instead, search or grep the relevant file when the user asks about a specific topic:

| Topic | Reference file |
|---|---|
| Getting started, quickstart, framework setup, `microfrontends.json` schema, fields, naming, examples | `references/configuration.md` |
| Path expressions, asset prefixes, flag-controlled routing, middleware | `references/path-routing.md` |
| Local proxy setup, polyrepo config, Turborepo, ports, deployment protection | `references/local-development.md` |
| Inspecting groups (`inspect-group`), adding/removing projects, fallback environments, navigation, observability | `references/managing-microfrontends.md` |
| Testing utilities (`validateMiddlewareConfig`, `validateRouting`, etc.), debug headers, common issues | `references/troubleshooting.md` |
| Deployment protection, Vercel Firewall, WAF rules for microfrontends | `references/security.md` |

When the user asks about a specific topic, use grep or search over the relevant reference file to find the answer without loading all references into context.
