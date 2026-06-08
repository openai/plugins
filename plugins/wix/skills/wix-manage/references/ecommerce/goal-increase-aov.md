---
name: "Goal: Increase AOV"
description: Maps the UPSELL_BOOST business goal to measurable KPIs and actionable discount flows. Covers AOV benchmarking, margin-based discount tiers, and minSubTotal strategy.
layer: goal
references:
  - name: "Flow: Upsell Boost"
    path: ecommerce/flow-upsell-boost.md
    load: true
  - name: "Flow: Bundle and Save"
    path: ecommerce/flow-bundle-and-save.md
    load: true
  - name: "Flow: Add Free Shipping"
    path: ecommerce/flow-add-free-shipping.md
    load: false
  - name: "Flow: Optimize Shipping Rates"
    path: ecommerce/flow-optimize-shipping-rates.md
    load: false
  - name: "Guardrail: Margin Protection"
    path: ecommerce/guardrail-margin-protection.md
    load: false
---
# Goal: Increase Average Order Value

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Flow: Upsell Boost](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/flow-upsell-boost)
> - [Flow: Bundle and Save](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/flow-bundle-and-save)
>
> **Shipping flows that also serve AOV goals** (load if shipping domain is active):
> - [Flow: Add Free Shipping](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/flow-add-free-shipping) — free shipping threshold pushes carts above AOV
> - [Flow: Optimize Shipping Rates](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/flow-optimize-shipping-rates) — rate optimization improves conversion on higher-value orders
>
> **Related skills** (read with `ReadFullDocsArticle` if needed):
> - [Guardrail: Margin Protection](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-margin-protection)

Incentivize customers to spend above the store's current average order value (AOV) by creating threshold-based discounts that reward higher cart totals.

---

## Business Goal

**Goal ID:** `UPSELL_BOOST`

The merchant wants to increase the average amount customers spend per order. This is achieved by setting a minimum subtotal condition above the current AOV, so customers are encouraged to add more items or upgrade to higher-priced products to unlock the discount.

---

## KPIs

| KPI | Definition | How to measure |
|---|---|---|
| Average Order Value (AOV) | Total revenue / total orders | `getSiteData` — revenue / ordersCount |
| Revenue per order | Gross revenue attributed to each completed order | Track via order data before and after campaign |
| Discount redemption rate | Orders qualifying for the discount / total orders | Count orders with the discount applied vs total |
| Cart size increase | Change in items per order after campaign | Compare items per order pre/post |

---

## Triggers

Activate this goal when the merchant expresses any of the following intents:

- "increase AOV"
- "boost order value"
- "upsell"
- "get people to spend more"
- "increase average order"
- "raise order size"
- "higher cart value"
- Any request mentioning order value, spending thresholds, or minimum purchase incentives

---

## Recommended Actions

### Primary: Flow: Upsell Boost Campaign

The primary action for this goal. Creates a percentage discount with a `minSubTotal` condition set above the current AOV. The discount percentage and threshold are tiered based on the store's average profit margin.

**When to use:** Always the first recommendation for AOV-focused goals. Works best when the store has clear AOV data and margin information.

**Key mechanics:**
- minSubTotal set to 1.15x-1.5x the effective AOV (based on margin tier)
- Discount percentage scaled to margin (10-20%)
- Scope prioritized: CATEGORY (high-margin) > ITEMS (specific upsell candidates) > SITE (fallback)

### Secondary: Flow: Bundle & Save Campaign

A complementary action that increases AOV by encouraging multi-item purchases. Instead of a subtotal threshold, it uses an item quantity threshold.

**When to use:** When the catalog has natural cross-sell opportunities (complementary products, accessories, related items). Particularly effective when the store has many lower-priced items where quantity-based incentives drive higher totals.

**Key mechanics:**
- minItemQuantity condition (typically 2-3 items)
- Targets categories with cross-sell potential
- Can run alongside an upsell boost if scoped to different categories

---

## Measurement Plan

### Before campaign launch

1. Record baseline AOV from `getSiteData` (revenue / ordersCount)
2. Record baseline items per order
3. Note the campaign start date

### During campaign (weekly check-ins)

1. Compare current AOV to baseline
2. Track discount redemption rate
3. Monitor margin impact (ensure effective margin stays above 15%)

### After campaign (30-day assessment)

1. Calculate AOV lift: `(new_aov - baseline_aov) / baseline_aov * 100`
2. Calculate incremental revenue attributable to higher order values
3. Assess whether the minSubTotal threshold needs adjustment:
   - If redemption rate > 80% — threshold may be too low, consider raising
   - If redemption rate < 10% — threshold may be too high, consider lowering
   - Sweet spot: 20-40% redemption rate

---

## Decision Matrix

| Scenario | Recommended Flow | Rationale |
|---|---|---|
| Clear AOV data, margin data available | Upsell Boost (primary) | Full data enables optimal threshold + discount calculation |
| Low-data store (few orders) | Upsell Boost with conservative defaults | Use price_p50 as AOV proxy, 10% discount, 1.15x threshold |
| Catalog has natural bundles | Bundle & Save (secondary) | Multi-item incentive drives AOV through quantity |
| Both AOV and cross-sell opportunity | Both flows, different scopes | Upsell Boost on high-value categories, Bundle & Save on accessories |
| Merchant specifies exact values | Honor merchant input | User overrides always take priority over calculated values |
