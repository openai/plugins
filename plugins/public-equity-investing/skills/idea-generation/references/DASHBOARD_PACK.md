# Idea Generation Dashboard Pack

Use this pack only for an explicitly selected standardized dashboard, reusable dashboard template, or structured payload-driven render for an idea screen, market map, watchlist review, or candidate funnel. For an ordinary standalone HTML idea-triage report, follow the flexible HTML artifact standard and the owning skill's idea-specific guidance instead of this fixed module map.

## Producer Role

`idea-generation` owns mandate interpretation, candidate scoring, false-positive rejection, variant-view triage, and workflow routing. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `idea_generation`
- `layout`: `single_page` for reusable idea screens unless the user explicitly requests tabs
- `hero.callout`: why the screen matters now and what decision it supports
- `snapshot`: universe size, number of actionable candidates, top long/short/watchlist candidate, rejection rate, source/data-quality status
- `sources`: user screen/portfolio/watchlist first, then market/filing/consensus/public sources with as-of labels
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `screen-summary`
   - `decision_box`: screen posture, top candidates, what is investable now, and what needs deeper work
   - `metric_tiles`: universe, candidates, rejects, data quality, style/mandate tags
2. `candidate-board`
   - `table`: candidates with ticker, beneficiary pathway where relevant, archetype, exposure proof, thesis stub, why now, expectations/valuation risk, catalyst path, first rejection, and next workflow
3. `triage`
   - `cards`: top long, short, pair, event, and watchlist ideas with variant view and first rejection risk
   - `scenario_map`: candidate paths where a few cases explain upside/downside or follow-up sequencing
4. `rejection-log`
   - `table`: rejected false positives and why they failed
5. `next-actions`
   - `question_list`: first diligence questions, source requests, and routing to model, earnings, pitch, hedge, event, or thesis-tracker workflows
   - `missing_evidence`: stale or missing data that blocks upgrade from candidate to research idea

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite any screen rule, market value, estimate, catalyst, liquidity metric, portfolio/watchlist overlap, or claimed reason a security surfaced.
- Label candidates as candidate, watchlist, deeper-research, or rejected; never as final recommendations.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not present screen output as a final trade recommendation.
- Do not invent unavailable market data, consensus, liquidity, borrow, or option-chain fields.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.
- Do not use `crowded` without verified positioning, ownership, flow, short-interest, or comparably direct support; use `expectations-heavy` or `crowding-risk candidate` when the evidence is indirect.
- Do not upgrade a name to deeper research without source-backed exposure proof; label unquantified beneficiaries `needs exposure attribution`.
- Do not render citations that fragment years, ticker symbols, numeric ranges, product names, or guidance values, or overwhelm the hero with a citation run.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm the candidate funnel, beneficiary pathways where relevant, exposure proof, expectations-risk posture, false-positive risks, next workflow routing, and missing evidence are visible.
- Confirm verified positioning is distinguished from inferred crowding risk and citations remain readable.
- Confirm the dashboard preserves user-provided screens/watchlists without overwriting them.

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
