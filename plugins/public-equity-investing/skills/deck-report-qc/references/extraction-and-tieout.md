# Extraction and Tie-out Guidance

## First-pass extraction

Use `scripts/inspect_deck_report.py` for first-pass extraction from PPTX, DOCX, XLSX, CSV, TXT, and markdown files. The script creates:
- `segments.csv`: extracted text by slide/page/section/sheet/line range
- `numbers.csv`: detected numerical mentions with rough metric keys and units
- `qc_issue_log.csv`: heuristic issues requiring review
- `qc_support_note.md`: first-pass scan support note
- `scan.json`: structured output for follow-up analysis

The script is intentionally conservative. Treat its findings as leads, not final conclusions.

For a substantive standalone review that produces a refined HTML report after the scan, write a JSON completion record and run the script's `--finalize` path. The record should include `completed_reviews`, `missing_inputs`, and optionally `status` and `reason`. Finalization points the manifest to the polished HTML, retains extraction files as support, removes the provisional report and dashboard contract for ordinary HTML reports, and records only genuinely open verification items. Use `--keep-dashboard-contract` only for an explicitly selected standardized-dashboard output.

## Visual review requirement

Always inspect the original deliverable when available. Deterministic text extraction can miss:
- numbers embedded in images or screenshots
- chart labels rendered graphically
- cut-off text, overlap, font issues, and alignment problems
- small footnotes and low-contrast text
- PDF-only rendering issues
- data tables converted to images

For PDF, scanned, or image-heavy materials, render pages and visually inspect the relevant pages. For PPTX, use presentation rendering where available to verify layout and chart appearance.

For a consequential visual finding, record the pages or slides actually inspected. A final QC report should distinguish:
- source pages/slides visually inspected
- workbook tabs or cells tied out
- external sources independently checked
- facts or claims not independently verified

When the final output is a local standalone HTML report, render and inspect screenshots through a local headless browser rather than the in-app Browser plugin. Check the opening viewport and material downstream sections for hierarchy, table density, clipping, contrast, and legibility before delivery. Inspect at a narrow/mobile viewport as well: wide tables may scroll within their own wrappers, but the document itself must not horizontally overflow; verify `document.documentElement.scrollWidth <= document.documentElement.clientWidth`.

## Tie-out hierarchy

Tie out deck/report values in this order:
1. controlling model or source workbook for output values
2. primary filings, audited financials, transcript, release, credit agreement, indenture, court/regulatory filing, company supplemental, or management reporting package
3. trusted data provider, consensus source, broker research, rating agency, or market-data export
4. company, management, broker, or user-provided materials, clearly labeled
5. internal estimate or analyst assumption, clearly labeled

If sources conflict, use `financial-source-of-truth` conflict handling. Do not silently average or choose the value that looks best.

## Evidence confidence

Use reader-facing confidence labels proportionate to the work performed:
- `confirmed internal mismatch`: the supplied materials prove their own values, labels, calculations, or statements conflict.
- `externally verified error`: a controlling primary or trusted dated external source proves the claim or value wrong.
- `needs review`: support is absent, conflicting, insufficiently dated, or not controlling.

For example, a deck identifier that conflicts with a supplied source note is a confirmed internal conflict. It becomes an externally verified identifier error only after confirmation against an appropriate controlling source.

## Repeated metric matching

A repeated metric should match when the following are the same:
- entity or asset
- metric definition
- period or as-of date
- currency and scale
- scenario
- source/model version

Do not flag as a confirmed mismatch when period, definition, or scenario differs. Instead flag `needs_review` and state the likely reason.

Examples:
- `FY25E EBITDA $120m` vs `2025E EBITDA $120m`: likely same metric
- `Adjusted EBITDA $120m` vs `Lender EBITDA $135m`: not necessarily a mismatch; check definitions
- `Net leverage 4.2x` vs `First-lien net leverage 3.1x`: not necessarily a mismatch
- `10 bps` vs `0.10%`: same magnitude but different unit expression
- `margin up 100 bps` vs `margin up 1.0%`: label as percentage-point convention issue, not necessarily numerical error

## Chart review workflow

For each chart:
1. Record chart title, period, units, series names, and source.
2. Compare the visual direction to the title and takeaway bullet.
3. Compare key labeled values to any table/model/source.
4. Check whether the axis baseline or scaling could mislead.
5. Confirm source/date and whether chart is based on actuals, estimates, company guidance, consensus case, credit/event case, or internal model.
6. Flag ambiguity if chart data is image-only and cannot be extracted.

## Source footnote coverage test

For each page/section, classify source coverage:
- `complete`: source, period/as-of date, and caveats are present
- `partial`: source is present but period/as-of/caveat is incomplete
- `missing`: no meaningful source for material data
- `not_applicable`: conceptual page with no material facts or numbers

Do not require sources for pure table-of-contents, process, or placeholder pages unless they contain factual or numerical claims.

## Completion record

If support artifacts, manifests, or review notes describe review status, update them to reflect the work actually performed. Do not deliver an HTML report that relies on rendered source-page inspection or workbook tie-out while a companion status note says those steps were not performed.
