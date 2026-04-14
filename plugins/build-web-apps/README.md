# Build Web Apps Plugin

This plugin packages builder-oriented workflows in `plugins/build-web-apps`.

It currently includes these skills:

- `react-best-practices`
- `shadcn-best-practices`
- `supabase-best-practices`
- `web-design-guidelines`

It is scaffolded to use these plugin-local MCP servers:

- `supabase`

## What It Covers

- React and Next.js performance guidance
- shadcn/ui composition, styling, and component usage guidance
- Supabase/Postgres schema, performance, and RLS best practices
- UI review guidance against web interface design guidelines
- end-to-end product building workflows that span frontend, backend, and
  database work

## Plugin Structure

The plugin now lives at:

- `plugins/build-web-apps/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points Codex at the plugin contents

- `.mcp.json`
  - plugin-local MCP dependency manifest
  - bundles the Supabase MCP endpoint used by bundled skills

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `skills/`
  - the actual skill payload
  - currently includes UI, component, React, and database-focused skills

## Notes

This plugin is MCP-backed through `.mcp.json` and currently combines:

- React and Next.js optimization guidance
- shadcn/ui frontend implementation guidance
- Supabase/Postgres optimization guidance
- web design and UI review guidance
