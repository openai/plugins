# Deck Report QC Dashboard Pack

Use this pack only when the user explicitly selects a standardized dashboard, reusable dashboard template, issue cockpit, remediation tracker, or structured payload-driven render for a Public Equity Investing deck/report QC review. For an ordinary substantive standalone QC review, produce a polished standalone HTML senior-review QC report following the flexible HTML artifact standard and the owning skill's evidence-scope guidance instead of this fixed module map.

## Producer Role

`deck-report-qc` owns issue identification, severity, source/number tie-out, chart/narrative checks, circulation posture, and remediation sequence. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `deck_report_qc`
- `layout`: `single_page` for reusable QC packs unless the user explicitly requests tabs
- `hero.callout`: whether the deliverable is clear, needs targeted fixes, blocked, or not circulable
- `snapshot`: QC posture, issue count, critical/high count, source coverage, repeated-number status, chart tie-out status, missing support files
- `sources`: controlling artifact, support model/files, evidence ledger, filings/releases/transcripts, and extracted first-pass scan outputs
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `qc-verdict`
   - `decision_box`: circulation posture, top blocker, recommended remediation order, and review confidence
   - `metric_tiles`: issue counts, critical/high count, source coverage, repeated-number status, chart status, missing support
2. `issue-log`
   - `table`: page/slide/section, severity, issue type, finding, evidence, suggested fix, and owner/status if known
3. `number-source-tieout`
   - `table`: repeated metrics, units, periods, source/model tie-out, mismatches, and confidence
   - `cards`: source-footnote coverage and caveat/disclosure gaps
4. `chart-narrative`
   - `table`: chart titles, axes, series, narrative takeaway, source support, and inconsistency notes
5. `remediation`
   - `timeline`: fix sequence, dependencies, missing support files, and review checkpoints
   - `missing_evidence`: unavailable model/source files, inaccessible charts, scanned pages, weak source metadata, and unresolved judgment calls

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite the controlling artifact and every support file or source used for a QC finding.
- Label deterministic findings versus judgment calls and use `needs_review` when the evidence is incomplete.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not certify external circulation from heuristic scans alone.
- Do not edit the original deck/report unless the user explicitly asks for remediation.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm severity ordering, repeated-number tie-out, source coverage, chart/narrative findings, and remediation sequence are visible.
- Confirm uncertainty is labeled rather than hidden.


public-equity research support layer requirement: QC dashboards should surface equity decision impact first: EPS/revenue/KPI support, valuation and price-target support, rating/stance support, benchmark/ETF/index exposure, catalyst claims, source conflicts, market-data freshness, and any Credit Markets handoff.
