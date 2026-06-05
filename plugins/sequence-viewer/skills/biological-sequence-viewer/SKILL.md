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
3. Call `sequence.open_from_chat` with the exact absolute local path whenever available. A workspace-relative path works only when the MCP host exposes active roots. The tool opens the rich app inline beneath its tool-call row.
4. After success, make the embedded viewer card the only opening affordance in the reply. Say: `The embedded Biological Sequence & Alignment Viewer is ready. Click or expand the Sequence open from chat tool card above to view it. Use Open in side pane inside the viewer to move the same live viewer to the right pane.` Do not repeat or code-format the file name or path, say that the path was opened, or imply that a path or file citation is clickable; compound alignment suffixes may not become clickable and citation clicks can open raw text instead.
5. After the app opens, answer follow-up questions from the viewer's model context. Re-read the current viewer context before answering questions about the current mode, selection, focused record, alignment column, or visible metrics.

Do not call the app-only `sequence.open` tool directly from chat. It is reserved for Codex's native file-preview host because it requires an opaque `codex-resource://` URI that only the host can mint. Use `sequence.open_from_chat` for chat requests.

If the user asks to move, send, pin, or open an already-mounted viewer in the right pane, do not call `sequence.open_from_chat` again. Tell them to click **Open in side pane** inside the existing viewer. That control moves the same live viewer and preserves its current mode, focus, selection, and alignment state. Chat cannot directly target an already-mounted viewer instance; inside the right pane, **Return to chat** moves it back inline.

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

## Follow-Up Questions

When answering from the mounted viewer context, prioritize the literal current state before adding biological interpretation. Useful context includes the active file, current Sequence or Alignment mode, selected record, selected residue range, selected alignment column range, per-row residues for selected columns, conservation metrics, search results, and focused annotations.
