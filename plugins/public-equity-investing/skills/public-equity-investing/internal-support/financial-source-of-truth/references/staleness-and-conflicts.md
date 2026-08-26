# Staleness and Source Conflict Handling

Use this guide to decide when a source is too old, incomplete, or contradicted to support a Public Equity Investing conclusion.

## Required freshness fields

For each material source, record:

- Document date
- Period covered
- As-of date
- Access date
- Version or draft status if available
- Whether the source may have been superseded

If one of these fields is missing and it matters to the decision, mark freshness as unknown.

## Freshness thresholds by data type

These thresholds are defaults. Tighten them when markets are volatile, the issuer is balance-sheet-stressed, an event is live, or the user asks for current information.

| Data type | Freshness expectation | Flag as stale when |
|---|---|---|
| Public-company historical annual financials | Latest filed annual period | New annual filing or restatement likely supersedes it |
| Public-company quarterly financials | Latest filed quarter or latest earnings release for the relevant period | New quarter has reported, filing/release supersedes it, or period is ambiguous |
| Earnings release and transcript | Exact reported quarter | New guidance, 10-Q/6-K, 8-K, investor day, or later management update supersedes it |
| Market prices, FX, yields, spreads, commodities | Timestamp or current date | No timestamp, old quote, volatile market, or output implies live precision |
| Consensus estimates | Vendor and date | No date, changed after earnings/guidance, or source does not identify estimate set |
| Company investor presentation or supplemental | Date of pack and period referenced | Newer filing, release, supplemental, or investor day supersedes it |
| Non-filed management data or conference deck | Specific date, event, and period | Later company disclosure, filing, or transcript contradicts or supersedes it |
| Credit ratings and outlooks | Agency, date, issuer/instrument | Later rating action, watch/outlook change, or debt instrument mismatch |
| Debt balances and liquidity | Latest reporting period or issuer disclosure | Quarter-end data likely changed materially or new issuance/refinancing occurred |
| Covenants, indentures, and legal terms | Current executed agreement, filed agreement, or current user-provided draft | Summary only, outdated draft, amendment likely supersedes it |
| Distressed/restructuring process data | Latest court docket, company filing, or proceeding milestone | New court filing, plan update, order, or hearing result supersedes it |
| Macro releases | Official release date, revision status | Revised data, newer release, preliminary estimate superseded by final |

## Staleness labels

Use these labels in evidence ledgers:

| Label | Meaning |
|---|---|
| current | Fresh enough for the stated use |
| current but volatile | Fresh now, but likely to change quickly; timestamp required |
| stale but usable for history | Old but appropriate for historical context |
| potentially superseded | There may be newer source material; avoid definitive conclusions |
| stale for decision | Too old for the decision; use only as context |
| unknown freshness | Missing date/as-of/version information |

## Conflict handling workflow

1. Identify the exact conflict.
   - Metric mismatch: revenue, EBITDA, leverage, FCF, debt balance, CDS/spread signal, price, valuation range, consensus, short interest, ownership, ETF/index weight.
   - Definition mismatch: adjusted EBITDA, ARR, net debt, same-store NOI, active customer, organic growth.
   - Timing mismatch: LTM period, fiscal year, quarter, as-of date, spot price.
   - Scope mismatch: consolidated versus segment, continuing ops versus total, restricted group versus issuer.
   - Source type mismatch: filed number versus company presentation versus broker summary.

2. Classify materiality.
   - High: changes recommendation, valuation range, common-equity risk view, risk sizing, rating/target support, or investment action.
   - Medium: changes framing but not decision.
   - Low: immaterial or disclosure-only.

3. Select preferred source.
   - Prefer the source that is most authoritative for that claim.
   - Prefer the source with the most precise scope, period, and definition.
   - Prefer current executed/filed/audited/source-system data over summaries.
   - If using a lower-tier source, explain why.

4. Document treatment.
   - Resolved: explain reconciliation and use corrected figure.
   - Partially resolved: use preferred figure and flag caveat.
   - Unresolved: present both figures and convert to evidence request.
   - Sensitivity: run both versions if the conflict affects value, credit, or risk sizing.

## Conflict register template

```markdown
| Issue | Source A | Source B | Difference | Materiality | Preferred source | Treatment | Evidence request |
|---|---|---|---|---|---|---|---|
| [metric/claim] | [S1] | [S2] | [variance] | [high/medium/low] | [source ID/unresolved] | [resolved/partial/unresolved/sensitivity] | [specific request] |
```

## Examples of correct treatment

- If an investor deck claims 30 percent EBITDA growth but the latest filing shows flat adjusted EBITDA, label the deck statement as an issuer/management claim, use the filing as preferred evidence for reported performance, and request the bridge.
- If consensus revenue differs across two vendors, cite both, state date and vendor, and avoid false precision. If the delta matters, run sensitivity.
- If covenant or recovery evidence is needed for a credit-security conclusion, route to Credit Markets. If it is used only for equity downside, cite the highest-quality available source and label it equity-risk context.
- If a market price is from yesterday and the user asks for current valuation, either retrieve current data or state that the price is stale for live valuation.

## Do-not-do list

- Do not average conflicting numbers without explaining source, definition, and timing differences.
- Do not use a company presentation as proof of adjusted EBITDA without reconciliation.
- Do not treat management guidance as achieved performance.
- Do not cite a transcript quote as proof that the strategy will work.
- Do not use stale market data in a conclusion that implies live pricing.
- Do not hide unresolved conflicts in footnotes if they affect the decision.
