# Long / Short Pitch Intake And Source Policy

## Source Priority

1. Connected or institutional-grade sources available in the session.
2. Company filings, releases, transcripts, investor decks, and official financials.
3. Market-data or consensus feeds available to the user.
4. User-provided models, notes, or research.
5. Web search or public summaries as a labeled fallback.

Rules:

- Prefer primary company sources over commentary.
- Verify recency for current prices, borrow, short interest, options pricing, consensus, and event spreads when tools are available.
- If a number is stale, approximate, or unavailable, label it.
- Keep fact, inference, and assumption separate.

## Request Types

- `new-trade-pitch`: build a new long, short, pair, event-driven, or equity special-situation pitch; route credit-first pitches to Credit Markets.
- `pitch-upgrade`: preserve the user's thesis while sharpening expression, catalyst, sizing, downside, and exit discipline.
- `explicit-short-pitch`: compressed pitch only when the user explicitly asks for quick/short/summary/one-pager/TL;DR.
- `qa-red-team`: findings-first investability review.
- `re-underwrite`: update after earnings, news, price movement, thesis drift, or new data.
- `partial-section`: answer only the requested part of the pitch, such as variant perception, why now, expression, sizing, disconfirmers, or cover rules.
- `sparse-context-screen`: turn incomplete facts into a provisional PM stance and data request list without pretending the pitch is fully underwritten.

## Pitch Modes

- `full-trade-pitch`: default mode; include scenario work, risk budget, monitoring, add/trim/exit rules.
- `explicit-short-pitch`: variant perception, expression, upside/downside, catalyst, kill criteria only when the user asks for a compressed version.
- `sparse-context-screen`: actionability, provisional stance, core mispricing hypothesis, why now, what would change the stance, and missing data.
- `partial-section`: requested section only, plus implications for the trade and missing data to upgrade conviction.
- `short-pitch`: catalyst to expose mispricing, borrow/carry, squeeze risk, cover rules.
- `pair-trade-pitch`: leg logic, hedge ratio, residual exposure, break conditions.
- `event-driven-pitch`: probability tree, timing, spread, break price, milestones.
- `distressed-equity-special-situation`: listed-equity expression, event path, liquidity runway, catalyst/default/refi read-through, and Credit Markets handoff for credit-security or recovery work.
- `qa-red-team`: severity-ordered findings and investability verdict.

## Minimum Inputs

- Security, issuer, ticker, instrument, or spread.
- Proposed side: long, short, pair, relative value, event-driven, distressed-equity special situation, Credit Markets handoff, or unknown.
- Current price, event spread, FCF/dividend yield, or valuation reference, plus as-of date; route debt yield/spread analysis to Credit Markets.
- Horizon or catalyst window.
- Core thesis or observed mispricing.
- Known valuation anchor or scenario frame.
- Key risks, constraints, or data gaps.

If inputs are missing, do not stall unless needed to avoid a misleading pitch. State `Screen-grade only; placeholder assumptions used.` before the first metric table and list missing data in `Open Items / Data Requests`.

## Sparse Context Rules

Sparse context is common in PM conversations. Do not respond with a blank pitch template.

When the user gives only a company, theme, sector, or rough thesis:

- infer the pitch mode from the user's wording when reasonable
- provide a provisional `Actionability` view: actionable candidate, watchlist, pass for now, or red-team only
- separate fact, assumption, and judgment
- make the missing-data list specific enough for an analyst to gather
- explain what evidence would upgrade, downgrade, or kill the idea
- avoid precise valuation, borrow, short interest, consensus, or live-price claims unless sourced

Ask one clarifying question only when no issuer, instrument, side, sector archetype, or thesis can be inferred.

## Partial Section Rules

When the user asks for only part of the report, answer that part directly.

Examples:

- `what is the variant perception?`: give consensus belief, contrary evidence, timing, and falsifiers
- `how would a PM size this?`: discuss conviction, liquidity, downside gap, catalyst timing, crowding, borrow/carry, and risk-budget constraints without giving account-specific advice
- `what would make us cover?`: give measurable cover triggers, time stops, squeeze/borrow triggers, and thesis-failure evidence
- `why now?`: give catalyst path, expected evidence windows, and what would make timing premature

End partial outputs with:

- `Implications For The Trade`
- `Missing Data To Upgrade Conviction`

## PM Source And Intake Additions

Capture mandate lens, portfolio role, benchmark relevance, position context, borrow/short interest, liquidity, options, ETF/index exposure, catalyst date quality, and data as-of times. Missing market data must be labeled before any pitch-ready conclusion.
