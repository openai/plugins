---
name: google-docs
description: Connector-first Google Docs creation and editing in local Codex plugin sessions, with direct native create and batchUpdate workflows for simple docs, DOCX-first import for polished deliverables, target-document checks, smart chip and building-block reconstruction, connector-readback verification, and reference routing for formatting, citations, tables, and write-safety.
---

# Google Docs

Use this skill for Google Docs work in Codex local-plugin sessions.
For blank or basic native Google Docs, create the doc directly with the Google Drive connector. Use `[@documents](plugin://documents@openai-primary-runtime)` plus DOCX import only when the requested deliverable needs polished document authoring, complex layout, visual design, image/figure placement, page-level QA, branded styling, or export-quality fidelity.

## Purpose Of This File

This file is intentionally minimal and covers:

1. connector loading and runtime boundaries in the Codex local-plugin environment
2. the direct native-create route for blank and basic Google Docs
3. the DOCX-first native import route for polished or complex Google Docs
4. the direct-request workflow for existing and newly created Google Docs
5. stateful operation and mandatory routing to reference files

All formatting, citation, table, request-shape, and production rules live in `references/`.
Read only the references required for the task. For the common calendar-backed meeting-notes edit, `references/reference-meeting-notes-direct.md` is the single task reference unless the task adds tables, figures, citations, import/export, or other non-meeting-notes requirements.

## Default Routing

Use this routing:

1. Blank or basic native Google Docs creation: read `references/reference-native-create-direct.md`, call `mcp__codex_apps__google_drive._create_file` with `mime_type: "application/vnd.google-apps.document"`, and use direct Docs `batchUpdate` requests only if content is requested.
2. Polished or complex net-new Google Docs creation: use `[@documents](plugin://documents@openai-primary-runtime)` to create a local `.docx` first, explicitly selecting the `google_docs_default` design preset unless the user asked for a special, branded, or highly polished visual treatment. Then read `references/reference-import-docx-to-native-docs.md` and import with `mcp__codex_apps__google_drive_import_document` using `upload_mode: "native_google_docs"`.
3. If the Documents plugin is unavailable for a polished or complex deliverable, report that the required local Documents authoring path is unavailable. Do not block blank or basic native Google Doc creation on the Documents plugin.
4. Existing Google Docs reads, summaries, edits, comments, and template-preserving modifications: use Google Docs connector or app tools directly.

Choose the simplest creation path that can faithfully satisfy the request. The connector-native path is the default for blank docs and basic documents with plain text, headings, lists, simple links, simple tables, and supported smart chips. The DOCX-import path is the high-quality workflow for deliverables where page layout, figure generation, visual polish, export quality, or full rendered visual QA matter.

The import reference owns the exact connector action, plugin install/reinstall handling, native-conversion verification, post-import normalization, and cleanup steps. Read it before any DOCX-first Google Docs import attempt.

For DOCX-first work, local DOCX staging hygiene is mandatory. Staging must be non-user-visible and untracked from the start. Do not create DOCX builder or helper scripts with tracked file-edit tools such as `apply_patch`, and do not create helper source files in the workspace or any path surfaced by Changes Made. Prefer the Documents plugin's built-in authoring workflow or a one-shot runtime command that keeps generation code ephemeral and persists only the required `.docx`, render outputs, and scratch assets in a per-task scratch directory. After successful native import and connector readback, remove those local staging artifacts unless the user explicitly asked to keep local files. Cleanup is required as a backstop, not as the visibility control.

Do not reference the local `.docx` in the final answer after successful native import. The final answer includes the Google Docs link only.

## Capability Position

Connector-first creation and editing is the preferred path for blank docs, basic native docs, existing native Google Docs, and targeted post-import edits. It is strong for text, headings, bullets, links, simple tables, tabs, comments, supported smart chips, meeting-notes-like building-block reconstruction, and template-preserving insertions.

It is not a universal replacement for DOCX-first creation. Use DOCX-first creation for net-new polished deliverables where page layout, figure generation, export quality, or full rendered visual QA matter.

For template-preserving work, sample the nearest comparable live document structure before writing. Reproduce connector-visible structure and supported element types rather than approximating everything as plain text. For unsupported UI-only constructs, copy an existing template document or recreate the observable constituent structure; do not claim native UI building-block insertion unless connector readback proves it.

## Google Docs Default Preset

For DOCX-first Google Docs creation, `google_docs_default` is the default visual contract. Do not let the Documents skill infer `standard_business_brief`, `compact_reference_guide`, or another Word-oriented preset from the content archetype alone. The expected result is a native-feeling Google Doc after import: Arial-based typography, black title/headings/body text, simple title block, restrained spacing, real lists, and no imported Word-template chrome such as blue headings, colored callouts, dense table borders, or running header/footer furniture.

Use a different Documents preset only when the user explicitly asks for a special visual treatment, a branded document, or a more polished formal artifact than a normal Google Doc.

## Runtime Model

This plugin is for the local Codex plugin environment.

1. Use Google Docs connector or app tools directly from Codex for reads, writes, and verification.
2. Do not use code-mode bridge writes or subprocess connector writes for this skill.
3. Do not run local `gdocs_*` helper scripts to digest `get_document` output or generate `batchUpdate` request arrays.
4. Prepare request JSON directly from connector readback, source data, and the examples in `references/reference-direct-request-composition.md`.
5. Keep connector calls separate from any local helper processing, and do not use embedded-runtime helper snippets or assumed global connector bindings.
6. This environment has no Browser Use or live browser-rendered inspection. Do not require browser foregrounding, screenshots, cursor placement, live rendered-page scans, or visible-tab checks.

## Stateful Operation

Maintain working state for the active document task instead of re-deriving context from scratch after every step.
Keep the target URL, document id, `tabId`, source materials, relevant readback snippets, resolved sections or tables, live indexes, write batches, and verification status current as the task progresses.
Refresh that state before connector writes when source gathering, document switches, connector errors, or runtime resets could make it stale.

## Non-Negotiable Output Invariant

Inserted or edited content must match the surrounding document's existing structure and connector-observable presentation closely enough that it should read as native template content.
This is launch-blocking, not cosmetic. Treat missing section hierarchy, mismatched heading level, font family, font size, bolding, link coverage, table styling, chip type, or template-shape drift visible in connector data as a failed output that must be corrected before handoff. Do not claim rendered visual verification from connector readback or HTML export alone.

When Google Drive PDF export and local PDF page rasterization are available, use the PDF-export visual QA workflow in `references/reference-pdf-export-visual-qa.md` after connector readback for layout-sensitive work. That workflow can verify exported Google Docs PDF pages for clipping, overlap, page breaks, table fit, and figure placement. If PDF export or raster review is unavailable, state the limitation plainly and do not imply rendered visual QA passed.

For presentation-oriented documents, structural completeness is not enough. A document can have all requested sections, headings, tables, and placeholders resolved while still being too dense, monotonous, or hard to scan. Treat readability, hierarchy, and appropriate use of visual devices as part of completion, not as optional polish.

## Canonical Workflow Bias

Prefer one simple proven workflow over a large tree of recovery branches.
When a task matches a known successful pattern, follow that pattern directly instead of re-evaluating every possible insertion or fallback path.
Do not let accumulated edge-case guardrails turn a straightforward document task into a long blocker-analysis exercise.
For net-new Google Doc requests, follow Default Routing first: connector-native for blank/basic docs, DOCX-first for polished/complex deliverables.
For existing document editing tasks, connector-created docs with content, and follow-on edits after a DOCX import, use direct connector `batchUpdate` request composition when viable.

## Direct-Request Workflow

For connector-created docs with content, existing document editing tasks, and follow-on edits after a DOCX import, use this sequence when viable:

1. Gather the required source material.
2. Create or attach to the destination document.
3. Resolve the exact destination `documentId`, URL, and `tabId` if tabs are present.
4. Read the destination through the connector. Use full `get_document` when structure, styles, tabs, tables, chips, or building-block-like content matter.
5. Make compact working notes from the connector response: target section ranges, relevant paragraph start/end indexes, element types, paragraph styles, text styles, table coordinates, list state, and revision id.
6. Sample the local template shape, including paragraph styles, list state, tables, links, and supported chip element types.
7. Compose the smallest clear `batchUpdate` request batch directly in the connector call. Split large or fragile edits into verified batches.
8. Use `write_control.requiredRevisionId` when the write is based on a fresh revision id and collaborator conflicts should fail fast.
9. Re-read the edited area after each substantial write, then continue from live indexes.
10. Verify and normalize formatting, links, chips, tables, and headings before final handoff.

For any secondary element that cannot be verified through connector reads, either use a connector-supported path with readback or clearly state the verification limit.

If a simple verified workflow is viable, use it. Do not drift into speculative alternate paths.

## Meeting-Notes Fast Path

For requests like "add meeting notes for today's/tomorrow's meeting from my calendar":

1. Read only `references/reference-meeting-notes-direct.md` unless the task adds tables, figures, citations, import/export, or other non-meeting-notes requirements.
2. Follow that reference directly; it owns Calendar lookup, Meeting notes shape, empty placeholders, attendee chips, declined-attendee styling, and fast connector readback.
3. Do not export HTML or PDF for this text-only fast path. Connector readback is the verification surface for chips, bullets, headings, and target identity.

## Release-Blocker Checklist

Before final handoff, explicitly verify these with connector readback:

1. every new or edited table has the intended rows, columns, cell text, table anchor, style requests, and column widths where the connector exposes them
2. every new or edited heading, label, and body block matches surrounding connector-visible style fields such as named style, font family, font size, bolding, links, and list state; imported net-new Docs should read back as Arial-based, black-text documents without obvious blue-heading or Word-template residue
3. every new or edited smart chip or building-block-like region preserves connector-visible element types where supported: `dateElement`, `person`, and `richLink`
4. every meeting-notes-like block was composed from sampled peer structure and `references/reference-meeting-notes-direct.md`
5. every inserted figure or image uses a connector-supported insertion path and is present in connector readback; if rendered placement cannot be inspected, say so plainly
6. the document is not relying on one repeated structure everywhere; for example, a long run of similar tables or identical header colors should be treated as a design smell unless the source template clearly calls for it
7. for layout-sensitive work, complete `references/reference-section-completeness-and-final-pass.md` and `references/reference-pdf-export-visual-qa.md` as applicable; if connector readback, HTML export, and PDF-export visual QA do not prove a rendered visual property, do not assert that property as verified

If any check fails, the task is not complete.
If a simple verified workflow is viable, use it. Do not drift into speculative alternate paths.

For connector-native creation and existing Google Doc edits, the following are workflow failures unless the user explicitly requested that export format for a separate deliverable:

1. using Drive `fetch` or plain-text/HTML export as the primary structure source instead of connector reads
2. invoking a non-connector write path for this skill, including code-mode bridge writes, nested Codex connector writes, or local `gdocs_*` helper scripts
3. claiming a script/planner/builder path was used
4. approximating supported chips as plain text when `insertDate`, `insertPerson`, or `insertRichLink` can express them

## Required Read Order

Before any Google Docs creation, content write, or edit operation:

If Default Routing uses connector-native create:

1. For a blank Google Doc, read only `references/reference-native-create-direct.md`.
2. For a basic doc with content, read `references/reference-native-create-direct.md` and `references/reference-direct-request-composition.md`.
3. Read task-specific files from the matrix below only when that task area is present.

If Default Routing uses `[@documents](plugin://documents@openai-primary-runtime)`:

1. Read the `[@documents](plugin://documents@openai-primary-runtime)` plugin skill.
2. Read `references/reference-import-docx-to-native-docs.md`.
3. For the post-import normalization pass, also read `references/reference-request-shapes-and-write-safety.md`, `references/reference-headings-and-question-format.md`, `references/reference-response-and-list-format.md`, and `references/reference-section-completeness-and-final-pass.md`.

If Default Routing uses connector edit workflow for an existing document:

1. For calendar-backed Meeting notes, read only `references/reference-meeting-notes-direct.md` unless the task clearly needs another reference.
2. For simple chip/text edits, read only `references/reference-direct-request-composition.md` unless the task clearly needs another reference.
3. For non-meeting structural edits, read `references/reference-connector-runtime-and-safety.md`, `references/reference-foreground-guard.md`, `references/reference-request-shapes-and-write-safety.md`, and `references/reference-direct-request-composition.md`.
4. For non-simple smart-chip or building-block parity work, also read `references/reference-smart-chips-and-building-blocks.md`.
5. Read other task-specific files from the matrix below only when that task area is present.
6. Before final handoff for layout-sensitive, table-heavy, figure-heavy, polished, or final-deliverable edits, read `references/reference-pdf-export-visual-qa.md`.
7. If uncertain, prefer the smallest likely relevant reference set; do not bulk-read the reference folder before a straightforward meeting-notes edit.

Do not execute creation or content edits until the required references are read in the current turn.

## Connector Load Checklist

1. Confirm the exact target Google Doc URL or document id and attach to that exact doc through the available Google Docs connector/app tools. For connector-native creation, the `_create_file` response establishes the new target document identity.
2. If the user only gives a title or title keywords for an existing doc, use the connector/app search path to identify candidate docs before asking for a URL. For a new blank/basic doc, treat the title as the new file name instead of searching for an existing doc unless the user asks to reuse one.
3. Resolve and record the document id and, if present, the working `tabId`.
4. Treat target-document identity as a hard precondition for connector writes.
5. Before each edit pass, identify the section, paragraph, table, cell, or chip range from current connector readback.
6. Before every connector write batch, apply the target-document guard: re-confirm the target document id, URL, and `tabId` from connector data. Do not re-read the guard reference file for each batch once the rule is known.
7. Do not use Browser Use, visible tab checks, or live browser-rendered inspection as requirements in this environment.
8. Use the narrowest connector read that preserves safety:
   - use full `get_document` when styles, tabs, lists, chips, tables, or building-block-like structures matter
   - use exact text/range helpers only for simple text anchors that do not involve chips or repeated sections
   - use table-specific reads before editing or rebuilding table content
9. Re-read after substantial edits so later writes use live indexes and current structure. Prefer one targeted read when it fully answers the verification question, but never fan out several paragraph/range reads against the same edited region. Use one full `get_document` when targeted reads cannot expose required chips, styles, lists, or multiple nearby paragraphs.
10. If the document has tabs, resolve the correct `tabId` and carry it through all reads and writes.
11. If the source doc is a template, create a copy before any edits.
12. Do not claim the connector is unavailable, read-only, or blocked unless the current session has already established that through actual capability evidence in this run.

## Task To Reference Map

| Task area | Required reference file |
| --- | --- |
| Calendar-backed Meeting notes, empty placeholders, attendee chips, declined-attendee styling, and fast connector readback | `references/reference-meeting-notes-direct.md` |
| Blank or basic connector-native Google Docs creation | `references/reference-native-create-direct.md` |
| Runtime attachment, section targeting, safety, and recovery | `references/reference-connector-runtime-and-safety.md` |
| Importing a locally created `.docx` into native Google Docs | `references/reference-import-docx-to-native-docs.md` |
| Confirming the target Google Doc before every write batch | `references/reference-foreground-guard.md` |
| Request objects, tab-aware calls, range-safe writes, sampling the local style baseline, and connector-readback verification when style metadata is incomplete | `references/reference-request-shapes-and-write-safety.md` |
| Preparing non-meeting direct `batchUpdate` request arrays from connector readback, including index ledgers, supported chip examples, and verification | `references/reference-direct-request-composition.md` |
| Header and prompt structure, including bolding the question being answered and matching local heading/body typography | `references/reference-headings-and-question-format.md` |
| Response structure, list behavior, and one-idea-per-bullet formatting | `references/reference-response-and-list-format.md` |
| Citation formatting and hyperlink requirements | `references/reference-citations-and-hyperlinks.md` |
| Existing smart-chip inspection, non-simple smart-chip parity, and building-block support tiers | `references/reference-smart-chips-and-building-blocks.md` |
| Native table creation, local table-style matching, population, styling, and acceptance checks | `references/reference-table-formatting-deep-dive.md` |
| Figures, diagrams, image preparation, insertion, and figure-block placement | `references/reference-figures-and-image-insertion.md` |
| Section completeness, source-list formatting, typography consistency, connector-observable comparison, and final production pass | `references/reference-section-completeness-and-final-pass.md` |
| PDF export, page rasterization, thumbnail limitations, and rendered visual QA | `references/reference-pdf-export-visual-qa.md` |
