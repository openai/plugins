---
name: dashboard-builder
description: Use when rendering, validating, or adapting standardized responsive Public Equity Investing HTML dashboards from structured analysis produced by visible Public Equity Investing skills. This capability owns the optional dashboard shell, module schema, and HTML export; it does not own underlying investment analysis or bespoke HTML design.
---

# Dashboard Builder

> Internal support playbook. Load through `internal-support/policy.md`; this renderer is bundled with the visible router rather than exposed as a skill entrypoint.

## Deliverable Intake

When another skill owns the analysis, inherit its resolved deliverable preferences and do not re-prompt before rendering. Only when this skill independently owns a new substantive standalone dashboard should it, before source gathering, analysis, or rendering, load `../../../../shared/deliverable-intake-policy.md` and perform its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices.

Build standardized, responsive, source-visible Public Equity Investing dashboards from typed listed-equity analysis payloads. Follow `../../../../shared/html-artifact-standard.md` for overall HTML quality. Use this capability when the user asks for a standardized dashboard, reusable dashboard template, structured payload-driven render, or when another Public Equity Investing skill explicitly selects this standardized rendering path. Do not load it merely because a producer skill is creating a polished bespoke HTML report.

## Boundary

- This skill owns the dashboard shell, module contract, responsive layout, validation, and HTML rendering.
- Visible producer skills may create bespoke HTML artifacts directly under `shared/html-artifact-standard.md`; they do not need to map every report into this schema.
- Credit Markets dashboards, credit-security dashboards, recovery dashboards, covenant dashboards, and distressed debt dashboards belong in the Credit Markets plugin. Use Credit Markets for credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis.
- The primary Public Equity Investing workflow owns the finance logic. For example, `earnings-preview` owns the pre-print bar and KPIs; `earnings-deep-dive` owns beat/miss and EPS quality; `long-short-pitch` owns trade expression and variant perception.
- Do not duplicate finance reasoning inside the renderer. Convert the primary skill's final analysis into a `public_equity_investing_dashboard.v1` payload. The JSON payload is an internal handoff contract, not the final user-facing artifact.
- Use generic issuer identity tiles by default. Do not require logos; use sourced or user-provided logos only when available and safe. The ticker badge should use a sourced or reasonable brand color when available, but prefer a darker brand shade so the white ticker text remains readable.

## Workflow

1. Select the primary analysis skill first unless the user supplied a finished dashboard payload.
2. Load `references/module-contract.md` when choosing modules or mapping a producer skill into tabs.
3. Use `references/mobile-qa.md` before finalizing a dashboard or changing layout behavior.
4. Create or receive a JSON payload with `kind: public_equity_investing_dashboard.v1`, `mode`, `layout`, issuer metadata, `metadata`, `hero`, `snapshot`, sections/tabs, modules, sources, workbook `model_citations`/`model_citations_path` when applicable, and explicit missing evidence. Keep this JSON as support/audit material; the rendered HTML is the user-facing artifact.
   - Production dashboards must set `metadata.payload_stage: "production"` and `metadata.citation_policy: "strict"`.
   - Production metadata must include `freeze_time`, `source_posture`, `readiness_label`, `readiness_posture`, and `decision_context`.
   - Draft/support payloads may use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"`, but gaps must remain visible and the payload must not be presented as PM-ready.
   - Assign stable source IDs in top-level `sources` (`S1`, `S2`, or more descriptive IDs), then cite every material number, estimate, quote, date-sensitive claim, and assumption inline using `citations`, `source_id/source_ids`, or bracketed markers such as `[S1]` in text.
5. Validate the payload:

```bash
python skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py payload.json --profile production
```

6. Render a standalone HTML dashboard:

```bash
python skills/public-equity-investing/internal-support/dashboard-builder/scripts/render_dashboard.py payload.json output/index.html --profile production
```

7. Run a structural smoke pass: no unresolved placeholders, valid tab ids, supported modules only, source ledger present, and mobile-safe tables.
8. Run the chart-readiness smoke pass: financial trend, EPS actual/estimate, and equity price/event charts must have enough complete renderer-ready rows to display. If a chart does not have enough complete source-backed rows, omit the chart module and add a `missing_evidence` module that names the unavailable series.
9. Run the citation smoke pass: no unresolved citation chips, no numeric material without inline citation support, hero `dek` and `callout` preserve `hero.citations`, and hover/focus previews work for citation chips.

## Producer Pack Index

Producer skills own the investment analysis and choose the source-backed content. `dashboard-builder` owns the shared shell, module rendering, validation, responsive behavior, and export only when its standardized dashboard path is selected. When a producer retains a local `references/DASHBOARD_PACK.md` and elects this path, load that pack before mapping analysis into `public_equity_investing_dashboard.v1`.

Typed producer packs:

- `company-tearsheet/references/DASHBOARD_PACK.md`
- `comps-valuation/references/DASHBOARD_PACK.md`
- `deck-report-qc/references/DASHBOARD_PACK.md`
- `earnings-deep-dive/references/DASHBOARD_PACK.md`
- `earnings-preview/references/DASHBOARD_PACK.md`
- `economic-impact-report/references/DASHBOARD_PACK.md`
- `event-driven-analyzer/references/DASHBOARD_PACK.md`
- `idea-generation/references/DASHBOARD_PACK.md`
- `initiating-coverage/references/DASHBOARD_PACK.md`
- `long-short-pitch/references/DASHBOARD_PACK.md`
- `meeting-prep/references/DASHBOARD_PACK.md`
- `memo-builder/references/DASHBOARD_PACK.md`
- `equity-model-update/references/DASHBOARD_PACK.md`
- `portfolio-risk-management/references/DASHBOARD_PACK.md`
- `scenario-sensitivity-generator/references/DASHBOARD_PACK.md`
- `thesis-tracker/references/DASHBOARD_PACK.md`

If a workflow has no typed producer pack, use `references/module-contract.md`, keep the producer skill as analysis owner, and include `missing_evidence` for any unsupported module rather than inventing dashboard-only numbers.

Model-output dashboard maps:

- `comps-valuation/references/workbook/dashboard-map.md`
- `dcf-model-builder/references/dashboard-map.md`
- `model-audit-tieout/references/dashboard-map.md`
- `equity-model-update/references/dashboard-map.md`
- `three-statement-model-builder/references/dashboard-map.md`

Load the relevant model-output map whenever a dashboard cites workbook cells, model audit findings, formula exceptions, source-to-cell provenance, or safe workbook-update results.

## Output Rules

- Keep enough analytical depth to satisfy the task, but do not add sections solely to fill a dashboard module inventory. Short dashboards are explicit-only.
- Use `layout: "single_page"` for PM diligence dashboards unless the user asks for tab-only navigation. It keeps all sections visible on one page and renders a sticky table of contents for section jumping.
- Every material number, quote, estimate, source timestamp, date-sensitive claim, and assumption must be cited inline where it appears, not only in the bottom source ledger. Use `citations: ["S1"]`, `source_id: "S1"`, `source_ids: ["S1", "S2"]`, or bracketed text markers such as `Q1 revenue was $8.1M [S1]`.
- Prefer subtle numeric citation links for actual metric values. When a sourced value is numeric, the rendered number itself should link to the source ledger/source URL and show the hover/focus preview; avoid placing a separate citation chip beside every metric.
- When every line in a section depends on the same source set, use a compact section-level source note rather than repeating identical chips after each sentence. Keep point-of-use citations for specific numbers, quotes, dates, and claims that need their own source.
- The bottom source ledger remains mandatory, but it is not sufficient by itself. The reader should be able to audit a number or claim from the module where they see it.
- Workbook-backed dashboards may include `model_citations` or `model_citations_path` from DCF, three-statement, comps, or equity-model-update workflows. These records are rendered as source-ledger rows and citation popovers with workbook, sheet, range, value, and formula details. Keep the citation JSON and any Markdown `support_note.md` sidecar as support material; do not expose them as the lead artifact.
- Citation links/chips must support click-through to the source ledger or source URL and hover/focus previews with source title, type/status, date, and excerpt/pinpoint when available. Citation links should inherit normal text color rather than using default bright-blue hyperlink styling.
- Preserve GAAP/non-GAAP, period, units, scale, estimate `as_of`, and source posture labels from the producer skill.
- The quarter/period belongs in the hero headline, dek, or metadata. Do not spend a snapshot/highlight tile on the quarter when it is already in the headline.
- Snapshot/highlight tiles must hero the investor question, not merely the largest absolute numbers. Prefer surprise %, growth acceleration, clean EPS beat, guide change, unit growth, backlog, margin path, capex guide, or other name-specific KPIs over generic reported values. If the stock-moving point is a growth rate or surprise %, make that the tile value and put the absolute dollar value in the detail.
- Use generic issuer identity tiles by default. Treat logos as optional decoration, not a dependency. Populate `issuer.accent_color`, `issuer.brand_color`, `issuer.brand_dark_color`, `issuer.identity_color`, or `issuer.brand_colors` when known; the renderer will choose a dark, white-text-readable ticker badge color from those inputs.
- Keep PM dashboards information dense by default: avoid decorative whitespace, keep section spacing compact, and use dense table mode for analyst-facing KPI, guide, beat/miss, transcript, and read-through modules.
- Keep typography consistent across modules. Use the shared dashboard font scale and fixed responsive breakpoints rather than ad hoc viewport-scaled heading sizes.
- Include `market_events` when recent news, market structure, macro, regulatory, litigation, product, management, peer, or forward-catalyst context could affect the investment decision. The dashboard renders the event table; the producer skill owns event selection, sourcing, and impact analysis.
- For earnings-preview and earnings-deep-dive dashboards, include the earnings visualization pack only when complete source-backed data exists:
  - `financial_trend_chart` for the last several reported quarters with revenue, gross profit, net income, and the best source-backed profitability margin line for the issuer and quarter. Default to net margin only when it is a fair recurring-profitability proxy. Use operating margin, adjusted operating margin, EBITDA margin, FCF margin, or another explicitly labeled margin when net income is distorted by below-the-line gains/losses, tax, FX, mark-to-market, equity-investment gains, restructuring, impairments, litigation, asset sales, or other non-recurring items.
  - `eps_actual_vs_estimate_chart` for the past five quarters of estimated EPS versus actual EPS, or fewer only when the visible module states the available window.
  - `equity_price_event_chart` only when the price tape is substantive: source-backed daily data needs at least 10 distinct price points over at least 7 calendar days, hourly data needs at least 24 time-stamped price points over at least 6 hours, and minute/intraday data needs at least 60 time-stamped price points over at least 45 minutes. A sparse reaction tape, quote-card trio, or a few article-reported closes is not enough; use `market_events` plus `missing_evidence` instead.
  If any required series is missing, stale, not parseable, not comparable by period/basis, or too thin for the chart's minimum window, omit the chart and list the missing series in `missing_evidence` rather than filling blanks. QA validates enough chart-ready rows survive renderer field requirements; strict payloads with incomplete chart modules fail validation.
- For `financial_trend_chart`, the producer skill should set `data.margin_metric`, `data.margin_label`, and `data.margin_rationale` when it selects a line other than net margin. The renderer supports this handoff but does not decide finance quality on its own.
- Chart axes must be readable as scales, not mystery thresholds. Positive-only bar and EPS charts should start at zero, show multiple gridlines/ticks, and avoid negative lower bounds created only by padding.
- Add charts only when they reduce interpretation time. Prefer compact native charts for small comparable metric sets such as segment growth, revenue mix, guidance deltas, exposure, or catalyst probability. Do not chart every table.
- Hero `dek` and `callout` honor `hero.citations`. Use them for source-backed masthead claims, including numeric callouts that should render as subtle source links.
- Render as one standalone local HTML file unless the user asks for a web app or deployment.
- Keep JavaScript limited to local UI behavior such as tabs. Do not fetch remote data from rendered dashboards.
