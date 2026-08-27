# Dashboard Map: DCF Model Builder

Use `dashboard-builder` for model-backed valuation dashboards when the DCF workbook output needs a browsable investor view.

## Decision Question

What valuation range is supportable, what drives it, and how does it compare with current market price or the decision threshold?

## Recommended Payload

- `kind`: `public_equity_investing_dashboard.v1`
- `mode`: `dcf_model_builder`
- `metadata.citation_policy`: `strict`
- `model_citations_path`: `model_citations.json` from formula mode when workbook cells are cited
- `sources`: filings, release/transcript, consensus/market data, WACC inputs, and model citation records

## Recommended Tabs And Modules

1. Valuation Read: `decision_box`, `metric_tiles`.
2. Scenario Range: `scenario_map`, `table`.
3. Value Drivers: `bar_chart`, `table`, `cards`.
4. WACC And Terminal Value: `table`, `scenario_map`.
5. Source And Model QA: `source_list`, `missing_evidence`, `table`.

## Required Evidence

Dashboard values sourced from workbook formulas should cite model-output records such as `model-output:dcf-value-per-share`, which resolve to workbook/sheet/cell/range and formula details.

## Do Not

- Do not cite generic model output when `model_citations.json` exists.
- Do not claim formula-workbook status if the formula builder failed inspection.
- Do not expose raw citation JSON as the user-facing artifact.


## Equity Valuation PM Modules

Dashboards for DCF work should surface a PM decision box, current price versus implied value/share, what is priced in, variant estimate path, DCF bridge, reverse DCF, scenario skew, downside mechanism, action rules, source posture, and missing evidence. Sector context belongs inside this dashboard rather than a standalone sector dashboard.
