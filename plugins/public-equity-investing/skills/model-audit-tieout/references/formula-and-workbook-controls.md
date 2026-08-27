# Formula and Workbook Controls

## Workbook architecture checks

Check whether the workbook has a clear, reviewable architecture:
- first visible tab is a decision-useful `Cover` or dashboard that surfaces key outputs, model status, source posture, warnings/hard failures, and a workbook map
- assumptions and inputs are separated from calculations and outputs
- historical actuals are separated from forecasts
- source tabs are labeled and preserved
- output tabs tie to calculation tabs
- checks are visible and summarized
- the workbook is not dependent on hidden tabs, external links, or undocumented macros

## Formula integrity checks

### Formula consistency
Look for formulas that should copy across a row, column, or period but do not.

Red flags:
- one period has a different formula family from adjacent periods
- one line item switches from formula to hardcode without explanation
- copied formulas point to the wrong row, tab, or period
- forward-year formulas still point to historical-year inputs

### Hardcoded values inside formulas
Hardcodes inside formulas can be acceptable for simple constants but should be reviewed when they drive material outputs.

Usually acceptable if documented:
- 0, 1, -1, 100, 1000, 12, 365, tax-rate conversions, basis-point conversions

Review carefully:
- margin percentages
- growth rates
- multiples
- interest rates
- debt terms
- working capital assumptions
- synergy, add-back, run-rate, or cost-out numbers
- prices, shares, market caps, yields, spreads, or fx rates

### External links
External links are high-risk when they are stale, inaccessible, or undocumented.

Escalate if:
- the workbook refers to another workbook that was not uploaded
- external-linked source data is used in final outputs
- the link path suggests a personal drive or local machine
- the linked file name implies a prior version, outdated model, or different transaction

### Hidden and very hidden sheets
Hidden sheets are not inherently wrong, but they must be explained when they contain assumptions, source data, formulas, or outputs.

Escalate if:
- a hidden sheet feeds key outputs
- very hidden sheets exist
- hidden sheets contain hardcoded assumptions or external-linked data
- the workbook relies on hidden checks that are not summarized in visible tabs

### Volatile formulas
Volatile functions can make model outputs change unexpectedly.

Review formulas using:
- today
- now
- rand
- randbetween
- offset
- indirect
- cell
- info

### Circularity and iterative calculation
Circular references are sometimes used intentionally in finance models, especially for interest expense and cash sweep logic. They still require documentation.

Escalate if:
- circularity is accidental
- iterative calculation settings are unknown
- the model breaks when circularity is disabled
- interest, cash, debt, or working capital use opaque plugs

## Control checks by schedule

### Balance sheet
- assets equal liabilities plus equity in every period
- retained earnings ties to net income and dividends/distributions
- cash ties to cash flow statement ending cash
- debt schedule ties to balance sheet debt

### Cash flow statement
- net income ties to income statement
- depreciation/amortization ties to capex/fixed asset schedules
- working capital movements tie to balance sheet accounts
- ending cash ties to balance sheet cash

### Debt schedule
- beginning debt plus draws minus repayments equals ending debt
- interest rate and spread assumptions are correct by tranche
- mandatory amortization, excess cash sweep, revolver draw/paydown, fees, and maturity are modeled
- covenant calculations use defined terms, not generic EBITDA unless appropriate

### Valuation and return outputs
- enterprise value converts to equity value with all material claims included
- per-share value uses correct diluted share count
- irr and moic calculations use correct timing and equity invested
- sensitivity tables link to the same output as the base case

### Data tables and sensitivities
- data tables actually change the intended input cells
- row and column inputs are labeled clearly
- sensitivity output cell is correct
- sensitivities do not rely on stale manual pasted values

## Recommended manual checks beyond the script

The bundled script performs static inspection only. Always supplement it with judgment:
- recalculate the workbook in Excel or another spreadsheet environment when possible
- inspect key formulas directly in the workbook
- trace precedents and dependents around material outputs
- compare model outputs to deck/memo numbers
- review formulas around recently edited cells
- test downside cases and see whether checks still pass
