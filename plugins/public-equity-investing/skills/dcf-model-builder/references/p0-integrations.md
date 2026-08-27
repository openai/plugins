# P0 Integrations

## Shared core
- `financial-source-of-truth`: use before modeling when source freshness, source hierarchy, citations, or fact/assumption separation matters. Feed its outputs into `source_basis`.
- `financials-normalizer`: use before modeling when historicals come from filings, PDFs, XLS/CSV, VDR exports, management statements, or non-standard accounting presentations. Feed normalized financials into `historicals` and driver assumptions.
- `excel-data-cleaner`: use when raw Excel/CSV data has messy headers, dates, units, merged cells, or QA flags before it becomes `plan.json` input.
- `model-audit-tieout`: use after model generation for formula, hardcode, source, sign, link, and tie-out checks. This DCF skill includes machine checks but not a full external workbook audit.
- `scenario-sensitivity-generator`: use when the user needs bespoke downside cases, break-even cases, Monte Carlo-style stress, commodity decks, rate cases, or event probabilities beyond bundled sensitivities.
- `memo-builder`: use `p0_handoff`, the workbook `Cover`, and optional `support_note.md` to produce public-equity investment, client, PM, or committee memos.
- `deck-report-qc` and `style-guide-adapter`: use after exporting exhibits into decks or reports.

## Public Equity Investing
- `equity-model-update`: use after earnings, filings, guidance changes, or transcript updates before running the DCF.
- `comps-valuation`: use for peer multiple support, market cross-checks, implied valuation, and football-field style support.
- Credit Markets: use when credit instruments, creditworthiness, covenant packages, restructuring, recovery waterfalls, spread/yield relative value, or debt-security valuation drive the case; keep only common-equity read-through locally.
- `long-short-pitch`: use when converting the DCF into a tradable long/short recommendation with catalysts, risk, and variant view.
- `thesis-tracker`: use the DCF drivers to create confirm/disconfirm signals and update cadence.
- `earnings-preview` and `earnings-deep-dive`: use to update assumptions around prints.
- `sector-context-overlay`: use for banks, insurance, REITs, E&P, biotech/pharma, exchanges/market infrastructure, marketplaces, SaaS, and other supported areas where generic FCFF is insufficient.
