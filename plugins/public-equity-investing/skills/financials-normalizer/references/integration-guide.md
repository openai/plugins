# Integration guide

This skill is a shared-core feeder for Public Equity Investing skills. It should create reliable inputs, not complete the downstream analysis itself.

## Shared core handoffs

- `financial-source-of-truth`: use for evidence policy, source access caveats, conflict policy, connector honesty, and citation discipline. `financials-normalizer` applies those rules to financial statement, KPI, consensus, and market-data support.
- `excel-data-cleaner`: use first when spreadsheet structure blocks extraction. Examples: merged headers, multiple tables per tab, blank rows, malformed dates, export artifacts, or broken table shapes.
- `model-audit-tieout`: use after normalized data is placed into a workbook/model to audit formulas, links, hardcodes, checks, and sign conventions.
- `scenario-sensitivity-generator`: use after a base case exists to build downside/upside cases, sensitivities, breakevens, and stress tests.
- `memo-builder`: use after normalized tables and QA findings are complete to generate decision narratives.
- `deck-report-qc`: use after normalized outputs are inserted into decks/reports.
- `style-guide-adapter`: use after content is correct to match firm/client formatting and language.

## Public Equity Investing

Use normalized outputs for `earnings-preview`, `earnings-deep-dive`, `equity-model-update`, `long-short-pitch`, `thesis-tracker`, `portfolio-risk-management`, `economic-impact-report`, `comps-valuation`, `dcf-model-builder`, `three-statement-model-builder`, `scenario-sensitivity-generator`, `memo-builder`, and `sector-context-overlay`.

Recommended extra fields: filing/press release dates, period type, guidance, consensus/estimate source, provider/export as-of timestamp, company-defined KPIs, segment disclosures, share count, buybacks/SBC, net debt, capital allocation, index/ETF constituent support when relevant, and source filing references.

## Credit Markets handoff / equity-risk debt and liquidity context

Keep debt, liquidity, maturity, rating, CDS/spread, and refinancing fields only when they support common-equity downside, solvency, valuation bridge, or risk sizing. Recommended equity-context fields: net debt, cash, revolver availability, maturity wall summary, rating or CDS/spread signal, liquidity runway, refinancing date, and source document. Route covenant packages, recovery waterfalls, distressed-security value, bond/loan/CDS pricing, spread/yield relative value, and debt-security selection to Credit Markets.

## When not to hand off

Do not hand off as ready when there are blocker flags for missing periods, missing source refs, unresolved source conflicts, unknown currency/scale, material tie-out breaks, or unknown actual/forecast status. Hand off as partial only with explicit limitations.
