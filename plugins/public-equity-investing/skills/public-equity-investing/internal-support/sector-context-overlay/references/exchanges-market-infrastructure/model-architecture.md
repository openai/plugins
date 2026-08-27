# Model Architecture

Deferred reference for `sector-context-overlay` exchanges-market-infrastructure sector lens. Load only when the task needs a model build, model update, driver decomposition, or sensitivity design.

## Modeling rules for exchanges and market infrastructure

## Required model structure

Build segment-first models, not one-line CAGR models.

At minimum, separate:
1. transaction revenue by major business line
2. recurring revenue by major business line
3. collateral- or rate-sensitive economics
4. expense base, technology investment, and capital allocation

## Mandatory decomposition

- Listed derivatives: volume by product family times average rate per contract, with separate assumptions for mix and open-interest durability.
- Cash equities and options: matched shares or contracts times net capture, explicitly modeling liquidity payments and any proprietary-product mix.
- Electronic trading venues: ADNV or ADV by asset class and channel times FPM, plus fixed fees by asset class where relevant.
- Data, connectivity, index, and listings: price times customer base, linked assets, issuer base, or subscription units depending on the business.
- Clearing and collateral economics: collateral balances times earned spread or fee logic, with clear rate assumptions.

## Mandatory sensitivities

Always include:
- volume sensitivity in key product lines
- product-mix or protocol-mix sensitivity
- net capture or FPM sensitivity
- rate sensitivity on collateral or balance-related economics
- recurring growth sensitivity
- expense or investment sensitivity
- downside case for regulatory or fee-pressure effects where material
