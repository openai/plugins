# Board Runtime

Use this reference whenever `produce` opens, updates, or restores the Creative Production board.

## One Board Per Workflow

`creative_production_board` is the single UI and state tool. Call `action=open` once and reuse its returned `boardId` for the whole workflow. The server stores each board independently under `$CODEX_HOME/creative-production/boards/<boardId>`.

Call `creative_production_board` directly. Do not wrap it in `functions.exec`: nested forwarding can reduce a rich MCP result to text and prevent the host from delivering the UI resource to the mounted board.

For generation:

1. Call `begin_generation` only when generation actually starts. Pass stable item IDs and useful titles, captions, prompts, and parent IDs.
2. Generate through the selected route.
3. For each successful local file, call `complete_generation` with the same `boardId`, matching item ID, and absolute `imagePath`. The path may be in the active task workspace or another readable local directory. The server validates the file, preserves the original, and creates a bounded preview.
4. Call `fail_generation` for terminal failures.
5. Check the returned board ID, item ID, and revision. Do not call `open` or create another widget to refresh the board.

The board app uses `set_ui_state` and `delete_items` for direct manipulation. Every mutation takes a cross-process file lock, rereads the latest board state, increments its revision, and commits with an atomic rename, so simultaneous MCP workers and delayed model results cannot overwrite newer changes.

Every result returns the same widget URI and sets `openai/widgetSessionId` to the board UUID. That stable pair lets the host route `begin_generation`, `complete_generation`, reads, and UI mutations back to the existing board surface. It does not authorize another `open`; call `open` once and reuse the board ID. `complete_generation` also carries that item's bounded preview. Direct widget actions reconcile their bridge result immediately, while the bounded refresh watcher remains a recovery path for missed delivery and thread restoration. The widget keeps a revisioned IndexedDB view cache of snapshots and already-seen previews so a remount remains useful if the host bridge is temporarily unavailable. The MCP store remains authoritative: visible boards retry transient bridge failures and never write polling events back into the trace log.

## Payload Boundary

Board reads contain metadata only. A targeted `read` with `itemId` returns one bounded preview. Never pass data URLs or image bytes to `complete_generation`; pass the absolute generated file path directly without copying it to a special ingest directory.

Use 4-6 items by default. Each item is one clean image, not a collage or contact sheet.
