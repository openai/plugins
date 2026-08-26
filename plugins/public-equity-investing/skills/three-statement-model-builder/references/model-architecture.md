# Model Architecture Reference

Use this reference when deciding how to structure a new or rebuilt 3-statement model.

Current shipped behavior has two explicit paths: `scripts/build_banker_formula_workbook.py` is the default user-facing path and materializes the bundled live-formula template as `banker_formula_workbook`; the bundled deterministic pipeline produces a values-based `deterministic_export` support workbook for controlled computed values, smoke tests, explicit lightweight exports, or honest fallback. Do not claim the deterministic pipeline creates a fully linked formula workbook.

## Architecture goals

A senior-quality model should be:

- easy to navigate
- easy to update
- hard to break accidentally
- transparent about assumptions
- explicit about scenario logic
- auditable from dashboard back to source data
- mechanically tied across all three statements

## Default workbook tabs for manual/formula workbooks

Use a lean set of tabs for small models and a more modular structure for institutional models.

### Minimum viable model

- `Control Panel`
- `Assumptions`
- `Income Statement`
- `Balance Sheet`
- `Cash Flow`
- `Checks`
- `Dashboard`

### Institutional model

- `README` or `Model Guide`
- `Control Panel`
- `Sources`
- `Historical`
- `Assumptions`
- `Scenarios`
- `Revenue Build`
- `COGS Gross Margin`
- `Opex Headcount`
- `Working Capital`
- `Capex D&A`
- `Debt Interest`
- `Tax`
- `Income Statement`
- `Balance Sheet`
- `Cash Flow`
- `Checks`
- `Dashboard`
- `Sensitivity`

### When to add specialized tabs

Add specialized tabs only when they clarify important logic.

- `Covenants` for lender or credit models
- `Segments` for multi-segment companies
- `Geo` for regional reporting
- `Customers` for concentration or retention-driven models
- `Unit Economics` for SaaS, marketplace, ecommerce, or consumer models
- `Inventory` for retail, manufacturing, or distribution
- `Leases` when lease liabilities or right-of-use assets are material
- `Equity` for option pools, preferred equity, dividends, or share count logic
- `Restructuring` for turnaround models
- `M&A` for acquisition, divestiture, or pro forma adjustments

## Tab purpose standards

### README / Model Guide

Include:

- model purpose
- version / date
- forecast horizon
- units and currency
- scenario definitions
- refresh instructions
- known limitations
- key open questions

### Control Panel

Include global controls:

- active scenario selector
- forecast start date
- units
- currency
- tax assumptions
- key toggle assumptions
- model status indicators
- links to major outputs and checks

### Sources

Include source inventory:

- source name
- type of source
- date received
- period covered
- reliability notes
- major adjustments made
- owner / provider where available

### Historical

Use for loaded historical statements and KPIs. Preserve source values separately from normalized values when possible.

Include:

- reported historical data
- normalization adjustments
- adjusted historical data
- bridge between reported and adjusted figures
- tie-outs to source totals

### Assumptions

Centralize model assumptions. Separate global assumptions from driver-specific assumptions.

Recommended sections:

- revenue assumptions
- gross margin / COGS assumptions
- opex assumptions
- headcount assumptions
- working capital assumptions
- capex and D&A assumptions
- debt / interest assumptions
- tax assumptions
- one-time or special assumptions

### Scenarios

Show scenario cases side-by-side. Each case should have a clear economic story, not just numbers.

For each scenario, include:

- case name
- narrative purpose
- key revenue drivers
- margin assumptions
- working capital assumptions
- capex assumptions
- debt / liquidity assumptions
- rationale

### Driver tabs

Driver tabs should calculate economic reality before statement presentation.

Examples:

- revenue by customer, product, unit, price, volume, seat count, ARR, GMV, transactions, or projects
- COGS by volume, margin, input cost, labor, hosting, fulfillment, or materials
- opex by department, headcount, vendor spend, sales and marketing, R&D, G&A
- working capital by DSO, DIO, DPO, accrued expense days, deferred revenue, or other operating balances
- capex by maintenance, growth, project, or percentage of revenue
- debt by tranche, amortization, revolver, interest rate, fees, and covenants

## Model flow

A robust model should flow as follows:

1. Source data
2. Historical normalization
3. Assumptions and scenarios
4. Driver schedules
5. Statement schedules
6. Integrated financial statements
7. Checks
8. Dashboard and sensitivities

Avoid output tabs that calculate core assumptions. Avoid circular logic unless it is intentional, documented, and controlled.

## Time structure

Choose the time grain based on the decision.

- Monthly: liquidity, startup, turnaround, covenant, working capital, cash burn, near-term budget
- Quarterly: public company, portfolio monitoring, interim reporting, lender updates
- Annual: investment screening, long-term strategic planning, valuation support
- Mixed: monthly near-term plus annual long-term when both liquidity and strategy matter

Separate historical and forecast periods. Use a visible border or row label. Do not hide the transition from actuals to forecast.

## Formula conventions for manual/future formula workbooks

Use consistent formulas across rows and periods.

Recommended practices:

- one formula pattern per row across forecast periods
- assumptions pulled from assumption tabs or scenario tables
- historical values linked from source or normalized historical sections
- no unexplained hardcodes inside formulas
- avoid merging cells in calculation areas
- avoid volatile functions where simpler formulas work
- avoid whole-column references in large models if they create performance issues
- use named ranges only when they improve clarity
- document circular references if any exist

## Sign convention

Pick and document one sign convention.

Common convention:

- revenue positive
- expenses positive on the income statement presentation, but subtracted in EBITDA / EBIT formulas
- assets positive
- liabilities positive
- operating cash inflows positive
- cash outflows negative in the cash flow statement
- working capital increases shown as cash outflows
- debt draws positive and repayments negative

If the user's workbook already uses a different coherent convention, preserve it and document it.

## Formatting conventions

Use formatting to communicate model meaning.

Recommended visual logic:

- inputs: visually distinct
- formulas: normal fill
- linked cells: optionally distinct if workbook convention supports it
- checks: clear pass / fail and variance
- historical periods: separated from forecast periods
- section headers: consistent and readable
- units: visible on each major tab

Formatting should support review, not hide complexity.

## Dashboard standards

A dashboard should answer the senior user's likely questions quickly:

- revenue growth
- gross margin and EBITDA margin
- cash balance and liquidity runway
- debt and leverage
- free cash flow
- capex intensity
- working capital investment
- key scenario outputs
- top risks and open assumptions

Dashboards should link to calculated outputs, not retype them.

## Public Equity Architecture Overlay

The first-tab Cover should answer what changed in the equity forecast, which model lines differ from consensus, whether EBITDA converts to FCF, how share count/capital return affect EPS and value per share, and which downside driver hits common equity first. Keep debt schedules as support for interest expense, liquidity, dilution/refinancing risk, and equity impairment; route credit-security valuation and covenant-package ownership to Credit Markets.
