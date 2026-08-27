# Event Driven Analyzer Dashboard Pack

Use this pack only for an explicitly selected standardized dashboard, reusable dashboard template, or structured payload-driven render for an event-driven situation. For an ordinary standalone HTML full event report, follow the flexible HTML artifact standard and the owning skill's event-specific guidance instead of this fixed module map.

## Producer Role

`event-driven-analyzer` owns event facts, scenario math, timing, probability judgment, market pricing, trade construction, and monitoring plan. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `event_driven_analyzer`
- `layout`: `single_page` for full event packages unless the user explicitly requests tabs
- `hero.callout`: the key event question and expected value/risk skew
- `snapshot`: event date/window, market-implied probability or spread if sourced, base case, downside case, timing, data confidence
- `sources`: filings/regulatory/court/company sources first, then market pricing, trusted news, expert/user materials, and assumptions
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `event-view`
   - `decision_box`: event stance, expected value/readiness, key risk, timing, and action posture
   - `metric_tiles`: spread/probability, timing, downside, upside, liquidity, and source confidence
2. `fact-pattern`
   - `timeline`: event chronology, upcoming milestones, regulatory/court/company deadlines
   - `market_events`: source-backed event news and market reactions
3. `scenario-tree`
   - `scenario_map`: approval/failure/delay/remedy/settlement cases, probabilities if supportable, price outcomes, and falsifiers
   - `table`: scenario math with source labels and probability-sum checks
4. `trade-monitoring`
   - `cards`: trade expression, implementation caveats, hedge/sizing considerations, and red-team risks
   - `question_list`: diligence checks and monitoring triggers
5. `gaps`
   - `missing_evidence`: missing pricing, probability support, event documents, legal/regulatory data, or terminal-only fields

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every event date, legal/regulatory fact, spread, price, probability, scenario assumption, and trade-readiness claim.
- Label facts, assumptions, model-derived fields, stale pricing, legal uncertainty, and missing documents.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not use probabilities that fail the event-math quality gate without an explicit diagnostic.
- Do not imply legal certainty or final trade readiness from incomplete event evidence.
- Do not use an executable `Buy`, `Own`, or `Initiate` headline when required live pricing or execution evidence is absent; show a `Wait`, `Monitor`, or entry-screen posture and the missing evidence.
- Do not force scenario-tree or expected-return modules from unsupported pricing, terminal-value, or probability inputs.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm fact pattern, scenario math, timing, market pricing, trade caveats, and missing evidence are visible.
- Confirm material legal/regulatory uncertainty is labeled.
- Confirm the decision posture and hero headline do not imply more actionability than the evidence supports.

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
