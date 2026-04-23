---
name: google-sheets
description: Analyze and edit connected Google Sheets with range precision. Use when the user wants to create Google Sheets, find a spreadsheet, inspect tabs or ranges, search rows, plan formulas, create or repair charts, clean or restructure tables, write concise summaries, or make explicit cell-range updates.
---

# Google Sheets

Use this skill to keep spreadsheet work grounded in the exact spreadsheet, sheet, range, headers, and formulas that matter.

## Purpose Of This File

This file is intentionally minimal and only covers:

1. routing to the right spreadsheet workflow
2. connector loading and runtime boundaries
3. stateful operation and mandatory routing to reference files

Detailed editing, formula, chart, upload, and batch-update rules live in `references/`.
Latency is not a constraint for this skill, so always read the relevant reference files before performing the task.

## Runtime Model

1. Use Google Sheets connector or app tools directly from Codex when they are available.
2. Keep connector calls separate from local helper processing.
3. Do not use embedded-runtime helper snippets or assumed global connector bindings.
4. Connector tools are not called from inside local spreadsheet builders. Treat connector calls and local `.xlsx` authoring as separate execution surfaces.

## Default Routing

1. New Google Sheets creation: first check whether the `$Spreadsheets` skill is installed, then check whether `$Excel` is installed.
2. If either skill is installed, YOU MUST use the first available skill in that order to create a local `.xlsx` as a scratch workbook. After creating the local `.xlsx`, read `references/reference-upload-xlsx-to-drive.md`.
3. If neither skill is installed, create the spreadsheet directly with Google Sheets MCP.
4. Existing Google Sheets edit: use Google Sheets MCP directly.

## Stateful Operation

Maintain working state for the active spreadsheet task instead of re-deriving context from scratch after every step.
Keep the spreadsheet URL or id, sheet names, `sheetId` values, ranges, headers, formulas, validation constraints, pending write batches, and verification status current as the task progresses.
Refresh that state before connector writes when source gathering, spreadsheet switches, connector errors, or runtime resets could make it stale.

## Required Read Order (No Skips)

If Default Routing uses `$Spreadsheets` or `$Excel`:
1. Read `$Spreadsheets` or `$Excel` skills
2. Read `references/reference-upload-xlsx-to-drive.md`

If Default Routing uses connector edit workflow:

1. Read `references/reference-edit-workflow.md`.
2. Read every task-specific file from the matrix below.
3. If the task spans multiple categories, read all matching files.
4. If uncertain, read every file in `references/`.

Do not execute content edits until the required references are read in the current turn.

## Release-Blocker Checklist

Before final handoff, explicitly verify:

1. The delivered artifact is a native Google Sheet, not a kept-source `.xlsx` upload.
2. The Google Sheet title does not have a `.xlsx` suffix.
3. The final answer references only the Google Sheet link or id. Do not cite the local scratch `.xlsx` path as a deliverable.

## Connector Load Checklist

1. Confirm the exact target Google Sheet URL or spreadsheet id before editing an existing spreadsheet.
2. If the user only gives a title or title keywords, use the connector/app search path to identify candidate spreadsheets before asking for a URL.
3. Resolve and record the spreadsheet id, target sheet names, and `sheetId` values.
4. Read spreadsheet metadata before deeper reads or writes.
5. Before each edit pass, identify the exact sheet, range, headers, formulas, and validation constraints being edited through connector reads.
6. Re-read target cells before writing when live values, formulas, formatting, or validation could affect the write.

## Task To Reference Map

| Task area | Required reference file |
| --- | --- |
| Existing spreadsheet edit workflow, grounding, validation-backed cells, output conventions, and write planning | `references/reference-edit-workflow.md` |
| Raw Sheets write shapes and example `batch_update` bodies | `references/reference-batch-update-recipes.md` |
| Uploading a locally created `.xlsx` to Google Drive | `references/reference-upload-xlsx-to-drive.md` |
| Formula design, repair, rollout, or syntax refresh | `references/reference-formula-patterns.md` |
| Chart creation, repair, chart-spec recall, or repositioning | `references/reference-chart-recipes.md` |
