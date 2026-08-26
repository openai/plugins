# Model Architecture

Deferred reference for `sector-context-overlay` bank sector lens. Load only when the task needs a model build, model update, driver decomposition, or sensitivity design.

## Modeling rules for banks

Build models around average balances, rates, credit costs, and capital. Do not force industrial-company templates onto a bank.

## Required model structure
Forecast at minimum:
- average earning assets by major portfolio
- asset yields by portfolio
- average deposits by type and deposit costs by type
- wholesale funding balances and costs
- fee revenue by major line
- operating expenses
- provision for credit losses
- taxes
- RWAs, CET1 dollars, CET1 ratio, leverage ratio
- dividends, buybacks, and share count where relevant
- tangible book value per share and ROTCE

## Mandatory decomposition
- Separate volume from rate for both assets and liabilities.
- Model provision from a credit view, not as a plug to hit EPS.
- Keep average-balance and period-end-balance concepts distinct.
- Carry securities marks, OCI, and capital consequences where relevant.
- Reflect acquisition accretion, hedges, and structural balance-sheet changes explicitly.

## Mandatory sensitivities
Run explicit sensitivities on:
- rate path and curve shape
- deposit beta and remix
- loan growth versus deposit growth
- credit costs / NCOs / cost of risk
- office CRE stress or other concentrated portfolio stress
- RWA inflation
- securities marks / liquidity stress where relevant
- payout and buyback assumptions
