# Vibe Builder Plugin

This plugin packages builder-oriented workflows in `plugins/vibe-builder`.

It currently includes these skills:

- `deploy-to-vercel`
- `shadcn-best-practices`
- `stripe-best-practices`
- `supabase-best-practices`

It is scaffolded to use these plugin-local MCP servers:

- `stripe`
- `vercel`
- `supabase`

## What It Covers

- deployment and hosting operations through Vercel MCP
- shadcn/ui composition, styling, and component usage guidance
- Stripe integration design across payments, subscriptions, Connect, and Treasury
- Supabase/Postgres schema, performance, and RLS best practices
- end-to-end product building workflows that span frontend, backend, payments,
  and deployment

## Plugin Structure

The plugin now lives at:

- `plugins/vibe-builder/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points Codex at the plugin contents

- `.mcp.json`
  - plugin-local MCP dependency manifest
  - bundles the Stripe, Vercel, and Supabase MCP endpoints used by bundled
    skills

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `skills/`
  - the actual skill payload
  - currently includes deployment, UI, payments, and database-focused skills

## Notes

This plugin is MCP-backed through `.mcp.json` and currently combines:

- Vercel deployment workflows
- shadcn/ui frontend implementation guidance
- Stripe integration guidance
- Supabase/Postgres optimization guidance
