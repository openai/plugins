# Metrics Library

Use this for formulas and framing rules; keep output labels explicit.

## Notation and Guardrails

- `t` = preview quarter; `t-1` = prior quarter; `t-4` = year-ago quarter; `t-8` = two years ago.
- Every numeric series needs unit, scale, period, source, and GAAP/non-GAAP or KPI definition where relevant.
- Do not compute percent change when the denominator is zero/negative/unstable; show absolute delta and flag limitation.
- If KPI definitions change, mark YoY/stack as not comparable unless a restated bridge exists.

## Core Formulas

- Level QoQ: `x_t / x_t-1 - 1`; rate QoQ: percentage-point delta.
- Level YoY: `x_t / x_t-4 - 1`; rate YoY: percentage-point delta.
- Two-year stack: `x_t / x_t-8 - 1`; optional CAGR: `(x_t / x_t-8)^(1/2) - 1`.
- Margin: numerator/denominator must be named; gross margin = `gross_profit / revenue`, op margin = `operating_income / revenue`.
- Surprise absolute: `reported - expected`; surprise percent for level metrics: `reported / expected - 1`.
- Margin/rate surprise: show bps or percentage-point delta, not level percent surprise.
- Guide midpoint: `(low + high) / 2`; guide delta: `reported_or_consensus - guide_mid`.
- Options implied move: preferred `ATM straddle / spot`; fallback `IV * sqrt(DTE / 365)` and label as approximation.

## EPS Quality Watch

Before the print, flag whether headline EPS could be a poor proxy for recurring operating performance.

Watch items:
- Consensus basis: GAAP EPS, adjusted EPS, operating EPS, continuing operations, or provider-standardized.
- Tax rate, below-the-line income/expense, interest income, FX, equity-investment marks, asset sales, impairments, litigation, restructuring, and pension items.
- Diluted share-count movement from buybacks, converts, SBC, or dilution.
- Whether the real bar is revenue, operating income, FCF, segment profit, or EPS.

If these items are likely material, add a call question and tell the user that post-print EPS should be bridged before updating forward estimates.

## Whisper Rules

Whisper is not consensus. Store and discuss separately with `value/range`, `as_of`, `provenance`, and confidence.

- Strong support: compare whisper to consensus and guide with source timestamp.
- Weak support: communicate as soft setup/range, not a hard number.
- No external whisper: only derive an `implied whisper` from guidance history or beat-pattern math when sourced; otherwise say not provided.
- Never blend consensus and whisper without explaining the bridge.

## Scenario Rules

- Base defaults to consensus or guide-consistent case.
- Bull/bear move only the KPIs that matter to the thesis; include driver, value/range, source/assumption, and falsifier.
- If historical forecast error exists, use it for widths; otherwise label generic placeholders such as +/-2% revenue, +/-50-100 bps margin, or +/-5-10% EPS as assumptions.

## Flags

Flag items likely to matter:

- Consensus/guide/whisper deltas above sector materiality.
- Trend break versus trailing four-quarter slope or historical forecast error.
- YoY deceleration >300 bps for growth metrics or margin compression >100 bps, unless sector-specific threshold overrides.
- Guidance midpoint materially below/above consensus.

## Common KPI Families

- SaaS/subscription: ARR, net new ARR, RPO/cRPO, billings, NRR/GRR, churn, customers/seats, ARPU/ARPA, FCF margin.
- Internet/marketplace/ads: users, engagement, impressions, pricing, take rate, GOV/GMV/GPV, active merchants/accounts.
- Consumer/retail: comps, traffic, ticket, pricing/promo, inventory, shrink, markdown cadence, gross margin.
- Semis/hardware: units, ASP, backlog, book-to-bill, channel inventory, utilization, capacity, gross margin guide.
- Banks/financials: NII, NIM, deposits, deposit beta, loan growth, PCL, charge-offs, CET1, efficiency ratio.
- Industrials/services: orders, backlog, book-to-bill, utilization, labor rates, pricing, end-market mix.
- Energy: production, realized price, hedges, LOE/unit, capex, FCF, return of capital.
