# Creative Production MCP

The plugin has one MCP server:

- `server.mjs`: source entrypoint for the persistent Creative Production app and the single structured image-generation-path choice.
- `server.bundle.mjs`: generated distribution entrypoint; do not commit it.

Keep app registrations under `registrations/`, shared server logic under `lib/`, and browser assets with the board app.

`mcp/lib/creative-board-store.mjs` is the sole board-state authority. It stores revisioned boards and structured NDJSON traces under `$CODEX_HOME/creative-production`, imports original generated files, creates bounded previews, and commits mutations atomically.

`creative_production_board` owns both the app and its state actions. Only `action=open` returns the widget template. Read, mutation, preview, and logging results return data to the existing app without advertising a template, so they cannot create replacement frames.

The packaged internal distribution is bundle-based. `.mcp.json` points at `./mcp/server.bundle.mjs`; `npm run build:plugin:prod` builds that file, copies it to `plugins/internal-distribution/build/creative-production`, and cleans generated bundle/vendor files from this source tree.

Do not add a separate intake server or workflow-specific structured forms.

## Development And Orchestration

Install dependencies and validate from the plugin root:

```bash
npm ci
npm run check
npm run test:web:moodboard
node ./scripts/probe-mcp.mjs
```

The orchestration is intentionally small:

1. `open` creates one UUID board and mounts the widget.
2. The widget sends direct edits through `set_ui_state` or `delete_items`.
3. The model calls `begin_generation` only when generation starts.
4. The model generates files, then calls `complete_generation` with each absolute, readable local path. The server validates the file, preserves the original, and creates a bounded preview.
5. Mutations return small non-UI receipts. A bounded watcher refreshes the mounted app only while a submitted generation is starting or active, then stops.
6. On task navigation back to the board, the widget performs one metadata read and restores the same UUID board.

State and traces live under `$CODEX_HOME/creative-production`. Cross-process file locks protect concurrent MCP mutations. The diagnostics panel is collapsed by default; it shows recent redacted events while the full per-board trace remains in `boards/<boardId>/trace.ndjson`.

For a local Desktop install, use the `install-refactored-plugin` skill from the worktree being tested. Restart Codex after installation and use a fresh task so tool metadata and widget resources come from the new installed version.
