# Model Workbook Specification

Use this reference when creating, restructuring, or reviewing the Excel/Sheets workbook.

## Workbook principles

- Keep raw data separate from normalized outputs.
- Use a single `Control` tab for valuation date, currency, source hierarchy, fiscal basis, and scenario selections.
- Avoid hardcoded values inside formulas. Place assumptions in clearly marked input cells.
- Every output should trace back to source data, assumptions, and formulas.
- Use consistent row order across data tabs so peer formulas can be audited quickly.
- Build for refreshability: formulas should copy across peer rows and update from clearly defined inputs.

## Recommended tabs

### Cover

First visible workbook tab. Required by `../../../../shared/workbook-artifact-standard.md` for generated XLSX artifacts.

Include:

- target company, ticker/security, valuation date, currency, units, workbook mode, and model status;
- target snapshot and peer-universe counts;
- selected multiple, low/mid/high implied value per share, and chart-ready valuation range;
- peer median/quartile tables and fit/outlier indicators where populated;
- source count, source gaps, stale-market-data flags, and confidence labels;
- QA status, denominator review flags, leverage/calendar comparability flags, and unresolved checks;
- workbook map for `Control`, `Universe`, `Market_Data`, `Financials`, `Multiples`, `Benchmarking`, `Valuation`, `Sensitivity`, `Sources`, and `QA_Log`.

Native charts are encouraged when using XlsxWriter. At minimum, include chart-ready cover rows for implied value/share range and primary trading multiple distribution.

### README / Model Guide

Include:

- Model purpose.
- Target company.
- Valuation date.
- Currency and units.
- Version/date prepared.
- Major limitations.
- Update steps.

### Control

Minimum fields:

- Target company/ticker.
- Valuation date.
- Reporting currency.
- Output currency.
- FX source/date if applicable.
- Fiscal year-end.
- LTM period definition.
- Forward estimate periods.
- Source priority.
- Scenario selection.
- QA status.

### Universe

Recommended columns:

- Ticker.
- Company name.
- Exchange/country.
- Peer tier: Target, Core, Secondary, Adjacent, Watchlist, Excluded.
- Business description.
- Segment/revenue mix.
- Geography.
- Customer/end-market mix.
- Size relevance.
- Growth relevance.
- Margin relevance.
- Inclusion rationale.
- Exclusion rationale.
- Analyst notes.

### Market_Data

Recommended columns:

- Ticker.
- Price.
- Valuation date.
- Basic shares.
- Diluted shares.
- Options/RSUs/converts adjustment.
- Market capitalization.
- Total debt.
- Lease debt treatment.
- Preferred stock.
- Minority interest.
- Cash and short-term investments.
- Enterprise value.
- Source.
- Source confidence.

Enterprise value bridge:

`Equity Value = Share Price * Diluted Shares`

`Enterprise Value = Equity Value + Debt + Preferred Stock + Minority Interest + Other Claims - Cash and Cash Equivalents - Non-operating Investments`

Adapt for sector-specific conventions. For banks and insurers, avoid standard EV metrics unless specifically justified.

### Financials

Recommended columns by period:

- Revenue.
- Gross profit.
- EBITDA.
- EBIT.
- Net income.
- EPS.
- Operating cash flow.
- Capital expenditure.
- Free cash flow.
- Sector KPIs.
- Source and definition.

Keep reported, adjusted, and normalized figures in separate rows or columns. Do not blend them silently.

### Adjustments

Include:

- Calendarization adjustments.
- FX translation.
- Non-recurring items.
- Stock-based compensation treatment.
- M&A/pro forma adjustments.
- Discontinued operations.
- Lease accounting adjustments.
- Segment or carve-out adjustments.
- Consensus definition adjustments.

Every adjustment should include a source, rationale, amount, period, and whether it affects all peers or only one company.

### Multiples

Recommended outputs:

- EV / Revenue: LTM, CY0, CY1, CY2.
- EV / EBITDA: LTM, CY0, CY1, CY2.
- EV / EBIT: LTM, CY0, CY1, CY2.
- P / E: LTM, CY0, CY1, CY2.
- FCF yield or P / FCF.
- Sector-specific metrics.
- Peer statistics: median, mean, harmonic mean where useful, 25th/75th percentile, min/max, core-peer median.
- Flags for negative, zero, not meaningful, or outlier denominators.

Do not calculate a misleading multiple when the denominator is negative, near zero, not comparable, or not meaningful. Use `NM` and explain.

### Benchmarking

Recommended categories:

- Size: revenue, market cap, EV.
- Growth: revenue CAGR, EBITDA CAGR, KPI growth.
- Profitability: gross margin, EBITDA margin, EBIT margin, FCF margin, ROIC.
- Capital intensity: capex/revenue, working capital, leverage.
- Quality: recurring revenue, retention, pricing power, customer concentration, cyclicality, regulation, asset intensity.
- Valuation premium/discount rationale.

### Valuation

Include:

- Selected peer set and selected multiple range.
- Target metric used for valuation.
- Implied enterprise value.
- Net debt and other claims.
- Implied equity value.
- Diluted shares.
- Implied value per share.
- Scenario outputs.
- Conclusion narrative.

### Sensitivity

Include at least one two-way sensitivity table:

- Selected multiple range vs target financial metric.
- Selected multiple range vs net debt or diluted share count.
- Growth/margin scenario vs selected multiple where appropriate.

### Sources

Each key source should include:

- Company/ticker.
- Metric.
- Period.
- Source name.
- Document or connector path.
- URL/accession if applicable.
- Retrieval date.
- Data date.
- Confidence level.
- Notes.

### QA_Log

Include:

- Check name.
- Status: Pass, Fail, Warning, Not run.
- Finding.
- Fix/action.
- Owner or next step.
- Date completed.

## Excel formula rules

- Use formulas for calculated fields whenever possible.
- Keep assumption cells separate and clearly marked.
- Use `IFERROR` sparingly; do not hide real issues. Prefer explicit denominator checks.
- Use `NM` or blank with flags for not-meaningful multiples.
- For peer statistics, calculate both all-peer and core-peer statistics.
- Use consistent rows and columns across tabs to allow formula copy-down.
- Avoid volatile formulas unless necessary.
- Avoid external links in final deliverables unless explicitly requested.

## Formatting conventions

Use a consistent convention, adapted to the user's template if one exists:

- Inputs: clearly shaded or marked.
- Formulas: standard model style.
- Linked cells: visually distinct from local formulas.
- Outputs: clearly highlighted and easy to find.
- Hardcodes in output tabs: avoided unless labeled as assumptions.
- Negative values and `NM`: visible and not hidden by formatting.

## Formula QA checks

Check for:

- Broken formulas: `#REF!`, `#VALUE!`, `#DIV/0!`, `#N/A`.
- Inconsistent formulas across peer rows.
- Hidden hardcodes in formulas or output ranges.
- Circular references.
- External links.
- Wrong signs for cash, debt, minority interest, and non-operating assets.
- Currency/unit mismatches.
- LTM and NTM mismatches.
- Outliers included without rationale.

## Public Equity PM Workbook Additions

Include `Multiple_Bridge` and `PM_Action_Box` tabs or equivalent sections. The Cover should show current price, implied value/share range, upside/downside to spot, selected multiple rationale, peer-set confidence, what is priced in, PM action implication, and unresolved data gaps.
