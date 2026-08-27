---
name: idea-generation
description: Use when triaging public-equity idea candidates. Do not use for final trade recommendations, pitches, memos, or models.
---

# Idea Generation For Public Equity Investing

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the categories needed for this workflow: `company_filings_ir`, `earnings_transcripts_presentations`, `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`. Use the shared runtime contract to map each attempted category to an available app, connector, file, export, or user-provided input.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Market Data & Estimates`
- `Company Filings & IR`
- `Internal Research`

## Internal Support

When this workflow needs rendering, evidence/data preparation, style, or sector context, route support through the visible `public-equity-investing` router and its bundled internal playbooks. Route workbook or model QA through the visible `model-audit-tieout` workflow.

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For a substantive idea screen, market map, watchlist review, or reusable/source-heavy candidate set, the default resolves the presentation surface to a polished standalone HTML idea-triage report unless the user requests another surface, a quick/no-file answer, or workbook/tracker output. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus; in non-interactive runs, default to the HTML idea-triage report and `Full working analysis` and disclose those assumptions outside the artifact. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Purpose

Triage public-equity idea candidates and screen outputs into research-worthy longs, shorts, pairs, catalysts, relative-value ideas, watchlist items, and rejected false positives. This is a PM-style research-prioritization skill, not a final recommendation engine.

A strong output explains why a security surfaced now, possible variant perception, what is priced in, what would make it investable, first rejection risk, and the next workflow.

Use chat for quick triage. For a substantial reusable screen, market map, watchlist review, or source-heavy candidate set, produce a polished standalone HTML idea-triage report following `../../shared/html-artifact-standard.md`; let the mandate and screening question determine the structure. Use `dashboard-builder` only when the user explicitly asks for a standardized dashboard, reusable dashboard template, or structured payload-driven render.

## Operating Rules

- Never present a screen result as a final recommendation.
- Label outputs as idea candidates, watchlist items, deeper-research candidates, or rejected false positives.
- Preserve user portfolios, watchlists, models, notes, and spreadsheets; add outputs rather than overwriting source work.
- Use prompt/connected/user files first, primary sources next, market/consensus data next, and web fallback only when current public data is needed.
- Do not fabricate unavailable market data or metrics.
- Use `crowded` only when supported by positioning, ownership, flow, short-interest, or comparably direct evidence. If the evidence is limited to price appreciation, narrative visibility, or simple valuation, use `expectations-heavy`, `valuation-gated`, or `crowding-risk candidate`.
- Do not advance a candidate solely because the stock rallied after a thematic catalyst or management mentioned the theme. For an advanced name, show a source-backed link from the driver to orders, backlog, revenue, margins, or estimate revisions; otherwise label it `needs exposure attribution`.

## Workflow

1. **Assess context.** With no context, use liquid public-equity defaults and state assumptions. With partial context, infer mandate/style and label assumptions. With rich context, treat provided portfolios, screens, notes, files, or connected data as primary evidence.
2. **Set mandate and universe.** Identify long-only, long/short, market-neutral, event, credit, region, sector, cap size, liquidity, benchmark, horizon, and allowed instruments.
3. **Normalize candidates.** Resolve tickers, ADRs, share classes, currencies, fiscal calendars, sectors, liquidity, benchmark membership, and portfolio/watchlist overlap.
4. **Screen by archetype and beneficiary pathway.** Use long, short, pair, relative value, catalyst, and watchlist archetypes rather than one generic rank. For thematic screens, map candidates by beneficiary pathway before ranking, such as electrical/power distribution, construction, networking, cooling, grid/generation, or colocation/real estate.
5. **Score if structured data exists.** Use `scripts/score_ideas.py` only for user-provided candidate rows and scoring fields.
6. **Apply PM triage.** Test denominator quality, estimate credibility, catalyst path, valuation support, risk compensation, verified positioning versus inferred expectations risk, liquidity, and false-positive risk.
7. **Output priorities and routing.** Lead with a candidate funnel and route candidates to model update, earnings, pitch, thesis tracker, hedge, event, credit, macro, scenario, memo, or QC workflows as appropriate.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: screen construction, source QC, variant view, catalyst path, risk flags, and prioritization. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Deterministic Scoring Helper

```bash
python scripts/score_ideas.py candidates.csv --output-dir output
```

The helper materializes supplied scores into ranked support outputs and warnings. It does not create proprietary market data or replace PM judgment. If no numeric score fields are supplied, treat output as qualitative triage.

For standardized dashboard handoffs only, use `references/DASHBOARD_PACK.md`. `idea-generation` owns candidate triage, screen interpretation, and workflow routing; `dashboard-builder` owns the shared shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown/CSV support files behind the HTML artifact unless explicitly requested.

## Output Contract

Default output:

- scope and assumptions;
- methodology and data/source caveats;
- headline research-priority conclusion and candidate funnel;
- beneficiary-pathway map when relevant to a thematic screen;
- ranked idea table with exposure proof and expectations risk;
- PM-style idea cards for highest-priority names;
- rejected/deprioritized false positives;
- cross-idea themes and risk observations;
- next research step for each important candidate;
- downstream routing.

Ranking buckets: `A - immediate research candidate`, `B - watchlist / needs trigger`, `C - screen flag only`, and `Reject`.

For thematic or source-heavy idea screens, express the funnel as `Advance to deeper work`, `Valuation / expectations gated`, `Exposure not yet proven`, and `Deprioritized or reject`. Make clear that `Advance to deeper work` is a research-priority status, not an investment recommendation, approved position, or attractive entry point; an advanced candidate may still be valuation-gated or entry-gated. A candidate without a quantified or source-backed link to the theme stays in `Exposure not yet proven` and is labeled `needs exposure attribution`.

## HTML Guidance

For a substantive HTML idea-triage report, load `../../shared/html-artifact-standard.md` and apply these workflow-specific rules:

- Lead with the research-priority conclusion and candidate funnel; make the funnel or an exposure-versus-expectations matrix the primary visual object.
- Use three to five first-read tiles only when each has a distinct job, such as universe size, advance count, valuation-gated count, unproven-exposure count, or the most important evidence gap.
- Keep methodology and evidence-posture commentary compact or place it below the candidate funnel when it would otherwise delay the primary research-prioritization visual.
- Put the ranked candidate board near the top. For thematic screens, organize candidates by beneficiary pathway before or alongside rank.
- Show `Exposure proof`, `Expectations risk`, `First rejection`, and `Next workflow` in the table or visible candidate summaries. Reserve longer idea cards for the highest-priority names.
- Distinguish verified positioning from inferred crowding risk; do not make the headline or status label more certain than the evidence.
- Keep citations traceable but readable: do not fragment years, ticker symbols, ranges, product names, or guidance values into separately linked tokens, and avoid an oversized citation run in the hero.
- Visually inspect local HTML via local headless-browser screenshots, not the in-app Browser plugin, and iterate on legibility, hierarchy, clipping, citation rendering, and whitespace before delivery.

## Reference Map

- `references/source-qc.md`: source hierarchy, stale data, citations, data caveats.
- `references/workflow.md`: full workflow and context adaptation.
- `references/screen-archetypes.md`: long, short, pair, catalyst, and watchlist archetypes.
- `references/sector-overlays.md`: sector metrics and traps.
- `references/output-standards.md`: report and idea-card templates.
- `references/downstream-routing.md`: local handoff patterns.
- `references/scoring-materializer.md`: deterministic scoring contract.

## Public Equity PM Judgment Layer

For substantial screens or idea queues, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

Every top idea must include `Actionability`, `Variant Wedge`, `Why Now`, `First Rejection`, `What Would Make It Investable`, `What Would Kill It`, and `Next Workflow`.

Required PM judgment:
- Long-only: benchmark fit, active share, quality durability, downside versus benchmark, liquidity, and add/trim path.
- Long/short hedge fund: catalyst path, shortability, borrow, gross/net impact, factor crowding, and cover discipline.
- Sell-side: rating-change potential, estimate revisions, target-price debate, client relevance, and risk-to-rating.
- ETF/index: index methodology, constituent weight, rebalance effects, liquidity, passive-flow relevance, and factor exposure.
- Public equity diligence: source pack completeness, thesis readiness, diligence queue, and next evidence needed.
