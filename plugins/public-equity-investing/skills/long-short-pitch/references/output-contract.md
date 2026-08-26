# Long / Short Pitch Output Contract

Use this reference after `long-short-pitch` is selected. Broad pitch requests default to the full pitch; quick or section-only outputs require explicit user wording.

## Standard Pitch Spine

1. `Trade Recommendation`
2. `Variant Perception`
3. `Security / Expression`
4. `Why Now / Catalyst Path`
5. `Scenario Price Targets / Returns`
6. `Risk / Reward and Sizing Considerations`
7. `Disconfirmers and Kill Criteria`
8. `Add / Trim / Exit / Cover Rules`
9. `Monitoring Dashboard`
10. `Open Items / Data Requests`

## Standalone HTML Trade-Pitch Report

Use flexible standalone HTML for a substantial reusable trade pitch or when the user explicitly requests HTML. The first-read layer should answer whether risk can be put on now, not reproduce a fixed monitoring dashboard.

Visible first-read order:

1. `Proposed Trade / Actionability`: posture, side/expression if supportable, horizon, core reason, and decisive caveat.
2. `Variant Wedge` and `What Is Priced In`: what operating evidence has changed and what expectation the trade would challenge.
3. `Implementation Gate`: the trade-critical evidence that is cleared, not cleared, missing, or illustrative only.
4. `Illustrative Scenario Skew` or supported scenario returns, clearly distinguished according to evidence quality.
5. Catalyst path, disconfirmers, and add/trim/exit/cover discipline.
6. Compact `Monitoring Triggers` or `Evidence To Watch` section and open items, followed by readable sources and limitations.

For short ideas, the `Implementation Gate` must make catalyst failure, valuation anchor, borrow/carry, defined-risk option feasibility where relevant, and squeeze/buyback exposure immediately visible. For pairs, replace short-specific fields with hedge ratio, residual exposure, liquidity mismatch, and catalyst symmetry.

Do not repeat the recommendation across a hero panel, action tile, bottom-line panel, and trade-recommendation section. Do not display internal evidence labels, fragmented fiscal-year/date/range citations, empty scenario cards, or decorative monitoring modules.

For a `watchlist`, `pass`, or `wait for proof` posture where no position is proposed, use the visible heading `Conditional Action Rules` instead of `Add / Trim / Exit / Cover Rules`. Reserve `Monitoring Dashboard` as a visible heading for the optional standardized-dashboard path; standalone HTML should use `Monitoring Triggers` or `Evidence To Watch`.

## Sparse Context Contract

Use this when the user provides only a company, theme, sector archetype, or rough thesis. Sparse context changes the confidence label, not the depth default: provide the full pitch spine where possible and label gaps.

Lead with:

`Screen-grade only; placeholder assumptions used.`

Then include:

1. `PM Stance`
2. `What The Market May Be Missing`
3. `Best Expression From Current Facts`
4. `Why Now / What Needs To Happen`
5. `What Would Upgrade Conviction`
6. `What Would Kill Or Downgrade The Idea`
7. `Missing Data To Underwrite`

`PM Stance` should choose one:

- `actionable candidate`: enough evidence exists to frame a proposed expression and next diligence
- `watchlist`: idea is interesting but needs a catalyst, valuation anchor, or source support
- `pass for now`: setup does not clear risk/reward, catalyst, liquidity, or evidence quality
- `red-team only`: user wants critique, not a proposed trade

Do not hide behind "need more data" if a provisional stance is possible. State the stance, then say exactly what would change it.

## Partial Request Contract

If the user explicitly asks for only one part of the pitch, do not return the full pitch spine. Answer the requested slice and add only the context needed to make it investable.

Use:

1. Requested section, using the user's heading when possible
2. `Implications For The Trade`
3. `Missing Data To Upgrade Conviction`

Examples:

- Variant perception: consensus belief, mispricing, evidence edge, timing, falsifiers.
- Expression: instrument, hedge needs, liquidity, factor/sector exposure, borrow/carry if short.
- Sizing logic: conviction, downside gap, liquidity, catalyst timing, crowding, and risk-budget framing.
- Cover rules: measurable thesis-failure evidence, catalyst time stop, price/risk-reward threshold, borrow/crowding change.
- Add/trim/exit rules: evidence threshold, valuation gap, catalyst progress, and risk/reward change.

## Trade Recommendation

Lead with one sentence that includes side, instrument/expression, current price/spread/yield if known, horizon, expected return or risk/reward, and primary condition/caveat. Use `proposed expression`, not personal-advice language.

If live market data is missing, use `current price not provided` rather than inventing one. If a directional stance is still possible, call it `screen-grade`.

## Variant Perception

Include consensus belief, what the market is mispricing, why timing is actionable, and what evidence would make the view consensus or wrong.

A strong variant perception is specific enough to be falsified. It should name the KPI, event, behavioral bias, accounting issue, capital-market constraint, or consensus blind spot that creates the edge.

## Security / Expression

Specify common equity, ADR, option, bond, loan, CDS, pair, basket, or event spread. Name liquidity constraints and factor/sector/commodity/FX/rates/credit exposures that must be hedged or accepted.

For pair trades, show long leg, short leg, hedge ratio, residual exposures, and break conditions.

## Scenario Price Targets / Returns

Include base, upside, and downside with probabilities that sum to 100% unless the user asks for a qualitative pitch.

| Scenario | Probability | Key drivers | Target price / spread / recovery | Total return | Trigger / timing |
|---|---:|---|---:|---:|---|

For shorts, show adverse upside risk as the loss case. If probabilities do not sum to 100%, flag the table as not pitch-ready.

When targets and probabilities are based on analyst assumptions and the pitch lacks a sourced valuation anchor or required implementation inputs such as borrow/carry or option pricing, title the object `Illustrative Scenario Skew`. State plainly that it screens the payoff shape but does not clear the trade for implementation.

## Risk / Reward and Sizing Considerations

Discuss sizing as a risk-management frame:

- confidence and evidence quality
- liquidity and time-to-exit
- downside gap risk
- catalyst timing uncertainty
- factor or sector exposure
- borrow, carry, squeeze, or financing cost
- gross/net exposure or pair residual exposure where relevant

Use sizing language as a proposed risk frame only. Do not tell the user what to trade in a personal account.

For a short pitch, show this implementation screen near the initial recommendation when relevant:

| Gate | Status | Why It Matters |
|---|---|---|
| Catalyst failure | Cleared / Not cleared / Missing | A valuation-only short is rarely sufficient after improved operating evidence. |
| Borrow / carry | Cleared / Not cleared / Missing | Determines whether the short can be held economically. |
| Defined-risk options | Cleared / Not cleared / Missing | Determines whether adverse squeeze exposure can be bounded at an acceptable cost. |
| Valuation anchor | Cleared / Illustrative only / Missing | Separates expensive from mispriced and timely. |
| Squeeze / buyback risk | Cleared / Not cleared / Missing | Determines the adverse path and cover discipline. |

## Disconfirmers and Action Rules

Disconfirmers must be measurable. Avoid vague claims like "execution improves" unless tied to a metric, date, or catalyst.

Action discipline:

- add if evidence improves and risk/reward remains attractive
- trim if price target gap closes faster than evidence
- exit if thesis fails or risk/reward no longer clears the hurdle
- cover if short thesis fails, catalyst passes, borrow/crowding risk changes, or downside skew flips
- hedge if thesis remains intact but factor or event exposure becomes dominant

## Missing Data Quality Bar

Missing data lists should be short and specific. Prefer:

- current price, market cap, net debt, liquidity, borrow fee, short interest, or option skew as applicable
- latest filing, transcript, investor deck, consensus snapshot, and model date
- KPIs that directly prove or disprove the variant perception
- event dates, lockups, regulatory milestones, refinancing maturities, or catalyst windows
- ownership/crowding, liquidity, and factor exposure for expression and sizing

Avoid generic asks like "more financials" or "more diligence" unless the user truly provided no context.

## Reader-Facing Evidence And HTML QC

- In user-facing HTML, use `Reported`, `Company guidance`, `Derived`, `Analyst assumption`, and `Not yet sourced` rather than internal evidence-label strings.
- Name partnership and commitment metrics according to their economics. An issuer purchase, cloud-spend, infrastructure, or capacity commitment must not be presented as revenue, bookings, or customer demand unless directly supported; state `not incremental revenue guidance` where that distinction could be missed in a headline tile.
- Keep fiscal years, tickers, dates, percentages, ranges, metric names, and product labels visually intact when attaching citations.
- Cite analyst scenarios as assumptions in the nearby explanation rather than presenting an internal assumption register like an independent source.
- Do not render empty headings, empty bullet lists, or empty scenario-card elements.
- Visually inspect substantive local HTML using local headless-browser screenshots before delivery.

## PM-Native Pitch Spine

Use `Proposed Trade / Actionability`, `Variant Wedge`, `What Is Priced In`, `Expression and Risk Budget`, `Scenario Skew`, `Catalyst Path`, `Disconfirmers`, `Add / Trim / Exit / Cover`, and `Monitoring`. Always include missing evidence and what would change the stance.
