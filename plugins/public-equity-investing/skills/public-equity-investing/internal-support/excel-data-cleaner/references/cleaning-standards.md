# Cleaning Standards

Use this reference when the cleaning choice affects model inputs, investment conclusions, or auditability.

## Decision Priority
1. User-provided rules, definitions, mappings, and output format.
2. Source semantics visible in sheet names, formulas, notes, labels, and data structure.
3. Public Equity Investing domain conventions from `domain-playbook.md`.
4. Conservative general defaults.

When rules conflict, preserve the source value and record the conflict in `assumptions_audit` unless the user explicitly decides.

## Non-Negotiables
- Preserve raw data and original-to-clean mappings.
- Prefer reversible changes: trim text, normalize obvious blanks, parse clear numbers/dates, rename headers with mappings.
- Do not silently fuzzy-merge entities, impute missing values, delete outliers, change signs, collapse categories, convert currencies, or aggregate detail rows.
- Treat identifiers as text: CUSIP, ISIN, account, SKU, zip, employee ID, phone-like fields.
- Keep units/currencies explicit; if mixed, preserve or add unit/currency fields.

## Structural Rules
- Detect headers as the first mostly non-empty label row followed by detail data; beware titles, metadata, footnotes, and multi-row headers.
- Combine multi-row headers only when levels form meaningful labels; preserve the header path in the dictionary.
- Remove fully empty rows/columns from `clean_data`; preserve them in `raw_source`.
- Flag subtotals/section rows. Remove from detail only when obvious and log the rule.
- Fill down merged/group labels only when clearly hierarchical and needed for analysis-ready rows.

## Header Rules
- Use clear, unique labels suitable for Excel tables, formulas, pivots, and imports.
- Keep standard market abbreviations: ARR, MRR, EBITDA, COGS, CAC, SKU, SLA, API, ID.
- Disambiguate duplicate headers with source context, not arbitrary suffixes when avoidable.
- Preserve both display names and machine names when the user needs import-ready output.

## Type Rules
- Normalize blank tokens: `""`, `-`, `--`, `n/a`, `na`, `null`, `none`, `not available`, `#n/a`.
- Parse obvious accounting numbers: `(1,234.50)` -> `-1234.50`.
- Do not parse magnitude suffixes such as `$1.2m` unless explicitly supported; otherwise flag.
- Treat `12%`, `12`, `0.12`, and `12 bps` as different until context proves the convention.
- Use real dates for actual dates; preserve fiscal periods such as `Q1 FY26`, `Apr-26`, or `2026-04` as periods when day precision is not real.
- Normalize booleans only for truly boolean fields; do not collapse business statuses with distinct meanings.

## Missing, Duplicate, And Exception Rules
- Missingness severity:
  - **Critical:** key/date/amount/owner/status/domain-required field missing.
  - **Analytical:** optional dimension missing but row usable.
  - **Cosmetic:** display field or note missing.
- Duplicate policy:
  - remove exact duplicates only when all values match and source identity is not needed;
  - keep and flag same-key rows with conflicting values;
  - merge only with a supplied or unambiguous business rule.
- Outliers are often the point. Flag unusual values rather than deleting them.

## Common Public Equity Investing Keys
- Issuer financials: issuer + metric + period + scenario/status + currency + units.
- Markets/risk: portfolio/account + security ID/ticker + date + metric.
- ETF/index: index or ETF + constituent ticker/security ID + effective/as-of date + weight + source.
- Credit Markets handoff / equity-risk signal: issuer + instrument ID/CUSIP/ISIN + maturity + metric + pricing date, only to preserve source posture or route out.
- Consensus/provider: provider + ticker + metric + fiscal period + estimate date + actual/estimate flag.
- Event-driven: target/acquirer + security ID/ticker + deal/event date + metric.

## Formula And Workbook Handling
- Preserve formulas unless asked to convert to values.
- Do not break named ranges, external links, pivots, charts, or formulas without warning.
- If extracting from formula-driven reports, state whether displayed values or formulas were used.

## Final QA
Before delivery, confirm raw source is preserved, row grain is coherent, headers are unique, types/formats are defensible, IDs remain text, duplicates are documented, quality checks are populated, assumptions are logged, and the workbook opens cleanly.
