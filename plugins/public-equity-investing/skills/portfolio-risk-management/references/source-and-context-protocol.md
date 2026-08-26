# Source and Context Protocol

## Purpose

Use this protocol to make the skill robust across no-context, partial-context, full-source, and refresh workflows. The goal is to produce a useful PM-grade answer without hallucinating current market data or silently overwriting user work.

## Context modes

### No-context mode

Trigger when the user gives no ticker, no position, no portfolio size, or no thesis.

Output:

1. Minimum intake checklist.
2. Default analysis structure.
3. Template tabs or CSV templates if the user is working in a spreadsheet.
4. Examples of the few inputs that unlock a real recommendation.

Do not invent a company, price, beta, volatility, current holdings, or recommended size.

Minimum intake checklist:

- Instrument/ticker and direction.
- Portfolio NAV/AUM and benchmark, if relevant.
- Current or proposed size.
- Investment thesis and intended holding period.
- Upside/base/downside or target/stop levels.
- Maximum acceptable loss or risk budget.
- For a short or option position, whether that maximum is a scenario loss budget or an absolute loss cap.
- Liquidity constraint and required exit window.
- Existing related exposures and hedges.
- Mandate/risk limits.

### Partial-context mode

Trigger when the user provides a thesis or ticker but not a complete risk pack.

Output:

- A v0 sizing view with facts, assumptions, and missing data separated.
- A preliminary recommended size only if enough information exists to compute a defensible range.
- Confidence labels for price, beta, volatility, liquidity, borrow, factor, and scenario inputs.
- A short list of data that would most improve the recommendation.
- A conditional rather than executable action label when current quote, liquidity, borrow/locate, or required option inputs are not established.

Use explicit labels:

- **User-provided fact**: supplied by the user or in the active file.
- **Sourced fact**: retrieved from a callable connected route, user-provided export, or cited source.
- **Assumption**: inferred or defaulted because the source was missing.
- **Placeholder**: intentionally blank until the user or source provides it.

### Full-source mode

Trigger when the user provides or enables access to a model, risk report, portfolio file, holdings export, data room, broker pack, or connected market data.

Output:

- Source inventory and source hierarchy.
- Normalized trade, portfolio, and risk inputs.
- Sizing recommendation with math trace.
- Scenario P&L and liquidity/execution view.
- Monitoring rules and open items.
- QC flags for stale or inconsistent inputs.

### Refresh mode

Trigger when updating an existing sizing analysis or workbook.

Output:

- What changed since prior version.
- Updated size and whether recommendation changed.
- Drivers of change: price, target/downside, volatility, beta, liquidity, factor exposure, catalyst timing, portfolio NAV, current holding, or risk limits.
- New tabs or sections; preserve prior versions.

## Source hierarchy

1. User-provided files, pasted context, active workbook/deck, and explicit assumptions.
2. Callable connected routes or user-provided exports: portfolio holdings, risk systems, OMS/EMS exports, market data providers, research systems, broker files, and internal models.
3. Primary market/company sources: filings, releases, presentations, transcripts, exchange/index/ETF sponsor data, issuer docs, exchange/index/ETF sponsor data, debt maturity schedules when relevant to common-equity risk, and official equity/security terms.
4. Callable third-party routes or user-provided exports: Bloomberg, FactSet, LSEG, S&P Capital IQ, MSCI/Barra, Axioma, Refinitiv, broker estimates, rating agencies, TRACE/FINRA, OCC/options data, short interest data, and consensus providers.
5. Public web fallback. Use only when better sources are unavailable and label the limitation.

## Freshness rules

Treat these as freshness-sensitive and date/time stamp them when possible:

- Last price, market cap, shares outstanding, enterprise value.
- Portfolio NAV, current holdings, gross/net exposure.
- Beta, correlation, volatility, factor exposure.
- ADV, float, short interest, borrow availability/cost, utilization, days to cover.
- Options prices, implied volatility, skew, open interest, delta/gamma/vega/theta.
- CDS levels, credit spreads, ratings, maturities, refinancing pressure, and covenant headlines only when used as common-equity risk signals; route yield, duration, recovery assumptions, spread DV01/CS01, and credit-security terms to Credit Markets.
- Rates, FX, commodities, index weights, ETF holdings.
- Earnings dates, regulatory events, trial dates, shareholder votes, merger close dates, lockups.
- Consensus estimates and revisions.

If data may be stale, say exactly which input is stale and why it matters for sizing.

For short positions with a user-provided maximum NAV loss, classify the constraint as a `scenario loss budget`, `absolute loss cap`, or `unresolved` before recommending an implementable size. A scenario budget needs a visible adverse-move assumption. An absolute cap needs a priced defined-loss option package or a no-position conclusion.

## Confidentiality and compliance

- Treat portfolio holdings, trades, sizing, risk limits, LP/client context, and internal research as confidential.
- Do not include client names or fund names in a clean external version unless the user requests it.
- Do not present a recommendation as guaranteed or riskless.
- For public-company analysis, avoid selective disclosure issues. If a source appears MNPI or restricted, flag it and do not use it unless the user confirms it is permitted for the workflow.
- Keep the answer framed as analytical support for a professional user, not as retail investment advice.

## Spreadsheet preservation

When modifying spreadsheets:

- Add versioned output tabs; do not overwrite source tabs.
- Preserve formulas, hidden sheets, comments, named ranges, and formatting unless explicitly asked.
- Put source notes and assumptions in separate tabs.
- Create QC flags instead of silently changing questionable inputs.
- If there are circular references, hardcodes, broken links, or stale external links, flag them before editing.

## Confidence labels

Use these labels in the output:

- **High confidence**: sourced from user file or reliable connected source, recent, internally consistent.
- **Medium confidence**: sourced but stale, estimated, or not fully tied to portfolio context.
- **Low confidence**: inferred, public-web-only, missing key inputs, or inconsistent sources.

## Missing data hierarchy

If many inputs are missing, prioritize the missing data that most affects sizing:

1. Portfolio NAV and current exposure.
2. Downside/stop case and max acceptable loss.
3. Liquidity/ADV and exit window.
4. Beta/factor/sector exposure.
5. Catalyst timing and gap risk.
6. Borrow and options terms; if the missing inputs are CDS, bonds, loans, spread DV01/CS01, recovery, covenant, or debt-security terms, use a Credit Markets handoff instead of local sizing.
7. Existing correlated positions and hedges.
