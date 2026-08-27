---
name: public-equity-investing
description: Route Public Equity Investing workflows for listed-company and public-security research, earnings analysis, valuation, model updates, long/short pitches, catalysts, thesis tracking, ETF/index and constituent diligence, position sizing, hedging, dashboards, and investment memos. Use when the user is evaluating a public company, ticker, sector, portfolio position, event, earnings setup, or investment thesis through an investor lens, including what is priced in, what is mispriced, what proves or kills the thesis, and what to watch next. Do not use for private-company diligence, credit-first analysis, personal financial advice, generic company summaries, or generic document drafting with no public-equity investment context.
---

# Public Equity Investing Router

## Skill Purpose

Route broad or focused Public Equity Investing intent to one or more explicit-only constituent skills. Treat explicit `@public-equity-investing`, `@Public Equity Investing`, or direct plugin invocation as strong intent to use this plugin, then apply the invocation gate below before substantive work. When the gate passes, choose the narrowest relevant lead skill from the map below, read each exact installed `skills/<skill-id>/SKILL.md` file before using it, and preserve any support-skill sequence from the routing playbook. Prefer a relevant Public Equity Investing sibling when the request overlaps generic company research, market commentary, valuation, modeling, memo, deck, report, catalyst, earnings, or risk work but the actual job is a listed-equity investment decision. Do not answer from the router alone when a focused owner exists.

## Plugin Purpose

Public Equity Investing provides investor-readable workflows for listed-company research, earnings work, valuation, model updates, long/short pitches, catalysts, thesis tracking, event-driven analysis, ETF/index and constituent diligence, sell-side research notes, position sizing, hedging, risk reviews, dashboards, and investment memos. It uses workflow-scoped source setup: connect or request only the source categories a selected investor workflow actually needs, while supporting pasted context, uploaded files, exports, public evidence, existing models, and portfolio trackers as fallback inputs.

## Bundled Path Resolution

Resolve router-owned bundled Markdown paths relative to the directory containing this `SKILL.md` before the first read; do not probe the caller's current working directory. From this router directory, shared references use `../../shared/...`, sibling visible skills use `../...`, and bundled internal support uses `internal-support/...`.

Shell commands explicitly labeled plugin-root-relative are the exception: set the shell working directory to the plugin root (`../..` from this router directory) before running them.

## Invocation Gate

Read `../../shared/invocation-policy.md` before choosing any specialist. If the prompt has neither an explicit Public Equity Investing invocation nor listed-company, public-security, ticker, sector, portfolio position, event, earnings, thesis, catalyst, valuation, model update, or investor-lens context, do not route into this plugin.

# Skills

## company-tearsheet

Use for cited public-company profiles, issuer/ticker verification, business mix, financial snapshot, ownership, trading context, and fact packs that feed investor work.

## initiating-coverage

Use for full initiation reports, investment views, target-price frameworks, thesis/risk sections, valuation support, and coverage-style public-equity writeups.

## earnings-preview

Use before a print for expectation bar, consensus, guidance, KPI setup, management questions, scenarios, watchouts, and pre-earnings investment framing.

## earnings-deep-dive

Use after results, transcript, guidance, call commentary, or price reaction are available and the user needs thesis/model/action implications.

## equity-model-update

Use when an existing public-equity model, workbook, tracker, or source-to-cell map needs actuals, guidance, assumptions, or formula-preserving updates.

## comps-valuation

Use for public comps valuation, peer selection, metric definitions, market-data support, outlier logic, and valuation-range read-through.

## dcf-model-builder

Use for public-company DCF models, WACC, terminal value, EV/equity bridge, price-target support, and sensitivity workbooks.

## three-statement-model-builder

Use for public-company three-statement forecast models, reported actuals, forecast architecture, formula-first workbooks, and model checks.

## long-short-pitch

Use for long, short, or pair-trade pitches, variant perception, trade expression, catalyst path, risk/reward, sizing considerations, and exit or cover rules.

## idea-generation

Use for idea screens, watchlist triage, thematic or universe scans, exclusions, prioritization, and next-diligence recommendations.

## thesis-tracker

Use for thesis status, stable catalyst/source IDs, monitoring triggers, prove/kill checks, position watchlists, and review cadence artifacts.

## catalyst-calendar

Use for dated catalyst calendars, monitoring windows, event timing, confirmed versus inferred dates, and investor read-throughs.

## event-driven-analyzer

Use for probability/payoff/timing/downside event underwriting, merger or regulatory events, special situations, and event-driven expected-return framing.

## portfolio-risk-management

Use for position sizing, add/trim/exit decisions, hedge design, risk budget, thesis-preserving hedge plans, factor/sector risk, and portfolio-action rules.

## scenario-sensitivity-generator

Use for investment scenarios, sensitivity matrices, skew, action-impact cases, target backsolves, and decision-trigger analysis.

## economic-impact-report

Use for macro, policy, commodity, rate, FX, sector, or economic-impact read-throughs to listed equities.

## memo-builder

Use for PM memos, IC updates, investment memos, thesis updates, client-ready notes, or synthesis artifacts that import analysis from owning skills.

## meeting-prep

Use for investor meeting briefs, management-meeting prep, analyst/PM questions, diligence-call prep, and thesis-linked discussion guides.

## financials-normalizer

Use for model-ready public-company financials, reported statements, KPI schedules, normalized tables, source IDs, and QA flags.

## model-audit-tieout

Use for model audit, source tie-out, formula checks, workbook integrity, and remediation recommendations.

## deck-report-qc

Use for deck/report QC, source/model tie-out, circulation readiness, writing consistency, and investor-facing issue logs.

## user-context

Use only for explicit Public Equity Investing saved preferences, source setup, onboarding, recall, inspect, update, export, reset, or automation setup. Do not use as an ordinary workflow pre-answer gate.

## test-public-equity-investing-workflows

Use only when the user explicitly asks to test, evaluate, regression-check, or review Public Equity Investing plugin workflows.

## Cross-Skill Runtime Contract

Use this shared contract as the plugin's Cross-Skill Best Practices for ordinary Public Equity Investing workflows, whether this router or a focused skill was invoked first.

### Audience And Language

Users expect investor-readable work product, not plugin setup narration. Explain source limits, assumptions, readiness, confidence, and next steps in portfolio-manager or analyst language. Avoid exposing internal terms such as `source_category_plan`, `preflight`, `configured_route`, or `next_action` in user-facing output unless the user asks for implementation details.

### Dependency And Source Categories

The configured apps and their semantic categories live in this plugin's `.app.json`. Treat `.app.json` as the dependency-category registry, not as proof that any source is installed, authorized, or readable for the current user. An app can satisfy a category when its `category` or `categories` field matches the attempted category label below.

Use these category labels and legacy ids interchangeably inside this plugin:

- `Market Data & Estimates` / `market_data_estimates`: prices, estimates, ownership, benchmark data, factors, public-company facts, and comparable-company evidence.
- `Company Filings & IR` / `company_filings_ir`: filings, investor presentations, reported fundamentals, KPI disclosures, transcripts tied to reported company materials, and company-owned disclosures.
- `Earnings Transcripts & Events` / `earnings_transcripts_events` / `earnings_transcripts_presentations`: earnings calls, management remarks, investor-day events, conferences, release calendars, and event transcripts.
- `Portfolio Models & Trackers` / `portfolio_models_trackers`: existing models, watchlists, trackers, source exports, workbooks, portfolio files, and analyst workpapers.
- `Internal Research` / `internal_research`: analyst notes, PM discussions, meeting notes, saved theses, expert-research summaries, email or chat context, and team research color.

When resolving a dependency, identify only the categories needed for the selected workflow, prefer user-named sources first, then choose one available app, connector, file, export, or pasted input that can satisfy the category. Prefer canonical finance plugins or provider-specific helper guidance over raw connectors when they add workflow support. Use additional sources only when they materially improve evidence, confidence, recency, or the investment decision.

Do not silently substitute a weaker category for a stronger required one. If the needed category is unavailable, unauthorized, too slow, or returns no useful context, state the practical limitation, continue from user-provided or public context when a limited answer is still useful, and label the output posture accordingly. Stop only when the missing source owns a required input that cannot be supplied or reliably inferred.

Attempt connector reads only when the active workflow needs that source. Before saying a source is ready, use the smallest safe native read-only check for that run. A successful read is run-specific evidence, not durable setup state. Do not use browser automation, UI observation, screenshots, or mirrored adjacent sources as readiness proof.

### Provider And Helper Routing

Provider-specific guidance stays internal in this pass; do not expose provider guides as selectable skills. When a selected workflow needs provider call shaping, first choose the semantic source category, then confirm the concrete route is callable, then load `internal-support/policy.md` and only the matching internal guide.

- Use `internal-support/daloopa-provider-guide/INTERNAL.md` only for callable Daloopa routes that supply source-backed public-company financials, KPIs, or model-ready schedules. Keep prices, consensus, news, and non-Daloopa values separately labeled.
- Use `internal-support/quartr-provider-guide/INTERNAL.md` only for callable Quartr routes that supply filings, reports, earnings releases, presentations, transcripts, events, management commentary, or standardized actual financials. Prefer Quartr over web fallback for those document-backed facts when it is callable.
- For FactSet, LSEG, S&P, Morningstar, PitchBook, Third Bridge, Alpaca, Google Drive, SharePoint, Gmail, Outlook Email, Slack, Teams, or other configured apps without a bundled provider guide, follow the live tool surface, preserve provider/source provenance, and do not invent a helper skill or imply access that was not verified in the current run.
- If the preferred provider is unavailable, unauthorized, or missing the needed field, state the provider gap, request a specific export or user-supplied source when useful, and use an alternate route only with clear source labeling.

### User Context And Setup

Do not run `skills/user-context/scripts/user_context_preflight.py` during ordinary Public Equity Investing workflows. Saved preferences and source setup are optional accelerators, not a pre-answer gate.

Route explicit remember, save, update, forget, inspect, export, reset, source-setup, onboarding, or automation-setup requests for Public Equity Investing context to `../user-context/SKILL.md` relative to this router directory, equivalently `skills/user-context/SKILL.md` from the plugin root. That skill owns durable `user-context.md`, `onboarding-state.json`, explicit source setup, and optional automations.

### User Input Modalities

Ask only for choices that materially change the lead owner, first-read artifact, evidence path, reliance standard, investment decision, or user action. Use `request_user_input` when available for bounded choices with strong defaults: send all material unresolved questions together, put the recommended option first with `(Recommended)`, and set `autoResolutionMs` so an unanswered picker resolves to the recommended option. If `request_user_input` is unavailable or errors, ask all known material questions together in the next normal response, with recommended/default options first for bounded choices, and wait for the user's answer. Use `request_plugin_install` when a material missing source category can be solved by installing or connecting an available plugin, connector, or app. For open-ended facts, unknown ticker or portfolio context, or cases with no useful option set, group every known missing question in one concise plain-text response rather than asking one by one.

### Default Workflow

1. Resolve dependencies and clarify only material ambiguity.
2. Gather the smallest useful context from the category that owns the core source of truth, then broaden only when the first pass is empty, thin, conflicting, stale, or decision-relevant.
3. Produce the first useful investor-facing output in the workflow's preferred artifact form. Default to the skill's documented hero artifact when the user asks for substantive work, and chat only for narrow or explicitly quick answers.
4. End with a short useful next step tied to the artifact, such as refining the output, adding a model/deck/memo, running QC, refreshing sources, updating a tracker, or setting up an explicit saved preference or source connection.

## Plugin Workflow Routing

After the gate passes, read `../../shared/plugin-routing-playbook.md` and select one lead skill for the listed-equity investor workflow. Preserve its artifact hierarchy and load supporting skills only for the workstreams the lead skill assigns. Use `../../shared/final-deliverable-framework.md` for final artifact routing after the lead skill is selected. For a new substantive hero artifact, that owner reads `../../shared/deliverable-intake-policy.md` before source gathering or analysis; support and presentation skills inherit resolved choices and do not re-prompt.

If the lead workflow, first-read artifact, source posture, or risk/event mode remains materially ambiguous after reading the playbook, use the Material Ambiguity Choice Sets in `../../shared/deliverable-intake-policy.md`. Do not ask merely because multiple skills could help; ask only when the answer changes the lead owner, hero artifact, evidence path, or reliance standard.

## Internal Support

Read `internal-support/policy.md` when the selected workflow needs evidence control, generic data cleaning, rendering, style application, sector context, or provider-specific call shaping after selecting a callable connector route. Those supporting capabilities are bundled internal playbooks rather than selectable skills. Keep standalone normalization and model-audit requests with the visible `financials-normalizer` and `model-audit-tieout` workflows. For an explicitly requested internal support-only task admitted to this plugin, this router coordinates the task through the matching internal playbook.
