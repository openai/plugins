---
name: event-driven-analyzer
description: Use when analyzing dated public-equity event paths, probabilities, payoffs, and expected returns. Do not use for generic catalyst lists, risk sizing, hedges, capital structure, covenants, or credit recovery.
---

# Event Driven Analyzer

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the categories needed for this workflow: `company_filings_ir`, `earnings_transcripts_presentations`, `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`. Use the shared runtime contract to map each attempted category to an available app, connector, file, export, or user-provided input.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Market Data & Estimates`
- `Company Filings & IR`
- `Earnings Transcripts & Events`
- `Internal Research`

## Internal Support

When this workflow needs rendering, evidence/data preparation, style, or sector context, route support through the visible `public-equity-investing` router and its bundled internal playbooks. Route workbook or model QA through the visible `model-audit-tieout` workflow.

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For an explicit full event analysis, full report, or reusable/source-heavy special-situations package, the default resolves the presentation surface to a polished standalone HTML event report unless the user requests an alternate surface, a quick/no-file answer, or model/math output. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus; in non-interactive runs, default to the HTML event report and `Full working analysis` while disclosing those assumptions outside the artifact. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Purpose

Convert a public-equity catalyst into a path-dependent underwriting view:

`event -> conditions -> timing -> scenarios -> payoffs -> probabilities -> expected return -> trade expression -> monitoring plan`

This skill owns event-driven analysis for mergers, spins, split-offs, activism, regulatory/litigation events, tenders, index events, rights offerings, lockups, de-SPACs, stubs, warrants, preferreds, and other dated public special situations.

Ownership boundary: this skill owns dated public-equity event paths, probability trees, payoff math, expected value, timing, trade expression, and monitoring. Use Credit Markets for credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis. If a distressed or restructuring event needs both, this skill can own the equity event path while Credit Markets supplies capital-structure, covenant, and recovery inputs.

## Do Not Use

- General long/short thesis without a controlling event: use `long-short-pitch`.
- Calendar/watchlist without underwriting: use `catalyst-calendar`.
- Credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, debt security selection, capital structure, priority, liquidity, fulcrum, or recovery waterfall work: use Credit Markets.
- Portfolio exposure, hedge, or sizing work: use `portfolio-risk-management`.
- Macro/rates/FX/commodity transmission map: use `economic-impact-report`.
- Ongoing thesis monitoring after underwriting: use `thesis-tracker`.

## Required Posture

- Do not invent an event. If no company/security/event is supplied and no active event is found, return an intake request or event-scan framing.
- Timestamp market-sensitive facts: price, spread, borrow, bond/loan level, option price, regulatory status, and court date.
- Prioritize primary documents over press commentary: merger agreements, 8-Ks, S-4/F-4, proxies, Schedule TO/14D-9, Form 10s, 13D/Gs, indentures, court/regulator records, and company releases.
- Separate `Fact`, `Assumption`, and `Judgment` for important inputs.
- Scenario probabilities must sum to 100% before presenting probability-weighted conclusions.
- Calibrate recommendation language to evidence stage. Without timestamped pricing and execution inputs required for the proposed expression, such as price/volume, spread, borrow, liquidity, when-issued trading, index treatment, or hedge inputs, present an underwriting framework or entry screen and use `Wait`, `Monitor`, or `Diligence to initiate` rather than an executable `Buy`, `Own`, or `Initiate` headline.
- If possible MNPI is supplied, do not recommend a trade from it; flag compliance/legal review.

## Workflow

1. **Classify the event and security.** Identify event type, sub-type, right security or spread expression, and whether a playbook reference is needed.
2. **Build the fact pack.** Capture parties, terms, current price, unaffected price, timing, outside date, approvals, conditions, litigation/regulatory posture, borrow/liquidity, and sources.
3. **Build the timeline.** Separate known dates from estimated windows and highlight the next real catalyst.
4. **Compute market pricing when supportable.** Use gross spread, annualized spread, market-implied probability, downside/break price, borrow/financing/dividend adjustments, hedge ratio, and expected return only where source-backed inputs exist. Otherwise state the missing trade-ready inputs and build an entry screen or gating-items view.
5. **Define terminal cases.** Use unaffected, peer-adjusted unaffected, standalone value, litigation/regulatory outcomes, SOTP, or Credit Markets-supplied recovery values only when the final question is a listed-equity event view.
6. **Build a supported event path.** Use a scenario tree with probability, timing, terminal value, return, rationale, and signposts only when the necessary inputs are supportable. Otherwise show mechanics, valuation screens, gating evidence, and the inputs needed for trade readiness without false precision.
7. **Identify gating items.** Name the controller, evidence, next signpost, and action threshold.
8. **Recommend expression and monitoring.** State buy/avoid/watch, implementation, sizing caveats, review thresholds, and monitoring plan.
9. **Red-team.** Explain how the trade loses money, what the market may know, what is stale/missing, and what changes the recommendation.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: fact timeline, market pricing, regulatory/legal conditions, probability/payoff math, trade expression, and red-team review. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Output Modes

- **Full event report:** default analytical route for broad or substantial reusable event-driven requests, especially those with many dates, sources, or tables. For an explicit full event analysis, full report, or reusable/source-heavy special-situations package, produce a polished standalone HTML event report following `../../shared/html-artifact-standard.md`; let the event type determine the report structure. Include event mechanics, evidence-backed valuation or pricing where available, trade or entry posture, monitoring, red team, open questions, and sources.
- **Standardized dashboard:** use only when the user explicitly asks for a standardized dashboard, reusable dashboard template, or structured payload-driven render. For that path, use `references/DASHBOARD_PACK.md`: `event-driven-analyzer` owns the event facts, supported scenario math, timing, probability/payoff view, trade construction, and monitoring judgment; `dashboard-builder` owns the shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown/CSV support files behind the HTML dashboard unless explicitly requested.
- **Explicit quick PM read:** use only when the user explicitly asks for quick, short, summary, one-page, brief, or TL;DR. Include recommendation, setup, pricing, implied probability, gating item, downside, expected return, next catalyst, and kill criteria.
- **Model/math mode:** deterministic spread, annualized return, implied probability, hedge ratio, CVR/spin/scenario EV, dated event probability, and payoff math. Use `scripts/event_math.py` with `references/event-math-schema.md`; use Credit Markets for capital structure, covenant, debt-security, and recovery math.
- **Red-team mode:** attack downside, probabilities, gate risk, source quality, timing, crowding, liquidity, borrow, and sizing.
- **Monitoring/update mode:** state what changed and whether probability, sizing, or recommendation changes.

Do not use quick mode just because context is sparse. Sparse context should produce a full screen-grade event report with source gaps, assumptions, and missing inputs.

## HTML Guidance

For a substantive HTML full event report, load `../../shared/html-artifact-standard.md` and use these event-specific requirements:

- Lead with a recommendation headline calibrated to the evidence stage, a decision/action-posture box, three to five event-specific evidence tiles, and the event type's primary analytical object.
- If required pricing or execution inputs are missing, make visible that the report is an underwriting framework or entry screen, name the evidence needed for an actionable recommendation, and do not make the title more actionable than the evidence.
- For a spin-off or split-off, lead with distribution mechanics and hard dates; a value-allocation bridge that keeps distributed stake, retained stake, and cash/debt transfer separate; SpinCo and RemainCo starting points; confirmed evidence versus the technical-supply thesis; and the entry screen, expression, monitoring, and red-team case.
- For merger arbitrage or tender work, lead with spread, downside, implied probability, and scenario tree only when sourced inputs support them. For litigation or regulatory work, lead with procedural path, remedy risk, and payoff implications. For flow or technical events, lead with confirmed flow mechanics, liquidity, execution evidence, and exit path.
- Keep `Fact`, `Assumption`, `Derived Calculation`, and `PM Judgment` visibly distinct.
- Include probability-weighted scenarios, expected-return math, and trade-execution modules only when inputs are sourced and supportable; otherwise replace them with event mechanics, valuation screens, evidence gaps, and gating inputs.
- Visually inspect the HTML according to the shared artifact standard before delivery and iterate on hierarchy, legibility, clipping, crowding, and decision clarity.

## Deterministic Helper

Run event math when the user provides structured inputs:

```bash
python scripts/event_math.py --mode cash_merger --input path/to/input.json --pretty
python scripts/event_math.py --mode scenario_ev --input path/to/input.json --pretty
python scripts/event_math.py --mode scenario_ev --input path/to/input.json --allow-probability-sum-mismatch --pretty
```

The helper performs repeatable math only. It does not fetch prices, verify terms, assign legal/regulatory probabilities, or replace PM judgment.
For `scenario_ev`, probabilities must sum to 1.0 by default. A mismatch hard-fails unless `--allow-probability-sum-mismatch` is passed for diagnostic, non-memo-ready output.

## Reference Map

- `references/event_taxonomy.md`: event labels and routing.
- `references/source_hierarchy.md`: source hierarchy by event type.
- `references/scenario_math.md`: spread, probability, annualization, EV, and hedge math.
- `references/event-math-schema.md`: deterministic helper input contract.
- `references/merger_arb_playbook.md`: mergers, tenders, collars, CVRs, deal breaks.
- `references/spins_activism_playbook.md`: spins, split-offs, activism, proxy fights.
- `references/litigation_regulatory_playbook.md`: court, agency, antitrust, CFIUS, IP, settlement.
- `references/restructuring_special_situations_playbook.md`: distressed, exchange offers, bankruptcy, technical events.
- `references/output_templates.md`: memo and dashboard templates.
- `references/quality_checks.md`: final QA.

## Final QA

Before finalizing, confirm event/security clarity, timestamped market data or caveat, fact/assumption/judgment split, primary-source priority, probabilities summing to 100%, explicit downside methodology, specific gating item, actionable monitoring plan, and a red-team section.

## Public Equity PM Judgment Layer

For substantial event work, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

Index / ETF / Passive Flow Event analysis is an explicit event-driven equity path.

Required PM judgment:
- State whether the edge is underwriting, timing, flow, legal/process, or mispriced optionality.
- Include base-rate awareness: what usually happens in this event class and what makes this case different.
- Include trade expression menu: common equity, pair, spread, options, stub, when-issued, rights, warrants, basket hedge, or avoid.
- Require path risk: mark-to-market pain, liquidity, borrow, crowding, event delay, financing cost, and exit liquidity.
- For flow events, include flow-vs-ADV, price/volume timestamp, float, market cap, borrow, ETF/index AUM assumptions, and exit plan.
