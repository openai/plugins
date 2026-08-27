# Quartr Connector Playbook

Load this reference only after the owning workflow selects a callable Quartr route. The source prompt was verified against the active Quartr connector on 2026-04-15; the live tool schema remains authoritative if it differs.

## Authority Order

Use this order when instructions conflict:

1. The live Quartr action schema exposed in the current runtime.
2. The canonical call shapes and workflow rules in this playbook.
3. The user's latest explicit instruction when it does not conflict with connector schema, citation rules, or data integrity.
4. The owning analytical workflow, such as comps, DCF, earnings analysis, working-capital analysis, or guidance tracking.

Never call an action with missing required arguments or `params: null`. When using a generic connector runner, pass action arguments inside top-level `params`, not `input`, `arguments`, or top-level action fields. Do not copy parameter names from examples blindly after the live schema changes.

## Scope And Source Order

Prefer Quartr over web search for public-company filings, annual reports, quarterly reports, earnings releases, presentations, transcripts, event summaries, management commentary, and standardized financial statements. Use another clearly labeled source only for data outside Quartr's coverage. Keep Quartr values distinct from non-Quartr values.

## Canonical Sequence

1. Search for the company.
2. Validate the match before using `companyId`.
3. Pull standardized actual financials one statement type at a time.
4. List documents or events to identify bounded source material.
5. Use document search, summaries, or targeted reads for segment detail, KPIs, guidance, strategy, risks, and qualitative context.
6. Compute derived metrics from sourced values.
7. Present results with provenance and clear assumptions.

Never invent `companyId`, `documentId`, `eventId`, source URLs, filing dates, or source page references.

## Output Budget

Quartr responses can be large because financial values include source metadata and document reads include full text.

- `search_companies`: search one company at a time.
- `get_financials`: always specify one `financialType`.
- `get_financials`: probe availability with one statement and one annual period first.
- `get_financials`: pull multi-year models one statement type at a time; split oversized responses into one year per call.
- `list_documents`: keep `limit` small, usually 5-10.
- `search_documents`: use short targeted queries, usually one to five words.
- `read_document`: use summaries or search before broad reads; use small `maxPages` values.

Do not repeatedly list connectors once Quartr actions are already known. Do not fall back to web search for filing values after Quartr has located the relevant filing.

## `search_companies`

Purpose: find the Quartr company record and capture `companyId`.

Expected shape:

```python
search_companies(query: str)
```

Correct examples:

```json
{"query": "AAPL"}
```

```json
{"query": "Apple"}
```

Avoid `keywords`, a `ticker` field, or a combined query such as `"Broadcom Inc AVGO"`.

Match rules:

- Search with ticker when known; otherwise use a clean company name without legal suffixes.
- Do not search a peer set in one call.
- Prefer active companies for current financial analysis.
- If the result is fuzzy, retry with ticker, a shorter distinctive name, or an alternate spelling.
- A ticker match or normalized company-name match is strong. Shared industry words alone are weak.
- If no exact or highly likely match appears, do not use the top result.

Capture:

- `id` as `companyId`
- `ticker`
- `name`
- `country`
- `gics`
- `status`
- company `url`

## `get_company`

Purpose: retrieve profile metadata or sanity-check a known company.

Expected shape:

```python
get_company(companyId: number)
```

Use this when profile metadata, industry context, company URLs, or an additional match check would improve the analysis.

## `get_financials`

Purpose: retrieve standardized income-statement, balance-sheet, or cash-flow values.

Expected shape:

```python
get_financials(companyId: number, startDate?: str, endDate?: str, periodType?: str, financialType?: str)
```

Valid `periodType` values:

- `quarterly`
- `halfYear`
- `yearly`
- `periodical`

Valid `financialType` values:

- `incomeStatement`
- `balanceSheet`
- `cashFlowStatement`

Correct example:

```json
{"companyId": 4742, "startDate": "2024-01-01", "endDate": "2025-12-31", "periodType": "yearly", "financialType": "incomeStatement"}
```

Usage rules:

- Obtain `companyId` from `search_companies`; do not guess it.
- Use ISO dates.
- Use `yearly` for annual historical actuals and `quarterly` for trend or earnings-update work.
- Pull each statement separately.
- For broad historical models, probe with one statement and one year first.
- Treat `null` values as missing, not zero.

Capture returned event, currency, statement type, report URL, source page, and reference URL metadata when available.

## `list_documents`

Purpose: identify company filings, releases, slides, transcripts, letters, and reports.

Expected shape:

```python
list_documents(companyId: number, documentTypes?: list[str], startDate?: str, endDate?: str, limit?: number)
```

Common `documentTypes`:

- `annual_report_10k`
- `quarterly_report_10q`
- `earnings_release_8k`
- `slide`
- `transcript`
- `annual_report_20f`
- `annual_report_40f`
- `press_release`
- `shareholder_letter`
- `sustainability_esg_report`

Use narrow document-type filters and small limits. Capture `id` as `documentId`, URL, title, document type, filing type, filing date, and `eventId`.

## `search_documents`

Purpose: search reports, slides, and transcripts for targeted qualitative or KPI detail.

Expected shape:

```python
search_documents(query: str, documentTypes: list[str], limit?: number, startDate?: str, endDate?: str, filingTypes?: list[str], filter?: str)
```

Correct example:

```json
{"query": "revenue segments", "documentTypes": ["reports"], "filingTypes": ["10-K"], "filter": "companyId:=4742", "limit": 5}
```

Use `documentTypes: ["reports"]` for filings, `["transcripts"]` for earnings-call commentary, and `["slides"]` for presentations. Use filing types only with reports. Use `filter: "companyId:=<id>"` for company-specific results. Keep queries short and retry empty searches with fewer words or synonyms.

Capture document, event, company, page, URL, and snippet fields.

## Document And Event Detail

Use these shapes:

```python
read_document(documentId: number, maxPages?: number)
get_document_summary(documentId: number)
list_events(companyId?: number, eventTypes?: list[str], limit?: number, startDate?: str, endDate?: str, order?: str)
get_event(eventId: number)
get_event_summary(eventId: number)
list_related_companies(companyId: number)
```

Prefer summaries or document search before `read_document`. Keep document reads narrow. Use event tools for earnings calls, investor days, guidance events, conferences, AGMs, M&A announcements, and transcript-driven qualitative analysis. Use related companies for peer discovery, then verify peers before using them in comps.

## Date And Period Rules

Use ISO `YYYY-MM-DD` dates in Quartr inputs. Anchor periods in this order:

1. User-specified dates or years.
2. Filing dates and event dates returned by Quartr.
3. Periods visible in an active artifact or user-provided data.
4. A period range supplied by the user.
5. The current date only as a last resort, with the assumption stated.

For non-calendar fiscal years, use a broad date range that covers the filings and label fiscal periods using returned event and document metadata.

## Guidance Versus Actuals

Before calculating beat, miss, or guidance accuracy:

1. Find the relevant earnings call or guidance event.
2. Retrieve the guidance language through an event summary, transcript search, or targeted read.
3. Create a mapping table showing the guidance period and the results period it applies to.
4. Verify the offset.
5. Calculate the comparison only after the mapping is clear.

Quarterly guidance from quarter N usually applies to quarter N+1 actuals. Do not compare same-quarter guidance to same-quarter actuals unless the disclosure explicitly says to do so. Annual guidance from Q1, Q2, or Q3 usually applies to the current fiscal year; Q4 annual guidance usually applies to the next fiscal year unless the disclosure says otherwise.

## Formatting And Tables

Use readable financial formatting: `$X.Xbn` or `$X,XXXmm`, `$X.XX` per share, one decimal for percentages and multiples, signed growth rates, signed basis points, and clearly labeled share counts.

For financial tables, use metrics as rows and chronological periods as columns. Place derived rows such as growth, margins, and variance below their sourced metrics unless the user requests another layout.

## Citation Rules

Carry provenance through tables, prose, charts, and artifacts.

- Prefer returned `referenceUrl` for standardized financial values.
- Otherwise cite `reportUrl`, document URL, event URL, or company URL.
- For document snippets, cite the document URL and include page number when available.
- Cite computed figures through their sourced inputs.
- Add `Data sourced from Quartr` to outputs that use Quartr data.

Never imply that non-Quartr values came from Quartr.

## Recovery

If a call fails:

1. Check live parameter names and types.
2. Retry with the smallest valid call.
3. For weak company matches, retry with ticker or a shorter distinctive name.
4. For oversized financial pulls, retain one `financialType` and split to one year per call.
5. For oversized document reads, use a summary or search, then read fewer pages.
6. For empty document search, retry with fewer words, synonyms, broader document types, or no filing-type filter.
7. If Quartr lacks the company, filing, or line item, state the gap and use another source only for the missing data.
8. If still blocked, state the exact failed call and the smallest missing input or fallback needed.
