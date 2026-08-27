# Output Templates and QA

## Public Equity Investing Trigger Table

For thesis, earnings, valuation, equity-liquidity read-through, event, or macro-factor scenarios, include:

| trigger | threshold | source / monitoring cadence | likely interpretation | action implication | next workflow | deadline |
|---|---:|---|---|---|---|---|

Default trigger categories:
- EPS, EBITDA, revenue, FCF, or guidance revision.
- Sector KPI threshold such as ARR, NRR, NIM, loss ratio, NOI, occupancy, production, take rate, or volume.
- Valuation support such as target multiple, discount to NAV, DCF-implied price, expected return versus hurdle, or break-even probability.
- Liquidity, maturity wall, refinancing, dilution, or common-equity downside threshold.
- Event probability, approval, court, vote, regulatory, financing, or timing milestone.
- Macro factor such as rates, FX, commodity, credit-spread signal, inflation, or policy move, only as a common-equity value or earnings read-through.

Do not stop at "watch this." State what changes if the threshold is hit.

## Scenario Interpretation Table

| scenario | driver change | output impact | source posture | what would change the view | recommended next step |
|---|---|---:|---|---|---|

Use this when the user needs a PM-ready synthesis rather than only raw matrices.

## Public Equity Investing QA Checklist

Before finalizing, confirm:
- scenario labels match the actual assumptions used;
- base case source is named;
- market-sensitive inputs have as-of dates or are labeled stale/missing;
- each case changes the intended drivers only;
- valuation, EPS, KPI, equity-liquidity, event, or macro assumptions are not blended without labels;
- outputs show absolute values and deltas where useful;
- probability-weighted values disclose probability source or assumption status;
- liquidity or downside cases show what breaks first for common equity;
- thesis triggers include thresholds and next actions;
- final language does not turn illustrative math into a recommendation.

## Handoff Outputs

When handing off to another skill, include:
- scenario overlay table;
- table names used;
- base-case source and as-of date;
- exact driver changes and timing;
- output values and deltas;
- trigger metrics and what changes the view;
- model-readiness caveats;
- workbook-QA requirement if Excel was changed or delivered.

## PM Action Threshold Template

Include action thresholds for `add`, `press`, `hold`, `trim`, `exit`, `hedge`, `wait for proof`, and `re-underwrite`. Thresholds must connect to a model line, price/value output, source, and date.
