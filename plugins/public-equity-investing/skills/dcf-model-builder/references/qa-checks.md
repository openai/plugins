# QA Checks

## Hard failures
Hard failures force `model_status = not-decision-ready`.

- Forecast cash flows are missing, non-numeric, or all unavailable.
- Terminal value method is missing or invalid.
- Perpetual growth terminal value has discount rate less than or equal to terminal growth.
- WACC/cost of equity is less than or equal to zero or cannot be supported by inputs.
- Discounting math fails, produces non-finite values, or produces negative enterprise value without explicit distressed context.
- EV-to-equity bridge is missing when per-share value is requested.
- Diluted shares are missing or less than or equal to zero when value per share is calculated.
- Sensitivity directionality fails: value should increase as WACC decreases, terminal growth increases, exit multiple increases, revenue growth increases, or EBIT margin increases.
- Source basis is missing for material valuation topics: historicals, forecast, WACC, terminal value, share count, net debt.
- Required base/downside/upside scenarios are missing.
- Actual/estimate period labels disagree across the workbook or sourced actuals are mixed with retained template example history.
- A source-backed PP&E roll-forward becomes negative under the selected forecast assumptions.

## Warnings
Warnings reduce confidence but may still allow a screen-grade or senior-review-ready output.

- Terminal value is more than 75% of enterprise value; greater than 85% is a major warning.
- Terminal growth exceeds 4% or appears inconsistent with currency, maturity, or macro context.
- WACC uses weak `analyst_estimate` or `placeholder` evidence labels.
- Forecast margin expansion exceeds 500 bps without strong source support.
- Capex intensity falls while growth accelerates, without an explicit asset-light rationale.
- NWC release is large and recurring without support.
- Source dates are mixed, stale, or not contemporaneous across market data, financials, share count, and debt.
- SBC, leases, pensions, NOLs, minorities, convertibles, or non-operating assets are material but not modeled.
- Exit multiple and perpetuity-growth methods imply materially different terminal values without explanation.
- Scenario spread is too narrow to be decision-useful.
- Placeholders remain active in a named-company model.
- An operating-driver question is modeled through a revenue proxy because the workbook does not support the relevant KPI build.
- Opening PP&E is unavailable, so capex and D&A sustainability cannot be tested through an asset roll-forward.

## Senior-review red flags
- Good-company/bad-stock issue not addressed through market-implied expectations.
- Terminal margin equals a cyclical peak or management target with no fade.
- Growth and reinvestment are inconsistent with ROIC economics.
- Forecast beats consensus but the thesis does not explain why.
- The DCF value is materially different from trading comps, precedents, or LBO support without explanation.
- Dilution and stock-based compensation are ignored for a high-SBC company.
- Cash taxes are assumed equal to book taxes despite material NOLs, credits, or foreign tax structure.
- Lease-heavy business uses EBITDA and EV bridge inconsistently.
- Acquisition-driven growth is treated as organic.
- Model output is presented as a point estimate rather than a range.
