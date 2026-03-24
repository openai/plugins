# Notion Plugin

This plugin packages Notion-driven documentation and planning workflows in
`plugins/notion`.

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

- `plugins/notion/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points Codex at the plugin contents

- `.mcp.json`
  - plugin-local MCP dependency manifest
  - bundles the Notion MCP endpoint used by the bundled skills

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `skills/`
  - the actual skill payload
  - each skill keeps the normal skill structure (`SKILL.md`, optional
    `agents/`, `references/`, `assets/`, `scripts/`)

## Notes

This plugin is MCP-backed through `.mcp.json` and currently depends on the
Notion MCP server at `https://mcp.notion.com/mcp`.

Plugin-level assets and `agents/openai.yaml` are wired into the manifest and
the bundled skill surface.
