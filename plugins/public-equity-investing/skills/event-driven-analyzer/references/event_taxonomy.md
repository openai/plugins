# Event Taxonomy and Classification

Use this reference when the event type is ambiguous or when a situation has multiple overlapping catalysts.

## Classification rule

Classify by the investment path, not by headline. A setup can have several labels. Example: a cash merger can also be an antitrust event, litigation event, financing event, and shareholder vote event.

Ownership boundary: use this skill when the central work is dated event path, probability, timing, payoff, expected-return, and monitoring math. Use Credit Markets when the central work is capital structure, covenant/document review, liquidity, maturity wall, priority, fulcrum-security, or recovery-waterfall analysis.

## Primary event types

### Cash merger arbitrage
Core question: Will the deal close, when, and what is the break price?
Key outputs: spread, annualized spread, implied close probability, break downside, close/delay/break/recut scenarios.

### Stock-for-stock merger arbitrage
Core question: Is the spread attractive after exchange ratio, acquirer hedge, collar, dividends, borrow, and acquirer risk?
Key outputs: deal value, hedge ratio, spread, collar sensitivity, acquirer risk, vote risk.

### Tender offer
Core question: Will tender conditions be satisfied, and what happens if the minimum condition or regulatory condition fails?
Key outputs: tender deadline, proration, minimum condition, withdrawal rights, extension path.

### CVR or contingent consideration
Core question: What is the probability-weighted value of future milestones, and are incentives aligned?
Key outputs: milestone tree, discounting, control-party incentive analysis, liquidity discount.

### Spin-off or split-off
Core question: What are SpinCo and RemainCo worth separately, and what technical flows create opportunity?
Key outputs: SOTP, distribution mechanics, forced-selling analysis, index eligibility, capital structure, management incentives.

### Activism
Core question: Can the activist force value creation or governance change, and what outcome is priced in?
Key outputs: campaign demands, vote math, board vulnerability, settlement probability, annual meeting timeline, value plan.

### Restructuring / distressed event
Core question: Which dated restructuring, exchange, court, maturity, or liability-management catalyst changes value, when, and with what payoff?
Key outputs: event path, process timeline, probability tree, sourced recovery/payoff assumptions, scenario EV, monitoring thresholds. Use Credit Markets for the capital structure, covenants, liquidity, maturity wall, priority, fulcrum-security, and recovery waterfall that support those payoffs.

### Litigation
Core question: What is the probability-weighted investment impact of trial, ruling, settlement, appeal, injunction, or damages?
Key outputs: merits matrix, damages/remedy range, procedural timeline, settlement incentives, security impact.

### Regulatory event
Core question: Which regulator controls the path, what process applies, and what remedies or delays are likely?
Key outputs: agency map, review stage, statutory timeline, theory of harm, remedy feasibility, interaction with outside date.

### Index / technical event
Core question: What flow is expected, who must buy/sell, and what is already priced?
Key outputs: inclusion/deletion logic, rebalance date, expected flow, liquidity, crowding, unwind plan.

### De-SPAC or SPAC event
Core question: What is the post-close equity really worth after redemption, PIPE, sponsor promote, warrant dilution, and lockups?
Key outputs: trust value, redemption, PIPE, minimum cash, sponsor economics, float, lockups, dilution, projections skepticism.

### Capital return / Dutch tender / exchange offer
Core question: What is the economic effect after proration, tax, participation, leverage, and signaling?
Key outputs: tender range, proration scenarios, accretion/dilution, balance-sheet impact, shareholder behavior.

## Intake questions by context

Ask only for information that is necessary and unavailable. Prefer best-effort with assumptions when the user has already provided enough to start.

Minimal intake:
- Company/ticker and security.
- Event type if known.
- User's position or intended trade, if relevant.
- Output mode only if the user wants something other than the default full memo: explicit quick read, model/math, red-team, or monitoring update.
- Allowed sources and whether to use callable connected routes, user-provided exports, or public web.

Event-specific missing facts:
- Merger: deal price, current price, expected close, outside date, break price, approvals.
- Stock deal: exchange ratio, acquirer price, collar, dividends, borrow.
- Spin: distribution ratio, SpinCo/RemainCo financials, dates, debt allocation.
- Activism: activist, ownership, demands, annual meeting date, nomination deadline.
- Litigation: venue, claim, procedural posture, next hearing/trial date, damages theory.
- Regulatory: agency, filing status, review stage, outside date, remedy path.
- Restructuring/distressed event: dated catalyst, court/RSA/exchange/maturity status, next process date, security expression, and any recovery/payoff assumptions already available. If debt stack, liquidity, maturities, prices, covenant status, or recovery waterfall are not already available and are central to the answer, route that work to Credit Markets.

## Multi-label examples

- `Cash merger + antitrust + financing`: cash sponsor take-private with high leverage and overlapping assets.
- `Spin-off + index technical + balance-sheet event`: parent distributes small levered SpinCo that index funds cannot hold.
- `Activism + sale process + governance`: activist seeks board seats and pushes strategic alternatives.
- `Litigation + regulatory + merger arb`: regulator sues to block a transaction and the trial schedule drives deal timing.
- `Distressed exchange + litigation + equity stub`: company attempts LME while creditor group challenges transaction.

## Output implication of classification

The classification determines which analysis must be included:
- Merger arb requires spread/probability/break-price math.
- Spin requires SOTP and forced-selling analysis.
- Activism requires vote math and campaign path.
- Litigation requires merits/timing/damages/settlement analysis.
- Regulatory requires agency process and remedy analysis.
- Restructuring under this skill requires a dated process path, probability/payoff tree, and monitoring plan; capital structure, covenant, and recovery waterfall work belongs in Credit Markets.
- Technical events require flow/liquidity/crowding analysis.
