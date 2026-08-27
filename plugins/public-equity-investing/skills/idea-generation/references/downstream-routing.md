# Downstream Workflow Routing

Use this reference to route idea-generation candidates to the right next skill or workstream. The goal is to make idea generation the top-of-funnel router, not to over-solve every idea in the initial screen.

## Public Equity Investing skills

### `equity-model-update`

Route here when the next step is to update or build the company model.

Triggers:
- Consensus bridge, guidance mismatch, margin bridge, EPS/EBITDA/FCF revision work.
- Segment model required.
- Valuation depends on normalized earnings or KPI rebuild.
- Recent filing, earnings release, transcript, KPI disclosure, or investor day changed the numbers.

Handoff fields:
- Ticker, setup type, key model debate, source documents, consensus concern, KPIs to update, base/upside/downside questions.

### `earnings-preview`

Route here when the candidate has an upcoming print or guidance event.

Triggers:
- Earnings within the catalyst window.
- The idea depends on whether the next print validates revisions, margin improvement, demand slowdown, or guidance reset.

Handoff fields:
- Consensus expectations, buy-side debate, KPIs to watch, likely questions, stock setup, upside/downside scenarios.

### `earnings-deep-dive`

Route here for post-print moves or results-driven screens.

Triggers:
- Large post-earnings stock move.
- Estimate revisions after print.
- Guidance change.
- Market reaction appears too harsh or too optimistic.

Handoff fields:
- Reported vs consensus, guidance delta, transcript issues, stock reaction, thesis implication.

### `long-short-pitch`

Route here when an idea is sufficiently developed to become an investable recommendation.

Triggers:
- Variant view is defined.
- Model or valuation work exists or can be completed.
- Catalyst path and risks are clear.
- PM wants a full long/short recommendation.

Handoff fields:
- Thesis, variant perception, valuation/risk-reward, catalyst path, key risks, position framing, hedge considerations.

### `thesis-tracker`

Route here for ongoing monitoring.

Triggers:
- Candidate moves from screen to active research or portfolio watch.
- Need confirm/disconfirm signals, KPIs, catalysts, and kill criteria.

Handoff fields:
- Thesis statement, must-be-true items, invalidation tests, KPIs, catalyst dates, risk flags, current status.

### `portfolio-risk-management` - `hedge_design`

Route here when the idea is attractive but has unwanted exposure.

Triggers:
- Sector beta, market beta, macro, rates, FX, commodity, factor, or style exposure should be neutralized.
- Pair trade or basket construction is needed.
- Options hedge, proxy hedge, or basis-risk analysis is needed.

Handoff fields:
- Core alpha thesis, exposures to hedge, acceptable basis risk, time horizon, liquidity constraints, candidate peers/indices.

### `event-driven-analyzer`

Route here when an event drives the setup.

Triggers:
- M&A, merger arb, spin, split-off, activism, strategic review, litigation, regulatory, restructuring, index event, lockup, tender, buyback, or recapitalization.

Handoff fields:
- Event type, timeline, probability, downside if failed/delayed, key approvals, legal/regulatory milestones, valuation of outcomes.

### Credit Markets

Route here when credit instruments, creditworthiness, or capital-structure priority are the primary question; retain only listed-equity read-through locally.

Triggers:
- Maturity wall, refinancing risk, covenant risk, high leverage, CDS/spread dislocation, debt trading poorly, liquidity runway issue, restructuring risk, or equity-credit divergence that could change common-equity downside or require Credit Markets work.

Handoff fields:
- Debt stack, maturities, liquidity, CDS/spread or debt-price signals, leverage, FCF, covenant concerns, suspected value break, and explicit Credit Markets handoff need.

### `economic-impact-report`

Route here when the idea depends on macro variables.

Triggers:
- Rates, yield curve, inflation, central bank policy, FX, commodities, credit spreads, sovereign risk, or cross-asset transmission.

Handoff fields:
- Macro variable, sensitivity, transmission channel, securities affected, scenario questions.

### `catalyst-calendar`

Route here when event timing needs to be tracked.

Triggers:
- Multiple names with upcoming earnings, conferences, trial data, regulatory decisions, lockups, product launches, investor days, M&A deadlines, or macro prints.

Handoff fields:
- Ticker, event, date/window, importance, expected evidence, owner, status.

### `portfolio-risk-management` - `position_sizing`

Route here when the user asks how to size or risk-manage an idea.

Triggers:
- Position size, drawdown, beta, factor risk, stop-loss, liquidity, scenario P&L, VaR, or portfolio exposure.

Handoff fields:
- Thesis, scenarios, liquidity, volatility, factor exposures, portfolio constraints, hedge candidates.

## Shared-core skills

### `financial-source-of-truth`

Use when source hierarchy, stale-data review, citations, or fact/assumption labeling is central.

### `financials-normalizer`

Use when inputs include messy filings, PDFs, VDR exports, statements, or non-standard financials that must be normalized before screening.

### `excel-data-cleaner`

Use when raw spreadsheet data needs cleaning, headers/units/date repair, or QA flags before analysis.

### `model-audit-tieout`

Use when a user-supplied model must be audited before relying on it for idea ranking.

### `scenario-sensitivity-generator`

Use when a candidate needs upside/downside, breakeven, stress, or scenario ranges.

### `memo-builder`

Use when the output should become an IC, investment, credit, client, or committee memo.

### `deck-report-qc`

Use before sending a deck/report to senior or external audiences.

### `style-guide-adapter`

Use when the user wants the output to match a firm/client precedent.

### `company-tearsheet`

Use to establish a concise source-backed company profile before deeper work.

### `meeting-prep`

Use when the idea-generation output needs to become meeting questions, management diligence asks, or PM discussion prep.

## Valuation, credit, and diligence intersections

Use local Public Equity Investing skills when an idea needs deeper work:

- `comps-valuation`, `dcf-model-builder`, `three-statement-model-builder`, and `scenario-sensitivity-generator`: if the user needs valuation, model rebuild, SOTP, comps, DCF, downside, or sensitivity work.
- Credit Markets: if recovery, claim priority, liquidity, maturity wall, refinancing, or distressed-security value drives the idea.
- `company-tearsheet`, `financial-source-of-truth`, `financials-normalizer`, and `meeting-prep`: if the candidate requires profile, evidence, normalization, or management/expert-call readiness before deeper analysis.

## Handoff format

When routing, provide a compact handoff block:

- Candidate:
- Direction/setup:
- Why it surfaced:
- Variant wedge:
- Why now/catalyst:
- Main risks:
- Data gaps:
- Next workflow:
- Specific question for next workflow:

Example:

"Route ABC to `equity-model-update`: rebuild the FY2 segment margin bridge and compare management cost-save targets to consensus. The idea only graduates from watchlist if the model shows EBITDA revisions can continue without assuming heroic revenue recovery."

## PM Routing

Route screen triage to idea-generation, investability and expression to long-short-pitch, formal memos and sell-side/client notes to memo-builder, portfolio monitoring to thesis-tracker, event math to event-driven-analyzer, and credit-first work to Credit Markets.
