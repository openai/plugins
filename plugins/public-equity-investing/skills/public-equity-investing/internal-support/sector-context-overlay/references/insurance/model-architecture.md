# Model Architecture

Deferred reference for `sector-context-overlay` insurance sector lens. Load only when the task needs a model build, model update, driver decomposition, or sensitivity design.

## Modeling rules for insurers

Build models around premiums, exposures, reserves, and capital for P&C, or around spread-earning assets, liabilities, and capital for life. Do not force industrial-company templates onto an insurer.

## Required model structure
Forecast at minimum:
- business mix by line or product
- gross and net written or earned premium, or sales, deposits, and account values
- rate, exposure, retention, and loss-trend assumptions
- current accident-year loss ratio, cat load, prior-year development, and expense ratio for P&C
- spread-earning assets, base yield, cost of funds, fee income, lapses or surrenders, and benefit ratios for life and annuity
- net investment income and alternative or variable investment contribution
- taxes and interest at holdco where relevant
- book value, adjusted book value, or statutory capital
- RBC or local solvency ratio, holdco liquidity, and capital return

## Mandatory decomposition
- separate price from exposure or volume
- separate gross from net and retained from ceded
- separate current accident-year from prior-year reserve development
- separate catastrophe or large loss from attritional results
- separate recurring base investment yield from variable or mark-sensitive income
- keep GAAP or IFRS, statutory, and holdco-cash concepts distinct

## Mandatory sensitivities
Run explicit sensitivities on:
- rate path and reinvestment yield
- loss trend, social inflation, and claim severity
- reserve strengthening or weaker development
- catastrophe burden or a PML event
- reinsurance cost and retention
- lapse, surrender, or policyholder behavior
- asset credit losses or spread widening
- rating downgrade or capital-action constraints
- buyback and dividend assumptions
