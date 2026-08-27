# Public Equity Investing Plugin

Public Equity Investing supports listed-company research, equity valuation, earnings analysis, event-driven equity work, sector/thematic equity context, catalyst tracking, position sizing, hedge analysis, thesis monitoring, dashboards, workbooks, and investor-facing equity research artifacts.

This plugin should be Public Equity Investing-first. Shared core skills may be reused from other plugins, but active routing and handoffs in this tree should point to skills installed inside this plugin unless a dependency is explicitly marked as optional or cross-plugin. Credit-first work routes to the sibling Credit Markets plugin.

## Get started

Try asking:

`@Public Equity Investing Help me get started with a first listed-equity task`

The plugin will route through the Public Equity Investing router, select the focused workflow, and ask for or connect only the source categories needed for that workflow. You can also start directly with a ticker, issuer, position, portfolio file, transcript, filing, earnings event, catalyst, model, uploaded file, exported workbook, pasted notes, or public evidence.

## Example workflows

| Workflow | Try this | Skill | Result |
| --- | --- | --- | --- |
| Prepare for earnings | `Build a pre-earnings preview for this public company.` | `earnings-preview` | An investor-facing preview with expectation bar, key debates, scenarios, and call questions |
| Analyze a post-print move | `Turn this earnings release and transcript into a thesis-impact deep dive.` | `earnings-deep-dive` | A post-earnings report with model, valuation, thesis, and action implications |
| Build a long/short pitch | `Create a long/short pitch with catalysts, valuation, risk/reward, and exit rules.` | `long-short-pitch` | A PM-facing trade pitch with variant perception, catalyst path, and risk controls |
| Update a model | `Flow these actuals and guidance through my public-equity model.` | `equity-model-update` | An updated workbook or change log with source-to-cell posture and thesis impact |
| Track catalysts | `Build a 90-day catalyst calendar for this position.` | `catalyst-calendar` | A dated catalyst view with confirmed/inferred timing, evidence, and monitoring actions |
| Review risk and sizing | `Assess whether I should add, trim, hedge, or exit this position.` | `portfolio-risk-management` | A sizing or hedge decision report with triggers, constraints, and evidence gaps |

## Invocation Gate

Use `shared/invocation-policy.md` before routing an untagged request. Public Equity Investing is entered automatically only for an unmistakable listed-equity investor workflow; otherwise it must be explicitly named or tagged. The implicitly surfaced `public-equity-investing` router applies this gate, then uses `shared/plugin-routing-playbook.md` and `shared/plugin-routing-map.json` to select the lead workflow while specialist and support skills remain explicit or router-invoked.

## Scope

Primary users:

- Long-only public-equity investors.
- Hedge fund equity analysts and portfolio managers.
- Sell-side equity research teams.
- Event-driven equity investors.
- Sector and thematic listed-equity research teams.
- ETF/index, passive-flow, benchmark-relative, and constituent diligence teams.

Primary workflows:

- Prepare pre-earnings previews and post-earnings deep dives.
- Build and update DCF, three-statement, comps, and public-company model outputs.
- Draft public-equity investment memos, long/short pitches, initiation notes, PM updates, client notes, and research updates.
- Track catalysts, thesis milestones, risks, hedges, and position sizing for listed-equity decisions.
- Analyze sector-specific KPIs, issuer/sector economic impacts, equity event paths, valuation debates, thesis read-throughs, benchmark-relative equity diligence, index-event work, constituent exposure, factor exposure, and ETF/index flow relevance.

Credit Markets owns bonds, loans, CDS, investment grade, high yield, leveraged loans, bank loans, private-credit / public-credit instruments, distressed debt, restructuring, recoveries, covenants, spreads, yields, and debt-security selection. Use Credit Markets for credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis. This plugin may reference leverage, liquidity, maturities, ratings, spreads, or covenant risk only when those facts support a common-equity or listed-equity thesis.


## Public Equity PM Judgment Standard

All core research skills should load `shared/pm-judgment-heuristics.md` for substantial public-equity work. Outputs should answer what is mispriced, what is already priced in, what proves the thesis, what kills it, why now, what changes sizing/rating/target/hedge/trim/exit/watchlist status, and what evidence is missing. Audience modes are `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, and `public_equity_diligence`.

## Default Artifact Depth

Recommend the full version of the relevant Public Equity Investing artifact. In interactive runs, honor the depth selected during intake. In non-interactive runs, default to full working analysis unless the query explicitly requests shorter output. Do not shorten simply because context is sparse or sources are missing. Sparse context should produce a full `screen-grade` structure with provisional posture, assumptions, missing evidence, and upgrade path.

Use compressed output when the user selects it during intake or explicitly asks for a `summary`, `short`, `quick read`, `one-pager`, `TL;DR`, `brief`, or a single requested section. In those cases, preserve source posture, key conclusion, material caveats, and exact missing data.

## Final Deliverable Framework

Use `shared/final-deliverable-framework.md` for final artifact routing and `shared/html-artifact-standard.md` for user-facing HTML quality. The default user-facing deliverable should be a human-readable artifact: a DOCX memo, HTML dashboard/report, XLSX workbook, or concise chat answer depending on the selected or high-confidence inferred surface. Markdown, JSON, CSV, manifests, run logs, and plan files are support or audit artifacts unless the user explicitly asks for them. Default Markdown sidecars should be named `support_note.md` or `*_support_note.md`; `report.md` is legacy/explicit only.

Before an artifact-owning skill begins source gathering or analysis for a new substantive hero deliverable, load `shared/deliverable-intake-policy.md` and use adaptive `request_user_input` intake for materially unresolved choices when callable. The user does not need to name a file extension: infer the surface when the prompt and conversation make it high-confidence, but ask when a new memo, report, note, or briefing could plausibly be Word, HTML, inline, deck, or workbook output. Preserve an existing artifact's format for edits/reviews and reuse resolved preferences through downstream model, QC, and dashboard steps without recording them in payloads or schemas.

For substantive single-company 60/90-day catalyst calendars, default to a polished HTML catalyst calendar unless the user requests another format, a quick/no-file answer, or a workbook/tracker; in interactive runs, ask only unresolved depth, audience/use, or focus choices. For high-confidence source-heavy earnings, event, scenario, model-audit, idea-generation, thesis-tracker, event-calendar, or multi-table equity workflows, recommend a polished HTML artifact while continuing to ask for materially unresolved format and depth choices in interactive runs. For formal IC, PM, committee, client, or research memos, recommend DOCX when the surface is unresolved; recommend HTML only for high-confidence source-heavy web-style reports, and inline for quick memo updates. In non-interactive runs, apply documented workflow defaults and disclose assumed format and depth in the delivery message or accompanying summary, not as visible artifact metadata. Let the workflow determine the HTML structure rather than forcing every artifact into a standard dashboard layout. Rendering to HTML does not compress the analysis.

Out of scope unless the user explicitly asks to leave the local Public Equity Investing workflow:

- Credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis.
- Buyer-process execution, CIM drafting, banker pitch books, and deal-circulation gates.
- Sponsor underwriting, LBO ownership handoffs, QoE diligence, and private investment committee workflows.
- Budget ownership, headcount planning, CFO reporting, and operating-company planning workflows.
- Standalone macro strategy, rates research, fixed-income portfolio workbench analysis, curve/DV01 trade construction, and broad cross-asset macro research.

## Skill Inventory

Entry router:

- `public-equity-investing`

Research and memo skills:

- `company-tearsheet`
- `earnings-preview`
- `earnings-deep-dive`
- `initiating-coverage`
- `memo-builder`
- `long-short-pitch`
- `idea-generation`
- `thesis-tracker`
- `meeting-prep`

Modeling, valuation, and data workflows:

- `dcf-model-builder`
- `three-statement-model-builder`
- `comps-valuation`
- `equity-model-update`
- `financials-normalizer`
- `model-audit-tieout`
- `scenario-sensitivity-generator`

Event, economic-impact, and risk skills:

- `catalyst-calendar`
- `event-driven-analyzer`
- `economic-impact-report`
- `portfolio-risk-management`

Internal sector context capability:

- `sector-context-overlay` (bundled internal playbook)
  - Supported lenses: banks, biotech/pharma, consumer internet/marketplaces, exchanges/market infrastructure, insurance, oil & gas E&P, REITs, and SaaS/subscription software.
  - This is a context layer for sector KPIs, modeling rules, valuation conventions, source hierarchy, output adaptations, and red flags.
  - It should not own earnings, model, memo, pitch, event, risk, or QC artifacts.

Circulation workflow:

- `deck-report-qc`

Internal support capabilities:

- `dashboard-builder`
- `financial-source-of-truth`
- `excel-data-cleaner`
- `style-guide-adapter`
- `sector-context-overlay`

These capabilities are packaged beneath the `public-equity-investing` router rather than selectable skills. Use `skills/public-equity-investing/internal-support/policy.md` and `shared/support-layer-routing-contract.md`: support outputs should preserve the owning workflow, decision impact, readiness effect, artifact role, and whether CSV/JSON/Markdown/log/profile/ledger files stay hidden unless requested in internal handoffs or support artifacts. User-facing hero artifacts should state material implications in natural language rather than exposing those internal field names.

## Canonical Routing

Use `public-equity-investing` as the only implicit entrypoint: it admits explicit plugin invocations and perfect-fit listed-equity investor requests, then reads `shared/plugin-routing-playbook.md` to select the specialist workflow below. `shared/plugin-routing-map.json` is the structured companion for tests and eval prompt coverage.

Use `earnings-preview` for full pre-print preview reports by default, centered on the expectation bar, stock-reaction drivers, source posture, and decision-relevant call questions. Add KPI histories, scenarios, market context, or expanded diligence modules when they are relevant and source-supported. Short summaries are explicit-only.

Use `earnings-deep-dive` after results, transcript, guidance, or call commentary are available.

Use `equity-model-update` when the user wants to update an existing public-company equity model, flow actuals through a model, or produce a model change log.

Use `dcf-model-builder` and `three-statement-model-builder` for explicit public-company model-building tasks. Use `comps-valuation` in `report` mode for comparable-company peer logic and valuation read-throughs, or in `workbook` mode for workbook/export asks; substantial reusable report-mode packages should become an HTML report/dashboard.

Use `model-audit-tieout` for substantive standalone reviews of existing models and model packages; by default, deliver a polished standalone HTML model-audit report that states permitted decision use, critical blockers, source tie-outs, illustrative audit sensitivities, and remediation sequence. Use a standardized dashboard only when explicitly requested.

Use `memo-builder` for formal equity written artifacts: IC memos, investment memos, committee notes, client notes, research notes, PM updates, and event notes. It can synthesize trade-pitch output, but it should not own live trade construction. Credit-first memos route to Credit Markets.

Use `long-short-pitch` for PM-facing equity trade pitches: explicit long/short pitches, pair trades, hedge-fund idea writeups, variant perception, trade expression, catalyst path, sizing considerations, and add/trim/exit/cover rules. Credit-security pitches route to Credit Markets.

Use `catalyst-calendar` for equity catalyst tracking and monitoring windows. Use `event-driven-analyzer` for full merger arbitrage, spin-off, tender, regulatory approval, and other dated public-equity event underwriting. Use `scenario-sensitivity-generator` for a focused success/delay/break or breakpoint overlay once event terms and current pricing are verified or supplied. Distressed exchanges, bankruptcies, restructuring, covenant, recovery, and debt-security event work route to Credit Markets unless Credit Markets outputs are only being used as inputs to a listed-equity event view.

Use `economic-impact-report` only when a macro, policy, commodity, geopolitical, or cross-asset development needs to be translated into public issuer, sector, earnings, valuation, equity risk, or portfolio implications. Do not use it as a standalone macro/rates/fixed-income workbench.

Use `portfolio-risk-management` in `position_sizing`, `hedge_design`, or `integrated_risk_plan` mode for listed-equity sizing and thesis-preserving hedges across common equity, shorts, pairs, options, equity events, ETFs, factors, and causal macro proxies. Credit hedges, CDS, bonds, loans, spread DV01, and capital-structure hedges route to Credit Markets.

Load the internal `sector-context-overlay` capability to add sector-specific KPIs and analytical judgment to earnings, model updates, tearsheets, initiation work, memos, trade pitches, event work, and risk outputs. It should not replace the primary workflow owner. The overlay uses progressive disclosure: one compact router selects exactly one sector lens, and deeper nuance lives in `sector-context-overlay/references/<sector>/`.

Load the internal `dashboard-builder` capability when the user asks for a standardized dashboard, a reusable or payload-driven dashboard template, or validated rendering through the shared module schema. For bespoke HTML reports, the primary analysis skill follows `shared/html-artifact-standard.md` and chooses a layout suited to its requested job. When `dashboard-builder` is selected, the primary analysis skill still owns the finance logic and `dashboard-builder` owns the shared module schema, single-page/tabbed responsive HTML shell, source/missing-evidence visibility, and validation.

Use `deck-report-qc` as the Public Equity Investing final circulation gate for client-facing or investment-team-facing equity decks and reports.

Use visible `financials-normalizer` and `model-audit-tieout` when normalization or model review is the user's standalone job. Load internal `financial-source-of-truth`, `excel-data-cleaner`, and `style-guide-adapter` capabilities when their support could change confidence, valuation, target, sizing, hedge posture, watchlist status, or circulation readiness. Keep `deck-report-qc` visible as the explicit circulation workflow. Support capabilities prepare or de-risk the owning workflow; they do not own the recommendation.

## Artifact Levels

Instruction-led artifacts:

- Research memos, investment notes, thesis updates, meeting prep, `sector-context-overlay` context, and narrative recommendations where the skill does not ship a deterministic script. Substantial reusable versions should render as polished HTML artifacts following `shared/html-artifact-standard.md`; use `dashboard-builder` only when the workflow selects its standardized rendering path. Chat is the hero only for narrow or explicitly quick asks.

Deterministic exports:

- Script-backed CSV, JSON, Markdown, or XLSX outputs generated by bundled helpers.
- CSV, JSON, Markdown, run logs, and manifests are support/audit files unless explicitly requested as the deliverable. Important status must also appear in the HTML dashboard/report, workbook `Cover`, or final chat handoff.
- These should include source assumptions, run logs, warnings, and validation status when the skill supports them.

Model workbooks:

- DCF, three-statement, comps, and equity-model-update outputs should clearly distinguish calculated deterministic exports from any template-based or future formula-workbook behavior.
- Do not describe an output as a fully linked banker formula workbook unless the skill ships formula materialization, workbook inspection, and formula integrity tests.
- Generated `.xlsx` workbooks should follow `shared/workbook-artifact-standard.md`: first visible tab named `Cover`, meaty dashboard-style read-through, source posture, warnings/hard failures, key outputs, chart-ready data, and workbook map.

Circulation-ready artifacts:

- Standardized dashboards should be produced through `dashboard-builder` from a typed `public_equity_investing_dashboard.v1` payload. Bespoke HTML reports should follow `shared/html-artifact-standard.md` without being forced through that payload or shell.
- Final decks, reports, and research packets should route through `deck-report-qc` for Public Equity Investing circulation checks and `style-guide-adapter` for formatting/style adaptation only.

## Connectors

The plugin may use user-provided files and connected apps when available. Connector presence in `.app.json` should be treated as optional runtime capability, not a guarantee that every data provider or workplace app is callable for every user.

When a connector or provider is unavailable:

- Ask the user for uploaded files, pasted excerpts, or exported CSV/XLSX data.
- Label assumptions as user-provided, source-derived, estimated, or placeholder.
- Do not imply live Bloomberg, FactSet, CapIQ, PitchBook, Morningstar, LSEG, Daloopa, brokerage, email, or collaboration-app access unless the connector is actually available in the runtime.

## Shared Core Versus Public Equity Investing-Specific Skills

Shared core workflows `financials-normalizer` and `model-audit-tieout`
remain visible because they own plausible user-requested deliverables.
Supporting capabilities such as `financial-source-of-truth`,
`excel-data-cleaner`, and `style-guide-adapter` are internal playbooks adapted to Public Equity Investing handoffs in this plugin. `company-tearsheet` and `meeting-prep` also remain visible workflows.

Public Equity Investing-specific visible skills such as `earnings-preview`,
`earnings-deep-dive`, `equity-model-update`, `long-short-pitch`,
`event-driven-analyzer`, and `portfolio-risk-management` own the domain-specific analytical language and output expectations. The internal `sector-context-overlay` capability supplies context under those owners.

## Maintenance Notes

- Credit Markets is the sibling owner for credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis. Keep this plugin focused on public-equity decisions.
- Standalone macro/rates/fixed-income ownership is intentionally not local for now. If needed later, add a real `fixed-income-rates-macro-workbench` or route to Credit Markets before advertising fixed-income ownership in the manifest.
- External regression and benchmark assets should live outside this production package in the external eval harness when created.
- Continue to keep shared-core skill handoffs Public Equity Investing-local when copying or refreshing skill text from other plugins.
- Sector context now lives in one compact `sector-context-overlay` router plus deferred references; keep this pattern when adding or refreshing sector coverage.

## External Evaluation Harness

Testing, smoke, benchmark, golden-fixture, and historical eval assets intentionally live outside this production package. Use the external eval harness and `../../plugin_evals/README.md` for commands and benchmark guidance.
