# Scenario Overlay Contract

When scenarios need to feed a workbook, memo, deck/report, or another skill, produce a scenario overlay table with these fields.

| field | purpose |
|---|---|
| version | model, note, or source version |
| scenario | bull, base, bear, stress, success, fail, delay, credit stress, macro shock |
| setup_type | equity, credit, distressed, event-driven, macro, earnings, valuation, thesis |
| module | revenue, EPS, EBITDA, FCF, KPI, valuation, multiple, liquidity, recovery, event, macro |
| driver | exact driver being changed |
| baseline_value | current base-case value |
| scenario_value | proposed case value |
| delta_type | absolute, percentage change, bps change, replacement, timing shift, probability, floor, cap |
| start_period_or_event | first affected period or event milestone |
| end_period_or_event | last affected period or milestone |
| rationale | why the change belongs in the case |
| evidence_label | sourced, derived, user_provided, analyst_assumption, placeholder |
| source_id | source reference or missing |
| impacted_output | price target, EV, EPS, EBITDA, FCF, spread, liquidity, recovery, return, thesis status |
| investment_implication | add, trim, hedge, avoid, monitor, update model, escalate credit, no conclusion |
| caveat | limitation, missing source, stale input, or model-readiness issue |

## Handoff Rules

- Use one row per changed driver per scenario.
- Do not hide formula changes inside scenario cases.
- Keep actual periods locked unless explicitly modeling pro forma or restated history.
- If the overlay contains placeholders, label them and keep the scenario status as not model-validated.
- Do not represent an overlay as a complete model rebuild.

## Equity Scenario Skew Contract

Every public-equity scenario package should show expected return versus hurdle, downside/upside ratio, break-even probability when calculable, kill/add/trim/exit thresholds, skew label, current-price anchoring, source posture, and whether upside is underwriteable or merely optical. Use Credit Markets for credit-security stress, recovery waterfall, covenant-package, spread/yield, or debt valuation outputs.
