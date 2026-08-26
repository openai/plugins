# Company Tearsheet Quality Checks

## Entity identity checks
- Confirm the entity is the correct public company, public issuer, Credit Markets issuer, or security, not a similarly named entity.
- For public companies, verify ticker/exchange and fiscal year-end.
- For Credit Markets, verify issuer/parent, instrument identifiers, and rating/security context when material.
- Do not use this skill for fund/manager diligence; route non-issuer fund or manager profiles outside `company-tearsheet`.

## Source checks
- Every material metric should have source, period, units, evidence label, and confidence.
- Do not use stale market data without an as-of date.
- Do not cite marketing claims as verified third-party facts.
- Do not rely on web snippets when user-provided or connected sources are available.
- Flag unaudited, preliminary, pro forma, adjusted, or management-defined numbers.

## Metric checks
- Revenue, EBITDA, net debt, leverage, margin, AUM/NAV, share price, market cap, EV, and valuation must have period and units.
- Do not mix fiscal years, calendar years, LTM, quarterly, forecast, and YTD without labels.
- Do not mix currencies or units without clear conversion disclosure.
- Derived metrics must show inputs or formula in a note.
- If source financials are hard to read or inconsistent, route to `financials-normalizer` before finalizing.

## Profile balance checks
- Keep the tearsheet concise. It should not become a full memo.
- Separate business description, metrics, developments, implications, and risks.
- Avoid unsupported adjectives like "best-in-class", "dominant", "high-quality", or "distressed" unless evidenced.
- Avoid investment recommendations unless explicitly requested and routed to the appropriate analysis skill.
- For public-equity investor tearsheets, do not omit security setup, ownership, or positioning needs silently. Market cap, float, ADV/liquidity, index membership, ETF/passive ownership, top holders, short interest, borrow/crowding, factor exposure, governance, capital allocation, sell-side coverage, and consensus setup should be sourced when relevant or identified in a compact source/as-of evidence-gaps block.
- When a current transaction, rumor, regulatory item, or other live event is material but not the requested focus, confirm it is featured in the investor read and catalyst/risk section, with missing primary evidence identified in the evidence-gaps block. Confirm it is not threaded through earnings drivers, valuation, and multiple summary panels unless it directly changes those analyses.

## Valuation framing checks
- Use the visible heading `Trailing Valuation Snapshot` or `Valuation Context` when valuation support consists of reported historical financials and derived trailing metrics.
- Do not include `Debate` in the heading unless forward estimates, peer evidence, target-price evidence, or explicit market expectations support a genuine expectations discussion.
- Do not present simplified enterprise value calculations as a full EV bridge or underwritten valuation case.

## HTML presentation checks
- For a selected HTML tearsheet, follow `../../../shared/html-artifact-standard.md` and keep the issuer baseline compact rather than forcing the standardized dashboard shell.
- Use plain investor-facing evidence language; do not expose internal evidence labels such as `fact_source_reported` or `missing_required_source` unless the user requests support detail.
- Do not fragment tickers, years, dates, numeric ranges, metric names, or product labels into separate citation links.
- Render and visually inspect local HTML using headless-browser screenshots before delivery, focusing on hierarchy, density, clipping, citation noise, and whitespace.

## Conflict checks
Flag if:
- multiple sources show different revenue/EBITDA/debt/AUM/NAV/share count/market cap values.
- a provider value differs from a filing/source package.
- a company presentation or management deck differs from filings, releases, transcripts, or provider data.
- a current source supersedes an older source in the package.

## Final QA checklist
Before returning:
1. Entity confirmed.
2. Source inventory exists or source limitations disclosed.
3. As-of date shown.
4. Metrics table includes source, period, units, evidence, confidence.
5. Stale/conflicting/missing data flagged.
6. Assumptions separated from facts.
7. Handoff recommendation is appropriate.
8. Source materials preserved.
