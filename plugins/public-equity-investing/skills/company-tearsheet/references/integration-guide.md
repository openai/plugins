# Integration Guide

## Position in the shared-core stack
`company-tearsheet` is a baseline profile skill. It should be fast, cited, and compact. It should not duplicate deeper workflows.

Recommended order:
1. `financial-source-of-truth` for source routing and evidence hierarchy.
2. `financials-normalizer` or `excel-data-cleaner` if the underlying data is messy.
3. `company-tearsheet` to create the baseline profile.
4. Downstream role skill for analysis, modeling, memo, deck, or meeting prep.
5. `deck-report-qc` or `model-audit-tieout` for final QA where relevant.

## Handoff rules

### Public Equity Investing
- `earnings-preview`: use profile fields to frame company, segment/KPI context, and current debate.
- `earnings-deep-dive`: use profile if company context is missing before post-print analysis.
- `equity-model-update`: use only as context; model updates require normalized financial inputs.
- `long-short-pitch`: use as the factual baseline before thesis, variant perception, valuation, and risk/reward.
- `comps-valuation`, or `dcf-model-builder`: hand off only after key financial metrics are source-backed and normalized.
- Credit Markets: use for Credit Markets, distressed, maturity wall, liquidity, capital structure, or recovery questions.
- `event-driven-analyzer`: use when the company profile is a baseline for M&A, spin, activism, litigation, regulatory, restructuring, or other special situations.
- `economic-impact-report`: use only when macro, policy, commodity, FX, rate, or cross-asset context is needed; do not turn a company profile into macro analysis.
- `thesis-tracker` or `portfolio-risk-management`: use when the profile feeds ongoing monitoring, sizing, or hedge work.
- `memo-builder`, `meeting-prep`, or `deck-report-qc`: use when the profile becomes a memo, call prep, or circulated deck/report.

### Shared core
- `financial-source-of-truth`: apply source hierarchy, citations, stale-data checks, fact/assumption labels, and conflict handling.
- `financials-normalizer` or `excel-data-cleaner`: clean and normalize messy financial source data before the profile uses it.
- `model-audit-tieout`: audit model values before using them as profile facts.

## Boundary rules
- If the user asks "is this a good investment?", do not answer from the tearsheet alone; route to the relevant investing skill.
- If the user asks for a full Credit Markets or distressed memo, route to Credit Markets.
- If the user asks for a full model, route to model-building skills after profile creation.
- If the user asks for a meeting brief, use `meeting-prep` after the profile.
- If source financials are unstructured or inconsistent, normalize before using them.
