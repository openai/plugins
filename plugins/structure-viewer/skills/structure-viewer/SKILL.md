---
name: structure-viewer
description: Open and inspect local molecular structure files in Codex's interactive Mol* rich viewer. Use when the user asks to open, visualize, inspect, or interact with PDB, CIF, mmCIF, MOL, or SDF artifacts.
---

# Molecular Structure Viewer

Use this skill when a user wants to inspect a molecular structure visually inside Codex.

## Opening Workflow

The plugin contributes native file-pane preview and a model-visible inline MCP App for supported molecular structure files. The model should not read or copy structure bytes into the conversation merely to open the viewer.

1. Resolve the user's intended local molecular structure file. Prefer the explicitly named path. If the request is ambiguous, search only the relevant workspace and ask a short clarification question when multiple plausible structures remain.
2. Confirm that the file is a supported PDB, CIF, mmCIF, MOL, or SDF artifact.
3. Call `structure.open_from_chat` with the exact absolute local path whenever available. A workspace-relative path works only when the MCP host exposes active roots. The tool opens the Mol* app inline beneath its tool-call row and returns a `viewerSessionId` in `structuredContent`; use that ID immediately for same-turn `structure.control_viewer` calls instead of waiting for later model context.
4. After success, make the embedded viewer card the only opening affordance in the reply. Say: `The embedded Molecular Structure Viewer is ready. Click or expand the Structure open from chat tool card above to view it. You can use Open in side pane, or ask me to move or control the viewer.` Do not repeat or code-format the file name or path, say that the path was opened, or imply that a path or file citation is clickable; citation clicks can open raw text instead.
5. After the Mol* app opens, answer follow-up questions from the viewer's model context. Re-read the current viewer context before answering questions about the displayed structure, representation, coloring, focused ligand, chain, residue, or selection.

Do not call the app-only `structure.open` tool directly from chat. It is reserved for Codex's native file-preview host because it requires an opaque `codex-resource://` URI that only the host can mint. Use `structure.open_from_chat` for chat requests.

If the user asks to move, send, pin, or open an already-mounted viewer in the right pane, do not call `structure.open_from_chat` again. Use `structure.control_viewer` with the `viewerSessionId` from current model context and action `set_display_mode`; use `fullscreen` for the side pane and `inline` for chat. The in-view **Open in side pane** and **Return to chat** buttons provide the same standard MCP App display-mode behavior.

The visible **Measure** control opens the molecule analysis panel, where the user can choose any two polymer residues, including residues on different chains, and inspect the closest-heavy-atom distance and atom pair without asking the model. Ligand contact controls and cutoff provenance are available in the same panel.

## Viewer Control Workflow

Use `structure.control_viewer` only for the active mounted viewer and only with the `viewerSessionId` from current model context. Residue identifiers use author chain and author residue numbering; include an insertion code when present.

Run mounted-viewer control in the same conversation that contains the viewer. Do not delegate these actions to a subagent, inspect the webview through browser or DevTools automation, or search the source tree for UI state. The app's current model context and `structure.control_viewer` are the supported control path. When an opening request also includes control actions, open the viewer first, re-read its model context, and then call `structure.control_viewer` directly for each requested action.

- `focus_residue`, `select_residue_range`, `select_chain`, or `select_residues`: focus one author-numbered residue or select a numeric range, a whole polymer chain, or a noncontiguous residue set. Use the exact author chain, residue number, and insertion code from model context.
- `clear_selection`: clear the current structure selection and inspector focus.
- `focus_ligand`: focus a ligand by component ID and optional chain.
- `show_ligand_contacts`: return and display polymer residues within a 2-8 Å cutoff using closest heavy-atom Euclidean distance.
- `measure_residue_distance`: measure the closest heavy-atom distance between two author-numbered residues.
- `set_representation` or `set_color`: change the live Mol* representation or color mode.
- `set_view_options`: explicitly set a dark or light background and toggle hydrogens, side chains or bases, animation, and the molecule inspector.
- `set_display_mode`: move the live viewer between `fullscreen` and `inline`.
- `reset_view`: reset the Mol* camera.

After a successful control or measurement action, state exactly what changed and preserve the method and cutoff provenance. Do not claim that a request succeeded when the tool reports `applied: false`.

## Supported Artifacts

- `.pdb` for PDB text coordinates.
- `.cif` and `.mmcif` for CIF/mmCIF-style coordinate text.
- `.mol` for MDL MOL small-molecule records.
- `.sdf` for MDL SD files supported by Mol*.

## Boundaries

- Do not read, inline, truncate, or summarize file contents merely to open the viewer.
- Do not pass a workspace path, `file://` URI, or fabricated `codex-resource://` URI to `structure.open`.
- When the MCP host exposes active local roots, `structure.open_from_chat` confines both relative and absolute paths to those roots. When roots are unavailable, it requires an exact absolute local path.
- `structure.open_from_chat` accepts only supported files.
- Do not infer the user's current selection from the source file after the app is open. Use the viewer context because the user may have rotated the model, focused a ligand, changed representations, or selected residues interactively.
- Do not call the automatically suggested ligand the biologically relevant ligand without evidence. It is a convenience ranking that excludes solvent and common crystallization additives; the user can choose another ligand.
- Report ligand contacts and residue measurements as coordinate-derived closest-heavy-atom distances, not inferred bonds or energetic interactions.
- Prefer author chain, residue number, and insertion code in user-facing residue references. Keep label numbering available for provenance.

## Follow-Up Questions

When answering from the mounted viewer context, prioritize the literal current state before adding biological interpretation. Useful context includes the active file, coordinate format, experiment and resolution metadata, model count, chain inventory, author and label residue coordinates, molecular components, current representation, color mode, selected ligand, distance cutoff, contact list, selected residues, measurements, and the exact focus or selection state.
