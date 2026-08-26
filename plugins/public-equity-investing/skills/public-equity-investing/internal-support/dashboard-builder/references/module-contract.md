# Dashboard Module Contract

Use this when mapping a Public Equity Investing skill output into a dashboard payload.

## Payload Shape

```json
{
  "kind": "public_equity_investing_dashboard.v1",
  "mode": "earnings_preview",
  "layout": "single_page",
  "title": "Issuer: dashboard title",
  "subtitle": "Optional supporting copy",
  "issuer": {
    "ticker": "HD",
    "name": "The Home Depot",
    "exchange": "NYSE",
    "sector": "Retail",
    "accent_color": "#f26a21",
    "brand_dark_color": "#9a3412",
    "brand_colors": ["#f26a21", "#9a3412"]
  },
  "metadata": {
    "payload_stage": "production",
    "freeze_time": "2026-05-15 09:00 ET",
    "source_posture": "Company IR first, then public fallback",
    "readiness_label": "PM-ready",
    "readiness_posture": "pm_ready",
    "citation_policy": "strict",
    "decision_context": "The core debate shown in the hero"
  },
  "hero": {
    "eyebrow": "Pre-earnings dashboard",
    "headline": "The Home Depot: Q1 FY2026 pre-print",
    "dek": "Short PM-facing setup sentence.",
    "callout_label": "Core Debate",
    "callout": "The most important question."
  },
  "snapshot": [
    {"label": "Event", "value": "May 19, 2026", "detail": "Q1 call at 9:00 a.m. ET", "status": "good"}
  ],
  "tabs": [
    {"id": "overview", "label": "Overview", "modules": []}
  ],
  "sources": [
    {"id": "S1", "title": "Issuer Q1 2026 10-Q", "url": "https://example.com/10q", "as_of": "2026-05-15", "type": "SEC filing", "excerpt": "Relevant supporting excerpt."}
  ],
  "model_citations_path": "model_citations.json",
  "qa": {"warnings": [], "hard_failures": []}
}
```

## Inline Citation Contract

Public Equity Investing dashboards are source-visible at the point of use. The source ledger is required, but it is not enough by itself.

- Give every source a stable top-level `sources[].id` such as `S1`, `S2`, `Filing-Q1`, or `Transcript-Q1`.
- Cite every material number, estimate, quote, date-sensitive claim, and assumption inline where it appears.
- Supported citation forms:
  - string markers: `"Q1 revenue was $8.1M [S1]"`
  - field citations: `{"value": "$8.1M", "citations": ["S1"]}`
  - row/module citations: `{"metric": "Revenue", "current": "$8.1M", "citations": ["S1"]}`
  - source ID aliases: `source_id: "S1"` or `source_ids: ["S1", "S2"]`
  - external-only fallback: `{"value": "June CPI", "source_url": "https://...", "source_title": "BLS CPI schedule", "as_of": "2026 schedule"}`
- Citation chips click through to the source ledger for known source IDs. External-only fallback chips open the source URL in a new window.
- Numeric values should usually render as the citation target themselves: the number keeps normal text color, gets a subtle underline/background affordance, links to the source ledger or source URL, and exposes the same hover/focus preview.
- Citation chips are still allowed for non-numeric claims, but keep them visually quiet and small. If a whole section or card uses the same source set, prefer a compact source note at the bottom of that section/card instead of repeating identical chips after every sentence.
- Citation chips and numeric citation links expose a hover/focus preview using source title, type/status, date/as-of, and excerpt/pinpoint/note when available.
- Workbook-backed dashboards may include `model_citations` or `model_citations_path` from model builders. Each record should have `id`, `workbook_path`, `sheet`, `cell` or `range`, optional `value`, optional `formula`, `line_item`, `source_id`, and `evidence_label`. Modules should cite the model-output record ID, for example `{"value": "$48.25", "citations": ["model-output:dcf-value-per-share"]}`. The renderer treats these records as source ledger entries and shows workbook/sheet/cell details in chips and popovers.
- Production payloads must set `metadata.payload_stage: "production"` and `metadata.citation_policy: "strict"` so validation hard-fails missing source ledgers, unresolved citation IDs, and numeric material without citation support.
- Production metadata must include `freeze_time`, `source_posture`, `readiness_label`, `readiness_posture`, and `decision_context`. Use production readiness postures such as `pm_ready`, `client_ready`, `committee_ready`, `senior_review_ready`, `external`, or `publication_ready` only when those gates are actually satisfied.
- Draft/support payloads may set `metadata.payload_stage: "draft"` or `"support"` and `metadata.citation_policy: "warn"`, but the rendered artifact must visibly retain gaps and cannot be described as PM-ready, client-ready, committee-ready, or publication-ready.
- Use `missing_evidence` for unsupported values. Do not create an uncited number and then bury the source gap at the bottom.

## Supported Modules

## Layout Modes

- `tabs` is the backward-compatible layout. It renders tab buttons and one visible panel at a time.
- `single_page` renders every tab as an anchored section and adds a sticky table of contents. Use this for PM diligence dashboards when the user wants to scan the full work product and jump between sections.
- Public Equity Investing dashboards should default to analyst-dense spacing. Use white space for hierarchy and scanning, not as decoration.
- Issuer identity tiles must work with 1-4 character tickers and should remain readable without crowding the box. Do not use a logo as a dependency. When available, provide brand colors in `issuer.accent_color`, `issuer.brand_color`, `issuer.brand_dark_color`, `issuer.identity_color`, or `issuer.brand_colors`; the ticker badge should use a darker brand shade so white ticker text remains legible.

## Snapshot / Highlight Rules

- Put quarter/period in the hero headline, dek, or metadata. Do not duplicate it as a highlight tile unless the user explicitly asks for a period tile.
- Highlight tiles should answer "what should the PM remember first?" Prefer surprise percentages, growth acceleration/deceleration, normalized EPS, guide deltas, margin inflections, backlog, unit growth, capex guide, or the company-specific KPI that changed the debate. When the investor signal is a rate or surprise, make that the primary value and put the absolute dollar value in supporting detail.
- For EPS, label GAAP, adjusted, operating, or clean/recurring basis. If GAAP is distorted, show the quality-adjusted read in the summary and beat/miss table rather than heroing the distorted headline alone.
- For capex, use the annual guide/range when that is the investor issue; use quarterly capex only when quarterly cash burn is the issue.

## Chart Rules

- Use charts when they shorten diligence time: segment growth, revenue mix, guide delta, margin trend, exposure concentration, or catalyst probability.
- Pair charts with the underlying table when precision matters. The chart should help scanning; the table should preserve exact values.
- Do not chart every module. If a table is already small and self-explanatory, keep it as a table.

### `decision_box`

Use for the PM bottom line.

Data keys:

- `label`
- `stance`
- `summary`
- `thesis_change`
- `estimate_revision`
- `stock_skew`
- `next_catalyst`
- `key_points`

### `metric_tiles`

Use for event, price, guide, valuation, spread, probability, liquidity, catalyst, or data-quality tiles.

Data keys:

- `items`: array of `{label, value, detail, status}`
- Each item may also include `citations`, `source_id`, `source_ids`, `source_url`, `source_title`, `excerpt`, or bracketed source markers in `value` / `detail`.

### `highlight_tiles`

Alias of `metric_tiles` for the top PM highlights when a producer wants to distinguish investment highlights from routine KPI tiles.

Data keys:

- `items`: array of `{label, value, detail, status}`

### `executive_summary`

Use for a dense PM-style paragraph that synthesizes the print, quality of beat, guidance, new disclosures, call-only datapoints, contradictions, and watch items.

Data keys:

- `headline`
- `body`
- `bullets`
- `net_read`

### `key_metrics`

Use for quarterly key metrics. This should be company-specific, not just generic financials. Include absolute values and growth/trajectory where relevant.

Data keys:

- `rows`: array of `{metric, current, growth, compare, trajectory, read}` by default
- `columns`: optional custom column list
- `density`: optional; use `dense` for PM tables
- Cite each row or cell with `citations`, `source_id/source_ids`, or inline source markers.

### `growth_trajectory`

Use for acceleration/deceleration across the metrics that actually drive the name.

Data keys:

- `rows`: array of `{metric, prior, current, trajectory, read}` by default
- `columns`: optional custom column list

### `cards`

Use for debates, drivers, risks, read-throughs, thesis pillars, evidence deltas, or source notes.

Data keys:

- `items`: array of `{eyebrow, title, body, status, bullets}`

### `table`

Use for KPI boards, expectation bars, beat/miss, guide bridges, EPS-quality screens, model updates, risks, or source posture.

Data keys:

- `columns`: array of strings or `{key, label}`
- `rows`: array of objects keyed to columns
- `mobile_label`: optional table description
- Cite cells with mapping values (`{"value": "$8.1M", "citations": ["S1"]}`), bracketed markers, or row-level `citations`.

### `scenario_map`

Use for bull/base/bear, probability trees, payoff trees, downside/recovery, or valuation cases.

Data keys:

- `cases`: array of `{type, title, headline, bullets}`

### `question_list`

Use for call prep, management-meeting prep, diligence requests, or monitoring questions.

Data keys:

- `questions`: array of `{question, why, listen_for}`

### `transcript_qa`

Use for post-earnings transcript and Q&A maps. Prefer this over `question_list` when a transcript exists and the user needs analyst, topic, management response, direct quote, and answer quality in one dense table.

Data keys:

- `rows`: array of `{number, analyst, topic, response, quote, quality}` by default
- `columns`: optional custom column list

Quote rule: keep direct quotes short, source-tagged, and only when transcript access supports them. If quotes are unavailable, state `transcript not provided` or use paraphrase with precise source posture.

### `read_throughs`

Use for in-depth cross-company and industry read-throughs.

Data keys:

- `rows`: array of `{name, relationship, parent_said, read_through, implication, confidence}` by default
- `columns`: optional custom column list

### `market_events`

Use for major news coverage, market events, regulatory items, macro shocks, product launches, management changes, litigation, capital allocation, upcoming catalysts, and other external context that can change the investor decision.

This module is presentation-only. The producer skill decides which events are material, over what lookback window, and what the impact is. Prefer a three-window scan: last quarter, last twelve months, and forward-looking anticipated events. Every event needs a cited source or an explicit missing-evidence label.

Data keys:

- `events`: array of `{date, event, type, impact, investor_read, source_title, source_url, as_of, citations}` by default
- `rows`: accepted as an alias for `events`
- `mobile_label`: optional table description

Event selection rules:

- Include only events that plausibly affect estimates, multiple, risk, positioning, industry read-through, or catalyst path.
- Separate company-specific events from sector, macro, regulatory, legal, geopolitical, rate/FX, commodity, and peer events.
- Include upcoming events when they are dated or have a well-labeled window. Do not invent exact dates.
- Cite the source for the event and label source posture, especially for public web fallback, analyst inference, or terminal-only gaps.
- Put the citation on the event row, not only in the source column, so the date/window, event, impact, and investor read each carry a visible chip.

### `bar_chart`

Use for compact native charting without external JavaScript. Good for small sets of comparable metrics.

Data keys:

- `items`: array of `{label, value, bar_value, display, detail}`
- `bar_value`: numeric value used for bar scaling
- `display`: optional value shown at the right of the bar
- `detail`: optional subtitle under the label

### `financial_trend_chart`

Use for earnings-preview and earnings-deep-dive dashboards when source-backed quarterly financial history is available. It renders grouped bars for revenue, gross profit, and net income by quarter, with a selected profitability-margin line overlay. Omit the module when any required metric is missing, stale, non-comparable, not parseable, or on an inconsistent basis. Strict QA requires at least two chart-ready rows after renderer field requirements are applied.

Data keys:

- `periods`: array of `{period, revenue, gross_profit, net_income, net_margin, operating_margin, adjusted_operating_margin, ebitda_margin, fcf_margin, source, as_of}`. Only the selected margin field is required, but include net margin too when source-backed and useful for the table or EPS-quality narrative.
- `revenue`, `gross_profit`, and `net_income` must be numeric and use the same units/scale.
- `margin_metric`: optional line metric key. Default is `net_margin`. Set to `operating_margin`, `adjusted_operating_margin`, `ebitda_margin`, `fcf_margin`, or another explicit row key when that better reflects recurring profitability.
- `margin_label`: optional display label such as `Operating Margin` or `Adjusted Operating Margin`.
- `margin_rationale`: optional note explaining why this line metric was selected, especially when net margin is distorted by below-the-line gains/losses, tax, FX, equity-investment marks, restructuring, impairments, litigation, asset sales, or other non-recurring items.
- The selected margin may be a decimal ratio such as `0.245` or a percent string such as `24.5%`.
- `mobile_label`: optional table description.

Producer selection rule:

- Default to net margin only when it is a fair recurring-profitability proxy.
- Prefer operating margin when net income is distorted but operating income remains comparable.
- Prefer adjusted operating margin, EBITDA margin, contribution margin, or FCF margin when those are the issuer's actual investor KPI and the basis is clearly sourced.
- If the margin choice is ambiguous, use the line that best answers the investor question and state the rationale in `margin_rationale`; do not silently chart a distorted margin.

Renderer scale behavior:

- Positive-only bar and EPS scales start at zero and use readable gridlines/ticks rather than padded negative lower bounds.
- The right-axis line scale should be labeled with multiple percentage ticks, not only top/bottom endpoints.

### `eps_actual_vs_estimate_chart`

Use for earnings dashboards when estimated EPS and actual EPS are available for the past five quarters on the same basis. If fewer quarters are available, use the chart only when the module title or note states the actual window. Omit the module when estimate timestamps, EPS basis, actual EPS, or parseable values are missing. Strict QA requires at least two chart-ready rows after renderer field requirements are applied.

Data keys:

- `periods`: array of `{period, estimated_eps, actual_eps, surprise, basis, source, as_of}`.
- `estimated_eps` and `actual_eps` must be numeric and on a consistent GAAP, adjusted, operating, or clean EPS basis.
- `surprise` is optional; when omitted, the renderer displays `actual_eps - estimated_eps`.
- `mobile_label`: optional table description.

### `equity_price_event_chart`

Use only when sourced equity-price history can be paired with material events that plausibly affected the equity and the price tape is substantive enough to visualize. This module renders a price line with numbered event markers and the event table directly underneath. Prefer this over a generic news list when the user needs to see how events map to price action, but omit it when the available market data is only a few closes, article-reported price points, or a sparse quote-card sample. Strict QA fails thin price tapes rather than letting them render.

Minimum price-tape gates:

- Daily price data: at least 10 distinct chart-ready price rows spanning at least 7 calendar days.
- Hourly price data: at least 24 distinct time-stamped chart-ready price rows spanning at least 6 hours.
- Minute or intraday price data: at least 60 distinct time-stamped chart-ready price rows spanning at least 45 minutes.

Data keys:

- `prices`: array of `{date, price}` or `{timestamp, price}` rows, with direct citations/source IDs on rows or a module-level price source.
- `price_granularity`, `price_frequency`, or `price_interval`: optional but recommended; accepted families are `daily`, `hourly`, and `minute`/`intraday`. When omitted, QA infers the cadence from timestamps and still applies the relevant minimums.
- `events`: array of `{date, event, type, impact, investor_read, source_title, source_url, as_of}`.
- `date` should match a price point where possible; otherwise markers are distributed across the visible price window.
- Include only sourced company, sector, macro, regulatory, product, management, legal, peer, or forward-catalyst events that affected estimates, multiple, risk, positioning, or catalyst path.

### `timeline`

Use for catalysts, post-print next checks, regulatory paths, event windows, or thesis-monitoring cadence.

Data keys:

- `events`: array of `{date, title, detail}`

### `text_block`

Use for compact explanatory copy where a table or cards would be overkill.

Data keys:

- `body`
- `bullets`

### `missing_evidence`

Use for terminal-only fields, unavailable transcript, stale estimates, missing options chain, no source timestamp, or model inputs still needed.

Data keys:

- `items`: array of strings or `{item, needed}`

### `source_list`

Usually added from top-level `sources`; use directly only when a tab needs a separate source ledger.

Data keys:

- `sources`: array of `{id, title, url, as_of, note, type, status, excerpt, pinpoint}`

## Producer Guidance

- Start with the primary skill's output contract; do not invent dashboard-only numbers.
- Map existing sections into modules rather than changing the analysis structure to fit a visual.
- Keep unavailable but important modules visible with precise absence labels.
- Do not create empty chart shells. If the financial trend, EPS actual/estimate, or equity event data is incomplete, omit the chart module and disclose the missing series in `missing_evidence`; strict QA fails chart modules that would be filtered to empty by the renderer.
- Put source limitations in both the relevant module and `missing_evidence`.
- Hero `dek` and `callout` honor `hero.citations`; use those citations for source-backed masthead claims and numeric callouts.
