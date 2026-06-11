# Notion Plugin

This plugin packages Notion-driven documentation and planning workflows in
`api_users_plugins/notion`.

It currently includes these skills:

- `notion-spec-to-implementation`
- `notion-research-documentation`
- `notion-meeting-intelligence`
- `notion-knowledge-capture`

## What It Covers

- turning Notion specs into implementation plans, tasks, and progress updates
- researching across Notion content and publishing structured briefs or reports
- preparing meeting agendas and pre-reads using Notion context
- capturing conversations, decisions, and notes into durable Notion pages

## Plugin Structure

The plugin now lives at:

- `api_users_plugins/notion/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points Codex at the plugin contents

- `.mcp.json`
  - plugin-local MCP server manifest
  - points Codex at the Notion MCP server used by the bundled skills

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `skills/`
  - the actual skill payload
  - each skill keeps the normal skill structure (`SKILL.md`, optional
    `agents/`, `references/`, `assets/`, `scripts/`)

## Notes

This plugin is MCP-backed through `.mcp.json` and uses the Notion MCP OAuth
flow for the bundled skills. It intentionally has no `.app.json` declaration so
it can be listed for API key login users.

Plugin-level assets and `agents/openai.yaml` are wired into the manifest and
the bundled skill surface.
