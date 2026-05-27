---
name: dropbox
description: Work with Dropbox through the configured Dropbox app connector. Use when the user wants to find, inspect, preview, summarize, create, or organize Dropbox files and folders.
---

# Dropbox

Use the Dropbox app connector for Dropbox file and folder work. Ground the target with Dropbox discovery before reading or mutating it, keep retrieval narrow, and verify writes with follow-up metadata or listing when the available tools support it.

## Workflow

1. Identify the Dropbox target from a path, file ID, folder listing, metadata lookup, or search result.
2. Prefer read-only discovery before fetches, previews, or writes.
3. Use the narrowest tool that matches the request: search for text discovery, metadata or folder listing for navigation, preview for inspect/open tasks, and fetch for extracted file text.
4. Before Dropbox writes, summarize the exact mutation plan and get explicit user confirmation when the tool or request changes Dropbox state.
5. After a successful write, report the returned Dropbox path or ID and verify the result when practical.

## Internal Skill Guidance

- **Path and ID discovery:** For `list_folder`, `get_file_metadata`, `file_preview`, and `fetch`, use paths or IDs returned by Dropbox discovery calls; when a target is not found or cannot be resolved, rediscover it instead of retrying a guessed locator.
- **Search vs. navigation:** Use `search.query` for text terms, not known Dropbox paths; use folder listing or metadata lookup when the user provides a path or file ID.
- **Fetch eligibility:** Call `fetch` only on files, and avoid full extraction for files known to be too large, unsupported, or not text-extractable; use metadata/preview or report the limitation instead of repeating the failed fetch.
- **Create conflicts:** Before `create_file` or `create_folder`, inspect the intended destination when practical; if it already exists, reuse it, select a new name, or obtain overwrite intent rather than retrying the same create.

## Write Safety

- Treat file creation, folder creation, sharing, moves, renames, and deletes as Dropbox mutations.
- Do not widen sharing or overwrite an existing target unless the user clearly asked for that outcome.
- Preserve returned `id:` and `ns:` locators for follow-on Dropbox calls instead of reconstructing paths manually.
