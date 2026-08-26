# Output Templates

## Default QC report

```markdown
# Deck / Report QC

## Executive QC verdict
- First-pass posture: [first-pass-clear | senior-review-ready | needs-targeted-fixes | not-circulable | blocked]
- Highest severity: [critical | high | medium | low | needs_review]
- Bottom line: [1-3 sentences]

## Review scope and evidence limitations
| Evidence area | Reviewed / available | Status | Limitation or next confirmation |
|---|---|---|---|
| Controlling artifact | PDF pages/slides inspected: [...] | visually inspected | [...] |
| Supporting model/workbook | Tabs/outputs tied out: [...] | tied out / partial | [...] |
| External source verification | Sources checked: [...] | verified / not performed | [...] |
| Not independently verified | Market data, company facts, estimates, source claims: [...] | open | [...] |

## Decision-critical tie-out
| Decision input | Deck/report value | Controlling support value | Confidence | Decision impact / correction |
|---|---|---|---|---|
| DCF value/share | [...] | [...] | confirmed internal mismatch | [...] |

## Top issues to fix first
| Priority | Severity | Confidence | Location | Issue | Why it matters | Suggested fix |
|---:|---|---|---|---|---|---|
| 1 | high | confirmed internal mismatch | Slide 7 | FY25E EBITDA differs from valuation summary | impacts multiple and valuation range | tie to model tab Outputs cell X |

## Issue log
| ID | Severity | Type | Confidence | Location | Finding | Evidence | Suggested fix | Owner/route |
|---|---|---|---|---|---|---|---|---|

## Recommended remediation sequence
1. [fix]
2. [fix]
3. [fix]

## Repeated metric / number tie-out
| Metric | Locations | Values found | Unit/period/scenario | Status | Comment |
|---|---|---|---|---|---|

## Source and footnote coverage
| Location | Material data/claim | Source present? | As-of/period present? | Caveat needed? | Status |
|---|---|---:|---:|---:|---|

## Chart and narrative tie-out
| Location | Chart / table | Narrative claim | Tie-out status | Issue / fix |
|---|---|---|---|---|

## Formatting and readability
| Location | Issue | Suggested fix |
|---|---|---|

## Missing files / open questions
- [source/model/file needed and why]
```

## Confidence descriptions

Use these labels in reader-facing QC output:
- `confirmed internal mismatch`: contradiction or calculation failure proved within the supplied deck, report, workbook, or source pack.
- `externally verified error`: incorrect value or claim proved against a controlling primary or trusted dated external source.
- `needs review`: potential issue or unresolved conflict that cannot be proven from available support.

Do not describe an external market fact, company identifier, or third-party claim as wrong when the supplied files only demonstrate an internal discrepancy.

## Standalone HTML senior-review report

For substantial standalone QC work, render a polished HTML report following `../../../shared/html-artifact-standard.md`. Keep the opening view focused on the verdict, circulation posture, review scope, and decision-critical tie-out. When a decision-critical tie-out exists, it must appear before a narrative `Top Issues`, `Must Fix Before Circulation`, or full issue-log section; metric tiles may summarize it, but do not substitute for the tie-out table or bridge. Put the complete issue register and source/presentation detail below that first-read layer. Use color to signal severity sparingly and avoid turning the review into a generic dashboard shell.

At narrow/mobile widths, tables may use a horizontally scrollable wrapper with a brief cue where useful, but the overall HTML page must remain constrained to the viewport. During local headless-browser QA, confirm `document.documentElement.scrollWidth <= document.documentElement.clientWidth` at a representative mobile width. Apply `min-width: 0` to grid or section children and `max-width: 100%; overflow-x: auto` to table wrappers when wide tables are retained.

## Fast senior-readout format

Use this when the user asks for a quick review or red flags only:

```markdown
## QC readout
Posture: [posture]

Must fix before circulation:
1. [issue - location - why it matters]
2. [issue - location - why it matters]

Should fix:
1. [issue]
2. [issue]

Looks clean:
- [area reviewed]

Blocked / not verified:
- [missing support]
```

## Issue log CSV schema

Use these columns if producing a CSV issue log:

```text
issue_id,severity,issue_type,confidence,source_file,location,metric_or_claim,finding,evidence,why_it_matters,suggested_fix,owner_route,status
```

## Circulation posture language

Use concise language:
- `first-pass-clear`: no heuristic blockers identified; still requires visual/source/model review before external circulation.
- `senior-review-ready`: suitable for MD/PM/partner review with limited marked questions.
- `needs-targeted-fixes`: do not circulate externally until listed fixes are made.
- `not-circulable`: material inconsistencies remain; artifact could mislead decision-makers.
- `blocked`: cannot assess because required source/model files are missing.

Medium source gaps, repeated-number mismatches, and unit/period ambiguity should generally be mapped to `needs-targeted-fixes`.

## Remediation routing language

Examples:
- `route to model-audit-tieout`: formula/model output issue, not a deck-only issue.
- `route to financial-source-of-truth`: source conflict or stale-data rule needed.
- `route to excel-data-cleaner`: source table is too messy to tie out reliably.
- `route to dcf-model-builder`: valuation model needs rebuild or scenario correction.
- `route to memo-builder`: after fixes, synthesize issue implications for IC.
