# Memo Builder Output Contracts

## Default Full Memo Spine

1. `Recommendation / Decision Ask`
2. `Executive Summary`
3. `Thesis and Evidence`
4. `What Must Be True`
5. `Valuation / Scenario Work`
6. `Risks, Disconfirmers, and Mitigants`
7. `Catalysts and Monitoring`
8. `Implementation Considerations`
9. `Open Items / Data Requests`

## `investment-memo`

1. recommendation and decision context
2. company / security / situation snapshot
3. thesis claims with evidence, KPIs, falsifiers, and time-to-truth
4. financial and operating setup
5. valuation and scenario analysis
6. catalyst path and monitoring plan
7. risk register and downside case
8. implementation considerations and constraints
9. open items, data requests, and source caveats

### Standalone HTML Investment Committee Memo

For a substantive buy-side investment committee memo delivered as HTML, use a polished standalone memo layout rather than a dashboard shell. The first read should be compact and decision-forward:

1. recommendation / decision ask and investability posture
2. decision hinge and what is priced in
3. valuation or scenario skew, including downside where supportable
4. source posture or evidence limitation when it changes the action

Continue with the full memo spine below that opening layer. Do not repeat the same recommendation through a hero callout, snapshot tile, and a second full recommendation panel. Use one clear decision block and reserve tables, scenario cards, and monitoring sections for information that advances the underwrite.

When a valuation case relies on forward-period earnings and an exit or terminal multiple over a multi-year horizon, show either discounted present value using an explicit discount rate / required-return assumption or annualized return / IRR against a stated hurdle. Do not present undiscounted terminal value appreciation as sufficient expected-return support for initiation. If evidence supports waiting but not buying, state the posture plainly: sufficient to decline initiation today, insufficient to support initiation.

For HTML citations, cite material figures and claims near their use without fragmenting tickers, prices, EPS ranges, percentages, dates, multiples, or metric labels into separately linked tokens. Visually inspect local HTML with local headless-browser screenshots before delivery, including the opening viewport, valuation/scenario work, and a narrow-screen view.


## `event-driven-committee-note`

1. recommendation and event setup
2. spread, consideration, timing, and break price
3. probability tree and expected value
4. regulatory, legal, shareholder, financing, or process milestones
5. downside and timing risk
6. monitoring and decision gates
7. open items

## `pm-update`

1. `What changed`
2. `Why it matters`
3. `Model / valuation impact`
4. `Thesis impact`
5. `Action options`
6. `Monitoring / next catalyst`
7. `Open items`

If `action options` require trade expression, sizing, add/trim/exit/cover rules, or pair mechanics, hand off to `long-short-pitch`.

## `screen-grade-scratch-memo`

Use when the user wants a memo but supplies only sparse context. Do not collapse into a blank template. Produce:

1. `Source Posture And Intake Checklist`
2. `Minimum Source Packet Required`
3. `First-Pass House View`
4. `Variant Wedge`
5. `What Is Priced In`
6. `Estimate Path`
7. `Valuation / Scenario Skew`
8. `Downside Mechanism`
9. `Catalysts And Time-To-Truth`
10. `Disconfirmers`
11. `Action Rules`
12. `Evidence Needed To Upgrade From Screen-Grade`

The associate gets the build path; the seasoned PM layer must still say what matters, what is missing, and what would change the decision.

## `qa-review`

Return critical findings first, ordered by severity, covering missing sections, weak logic, sourcing risks, downside gaps, catalyst gaps, and memo-readiness verdict: `ready`, `ready with conditions`, or `not ready`.

## Support Table Shapes

Use compact tables for:

- scenario summary: base/upside/downside, probability, price target, expected return, or key valuation bridge, key drivers
- risk register: risk, mechanism, severity, mitigant, monitoring trigger
- source posture: claim, source, as-of, confidence, gap
- what-must-be-true: claim, evidence, KPI, falsifier, timing

## PM Judgment Sections

Every full memo should include `Decision Hinge`, `What Must Be True`, `What Is Priced In`, `Downside Mechanism`, `Measurable Disconfirmers`, `Action Discipline`, and `Missing Evidence`. Sell-side notes include rating/target-price debate and estimate revision bridge. ETF/index notes include mandate, methodology, holdings/weights, tracking-error or benchmark implications, factor exposure, liquidity, and rebalance/corporate-action risk.
