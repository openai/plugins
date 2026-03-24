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

- `.app.json`
  - plugin-local app manifest
  - points Codex at the connected Notion app used by the bundled skills

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `skills/`
  - the actual skill payload
  - each skill keeps the normal skill structure (`SKILL.md`, optional
    `agents/`, `references/`, `assets/`, `scripts/`)

## Notes

This plugin is app-backed through `.app.json` and uses the connected Notion
integration for the bundled skills.

Plugin-level assets and `agents/openai.yaml` are wired into the manifest and
the bundled skill surface.
