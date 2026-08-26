---
name: economic-impact-report
description: Use when translating a specific event, policy change, macro shock, or industry development into public-equity issuer, sector, earnings, valuation, positioning, and portfolio implications. Do not use for standalone macro strategy, rates, FX, credit, futures, or generic market commentary.
---

# Economic Impact Report

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the categories needed for this workflow: `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`. Use the shared runtime contract to map each attempted category to an available app, connector, file, export, or user-provided input.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Market Data & Estimates`
- `Company Filings & IR`
- `Internal Research`

## Internal Support

When this workflow needs rendering, evidence/data preparation, style, or sector context, route support through the visible `public-equity-investing` router and its bundled internal playbooks. Route workbook or model QA through the visible `model-audit-tieout` workflow.

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For a substantive reusable economic-impact report or explicit HTML public-equity shock analysis, the default resolves the presentation surface to a polished standalone HTML economic-impact report unless the user requests an alternate surface, a quick/no-file answer, or a standardized dashboard. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus; in non-interactive runs, default to the HTML economic-impact report and `Full working analysis` while disclosing those assumptions outside the artifact. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Goal

Produce a decision-grade public-equity economic impact report. This is not a news summary and not a generic cross-asset macro note; it should tell a senior public-equity investor what changed, why it matters for listed equities, what reprices first, what is still uncertain, and which issuers, sectors, estimates, valuation debates, positioning risks, and portfolio actions matter most.

Default to a full decision-grade economic impact report unless the user explicitly asks for a summary, quick read, one-pager, brief, TL;DR, or another compressed format. For a substantial reusable report or explicit HTML public-equity shock analysis, produce a polished standalone HTML economic-impact report following `../../shared/html-artifact-standard.md`; chat-only is appropriate for narrow or explicitly quick reads.

## Use When

Use this skill when the user asks for:

- economic or market impact of a specific event
- first-, second-, third-, or fourth-order implications
- transmission map from shock to consequence
- winners and losers with mechanisms
- public-equity implications from rates, FX, options, futures, commodities, credit, policy, geopolitics, labor, supply-chain, demand, or regulatory shocks
- scenario analysis, catalysts, monitoring signals, or "what would change the view"
- a senior public-equity investor memo on policy, macro, regulatory, geopolitical, supply, credit-signal, commodity, industry, or earnings shocks

Do not use for:

- pure article summaries with no impact question
- generic macro explainers with no event or catalyst
- narrow workflows that need another local skill first, such as DCF, earnings deep dive, catalyst calendar, or spreadsheet cleanup
- one-line market color where a causal map is overkill
- standalone macro, rates, FX, futures, options, commodities, or credit strategy without a listed-equity issuer/sector/portfolio decision; route out
- standalone macro strategy, rates strategy, FX strategy, futures curve work, options-volatility trade construction, credit-security relative value, or debt-security selection; route those to the appropriate plugin, with Credit Markets owning credit instruments

## Non-Negotiables

- Bottom line first.
- Separate fact, inference, assumption, and scenario.
- Separate direct effects from higher-order effects.
- Separate immediate listed-equity implications, medium-term earnings/estimate implications, valuation/multiple implications, positioning/flow implications, and structural consequences.
- Every major claim must tie to a transmission channel.
- Every named issuer, sector, country, commodity, rate, currency, credit signal, or asset-class input must connect to a public-equity mechanism.
- Quantify whenever a reasonable range is possible.
- Distinguish what is genuinely new from stale reporting or prior expectations.
- Distinguish what is likely priced from what may still be mispriced.
- Address the strongest counterargument.
- End with scenarios, monitoring signals, falsifiers, and the public-equity action posture: `add`, `press`, `hold`, `trim`, `exit`, `hedge`, `watchlist`, `pass`, `wait for proof`, or `re-underwrite`.
- If current facts matter, verify dates, timestamps, and latest state before analyzing. Distinguish reported events from confirmed facts, and distinguish spot, futures, closing, and intraday commodity or market observations.

## Causal Spine

Use this full sequence:

1. Event and baseline.
2. What is new.
3. Transmission channels.
4. First variables likely to reprice.
5. Direct winners/losers.
6. Higher-order consequences.
7. Scenarios, catalysts, public-equity expression, and portfolio action.

If you cannot name the channel, do more source work before writing. Load `references/impact-framework.md` for timing, directness, confidence, domain, and quantification rules.

## Workflow

1. Define the event precisely, state its evidence status and market-data cut-off, and name the public-equity decision it could change.
2. Identify what changed versus consensus/baseline and what listed equities already appear to discount.
3. Draft the transmission map before broad research, ending every channel in issuer, sector, earnings, valuation, positioning, or portfolio implications.
4. Write the key hypotheses, confirmers, and falsifiers.
5. Gather evidence, prioritizing primary sources and recency.
6. Rank impacts by sign, magnitude, timing, confidence, and directness. Group representative issuer or sector candidates only when they share the same transmission channel, first affected line item, and directional read-through; split rows when the economics differ.
7. Identify what is priced and what may still be mispriced in the affected equities, peer group, sector, index, or factor exposure. Ground priced-in conclusions primarily in affected issuer/sector price action, revisions or valuation movement, or the relevant transmission market; use broad-index performance as context only.
8. Build base/upside/downside scenarios.
9. Write the strongest counterargument.
10. End with monitoring, falsifiers, and what would change portfolio action.

Use `references/workflow.md` for full-form reports.

## No Portfolio / Watchlist Fallback

If the user does not provide a portfolio, position list, thesis, benchmark, or watchlist, do not stall and do not invent holdings. Build a general public-equity exposure map:

- industries and sub-industries most exposed;
- countries, currencies, and geographic revenue/cost exposures;
- public companies and relevant private companies with public-equity read-throughs;
- commodities, rates, FX, credit-spread, volatility, or demand variables that transmit into equity estimates or multiples;
- likely beneficiaries, losers, second-order peers, suppliers, customers, and crowded expressions;
- a research queue using `watchlist`, `wait for proof`, `pass`, or `re-underwrite` rather than portfolio-specific add/trim/exit language.

Portfolio-specific action should be labeled `not available without holdings / active weights / mandate`. The report must still terminate in issuer impact, sector/peer impact, earnings or estimate path, valuation/multiple impact, positioning/flow impact, and next Public Equity Investing workflow.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: event verification, issuer/sector exposure, earnings and valuation read-through, positioning/flow impact, scenarios, and counterarguments. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.

## Output Modes

- **Full economic-impact report:** default analytical route for broad or substantial reusable public-equity impact requests, especially those with many issuers, scenarios, sources, or monitoring items. For a substantive reusable economic-impact report or explicit HTML public-equity shock analysis, produce a polished standalone HTML economic-impact report following `../../shared/html-artifact-standard.md`; let the event and equity transmission channels determine the report structure.
- **Standardized dashboard:** use only when the user explicitly asks for a standardized dashboard, reusable dashboard template, or structured payload-driven render. For that path, use `references/DASHBOARD_PACK.md`: `economic-impact-report` owns the public-equity transmission logic, scenario analysis, issuer/sector exposure map, earnings and valuation read-through, positioning implications, and portfolio watch items; `dashboard-builder` owns the shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown/CSV support files behind the HTML dashboard unless explicitly requested.
- **Explicit quick PM read:** use only when the user explicitly asks for quick, short, summary, one-page, brief, or TL;DR. Include event status, public-equity bottom line, primary transmission channel, most affected listed exposures, what is priced, what needs proof, and next monitor.


## Output Contract

Unless the user explicitly asks for a shorter or narrower format, produce the full report. The first 150 to 250 words should stand alone as an executive summary, but the rest of the report should still include the full causal map and investment implications.

Minimum sections:

- `Executive Call`
- `Event Status And Market Baseline`
- `Source And Freshness`
- `What Is New Vs. Expected`
- `Event-To-Equity Transmission Map`
- `Public Equity Framing`
- `Ranked Equity Impact Map` / `Issuer And Sector Impact` with issuer and sector exposure candidates
- `What Is Priced In Vs. What Requires Proof`
- `Earnings, Valuation, And Positioning Read-Through`
- `Scenario Matrix`
- `Monitoring Triggers And Research Queue`
- `Bottom-Line Judgment`

Use `references/report-template.md` for the full structure, `references/domain-checklists.md` for domain-specific checks, and `references/quality-bar.md` before final delivery.

For Markdown draft/support outputs explicitly requested by the user or used as renderer input, run `scripts/check_economic_impact_report.py <support_note.md>` when practical. The checker validates required sections, source/freshness posture, and unresolved placeholders; it is a QA guardrail, not a replacement for source work. Markdown files should not be the lead user-facing artifact when an HTML report is expected.

Use draft mode while iterating and delivery mode before circulating or sending a final file:

```bash
python scripts/check_economic_impact_report.py --mode draft path/to/support_note.md
python scripts/check_economic_impact_report.py --mode delivery path/to/support_note.md
```

`--mode delivery` is the default and must fail if the report is missing a dedicated `Source And Freshness` section, lacks a data cut-off/as-of date, lacks sources used, omits the stale/missing-data assessment, or discloses stale, missing, unknown, unsupported, or weak evidence for load-bearing claims. `--mode draft` surfaces the same source/freshness issues as warnings so the report can remain a work in progress.

## HTML Guidance

For a substantive standalone HTML economic-impact report, load `../../shared/html-artifact-standard.md` and use these workflow-specific requirements:

- Front-load an investor conclusion and an `Event Status And Market Baseline` block stating what is verified, what is reported or assumed, the as-of timestamp, relevant market benchmark, and material gaps. When material intraday observations inform the view, state an exact research cut-off time and time zone. For commodity shocks, distinguish benchmark, spot versus futures, contract/month when relevant, intraday versus close, and source timestamp.
- Make the `Event-To-Equity Transmission Map` the primary analytical object: event or shock -> channel -> first variable -> issuer/sector driver -> financial line item -> public-equity action or monitoring implication.
- Follow it with a `Ranked Equity Impact Map` that separates direct beneficiaries/losers from conditional and higher-order expressions. Combine exposures in one row only when their transmission channel, first affected line item, and directional read-through match; otherwise split them even if they are thematically adjacent. When company-specific work has not been completed, label named issuers as representative exposure candidates or a research queue, not investment conclusions.
- Include `What Is Priced In Vs. What Requires Proof` before the detailed scenario and monitoring material. Ground priced-in claims primarily in evidence from affected equities or sectors, estimate revisions, valuation movement, or transmission-market indicators such as commodity curves, product spreads, or freight; broad-index performance is supporting context, not primary proof. Keep immediate market impact separate from estimate revisions, multiple effects, positioning/flow risk, and structural implications.
- Use visible fact/inference/scenario distinctions where a reader could otherwise confuse a reported event, an assumed shock, a market observation, and PM judgment.
- Cite load-bearing figures, dated facts, and consequential disputed claims near use; use compact section-level source notes when several adjacent claims share sources. Do not repeat citation chips through every cell, monitoring row, or conclusion when they compete with the analysis.
- If no portfolio was supplied, keep the visible action posture to `watchlist`, `wait for proof`, `pass`, or `re-underwrite` and state what evidence would convert the screen into portfolio action.
- Visually inspect the HTML according to the shared artifact standard before delivery and iterate on hierarchy, legibility, clipping, table density, citation noise, and whether the transmission decision is immediately visible.

## Edge Cases

- If the event is underspecified but analyzable, state your interpretation and proceed.
- If the user provides only an article/headline, extract the surprise, baseline, and causal map.
- If a domain is not materially affected, say `not material`.
- If current facts or market moves are uncertain, verify before claiming a view.
- If the event looks dramatic but economically minor, say so clearly.
- If the effect is mostly expected or priced, say so clearly.
- If the cleanest expression is not equities, say so, but do not turn this skill into the non-equity trade-construction owner.

## Reference Map

- `references/impact-framework.md`: timing, directness, confidence, transmission channels, quantification, and domain checks.
- `references/workflow.md`: full workflow and failure modes.
- `references/report-template.md`: full report template.
- `references/domain-checklists.md`: public companies, industries, countries, rates, options, futures, and cross-asset checks.
- `references/quality-bar.md`: final quality bar.
