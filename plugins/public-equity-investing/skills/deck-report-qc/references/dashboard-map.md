# Dashboard Map: Deck And Report QC

Use `dashboard-builder` for Public Equity Investing QC only when the user explicitly selects a standardized dashboard, reusable dashboard template, issue cockpit, remediation tracker, or structured payload-driven render. An ordinary substantive standalone QC review uses a polished standalone HTML senior-review QC report rather than this fixed dashboard map.

## Decision Question

Is the deck, report, note, or memo ready for PM/senior review, and what issues block confidence?

## Recommended Payload

- `kind`: `public_equity_investing_dashboard.v1`
- `mode`: `deck_report_qc`
- `metadata.citation_policy`: `strict`
- `sources`: include reviewed artifact, model files, source pack, filing/release/transcript references, and any style guide

## Recommended Tabs And Modules

1. QC Verdict: `decision_box`, `metric_tiles`, `missing_evidence`.
2. Issue Register: `table`, `cards`.
3. Repeated Number Tie-Out: `table`, `bar_chart`.
4. Source And Footnote Coverage: `table`, `source_list`.
5. Chart And Narrative Tie-Out: `table`, `cards`.
6. Remediation Path: `timeline`, `question_list`.

## Required Evidence

Each issue row needs location, finding, evidence, why it matters, suggested fix, confidence, owner route, and status. Unsupported claims should route to `financial-source-of-truth`; model breaks should route to `model-audit-tieout`.

## Do Not

- Do not call a document externally ready based only on text extraction.
- Do not hide visual/PDF/chart review gaps.
- Do not make issue CSV or scan JSON the lead artifact unless requested.
