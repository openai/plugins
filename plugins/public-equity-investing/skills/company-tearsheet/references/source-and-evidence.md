# Source and Evidence Protocol

## Source hierarchy
Use the strongest available source that the user is permitted to access.

1. **User-provided source package**: uploaded files, pasted context, emails/Drive/Slack context, internal research, prior models, notes, decks, reports, and workbook extracts.
2. **Callable connected apps or user-provided approved-provider exports**: market-data, document, research, source-of-truth, and provider sources the user can access. Do not imply direct access when the runtime route is not callable.
3. **Primary public sources**: SEC/company filings, earnings releases, investor presentations, company websites, press releases, rating agency reports if accessible, court/regulatory filings.
4. **Trusted provider-standardized sources**: callable provider apps/connectors or user-provided exports from FactSet, S&P Global, CapIQ, LSEG, Morningstar, Moody's, Daloopa, Quartr, Aiera, MSCI, Bloomberg, or another permitted provider. If the requested provider route is not callable, request an export or continue with a clearly labeled fallback.
5. **Credible secondary sources**: reputable news, industry publications, sell-side or third-party research notes the user provides, reputable databases.
6. **Web fallback**: public search results when no stronger source is available.
7. **Assumptions**: user-provided or explicitly disclosed inferred assumptions. Never present assumptions as facts.

If a `financial-source-of-truth` skill is available, follow its more specific source hierarchy and citation protocol.

## Source inventory fields
Maintain a lightweight `Source_Index` for every tearsheet:

| Field | Description |
|---|---|
| `source_id` | Unique identifier such as `S1`, `S2`. |
| `source_name` | Filing, deck, export, provider, internal doc, or website name. |
| `source_type` | User file, connected app, primary filing, provider, press release, secondary source, web fallback, assumption. |
| `provider_or_owner` | Source owner, provider, or internal team. |
| `as_of_date` | Date the source data represents. |
| `retrieved_at` | Date/time the assistant accessed it. |
| `period_covered` | FY/Q/month/LTM/date range. |
| `source_location` | Page, slide, tab, cell range, URL, file name, message link, or data object. |
| `freshness_status` | Current, acceptable, stale, preliminary, unknown. |
| `notes` | Limitations, caveats, conflicts, or access constraints. |

## Stale-data checks
Use conservative stale-data flags:

| Source / data type | Current if | Stale trigger |
|---|---:|---:|
| Market price / market cap / EV | Same day or latest market close | Older than 1 trading day unless historical. |
| Public financials | Latest filed period or current reported quarter | Superseded by newer earnings release/filing. |
| Consensus estimates | Latest available set | Older than 7-14 days around earnings; older than 30 days otherwise. |
| Credit ratings / spreads | Latest available | Older than 1 week for active credits; older than 30 days for static profiles. |
| Public issuer debt terms / credit metrics | Latest filing, executed document, or latest market data | Superseded by refinancing, amendment, exchange, rating action, or newer filing. |
| Listed fund / manager AUM, NAV, holdings, or performance | Latest public reporting cycle | Older than latest available reporting cycle or missing as-of date. |
| Internal research model / estimate | Current model version or stated frozen date | Superseded by newer filing, print, guidance, consensus pull, or model update. |

Always flag data as `unknown` if freshness cannot be determined.

## Evidence labels
Use exact labels:

- `fact_source_reported`: directly supported by source document or connected system.
- `fact_provider_standardized`: supplied by trusted provider after standardization.
- `derived_calculation`: calculated from cited inputs.
- `issuer_management_claim`: statement from company, issuer, or management that needs evidence support.
- `management_adjusted`: company-defined adjusted metric or management adjustment.
- `analyst_adjusted`: analyst normalization, add-back, reclass, or pro forma change.
- `estimate_consensus`: consensus estimate or provider forecast.
- `analyst_interpretation`: synthesis based on cited facts, not directly stated by a source.
- `assumption_user_provided`: assumption supplied by the user.
- `assumption_inferred`: inferred from incomplete context; disclose and keep low confidence.
- `missing_required_source`: needed fact or metric not available.
- `stale_source`: source may be superseded for current decision.
- `contradicted_source`: source conflicts with another material source.
- `unknown`: evidence type cannot be determined.

## Confidence labels
- `high`: primary/connected source, current, clear entity, period, unit, and label.
- `medium`: trusted provider or clear source with minor mapping ambiguity or age.
- `low`: stale, preliminary, OCR-heavy, inferred, conflicting, or unclear period/unit/source.

## Citation format
For chat output, cite sources using the environment's native citation syntax when available. For file or artifact output, use compact source references in tables:

`Metric | Period | Value | Source | Evidence | Confidence`

Where `Source` should be a source ID plus location: `S2 p.14`, `S4 tab Revenue cell D22`, `S1 FY2025 10-K Item 8`, `S5 provider pull 2026-05-07`.

## Conflict handling
When sources conflict:

1. Preserve both values when material.
2. Prefer primary source over provider, connected system over copied spreadsheet, final filing over preliminary release, audited over unaudited, latest version over superseded version.
3. State why a value was selected if one is used.
4. Add conflict note to `Risks / gaps` if the conflict matters to the profile.
5. Do not average, smooth, or backsolve conflicting values unless the user asks and the method is disclosed.

## Fact vs assumption standard
- Facts require support from a source.
- Calculations require cited inputs and a visible formula or explanation.
- Claims from company, issuer, or management are still claims, even if cited.
- Assumptions must be marked as assumptions and should not be blended into fact tables.

## Public Equity Data Freshness

Market cap, price, float, ADV, short interest, ownership, ETF/index membership, consensus, and factor exposure require source labels and as-of dates. If unavailable, use missing evidence and route to the next analytical workflow rather than inventing.
