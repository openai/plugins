---
name: google-sheets
description: Analyze and edit connected Google Sheets with range precision. Use when the user wants to find a spreadsheet, inspect tabs or ranges, search rows, plan formulas, clean or restructure tables, write concise summaries, or make explicit cell-range updates.
---

# Google Sheets

Use this skill to keep spreadsheet work grounded in the exact spreadsheet, sheet, range, headers, and formulas that matter.

## Default Routing

1. Net-new Google Sheets creation: if the `$Spreadsheets` or `$Excel` skill exists, you MUST use the available spreadsheet authoring skill to create a local `.xlsx` first. After creating the local `.xlsx`, import it into Google Drive with the available MCP import or upload tool.
2. Editing existing Google Sheets: use the Google Sheets connector directly.

## Workflow

1. If the spreadsheet or tab is not already grounded, identify it first and read metadata before deeper reads or writes.
2. Prefer narrow reads and row search over dumping large tabs into context.
3. Ground the task in exact sheet, range, header, and formula context before proposing changes.
4. When a read could influence a write, default to `get_cells`. Treat `get_range` as the exception and use it only when plain displayed values are truly sufficient.
5. If the task involves filling in, editing, or normalizing existing cells, do not rely on `get_range` alone. Inspect the target cells with `get_cells` first so value choices come from the live cell metadata.
6. When validation-backed cells may matter, prefer a `get_cells` read that includes the live constraint data you need, for example `dataValidation,formattedValue,effectiveValue,userEnteredValue`.
7. When preparing to write into existing cells, check whether the target range is constrained by dropdowns or other data validation before choosing values. Do not infer allowed values from plain neighboring text alone when validation may exist.
8. If validation is present, restate the allowed values or rule before drafting or applying the write.
9. Before the first write-heavy `batch_update`, read `./references/batch-update-recipes.md` for request-shape recall.
10. Cluster logically related edits into one `batch_update` so the batch is coherent and atomic. Avoid both mega-batches and one-request micro-batches.
11. If the user asks to clean, normalize, or restructure data, summarize the intended table shape before writing.
12. For exact-row, fixed-count, or report-style tasks, keep the findings narrowly scoped to the requested conclusions only. Do not add extra metrics, adjacent commentary, or bonus rows unless the user asked for them.

## Output Conventions

- Always reference the spreadsheet, sheet name, and range when describing findings or planned edits.
- For `batch_update` work, use a compact table or list with the request type, target range or sheet, proposed change, and reason.

## References

- For raw Sheets write shapes and example `batch_update` bodies, read `./references/batch-update-recipes.md`.
