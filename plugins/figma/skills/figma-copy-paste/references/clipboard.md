# Native Clipboard Transfer

## Copy

If the Computer plugin reports that the device is locked, stop before Copy, verify the destination is unchanged, and ask the user to unlock it. Never bypass the OS lock.

Before Copy and Paste, confirm Computer can act on the Figma window. If it cannot, reactivate the exact Figma app or browser tab with Computer and retry once; then stop without mutating the destination if the window remains unavailable.

For a FigJam source (`/board/`), read [figjam.md](figjam.md) before selecting the node.

For a Design source opened in Dev Mode (`m=dev` or Inspect), switch to Design mode before selecting or copying. Dev Mode may serialize properties or a different focused node even when the pasteboard contains `figmeta`.

1. Open the exact node deep link and use Computer to select the exact Layers-panel row, not canvas text or Dev Mode inspector content. Browser accessibility/DOM may be used when available, but is optional.
2. Re-check that the selected URL still contains the expected node ID, and that the properties panel shows the expected layer name and dimensions; names such as `Window` are not unique.
3. Focus Figma and invoke Copy through Computer's real app keypress. Browser-scoped `press` events do not count as OS-level Copy.
4. On macOS, validate the host pasteboard:

   ```bash
   scripts/inspect_figma_clipboard.py \
     --expect-file-key FILE_KEY \
     --expect-node-id NODE_ID \
     --wait-seconds 5 \
     --require-match
   ```

   Run with host/escalated access if a sandboxed call sees an empty pasteboard. Browser-scoped clipboard inspectors are not authoritative.
   On Windows, where this host validator is unavailable, record clipboard validation as unavailable and continue only after confirming the exact source selection and capturing the destination baseline. Treat any unexpected destination delta as failure and reset immediately.
5. If validation returns visible child text instead of `figmeta`, treat it as a focus failure. Click the exact Layers row again before retrying. Do not repeat Copy with unchanged focus.
6. If validation still fails, invoke Figma's top Edit-menu `Copy`, then poll again. Use the selected layer row's context-menu `Copy` as the final fallback and poll once more.
7. If all three attempts fail for a nested node in a view-only source, read [view-only-nested.md](view-only-nested.md). Otherwise report a safe copy failure. Do not recreate or request edit access unless the user asks.

## Paste

1. Focus an empty destination canvas area and invoke OS-level Paste.
2. Do not use canvas `Paste here`; it has stalled in automation.
3. Wait up to 20 seconds for `Pasting…` to resolve, a variable prompt to appear, or a new node to materialize.
4. If the paste stalls, cancel or undo, verify the destination returned to its baseline, and retry the complete copy sequence once.
5. If Figma reports unpublished variables, choose `Copy variables into this file`. Otherwise preserve remote library bindings.

Track: `selected`, `copied`, `clipboard-validated`, `paste-started`, `variable-prompt`, `pasted`, `verified`, `reset`. Return the last state and timings on failure.
