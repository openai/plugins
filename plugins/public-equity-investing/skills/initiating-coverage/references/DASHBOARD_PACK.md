# Initiating Coverage Dashboard Pack

Use this pack only when the user explicitly requests a standardized dashboard, reusable validated template, or structured payload-driven render for an initiation, buy-side deep dive, coverage launch, or sector initiation. An ordinary substantial initiation is a polished standalone HTML initiation report following `../../../shared/html-artifact-standard.md`.

## Producer Role

`initiating-coverage` owns the report architecture, thesis, evidence hierarchy, model/valuation framing, and research judgment. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `initiating_coverage`
- `layout`: `single_page` for full initiation packages unless the user explicitly requests tabs
- `hero.callout`: the variant view or investment debate that makes the report worth reading
- `snapshot`: rating/research posture if applicable, target/valuation range if supportable, upside/downside skew, key catalyst, key risk, data cut-off
- `sources`: filings, company materials, model outputs, consensus/market data, expert/user materials, and assumptions clearly separated
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `view`
   - `executive_summary`: thesis-led initiation summary with what is proven, assumed, and still unresolved
   - `decision_box`: recommendation or research posture, valuation stance, thesis change triggers, and next catalyst
2. `thesis`
   - `cards`: 3-5 evidence-linked thesis pillars, variant perception, and falsifiers
   - `scenario_map`: bull/base/bear cases with drivers, valuation implications, and breakpoints
3. `company-industry`
   - `key_metrics`: issuer-specific KPIs and operating drivers
   - `table`: company/industry positioning, segment economics, market share, or end-market exposure
4. `model-valuation`
   - `table`: forecast drivers, valuation methods, multiple/DCF support, sensitivity outputs, and basis labels
   - `bar_chart`: valuation bridge or sensitivity only when the sourced data is complete
5. `catalysts-risks`
   - `timeline`: catalyst path, earnings, investor day, regulatory, product, or macro events
   - `cards`: key risks, disconfirming evidence, and monitoring triggers
6. `evidence`
   - `missing_evidence`: unresolved conflicts, stale data, model gaps, and open source requests

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every metric, valuation input, target/range, estimate, market-size claim, and catalyst date.
- Label facts, company claims, estimates, model-derived values, PM judgment, assumptions, and missing evidence.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not let dashboard modules invent report logic that is absent from the initiation.
- Do not convert an ordinary initiation report into an action-rules dashboard simply because the research is source-heavy or intended for PM review.
- Do not present unsupported rating or price-target language as decision-ready.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm the dashboard contains a real thesis, valuation method, catalysts, risks, source confidence, and open evidence requests.
- Confirm model/workbook outputs are clearly labeled when they are support artifacts rather than native dashboard calculations.
- Confirm citation rendering remains readable and does not fragment tickers, fiscal periods, dates, prices, ranges, multiples, or metric names.

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
