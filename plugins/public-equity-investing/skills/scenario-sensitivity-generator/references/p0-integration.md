# P0 Integration

## Ownership Matrix

| Area | This skill owns | Adjacent skill owns |
|---|---|---|
| Source data confidence | Uses caveats and reconciled inputs | `financial-source-of-truth` and `financials-normalizer` own source hierarchy, evidence labels, normalization, and exception registers |
| Equity model update | Scenario overlay and sensitivity outputs | `equity-model-update` owns actuals, guidance, consensus, transcript, KPI, and estimate-change refreshes |
| Integrated model mechanics | Scenario overlays and target outputs | `three-statement-model-builder` owns IS/BS/CF architecture |
| Valuation mechanics | Sensitivity ranges and valuation implications | `dcf-model-builder`, `comps-valuation` own valuation construction |
| Earnings implications | Scenario effects on print setup or post-print analysis | `earnings-preview` and `earnings-deep-dive` own earnings narrative and source review |
| Equity liquidity downside | Common-equity liquidity, maturity, covenant-pressure, recovery read-through, and refinancing sensitivities | Credit Markets owns capital-structure, debt-security, covenant-package, recovery, and public-credit-instrument research |
| Event-driven probability | Probability-weighted outcome tables | `event-driven-analyzer` owns event facts, process risk, approvals, documents, and catalyst analysis |
| Macro factor translation | Sensitivity table from supplied factor assumptions | `economic-impact-report` owns broader macro transmission and cross-asset analysis |
| Position/risk sizing | Scenario P&L inputs and thesis triggers | `portfolio-risk-management` owns sizing, risk limits, and hedge selection through its selected mode |
| Memo/deck output | Scenario conclusions and handoff blocks | `memo-builder`, `long-short-pitch`, and `deck-report-qc` own final narrative and circulation QA |
| Workbook QA | Scenario logic checks and assumptions | `model-audit-tieout` owns final workbook-level audit |

## Boundary With Model Builders

This skill may add scenario overlays, sensitivity tables, target backsolve tables, thesis triggers, and decision outputs to an existing model. It should not rebuild the integrated model unless the user explicitly asks for a model rebuild and no better routing is available.

Use `three-statement-model-builder` when:
- there is no integrated model;
- the balance sheet or cash flow does not tie;
- the forecast lacks working capital, capex, debt, tax, or retained earnings logic;
- scenarios require statement linkage the current model does not have;
- the user asks to build or rebuild the operating model itself.

Use `dcf-model-builder` or `comps-valuation` when valuation calculations need to be constructed rather than sensitized.

This skill should hand model builders a scenario overlay table, not a separate shadow model.
