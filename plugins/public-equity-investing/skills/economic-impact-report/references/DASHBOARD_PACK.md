# Economic Impact Report Dashboard Pack

Use this pack only when the user explicitly selects a standardized dashboard, reusable dashboard template, or structured payload-driven render for an economic, macro, policy, rates, commodity, geopolitics, or demand shock. For an ordinary standalone HTML economic-impact report, follow the flexible HTML artifact standard and the owning skill's event-to-equity guidance instead of this fixed module map. The dashboard must terminate in public-equity issuer, sector, earnings, valuation, positioning, and portfolio implications.

## Producer Role

`economic-impact-report` owns the public-equity transmission logic, affected issuers/sectors, scenario framing, source/freshness posture, estimate and valuation read-through, positioning/flow impact, and PM action implications. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `economic_impact_report`
- `layout`: `single_page` for full impact maps unless the user explicitly requests tabs
- `hero.callout`: the shock/transmission question and most exposed public-equity debate
- `snapshot`: shock magnitude, affected equity universe, top beneficiary, top risk, time horizon, source freshness, and PM action posture
- If no portfolio/watchlist/thesis was provided, include a general exposure map for industries, countries/currencies, public companies, relevant private companies, commodities, suppliers/customers, and second-order peers; label portfolio-specific action unavailable.
- `sources`: official economic releases first, then company filings, market data, trusted news/research, and user assumptions
- `Source posture`, `Missing evidence`, `Line item affected`, `Priced-in status`, and `PM action` must be visible in the payload rather than buried in prose.
- On this explicitly selected dashboard path, the HTML dashboard/report is the human deliverable; JSON, Markdown, CSV, and run logs are support artifacts.
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `impact-thesis`
   - `executive_summary`: shock, public-equity mechanism, likely listed-equity winners/losers, time horizon, and confidence
   - `decision_box`: PM bottom line, portfolio action posture, and what would change the view
2. `transmission-map`
   - `cards`: demand, pricing, margin, balance-sheet, rate, FX, commodity, regulatory, or funding channels, each ending in issuer/sector/line-item implications
   - `timeline`: expected sequence and data-release checkpoints
3. `issuer-sector-exposure`
   - `table`: issuers/sectors with exposure driver, first financial line item affected, sensitivity, evidence, valuation/risk implication, priced-in status, and confidence
   - `bar_chart`: exposure concentration, scenario sensitivity, or estimate-revision dispersion only when source-backed
   - `table`: no-portfolio fallback rows should include exposure bucket, affected industries/countries/currencies/companies/commodities, equity mechanism, first estimate or valuation line affected, positioning/flow read-through, and next workflow
4. `scenarios`
   - `scenario_map`: bull/base/bear or shock-size cases with public-equity read-throughs and falsifiers
5. `watch-items`
   - `market_events`: relevant policy, data, macro, company, sector, or regulatory events
   - `question_list`: next data checks, source requests, and research questions
   - `missing_evidence`: stale macro releases, unsupported issuer exposures, model gaps, and unavailable market data

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every macro datapoint, policy date, issuer exposure, sensitivity, estimate, and market move.
- Label stale releases, proxy exposures, model-derived sensitivities, and assumptions.
- Make cross-asset references explicit inputs: rate, FX, commodity, credit, option, or futures data may support equity impact, but the dashboard should not become a non-equity trade-construction artifact.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not turn a macro note into generic commentary with no issuer/security linkage.
- Do not turn the dashboard into a standalone rates, FX, commodity, futures, options, or credit-security dashboard.
- Do not overclaim causality when evidence only supports correlation or a plausible channel.
- Do not present standalone rates, FX, commodity, futures, options, credit-security, CDS, bond, loan, spread/yield, covenant, recovery, or debt-security analysis as the Public Equity Investing output.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm the dashboard has a clear transmission map, issuer/sector exposure table, earnings/valuation/positioning read-through, scenarios, and freshness labels.
- Confirm unsupported exposures appear in `missing_evidence`, not hidden in narrative.
