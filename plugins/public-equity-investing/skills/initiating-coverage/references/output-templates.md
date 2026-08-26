# Output Templates

## Standalone HTML Long-Only Initiation Report

Use this as the normal first-read initiation surface. It should open with one clear research posture, the central ownership debate, a concise evidence snapshot, and the gating work still required. Keep one decision block rather than repeating the conclusion across dashboard-style tiles.

For a capital-intensive or financing-risk thesis, include an early `Capital Return And Funding Gate` with capex, pro forma fully diluted capitalization, debt/lease/dilution exposure, interest burden, cash conversion or after-financing return proof, valuation implication, and missing evidence. Treat equity-value-to-revenue metrics as preliminary context until this gate is supported.

When a target price or ownership recommendation cannot yet be supported, use `Preliminary initiation underwrite` or `Watchlist initiation` as the visible posture and identify the work needed to complete coverage.

Separate `Evidence confidence` from `Underwriting status`: source reliability and investability are different judgments. Include current price, market capitalization, enterprise-value inputs, consensus context, and their as-of timestamps when obtainable; show unavailable valuation inputs as explicit missing evidence rather than silently excluding market context.

Use plain-English metric labels in the first-read layer. For example, prefer `Pro Forma Net Debt + Recorded Leases` to shorthand such as `PF Recognized Claims`.

## Initiation Report Support Note / Renderer Input

```markdown
# [Company / Ticker] Initiating Coverage
Prepared: [date] | Data cut-off: [date/time] | Mode: [mode]
Rating/View: [rating] | Target price: [target] | Current price: [price] | Implied return: [%]
Market data as-of: [date/time and source] | Market cap / EV: [values or missing inputs]
Evidence confidence: [high/medium/low] | Underwriting status: [complete/preliminary/watchlist/more work required]

## MD / PM-level answer
[one paragraph]

## Investment thesis
1. **[pillar]** - [claim] [source/evidence]
2. **[pillar]** - [claim] [source/evidence]
3. **[pillar]** - [claim] [source/evidence]

## Key debates and variant perception
| Debate | Consensus view | Our view | Evidence | What would change our mind |
|---|---|---|---|---|

## Business and industry overview
[concise overview]

## Model and forecast drivers
| Driver | Historical baseline | Forecast assumption | Sensitivity | Evidence |
|---|---|---|---|---|

## Valuation and target price
[method, math, implied multiple, sensitivities]

## Catalysts and timeline
| Timing | Catalyst | Expected read-through | Evidence | Risk |
|---|---|---|---|---|

## Risks and disconfirming evidence
| Risk | Thesis impact | Leading indicator | Downside case | Mitigant/monitoring |
|---|---|---|---|---|

## Source register, conflicts, and assumptions
[table]
```

## Buy-side PM memo format

```markdown
# [Company / Ticker] Buy-Side Initiation

## Decision
[long / short / watchlist / avoid / more work needed]

## Variant perception
[what we believe vs market]

## Why now
[catalyst and timing]

## Risk/reward
[base/upside/downside, path, skew]

## Thesis kill signals
[signals]

## Position considerations
[liquidity, sizing considerations, hedge/pair ideas if requested]
```

## Sell-side initiation summary box

```markdown
| Field | Value |
|---|---|
| Rating | [rating] |
| Target price | [target] |
| Current price | [price] |
| Upside/downside | [%] |
| Market cap / EV | [values] |
| Primary valuation | [method] |
| Key catalyst | [catalyst] |
| Key risk | [risk] |
| Data cut-off | [date] |
```

## Source request checklist output

```markdown
## Missing sources needed before publication
- Latest 10-K / 10-Q / interim report
- Latest earnings release and transcript
- Investor deck
- Consensus estimates
- Current share price and diluted shares
- Net debt and non-operating assets/liabilities
- Peer set and trading multiples
- Sector-specific KPIs
- Existing model or forecast assumptions
- Compliance/disclosure language if external publication
```
