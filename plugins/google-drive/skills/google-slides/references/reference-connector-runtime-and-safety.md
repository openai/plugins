# Connector Runtime And Safety

When to read: always, before any Slides write.

## Runtime Attachment

1. Confirm the target working presentation URL or id and attach to that exact deck through the available Google Slides connector/app tools.
2. Use `node_repl` for source processing or helper code, not for connector calls.
3. Connector calls are separate from `node_repl`; do not use embedded-runtime helper snippets or assumed global connector bindings.
4. Browser Use is not required for Slides editing. Use connector reads and thumbnails.
5. Reuse the resolved presentation id when available, but re-confirm it before writes.
6. Treat target deck identity as a hard precondition for connector writes.

## Required Write-Batch Check

1. Confirm the intended working deck URL or presentation id.
2. Re-read enough connector metadata to verify the deck identity.
3. Resolve the target slide object id and target page elements from fresh connector data.
4. Only then issue the connector write batch.

## Safety And Recovery

1. Use live object IDs from the current deck state. Never guess IDs.
2. Prefer one small write pass followed by verification over broad speculative rewrites.
3. If edits land in the wrong place, stop and re-resolve the deck, slide, and object IDs before writing again.
4. If formatting drift appears after a write, patch locally instead of redoing the whole deck.
5. If the connector is unavailable, this plugin cannot safely edit the live Slides deck. Stop and report the runtime constraint.
6. Do not call the connector read-only unless a write-capability check in the current session proves it.
7. If a referenced deck is a template or source deck that should be preserved, create a copy before editing.
