---
name: google-sheets
description: Analyze and edit connected Google Sheets with range precision. Use when the user wants to create Google Sheets, find a spreadsheet, inspect tabs or ranges, search rows, plan formulas, create or repair charts, clean or restructure tables, write concise summaries, or make explicit cell-range updates.
---

# Google Sheets

Use this skill to keep spreadsheet work grounded in the exact spreadsheet, sheet, range, headers, and formulas that matter.

## Purpose Of This File

This file is intentionally minimal and only covers:

1. routing to the right spreadsheet workflow
2. stateful operation and mandatory routing to reference files

Detailed editing, formula, chart, upload, and batch-update rules live in `references/`.
Latency is not a constraint for this skill, so always read the relevant reference files before performing the task.

## Default Routing

1. New Google Sheets creation: first check whether the `[@spreadsheets](plugin://spreadsheets@openai-primary-runtime)` plugin or the `$Excel` skill is installed.
2. If either is installed, YOU MUST use `[@spreadsheets](plugin://spreadsheets@openai-primary-runtime)` or `$Excel` to create a local `.xlsx`. Then import the `.xlsx` into Drive as a native Google Sheets spreadsheet. Read `references/reference-import-spreadsheet-to-native-sheets.md`.
4. If neither skill is installed, create the spreadsheet directly with Google Sheets MCP.
5. Existing Google Sheets edits: use Google Sheets MCP directly.

Do not reference the local `.xlsx` in the final answer. Your final answer includes the Google Spreadsheet link only.

## Canonical Workflow Bias

Prefer one simple proven workflow over a large tree of recovery branches.
When a task matches a known successful pattern, follow that pattern directly instead of re-evaluating every possible fallback path.
Do not let accumulated edge-case guardrails turn a straightforward Sheets task into a long blocker-analysis exercise.

For sheet creation and editing tasks, prefer this sequence when viable:

1. Gather the required source material.
2. Pick the correct default routing.
3. Establish the sheet checklist or sheet plan.
4. Build or edit the sheet.
5. Verify the sheet is clean, complete, native, and scannable.
6. Stop once the verified workflow has succeeded.

If a simple verified workflow is viable, use it. Do not drift into speculative alternate paths.

## Required Read Order (No Skips)

If Default Routing uses `[@spreadsheets](plugin://spreadsheets@openai-primary-runtime)` or `$Excel`:
1. Read the `[@spreadsheets](plugin://spreadsheets@openai-primary-runtime)` plugin skill or `$Excel` skill
2. Read `references/reference-import-spreadsheet-to-native-sheets.md`

If Default Routing uses connector edit workflow:

1. Read `references/reference-edit-workflow.md`.
2. Read every task-specific file from the matrix below.
3. If the task spans multiple categories, read all matching files.
4. If uncertain, read every file in `references/`.

Do not execute content edits until the required references are read in the current turn.

## Final Answer Requirement

If the `[@spreadsheets](plugin://spreadsheets@openai-primary-runtime)` plugin or the `$Excel` skill is installed, you MUST use one of them to create a local `.xlsx` and import it to Google Drive with `upload_mode: "native_google_sheets"`.
Even though you created a local `.xlsx`, do not cite the local path in the final answer. The final answer cites only the Google Spreadsheet link.

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
| Importing a locally created `.xlsx`, `.xls`, `.ods`, `.csv`, or `.tsv` into Google Sheets | `references/reference-import-spreadsheet-to-native-sheets.md` |
| Formula design, repair, rollout, or syntax refresh | `references/reference-formula-patterns.md` |
| Chart creation, repair, chart-spec recall, or repositioning | `references/reference-chart-recipes.md` |
