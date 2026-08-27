# Model Math

## Timeline

Annual models emit `FYyyyy` periods. Quarterly models emit `Qn-FYyyyy` periods. Quarterly assumptions supplied annually are converted using a period time factor of `0.25` where appropriate.

## Revenue

`segments`: each segment begins with `base_revenue` and compounds by period growth. Period revenue is the sum of segment revenue.

`total_growth`: total revenue begins with `base_revenue` or latest historical revenue and compounds by period growth.

`volume_price`: units and price compound separately. Revenue equals units times price.

## Income statement

- COGS = revenue x (1 - gross margin), or revenue x COGS percent.
- Gross profit = revenue - COGS.
- Opex = revenue x opex percent, or specified amount.
- EBITDA = gross profit - opex.
- D&A comes from the PP&E schedule.
- EBIT = EBITDA - D&A.
- Interest expense = average debt base x interest rate x period time factor.
- EBT = EBIT - interest.
- Book tax = positive EBT x book tax rate.
- Cash tax = taxable income after NOL usage x cash tax rate.
- Net income = EBT - book tax.
- Deferred tax add-back = book tax - cash tax.

## Working capital

- AR = annualized revenue x AR days / 365.
- Inventory = annualized COGS x inventory days / 365.
- AP = annualized COGS x AP days / 365.
- Other current assets = annualized revenue x percent of revenue.
- Accrued expenses = annualized revenue x percent of revenue.
- Deferred revenue = annualized revenue x percent of revenue.
- NWC = AR + inventory + other current assets - AP - accrued expenses - deferred revenue.
- Change in NWC = current NWC - prior NWC.

A positive change in NWC is a use of cash in CFO.

## PP&E and D&A

- Capex = revenue x capex percent, or specified capex amount.
- D&A = beginning PP&E x depreciation rate, or revenue x D&A percent, or specified D&A amount.
- Ending PP&E = beginning PP&E + capex - D&A - disposals.

## Cash flow

- CFO = net income + D&A + deferred tax - change in NWC.
- Cash flow from investing = -capex.
- Cash flow from financing = debt draws - debt repayments - dividends - buybacks + issuance.
- Ending cash = beginning cash + CFO - capex + financing flows.
- Free cash flow in summary outputs = CFO - capex.

## Debt and cash sweep

The model tracks total debt and revolver availability:

1. Beginning debt and beginning cash come from the latest historical balance sheet or debt plan.
2. Scheduled draws increase debt and cash, subject to revolver availability when a revolver commitment is specified.
3. Mandatory amortization reduces debt and cash.
4. If cash falls below minimum cash, the model draws the revolver up to available commitment.
5. If cash exceeds minimum cash, the model uses `sweep_pct` of excess cash to repay debt.
6. Optional repayments pay revolver debt first, then other debt in aggregate.

## Balance sheet

- Cash ties to the cash flow statement.
- AR, inventory, OCA, AP, accrued expenses, and deferred revenue come from working capital schedules.
- PP&E comes from the PP&E schedule.
- Debt comes from the debt schedule.
- Common equity rolls forward with issuance less buybacks.
- Retained earnings rolls forward with net income less dividends.

## Liquidity and covenant metrics

- Net debt = debt - cash.
- Liquidity = cash + revolver availability.
- Net leverage = net debt / EBITDA.
- Interest coverage = EBITDA / interest expense.
- Covenant breach flag = 1 if liquidity, leverage, or coverage fail supplied thresholds.
