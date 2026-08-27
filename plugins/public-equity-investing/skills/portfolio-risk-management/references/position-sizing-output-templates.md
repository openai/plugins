# Output Templates

## Standalone HTML Integrated Risk Decision Report

For a substantive integrated size-and-hedge decision, use a polished standalone HTML risk decision report following `../../../shared/html-artifact-standard.md`. Structured tables, scenarios, and monitoring triggers are appropriate; do not convert the ordinary report into a standardized dashboard unless explicitly requested.

The first-read layer should include:

| Required first-read block | Content |
| --- | --- |
| `Current Action` | `Conditional risk screen`, `Not implementation-ready`, `Initiate`, `Resize`, `Hedge`, or `Do not initiate`, with the reason. |
| `Constraint Interpretation` | Whether the loss limit is a `scenario loss budget`, an `absolute loss cap`, or unresolved. |
| `Illustrative Unhedged Size` | Show only when tied to a stated adverse-move assumption; never imply it satisfies an absolute cap for a short. |
| `Hard-Cap Compliant Package` | For a short, priced share-for-share long calls or `no position`; include maximum-loss inputs. |
| `Missing Inputs Before Entry` | Executable quote, ADV/exit capacity, borrow/locate and squeeze inputs, portfolio checks, and option terms when needed. |

If current executable price, liquidity/exit capacity, short borrow/locate inputs, or required option-chain terms are missing, do not use `initiate` as the lead action. Label the output `Conditional risk screen` or `Not implementation-ready`, and state which conditional size or hedge package can be evaluated once inputs are available.

For HTML readability, do not fragment tickers, dates, percentages, basis-point amounts, instrument terms such as `GLP-1`, or scenario labels with inline citation links. Prefer compact citations adjacent to complete figures, table-row source columns, or short section-level notes. Visually inspect local HTML with local headless-browser screenshots before delivery.

## Default PM readout

Use this structure unless the user asks for a spreadsheet, deck, or shorter answer.

# Risk Position Sizing - [Security / Trade]

## 1. Decision summary

| Item | Recommendation |
|---|---|
| Action | initiate / add / hold / trim / hedge / avoid / watchlist |
| Recommended size | [% NAV] / [$] / [shares/contracts/notional] |
| Current/proposed size | [if provided] |
| Binding constraint | loss budget / liquidity / volatility / exposure limit / conviction / portfolio fit |
| Loss-limit interpretation | scenario loss budget / absolute loss cap / unresolved |
| Implementation readiness | conditional risk screen / not implementation-ready / executable after checks |
| Confidence | high / medium / low |
| PM judgment | [1-3 sentences on why this is the right size] |

## 2. Trade setup

- Instrument/direction:
- Thesis being expressed:
- Time horizon/catalyst:
- Target/base/downside:
- Key data date/time:
- User-provided facts:
- Assumptions:

## 3. Risk/return case

| Case | Price/return | P&L $ | P&L % NAV | Timing | Notes |
|---|---:|---:|---:|---|---|
| Upside |  |  |  |  |  |
| Base |  |  |  |  |  |
| Downside |  |  |  |  |  |
| Stress |  |  |  |  |  |

## 4. Constraint interpretation and compliant package

| Constraint branch | Size/package | Maximum loss treatment | Current action |
|---|---:|---|---|
| Scenario loss budget |  | Stated adverse move plus cost/reserve assumptions | Conditional size if scenario is accepted |
| Absolute loss cap |  | Priced defined-loss package required for an equity short | Do not initiate without compliant protection |

## 5. Sizing triangulation

| Sizing lens | Implied max size | Constraint status | Interpretation |
|---|---:|---|---|
| Loss budget |  | binding / not binding |  |
| Volatility budget |  | binding / not binding |  |
| Liquidity / exit |  | binding / not binding |  |
| Gross/net/beta limits |  | binding / not binding |  |
| Factor/sector limits |  | binding / not binding |  |
| Conviction/catalyst quality |  | binding / not binding |  |
| Portfolio fit/correlation |  | binding / not binding |  |

## 6. Portfolio impact

| Exposure | Before | Incremental | After | Limit / context | Flag |
|---|---:|---:|---:|---:|---|
| Gross exposure |  |  |  |  |  |
| Net exposure |  |  |  |  |  |
| Beta-adjusted net |  |  |  |  |  |
| Sector exposure |  |  |  |  |  |
| Issuer exposure |  |  |  |  |  |
| Factor exposure |  |  |  |  |  |
| Liquidity bucket |  |  |  |  |  |

## 7. Liquidity and execution

- ADV / dollar ADV:
- Position as % ADV:
- Exit days at selected participation rate:
- Stress-liquidity assumption:
- Borrow/options/equity-risk signal notes:
- Execution recommendation:

## 8. Monitoring rules

| Trigger | Threshold | Action | Owner / cadence |
|---|---|---|---|
| Add |  |  |  |
| Trim |  |  |  |
| Exit / thesis break |  |  |  |
| Risk review |  |  |  |
| Catalyst |  |  |  |

## 9. Open items and QC flags

- Missing data that matters:
- Stale inputs:
- Formula/source tie-out issues:
- Compliance/mandate review items:

## Deterministic support output schema

The shipped calculator writes CSV support tables plus an optional support note, not a native multi-tab workbook. If a workbook is required, create it with a spreadsheet/workbook tool from these CSVs and preserve the source workbook.

### `position_summary.csv`

Columns: analysis_date, security, ticker, direction, entry_price, recommended_size_pct_nav, recommended_notional, recommended_shares_or_units, raw_binding_constraint, raw_binding_size_pct_nav, confidence, proposed_size_pct_nav, current_size_pct_nav

### `sizing_cases.csv`

Columns: sizing_lens, input_value, formula, implied_size_pct_nav, implied_notional, binding_flag, notes

### `scenario_pnl.csv`

Columns: scenario, probability, price_or_return, pnl_dollars, pnl_pct_nav, time_horizon, liquidity_assumption, action_rule, notes

### `exposure_impact.csv`

Columns: exposure_type, before, incremental, after, limit, status, source

### `liquidity_exit.csv`

Columns: security, price, adv_shares, adv_dollars, position_shares, position_dollars, position_pct_nav, participation_rate, days_to_exit, stressed_participation_rate, stressed_days_to_exit, notes

### `monitoring_rules.csv`

Columns: trigger_type, metric, threshold, action, owner, cadence, source

### `support_note.md`

Optional support note with recommended size, binding constraint, scenario P&L, liquidity, and PM caveat. For substantial reusable sizing work, the lead user-facing artifact should be a decision summary, HTML report/dashboard, or workbook/deck surface rather than Markdown.

## Template CSV bundle

`scripts/create_position_sizing_templates.py` writes blank intake CSVs: `trade_setup.csv`, `portfolio_context.csv`, `exposure_impact.csv`, `liquidity.csv`, `scenarios.csv`, `options_overlay.csv`, `pair_legs.csv`, `factor_exposures.csv`, `etf_index_context.csv`, `macro_proxy_inputs.csv`, `monitoring_rules.csv`, and `sources.csv`. Credit-security inputs route to Credit Markets rather than a local template.

## Deck structure

If creating a deck section, use this sequence:

1. Executive sizing recommendation.
2. Trade setup and thesis expression.
3. Risk/return and scenario P&L.
4. Sizing triangulation.
5. Portfolio exposure impact.
6. Liquidity/exit and execution plan.
7. Monitoring rules and decision triggers.
8. Appendix: sources, assumptions, and QC flags.

## Existing-analysis critique format

When reviewing an existing analysis, use:

1. What is directionally right.
2. What is missing or stale.
3. Where the sizing math is fragile.
4. Hidden exposures or basis risks.
5. Liquidity/exit concerns.
6. Recommended revised size and why.
7. Specific edits to make the analysis PM-ready.
