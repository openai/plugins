# Profile Templates

## Universal one-page tearsheet

```markdown
# [Entity] Tearsheet
**Profile type:** [public_company / equity_issuer_profile / public_sector_peer]
**As of:** [date/time]
**Scope:** [requested use case, periods, sources]
**Source caveat:** [latest / limited / stale / partial / source package only]

## One-line view
[One concise sentence explaining what the entity is and why it matters for the user's workflow.]

## Business snapshot
| Field | Detail | Source | Evidence | Confidence |
|---|---|---|---|---|
| Business model |  |  |  |  |
| HQ / footprint |  |  |  |  |
| Listing / identifiers |  |  |  |  |
| Segments / products |  |  |  |  |
| Customers / end markets |  |  |  |  |

## Key metrics
| Metric | Period | Value | Units | Source | Evidence | Confidence |
|---|---:|---:|---|---|---|---|

## Recent developments
- [Sourced bullet]
- [Sourced bullet]
- [Sourced bullet]

## Relevance for this workflow
- [Implication for public equity / earnings / valuation / meeting prep; route credit-first implications to Credit Markets]

## Risks, gaps, and evidence flags
- [Missing source, stale data, conflict, evidence request, or source-backed risk]

## Recommended next step
[Downstream skill or missing source needed.]
```

## Public company / equity profile

Prioritize:
- ticker, exchange, market cap, enterprise value, share price/date, fiscal year-end.
- revenue, EBITDA/operating income, EPS/FCF where relevant, margin, growth, net debt/leverage, segment mix.
- latest reporting event, guidance, consensus context if available, recent stock/credit move only if current.
- thesis-relevant debates, catalysts, and risks without making a recommendation.

Use when feeding `earnings-preview`, `earnings-deep-dive`, `equity-model-update`, `long-short-pitch`, `comps-valuation`, `dcf-model-builder`, or `memo-builder`.

## Standalone HTML tearsheet

When the user requests HTML or selects it during intake, produce a polished standalone HTML tearsheet following `../../../shared/html-artifact-standard.md`. Keep it a compact issuer baseline rather than a dashboard shell or initiation report.

Recommended first-read sequence:

1. Investor read: one factual sentence describing the earnings engine and the most important unresolved diligence question.
2. Metric strip: four or five sourced metrics that establish scale, profitability, valuation context, and balance-sheet or capital-allocation relevance.
3. Earnings drivers: a compact table or card row showing the few segments or KPIs that actually drive the long-only review.
4. Valuation context: trailing or derived multiples, forward consensus, or peers only to the extent sourced.
5. Catalysts and risks: a short matrix linked to the review question.
6. Evidence gaps and next route: only gaps that affect further work, plus a concise source ledger.

Use the visible heading `Trailing Valuation Snapshot` or `Valuation Context` when only historical figures or analyst-derived trailing multiples are available. Do not include `Debate` in the heading unless forward estimates, relevant peers, target-price evidence, or explicit market-expectation evidence is sourced.

When a current transaction, rumor, regulatory item, or other live event is material but not the requested focus, feature it in the investor read and catalysts/risks section and identify missing primary evidence in the evidence-gaps block. Do not repeat it through earnings drivers, valuation, and multiple summary panels unless it directly changes those analyses.

Visible evidence labels should be natural investor language:

| Internal support label | Reader-facing HTML label |
|---|---|
| `fact_source_reported` | Reported |
| `fact_provider_standardized` | Provider data |
| `derived_calculation` | Derived |
| `issuer_management_claim` | Management statement |
| `management_adjusted` | Company-defined |
| `missing_required_source` | Not yet sourced |

## Public issuer / credit profile

Prioritize:
- issuer, parent/guarantors if disclosed, ticker/CUSIP/ISIN when available, ratings, debt stack, maturity wall, instrument prices/yields/spreads.
- revenue, EBITDA/operating income, FCF, debt, liquidity, leverage, interest coverage, covenant or indenture terms when public or user-provided.
- refinancing risk, collateral or structural priority, cash burn, recovery context, trading levels, rating actions, and restructuring milestones.
- missing credit documents, stale trading levels, and definition conflicts.

Use when feeding Credit Markets, `scenario-sensitivity-generator`, `equity-model-update`, `portfolio-risk-management`, or `memo-builder`.

## Sector peer / competitor profile

Prioritize:
- public peer identity, business model, segments, geography, KPI set, market cap/EV, current valuation, and latest earnings event.
- key differences versus the focus company: growth, margin, mix, leverage, capital allocation, disclosure quality, and catalyst exposure.
- valuation or operating metrics that will feed comps, thesis testing, or peer read-through.

Use when feeding `comps-valuation`, `earnings-preview`, `earnings-deep-dive`, `equity-model-update`, `long-short-pitch`, or `memo-builder`.

## Ultra-compact profile block

Use inside a deck, memo, or meeting brief when space is tight:

```markdown
**[Entity]** is [business model / strategy] serving [customers/end markets] across [geography]. Latest source-backed scale: [metric 1], [metric 2], [metric 3] as of [period]. Current relevance: [why it matters]. Key gaps/flags: [gap or risk].
```

## Public Equity Investor Profile Additions

Add security and liquidity snapshot, index membership, ETF ownership/flow relevance, factor exposure, short interest, ownership concentration, governance, capital allocation, balance-sheet risk, and next analytical route when available or material to the requested review. The tearsheet remains factual, not a recommendation.

Default security setup / ownership / positioning block:

| Field | Value | As-of | Source | Confidence | Why it matters |
|---|---|---|---|---|---|
| Market cap / EV |  |  |  |  | Valuation and investability anchor |
| Float / free float |  |  |  |  | Capacity, passive flow, squeeze risk |
| ADV / liquidity / days-to-exit |  |  |  |  | Can a PM build or exit the position? |
| Index membership / benchmark weight |  |  |  |  | Active-weight and passive-flow relevance |
| ETF/passive ownership or flow signal |  |  |  |  | Rebalance and flow pressure |
| Top holders / ownership concentration |  |  |  |  | Governance, sponsorship, overhang |
| Short interest / borrow / days to cover |  |  |  |  | Short crowding and squeeze risk |
| Factor exposure / beta |  |  |  |  | Stock-specific versus factor-driven risk |
| Governance / capital allocation |  |  |  |  | Management quality and minority-holder risk |
| Sell-side coverage / consensus setup |  |  |  |  | Estimate path and variant wedge |

If a field is unavailable, retain `missing_required_source` with the required provider/export/source in support data. In reader-facing HTML, consolidate non-central unsourced fields into one compact evidence-gaps block rather than displaying a large low-information positioning table.
