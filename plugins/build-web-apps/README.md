# Build Web Apps Plugin

This plugin packages builder-oriented workflows in `plugins/build-web-apps`.

It currently includes these skills:

- `deploy-to-vercel`
- `react-best-practices`
- `shadcn-best-practices`
- `stripe-best-practices`
- `supabase-best-practices`
- `web-design-guidelines`

It is scaffolded to use these plugin-local MCP servers:

- `stripe`
- `vercel`
- `supabase`

## What It Covers

- deployment and hosting operations through Vercel MCP
- React and Next.js performance guidance sourced from Vercel best practices
- shadcn/ui composition, styling, and component usage guidance
- Stripe integration design across payments, subscriptions, Connect, and Treasury
- Supabase/Postgres schema, performance, and RLS best practices
- UI review guidance against web interface design guidelines
- end-to-end product building workflows that span frontend, backend, payments,
  and deployment

## Plugin Structure

The plugin now lives at:

- `plugins/build-web-apps/`

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
- React and Next.js optimization guidance
- shadcn/ui frontend implementation guidance
- Stripe integration guidance
- Supabase/Postgres optimization guidance
- web design and UI review guidance
