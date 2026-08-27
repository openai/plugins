# Model Architecture

Deferred reference for `sector-context-overlay` oil-gas-ep sector lens. Load only when the task needs a model build, model update, driver decomposition, or sensitivity design.

## Modeling rules for E&P companies

Build E&P models from production by commodity and basin upward. Do not force a generic revenue-growth model onto a depleting asset business.

## Required model structure
Forecast at minimum:
- production by commodity and by major basin or asset
- benchmark price deck and realized-price bridge by commodity
- hedge volumes, strike structure, and cash settlements
- LOE, GPT, production taxes, cash G&A, and interest
- capex split into drilling, completions, facilities, land, and other where available
- maintenance versus growth capital framing
- reserve roll-forward or inventory roll-forward logic
- free cash flow, leverage, and liquidity
- NAV and downside case by security

## Mandatory decomposition
- separate oil, gas, and NGL economics
- separate benchmark price from differentials and hedge effects
- separate PDP decline from new-well contribution
- separate maintenance capital from growth capital
- separate organic reserve additions from acquired reserve additions
- separate PDP value from undeveloped inventory value
- separate operating control from non-operated exposure

## Mandatory sensitivities
Run explicit sensitivities on:
- WTI or Brent
- Henry Hub and relevant basis differentials
- NGL realizations
- D&C and service cost inflation or deflation
- type-curve or EUR assumptions
- drilling cadence and maintenance capital
- hedge roll-off
- transport and gathering cost burden
- exit multiple or NAV discount where used
- refinancing cost and liquidity availability
