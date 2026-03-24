---
name: google-sheets
description: Analyze and edit connected Google Sheets with range precision. Use when the user wants to find a spreadsheet, inspect tabs or ranges, search rows, plan formulas, clean or restructure tables, write concise summaries, or make explicit cell-range updates.
---

# Google Sheets

Use this skill to keep spreadsheet work grounded in the exact spreadsheet, sheet, range, headers, and formulas that matter.

## Workflow

1. If the spreadsheet or tab is not already grounded, identify it first and read metadata before deeper reads or writes.
2. Prefer narrow reads and row search over dumping large tabs into context.
3. Ground the task in exact sheet, range, header, and formula context before proposing changes.
4. Before the first write-heavy `batch_update`, read `./references/batch-update-recipes.md` for request-shape recall.
5. Cluster logically related edits into one `batch_update` so the batch is coherent and atomic. Avoid both mega-batches and one-request micro-batches.
6. If the user asks to clean, normalize, or restructure data, summarize the intended table shape before writing.

## Output Conventions

- Always reference the spreadsheet, sheet name, and range when describing findings or planned edits.
- For `batch_update` work, use a compact table or list with the request type, target range or sheet, proposed change, and reason.

## References

- For raw Sheets write shapes and example `batch_update` bodies, read `./references/batch-update-recipes.md`.
