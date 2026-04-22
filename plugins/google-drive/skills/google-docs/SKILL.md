---
name: google-docs
description: Connector-first Google Docs editing in local Codex plugin sessions with no Browser Use, node_repl-aware runtime boundaries, target-document checks, connector-readback verification, and reference routing for formatting, citations, tables, and write-safety.
---

# Google Docs

Use this skill for connector-first editing of Google Docs in Codex local-plugin sessions where Browser Use and rendered visual inspection are unavailable.

## Purpose Of This File

This file is intentionally minimal and only covers:

1. connector loading and runtime boundaries in the Codex `node_repl` world
2. mandatory routing to reference files

All formatting, citation, table, and production rules live in `references/`.
Latency is not a constraint for this skill, so always read the relevant reference files before performing the task.

## Runtime Model

This plugin is for the local Codex plugin environment.

1. Use Google Docs connector or app tools directly from Codex when they are available.
2. Use `node_repl` only for source processing or small JavaScript utilities that are not connector calls.
3. Do not use embedded-runtime helper snippets or assumed global connector bindings.
4. Connector tools are not called from inside `node_repl`. Treat connector calls and `node_repl` helper work as separate execution surfaces.
5. This environment has no Browser Use or rendered visual inspection. Do not require browser foregrounding, screenshots, cursor placement, rendered-page scans, or visible-tab checks.

## Non-Negotiable Output Invariant

Inserted or edited content must match the surrounding document's existing structure and connector-observable presentation closely enough that it should read as native template content.
This is launch-blocking, not cosmetic. Treat missing section hierarchy, mismatched heading level, font family, font size, bolding, link coverage, table styling, or template-shape drift visible in connector data as a failed output that must be corrected before handoff. Do not claim rendered visual verification when the model cannot see the document.

For presentation-oriented documents, structural completeness is not enough. A document can have all requested sections, headings, tables, and placeholders resolved while still being too dense, monotonous, or hard to scan. Treat readability, hierarchy, and appropriate use of visual devices as part of completion, not as optional polish.

## Canonical Workflow Bias

Prefer one simple proven workflow over a large tree of recovery branches.
When a task matches a known successful pattern, follow that pattern directly instead of re-evaluating every possible insertion or fallback path.
Do not let accumulated edge-case guardrails turn a straightforward document task into a long blocker-analysis exercise.
For document-creation and document-editing tasks, prefer this general sequence when viable:

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

1. Read `references/reference-connector-runtime-and-safety.md`.
2. Read `references/reference-foreground-guard.md` for target-document identity checks.
3. Read `references/reference-request-shapes-and-write-safety.md`.
4. Read every task-specific file from the matrix below.
5. If the task spans multiple categories, read all matching files.
6. If uncertain, read every file in `references/` except the archive.

Do not execute content edits until the required references are read in the current turn.

## Connector Load Checklist

1. Confirm the exact target Google Doc URL and attach to that exact doc through the available Google Docs connector/app tools.
2. Resolve and record the document id and, if present, the working `tabId`.
3. Treat target-document identity as a hard precondition for connector writes.
4. Before each edit pass, identify the section or range being edited through connector reads.
5. Before every connector write batch, re-read `references/reference-foreground-guard.md` and re-confirm the target document id, URL, and `tabId` when applicable.
6. Do not use Browser Use, visible tab checks, or rendered-page inspection as requirements in this environment.
7. Read via connector first, using the current tool names for the Google Docs actions:
   - get document text
   - get full document structure
8. If the document has tabs, resolve the correct `tabId` and carry it through all reads and writes.
9. If the source doc is a template, create a copy before any edits.
10. Do not claim the connector is unavailable, read-only, or blocked unless the current session has already established that through actual capability evidence in this run.

## Task To Reference Map

| Task area | Required reference file |
| --- | --- |
| Runtime attachment, section targeting, safety, and recovery | `references/reference-connector-runtime-and-safety.md` |
| Confirming the target Google Doc before every write batch | `references/reference-foreground-guard.md` |
| Request objects, tab-aware calls, range-safe writes, sampling the local style baseline, and connector-readback verification when style metadata is incomplete | `references/reference-request-shapes-and-write-safety.md` |
| Header and prompt structure, including bolding the question being answered and matching local heading/body typography | `references/reference-headings-and-question-format.md` |
| Response structure, list behavior, and one-idea-per-bullet formatting | `references/reference-response-and-list-format.md` |
| Citation formatting and hyperlink requirements | `references/reference-citations-and-hyperlinks.md` |
| Native table creation, local table-style matching, population, styling, and acceptance checks | `references/reference-table-formatting-deep-dive.md` |
| Figures, diagrams, image preparation, insertion, and figure-block placement | `references/reference-figures-and-image-insertion.md` |
| Section completeness, source-list formatting, typography consistency, connector-observable comparison, and final production pass | `references/reference-section-completeness-and-final-pass.md` |

## Archive

Historical context only:

- `references/reference-full-skill-archive-2026-03-11.md`
