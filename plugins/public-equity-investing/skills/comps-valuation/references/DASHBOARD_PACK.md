# Comps Analysis Dashboard Pack

Use this pack only when a comps request explicitly selects a standardized dashboard, reusable dashboard template, PM cockpit, or structured payload-driven render. For an ordinary standalone HTML comps report, follow the flexible HTML artifact standard and the report-mode guidance in the owning skill instead of this fixed module map.

## Producer Role

`comps-valuation` owns the peer judgment, multiple interpretation, valuation read-through, and premium/discount logic. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `comps_analysis`
- `layout`: `single_page` for full PM diligence dashboards unless the user explicitly requests tabs
- `hero.callout`: the single valuation question or peer-set controversy
- `snapshot`: selected multiple/range, implied valuation skew, peer count, highest-quality comp, largest caveat, and source/as-of posture
- `sources`: filings and market/consensus provider sources first; label screen-grade, stale, unavailable, or user-provided inputs
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `overview`
   - `decision_box`: selected comp read, valuation posture, premium/discount view, and what would change the conclusion
   - `cards`: peer-set thesis, excluded peers, denominator caveats, and source posture
2. `peer-set`
   - `table`: peer inclusion/exclusion with business-model fit, geography, size, growth, margin, liquidity, and caveat columns
3. `valuation`
   - `table`: trading comps with market data as-of, EV bridge, denominator, multiple, growth/margin context, and citations
   - `bar_chart`: selected multiple or valuation-range visualization only when the sourced table is complete enough to speed interpretation
4. `premium-discount`
   - `cards`: reasons for premium/discount, quality adjustments, and unusable denominators
   - `scenario_map`: low/base/high selected-multiple cases, implied value ranges, and falsifiers
5. `refresh-gaps`
   - `missing_evidence`: missing prices, shares, debt, consensus, stale market data, peer validation gaps, and unsupported multiples

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every market value, multiple, estimate, peer inclusion/exclusion claim, and selected-multiple assumption.
- If data is unavailable, leave the row visible with `TBD / not sourced` and add a precise `missing_evidence` item.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not invent multiples or consensus fields.
- Do not turn a weak screen into a decision-grade valuation conclusion.
- Do not create a workbook or CSV export here; route formula-ready artifacts to `comps-valuation`.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.
- Do not fragment tickers, prices, multiples, percentages, dates, numeric ranges, metric names, or peer labels with citations.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm source ledger, peer-set rationale, selected multiple/range, and missing evidence are visible.
- Confirm all modules are supported by `dashboard-builder` and no chart shell is empty.
- Confirm citation rendering remains readable and action language is supported by the requested decision context.

## Equity Comps PM Modules

Dashboard payloads should include current price versus implied value, peer-median-to-selected-multiple bridge, premium/discount rationale, what is priced in, estimate path, scenario skew, action rules, source posture, and missing evidence.
