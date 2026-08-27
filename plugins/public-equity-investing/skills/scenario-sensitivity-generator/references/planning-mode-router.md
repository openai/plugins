# Public Equity Investing Mode Router

Choose the right mode before building outputs.

| Mode | Use when | Output should include | Avoid |
|---|---|---|---|
| Price-target scenario | The user needs bull/base/bear value, skew, or probability-weighted target | scenario values, return vs current price, probability if supplied, thesis implication | implying the weighted target is a recommendation by itself |
| Valuation sensitivity | The user needs DCF, multiple, SOTP, or reverse-valuation ranges | selected valuation metric, assumption axis, implied price/value, caveats | rebuilding a full DCF or comps model inside this skill |
| Estimate / KPI sensitivity | The user needs EPS, EBITDA, revenue, margin, guidance, or KPI driver impact | driver change, output change, estimate or price implication, source caveat | generic revenue growth shocks when a sector KPI is available |
| Equity liquidity downside | The user needs common-equity liquidity, maturity, refinancing, CDS/spread signal, covenant-pressure, or recovery read-through downside | cash/liquidity headroom, maturity pressure, common-equity recovery read-through, spread-signal sensitivity, breach point | credit-security valuation, covenant-package analysis, recovery waterfall, or credit memo drafting; route those to Credit Markets |
| Event probability tree | The user needs success/fail/delay math for a catalyst | probability range, success/fail values, expected value, timing/downside caveat | treating process probability as a sourced fact without support |
| Macro factor sensitivity | Rates, FX, commodities, policy, inflation, or spreads drive the view | factor move, sensitivity source, price/value impact, next monitoring signal | broad macro essay without security-level translation |
| Thesis trigger table | The user needs monitoring thresholds or add/trim/hedge/exit markers | trigger, threshold, implication, next step, source/owner | vague "continue to monitor" language |

Combine modes when needed, but name the role of each exhibit so the pack does not become a pile of unrelated tables.
