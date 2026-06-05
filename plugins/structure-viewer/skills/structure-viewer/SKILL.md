---
name: structure-viewer
description: Open and inspect local molecular structure files in Codex's interactive Mol* rich viewer. Use when the user asks to open, visualize, inspect, or interact with PDB, CIF, mmCIF, or MOL artifacts.
---

# Molecular Structure Viewer

Use this skill when a user wants to inspect a molecular structure visually inside Codex.

## Opening Workflow

The plugin contributes native file-pane preview and a model-visible inline MCP App for supported molecular structure files. The model should not read or copy structure bytes into the conversation merely to open the viewer.

1. Resolve the user's intended local molecular structure file. Prefer the explicitly named path. If the request is ambiguous, search only the relevant workspace and ask a short clarification question when multiple plausible structures remain.
2. Confirm that the file is a supported PDB, CIF, mmCIF, or MOL artifact.
3. Call `structure.open_from_chat` with the exact absolute local path whenever available. A workspace-relative path works only when the MCP host exposes active roots. The tool opens the Mol* app inline beneath its tool-call row.
4. After success, make the embedded viewer card the only opening affordance in the reply. Say: `The embedded Molecular Structure Viewer is ready. Click or expand the Structure open from chat tool card above to view it. Use Open in side pane inside the viewer to move the same live viewer to the right pane.` Do not repeat or code-format the file name or path, say that the path was opened, or imply that a path or file citation is clickable; citation clicks can open raw text instead.
5. After the Mol* app opens, answer follow-up questions from the viewer's model context. Re-read the current viewer context before answering questions about the displayed structure, representation, coloring, focused ligand, chain, residue, or selection.

Do not call the app-only `structure.open` tool directly from chat. It is reserved for Codex's native file-preview host because it requires an opaque `codex-resource://` URI that only the host can mint. Use `structure.open_from_chat` for chat requests.

If the user asks to move, send, pin, or open an already-mounted viewer in the right pane, do not call `structure.open_from_chat` again. Tell them to click **Open in side pane** inside the existing viewer. That control moves the same live viewer and preserves its current camera, representation, focus, and selection state. Chat cannot directly target an already-mounted viewer instance; inside the right pane, **Return to chat** moves it back inline.

## Supported Artifacts

- `.pdb` for PDB text coordinates.
- `.cif` and `.mmcif` for CIF/mmCIF-style coordinate text.
- `.mol` for MDL MOL small-molecule records.

## Boundaries

- Do not read, inline, truncate, or summarize file contents merely to open the viewer.
- Do not pass a workspace path, `file://` URI, or fabricated `codex-resource://` URI to `structure.open`.
- When the MCP host exposes active local roots, `structure.open_from_chat` confines both relative and absolute paths to those roots. When roots are unavailable, it requires an exact absolute local path.
- `structure.open_from_chat` accepts only supported files.
- Do not infer the user's current selection from the source file after the app is open. Use the viewer context because the user may have rotated the model, focused a ligand, changed representations, or selected residues interactively.

## Follow-Up Questions

When answering from the mounted viewer context, prioritize the literal current state before adding biological interpretation. Useful context includes the active file, coordinate format, chain inventory, molecular components, current representation, color mode, focused ligand, selected residues, and the exact focus or selection state.
