# Issue Taxonomy

Use this taxonomy to classify deck and report QC findings.

## Severity levels

| Severity | Definition | Examples |
|---|---|---|
| critical | likely to change decision, valuation, market view, recommendation, or trust in the analysis | wrong EPS/EBITDA in valuation summary; EV/EBITDA conflicts with model; price target or rating support conflicts with source; source contradicts thesis |
| high | material issue that must be fixed before circulation | repeated metric mismatch; missing source on key market data; chart contradicts title; unit ambiguity in valuation table |
| medium | localized issue that should be fixed but probably does not change the decision | stale as-of date, inconsistent decimals, unclear footnote, minor chart label mismatch |
| low | polish or formatting issue | inconsistent capitalization, alignment, extra spaces, minor style inconsistency |
| needs_review | possible issue that cannot be confirmed from available files | chart appears image-only; number may use different period; source/model missing |

## Issue types

### number_mismatch
Same metric appears with conflicting values.
Required fields: location, metric, values, likely controlling value, suggested fix.

### unit_or_period_ambiguity
Metric lacks clear unit, currency, scale, period, or scenario.
Required fields: location, ambiguous term, why it matters, suggested fix.

### source_gap
Material claim, table, or chart lacks source, as-of date, period, or caveat.
Required fields: location, claim/metric, missing source element, suggested fix.

### source_conflict
Two sources disagree or the deck/report value conflicts with controlling source.
Required fields: locations/sources, conflicting values, source hierarchy, recommended resolution.

### chart_narrative_mismatch
Chart visual/data does not support title, subtitle, or bullet takeaway.
Required fields: location, chart statement, conflicting evidence, suggested fix.

### chart_format_or_label_issue
Axis, legend, series, label, scale, or chart format is confusing or inconsistent.
Required fields: location, issue, possible interpretation risk, suggested fix.

### narrative_contradiction
Executive summary, section page, conclusion, risk page, or recommendation conflicts with another part of the document.
Required fields: conflicting locations, statements, recommended rewrite direction.

### caveat_or_disclosure_gap
Claim relies on estimates, company/management materials, unaudited figures, non-GAAP data, assumptions, or preliminary numbers without labeling.
Required fields: location, claim, needed caveat.

### formatting_consistency
Style, alignment, labels, spacing, capitalization, page numbering, or table formatting is inconsistent.
Required fields: location, issue, fix.

### readability_accessibility
Content is hard to read or navigate because of small font, low contrast, missing title, overloaded page, color-only encoding, or image text.
Required fields: location, issue, audience impact, fix.

### missing_support_file
A required model/source/deck/report supporting artifact is missing.
Required fields: missing file, why needed, what can/cannot be verified without it.

## Recommended remediation order

1. Fix critical and high number/source/model issues.
2. Fix chart-narrative mismatches and misleading titles.
3. Fix unit, period, and caveat ambiguity.
4. Fix source footnotes and as-of dates.
5. Fix formatting and readability issues.
6. Re-run the QC pass after changes.

## Confidence labels

Use these labels in the issue log:
- `confirmed`: issue is directly supported by available files
- `likely`: issue appears likely but needs one supporting file or visual confirmation
- `possible`: heuristic or judgment issue; needs human review
- `blocked`: cannot assess without missing source/model/visual artifact
