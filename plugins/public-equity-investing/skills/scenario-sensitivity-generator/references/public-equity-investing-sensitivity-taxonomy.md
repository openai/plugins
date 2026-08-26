# Public Equity Investing Sensitivity Taxonomy

Use this reference when selecting sensitivity exhibits. Keep `SKILL.md` lean; load this file only when the user needs a full scenario pack or when choosing among multiple table types.

## 1. `price_target_scenario`

Purpose: compare bull/base/bear or custom price-target cases.

Use when:
- the user needs upside/downside/skew around a common stock, ADR, listed equity, ETF/index constituent, or equity-linked expression used by a public-equity investor;
- an initiation, long/short pitch, memo, or PM update needs probability-weighted value;
- the debate is whether expected return compensates for downside.

Minimum inputs:
- current or anchor share price;
- scenario price targets;
- probabilities if probability-weighted value is requested.

Interpretation:
- Do not treat a probability-weighted target as a recommendation by itself.
- Call out whether the case depends on multiple expansion, EPS revisions, event success, or macro easing.

## 2. `valuation_sensitivity`

Purpose: translate valuation assumptions into implied price or value.

Use when:
- target price depends on EV/EBITDA, P/E, P/B, P/TBV, P/FFO, NAV, or SOTP assumptions;
- public comps or a DCF output need a market-implied cross-check;
- the question is "what multiple is required to justify the current price?"

Minimum inputs:
- EBITDA and net debt plus shares for EV/EBITDA;
- EPS and P/E multiple for P/E;
- relevant sector metric for sector-specific overlays.

Interpretation:
- Separate mechanically implied price from underwriteable price.
- Use `comps-valuation`, or `dcf-model-builder` when the valuation mechanics themselves need to be built.

## 3. `eps_revision_sensitivity`

Purpose: test how estimate revisions and multiple changes interact.

Use when:
- pre-earnings or post-earnings work depends on EPS, EBITDA, FCF, or revenue revision risk;
- a stock's move depends on both numbers and multiple;
- market reaction to a print is likely to be nonlinear.

Minimum inputs:
- EPS or EBITDA base;
- base multiple;
- revision and multiple-change ranges.

Interpretation:
- Distinguish clean estimate revisions from low-quality beats.
- Pair with `earnings-preview`, `earnings-deep-dive`, or `equity-model-update` when source data needs updating.

## 4. `kpi_driver_sensitivity`

Purpose: connect sector drivers to financial output.

Use when:
- a sector KPI drives the thesis more than broad revenue growth;
- the user asks what a change in NIM, ARR, NRR, GMV, take rate, NOI, occupancy, loss ratio, production, or volume means;
- the base model can be approximated with revenue and margin flow-through.

Minimum inputs:
- revenue or KPI base;
- margin, incremental margin, or flow-through assumption;
- shock ranges.

Interpretation:
- Name the actual sector KPI in the final answer.
- Do not pretend the table is model-validated if it is a high-level flow-through approximation.

## 5. `equity_liquidity_downside`

Purpose: translate downside into liquidity and balance-sheet pressure.

Use when:
- a public issuer has maturity wall, refinancing, covenant-pressure, liquidity, or common-equity recovery read-through risk;
- downside survives on EBITDA but fails on cash;
- Credit Markets output needs to be summarized as a common-equity stress table.

Minimum inputs:
- cash, revolver or other liquidity, minimum liquidity threshold;
- FCF or cash burn;
- next-12-month maturities;
- debt and EBITDA for leverage.

Interpretation:
- Show absolute liquidity and headroom, not only deltas.
- Route deeper credit analysis to Credit Markets.

## 6. `event_probability_tree`

Purpose: model probability-weighted outcomes for special situations.

Use when:
- M&A, tender, CVR, litigation, regulatory, spin, activism, restructuring, index inclusion, or liability-management outcomes drive value;
- the debate is probability, downside, timing, or spread.

Minimum inputs:
- success price;
- fail price;
- probability range;
- anchor price.

Interpretation:
- Treat timing, borrow, financing, legal/regulatory risk, and liquidity as separate caveats.
- Route event facts and process analysis to `event-driven-analyzer`.

## 7. `macro_factor_sensitivity`

Purpose: test public-equity exposure to rates, credit-spread signals, FX, commodities, inflation, or policy variables.

Use when:
- rate or credit-spread-signal moves affect valuation, common-equity downside, multiples, or FCF;
- FX or commodity variables are the key swing factor;
- a macro shock needs a quick translation into security impact.

Minimum inputs:
- factor sensitivity per unit move;
- anchor price or model output;
- factor move range.

Interpretation:
- Keep factor sensitivity source-labeled and tied to a stock, sector, estimate, valuation, or portfolio-action implication.
- Route broader macro chain-of-impact analysis to `economic-impact-report`.

## 8. `thesis_trigger_table`

Purpose: convert scenarios into concrete monitoring and decision rules.

Use when:
- a thesis needs confirm/disconfirm markers;
- a PM needs add/trim/hedge/exit levels;
- a memo needs exact watch items and what would change the view.

Minimum inputs:
- trigger;
- threshold;
- implication;
- next action or next skill.

Interpretation:
- Do not use vague "monitor" language without a threshold.
- Route persistent monitoring to `thesis-tracker`.

## Credit Markets Boundary

Use `equity_liquidity_downside` only when liquidity, maturity, or refinancing risk changes common-equity value, dilution risk, or solvency optionality. Route credit-security valuation, recovery waterfall, covenant-package analysis, spread/yield relative value, CDS, bond comps, and loan comps to Credit Markets.
