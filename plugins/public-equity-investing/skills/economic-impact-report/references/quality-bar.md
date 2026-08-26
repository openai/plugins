# Quality Bar And Failure Checks

## Gold Standard
A strong economic impact report is not a news summary, macro essay, or cross-asset trade note. It is a public-equity decision document.

It should tell a senior public-equity investor:
- what changed;
- why it matters for listed equities;
- what should reprice first across issuers, peer groups, sectors, factors, or benchmark/ETF exposures;
- what is still uncertain;
- where the highest-conviction consequences sit across earnings, estimates, valuation, positioning, liquidity, and portfolio action.

It should move from event to mechanism to public-equity implication. It should separate facts from judgment, direct effects from higher-order effects, and near-term equity consequences from long-duration strategic consequences.

For a substantial standalone HTML report, the first read should center on event status, market baseline, the event-to-equity transmission map, and the ranked equity impact map rather than a fixed dashboard module inventory.

## Evidence Standards
- Prefer primary material.
- Include a visible `Source And Freshness` section with data cut-off/as-of date, sources used, evidence posture, stale or missing data, and source conflicts.
- Include a visible `Event Status And Market Baseline` block that separates confirmed facts, reported or assumed events, and time-sensitive market observations. When material intraday observations inform the report, state an exact research cut-off time and time zone. For commodity shocks, state the benchmark and distinguish spot, futures, intraday, and closing observations where relevant.
- Tie every major claim to a public-equity mechanism.
- Label judgments as fact, inference, or scenario when uncertainty matters.
- Include rough magnitude estimates whenever possible.
- Use historical analogs to bound outcomes, not to assume repetition.
- Let confidence track evidence quality, not writing confidence.
- Surface unknowns explicitly.
- Keep citations decision-useful: cite material facts near use, then avoid repeated citation chips that make tables or monitoring queues harder to read.
- Group representative listed exposures only when the transmission channel, first affected line item, and directional read-through are genuinely shared; thematic adjacency is not enough.
- Judge what is priced in primarily from the affected equities/sectors, revisions, valuation movement, and relevant transmission markets; treat broad-index performance as context rather than primary evidence for an exposure call.

## Delivery-Mode Source Gate
Final delivery must not pass with missing, stale, or weak evidence posture. Run:

```bash
python scripts/check_economic_impact_report.py --mode delivery path/to/support_note.md
```

Delivery mode fails when the report lacks a dedicated `Source And Freshness` section, omits a data cut-off/as-of date, omits sources used, omits the stale/missing-data assessment, or discloses load-bearing evidence that is stale, missing, unknown, unsupported, unverified, preliminary, assumption-led, secondary-only, or otherwise weak. Use `--mode draft` for work-in-progress reports where those issues should remain warnings.

## Self-QA Before Answering
Ask internally:
1. Did I identify what is genuinely new relative to the baseline?
2. Did I explain why now and the likely repricing sequence?
3. Did I name the transmission channels?
4. Did I state what the equity market is likely to care about first?
5. Did I separate direct from second-, third-, and fourth-order effects?
6. Did I rank impacts by sign, magnitude, timing, confidence, and directness?
7. Did I quantify where a reasonable range was possible?
8. Did I identify issuer, sector, earnings, valuation, positioning, and portfolio implications?
9. Did I explain what may already be priced and what may be mispriced in the affected equities?
10. Did I include the strongest counterargument?
11. Did I include scenarios, catalysts, and what would change the view?
12. Does the source/freshness posture pass delivery mode rather than merely warning in draft mode?
13. If no portfolio/watchlist was provided, did I build a general exposure map across industries, countries/currencies, companies, commodities, supplier/customer groups, and second-order peers rather than inventing holdings?
14. Could a senior public-equity investor make a sharper decision after reading this?

If any answer is no, revise.

## Common Failure Modes
Revise any output that does one or more of the following:
- It lacks issuer, sector, earnings, valuation, positioning, or portfolio implications.
- It recommends a standalone rates, FX, options, futures, commodity, or credit-security expression instead of a public-equity conclusion or explicit handoff.
- It fails to state what is already priced in.
- It does not identify what would change the PM action.
- summarizes the article instead of analyzing public-equity impact;
- lists impacted names without explaining the transmission channel;
- confuses headline intensity with economic importance;
- ignores what was already expected or already priced;
- treats rates, FX, options, futures, commodities, or credit as standalone strategy outputs instead of public-equity transmission inputs;
- over-focuses on the named company and misses suppliers, customers, competitors, peers, sector baskets, or financing channels;
- collapses all time horizons into one conclusion;
- gives speculative higher-order effects the same confidence as direct effects;
- uses qualitative language where a rough range is possible;
- names a non-equity asset class as the answer without routing trade construction out of Public Equity Investing;
- omits the strongest counterargument;
- omits falsifiers or monitoring signals;
- sounds balanced by making every impact equally important.
- defaults a substantive report into rigid dashboard modules when the user did not request a standardized dashboard;
- treats grouped issuer examples as security-level investment conclusions without issuer-specific supporting evidence;
- combines exposures with materially different operating or valuation transmission channels into one ranked row;
- uses broad-index performance as the principal evidence that an issuer or sector shock is priced in;
- lets repeated source chips or internal evidence machinery overwhelm the investor readout.

## Tone Check
The prose should be:
- senior;
- concise;
- bottom-line first;
- evidence-led;
- explicit about uncertainty without becoming vague.

Avoid:
- throat-clearing;
- generic macro filler;
- repetitive "this could be positive or negative" hedging;
- name-dropping companies without mechanisms;
- false precision when the data is weak.
