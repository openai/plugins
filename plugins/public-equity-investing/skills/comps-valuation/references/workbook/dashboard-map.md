# Dashboard Map: Comps Model Builder

Use `dashboard-builder` for workbook-backed comps dashboards when valuation ranges, peer selection, outlier handling, or source posture need a reusable investor view.

## Decision Question

What peer-based valuation range is supportable, which peers drive it, and what data quality or comparability issues affect confidence?

## Recommended Payload

- `kind`: `public_equity_investing_dashboard.v1`
- `mode`: `comps_model_builder`
- `metadata.citation_policy`: `strict`
- `model_citations_path`: include when workbook cells or audit outputs are cited
- `sources`: market data, filings, consensus/vendor snapshot, source notes, and workbook audit records

## Recommended Tabs And Modules

1. Valuation Snapshot: `decision_box`, `metric_tiles`.
2. Peer Universe: `table`, `cards`.
3. Multiples And Range: `table`, `bar_chart`, `scenario_map`.
4. Outliers And Denominators: `table`, `missing_evidence`.
5. Source And QA Posture: `source_list`, `table`.

## Required Evidence

Every peer metric, market price, share count, net debt bridge, and selected multiple should cite source IDs or workbook cell records.

## Do Not

- Do not smooth over peer exclusions without a rejection log.
- Do not use stale market/consensus data without visible labels.
- Do not lead with raw workbook-audit JSON or CSV.


## Equity Comps Model Dashboard Modules

Dashboards should surface PM decision box, current price versus implied value, selected-multiple bridge, peer quality score, liquidity/float and ETF/index exposure, source freshness, scenario skew, action rules, and missing evidence.
