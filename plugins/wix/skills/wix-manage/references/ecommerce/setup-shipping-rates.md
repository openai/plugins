---
name: "Setup: Shipping Rates"
description: Configures shipping option rates — rate types (flat, tiered, free), condition types and operators, free shipping threshold calibration, AOV sanity check, per-item penalty avoidance, and tier gap detection.
layer: config
---
# Shipping Rates

## AOV Sanity Check

**MANDATORY before any threshold calculation that references AOV.** Raw AOV can be misleading due to data issues or bulk purchases.

1. Extract `price_p25` and `price_p50` from `catalog_stats` (use the "All Products" category group).

2. Evaluate AOV against catalog price distribution:

| Condition | Interpretation | Action |
|---|---|---|
| AOV < price_p25 | Anomalous — likely a data or unit issue | Override: use `price_p50` as base. Note in reasoning. |
| AOV > price_p90 | Possible bulk/combo orders | Still use AOV but note discrepancy. |
| price_p25 <= AOV <= price_p90 | Reasonable | Use AOV as-is. |

3. Store the result as `effective_aov`. Use `effective_aov` everywhere AOV would be referenced — backup rate calibration, shipping thresholds, free shipping thresholds.

---

## Rate Types

Rate types are determined by the conditions array, not by an explicit field.

| Rate Type | Configuration |
|---|---|
| Flat rate | `conditions[]` empty, just `amount` |
| Free shipping | `amount = "0"` with optional `BY_TOTAL_PRICE GTE [threshold]` |
| Weight-based tiers | `BY_TOTAL_WEIGHT` conditions |
| Price-based tiers | `BY_TOTAL_PRICE` conditions |
| Quantity-based | `BY_TOTAL_QUANTITY` conditions |

## Condition Operators

Supported operators: `EQ`, `GT`, `GTE`, `LT`, `LTE`.

When multiple conditions appear in the same rate entry, they combine with AND logic.

## Free Shipping Threshold Calibration

Optimal range: `effective_aov x 1.0` to `effective_aov x 1.5`

| Scenario | Impact |
|---|---|
| `threshold > AOV x 2` | Too high -- customers rarely qualify |
| `threshold < AOV x 0.8` | Too low -- potential margin erosion |

Enhanced calibration using catalog stats:
- If `price_p75 > aov x 1.5` then use `price_p50 x 1.5`
- If `price_p75 < aov` then use `aov x 1.2`
- Default: `max(aov x 1.2, price_p75)`

## Per-Item Penalty Avoidance

`multiplyByQuantity = true` charges `amount x cart quantity`. Always flag this configuration and recommend switching to flat rate or tiered pricing instead.

## Price-Based Tiers Recommendation

Recommend switching from flat to tiered rates when ALL of the following are true:
- `price_spread_ratio > 10`
- `price_stddev > price_avg x 0.5`
- Only flat rates currently exist

Recommended tier structure:
- **Tier 1**: Below p50 -- lower rate
- **Tier 2**: p50 to p75 -- standard rate
- **Tier 3**: Above p75 -- higher rate or free

## Flat Rate Confirmation

When ALL of the following are true, flat rate is optimal and no change is needed:
- `price_spread_ratio <= 3`
- `price_stddev < price_avg x 0.3`

## Tier Gap Detection

Sort all conditions by value and look for gaps between ranges. Gaps mean some cart totals have no matching rate, which can cause checkout failures.

## Shipping Cost Sanity Check

Any rate `amount > AOV x 0.15` (15% of average order value) should be flagged as a cart abandonment risk.
