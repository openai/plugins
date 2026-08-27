# Equity Model Update Workflow

## Boundary

Own safe copied-workbook updates, source-to-model refresh maps, model change logs, and post-update tie-out checklists for public-company models. Do not own pure earnings prose, full formula audits, original workbook mutation, trade pitches, or memo synthesis.

## Operating Modes

### No User Model

- Produce a screen-grade model update checklist.
- State that user-model deltas are unavailable.
- Use public or connected sources only when available.
- Focus on likely model lines, KPI thresholds, missing data, and post-print update tasks.
- Use `csv_update_map_export` only; do not imply an Excel model was updated.

### Partial Context

- Preserve user-provided assumptions and focus areas.
- Separate sourced facts from agent estimates.
- Flag missing model lines, source IDs, fiscal periods, units, and stale consensus.
- Produce a first-pass change map rather than pretending the model has been updated.
- If a workbook exists but mappings are incomplete, create `model_update_control_pack.xlsx` with review tabs instead of editing model cells.
- If source facts cannot map to comparable workbook inputs, classify them as `reference_only` or `missing_model_architecture`; do not populate proposed values or estimate-change deltas.

### Existing Workbook Or Model

- Audit before changing.
- Default to `xlsx_update_copy` when source/model/workbook mapping is sufficient.
- Always preserve the uploaded original; write only to a copied workbook.
- Preserve tabs, formulas, workbook structure, source files, hidden sheets, names, charts, pivots, and user hardcodes.
- Update only mapped input cells with exact sheet/cell references, source IDs, freshness labels, confidence, and prior/new values.
- Do not overwrite formulas unless the user explicitly approves through `overwrite_formula_allowed`; even then, label it for model-owner review.
- If target cells are formulas, missing, protected, merged, stale, or ambiguous, create `model_update_control_pack.xlsx` with `Update_Cover`, `Source_Map`, `Rebuild_Requirements`, `Change_Log`, `Tie_Out`, and `Stale_Data` tabs.
- When required revenue, margin, EPS, segment, share-count, or net-cash schedules do not exist, describe the workbook as structurally insufficient for a refreshed valuation and specify rebuild requirements.
- Route formula integrity, circularity, external links, and tie-out checks to `model-audit-tieout`.

### Pre-Print Setup

- Compare user model, guidance, consensus, revision path, peer prints, price action, and options-implied move where available.
- Identify model lines that will matter most after the print.
- Build thresholds for clean beat, messy beat, in-line, miss/reset, and thesis-break cases.

### Post-Release / Pre-Call

- Map reported actuals and updated guidance to model lines.
- Separate accounting noise from durable driver changes.
- For EPS lines, bridge reported GAAP EPS to adjusted/operating or recurring EPS before changing forward EPS. Isolate tax, share-count, below-the-line, mark-to-market, and non-recurring items.
- Keep valuation categories separate: unchanged legacy cached valuation, informational/mechanical reference bridge where supportable, and refreshed target value only when the forecast architecture can be updated and tied out.
- Generate management questions tied to the model update map.
- When workbook mappings are safe, return the copied updated workbook first, then the model-update dashboard/control outputs.

### Post-Call Update

- Incorporate transcript clarifications.
- Update the source-to-model map and change log.
- Preserve unresolved items in the tie-out checklist.
- Hand final workbook integrity to `model-audit-tieout`.
- If the control pack or updated workbook is restyled, renamed, or otherwise re-exported for final handoff, promote the final exported workbook in `manifest.json`, `run_log.json`, and `model_update_citations.json`, including final sheet-name references.
- Re-run workbook preflight before applying any second-pass updates; prior model cells may have moved after analyst edits.

## Source Hierarchy

Use this order unless the user instructs otherwise:

1. User-provided model, files, notes, and assumptions.
2. Company primary sources: filings, releases, supplements, decks, transcripts, investor days.
3. Connected market-data, consensus, and research apps when available.
4. Broker/internal research and prior user work.
5. Industry, macro, government, and alternative datasets.
6. Public web fallback.

## Required Labels

Label values as reported actual, company guidance, consensus, user estimate, agent estimate, market-implied, inferred/calculated, or judgment. For EPS, also label GAAP, adjusted, operating, or recurring basis. Show the calculation for inferred values and flag stale or missing source IDs.

## Neighboring Skills

- `financial-source-of-truth`: source hierarchy, evidence posture, freshness gaps.
- `financials-normalizer`: messy financial statement extraction or normalization.
- `excel-data-cleaner`: raw tabular cleanup before mapping.
- `earnings-preview`: event setup when no model update contract is needed.
- `earnings-deep-dive`: post-print interpretation and narrative.
- `scenario-sensitivity-generator`: model sensitivity tables.
- `thesis-tracker`: confirm/disconfirm evidence ledger.
- `long-short-pitch`: investable recommendation, sizing, add/trim/exit.
- `memo-builder`: formal IC/client/PM written memo.
- `model-audit-tieout`: workbook formula, link, check, and tie-out integrity.
