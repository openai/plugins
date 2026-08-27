# Portfolio Risk Management Dashboard Pack

Use this pack only when the user explicitly requests a standardized dashboard, recurring monitoring dashboard, reusable validated template, or structured payload-driven render for a position-sizing analysis, hedge design, integrated risk plan, drawdown map, liquidity check, or PM risk package. An ordinary substantial integrated plan is a polished standalone HTML risk decision report following `../../../shared/html-artifact-standard.md`.

## Producer Role

`portfolio-risk-management` owns size, hedge selection, retained-exposure judgment, binding constraints, basis risk, scenario P&L, liquidity analysis, and monitoring rules. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

| Skill mode | Payload mode | Lead decision |
| --- | --- | --- |
| `position_sizing` | `portfolio_risk_position_sizing` | Recommended size and binding constraint. |
| `hedge_design` | `portfolio_risk_hedge_design` | Recommended hedge package, basis risk, and readiness. |
| `integrated_risk_plan` | `portfolio_risk_integrated_plan` | Size-versus-hedge comparison and retained alpha. |

Use `layout: single_page` for reusable risk packages unless the user explicitly requests tabs. The hero callout should state the recommended action, intended alpha, unwanted risk, retained exposure, binding constraint, and whether a size-down/no-hedge alternative is cleaner.

## Tabs And Modules

1. `risk-decision`
   - `decision_box`: mode, recommended size and/or hedge, action, confidence, intended alpha, unwanted risk, retained exposure, binding constraint, basis risk, size-down/no-hedge alternative, and what changes the recommendation.
   - `metric_tiles`: size, downside loss, liquidity exit, gross/net/beta/factor impact, active-weight impact, ADV/exit days, cost/carry, borrow/squeeze/crowding, and readiness.
2. `exposure-map`
   - `table`: keep, hedge, reduce, and monitor classifications with evidence and decision impact.
3. `constraints-and-candidates`
   - `table`: sizing constraints in `position_sizing` mode, hedge candidates and basis-risk ranking in `hedge_design` mode, or both in `integrated_risk_plan` mode.
4. `risk-return`
   - `scenario_map`: upside/base/downside/stress/catalyst-path cases and at least one hedge-failure case when protection is recommended.
5. `liquidity-execution`
   - `key_metrics`: ADV, participation rate, days to exit, borrow/financing, option liquidity where relevant, cost/carry, and implementation-readiness gaps.
6. `monitoring`
   - `timeline`: add, trim, exit, cover, resize, hedge, roll, remove, re-underwrite, and thesis-break triggers.
   - `missing_evidence`: missing NAV/AUM, limits, price, ADV, volatility, borrow, option-chain, factor, downside, basis-risk, or Credit Markets handoff inputs.

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Cite every price, size, NAV/AUM, volatility, liquidity, exposure, borrow/financing, cost/carry, target/downside, hedge input, and scenario assumption.
- Label assumptions, user-provided limits, model-derived fields, stale market data, and implementation-readiness gaps.
- Credit instruments, CDS hedge implementation, bonds, loans, spread DV01/CS01, recovery, covenants, and capital-structure hedges require a visible Credit Markets handoff.

## Do Not

- Do not size from conviction alone or hide the binding constraint.
- Do not turn an assumed adverse-move scenario into an implementation recommendation when the user's loss limit may be an absolute cap.
- Do not recommend a hedge without showing retained exposure, basis risk, cost/carry, hedge-failure risk, and the size-down/no-hedge alternative.
- Do not make JSON, Markdown, CSV, manifests, or run logs the lead user-facing artifact unless explicitly requested.

## QA Checks

- Confirm the PM decision box shows intended alpha, unwanted risk, retained exposure, binding constraint, and size-down/no-hedge alternative.
- Confirm sizing output shows gross/net/beta/factor impact and liquidity exit when sizing is in scope.
- Confirm hedge output shows basis risk, cost/carry, hedge-failure scenario, readiness, and exit rules when hedging is in scope.
- Confirm an absolute loss cap on a short uses priced share-for-share call protection or concludes `do not initiate`.
- Confirm citation rendering remains readable and does not fragment tickers, dates, percentages, basis-point amounts, instrument terms, or scenario labels.
- Confirm support JSON, Markdown, CSV, and logs remain behind the dashboard or decision summary unless explicitly requested.
- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
