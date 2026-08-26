# Fund Comparison — Full Workflow

Complete execution contract for structural snapshots, targeted analysis, and confirmed HTML report generation.

## Deliverable

The default first deliverable is a Markdown structural snapshot, not HTML. Create one self-contained HTML file, `comparison-[TICKERA]-vs-[TICKERB].html`, only after the user explicitly confirms after seeing that snapshot. No companion chart, PDF, or data files unless the user explicitly requests the underlying JSON. Do not inspect `assets/template.html` during normal report generation.

## Tool Discovery

When the environment requires deferred tool discovery, discover the ID lookup, data, portfolio
analysis, and analyst research tools in one search before Batch 1. Do not search for or invoke an
authentication tool unless a Morningstar call reports an authentication failure.

## Execution Discipline

Reuse all valid results from the current comparison session. Retrieve only fields still required
for the requested analysis or report. Group independent calls into the fewest supported concurrent
batches; if the environment cannot execute them concurrently, issue them without intervening
planning, status output, or other nonessential work. After the user confirms a full report, follow
the direct path: retrieve, validate, render, and deliver. Add intermediate steps only to resolve
missing data, ambiguity, or an error.

## User-Facing Language

This document's section names, step labels, and internal identifiers — "Batch 1", "Batch 2", "Assemble `D`", `D` itself, datapoint IDs (e.g. `OF003`, `OS385`), rule numbers ("rule 1–3"), `meta.cross_category_warning`, "gate", "structural read", and similar — are internal execution scaffolding, not user-facing vocabulary. Never mention these names, labels, or IDs in a response to the user, including in status updates, tables, or explanations of what you're about to do. Describe the same actions in plain comparison language instead (e.g. say "looking up both tickers" rather than "running Batch 1", say "Morningstar Category" rather than `OF003`). This applies throughout every stage below.

## Batch 1 — Resolve Identifiers

Call `morningstar-id-lookup-tool` once with both fund identifiers.

- Proceed only for FE (ETF), FO (open-end), FC (closed-end). Exclude ST; notify the user.
- If a fund is inactive (`OS999`), exclude and notify. Stop if fewer than 2 valid funds remain.
- Prefer exact ticker on ambiguous match; ask if still ambiguous.
- Store both investment IDs.

Do not repeat this call unless the result failed, was incomplete, or was ambiguous.

## Batch 2 — Structural Snapshot

When Batch 1 IDs return, immediately issue all three independent calls as one concurrent batch where supported. Do not produce text output or start a separate planning step between receiving Batch 1 results and issuing these calls:

1. `morningstar-data-tool` — both investment IDs, only the snapshot datapoints below.
2. `portfolio-analysis: asset_allocation` for Fund A.
3. `portfolio-analysis: asset_allocation` for Fund B.

### Snapshot Datapoints

| Datapoint | ID | Used for |
|---|---|---|
| Fund name | `OS01W` | meta, overview |
| Ticker | `OS385` | meta, overview |
| Vehicle type | `LS466` | overview |
| Morningstar Category | `OF003` | comparability, overview |
| Fund Inception Date | `OS00F` | overview |
| Index Fund | `OF00C` | derive Active / Index (non-ETFs) |
| Actively Managed | `OF00D` | derive Active / Index (ETFs) |
| Primary Prospectus Benchmark | `OF00L` | comparability, overview |
| % Assets in Top 10 Holdings | `HS07J` | portfolio characteristics |
| Net Expense Ratio | `OS00M` | overview |
| Fee Level — Broad | `UB412` | overview |
| Turnover Ratio % | `OS03S` | portfolio characteristics |

Retain this result for the current comparison session. Do not repeat the snapshot call unless it failed, was incomplete, ambiguous, or either ticker changes.

### Asset Allocation Result

`asset_allocation` returns net % by: US equity, non-US equity, bonds, cash, other. Use `asset_allocation.portfolio`. Retain both results for the current comparison session; they determine eligibility for later composition calls and are never repeated for a confirmed report.

## Structural Snapshot and Decision

After Batch 2, always show two compact Markdown tables followed by a short structural read. Do not generate HTML or automatically retrieve the full report dataset at this stage, even if the initial request asked for a report or HTML.

### Required Snapshot Tables

**Fund profile:** Vehicle Type, Morningstar Category, Active / Index, Primary Benchmark, Top 10 Holdings, Turnover, Net Expense Ratio.

**Broad portfolio exposure:** US Equity, Non-US Equity, Bonds, Cash, Other.

Use `N/A` for unavailable values. If a tool call failed, make that clear in a brief limitation note.

### Structural Read

Use the first applicable rule and lead with a factual contrast, not only the name of the comparison level:

1. Different Morningstar Categories: name each fund's category and, when available, the different benchmarks or mandates.
2. Same category, material allocation difference: state the largest allocation contrast with the two values.
3. Same category and similar allocation, different active/index status: state the actual implementation contrast, including each benchmark when available (for example, `SPY tracks the S&P 500 while QQQ tracks the Nasdaq-100`).
4. Same category and similar implementation: use a similarity-first read. Say the funds are structurally similar or near substitutes, name the shared category, implementation, benchmark, and broad allocation where available, then identify any practical distinctions such as vehicle type, cost, access, or finer portfolio positioning. Do not call the absence of a difference the “main difference,” and do not imply that vehicle type or fees drive performance/risk differences.

Set `meta.cross_category_warning = true` when the non-missing `OF003` values differ; otherwise set it to `false`. Ground later narratives in this structural result.

For rules 1–3, use this lead-in, replacing the bracketed text with the factual contrast identified above:

> The main difference likely to drive performance and risk differences is that **[factual contrast]**.

For rule 4, use this lead-in instead:

> Structurally, **[Fund A]** and **[Fund B]** are near substitutes: **[shared structural facts]**. The practical differences are **[actual remaining distinctions]**.

Then offer the two paths in one compact paragraph:

> I can examine a specific area further (for example regional exposure, style, sectors, or fixed-income positioning), or **generate a full HTML comparison report** covering fund identity, structure, management, and cost; structural composition and eligible holdings breakdowns; returns and category ranks; risk; ratings; and analyst research with a concise synthesis. How would you like to proceed?

## Targeted Follow-up

When the user asks a focused follow-up, retrieve only the relevant data and show compact Markdown tables plus a structural interpretation. Do not retrieve unrelated report data or create HTML. End with the same compact full-report offer above.

| Question area | Calls |
|---|---|
| Regional exposure | `equity_regional_exposure` for each fund with equity ≥ 10% |
| Equity positioning | Eligible `equity_style`, `equity_sectors`, and/or `equity_regional_exposure` |
| Fixed-income positioning | Eligible `fixed_income_style`, `fixed_income_sectors`, and/or `fixed_income_maturity` |
| Active management | Relevant snapshot fields plus manager datapoints, equity/fixed-income positioning only when needed |
| Performance and risk | Supplemental return, category-rank, and risk datapoints only |

Reuse prior targeted results in the same comparison session. If the user confirms HTML, retrieve any data still needed for the full report; do not repeat cached calls or datapoints.

## Confirmed Full Report — Supplemental Data and Detail

Only an explicit confirmation after the snapshot, such as “Generate the full report,” “Yes, make the HTML,” or “Proceed with the full comparison,” starts this stage.

Immediately issue all of the following as one concurrent batch where supported, before receiving any of their results:

1. `morningstar-data-tool` for both IDs with every full-report datapoint below that was not already retrieved in the snapshot.
2. All eligible calls in the table below.

Eligibility is already known from the cached asset-allocation results, so do not wait for the supplemental data call before issuing portfolio-analysis calls. Do not repeat a cached call or datapoint unless its prior result failed, was incomplete, or is no longer applicable.

### Full-report Supplemental Datapoints

Request these IDs, omitting any field already retrieved in the snapshot or a prior targeted follow-up. Merge all cached and supplemental results into one in-memory comparison dataset before assembling `D`.

| Area | IDs |
|---|---|
| Fund identity and management | `LS05M`, `OF009`, `OF015`, `OF033`, `OF00F`, `OF041`, `OS388` |
| Additional benchmark and income | `RR03A`, `PM002` |
| Trailing returns | `PD00B`, `PD00D`, `PD014`, `PD00F`, `PD00H`, `PM00I` |
| Trailing category ranks | `PD00C`, `PD00E`, `PD00J`, `PD00G`, `PD00I`, `RR286` |
| Calendar returns and ranks | `AR002`–`AR006`, `AR00E`–`AR00I` |
| Risk and risk/return | `RR015`, `RR016`, `RR017`, `RR010`–`RR013`, `RR153`, `RR154`, `RR159`, `RR160`, `PM00E`, `PM00G` |
| Ratings | `MMR01`, `CNAXS`, `MMR04`, `RR01Y`, `QFR0H`, `MMR3E`, `MMR2E`, `MMR1E` |

| Call | Condition |
|---|---|
| `equity_style` for A | A equity ≥ 10% |
| `equity_style` for B | B equity ≥ 10% |
| `equity_sectors` for A | A equity ≥ 10% |
| `equity_sectors` for B | B equity ≥ 10% |
| `equity_regional_exposure` for A | A equity ≥ 10% |
| `equity_regional_exposure` for B | B equity ≥ 10% |
| `fixed_income_style` for A | A bonds ≥ 10% |
| `fixed_income_style` for B | B bonds ≥ 10% |
| `fixed_income_sectors` for A | A bonds ≥ 10% |
| `fixed_income_sectors` for B | B bonds ≥ 10% |
| `fixed_income_maturity` for A | A bonds ≥ 10% |
| `fixed_income_maturity` for B | B bonds ≥ 10% |
| `monthly_growth` for A | Always |
| `monthly_growth` for B | Always |
| `analyst-research-tool` for A | Always |
| `analyst-research-tool` for B | Always |

As soon as all confirmed-report results arrive, assemble and write `D`. Do not emit progress commentary or perform a separate planning pass before writing it, unless needed to recover from an error.

## Assemble `D`

### Top-Level Field Contract

| Field | Shape | Source | Requirement |
|---|---|---|---|
| `meta` | object | ID lookup + combined data | Required |
| `overview_groups` | array of group objects | combined data | Required |
| `portfolio_characteristics` | display rows | combined data + `equity_style` | Required; may be empty |
| `asset_allocation` | 5 rows | `asset_allocation` calls | Required |
| `equity_style_a` | object or `null` | `equity_style` for A | `null` if A equity < 10% |
| `equity_style_b` | object or `null` | `equity_style` for B | `null` if B equity < 10% |
| `equity_sectors` | rows or `null` | `equity_sectors` | `null` if neither fund ≥ 10% equity |
| `equity_regions` | rows or `null` | `equity_regional_exposure` | `null` if neither fund ≥ 10% equity |
| `fi_style_a` | object or `null` | `fixed_income_style` for A | `null` if A bonds < 10% |
| `fi_style_b` | object or `null` | `fixed_income_style` for B | `null` if B bonds < 10% |
| `fi_sectors` | rows or `null` | `fixed_income_sectors` | `null` if neither fund ≥ 10% bonds |
| `fi_maturity` | rows or `null` | `fixed_income_maturity` | `null` if neither fund ≥ 10% bonds |
| `growth_chart` | date array + two value arrays | `monthly_growth` × 2 | Required |
| `trailing_returns` | period rows | combined data | Required |
| `annual_returns` | year rows | combined data | Required |
| `category_rankings` | trailing and annual rank rows | combined data | Required |
| `risk` | period-keyed metric rows | combined data | Required |
| `risk_return` | period rows | combined data | Optional when unavailable |
| `ratings` | metric rows | combined data | Required |
| `analyst_a` | string | `analyst-research-tool` for A | Required |
| `analyst_b` | string | `analyst-research-tool` for B | Required |
| `narrative_p1` | string | synthesis | Required |
| `narrative_p2` | string | synthesis | Required |
| `narrative_p3` | string | synthesis | Required |

Do not include legacy fields `profile` or `cost`.

### `meta`

| Property | Source |
|---|---|
| `ticker_a` | `OS385` for A |
| `name_a` | `OS01W` for A |
| `ticker_b` | `OS385` for B |
| `name_b` | `OS01W` for B |
| `report_date` | today's date (YYYY-MM-DD) |
| `data_as_of_date` | date from combined data (`N/A` when missing) |
| `cross_category_warning` | `true` if `OF003` differs, else `false` |

### `overview_groups`

Array of group objects: `{"group": "Label", "rows": [{"label": "...", "a": "...", "b": "..."}]}`. Omit individual rows when both funds have no data.

| Group | Row | Source |
|---|---|---|
| Fund Identity | Name | `OS01W` |
| Fund Identity | Type | `LS466` |
| Fund Identity | Base Currency | `LS05M` |
| Fund Identity | Ticker | `OS385` |
| Structure & Access | Active / Index | derived (ETFs: `OF00D` Yes=Active/No=Index; non-ETFs: `OF00C` Yes=Index/No=Active) |
| Structure & Access | Fund Size | `OF009` formatted |
| Structure & Access | Inception Date | `OS00F` |
| Structure & Access | Min. Investment | `OS388` |
| Management | Number of Managers | count the current named-manager array from `OF015` |
| Management | Average Tenure | `OF033`, formatted as `"X.X Years"` |
| Management | Longest Tenure | `OF00F`, formatted as `"X.X Years"` |
| Management | Investment Advisor | `OF041` |
| Classification & Benchmark | Morningstar Category | `OF003` |
| Classification & Benchmark | Prospectus Benchmark | `OF00L` |
| Cost & Income | Net Expense Ratio | `OS00M` formatted |
| Cost & Income | Fee Level | `UB412` |
| Cost & Income | SEC 30-Day Yield | `PM002` formatted |

### `portfolio_characteristics`

Display before Asset Allocation in Structural Composition. Row shape: `{"label": "...", "a": "...", "b": "..."}`. Omit a row when both funds have no data; emit an empty array when neither row is available.

| Row | Source |
|---|---|
| Top 10 Holdings % | `HS07J`, formatted as a percentage |
| Avg Market Cap | `avg_market_cap` from each eligible `equity_style` response |
| Portfolio Turnover | `OS03S`, formatted as a percentage |

### `asset_allocation`

Always 5 rows. Values are raw percentages (numeric, not strings). Source: `asset_allocation.portfolio`.

```json
[
  {"label": "US Equity",     "a": 66.2, "b": 97.2},
  {"label": "Non-US Equity", "a": 3.4,  "b": 0.3},
  {"label": "Bonds",         "a": 0.0,  "b": 0.0},
  {"label": "Cash",          "a": 0.2,  "b": 1.0},
  {"label": "Other",         "a": 0.2,  "b": 1.5}
]
```

### `equity_style_a` / `equity_style_b`

Fields: `equity_style_breakdown.portfolio.{large|mid|small}_{value|blend|growth}`. All 9 cell values are whole numbers (`Math.round()`). Put `avg_market_cap` in `portfolio_characteristics`: raw value is USD millions ÷ 1000, format as `"$X.XB"`. Omit or null `portfolio_analyzed` when ≥ 95% — footnote shown only when < 95%.

```json
{
  "large_value": 15, "large_blend": 28, "large_growth": 28,
  "mid_value": 5,   "mid_blend": 8,   "mid_growth": 9,
  "small_value": 1,  "small_blend": 2,  "small_growth": 3,
  "portfolio_analyzed": 99.1
}
```

### `equity_sectors`

Row shape: `{"group": "Cyclical", "sector": "Basic Materials", "a": 2.4, "b": 0.3}`.

Fixed order — **Cyclical:** Basic Materials, Consumer Cyclical, Financial Services, Real Estate; **Sensitive:** Communication Services, Energy, Industrials, Technology; **Defensive:** Consumer Defensive, Healthcare, Utilities. Omit all-zero rows. Set individual `a` or `b` to `null` if that fund is below the 10% equity threshold (template renders as single-fund view). Set entire field to `null` if neither fund qualifies.

### `equity_regions`

Row shape: `{"sector": "Americas", "a": 99.6, "b": 75.1}`. Source: `world_regions.portfolio` from `equity_regional_exposure`. Fixed order: Americas, Greater Europe, Greater Asia, Not Classified. Omit all-zero rows. Set individual `a` or `b` to `null` if that fund is below the 10% equity threshold. Set the entire field to `null` if neither fund qualifies.

### `fi_style_a` / `fi_style_b`

Same 9-cell integer object as equity style. Rows: High / Med / Low (Credit Quality) — Cols: Ltd / Mod / Ext (Interest Rate Sensitivity). Fields from `fixed_income_style_breakdown.portfolio` (expected pattern: `limited_high`, `limited_medium`, `moderate_high`, etc. — verify field names on first live FI call).

### `fi_sectors`

Row shape: `{"sector": "Government", "a": 45.2, "b": null}`.

Emit only sectors present in the tool response. Fixed order: Government, Municipal, Corporate, Securitized, Cash & Equivalents, Derivative. Set individual `a` or `b` to `null` if that fund is below the 10% bonds threshold. Set entire field to `null` if neither fund qualifies.

### `fi_maturity`

Row shape: `{"sector": "1-3 Years", "a": 23.1, "b": null}`. Source: `fixed_income_maturity.portfolio`. Fixed order: 1-3 Years, 3-5 Years, 5-7 Years, 7-10 Years, 10-15 Years, 15-20 Years, 20-30 Years, Over 30 Years. Emit only maturity buckets present in the tool response. Set individual `a` or `b` to `null` if that fund is below the 10% bonds threshold. Set the entire field to `null` if neither fund qualifies.

### `growth_chart`

Source: `monthly_growth_from_10k.portfolio` from each `monthly_growth` call (a dict of `{"YYYY-MM-DD": value}`). Common date range: start from the later inception date; end at the latest date present in both. Values are dollars starting at 10000.

```json
{
  "Date": ["2015-01-31", "2015-02-28"],
  "[TICKER A] — [Name A]": [10000.0, 10500.0],
  "[TICKER B] — [Name B]": [10000.0, 10625.0]
}
```

### `trailing_returns`

Row shape: `{"period": "YTD", "a": 10.96, "b": 8.23}`. Omit rows with no data. 2Y+ are annualized. Values are 2dp numerics.

| Period | Source |
|---|---|
| YTD | `PD00B` |
| 1 Yr | `PD00D` |
| 2 Yr | `PD014` |
| 3 Yr | `PD00F` |
| 5 Yr | `PD00H` |
| 10 Yr | `PM00I` |

### `annual_returns`

Row shape: `{"year": 2025, "a": 17.84, "b": 22.31}`. Replace Y+0–Y-4 with actual calendar year labels. Omit rows with no data. Values are 2dp numerics.

| Source | Year |
|---|---|
| `AR002` | Y+0 |
| `AR003` | Y-1 |
| `AR004` | Y-2 |
| `AR005` | Y-3 |
| `AR006` | Y-4 |

### `category_rankings`

Object with `trailing` and `annual` arrays. Use the same period/year order as `trailing_returns` and `annual_returns`; row shapes are `{"period": "YTD", "a": 18, "b": 44}` and `{"year": 2025, "a": 18, "b": 44}`. Render each available rank inline after the corresponding return as `"17.75% (27)"`. A rank of `1` is best and `100` is worst within each fund's Morningstar Category. These ranks are category-relative, so when funds have different categories they are not directly comparable to one another.

| Rank set | Sources |
|---|---|
| Trailing | `PD00C`, `PD00E`, `PD00J`, `PD00G`, `PD00I`, `RR286` for YTD / 1 / 2 / 3 / 5 / 10 years |
| Calendar year | `AR00E`–`AR00I` for Y+0 through Y-4 |

### `risk`

Period-keyed object. Row shape: `{"metric": "Sharpe Ratio", "a": 1.77, "b": 1.45}`. Omit rows with no data. Values are 3dp numerics.

| Period | Metric | Source |
|---|---|---|
| 1y | Sharpe Ratio | `RR010` |
| 3y | Std Dev | `RR015` |
| 3y | Sharpe Ratio | `RR011` |
| 3y | Upside Capture | `RR153` |
| 3y | Downside Capture | `RR159` |
| 5y | Std Dev | `RR016` |
| 5y | Sharpe Ratio | `RR012` |
| 5y | Upside Capture | `RR154` |
| 5y | Downside Capture | `RR160` |
| 10y | Std Dev | `RR017` |
| 10y | Sharpe Ratio | `RR013` |

### `risk_return`

Row shape: `{"period": "3 Yr", "a_return": 21.10, "a_risk": 13.3, "b_return": 18.45, "b_risk": 16.1}`. Use `null` for unavailable periods. The first usable row becomes the default scatter period. Optional when no periods have data.

| Period | Return | Risk |
|---|---|---|
| 3 Yr | `PM00E` | `RR015` |
| 5 Yr | `PM00G` | `RR016` |
| 10 Yr | `PM00I` | `RR017` |

### `ratings`

Row shape: `{"metric": "Medalist Rating", "a": "Gold", "b": "Silver"}`.

| Row | Source | Notes |
|---|---|---|
| Medalist Rating | `MMR01` | Apply asterisk if `CNAXS` has a footnote value |
| Analyst-Driven % | `MMR04` | Integer + "%" — e.g. `"100%"` |
| Star Rating | `RR01Y` | 1–5 |
| Portfolio Risk Score | `QFR0H` | 2dp numeric |
| Process Pillar | `MMR3E` | |
| People Pillar | `MMR2E` | |
| Parent Pillar | `MMR1E` | |

**Medalist footnotes** — apply asterisk to the Medalist Rating cell and emit the applicable text after the table:
- `CNAXS = Issuer Initiated Rating` → `*`: *In Australia and New Zealand only, starting June 2026, Morningstar may receive a fee from product issuers for Issuer Initiated Ratings. Fees are not linked to the rating outcome.*
- `CNAXS = Tracks Morningstar Index` → `**`: *Certain funds track indexes created by Morningstar. Conflicts are mitigated via information barriers and ongoing compliance monitoring.*

### `analyst_a` / `analyst_b`

Write one sentence per fund from `analyst-research-tool`, maximum 50 words. State only the
analyst's most decision-relevant conclusion; omit background already visible in the report. If
research is unavailable, note that in one short sentence.

### Narrative Fields

Write three compact sections. The template supplies the fixed headings below; do not include
headings in the field values. Limit each field to 1–2 sentences and 75 words. Across all three
fields, mention only material differences, use no more than two numbers per field, and avoid
restating tables or analyst summaries. Every claim must be grounded in prior data; introduce no
new numbers, generic commentary, investment advice, or suitability language.

- `narrative_p1` — **Mandate & Structure:** state the category-based comparability result and the single most important mandate, sector, style, or allocation difference.
- `narrative_p2` — **Performance & Risk:** state at most one material return difference and one related risk difference.
- `narrative_p3` — **Cost & Quality:** state the expense-ratio difference and mention ratings or pillars only when materially different; end with one short distinction in intended role.

### Formatting Rules

| Field | Rule |
|---|---|
| Trailing returns, annual returns, `risk_return` return fields | Round to 2dp, numeric |
| Risk metrics (Std Dev, Sharpe, Capture) | Round to 3dp, numeric |
| Asset allocation values | Round to 2dp, numeric |
| Style box cells (equity and FI) | `Math.round()` → whole number integer |
| Portfolio Risk Score | Round to 2dp, numeric |
| Analyst-Driven % | Integer + "%" string — e.g. `"100%"` |
| Fund Size (`OF009`) | `"$X.XB"` / `"$X.XT"` (raw value is dollars) |
| Avg Market Cap in `portfolio_characteristics` | `"$X.XB"` (raw value is USD millions ÷ 1000) |
| Percentage display values in `overview_groups` | `"X.XX%"` string |
| Management tenure (`OF033`, `OF00F`) | `"X.X Years"` string |
| Number of Managers (`OF015`) | Count the returned array; display as a whole-number string |

Do not pass raw tool values through unchanged.

### Missing Value Rules

- Missing numeric values in arrays: use `null` (renders as `--`).
- Missing data and tool failure both render as `N/A`; note tool failure distinctly from missing data.

## Inject and Validate

Write `D` once to a unique, unused path:
`/tmp/fund-comparison-data-[TICKERA]-[TICKERB]-[RUN-ID].json`, where `[RUN-ID]` is a timestamp or
other collision-resistant value. Retain the exact path for the remainder of the session so the
file can be provided if the user explicitly asks. Treat it as an internal intermediate: do not
mention or link it during normal delivery.

Never overwrite a prior run's intermediate file. If writing fails, choose another unused path and
retry with the already assembled `D`; do not recompute, revise, or regenerate its contents. Then
run:

```bash
node <skill-dir>/scripts/inject-template.mjs \
  <skill-dir>/assets/template.html \
  /tmp/fund-comparison-data-[TICKERA]-[TICKERB]-[RUN-ID].json \
  comparison-[TICKERA]-vs-[TICKERB].html
```

The injector validates JSON shape, confirms the template marker (`const D = __DATA_JSON__;`),
performs the injection, and prints output path, validation status, and byte size for internal use.

If the injector succeeds, treat rendering and validation as complete. Do not report successful
validation or byte size to the user. Do not run `node --check`, marker grep, file-size commands,
or template inspection unless the injector fails or the user is debugging skill internals. Do
not inline the full `D` object into shell commands.

## Final Response

Respond with:

- Output file path
- Important data limitations
- `I still have the comparison data in context—ask any follow-up question about the funds, exposures, performance, risk, costs, or ratings.`

Report validation only when it fails and prevents delivery. Do not print or link the intermediate
`D` JSON unless the user explicitly asks. If asked for `D`, provide the retained
run-specific JSON path; summarize or omit large `growth_chart` arrays only when the user asks for
a summary rather than the complete file.
