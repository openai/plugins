---
name: meeting-prep
description: Use when creating Public Equity Investing meeting prep briefs. Do not use for private diligence, IB, FP&A, legal, or scheduling-only tasks.
---

# Meeting Prep

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the catalogued source categories needed for the current meeting. Prefer a user-named source first, then one available app, connector, file, export, or pasted input that satisfies the category. Attempt the smallest useful native read only when the workflow needs that source. If a route needs auth, connection, or setup, state the practical limitation and continue from prompt context, active artifacts, pasted or exported material, and public sources when the meeting brief can still be useful. Do not inspect unrelated source categories, run broad source setup, write connector readiness, or create, read, migrate, or update `category-state.json`.

The runtime source categories below cover the catalogued Public Equity Investing sources. Use `references/context-and-sources.md` for the broader evidence hierarchy, including optional meeting-logistics connectors.

### Workflow Sources

When this skill uses a source category, use it for the following information. These are semantic source categories, not fixed connector names.

- `company_filings_ir`: filings, IR materials, and reported financials needed for the meeting baseline.
- `earnings_transcripts_presentations`: transcripts, presentations, events, and recent management commentary needed for question planning.
- `internal_research`: internal notes, expert context, and team discussions when they materially improve the meeting plan.
- `portfolio_models_trackers`: portfolio context, watchlists, models, and thesis trackers only when they materially change the investor stance or follow-up.
- `market_data_estimates`: market data, consensus, estimates, and ownership only when they materially change the investor stance or questions.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Internal Research`
- `Company Filings & IR`
- `Earnings Transcripts & Events`
- `Portfolio Models & Trackers`
- `Market Data & Estimates`

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For a substantive reusable meeting-prep packet or explicit HTML meeting brief, the default resolves the presentation surface to a polished standalone HTML live-meeting brief unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In interactive runs, ask only remaining material choices such as depth, audience/use, meeting type, or focus; in non-interactive runs, default to the HTML live-meeting brief and `Full working analysis` while disclosing those assumptions outside the artifact. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Mission

Create decision-useful Public Equity Investing meeting readiness: what to ask first, what to listen for, how to follow up if the answer is evasive, what not to say, what evidence to request, what decisions to drive, and what follow-ups to send. For a live meeting, the prep sheet is a conversation tool, not a general research report.

Default prep bundle:

1. meeting objective, investor stance, and compact verified baseline;
2. conversation flow: opening frame, lead question, pressure-test, and close;
3. three or four must-ask questions ranked by decision impact, with listen-fors and evasive-answer follow-ups;
4. compact must-know context, time-permitting questions, and evidence requests;
5. likely pushbacks, compliance boundaries, and what not to ask or say;
6. follow-up/action tracker;
7. source log and material open gaps.

Preserve existing briefs, decks, memos, spreadsheets, trackers, and notes. Add new outputs, comments, suggested edits, speaker notes, or change logs unless the user explicitly asks to modify the original.

Use chat for quick prep. For a substantive reusable prep packet or explicit HTML meeting brief, produce a polished standalone HTML live-meeting brief following `../../shared/html-artifact-standard.md`; let the meeting type and decision needed determine the hierarchy. Keep background research proportional to its utility in the conversation: do not turn meeting prep into an earnings deep dive, tearsheet, or initiation report merely because HTML space is available.

Use `dashboard-builder` only when the user explicitly asks for a standardized dashboard, reusable dashboard template, or structured payload-driven render. For that optional route, use `references/DASHBOARD_PACK.md`: `meeting-prep` owns the meeting objective, context, question sequencing, evidence requests, pushbacks, and follow-up logic; `dashboard-builder` owns the standardized shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown/CSV support files behind the HTML dashboard unless explicitly requested.

## Public Equity Investing Boundary

Use this skill for meetings tied to public securities, listed issuers, equity-risk credit signals, event-driven situations, sector research, PM/risk reviews, earnings, investor days, conferences, expert calls, and public-equity-investing client or committee discussions. Route credit-instrument, creditworthiness, covenant, recovery, restructuring, and debt-security meetings to Credit Markets.

Do not use this skill as the lead owner for private-markets diligence, investment-banking pitch or process meetings, corporate FP&A or operating-cadence meetings, legal/regulatory/contract meetings, or scheduling-only tasks.

If the user asks for those non-local workflows, route to the appropriate plugin/tool when available or state that the workflow is non-local to Public Equity Investing.

## Workflow

1. **Determine mode.** Build from scratch, refresh existing prep, turn analysis into call prep, prepare for a specific meeting, prepare follow-ups, or review/upgrade an existing prep packet.
2. **Infer audience and meeting type.** Management/IR, issuer, PM, client, committee, expert, earnings, investor day, credit, risk, portfolio review, model review, catalyst prep, or research kickoff. Load `references/meeting-type-playbooks.md` when needed.
3. **Build context pack.** Start with the prompt and active artifacts. Use runtime apps/connectors only when they are actually callable. Do not imply calendar, email, Slack, Drive, market-data, or research connectors are available if they are not.
4. **Handle sparse context.** With no context, produce starter prep plus data request list. With partial context, label assumptions and prioritize decision-changing gaps. With full context, produce tailored questions, evidence requests, likely responses, and follow-ups. Do not reproduce a long issuer or earnings background unless it changes the meeting plan.
5. **Compose with local skills.** Use source, tearsheet, memo, style, QC, scenario, audit, model, earnings, event, risk, hedge, thesis, or sector skills when meeting prep depends on their domain. Use Credit Markets as a handoff for credit-first meeting prep.
6. **Create brief.** State why the meeting matters now, what decision/information is needed, what is known/assumed, the must-ask questions in meeting order, what to listen for, what follow-up to use if an answer remains qualitative or evasive, evidence requests, pushbacks, and action items.
7. **Prepare follow-ups if post-meeting.** Capture decisions, new facts, changed assumptions, open questions, evidence requests, commitments, owners, dates, dependencies, and draft follow-up language if useful.

## First-Class Meeting Modes

Support these modes explicitly: `management_ir`, `expert_call`, `pm_internal_review`, `investment_committee`, `client_update`, `sell_side_call`, `earnings_call`, `investor_day`, `portfolio_watchlist_review`, `model_review`, `research_kickoff`, and `post_meeting_follow_up`.

For every mode, rank questions by decision impact, include what not to ask or say, identify evidence requests, anticipate likely pushbacks, and assign follow-up actions. For a finite live conversation, make three or four questions the must-ask set and place additional questions in an `If Time Permits` block. Tie every must-ask question to an estimate, valuation, thesis, catalyst, sizing, or monitoring consequence. The senior PM layer should press on what would change the view, what evidence is missing, what answer would be evasive, what the market already knows, and what should route to a model, memo, thesis tracker, sizing review, or Credit Markets handoff.

## HTML Guidance

For a substantive standalone HTML meeting brief, load `../../shared/html-artifact-standard.md` and apply these meeting-specific requirements:

- Make the live conversation plan the primary visual object. Lead with the meeting objective, one-sentence investor stance, core decision or information gap, and a compact disclosed baseline.
- Place a compact `Conversation Flow` block immediately after the opening stance/baseline and before detailed question cards or extended background. It should show the opening frame, lead question, pressure-test, and close/evidence request at a glance.
- For `management_ir`, `sell_side_call`, `expert_call`, `earnings_call`, or `investor_day`, display three or four must-ask questions after the conversation flow and before extended background. For each, show `Why it matters`, `Listen for`, `If evasive`, and `Model / thesis implication` or the closest decision consequence.
- Keep each must-ask subfield concise enough for live use: generally one short sentence, and no more than two short sentences where material nuance would otherwise be lost.
- Put secondary questions in a compact `If Time Permits` block. Do not render a long list of equally weighted question cards.
- Keep the disclosed baseline short: usually four or five facts or metrics that make the questions intelligible. Detailed historical tables, scenario work, and extended industry context belong only when they change a live question or follow-up.
- Include a usable conversation-flow block before detailed questions: opening frame, first question, productive follow-up if management remains qualitative, and closing evidence request or next public disclosure to monitor.
- Keep the compliance boundary visible for external meetings: public-disclosure-only posture, prohibited asks, and clean ways to restate questions without seeking material nonpublic information.
- Give the headline, stance box, baseline, and question plan distinct jobs. Do not repeat the same conclusion across several visible panels.
- Keep citations traceable but readable: do not fragment company names, product names, periods, dates, numeric ranges, or metric labels into separately linked tokens.
- Visually inspect local HTML via local headless-browser screenshots, not the in-app Browser plugin, and iterate on hierarchy, density, clipping, citation rendering, and whether the must-ask questions are quickly usable in a live meeting.

## When To Invoke Support

Load `shared/support-layer-routing-contract.md` when support services are needed. Use `financial-source-of-truth` for verified facts, claims, citations, and source gaps; use `company-tearsheet`, `financials-normalizer`, or `excel-data-cleaner` for issuer/table prep; use `deck-report-qc` for pre-read/circulation review; use `style-guide-adapter` only after substantive prep is locked. Support artifacts stay secondary to the live-meeting brief or optional standardized dashboard.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: source pack, company and market context, key questions, risk flags, and follow-up tracker. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Quality Bar

The objective is explicit, the brief is usable during the meeting, facts and assumptions are separated, material source gaps are visible, must-ask questions are sequenced by decision impact, evasive-answer follow-ups and decision consequences are clear, evidence requests are specific, likely objections are covered, action items have owner/timing where available, and no source artifact is modified or deleted without permission.

## Reference Map

- `references/context-and-sources.md`: source hierarchy and optional connector behavior. Treat connectors as optional runtime inputs.
- `references/meeting-type-playbooks.md`: persona and meeting-type modules.
- `references/question-and-evidence-bank.md`: question and evidence-request patterns.
- `references/follow-up-and-action-tracking.md`: debrief and tracker fields.
- `references/output-templates.md`: standard brief formats.
- `references/safety-and-integrations.md`: non-destructive editing and circulation rules.
