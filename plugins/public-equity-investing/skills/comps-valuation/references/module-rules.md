# Module And Asset-Class Rules

## Corporate

Use EV-based and equity-based multiples as appropriate:

- `EV/LTM Revenue`
- `EV/NTM Revenue`
- `EV/LTM EBITDA`
- `EV/NTM EBITDA`
- `EV/LTM EBIT`
- `EV/NTM EBIT`
- `P/E`
- `P/FCF`, `FCF yield`, or sector-specific metrics when support exists

Keep reported and adjusted denominators separate. Do not overwrite reported metrics with adjusted ones.

## Banks and lenders

Do not use EV-based multiples by default. Use:

- `P/TBV`
- `P/B`
- `P/E`
- ROE, ROTCE, ROA
- NIM
- CET1 or relevant capital ratio
- deposit mix
- credit losses, NPLs, reserves, and asset sensitivity where available

Flag whether book value is tangible, common, or total equity.

## Insurance

Use:

- `P/B`
- `P/E`
- ROE
- combined ratio
- reserve adequacy
- book-value growth

Label life, P&C, brokerage, and reinsurance differences. Do not force a single multiple across fundamentally different insurance models.

## Asset managers and exchanges

Use:

- `P/E`
- `EV/EBITDA`
- AUM, flows, fee rate, and revenue yield where available
- volume, clearing, transaction, or data revenue metrics for exchanges
- margin and operating leverage

Separate market beta, flows, and fee-rate changes when explaining premiums or discounts.

## REITs and real assets

Use:

- `P/FFO`
- `P/AFFO`
- NAV premium/discount
- implied cap rate
- occupancy
- same-store NOI
- leverage
- property-type read-through

For REITs, treat the module as a specialized public-equity comp sheet, not a generic corporate trading comps screen.

### REIT denominator hierarchy

1. Recurring Core / adjusted FFO per share as the primary equity multiple denominator.
2. Cleaner ex-item Core FFO when promote income, casualty / business-interruption proceeds, lease termination income, large disposition items, or other non-recurring items distort recurring FFO.
3. Reported NAREIT FFO only when no cleaner recurring FFO metric is available. Label it as reported.
4. AFFO / CAD as a secondary cross-check when disclosed or cleanly derivable. Do not make AFFO availability determine peer inclusion.
5. EV/EBITDAre, NAV premium/discount, and implied cap rate as cross-checks when relevant.

### REIT peer preservation

Do not exclude a very close REIT peer only because one secondary field is missing. Include the peer in the core table with `N/A`, `N/M`, or a clearly labeled derived value if:

- it is economically one of the closest public peers;
- the primary FFO-style denominator is available; and
- the missing value is not central to the user's requested decision.

Only exclude a close peer if the primary valuation denominator or pricing data cannot be sourced. List the exact missing blocker.

### REIT table

For REIT requests, the core table should usually include:

| Ticker | Peer role | Price / as-of | FFO denominator used | P/FFO | AFFO or CAD denominator | P/AFFO or P/CAD | Leverage | Occupancy basis | Normalized read-through |
|---|---|---:|---|---:|---|---:|---|---|---|

Prefer a complete table for the closest 4-8 peers over a long table with many missing fields.

## Distressed or stressed companies

Do not let normal trading comps imply false precision. Flag:

- capital-structure impairment;
- liquidity and going-concern issues;
- debt trading levels;
- whether equity value is option value;
- whether EV is effectively owned by creditors;
- whether recovery value matters more than trading multiples.

Route to Credit Markets when credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, claim priority, liquidity, or capital-structure impairment is the real task.

## Private-company target

Use public comps only to infer a valuation range. Target financials from CIM, banker deck, management accounts, or management materials are `seller_claim` or `management_claim` unless verified.

Route to `financials-normalizer`, `financial-source-of-truth`, or `three-statement-model-builder` when the target denominator is not reliable.
