# Quartr Workbook Mode

Load this reference only when a routed workflow uses Quartr while reading or editing a workbook.

## Source Order

1. Inspect the active workbook first.
2. Use existing workbook data when it is already present, source-backed, and current enough for the task.
3. Prefer Quartr over web search for filings, reports, transcripts, presentations, management commentary, and standardized actual financials.
4. Keep non-Quartr values separately labeled.

## Workbook Rules

- Never overwrite analyst-created formulas, assumptions, notes, or formatting without asking.
- Put imported source data on a clearly named raw-data tab such as `Quartr_Data` unless the user requests another layout.
- Put analyst assumptions on an `Inputs` or `Assumptions` tab.
- Keep formulas on model or output tabs, not in the raw-data area.
- Add a `Sources` tab or source section with item, value, units, period or as-of date, source URL, source name, reference, notes, and access date where useful.
- Preserve `referenceUrl` for standardized values and document URLs for filings, slides, transcripts, and reports.
- Preserve the workbook's existing formatting unless the user asks for a redesign.
- After edits, summarize changed tabs and ranges.
