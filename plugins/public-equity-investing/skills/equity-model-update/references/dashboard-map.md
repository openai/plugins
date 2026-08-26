# Dashboard Map: Equity Model Update

Use `dashboard-builder` for safe model-update dashboards when the user needs to see changed cells, blocked cells, stale sources, tie-out status, and workbook implications.

## Decision Question

Which source-backed model updates were safely applied to a copied workbook, which were blocked, and what needs analyst review?

## Recommended Payload

- `kind`: `public_equity_investing_dashboard.v1`
- `mode`: `equity_model_update`
- `metadata.citation_policy`: `strict`
- `model_citations_path`: `model_update_citations.json`
- `sources`: update source pack, uploaded workbook copy, source-to-model map, and stale/blocked evidence records

## Recommended Tabs And Modules

1. Update Verdict: `decision_box`, `metric_tiles`.
2. Changed Cells: `table`.
3. Blocked Or Needs Review: `missing_evidence`, `table`.
4. Source Freshness: `source_list`, `table`.
5. Tie-Out And Handoffs: `timeline`, `question_list`.

## Required Evidence

Each changed cell should cite workbook, sheet, cell, prior value, new value, source ID, source label/date, freshness, and review status.

## Do Not

- Do not mutate the original uploaded workbook.
- Do not overwrite formulas without explicit approval.
- Do not make CSV/log/manifest files the lead output when a safe XLSX copy or control workbook exists.
