# Model Architecture

Deferred reference for `sector-context-overlay` reits sector lens. Load only when the task needs a model build, model update, driver decomposition, or sensitivity design.

## Modeling rules for REITs

Build REIT models from property cash flows upward. Do not force a generic corporate revenue-growth model onto a landlord.

## Required model structure
Forecast at minimum:
- same-store revenue, expenses, and NOI
- occupancy, lease rates, concessions, bad debt, or operating KPIs appropriate to the sector
- acquisition, disposition, development, and redevelopment activity
- recurring capex, TI/LC, and maintenance spend
- G&A and any fee income or JV income
- debt balances, interest rate, and maturity or refinancing assumptions
- preferred dividends or non-controlling interests where relevant
- Nareit FFO, AFFO or CAD, and dividend payout
- net asset value bridge and leverage metrics

## Mandatory decomposition
- separate same-store from non-same-store
- separate occupancy from pricing
- separate cash rent change from GAAP rent change
- separate contractual escalators from mark-to-market lease rollover
- separate development contribution from acquisition contribution
- separate recurring capex and leasing costs from one-time redevelopment or value-add capex
- separate organic NOI from noncash adjustments and gains on sale

## Mandatory sensitivities
Run explicit sensitivities on:
- occupancy
- leasing spreads or mark-to-market rent capture
- same-store expense growth
- development yield and lease-up timing
- acquisition cap rate versus funding cost
- exit cap rate and NAV
- refinancing rate and debt availability
- tenant default, bad debt, or rent-coverage deterioration
- dividend payout policy and retained cash
