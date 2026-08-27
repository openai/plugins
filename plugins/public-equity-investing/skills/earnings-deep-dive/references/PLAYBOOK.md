# Earnings Deep Dive Playbook

Use for full mechanics after `SKILL.md` routes the request.

## Source Precedence

- GAAP financials: filed 10-Q/10-K, filed 8-K/exhibits, earnings release tables, deck/prepared remarks, transcript only as narrative cross-check.
- Guidance: filed PR/exhibit first; call-only guidance is allowed only when labeled `CALL-ONLY`.
- Reissues: use final version, note timestamp, and preserve source trail.
- No attachments: use connected/institutional sources, then company IR/SEC, then reputable transcript/consensus providers, then labeled web fallback.

## Normalization

- Pick base currency/scale and convert at ingestion; never mix `$m` and `$bn`.
- Keep reported and constant-currency separate.
- EPS must specify GAAP/non-GAAP, basic/diluted, and share-count source; adjusted EPS needs reconciliation source plus GAAP comparable.
- Every post-print runs an EPS quality screen. Do not let a headline GAAP EPS beat drive the conclusion until below-the-line, tax, mark-to-market, share-count, and non-recurring items are checked.
- KPI definition changes require a schema-change note and driver-registry update.

## Expectations

State the benchmark: consensus for stock-impact, internal estimates for decision benchmark, whisper only if labeled separately. Every output should show estimate set ID/vendor, as-of timestamp, metric definition, unit, and GAAP/non-GAAP basis.

Core math:

- Beat/miss: `reported - expected`.
- Surprise %: `(reported - expected) / expected`; suppress when expected is zero/near-zero.
- Margin/rate deltas: bps or percentage points.
- Guidance midpoint: `(low + high) / 2`; delta to consensus/internal when available.

## EPS Quality Screen

Run this check in every full deep dive. Keep it short unless triggered.

Include a full EPS quality / ex-gain bridge when any trigger is present:

- GAAP EPS surprise is much larger than revenue, operating income, segment profit, FCF, or adjusted EPS surprise.
- EPS is affected by equity-investment gains/losses, mark-to-market items, tax benefits/charges, FX, asset sales, impairments, litigation, restructuring, pension items, or other below-the-line/non-recurring items.
- Consensus basis is unclear or mismatched: GAAP EPS versus adjusted EPS versus operating EPS.
- Management emphasizes adjusted EPS, operating income, FCF, or segment profit instead of GAAP EPS.
- The stock reaction appears to capitalize a headline EPS beat that may not be recurring.
- The issuer has material investment holdings, fair-value accounting, insurance reserves, or financial-asset marks.

Bridge format when triggered:

| Step | EPS / amount | Source | Treatment | Read-through |
|---|---:|---|---|---|
| Reported GAAP diluted EPS |  |  | Starting point |  |
| Less: identified non-operating / non-recurring items |  |  | Remove or isolate |  |
| Tax/share-count normalization if material |  |  | Adjust only with support |  |
| Estimated operating / recurring EPS |  |  | Analyst-derived if not company-reported |  |
| Consensus basis used for beat/miss |  |  | Must match definition |  |

If no trigger is found, write a one-line conclusion: `No material EPS-quality trigger identified from available sources; GAAP and operating signals appear directionally aligned, subject to filing tie-out.`

## Analysis Modules

- Standardized P&L: revenue, gross profit/margin, opex, operating income/margin, below-the-line, net income, diluted shares, EPS, non-GAAP bridge.
- Drivers: isolate 2-3 items explaining the print; for each show what moved, why it moved, and how it changes forward expectations.
- Segment/mix: recreate disclosed segment tables; quantify mix only when segment data supports it.
- Volume/price/mix: decompose only with required source inputs; otherwise keep causal narrative qualitative and label missing inputs.
- Margin/opex: separate mix, price, input costs, utilization, FX, one-time items, cash opex, SBC, and run-rate versus temporary items.
- Cash quality: CFO, capex, FCF, working capital, accruals, reserves, pull-forward/deferral language when evidenced.

## Guidance and Outlook

Capture metric, period, low/high/mid, units, GAAP/non-GAAP, assumptions, and source tag. Qualitative guidance remains exact wording; do not invent numeric ranges. Multiple currencies or reported/CC guidance stay separate.

## Transcript

Scan guidance caveats, demand indicators, margin/opex commentary, risks/constraints, and Q&A pushback. Full deep dives must include a transcript/Q&A and debate-map section. Quotes or paraphrases need section, speaker, questioner name, firm if available, answering executive, topic, source tag, why it matters, bull/bear implication, falsifier/next check, and driver/thesis impact. If the transcript is unavailable, keep the section and label the missing artifact rather than omitting it.

## Model Update Logic

1. Update actual quarter actuals/KPIs from authoritative sources.
2. Update forward drivers only when guidance or analyst-derived assumptions support the change.
3. Map every update to `DriverID`, period, old/new value, source tag, why, and confidence.
4. Use audit-ready model update mode only when the user supplies or references a model/workbook, driver registry, output registry, normalized CSVs, model-update inputs, or explicit data to update the model.
5. Use packet mode unless the user supplies a prior workbook/registry and asks for apply.
6. Diff the story: key drivers, output deltas, guide/estimate bridge, and open items; suppress formatting noise.

## Sector Adaptation

Use only KPIs that matter this quarter:

- SaaS/subscription: ARR, RPO/cRPO, NRR/GRR, churn, seats/customers, ARPU, billings, FCF margin.
- Semis/hardware: units, ASP, backlog, book-to-bill, channel inventory, utilization, capacity, gross margin guide.
- Banks/financials: NII, NIM, loan/deposit growth, beta, PCL, charge-offs, CET1, efficiency ratio.
- Consumer/retail: comps, traffic, ticket, pricing/promo, shrink, inventory, markdowns.
- Industrials/services: orders, backlog, book-to-bill, utilization, labor, pricing, end-market mix.
- Internet/ads/marketplaces: DAU/MAU, ARPU, impressions, pricing, engagement, take rate, merchant/account growth.
- Insurance/energy/travel: use loss/combined ratios; production/realized price/LOE/capex; RASM/CASM/load factor/fuel, respectively.

## QA

Before delivery, confirm source tags, unit/scale consistency, estimate definitions, GAAP/non-GAAP labels, EPS quality screen completion, precise absence labels, quote completeness, no unresolved placeholders, and visible source limitations.

## PM Post-Print Judgment

Start from thesis change, estimate revision direction, valuation support, and position action. Separate headline results, clean results, guidance delta, call-only commentary, management credibility, Street revision implications, and next falsifier.
