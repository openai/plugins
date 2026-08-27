# Peer Selection

## What a good peer set means

A good peer set is:

- explainable in 30 seconds;
- economically comparable rather than cosmetically similar;
- liquid enough that market-implied multiples are meaningful;
- not cherry-picked to force a valuation answer.

## Build peers in this order

1. Start with the narrowest useful taxonomy: sector, industry group, industry, then subindustry.
2. Add geography and listing filters that reflect how the market prices the business.
3. Add business-model tags that actually drive multiples, such as subscription, marketplace, regulated, hardware, services, asset-heavy, transaction-driven, or recurring-revenue.
4. Check size, growth, margin, leverage, cyclicality, liquidity, customer mix, and accounting basis.
5. Keep 6-12 peers when possible, but prefer a clean narrow set over a broad noisy one.
6. Allow manual overrides only with a short rationale.

## Peer role labels

Assign each material peer one role:

| Role | Meaning | Treatment |
|---|---|---|
| `core_peer` | Closest economic comp | Should influence selected range |
| `secondary_peer` | Relevant but less direct | Use as context unless core set is too small |
| `aspirational_peer` | Useful business-model read-through, weaker anchor | Do not let it drive valuation without explanation |
| `negative_peer` | Shown to explain why it should not anchor valuation | Include in rationale, usually exclude from selected range |
| `excluded_close_peer` | Economically relevant but missing a required primary field | Name the exact blocker |
| `not_clean_comp` | Conglomerate, segment-mix, distressed, illiquid, or accounting mismatch | Context only unless justified |

## Inclusion and exclusion rules

- Prefer primary listings.
- ADRs are acceptable if liquidity is sufficient and share factors are handled correctly.
- Exclude distressed companies unless the target is also distressed or the distress read-through is central.
- Exclude banks, insurers, and REITs from corporate peer sets unless the user explicitly wants cross-sector comparisons.
- Conglomerates can stay only if flagged as `not_clean_comp`.
- If the target is loss-making, prioritize peers with similar growth and margin profiles and weight revenue or sector-specific KPIs more heavily.
- Do not silently drop close peers. If a close peer is excluded, list it under `Excluded close peers` with the exact blocker.

## Peer-set review output

For peer-set review tasks, use:

| Company | Proposed role | Keep / move / exclude | Rationale | Missing data / caveat |
|---|---|---|---|---|

Then conclude with:

- core peer set;
- secondary context set;
- excluded close peers;
- peers to avoid as valuation anchors;
- the multiples most appropriate for the resulting set.

## Sparse or missing-market-data fallback

When the user asks for a clean comps table but does not provide source data and live market data is unavailable, still produce a peer-selection framework.

Minimum fallback behavior:

- propose 6-12 likely peer candidates when the business model is identifiable;
- if candidates are uncertain, label them `watchlist_peer` rather than `core_peer`;
- list obvious excluded or non-clean peers instead of silently dropping them;
- state the exact fields needed before the peer can anchor valuation;
- avoid a selected valuation range until market data, estimates, and denominators are sourced.

Use role labels conservatively:

- `core_peer`: only when business-model fit is strong and source data exists or can be clearly requested.
- `watchlist_peer`: plausible candidate, but source data or fit still needs validation.
- `negative_peer`: useful to explain why a tempting comp should not drive valuation.
- `excluded_close_peer`: close peer blocked by missing data, fiscal mismatch, capital structure distortion, or denominator issue.

## Public Equity Peer Filters

After business-model fit, test public-equity investability: liquidity, float, index membership, ETF ownership, short interest/borrow, ADR or share-class issues, consensus coverage, estimate-revision relevance, sector KPI regime, accounting calendar, and source freshness. Debt comps, bond comps, loan comps, CDS, spread/yield relative value, and recovery comps route to Credit Markets unless they are only context for common-equity downside.
