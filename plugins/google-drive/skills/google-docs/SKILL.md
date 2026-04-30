---
name: google-docs
description: Documents-first net-new Google Docs creation plus connector-first Google Docs editing in local Codex plugin sessions, with target-document checks, connector-readback verification, and reference routing for formatting, citations, tables, and write-safety.
---

# Google Docs

Use this skill for Google Docs work in Codex local-plugin sessions where Browser Use and rendered visual inspection are unavailable.
Net-new Google Doc deliverables must be authored through `[@documents](plugin://documents@openai-primary-runtime)` as local `.docx` files first, then uploaded as native Google Docs.

## Purpose Of This File

This file is intentionally minimal and only covers:

1. connector loading and runtime boundaries in the Codex local-plugin environment
2. stateful operation and mandatory routing to reference files

All formatting, citation, table, and production rules live in `references/`.
Latency is not a constraint for this skill, so always read the relevant reference files before performing the task.

## Default Routing

Use this routing:

1. Net-new Google Docs creation: use `[@documents](plugin://documents@openai-primary-runtime)` to create a local `.docx` first, including that skill's DOCX QA workflow.
2. Upload and convert the `.docx` into Drive as a native Google Docs document. Read `references/reference-import-docx-to-native-docs.md`.
3. If the Documents plugin is unavailable, do not create the net-new Google Doc directly. Report that the required local Documents authoring path is unavailable.
4. Existing Google Docs reads, summaries, edits, comments, and template-preserving modifications: use Google Docs connector or app tools directly.

Do not reference the local `.docx` in the final answer after successful native import. The final answer includes the Google Docs link only.

## Runtime Model

This plugin is for the local Codex plugin environment.

1. Use Google Docs connector or app tools directly from Codex when they are available.
2. Keep connector calls separate from any local helper processing.
3. Do not use embedded-runtime helper snippets or assumed global connector bindings.
4. This environment has no Browser Use or rendered visual inspection. Do not require browser foregrounding, screenshots, cursor placement, rendered-page scans, or visible-tab checks.

## Stateful Operation

Maintain working state for the active document task instead of re-deriving context from scratch after every step.
Keep the target URL, document id, `tabId`, source materials, resolved sections or tables, live indexes, write batches, and verification status current as the task progresses.
Refresh that state before connector writes when source gathering, document switches, connector errors, or runtime resets could make it stale.

## Non-Negotiable Output Invariant

Inserted or edited content must match the surrounding document's existing structure and connector-observable presentation closely enough that it should read as native template content.
This is launch-blocking, not cosmetic. Treat missing section hierarchy, mismatched heading level, font family, font size, bolding, link coverage, table styling, or template-shape drift visible in connector data as a failed output that must be corrected before handoff. Do not claim rendered visual verification when the model cannot see the document.

For presentation-oriented documents, structural completeness is not enough. A document can have all requested sections, headings, tables, and placeholders resolved while still being too dense, monotonous, or hard to scan. Treat readability, hierarchy, and appropriate use of visual devices as part of completion, not as optional polish.

## Canonical Workflow Bias

Prefer one simple proven workflow over a large tree of recovery branches.
When a task matches a known successful pattern, follow that pattern directly instead of re-evaluating every possible insertion or fallback path.
Do not let accumulated edge-case guardrails turn a straightforward document task into a long blocker-analysis exercise.
For net-new Google Doc deliverables, follow Default Routing first.
For existing document editing tasks and follow-on edits after a DOCX import, prefer this general sequence when viable:

1. gather the required source material
2. create or attach to the destination document
3. establish the heading and section skeleton
4. fill the core text or structured content
5. decide which content should stay prose, become a table, become a short card, or become a compact visual block
6. verify and normalize formatting
7. add secondary elements such as tables, links, or connector-supported figures only after the core structure is stable
8. stop once the document is clean, complete, and scannable

For any secondary element that cannot be verified through connector reads, either use a connector-supported path with readback or clearly state the verification limit.

If a simple verified workflow is viable, use it. Do not drift into speculative alternate paths.

## Release-Blocker Checklist

Before final handoff, explicitly verify these with connector readback:

1. every new or edited table has the intended rows, columns, cell text, table anchor, style requests, and column widths where the connector exposes them
2. every new or edited heading, label, and body block matches surrounding connector-visible style fields such as named style, font family, font size, bolding, links, and list state
3. every inserted figure or image uses a connector-supported insertion path and is present in connector readback; if rendered placement cannot be inspected, say so plainly
4. when available, export the document as `text/html` through Google Drive and use the generated markup/CSS as a rendered-structure proxy for heading tags, font families, font sizes, table cells, fills, widths, and paragraph ordering
5. the document is not relying on one repeated structure everywhere; for example, a long run of similar tables or identical header colors should be treated as a design smell unless the source template clearly calls for it
6. if neither connector readback nor HTML export exposes enough data to prove a rendered visual property, do not assert that property as verified

If any check fails, the task is not complete.
If a simple known-good workflow is available and the run instead collapses into repeated fallback experiments, the task is also not complete.

## Required Read Order (No Skips)

Before any content write or edit operation:

If Default Routing uses `[@documents](plugin://documents@openai-primary-runtime)`:

1. Read the `[@documents](plugin://documents@openai-primary-runtime)` plugin skill.
2. Read `references/reference-import-docx-to-native-docs.md`.

If Default Routing uses connector edit workflow:

1. Read `references/reference-connector-runtime-and-safety.md`.
2. Read `references/reference-foreground-guard.md` for target-document identity checks.
3. Read `references/reference-request-shapes-and-write-safety.md`.
4. Read every task-specific file from the matrix below.
5. If the task spans multiple categories, read all matching files.
6. If uncertain, read every file in `references/`.

Do not execute content edits until the required references are read in the current turn.

## Connector Load Checklist

1. Confirm the exact target Google Doc URL or document id and attach to that exact doc through the available Google Docs connector/app tools.
2. If the user only gives a title or title keywords, use the connector/app search path to identify candidate docs before asking for a URL.
3. Resolve and record the document id and, if present, the working `tabId`.
4. Treat target-document identity as a hard precondition for connector writes.
5. Before each edit pass, identify the section or range being edited through connector reads.
6. Before every connector write batch, re-read `references/reference-foreground-guard.md` and re-confirm the target document id, URL, and `tabId` when applicable.
7. Do not use Browser Use, visible tab checks, or rendered-page inspection as requirements in this environment.
8. Read via connector first, choosing the narrowest current Google Docs action that fits the task:
   - use `get_document_text` when paragraph text and indexes are enough
   - use `get_document` when full structure, styles, tabs, or non-text elements matter
   - use `find_document_text_range` when exact source text can anchor the target range
   - use `get_paragraph_range` or `get_document_paragraph_range` when an index must expand to paragraph boundaries
   - use `get_tables` before editing or rebuilding table content
9. Re-read after substantial edits so later writes use live indexes and current structure.
10. If the document has tabs, resolve the correct `tabId` and carry it through all reads and writes.
11. If the source doc is a template, create a copy before any edits.
12. Do not claim the connector is unavailable, read-only, or blocked unless the current session has already established that through actual capability evidence in this run.

## Task To Reference Map

| Task area | Required reference file |
| --- | --- |
| Runtime attachment, section targeting, safety, and recovery | `references/reference-connector-runtime-and-safety.md` |
| Importing a locally created `.docx` into native Google Docs | `references/reference-import-docx-to-native-docs.md` |
| Confirming the target Google Doc before every write batch | `references/reference-foreground-guard.md` |
| Request objects, tab-aware calls, range-safe writes, sampling the local style baseline, and connector-readback verification when style metadata is incomplete | `references/reference-request-shapes-and-write-safety.md` |
| Header and prompt structure, including bolding the question being answered and matching local heading/body typography | `references/reference-headings-and-question-format.md` |
| Response structure, list behavior, and one-idea-per-bullet formatting | `references/reference-response-and-list-format.md` |
| Citation formatting and hyperlink requirements | `references/reference-citations-and-hyperlinks.md` |
| Native table creation, local table-style matching, population, styling, and acceptance checks | `references/reference-table-formatting-deep-dive.md` |
| Figures, diagrams, image preparation, insertion, and figure-block placement | `references/reference-figures-and-image-insertion.md` |
| Section completeness, source-list formatting, typography consistency, connector-observable comparison, and final production pass | `references/reference-section-completeness-and-final-pass.md` |
