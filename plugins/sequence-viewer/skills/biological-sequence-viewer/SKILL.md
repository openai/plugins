---
name: biological-sequence-viewer
description: Open and inspect local biological sequence and multiple-sequence-alignment files in Codex's interactive rich viewer. Use when the user asks to open, visualize, inspect, or interact with FASTA, FASTQ, GenBank, EMBL, aligned FASTA, CLUSTAL, Stockholm, A2M, A3M, MSF, PHYLIP, NEXUS, or PIR artifacts.
---

# Biological Sequence & Alignment Viewer

Use this skill when a user wants to inspect a biological sequence or multiple sequence alignment visually inside Codex.

## Opening Workflow

The plugin contributes native file-pane preview and a model-visible inline MCP App for supported sequence and alignment files. The model should not read or copy file bytes into the conversation merely to open the viewer.

1. Resolve the user's intended local file. Prefer the explicitly named path. If the request is ambiguous, search only the relevant workspace and ask a short clarification question when multiple plausible artifacts remain.
2. Confirm that the file is a supported biological sequence or alignment artifact.
3. Call `sequence.open_from_chat` with the exact absolute local path whenever available. A workspace-relative path works only when the MCP host exposes active roots. The tool opens the rich app inline beneath its tool-call row and returns a `viewerSessionId` in `structuredContent`; use that ID immediately for same-turn `sequence.control_viewer` calls instead of waiting for later model context.
4. After success, make the embedded viewer card the only opening affordance in the reply. Say: `The embedded Biological Sequence & Alignment Viewer is ready. Click or expand the Sequence open from chat tool card above to view it. You can use Open in side pane, or ask me to move or control the viewer.` Do not repeat or code-format the file name or path, say that the path was opened, or imply that a path or file citation is clickable; compound alignment suffixes may not become clickable and citation clicks can open raw text instead.
5. After the app opens, answer follow-up questions from the viewer's model context. Re-read the current viewer context before answering questions about the current mode, selection, focused record, alignment column, or visible metrics.

Do not call the app-only `sequence.open` tool directly from chat. It is reserved for Codex's native file-preview host because it requires an opaque `codex-resource://` URI that only the host can mint. Use `sequence.open_from_chat` for chat requests.

If the user asks to move, send, pin, or open an already-mounted viewer in the right pane, do not call `sequence.open_from_chat` again. Use `sequence.control_viewer` with the `viewerSessionId` from current model context and action `set_display_mode`; use `fullscreen` for the side pane and `inline` for chat. The in-view **Open in side pane** and **Return to chat** buttons provide the same standard MCP App display-mode behavior.

## Viewer Control Workflow

Use `sequence.control_viewer` only for the active mounted viewer and only with the `viewerSessionId` published in its current model context. Coordinates are 1-based.

Run mounted-viewer control in the same conversation that contains the viewer. Do not delegate these actions to a subagent, inspect the webview through browser or DevTools automation, or search the source tree for UI state. The app's current model context and `sequence.control_viewer` are the supported control path. When an opening request also includes control actions, open the viewer first, re-read its model context, and then call `sequence.control_viewer` directly for each requested action.

- `set_display_mode`: move the live viewer between `fullscreen` and `inline`.
- `set_mode`: switch between Sequence and Alignment when the artifact supports both.
- `set_sequence_record`: switch to an exact record ID, source label, or unambiguous description from the structured `sequenceRecords` context.
- `focus_sequence_coordinate`, `select_sequence_range`, or `select_sequence_feature`: focus coordinates, select a range, or pin an annotated feature. Prefer exact feature IDs from structured `features` context, but a unique case-insensitive feature type, label, or qualifier value such as `CDS` or `kinase domain` also works. If a biological selector is ambiguous, use the returned exact candidate ID; include `record` when the file contains multiple records.
- `search_sequence` and `navigate_sequence_search_hit`: search the displayed sequence, including reverse-complement matches for nucleic acid records, and move through the resulting hits.
- `set_sequence_view_options`: choose a molecule-compatible residue palette, wrap width, and feature, translation, or FASTQ-quality visibility.
- `clear_sequence_selection`: clear the active sequence range and pinned feature.
- `focus_alignment_cell`, `focus_alignment_reference_coordinate`, or `select_alignment_columns`: focus an alignment row/column, map an ungapped active-reference coordinate into the alignment, or select a 1-based inclusive column range.
- `set_alignment_reference`: use `consensus`, `none`, or an exact row ID or label.
- `search_alignment` and `navigate_alignment_search_hit`: search the alignment motif view and move through the resulting hits.
- `filter_alignment_rows`, `set_alignment_row_visibility`, or `show_all_alignment_rows`: filter rows by label or description, hide or show exact row IDs or labels, or restore every row.
- `set_alignment_view_options`: set molecule interpretation, analysis and search scopes, cell width, color mode, residue palette, annotation tracks, identical-as-dots rendering, and RNA structure overlays. Use modality-compatible colors and palettes.
- `clear_alignment_selection` or `reset_alignment_view`: clear the current focus/selection or restore default alignment controls.
- `compute_alignment_guide_tree`: compute an exploratory UPGMA Newick guide tree from uncorrected alignment p-distance.

After a successful control action, briefly say what changed. Do not claim that a requested state changed when the tool reports `applied: false`.

## Supported Artifacts

- Sequence-first files: FASTA, FASTQ, GenBank, EMBL, and common plain biological sequence suffixes.
- Alignment-first files: aligned FASTA, AFA, CLUSTAL, Stockholm, A2M, A3M, MSF, PHYLIP, NEXUS, and PIR.
- Ambiguous rectangular FASTA files open in the combined viewer with an in-view Sequence / Alignment mode choice.

## Boundaries

- Do not read, inline, truncate, or summarize file contents merely to open the viewer.
- Do not pass a workspace path, `file://` URI, or fabricated `codex-resource://` URI to `sequence.open`.
- When the MCP host exposes active local roots, `sequence.open_from_chat` confines both relative and absolute paths to those roots. When roots are unavailable, it requires an exact absolute local path.
- `sequence.open_from_chat` accepts only supported files.
- Do not infer the user's current selection from the source file after the app is open. Use the viewer context because the user may have changed modes, rows, columns, or selections interactively.
- Treat FASTQ summary quality as Phred+33 unless the source explicitly establishes another encoding.
- Treat the built-in UPGMA tree as an exploratory guide tree, not publication-grade phylogenetic inference.
- Preserve compound GenBank and EMBL feature segments; do not describe the gaps between joined segments as part of the feature.

## Follow-Up Questions

When answering from the mounted viewer context, prioritize the literal current state before adding biological interpretation. Useful context includes the active file, current Sequence or Alignment mode, record and feature inventories, selected record, selected residue range, six-frame translation, aggregate FASTQ QC, exact compound feature segments, selected alignment column range, visible and hidden row state, row filters, per-row residues for selected columns, conservation metrics, guide-tree provenance, search results, and focused annotations.
