# Target Backsolve Rubric

Use this when the user asks what must be true for a price target, return hurdle, valuation, spread, liquidity threshold, recovery value, or thesis trigger to work.

## Feasibility Labels

For every target backsolve, classify the result:

- `mathematically possible and underwriteable`
- `mathematically possible but stretched`
- `mathematically possible but dependent on multiple expansion`
- `mathematically possible but dependent on aggressive estimate revisions`
- `mathematically possible but dependent on event probability`
- `mathematically possible but dependent on financing or liquidity access`
- `mathematically possible but inconsistent with historical performance`
- `mathematically possible but violates another constraint`
- `not mathematically possible within allowed levers`
- `not enough information`

## Feasibility Tests

Always test feasibility against:
- historical best observed performance;
- consensus and guidance path;
- sector KPI bounds;
- valuation multiple support;
- balance sheet, liquidity, maturity, and covenant constraints;
- event timing and probability support;
- macro factor sensitivity;
- downside support and risk/reward skew;
- source quality and as-of dates.

## Backsolve Output

Show:
- target metric;
- time horizon;
- locked constraints;
- allowed levers;
- required path;
- feasibility label;
- what must be true;
- what would disconfirm the path;
- next workflow or data request.

Never present a solved target path as investable without underwriteability and evidence posture.
