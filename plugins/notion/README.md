# Notion Plugin

This plugin packages Notion-driven documentation and planning workflows in
`plugins/notion`.

It currently includes these skills:

- `notion-spec-to-implementation`
- `notion-research-documentation`
- `notion-meeting-intelligence`
- `notion-knowledge-capture`
- `notion-codex-memory`

## What It Covers

- turning Notion specs into implementation plans, tasks, and progress updates
- researching across Notion content and publishing structured briefs or reports
- preparing meeting agendas and pre-reads using Notion context
- capturing conversations, decisions, and notes into durable Notion pages
- mirroring Codex memories into Notion Memories, so Notion Agent knows what
  Codex learned about you

## Plugin Structure

The plugin now lives at:

- `plugins/notion/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points the runtime at the plugin contents

- `.app.json`
  - plugin-local app manifest
  - points the runtime at the connected Notion app used by the bundled skills

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `hooks.json`
  - `SessionStart` and `Stop` hooks that mirror Codex memories into Notion
    Memories (see below)

- `scripts/codex-memory/`
  - the dependency-free Node.js script the hooks and the
    `notion-codex-memory` skill run

- `skills/`
  - the actual skill payload
  - each skill keeps the normal skill structure (`SKILL.md`, optional
    `agents/`, `references/`, `assets/`, `scripts/`)

## Notes

This plugin is app-backed through `.app.json` and uses the connected Notion
integration for the bundled skills.

Plugin-level assets and `agents/openai.yaml` are wired into the manifest and
the bundled skill surface.

## Codex memories in Notion

With `[features] memories = true`, Codex consolidates what it learns into
`~/.codex/memories/memory_summary.md` and `MEMORY.md` in the background. The
plugin's hooks notice when Codex finishes updating those files and write them
to the user's Notion Memories. They do nothing when Codex memories are off.

- **Same connection:** writes go through the Notion tools Codex is already
  signed in to (the Notion app, or the `notion` server in `.mcp.json`), using
  `codex app-server` and `mcpServer/tool/call` on an ephemeral thread. No model
  runs, the scripts never handle a token, and the thread does not feed back
  into Codex memories.
- **Same write as the Notion memory guide:** `notion-create-pages` with
  `parent: "memory"`, one memory per topic with a Type (`Role and background`,
  `Coding workflow preferences`, and one Work memory per Codex task group),
  and the user's name instead of "the user".
- **Conservative:** unchanged memories are skipped, an existing memory with
  the same title is never duplicated, a page edited or deleted in Notion is
  never touched again, nothing is ever deleted, and the About page is not
  changed.
- **Out of the way:** the hooks only start a detached worker and return. The
  worker connects to Notion only when there is something to write, logs to
  `~/.codex/notion-memory/notion-memory.log`, and never fails a hook.

Requirements: Node.js 22.18 or newer and `codex` on the `PATH` that hooks use
(or `codexPath` in `~/.codex/notion-memory.json`). Codex asks users to trust
the hooks once after installing or updating the plugin.

Run the offline tests with `npm test` in `scripts/codex-memory/`.
