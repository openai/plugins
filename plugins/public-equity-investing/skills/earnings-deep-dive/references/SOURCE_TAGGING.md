# Source Tagging (Mandatory)

## Table of contents
1. [Rules](#rules)
2. [Standard format](#standard-format)
3. [Examples by artifact type](#examples-by-artifact-type)
4. [Common failure modes](#common-failure-modes)

---

## Rules
1) Every number and quote must have a Source Tag.
2) A Source Tag must be **specific enough that a human can find it in under 30 seconds**.
3) Use the most authoritative source available (filings > PR tables > deck > transcript).
4) If the only source is the transcript, label `CALL-ONLY` and cross-check any numeric claim against filings if possible.
5) If the value is not present, use the most precise label: `not guided`, `not disclosed`, `not provided`, or `MISSING: <dependency>`.

## Standard format
Use a single string in this form:

```
<ArtifactLabel> | <LocationPointer> | <OptionalNotes>
```

Where:
- **ArtifactLabel** = one of: `10-Q`, `10-K`, `8-K`, `Earnings PR (Exhibit 99.1)`, `Deck`, `Prepared Remarks`, `Transcript Prepared`, `Transcript Q&A`, `Company IR`, `SEC`, `Consensus/Data Provider`, `Web Fallback`, `Model`
- **LocationPointer** should be one of:
  - `p.<page>` + `Table <name/number>`
  - `p.<page>` + `Section <heading>`
  - `Slide <#>`
  - `line <#>` (for transcript) + speaker context

## Examples by artifact type

### SEC filings / exhibits
- `10-Q | p.12, Consolidated Statements of Operations | GAAP revenue`
- `8-K | Exhibit 99.1 p.3, Table 1 | Non-GAAP reconciliation`

### Earnings press release (non-filed copy)
- `Earnings PR | p.2, Highlights bullets | Guidance range statement`

### Earnings deck
- `Deck | Slide 7, Segment performance table | Segment revenue`

### Transcript (Prepared)
- `Transcript Prepared | CEO, line 145–162 | Demand commentary`

### Transcript (Q&A)
- `Transcript Q&A | CFO → Analyst (Firm), line 980–1006 | GM guide cadence`

### Model references (for internal traceability)
- `Model v2026.02.21_1430ET | Drivers tab, NamedRange: GM_Assumption | Update applied`

### Public-source fallback
- `Consensus/Data Provider | retrieved 2026-04-07 | revenue estimate proxy`
- `Web Fallback | provider page, retrieved 2026-04-07 | third-party transcript; official transcript not found`

## Common failure modes
- **Too vague:** `10-Q` (missing page/table)
- **Wrong precedence:** citing transcript for a GAAP number that is in the 10-Q
- **No speaker context:** transcript quote without speaker + section
- **No reconciliation:** non-GAAP metric with no GAAP comparable + reconciliation tag
