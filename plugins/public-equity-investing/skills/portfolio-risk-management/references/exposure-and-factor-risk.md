# Exposure and Factor Risk

## Purpose

Use this reference to decompose position risk before recommending size. The central question is whether the position expresses the intended thesis or merely adds hidden exposure to the book.

## Exposure map

Create an exposure map across these dimensions:

- Security/instrument exposure.
- Issuer and related-issuer exposure.
- Sector and sub-industry exposure.
- Geography and currency exposure.
- Market beta and benchmark active weight.
- Style factors: value, growth, quality, momentum, size, low volatility, leverage, profitability, revisions, short interest, crowding.
- Macro factors: rates, inflation, FX, commodities, CDS/credit-spread signals as equity-risk context, and liquidity regime.
- Event factors: earnings, regulatory, litigation, M&A, product launch, trial data, lockup, index event.
- Liquidity and financing factors: ADV, float, borrow, options depth, ETF liquidity, margin/financing, and balance-sheet stress signals.

## Core calculations

### Position exposure

- Dollar exposure = shares/contracts x price x multiplier.
- Percent NAV = dollar exposure / portfolio NAV.
- Gross exposure contribution = absolute dollar exposure / NAV.
- Net exposure contribution = signed dollar exposure / NAV.
- Beta-adjusted exposure = signed percent NAV x beta.
- Active weight = portfolio weight - benchmark weight.

### Short exposure

For shorts, show both market value and loss asymmetry:

- Short market value % NAV.
- Adverse move loss at upside/squeeze price.
- Borrow cost drag.
- Dividend/financing drag.
- Days-to-cover and utilization if available.

### Options exposure

Show at least:

- Premium at risk.
- Delta-adjusted notional.
- Gamma exposure around catalyst.
- Vega exposure to implied volatility change.
- Theta decay to catalyst/expiry.
- Open interest and bid/ask/liquidity.

### Equity-risk credit signals as common-equity context

Show only the equity read-through:

- CDS or credit-spread signal, with date and source, when it changes common-equity downside.
- Rating, maturity wall, refinancing, covenant headline, or liquidity stress as a solvency or equity-impairment input.
- Whether the signal changes common-equity size, hedge review status, or re-underwrite status.
- Do not compute market-value/par credit exposure, CS01/DV01, recovery, debt seniority, or dealer-depth sizing here; route those to Credit Markets.

## Factor risk questions

Ask and answer:

1. Is the proposed position adding market beta that is intended or incidental?
2. Is sector exposure already crowded in the book?
3. Is the thesis really a factor bet in disguise?
4. Will the position work if the market, sector, or factor moves against it?
5. Does historical correlation understate current common ownership or crowdedness?
6. Does the position interact with existing longs, shorts, pairs, options, equity-risk credit signals, or Credit Markets outputs?

## Long-only / mutual fund nuance

For long-only and benchmark-aware users:

- Active weight and tracking error matter as much as absolute size.
- A 3% position can be underweight if benchmark weight is larger.
- Illiquid active underweights can create risk if the name rallies sharply.
- Concentration and diversification limits may bind before loss-budget sizing.
- Include benchmark sector/country/industry exposure if available.

## Hedge fund / long-short nuance

For hedge funds:

- Gross, net, beta-adjusted net, factor exposure, and liquidity buckets matter.
- Long and short books can be balanced in dollars but not in beta or factor exposure.
- A new short can hedge beta but add short-squeeze/crowding risk.
- A new long can improve alpha but worsen factor concentration.
- Include capital usage and margin/financing where relevant.

## Event-driven nuance

For special situations:

- Exposure should be measured by spread/gap risk, not only beta.
- The key risk can be deal break, regulatory block, court ruling, shareholder vote, financing failure, product outcome, or timing delay.
- Liquidity often disappears at exactly the wrong time.
- A small percent NAV can still be too large if the adverse gap is severe.

## Sector-specific red flags

### Banks and financials

- Rate sensitivity, deposit beta, credit cycle, regulatory capital, liquidity, CRE exposure, marks, and capital return.
- Book value and capital ratios can move faster than ordinary earnings estimates.

### Insurance

- Reserve risk, catastrophe exposure, investment portfolio duration, capital adequacy, pricing cycle, and ratings.

### SaaS/software

- Duration, revenue growth, NRR, CAC/payback, FCF conversion, seat/usage trends, and valuation multiple sensitivity.

### Semiconductors/hardware

- Cycle, inventory correction, customer concentration, capex cycle, geopolitics/export controls, and supply chain.

### Biotech/pharma

- Binary trial/regulatory risk, cash runway, dilution, patent cliffs, reimbursement, and pipeline concentration.

### Energy/materials

- Commodity beta, hedging, decline/cost curve, reserves, leverage, FX, and political/regulatory risk.

### REITs/real estate

- Rates, cap rates, leverage, refinancing, occupancy, NOI, tenant concentration, and asset-type cycle.

## Output standard

The exposure section should be concise but complete. It should not drown the user in factor jargon. Focus on the exposures that can change the recommended size.
