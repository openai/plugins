---
name: notion-codex-memory
description: Mirror Codex memories into Notion Memories on demand, preview what would be written, or show which memories are mirrored; use when the user asks to sync, save, or check their Codex memories in Notion.
metadata:
  short-description: Mirror Codex memories into Notion Memories
---

# Codex Memory in Notion

The Notion plugin already does this automatically. When Codex memories are on
(`[features] memories = true` in `~/.codex/config.toml`), its `SessionStart`
and `Stop` hooks watch `~/.codex/memories/` and, after Codex updates its
memories, write them to the user's Notion Memories through the Notion
connection Codex is signed in to.

Use the bundled script for manual actions. Resolve it relative to the plugin
root (two directories up from this file). It needs Node.js 22.18 or newer.

- Write Codex memories now: `node <plugin-root>/scripts/codex-memory/main.ts sync`
- Preview what would be written, without calling Notion:
  `node <plugin-root>/scripts/codex-memory/main.ts preview`
- Show the memories it manages: `node <plugin-root>/scripts/codex-memory/main.ts status`

`sync` prints counts. `changedInNotion` memories were edited or deleted in
Notion and are left alone on purpose. `skippedExisting` memories already had a
memory with the same title, so no duplicate was created.

Do not write Codex memories into Notion by hand with the Notion tools; the
script keeps track of which pages it owns. If `sync` reports no connected
Notion server, ask the user to connect Notion in Codex. If `preview` returns an
empty list, Codex memories are off or Codex has not written any yet. Logs are in
`~/.codex/notion-memory/notion-memory.log`.
