# Output Templates

## Rapid screen template

```markdown
# Model Audit Rapid Screen: [model/company/deal]

## Readiness posture
**Status:** [green/yellow/red/gray]
**Decision use:** [ready / ready with caveats / not ready / not assessable]
**Scope reviewed:** [workbook tabs, source docs, outputs, limitations]

## Top issues
| severity | issue | location | decision impact | fix |
|---|---|---|---|---|
| [critical/high/etc.] | [finding] | [tab/cell/source] | [impact] | [action] |

## What appears solid
- [area]
- [area]

## Must-fix before use
1. [fix]
2. [fix]
3. [fix]

## Open questions / missing files
- [question]
```

## Full audit memo template

```markdown
# Model Audit Tie-out Memo: [model/company/deal]

## Executive summary
[3-6 bullets on model readiness, major issues, source support, and decision impact.]

## Decision-readiness posture
**Posture:** [ready for decision / ready with caveats / not ready / not assessable]
**Reason:** [brief explanation]
**Permitted use:** [use for decision / preliminary screen only / do not use for portfolio action until remediated and re-audited]
**Reviewed for:** [ic, credit committee, client deck, research review, earnings, trading, board, etc.]
**Materiality lens:** [what would change the decision]

## Model overview
| item | assessment |
|---|---|
| model type | [dcf/3-statement/comps/Credit Markets/event-driven/risk/etc.] |
| workbook / files reviewed | [file names] |
| key output(s) | [outputs] |
| key tabs | [tabs] |
| source documents reviewed | [sources] |
| limitations | [what was not reviewed] |

## Priority issue log
| severity | finding_type | category | location | finding | why it matters | recommended fix | owner |
|---|---|---|---|---|---|---|---|
| [critical/high/etc.] | [Formula/control defect / Source contradiction / Unsupported assumption / Missing forecast refresh / Missing decision output / Not comparable without bridge] | [category] | [tab/cell/doc] | [finding] | [impact] | [fix] | [owner] |

## Formula and workbook controls
- **Formula consistency:** [findings]
- **Hardcodes:** [findings]
- **External links / hidden tabs:** [findings]
- **Checks:** [findings]
- **Circularity / volatility:** [findings]

## Source tie-out findings
| output_or_driver | model_location | model_value | source | source_value | tie_status | evidence_label | decision_impact |
|---|---|---:|---|---:|---|---|---|
| [driver] | [tab/cell] | [value] | [source] | [value] | [ties/etc.] | [label] | [impact] |

## Assumption and scenario critique
- **Base case:** [support and concerns]
- **Downside case:** [support and concerns]
- **Upside case:** [support and concerns]
- **Sensitivities:** [true drivers vs missing drivers]
- **Illustrative audit sensitivity:** [diagnostic stress clearly labeled as auditor-created; do not describe as the repaired base case]

## Recommended remediation sequence
1. [critical fix]
2. [high fix]
3. [medium fix]

## Evidence requests
- [source request]
- [issuer/management/broker/provider/lender question]

## Appendix: scope and method
[Briefly describe workbook inspection, source documents reviewed, manual checks, and limitations.]
```

## Issue log row format

Use this format for every issue. Finding type distinguishes broken mechanics from unsupported underwriting or missing package scope:

```markdown
| severity | finding_type | category | location | finding | why it matters | recommended fix | owner |
|---|---|---|---|---|---|---|---|
| high | Formula/control defect | formula_integrity | Debt Schedule!F42 | revolver paydown formula breaks in the downside case | understates liquidity trough and covenant pressure | correct formula across forecast periods and rerun downside | analyst |
```

## Formula exception format

```markdown
| sheet | cell | issue | formula/value | recommended review |
|---|---|---|---|---|
| [sheet] | [cell] | [hardcoded number in formula / external link / volatile function / inconsistent formula] | `[formula]` | [action] |
```

## Source tie-out ledger format

```markdown
| output_or_driver | model_location | model_value | source_name | source_location | source_value | tie_status | variance | evidence_label | as_of_date | decision_impact | recommended_action |
|---|---|---:|---|---|---:|---|---:|---|---|---|---|
| [driver] | [tab/cell] | [value] | [source] | [page/table] | [value] | [ties] | [variance] | [label] | [date] | [impact] | [action] |
```

## Decision-readiness language

Use direct language:
- "the model is not ready for ic use until the debt schedule and source tie-outs are fixed."
- "the valuation output appears mechanically coherent, but the margin and terminal-value assumptions are assumption-led and need sensitivity support."
- "the model can be used for a preliminary screen, but not for a final investment recommendation."
- "do not use for portfolio action until remediated and re-audited."
- "the Credit Markets handoff is blocked by missing covenant definitions and unsupported add-backs."

For an audit-only mandate, lead with the audit verdict and permitted use rather than an investment stance. Use `add`, `trim`, `exit`, `hedge`, or `wait for proof` only when an investment decision output is actually being assessed.

For operating and three-statement models, a linked valuation/scenario decision output may sit in a companion workbook or downstream package. Treat missing decision output as a package-readiness blocker when the stated use requires it; do not automatically treat absent target price inside the operating workbook as a formula or architecture defect.

Avoid vague language:
- "looks fine"
- "probably okay"
- "minor issues" when severity is unknown
- "audited" unless a real audit was performed by qualified auditors

## Follow-up remediation output

When the user asks to fix issues after the audit, provide:

```markdown
# Remediation Plan

## Changes I recommend making now
1. [change]
2. [change]

## Changes requiring user/source confirmation
1. [change]
2. [change]

## Changes I would not make without senior review
1. [change]
2. [change]

## Files or data needed
- [file]
```

If actually editing the workbook, preserve raw/source tabs where possible and document every changed cell/range.
