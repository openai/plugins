# Earnings Deep Dive Dashboard Pack

Use this only when a post-earnings request explicitly selects a standardized dashboard, reusable dashboard template, PM cockpit, tabbed dashboard, or structured payload-driven render. For an ordinary standalone HTML deep dive or full report, use the flexible HTML standard instead of this fixed module map.

## Producer Role

`earnings-deep-dive` owns the post-print analysis. `dashboard-builder` owns the shared HTML shell, module rendering, and responsive QA.

## Recommended Payload

- `mode`: `earnings_deep_dive`
- `layout`: `single_page` for full PM diligence dashboards unless the user explicitly requests tabs
- `hero.callout`: whether the quarter changed the investment case
- `snapshot`: 4-8 PM-selective highlights such as revenue surprise %, clean EPS beat, segment growth surprise, guide change, backlog, margin inflection, capex guide, stock/valuation skew, or next catalyst. Do not use a `Quarter` tile when the quarter is in the hero. When a growth rate or surprise is the investor signal, make it the tile value and put the absolute amount in the detail.
- `financial_trend_chart`: include when the last several reported quarters have source-backed revenue, gross profit, net income, and a comparable profitability margin. Use net margin only when it is a good recurring-profitability proxy; otherwise set `margin_metric`, `margin_label`, and `margin_rationale` for operating margin, adjusted operating margin, EBITDA margin, FCF margin, or the issuer's source-backed KPI.
- `eps_actual_vs_estimate_chart`: include when the past five quarters have estimated EPS and actual EPS on the same GAAP/adjusted/clean basis. Use fewer quarters only when the module title states the available window.
- `equity_price_event_chart`: include only when equity-price history is source-backed and substantive: daily tapes need at least 10 distinct points over at least 7 calendar days, hourly tapes need at least 24 time-stamped points over at least 6 hours, and minute/intraday tapes need at least 60 time-stamped points over at least 45 minutes. If the available post-print tape is only a few closes or article-reported prices, omit the chart and use `market_events` plus `missing_evidence`.
- `market_events`: source-backed recent news, market events, regulatory/macro items, peer moves, management interviews, and upcoming catalysts that changed or could change the post-print read.
- `sources`: release/filing first, deck/prepared remarks next, transcript for narrative, consensus/market data with `as_of`

## Tabs And Modules

1. `verdict`
   - `executive_summary`: dense PM paragraph with clean print, quality of beat, guide, call-only datapoints, contradictions, watch items, and net read
   - `decision_box`: PM bottom line, thesis change, estimate revision, stock skew, next catalyst
   - `cards`: what changed, what matters, and what remains unresolved
2. `beat-miss`
   - `table`: granular reported vs consensus/internal estimates, actual, variance, surprise %, source, basis, and PM read. Include segment/margin/constant-currency metrics where relevant, not only revenue and EPS.
3. `eps-quality`
   - `table`: GAAP/adjusted/operating/recurring EPS screen, below-the-line items, tax/share-count/one-time items, and clean EPS beat/miss where derivable
4. `quarterly-metrics`
   - `financial_trend_chart`: revenue, gross profit, net income, and the selected profitability margin by quarter when complete comparable data exists. Use operating margin or another explicitly labeled metric when net margin is distorted by below-the-line gains/losses, tax, FX, equity-investment marks, restructuring, impairments, litigation, asset sales, or other one-time items.
   - `eps_actual_vs_estimate_chart`: estimated EPS versus actual EPS for the past five quarters when source-backed estimate history exists
   - `key_metrics`: company-specific quarterly key metrics with absolute values, growth, consensus/guide where available, trajectory, and PM read
   - `growth_trajectory`: acceleration/deceleration across the issuer's load-bearing metrics
   - `bar_chart`: compact chart for segment growth, revenue mix, margin trajectory, or another small comparable metric set when the visual speeds interpretation
5. `guidance`
   - `table`: deep guidance bridge with prior view, new frame, vs prior, consensus if sourced, read, and source. Include qualitative guidance when the company does not provide revenue/EPS guide.
   - `cards`: guide credibility, cadence, and contradictions
6. `drivers`
   - `cards`: 2-3 load-bearing drivers and segment/KPI read-throughs
7. `transcript-map` (only when transcript evidence is available)
   - `transcript_qa`: analyst, firm, topic, management response, short direct quote where available, quality of response, and PM implication
   - `cards`: high-signal call points, contradictions, and quote context within citation limits
8. `read-throughs` (only when substantive read-through evidence is available)
   - `read_throughs`: names, relationship to issuer, what management said, read-through, implication, and confidence
9. `market-events` (only when substantive cited events are available)
   - `equity_price_event_chart`: equity-price history annotated with material events only when the price tape passes the daily/hourly/minute minimums above
   - `market_events`: last-quarter, last-twelve-month, and forward-looking company/sector/macro/regulatory events with source, impact, investor read, and confidence
   - `cards`: contradictions between the event tape and management's post-print narrative when relevant
10. `model-impact`
   - `table`: revenue, margin, EPS, FCF, valuation, and thesis impact
11. `watch-list`
   - `timeline`: next catalysts and falsifier cadence
   - `missing_evidence`: source gaps and model inputs still needed

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every material number, reported metric, estimate, guide field, quote, event date, market move, KPI, and assumption inline where it appears.
- Use `metadata.citation_policy: "strict"` for production dashboards.
- Keep the top-level source ledger mandatory; label missing transcript, consensus, price, peer, model, and market data in `missing_evidence`.
- Keep raw JSON, Markdown notes, CSV exports, and run logs as support/audit material unless the user explicitly asks for them.

## Do Not

- Do not use transcript claims as primary numeric evidence when release/filing tables are available.
- Do not hide EPS-quality issues behind a headline beat/miss.
- Do not chart net margin as the default line when the EPS-quality screen shows a material distortion. Pick the margin that best reflects recurring operating performance and state the rationale.
- Do not populate highlights mechanically from reported absolute values when a surprise %, growth rate, guide change, margin inflection, or normalized number better captures what matters.
- Do not summarize recent news mechanically. Include only events that affect the quarter interpretation, guidance credibility, estimate revision, multiple, risk, read-throughs, or next-catalyst path.
- Do not include uncited event claims. Prefer filings/releases/transcripts for company events; use reputable news/market sources for external events and label source posture.
- Do not populate chart shells with blanks. If revenue/gross profit/net income/selected margin, EPS estimate/actual history, or price/event data is missing, omit the relevant chart and add a precise `missing_evidence` item.
- Do not render empty scenario cards, transcript tables, event tables, or other blank modules. Use a concise `missing_evidence` item when the absence matters.
- Do not display `Not sourced` for a market event whose citation resolves to the source ledger; carry its cited source through to the visible event row.
- Do not waste dashboard space. Favor dense tables, compact chart/table pairings, and short PM reads over airy narrative blocks.
- Do not overfit KPI modules to one company. Use sector and business-model context to select the issuer's own drivers.
- Do not invent transcript questions, speakers, firms, or quotes.
- Do not use a company logo as a hard dependency; prefer ticker identity tile.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm the verdict, beat/miss, EPS quality, guide bridge, source ledger, and missing evidence are visible; confirm transcript maps, read-throughs, and market events only when populated and source-supported.
- Confirm no chart shell renders without complete, comparable source-backed data.
- Confirm no blank scenario card or empty optional module renders and cited market events display their source.

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
