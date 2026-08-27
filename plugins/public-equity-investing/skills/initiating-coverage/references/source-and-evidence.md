# Source and Evidence Protocol

## Source hierarchy

Use sources in this order unless the user instructs otherwise:

1. User-provided context and files.
2. Callable connected routes and user-provided exports.
3. Company primary sources: 10-K, 10-Q, 8-K, S-1, prospectus, proxy, investor deck, earnings release, transcript, press release.
4. Callable financial-data provider routes or user-provided consensus/estimate exports.
5. Exchange, regulator, rating agency, central bank, or government sources where relevant.
6. Reputable public web and news.
7. Explicit assumptions.

## Required source fields

For each source-register entry capture:
- source_id,
- source_name,
- source_type,
- date_published,
- date_accessed,
- period_covered,
- document_section_or_page when available,
- reliability tier,
- stale flag,
- notes.

## Evidence labels

Use one of:
- `fact`: directly supported by a reliable source.
- `company_claim`: stated by the company or management but not independently verified.
- `street_estimate`: consensus, sell-side estimate, or third-party forecast.
- `model_derived`: calculated from sourced inputs or a provided model.
- `banker_or_pm_judgment`: professional interpretation based on evidence.
- `assumption`: user/model/assistant assumption not directly sourced.
- `mixed`: combines supported facts with assumptions or judgment.
- `needs_source`: material claim still missing evidence.

## Confidence labels

Use one of:
- `high`: primary source or multiple trusted sources, recent and directly relevant.
- `medium`: credible but indirect, older, partial, or requires some interpretation.
- `low`: weak evidence, incomplete, stale, or assumption-heavy.

## Stale-data checks

Flag stale data when:
- public-company market data is not current as of the report date,
- latest fiscal period is missing,
- estimates are pre-earnings when post-earnings estimates should be available,
- transcript/earnings data is more than one quarter old for current setup claims,
- macro/commodity/rate data is not aligned to current report date,
- industry data predates a major regulatory, macro, or company event.

## Market Data And Valuation Inputs Completion Step

Before delivering a substantive initiation report, attempt to source the current price with an as-of timestamp, market capitalization, reported and fully diluted share-count inputs, cash and debt/lease inputs required for enterprise value, and available consensus or estimate context. Use approved connected or accessible market-data sources where available and retain source IDs and freshness labels.

If a required input cannot be retrieved, mark it `needs_source`, explain which valuation or ownership conclusion cannot be supported without it, and keep the initiation posture appropriately preliminary. Do not omit retrievable current market data merely because the capital-return thesis remains unproven.

Keep two judgments separate in the report header and conclusion:
- `Evidence confidence`: confidence in reported operating, financing, market-data, and estimate inputs.
- `Underwriting status`: whether the available evidence is sufficient for ownership, a target price, watchlist status, or more work.

## Conflict handling

If sources disagree:
1. Identify the conflict explicitly.
2. Prefer primary source for reported historicals.
3. Prefer latest consensus provider for current estimates if user approved that provider.
4. Preserve user-provided internal estimates as `user_assumption` or `model_derived`, not objective fact.
5. Show the impact of the conflict if material.
6. Do not average conflicting sources unless there is a clear reason.

## Citation style

Use consistent footnotes or inline citations according to the user's environment. When building an output that cannot preserve clickable citations, include a source register with source IDs and map each material claim to a source ID.

Example:
- Revenue was $X in FY2025 [S1].
- We assume revenue CAGR of Y% from FY2025-FY2028 based on pipeline commentary [S2] and user model assumptions [A1].
