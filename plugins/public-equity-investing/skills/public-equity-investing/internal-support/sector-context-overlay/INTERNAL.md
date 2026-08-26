---
name: sector-context-overlay
description: Use when public-equity-investing work needs sector-specific KPIs, modeling rules, valuation conventions, or red-flag checks. Do not use as the primary owner for earnings, models, memos, pitches, equity events, or risk artifacts.
---

# Sector Context Overlay

> Internal support playbook. Load through `internal-support/policy.md`; this context overlay is bundled with the visible router rather than exposed as a skill entrypoint.

## Deliverable Intake

This overlay does not own a hero deliverable. Inherit the owning workflow's resolved deliverable preferences and do not call `request_user_input` independently.

Use this as a Public Equity Investing context layer, not as a standalone artifact engine. It preserves sector-specific judgment while keeping the primary deliverable owned by the relevant local skill. It must never fail just because a prompt is sparse, cross-sector, or attached to a stale legacy sector label.

## Use When

Use when a public issuer, security, sector screen, model, earnings note, investment memo, long/short pitch, catalyst review, credit analysis, or risk output needs one of the supported sector lenses.

Supported sector lenses:

- `banks`
- `biotech-pharma`
- `consumer-internet-marketplaces`
- `exchanges-market-infrastructure`
- `insurance`
- `oil-gas-ep`
- `reits`
- `saas-subscription-software`

## Do Not Use For

Do not use as the primary owner for DCFs, three-statement models, comps, earnings previews, earnings deep dives, memos, long/short pitches, event math, credit recovery, catalyst calendars, hedge work, or deck/report QC. Route those artifacts to the owning skill and load this skill only for sector context.

Do not force a sector lens when the issuer belongs to an unsupported sector. Use the core Public Equity Investing skill and state that no local sector overlay is installed.

When sector labels conflict with business-model evidence, business-model economics win. Example: Snowflake, Rapid7, Cloudflare, and cybersecurity/data-platform prompts use `saas-subscription-software`, not a stale legacy REIT/biotech label.

## Workflow

1. Identify the primary artifact owner first: `earnings-preview`, `earnings-deep-dive`, `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `equity-model-update`, `company-tearsheet`, `initiating-coverage`, `memo-builder`, `long-short-pitch`, `event-driven-analyzer`, Credit Markets, `portfolio-risk-management`, or `deck-report-qc`.
2. Identify the applicable sector lens using `references/sector-index.md`.
3. If the issuer/sector is ambiguous, cross-sector, or legacy-labeled, run `scripts/resolve_sector_lens.py --prompt "<user request>"` and follow its primary lens, confidence, secondary lenses, and reference-file list.
4. Load only the relevant sector folder under `references/<sector>/`.
5. Load `archetypes.md` first when classification, peer set, or business-model diagnosis matters.
6. Load `kpi-cheat-sheet.md` for sector metric definitions, KPI tables, or measurement framework.
7. Load `modeling-rules.md`, `valuation-rules.md`, or `model-architecture.md` only for valuation, forecast, model update, sensitivity, security underwriting, or downside work.
8. Load `source-hierarchy.md` when sources conflict, provenance is thin, or diligence/source questions matter.
9. Load `references/pm-judgment-heuristics.md` and `references/research-output-overlay-contract.md` for substantial outputs.
9. Load `red-flags.md` before finalizing recommendations, trade conclusions, downside cases, or circulation-ready outputs.
10. Load `output-overlays.md` when adapting sector judgment into the owning skill's deliverable.

## Cross-Sector Guardrail

- If one supported sector clearly drives economics, use it as primary and mention secondary lenses only where they affect KPIs or risk.
- If two supported sectors both matter, choose the lens that drives valuation and forecast mechanics; add a short `Secondary Sector Checks` section.
- If no supported sector fits, do not improvise a fake overlay. Use the owning skill and state `No local sector overlay installed for this issuer`.
- Every routed overlay should still produce usable sector KPI guidance: selected lens, issuer archetype, first questions, KPI set, modeling/valuation conventions, red flags, and missing sources.

## Handoff Contract

Keep the primary deliverable with the owning skill:

- Research and earnings: `company-tearsheet`, `earnings-preview`, `earnings-deep-dive`, `initiating-coverage`, `meeting-prep`.
- Models and valuation: `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `equity-model-update`, `scenario-sensitivity-generator`.
- Written investment artifacts: `memo-builder`, `long-short-pitch`, `idea-generation`, `thesis-tracker`.
- Event and risk: `catalyst-calendar`, `event-driven-analyzer`, `portfolio-risk-management`. Use Credit Markets for credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis.
- Source, data, and circulation: `financial-source-of-truth`, `financials-normalizer`, `excel-data-cleaner`, `model-audit-tieout`, `deck-report-qc`, `style-guide-adapter`.

## Output Contract

Any output using this overlay should state:

- The primary owning skill.
- The selected sector lens and issuer archetype.
- The sector KPIs or modeling conventions that changed the analysis.
- The sector-specific valuation, forecast, downside, or source adjustments applied.
- The main red flags and diligence/source gaps.
- The sector reference files loaded, when useful for auditability.
- The mandate lens, PM debate, KPI hierarchy, valuation implications, benchmark/positioning relevance, disconfirmers, dashboard modules to add, and source gaps.
- Any secondary lenses considered and why they were not primary.

## Legacy Skill Name Mapping

If a user explicitly asks for a retired sector skill name, route it here:

- `bank-sector-analysis` -> `sector-context-overlay` with `banks`.
- `biotech-pharma-sector-analysis` -> `sector-context-overlay` with `biotech-pharma`.
- `consumer-internet-marketplaces-sector-analysis` -> `sector-context-overlay` with `consumer-internet-marketplaces`.
- `exchanges-market-infrastructure-sector-analysis` -> `sector-context-overlay` with `exchanges-market-infrastructure`.
- `insurance-sector-analysis` -> `sector-context-overlay` with `insurance`.
- `oil-gas-ep-sector-analysis` -> `sector-context-overlay` with `oil-gas-ep`.
- `reits-sector-analysis` -> `sector-context-overlay` with `reits`.
- `saas-subscription-software-sector-analysis` -> `sector-context-overlay` with `saas-subscription-software`.

## Public Equity PM Judgment Layer

For substantial sector overlays, load `shared/pm-judgment-heuristics.md` and `references/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

This skill should inject sector judgment into the owning skill, not produce a standalone sector explainer.

Required overlay fields: `sector_overlay.selected_lens`, `issuer_archetype`, `mandate_lens`, `pm_debate`, `kpi_set`, `valuation_implications`, `dashboard_modules_to_add`, `source_gaps`, `red_flags`, and `secondary_lenses`.
