# Company Tearsheet Dashboard Pack

Use this pack only for an explicitly selected standardized dashboard, reusable dashboard template, or structured payload-driven render for a public issuer baseline, diligence starter, pipeline card, or source-heavy profile artifact. For an ordinary standalone HTML tearsheet, follow the flexible HTML artifact standard and the owning skill's compact profile guidance instead of this fixed module map.

## Producer Role

`company-tearsheet` owns issuer identity, baseline facts, metric selection, source confidence, and downstream handoff. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `company_tearsheet`
- `layout`: `single_page` for reusable issuer profiles unless the user explicitly requests tabs
- `hero.callout`: why this issuer matters for the next workflow
- `snapshot`: ticker/security, profile type, market/financial snapshot if sourced, key KPI, latest material event, confidence label
- `sources`: primary filings/releases first, trusted providers next, and assumptions or missing fields clearly labeled
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `issuer-baseline`
   - `decision_box`: profile posture, confidence, recommended next workflow, and most important source gap
   - `metric_tiles`: ticker/security, sector, fiscal year, market snapshot, and source confidence
2. `business-snapshot`
   - `cards`: business model, segment mix, geography, customer/end-market exposure, and management claims with citations
   - `table`: segment, revenue, growth, margin, KPI, or geography rows when source-backed
3. `key-metrics`
   - `key_metrics`: source-backed operating, financial, valuation, capital-structure, and issuer-specific KPIs
4. `recent-developments`
   - `market_events`: filings, earnings, management changes, capital allocation, regulatory/legal/product events, and PM relevance
5. `risks-and-handoffs`
   - `cards`: risks, stale/conflicting data, confidence limits, and recommended downstream skill
   - `missing_evidence`: unsupported facts, stale values, missing debt/ownership/segment/KPI fields

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every factual issuer claim, metric, market-data value, leadership item, segment/geography figure, and event date.
- Label profile type and confidence for every major section.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not turn the tearsheet into a recommendation, trade pitch, full memo, or model.
- Do not compress a broader investment request into a profile when another Public Equity Investing skill should own it.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.
- Do not let a live event, extensive diligence-question list, or long register of unavailable fields turn a baseline profile into initiation coverage.
- Do not render internal evidence labels as investor-facing prose or fragment tickers, years, dates, numeric ranges, metric names, or product labels with citations.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm identity, periods, units, currency, source confidence, stale/conflicting data, and missing evidence are visible.
- Confirm the issuer baseline and core earnings drivers remain primary, missing fields are proportionate, and citation rendering remains readable.
- Confirm every next-step handoff points to the correct owning skill.

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
