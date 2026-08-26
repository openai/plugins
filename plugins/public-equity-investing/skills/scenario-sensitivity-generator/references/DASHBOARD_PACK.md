# Scenario Sensitivity Dashboard Pack

Use this pack only when the user explicitly requests a standardized dashboard, reusable dashboard template, PM cockpit, or structured payload-driven render for a public-equity scenario pack, valuation sensitivity, earnings revision case, event probability tree, macro-factor read-through, liquidity downside case, or thesis trigger table. An ordinary substantial scenario sensitivity package or sourced event scenario overlay should be a polished standalone HTML scenario report following `../../../shared/html-artifact-standard.md`.

## Producer Role

`scenario-sensitivity-generator` owns the scenario math, base-case source, current-price anchoring, driver deltas, expected-return/skew interpretation, action thresholds, source posture, model-readiness caveats, and missing evidence. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `scenario_sensitivity`
- `layout`: `single_page` for PM decision packs unless the user explicitly requests tabs
- `hero.callout`: the decision hinge, such as "Does the upside clear the hurdle after downside and evidence quality?"
- `snapshot`: current price, base case, probability-weighted value, expected return versus hurdle, downside/upside ratio, break-even probability, skew label, and recommended PM action
- `sources`: model output, consensus/export, company filing, market-data snapshot, event/source document, or explicitly labeled user assumption
- Source posture and Missing evidence must be visible in the dashboard, not buried in the support files.
- On this explicitly selected dashboard path, the HTML dashboard/report is the human deliverable. JSON, Markdown, CSV, run logs, and manifests are support artifacts unless explicitly requested.

## Tabs And Modules

1. `pm-decision`
   - `decision_box`: action posture, underwriteable versus optical upside, what is priced in, what changes the action, and top missing evidence
   - `metric_tiles`: expected return versus hurdle, downside/upside ratio, break-even probability, skew label, current price, and source/readiness posture
2. `scenario-map`
   - `scenario_map`: bull/base/bear or custom cases with price/value output, probability, return, evidence quality, and falsifiers
   - `table`: probability-weighted value, scenario values, implied returns, and action rules
3. `sensitivity-drivers`
   - `table`: valuation, EPS/revision, KPI, macro-factor, event, or liquidity-driver sensitivities with source labels and as-of dates
   - `bar_chart`: compact expected-return, value, or driver-impact chart only when complete source-backed rows exist
4. `thresholds`
   - `question_list` or `table`: add, press, hold, trim, exit, hedge, wait-for-proof, and re-underwrite thresholds tied to model lines, source IDs, and dates
   - `timeline`: data releases, earnings, event dates, or review checkpoints that change the scenario tree
5. `evidence-and-qa`
   - `source_list`: source ledger, model/source posture, and freshness labels
   - `missing_evidence`: missing current price, stale consensus, unsupported probabilities, weak source basis, absent model tie-out, or unavailable market data

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- For discrete-event dashboards, use primary transaction documents and the freshest accessible market-data source for load-bearing offer terms, timing mechanics, and current-price inputs before relying on press reporting or older price observations.
- Cite every current price, target/value output, probability, hurdle return, multiple, EPS/EBITDA/FCF assumption, KPI driver, factor sensitivity, liquidity input, and event date.
- Label whether each value is model-validated, source-derived, user-provided, consensus-derived, market-data-derived, or illustrative.
- Probability-weighted cases must disclose probability source, probability sum, and whether the output is valid. If probabilities are incomplete or do not sum to 100%, show the issue in `missing_evidence` and do not present the probability-weighted value as decision-ready.
- When probabilities are illustrative rather than independently underwritten, lead with implied-probability and required-probability breakpoints; keep sample probability-weighted value secondary and explicitly illustrative.
- Require agreement-verified timing-consideration mechanics and an exact assumed resolution date before featuring precise timing-adjusted expected-return or hurdle-probability outputs; otherwise label those outputs provisional.
- Source posture and missing evidence must be visible; do not hide weak assumptions behind clean tables.
- Empty, unsourced, or current-price-missing scenario outputs must use draft/support readiness and must not claim senior-review-ready status.
- Keep citation rendering readable: do not fragment tickers, dates, prices, percentages, scenario labels, or every derived table cell into repetitive citation links, and do not present an analyst assumption as an external evidentiary source.

## Do Not

- Do not rebuild a DCF, three-statement model, comps workbook, earnings model, event analysis, memo, hedge, or sizing workflow inside this dashboard.
- Do not make raw JSON, Markdown notes, CSV sidecars, run logs, or manifests the lead user-facing artifact unless explicitly requested.
- Do not present credit-security valuation, recovery waterfalls, covenant-package work, spread/yield relative value, CDS hedges, bond comps, or loan comps as Public Equity outputs; route those to Credit Markets.
- Do not call upside underwriteable if it misses the hurdle, depends on unsupported probabilities, lacks current-price anchoring, or has downside that overwhelms the expected return.
- Do not create a standalone sector dashboard. Sector context belongs inside the owning valuation or scenario dashboard.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm the dashboard states current price, base-case source, expected return versus hurdle, downside/upside ratio, break-even probability, skew label, and action thresholds where applicable.
- Confirm every chart has enough complete, source-backed rows; otherwise omit the chart and add `missing_evidence`.
- Confirm analyst probabilities, hurdle rates, break-value capture, and derived calculations are visibly distinguished from sourced facts.
- Confirm citation rendering remains readable and the recommendation is not repeated across redundant first-read modules.
- Confirm JSON/Markdown/CSV/run-log artifacts remain support files behind the HTML dashboard/report unless the user explicitly requests them.
- Confirm any credit, rates, FX, commodity, or macro input terminates in common-equity value, estimate, risk/reward, or portfolio-action implications.
