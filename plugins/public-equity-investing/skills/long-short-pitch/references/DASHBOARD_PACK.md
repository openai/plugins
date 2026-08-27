# Long Short Pitch Dashboard Pack

Use this pack only when the user explicitly requests a standardized dashboard, reusable dashboard template, PM cockpit, or structured payload-driven render for a long, short, pair, catalyst, or PM-facing trade pitch. Ordinary substantive or explicitly requested HTML pitches should use the flexible standalone HTML trade-pitch report in `../SKILL.md` instead.

## Producer Role

`long-short-pitch` owns trade construction, variant perception, expression, risk/reward, sizing considerations, and add/trim/exit/cover rules. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `long_short_pitch`
- `layout`: `single_page` for full PM pitch packages unless the user explicitly requests tabs
- `hero.callout`: the variant perception and what the market is missing
- `snapshot`: direction, instrument, expected return/skew if supportable, next catalyst, stop/falsifier, hedge/sizing caveat
- `sources`: user thesis/materials first, then filings, market/consensus data, news/events, model outputs, and assumptions
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `pitch`
   - `decision_box`: action posture, thesis, trade expression, catalyst path, risk/reward, and thesis-break trigger
   - `executive_summary`: concise PM read with what is variant and what is already priced in
   - For shorts, put the implementation gate near the decision box: catalyst, valuation anchor, borrow/carry, options feasibility when relevant, squeeze/buyback risk, and cover rule.
2. `thesis`
   - `cards`: thesis pillars, evidence, variant perception, and disconfirmers
   - `table`: KPI/valuation/setup evidence where a table improves diligence speed
3. `scenarios`
   - `scenario_map`: bull/base/bear or long/short/pair cases with drivers, probabilities where supportable, and payoff/skew; label assumption-driven incomplete-underwriting work as `Illustrative Scenario Skew`
4. `catalysts-risk`
   - `timeline`: catalysts, add/trim/exit/cover triggers, and review dates
   - `market_events`: source-backed company/sector/macro/regulatory events that affect the pitch
5. `monitoring`
   - `question_list`: must-answer diligence questions and checks
   - `missing_evidence`: stale market data, unavailable consensus, missing borrow/options/liquidity, and model gaps

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every price, valuation, estimate, catalyst, market event, scenario assumption, and risk/reward figure.
- Label assumptions, model-derived values, user-provided views, stale market data, and unsupported claims.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not turn a narrow conversational pitch into files unless the user asks or the work is substantial/reusable.
- Do not hide sizing, hedge, borrow, liquidity, or catalyst caveats when they affect implementation readiness.
- Do not label issuer purchase, cloud-spend, capacity, or infrastructure commitments as revenue or demand evidence without supporting disclosure of incremental economics.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.
- Do not expose internal evidence-label strings, fragment dates or fiscal years with citation links, render empty scenario fields, or repeat the same recommendation across dashboard panels.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm variant perception, trade expression, scenario skew, catalysts, disconfirmers, and monitoring rules are visible.
- Confirm output sounds like PM judgment rather than a generic template.
- Confirm shorts surface implementation gates near the recommendation and assumption-driven scenarios are identified as illustrative rather than actionable.

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
