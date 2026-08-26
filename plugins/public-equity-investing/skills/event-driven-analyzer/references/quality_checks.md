# Quality Checks

Use this before finalizing any event-driven output for senior review.

## Mandatory checks

- Event type is explicit and, if multi-label, all relevant labels are named.
- Security expression is explicit.
- Current market data is timestamped or clearly unavailable.
- Facts, assumptions, and judgments are separated.
- Primary source documents are used when available.
- Missing critical documents are named.
- Timeline distinguishes known dates from estimated dates.
- Gating item is specific and tied to a decision-maker or process.
- Downside/break value methodology is explicit.
- Scenario probabilities sum to 100%; `scripts/event_math.py --mode scenario_ev` hard-fails mismatches unless `--allow-probability-sum-mismatch` is explicitly used for diagnostic output.
- Expected return and annualized return are not used without downside.
- Recommendation is explicit, or no-trade rationale is explicit.
- Monitoring plan includes date/window, source, signal, and action.
- Red-team section states how the trade loses money.

## Event-specific checks

### Merger arb
- Deal price and current price confirmed or marked unverified.
- Spread and annualized spread calculated.
- Market-implied probability calculated if downside is available.
- Merger agreement/proxy status checked.
- Outside date and expected close date distinguished.
- Break fee/reverse termination fee and financing condition reviewed or marked missing.
- Regulatory approvals and vote thresholds named.
- Acquirer risk and hedge ratio included for stock deals.

### Spin-off
- Distribution mechanics and dates included.
- SpinCo and RemainCo financials separated.
- Debt/cash/liability allocation considered.
- Stranded costs and dis-synergies considered.
- Forced selling/index/holder base analyzed.
- Entry timing considered.

### Activism
- Activist ownership and demands stated.
- Governance and nomination mechanics considered.
- Vote math and shareholder base assessed.
- Settlement vs proxy fight probability included.
- Value creation plan judged, not just summarized.

### Litigation/regulatory
- Venue/agency and procedural posture stated.
- Timeline and next official date included.
- Remedy/damages/settlement path analyzed.
- Legal-advice boundary respected.
- Official sources prioritized.

### Restructuring/distressed
- Dated catalyst or process path is explicit.
- Probability/payoff tree uses sourced or clearly labeled recovery assumptions.
- If capital structure, covenants, liquidity, maturity wall, fulcrum security, priority, or recovery waterfall are central, the output routes to or incorporates work from Credit Markets.
- Priming/LME/class vote/court risk is considered as event-path risk, with legal conclusions reserved for counsel.

### Technical/special situations
- Flow mechanics and dates included.
- Flow size compared with liquidity.
- Crowding and pre-positioning considered.
- Exit plan stated.

## Senior-taste checks

Ask yourself:
- Would a PM know what to do after reading the first page?
- Is the variant view clear?
- Did the output identify the real gating item, or only generic risks?
- Is downside intellectually honest?
- Is the trade expression practical in real market conditions?
- Are we over-precise relative to source quality?
- Did we state what would change our mind?

## Common failure modes

- Summarizing news instead of underwriting outcomes.
- Treating annualized spread as the conclusion.
- Failing to calculate market-implied probability.
- Accepting unaffected price as break price without adjustment.
- Ignoring timing risk.
- Ignoring stock-deal acquirer risk.
- Ignoring borrow/liquidity/carry.
- Using generic regulatory or litigation risk language.
- Omitting a monitoring plan.
- Giving a trade recommendation based on possible MNPI.
