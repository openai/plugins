# Daloopa Connector Playbook

Load this reference only after the owning workflow selects a callable Daloopa route. The source prompt was verified against the active Daloopa connector on 2026-04-14; the live tool schema remains authoritative if it differs.

## Authority Order

Use this order when instructions conflict:

1. The live Daloopa action schema exposed in the current runtime.
2. The canonical call shapes and workflow rules in this playbook.
3. The user's latest explicit instruction when it does not conflict with connector schema, citation rules, or data integrity.
4. The owning analytical workflow, such as comps, DCF, earnings analysis, working-capital analysis, or guidance tracking.

Never call an action with missing required arguments or `params: null`. Construct the smallest valid argument object first. Do not copy parameter names from examples blindly after the live schema changes.

## Scope And Source Order

Use Daloopa for source-backed public-company financials, KPIs, and targeted filing or document snippets. Use another clearly labeled source for live prices, consensus, or news when Daloopa does not provide the needed data. Keep Daloopa values distinct from non-Daloopa values.

## Canonical Sequence

1. Discover the company.
2. Discover relevant series IDs.
3. Pull fundamentals for explicit periods and selected series IDs.
4. Search documents only when qualitative context is needed.
5. Compute derived metrics from sourced values.
6. Present results with citations and clear assumptions.

Never invent `company_id`, `series_ids`, `fundamental_id`, periods, or source URLs.

## Output Budget

Daloopa can return large result sets. Prefer several narrow calls over one broad call.

- `discover_companies`: search one company at a time with at most one or two keywords, usually ticker and short company name.
- `discover_company_series`: use one company, one anchor period, and one narrow metric family per call.
- `discover_company_series`: use one to five tightly related keywords, not a full financial-statement keyword list.
- `get_company_fundamentals`: use selected series IDs only and keep normal batches to roughly 15 series IDs or fewer.
- `search_documents`: start with one to four keywords because keywords use AND logic.

For financial statements, discover small metric families separately: revenue, profitability, balance-sheet cash and debt, then cash flow. If a call is too large, split by fewer keywords first and fewer periods second.

## `discover_companies`

Purpose: find the Daloopa company record and capture `company_id`.

Expected shape:

```python
discover_companies(keywords: list[str])
```

Correct examples:

```json
{"keywords": ["AAPL"]}
```

```json
{"keywords": ["AVGO", "Broadcom"]}
```

Avoid scalar `keyword`, a `ticker` field, or a combined string such as `"Broadcom Inc AVGO"`.

Search rules:

- For tickers, use the exact ticker symbol.
- For company names, use the core name without legal suffixes such as Inc., Corp., Ltd., LLC, PLC, GmbH, or S.A.
- If a result is absent or ambiguous, retry with a shorter or more distinctive company name.
- Discover peers separately or in very small batches.

Capture:

- `company_id`
- `ticker`
- `name`
- `latest_calendar_quarter`
- `latest_fiscal_quarter`

## `discover_company_series`

Purpose: find available financial or KPI series and their IDs.

Expected shape:

```python
discover_company_series(company_id: int, keywords: list[str], periods: list[str])
```

Correct example:

```json
{"company_id": 2, "keywords": ["revenue", "sales"], "periods": ["2025Q4"]}
```

Usage rules:

- Call this only after `discover_companies`; do not guess `company_id`.
- Use focused keyword lists and explicit periods.
- Search related synonyms when needed, such as `["revenue", "sales", "net sales"]`.
- Inspect returned labels before choosing series IDs.
- Capture `id`, `full_series_name`, and hierarchy or row metadata when available.

When building historical actuals, prefer series in this order:

1. Income Statement, Balance Sheet, or Cash Flow Statement lines.
2. Actual reported line items for the requested period.
3. Segment detail only when the task requests segment revenue or KPIs.
4. Guidance only when the task explicitly asks for guidance or forecast commentary.
5. Avoid Guidance, Projected, 8-K, Reconciliation, and KPI series for historical actuals unless no direct statement line exists.

If multiple series match, choose the cleanest statement hierarchy and most direct label, then pull a small sample to verify it.

## `get_company_fundamentals`

Purpose: retrieve values for selected periods and series IDs.

Expected shape:

```python
get_company_fundamentals(company_id: int, periods: list[str], series_ids: list[int])
```

Correct example:

```json
{"company_id": 2, "periods": ["2024Q1", "2024Q2", "2024Q3", "2024Q4"], "series_ids": [12345, 67890]}
```

Usage rules:

- Obtain `series_ids` from `discover_company_series` first.
- Use explicit period strings only: `YYYYQ#` for quarters and `YYYYFY` for fiscal years.
- Use the latest period fields returned by `discover_companies` as anchors when available.
- For TTM, pull the last four quarters and aggregate them.
- For YoY, pull the current period and the same period one year earlier.
- For sequential trends, pull consecutive quarters.
- Capture returned `id` or `fundamental_id` for each value.

Expected return fields:

- `id`
- `series_id`
- `title`
- `value_year_to_date`
- `value_quarter`
- `unit`
- `calendar_period`
- `fiscal_period`

Use `value_quarter` for quarterly analysis when available. Use `value_year_to_date` only for explicit YTD work or when quarterly values are unavailable. If cash-flow values are cumulative and quarterly values are required, subtract the prior quarter's YTD amount and label the conversion.

## `search_documents`

Purpose: search filings, transcripts, and company documents for qualitative context.

Expected shape:

```python
search_documents(keywords: list[str], company_ids: list[int], periods: list[str])
```

Correct example:

```json
{"keywords": ["revenue", "guidance"], "company_ids": [2], "periods": ["2024Q3", "2024Q4"]}
```

Use document search for management commentary, risk factors, guidance, outlook, strategy, competition, acquisitions, disclosures, or explanations for performance. Use `company_ids`, not tickers. Keywords use AND logic; retry sparse searches with fewer or broader terms. Treat document search as beta when presenting its results and use returned document IDs for citations.

## Period Rules

Use explicit `YYYYQ#` and `YYYYFY` periods in connector calls.

Anchor periods in this order:

1. Latest-period fields returned by `discover_companies`.
2. Periods visible in an active artifact or user-provided data.
3. A period range supplied by the user.
4. The current date only as a last resort, with the assumption stated.

For multi-company analysis, use calendar periods for comparability. Present fiscal labels when useful.

## Guidance Versus Actuals

Before calculating beat, miss, or guidance accuracy:

1. Create a mapping table showing the guidance period and the results period it applies to.
2. Verify the offset.
3. Calculate the comparison only after the mapping is clear.

Quarterly guidance from quarter N usually applies to quarter N+1 actuals. Do not compare same-quarter guidance to same-quarter actuals unless the disclosure explicitly says to do so. Annual guidance from Q1, Q2, or Q3 usually applies to the current fiscal year; Q4 annual guidance usually applies to the next fiscal year unless the disclosure says otherwise.

## Formatting And Tables

Use readable financial formatting: `$X.Xbn` or `$X,XXXmm`, `$X.XX` per share, one decimal for percentages and multiples, signed growth rates, signed basis points, and clearly labeled share counts.

For financial tables, use metrics as rows and chronological periods as columns. Place derived rows such as growth, margins, and variance below their sourced metrics unless the user requests another layout.

## Citation Rules

Capture source IDs when pulling data and carry them through tables, prose, charts, and artifacts.

- Cite each Daloopa financial figure with `https://daloopa.com/src/{fundamental_id}`.
- Cite document results with `https://marketplace.daloopa.com/document/{document_id}`.
- Cite computed figures through their sourced inputs.
- Add `Data sourced from Daloopa` to outputs that use Daloopa data.

Never present uncited Daloopa figures or imply that non-Daloopa values came from Daloopa.

## Recovery

If a call fails:

1. Check live parameter names and types.
2. Retry with the smallest valid call.
3. For oversized output, narrow metric families, periods, peer sets, or series-ID batches before retrying.
4. For empty series discovery, retry with broader synonyms.
5. For empty document search, retry with fewer keywords because keywords use AND logic.
6. If still blocked, state the exact failed call and the smallest missing input or fallback needed.
