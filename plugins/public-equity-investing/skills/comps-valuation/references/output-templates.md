# Output Templates

## Standard comps memo

Use these sections in order:

1. `Executive Summary`
2. `Peer Set And Rationale`
3. `Core Comps Table`
4. `Stats And Outliers`
5. `Valuation Read-Through`
6. `QA Flags And Caveats`
7. `Open Items / Data Requests`
8. `Comps Output Posture`

## Standalone HTML comps report

When report mode calls for a substantive reusable or HTML artifact, produce a polished standalone HTML comps report following `../../../shared/html-artifact-standard.md`. Keep peer selection, valuation evidence, and the premium or discount question central rather than forcing a standardized dashboard shell.

Recommended first-read sequence:

1. Valuation read: whether the premium or discount is supported and the most important unresolved proof point.
2. Metric strip: four or five sourced items covering current price, primary multiple, relative premium or discount, supportable implied value range if available, and the key operating proof point.
3. Peer-set rationale: Core, Secondary, and Excluded peer roles with concise decision-relevant reasons.
4. Core trading-comps table: prices, EV bridge basis, denominators, multiples, growth/margin context, and as-of/source posture.
5. Premium or discount bridge: why growth, margins, business model, scale, or data quality support or fail to support the selected relative valuation.
6. Valuation posture, material evidence gaps, and concise source ledger.

Label forward data as `third-party forward estimates` unless the source and as-of basis support calling it `consensus`; do not allow aggregator-sourced estimates to imply unverified consensus breadth.

Do not turn an ordinary comps report into an action-rules dashboard. Without requested portfolio action or supplied holding and mandate context, use a valuation posture rather than add, trim, hedge, sizing, or exit instructions.

## Core comps table

Default corporate table:

| Company | Ticker | Peer role | Market data as-of | EV | LTM revenue | LTM EBITDA | NTM revenue | NTM EBITDA | EV/LTM rev | EV/NTM rev | EV/LTM EBITDA | EV/NTM EBITDA | Notes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|

Use fewer fields for narrower tasks and add module-specific columns for banks, insurers, REITs, asset managers, exchanges, distressed companies, or private-company targets.

## Screen-grade fallback table

Use this when live market data, current estimates, or source files are unavailable. This is better than returning no output, but it must not imply a valuation conclusion.

Lead with:

`Comps posture: screen-grade; missing market data and/or estimates are explicitly labeled.`

Fallback table:

| Company / candidate | Ticker | Proposed role | Why it belongs / should be tested | Why it may not be clean | Required market / financial fields | Source requirement |
|---|---|---|---|---|---|---|

Acceptable missing-value labels:

- `TBD`
- `not sourced`
- `TBD / not sourced`
- `not provided`
- `requires market data`
- `requires consensus`

Do not use `0.0x`, `NM`, or blank cells to hide missing data. `NM` is only for true negative or non-meaningful denominators after the denominator is known.

Include a `Missing source requirements` section immediately after the fallback table when any metric is unsourced.

## Target valuation add-on

Add these sections when a target is present:

1. `Selected Multiple Set`
2. `Implied Enterprise Value`
3. `Bridge To Equity Value`
4. `Implied Value Per Share`, if applicable

Suggested table:

| Metric | Low | Mid | High | Basis / caveat |
|---|---:|---:|---:|---|
| Selected multiple |  |  |  |  |
| Target denominator |  |  |  |  |
| Implied EV |  |  |  |  |
| Net debt / other claims |  |  |  |  |
| Implied equity value |  |  |  |  |
| Diluted shares |  |  |  |  |
| Implied value per share |  |  |  |  |

## QA review

For `qa-review`, return:

1. critical findings first, ordered by severity;
2. broken definitions or inconsistent numerators and denominators;
3. weak peer logic or cherry-picking concerns;
4. missing caveats, stale data, unsupported adjustments, or source conflicts;
5. a verdict: `usable`, `usable with conditions`, or `not reliable`.

## Data request table

When more data would materially improve the answer, use:

| Priority | Needed item | Why it matters | Affected output | Minimum acceptable substitute |
|---|---|---|---|---|

Ask for exact missing fields, not a generic data dump.

For fallback comps, default P0 items are current share price/as-of date, share count/dilution, cash/debt/EV bridge, LTM denominators, NTM estimates/as-of date, and source-supported peer rationale.

## Comps output posture

Use one posture label:

- `decision-useful`: peer set, market data, denominators, and EV bridges are current enough and caveated appropriately.
- `usable-with-caveats`: output is directionally useful but has missing fields, stale data, or peer-set limitations.
- `screening-only`: useful for early discussion, not enough support for a decision range.
- `not-reliable`: source conflicts, missing primary data, stale market data, or denominator problems make the output unsafe to rely on.
