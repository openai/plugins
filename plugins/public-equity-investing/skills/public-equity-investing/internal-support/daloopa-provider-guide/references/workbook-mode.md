# Daloopa Workbook Mode

Load this reference only when a routed workflow uses Daloopa while reading or editing a workbook.

## Source Order

1. Inspect the active workbook first.
2. Use existing workbook data when it is already present, source-backed, and current enough for the task.
3. Use Daloopa when the workbook lacks the data, the user asks for fresh data, or the task requires provider-backed sourcing.
4. Keep non-Daloopa values separately labeled.

## Workbook Rules

- Never overwrite analyst-created formulas, assumptions, notes, or formatting without asking.
- Put imported source data on a clearly named raw-data tab such as `Daloopa_Data` unless the user requests another layout.
- Put analyst assumptions on an `Inputs` or `Assumptions` tab.
- Keep formulas on model or output tabs, not in the raw-data area.
- Preserve source IDs, source URLs, or citation columns when importing Daloopa values.
- Preserve the workbook's existing formatting unless the user asks for a redesign.
- After edits, summarize changed tabs and ranges.
