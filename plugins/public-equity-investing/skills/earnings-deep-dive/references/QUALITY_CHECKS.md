# Quality Checks

## Hard Fails

- Any user-facing number or quote lacks a source tag.
- GAAP/non-GAAP, reported/CC, unit/scale, period, or estimate definition is mixed without labeling.
- Non-GAAP metric lacks closest GAAP comparable or reconciliation source when available.
- EPS surprise is interpreted without screening for below-the-line, tax, mark-to-market, share-count, non-recurring, or estimate-basis distortion.
- Transcript used as primary source for a filed numeric claim.
- Qualitative guidance converted into a number without a supplied mapping.
- Workbook apply attempted without explicit user request and required workbook/registries.
- Final user-facing report/dashboard, or any generated support note, includes unresolved `{PLACEHOLDER}`, `[TOKEN]`, `TODO`, or authoring `MISSING: add ...`.

## Chat Checklist

- Source posture and limitations are visible near the top.
- Estimate set/vendor/as-of are disclosed.
- Beat/miss and guidance deltas use compatible definitions.
- EPS quality screen is present; if a trigger exists, the full ex-gain / recurring EPS bridge is shown with source tags and confidence.
- The memo identifies what changed, why it matters, and how it changes forward estimates/thesis.
- Quotes are complete enough to be useful and tied to a driver/debate.
- Falsifiers tie to a real next catalyst or reporting cadence.
- Investor-facing prompts include thesis change, likely estimate revision, and stock/valuation skew.

## Deterministic Checklist

- `validate_plan.py` passes before running.
- `validate_normalized_inputs.py` passes or warnings are disclosed.
- Generated outputs write outside the packaged skill tree.
- `verify_tearsheet.py` passes for generated report text or support notes before they are rendered or handed off.
- Packet/apply mode and any workbook limitations are disclosed.

## PM Judgment QA

Fail if the output only summarizes earnings, misses clean-versus-headline quality, lacks transcript/source caveats, omits model/estimate implications, or avoids the position action question.
