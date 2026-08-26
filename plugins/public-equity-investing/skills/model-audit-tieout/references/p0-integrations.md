# Public Equity Investing Skill Integrations

## Role of model-audit-tieout

This skill is the quality-control and review layer for existing public-equity financial models. It should not replace model-builder skills or Credit Markets. It should help decide whether a model is usable, what breaks, what does not tie, and what must be fixed before the output is used in an investment, client, PM, or committee decision.

## Integration rules

### financial-source-of-truth
Use for source hierarchy, stale-data standards, citation format, evidence labels, assumption/fact separation, and source conflicts.

Typical handoff:
1. model-audit-tieout identifies key model drivers and unsupported or conflicting values.
2. financial-source-of-truth establishes the controlling source and evidence posture.
3. model-audit-tieout updates the issue log and tie-out ledger.

### excel-data-cleaner
Use before audit when the workbook or data extract is too messy to review reliably.

Trigger examples:
- source tabs have merged, duplicated, or ambiguous headers
- row grain is unclear
- imported data has mixed date/number formats
- category labels are inconsistent
- raw exports need normalization before tie-out

### three-statement-model-builder
Use after audit when an integrated operating model needs to be rebuilt, extended, or corrected.

Audit focus before handoff:
- balance sheet and cash flow checks
- working capital, debt, capex, and tax logic
- forecast driver support
- scenario design

### dcf-model-builder
Use after audit when a valuation model needs to be built or remediated.

Audit focus before handoff:
- source-supported historicals
- forecast assumption support
- wacc and terminal value logic
- ev-to-equity bridge
- valuation sensitivity table integrity

### comps-valuation
Use when the model audit finds issues in peer selection, market data, valuation multiples, calendarization, or implied valuation ranges.

Audit focus:
- peer rationale
- market cap, enterprise value, net debt, shares, and currency
- ltm/ntm metric source and normalization
- outlier treatment
- valuation range precision

### equity-model-update
Use after audit when a public-company model needs to be refreshed from new actuals, guidance, consensus, transcripts, filings, KPIs, share count, net debt, or market data.

Audit focus:
- actuals and estimate bridge
- guidance and consensus as-of dates
- segment and KPI definitions
- share count, net debt, and EV bridge
- model change log and source support

### Credit Markets
Use after audit when credit-instrument, distressed, refinancing, maturity wall, recovery-waterfall, covenant-package, or capital-structure analysis needs to be corrected or expanded outside this plugin.

Public Equity audit focus before handoff:
- debt schedule and maturity wall as common-equity risk inputs
- liquidity runway
- covenant-pressure disclosure and source support
- recovery read-through or valuation-cushion assumptions
- CDS/spread/yield/price signals and source timestamps

Route covenant-package interpretation, debt-security valuation, recovery waterfall, and credit memo work to Credit Markets.

### memo-builder
Use after audit to turn findings into a decision memo or IC section.

Audit output to pass forward:
- readiness posture
- unresolved critical/high issues
- key source-supported findings
- assumptions requiring sensitivity
- decision-impact caveats
- open evidence requests

### earnings-preview and earnings-deep-dive
Use when the model supports pre-earnings or post-earnings analysis.

Audit focus:
- consensus and guidance as-of dates
- quarter/period alignment
- reported vs adjusted metrics
- KPI definitions
- model update bridge
- transcript/source support

### economic-impact-report
Use when a market, macro, regulatory, geopolitical, rate, commodity, or policy shock drives model changes.

Audit focus:
- current market data
- scenario coherence
- second-order effects
- exposure mapping
- stale assumptions after the event

### event-driven-analyzer and economic-impact-report
Use when the model supports event-driven, special-situation, macro, policy, rate, commodity, FX, or cross-asset analysis.

Audit focus:
- transaction or event terms
- probability and scenario math
- timing, gating milestones, and downside
- market/macro assumptions and source timestamps

### deck-report-qc
Use when model outputs appear in a deck, report, memo, board pack, or client deliverable.

Audit focus before handoff:
- model output values to deck values
- units, periods, currency, and rounding
- footnotes and source citations
- chart labels and narrative consistency

## Recommended P0 workflow examples

### Public equity valuation review
1. financial-source-of-truth validates filings, market data, consensus, and transcript support.
2. model-audit-tieout audits 3-statement, DCF, and comps model outputs.
3. dcf-model-builder, three-statement-model-builder, equity-model-update, or comps-valuation remediates if needed.
4. memo-builder, long-short-pitch, or earnings-deep-dive uses only decision-ready outputs.

### Credit Markets review
1. financial-source-of-truth establishes source hierarchy for filings, credit docs, ratings, market data, and lender materials.
2. model-audit-tieout audits debt schedule, covenant, liquidity, recovery, and downside calculations.
3. Credit Markets prepares any credit-instrument memo, covenant-package review, or recovery waterfall.
4. deck-report-qc reconciles the committee or client deck/report to the model.
