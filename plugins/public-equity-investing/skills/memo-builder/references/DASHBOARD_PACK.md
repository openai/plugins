# Memo Builder Dashboard Pack

Use this pack only when the user explicitly requests a standardized dashboard, reusable dashboard template, PM cockpit, or structured payload-driven render for a memo, committee note, PM update, client-style research packet, or source-heavy written artifact. An ordinary substantive memo should remain a polished standalone HTML memo following `../../../shared/html-artifact-standard.md`.

## Producer Role

`memo-builder` owns memo synthesis, narrative architecture, argument quality, evidence selection, and audience framing. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `memo_builder`
- `layout`: `single_page` for full memo/report packages unless the user explicitly requests tabs
- `hero.callout`: the memo's main decision, recommendation, or debate
- `snapshot`: recommendation/research posture, thesis status, valuation or risk skew if supportable, next catalyst, top unresolved issue, source confidence
- `sources`: user materials, primary filings/releases/transcripts, model outputs, market/consensus data, and assumptions separated
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `memo-summary`
   - `executive_summary`: full memo summary with recommendation, evidence, caveats, and audience-specific read
   - `decision_box`: decision, action posture, thesis change, estimate/model effect, and next catalyst
2. `argument`
   - `cards`: core arguments, evidence, counterarguments, and decision implications
   - `table`: key metrics, valuation, model changes, or source-backed debate items
3. `scenarios-risks`
   - `scenario_map`: upside/base/downside, risk/reward, or decision cases
   - `cards`: risks, mitigants, red-team points, and falsifiers
4. `catalysts-monitoring`
   - `timeline`: catalysts, review cadence, action triggers, and open decisions
   - `market_events`: recent source-backed events that affect the memo
5. `evidence`
   - `missing_evidence`: unresolved source conflicts, stale data, unavailable model support, and open questions

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every material number, claim, event, valuation input, estimate, and model-derived value.
- Label facts, assumptions, PM judgment, management claims, model output, stale values, and unsupported claims.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not convert an ordinary standalone HTML investment committee memo into a dashboard merely because it is substantial or source-heavy.
- Do not use dashboard layout to change the memo's thesis or audience.
- Do not create `.docx` or `.xlsx` artifacts unless the user explicitly asks and the right tool/template is available.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm thesis, counterarguments, source confidence, risks, catalysts, and unresolved evidence are visible.
- Confirm citation rendering remains readable and does not fragment ticker symbols, price or EPS ranges, multiples, percentages, or dates.
- Confirm memo substance remains owned by `memo-builder`.

## PM Judgment Dashboard Slot

When this skill produces or hands off a `public_equity_investing_dashboard.v1` payload, surface the PM judgment layer inside existing supported modules rather than inventing a custom shell.

Required dashboard content where relevant:
- PM decision box: use `decision_box` for actionability, position action, or rating/target implication.
- Variant wedge and what is priced in: use `text_block`, `key_metrics`, or `table`.
- Estimate/revision bridge: use `table`, `metric_tiles`, or `financial_trend_chart` when source-backed.
- Scenario skew and downside mechanism: use `scenario_map`.
- Catalyst timeline and decision pressure: use `timeline` or `market_events`.
- Disconfirmers and action rules: use `question_list`, `table`, or `text_block`.
- Benchmark/factor/ETF exposure: use `table` or `key_metrics` when relevant and source-backed.
- Source posture and missing evidence: include `source_list` and `missing_evidence` in all production-ready dashboards.

Sector context belongs in the owning skill dashboard through hero debate, snapshot KPI, key metrics, valuation table, risk/falsifier cards, missing evidence, and source ledger. Do not create a standalone sector dashboard.
