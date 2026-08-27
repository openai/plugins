# Earnings Preview Dashboard Pack

Use this pack only for an explicitly selected standardized dashboard, reusable dashboard template, PM cockpit, tabbed dashboard, or structured payload-driven render for a pre-earnings request. For an ordinary standalone HTML full preview report, follow the flexible HTML artifact standard and the owning skill's preview-specific guidance instead of this fixed module map.

## Producer Role

`earnings-preview` owns the analysis. `dashboard-builder` owns the shared HTML shell, module rendering, and responsive QA.

## Recommended Payload

- `mode`: `earnings_preview`
- `layout`: `single_page` for full PM diligence dashboards unless the user explicitly requests tabs
- `hero.callout`: the single stock-moving debate into the print
- `snapshot`: event timing, latest price/valuation setup if sourced, top consensus/guide bar, most important KPI bar, biggest guide-cadence risk. Do not duplicate the quarter if it appears in the hero. When a growth rate, acceleration, or surprise is the stock-moving setup, make it the tile value and put the absolute amount in the detail.
- `financial_trend_chart`: include when source-backed revenue, gross profit, net income, and a comparable profitability margin history exists for the last several reported quarters. Use net margin only when it is a good recurring-profitability proxy; otherwise set `margin_metric`, `margin_label`, and `margin_rationale` for operating margin, adjusted operating margin, EBITDA margin, FCF margin, or the issuer's source-backed KPI.
- `eps_actual_vs_estimate_chart`: include when the past five quarters have estimated EPS and actual EPS on the same GAAP/adjusted/clean basis.
- `equity_price_event_chart`: include only when sourced equity-price history is substantive enough to visualize: daily tapes need at least 10 distinct points over at least 7 calendar days, hourly tapes need at least 24 time-stamped points over at least 6 hours, and minute/intraday tapes need at least 60 time-stamped points over at least 45 minutes. If only a few closes or article-reported prices are available, omit the chart and use `market_events` plus `missing_evidence`.
- `market_events`: source-backed major news, market events, regulatory/macro items, peer read-throughs, and upcoming catalysts from the last quarter, last twelve months, and forward-looking window when relevant to the print.
- `sources`: company IR/filings first, consensus/market sources second, web fallback clearly labeled

## Tabs And Modules

1. `overview`
   - `decision_box`: stance into the print, bar location, top stock-moving cruxes, one thing that changes conviction
   - `cards`: top debates or key diligence questions
2. `expectation-bar`
   - `table`: consensus, guide, whisper if sourced, source timestamp, confidence, and PM read
   - `missing_evidence`: terminal-only consensus, options, or whisper fields
3. `kpi-board`
   - `financial_trend_chart`: revenue, gross profit, net income, and the selected profitability margin by quarter when complete comparable data exists. Prefer operating margin or another explicitly labeled metric when historical net margin is distorted by non-operating, tax, equity-investment, FX, restructuring, litigation, impairment, asset-sale, or other one-time items.
   - `eps_actual_vs_estimate_chart`: estimated EPS versus actual EPS for the past five quarters when estimate history exists
   - `key_metrics`: quarterly key-metric baseline, consensus/guide bar, required growth/acceleration, and PM read using the issuer's business model
   - `growth_trajectory`: acceleration/deceleration map for the metrics most likely to drive the print
   - `bar_chart`: compact chart for KPI bars, revenue mix, segment growth, or guide delta when the visual helps a PM scan faster
4. `guidance`
   - `cards`: guide bridge, cadence, credibility, and key model pressure points
5. `macro-reads`
   - `cards` or `table`: peer, macro, sector, channel, and alternative-data read-throughs with confidence
6. `market-events`
   - `equity_price_event_chart`: recent equity-price history annotated with material company/sector/macro/regulatory events only when the price tape passes the daily/hourly/minute minimums above
   - `market_events`: recent company/sector/macro/regulatory news and upcoming events with date/window, source, potential impact, PM read, and confidence
   - `missing_evidence`: any terminal-only news, channel-check, options, regulatory, or peer-event fields still needed
7. `scenarios`
   - `scenario_map`: bull/base/bear drivers, ranges where sourced, and falsifiers
8. `call-prep`
   - `question_list`: must-answer questions, why each matters, listen-fors, validates/breaks thesis
9. `refresh-gaps`
   - `missing_evidence`: exact data refresh list before trading the print

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every material number, estimate, guide/consensus field, event date, market move, KPI, and assumption inline where it appears.
- Use `metadata.citation_policy: "strict"` for production dashboards.
- Keep the top-level source ledger mandatory; label missing consensus, options, whisper, peer, and market data in `missing_evidence`.
- Keep raw JSON, Markdown notes, CSV exports, and run logs as support/audit material unless the user explicitly asks for them.

## Do Not

- Do not let the dashboard replace the full pre-print analytical structure.
- Do not hide missing options-implied move, consensus timestamp, or whisper support.
- Do not imply a trade-ready pre-print position from company guidance and public operating evidence alone when implied move, relevant market context, or required expectation evidence is missing.
- Do not label a multi-day or broad-expiry options measure as an earnings implied move when it contains substantial pre-event trading time or another material catalyst window; label it `expiry-tenor volatility context` and make the limitation prominent.
- Do not chart net margin as the default line when the historical EPS-quality screen shows a material distortion. Pick the margin that best frames recurring operating performance into the print and state the rationale.
- Do not treat news coverage as a generic clipping service. Only include events that can plausibly affect estimates, guide credibility, multiple, risk, positioning, or call questions.
- Do not include uncited market events. Use primary sources where possible, then reputable news/market-data fallback with explicit `as_of`.
- Do not populate chart shells with blanks. If financial trend, selected margin, EPS estimate/actual, or price/event series are missing or not comparable, omit the chart and add a precise `missing_evidence` item.
- Do not waste space. Pre-print dashboards should be dense, with compact tables/charts and short PM reads rather than loose narrative sections.
- Do not use generic KPI rows when sector or business-model metrics are available. Use `sector-context-overlay` to pick the right KPIs when needed.
- Do not use a company logo as a hard dependency; prefer ticker identity tile.
- Do not render a chart whose unit or scale conflicts with adjacent headings or tables.
- Do not render citation links that fragment readable dates, times, ticker symbols, product names, or product specifications.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm the expectation bar, KPI dashboard, market events, scenarios, call-prep questions, source ledger, and missing evidence are visible.
- Confirm no chart shell renders without complete, comparable source-backed data.
- Confirm chart units match neighboring labels and tables, citations remain readable, and the recommendation language matches the evidence available before the print.
- Confirm any hero-tile implied move reasonably isolates earnings; otherwise use the `expiry-tenor volatility context` label or move it out of the first-read tiles.

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
