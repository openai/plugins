# Dashboard Map: Three-Statement Model Builder

Use `dashboard-builder` for operating-model cockpit views across revenue, margins, cash flow, balance sheet, liquidity, scenarios, and checks.

## Decision Question

Is the forecast internally consistent, financeable, and useful for the public-company investment decision under base and downside cases?

## Recommended Payload

- `kind`: `public_equity_investing_dashboard.v1`
- `mode`: `three_statement_model_builder`
- `metadata.citation_policy`: `strict`
- `model_citations_path`: `model_citations.json` from formula mode when citing workbook outputs
- `sources`: filings, release/transcript, consensus/market data, source notes, and model citation records

## Recommended Tabs And Modules

1. Operating Read: `decision_box`, `metric_tiles`.
2. Income Statement: `table`, `bar_chart`.
3. Cash Flow And Liquidity: `table`, `scenario_map`.
4. Balance Sheet And Debt: `table`, `cards`.
5. Checks And Sources: `source_list`, `missing_evidence`, `table`.

## Required Evidence

Model-backed dashboard claims should cite workbook-cell records such as `Income Statement!I6`, `Balance Sheet!I22`, and `Checks!C6` through `model_citations_path`.

## Do Not

- Do not hide balance sheet or cash flow check breaks.
- Do not present unbalanced or placeholder-driven outputs as decision-grade.
- Do not make run logs or citation JSON the lead artifact.


## Equity Forecast PM Modules

Dashboards should surface PM decision box, current price context, estimate path, revenue/margin/EPS/FCF bridges, scenario skew, what breaks first in downside, action rules, source posture, and missing evidence.
