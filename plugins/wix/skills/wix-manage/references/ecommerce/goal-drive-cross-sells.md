---
name: "Goal: Drive Cross-Sells"
description: Maps the BUNDLE_AND_SAVE business goal to multi-item purchase KPIs and bundling flows.
layer: goal
references:
  - name: "Flow: Bundle and Save"
    path: ecommerce/flow-bundle-and-save.md
    load: true
---
# Goal: Drive Cross-Sells and Product Discovery

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Flow: Bundle and Save](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/flow-bundle-and-save)

Promote product discovery and multi-item purchases by creating bundle-based discounts that reward customers for buying across categories or adding complementary items to their cart.

---

## Business Goal

**Goal ID:** `BUNDLE_AND_SAVE`

The merchant wants customers to explore more of the catalog and purchase multiple items per order. This is achieved through minimum item quantity conditions that incentivize buyers to add more products, particularly in categories with natural cross-sell relationships.

---

## KPIs

| KPI | Definition | How to measure |
|---|---|---|
| Items per order | Average number of line items per completed order | Order data: total items / total orders |
| Cross-sell rate | Percentage of orders containing items from 2+ categories | Analyze order composition across categories |
| Category diversity per order | Number of distinct categories represented per order | Track unique categories per order before and after |
| Bundle discount redemption | Orders meeting the minItemQuantity condition / total orders | Count qualifying orders vs total |

---

## Triggers

Activate this goal when the merchant expresses any of the following intents:

- "bundle"
- "cross-sell"
- "buy together"
- "product discovery"
- "multi-buy"
- "encourage people to buy more items"
- "sell accessories with main products"
- "increase items per order"
- "mix and match"
- Any request about getting customers to explore more of the catalog

---

## Recommended Actions

### Primary: Flow: Bundle & Save Campaign

The sole action for this goal. Creates a percentage discount with a `minItemQuantity` condition that activates when the customer adds enough items to their cart.

**When to use:** Whenever the merchant wants to incentivize multi-item purchases, cross-category exploration, or product discovery.

**Key mechanics:**
- minItemQuantity condition (typically 2-3 items based on catalog profile)
- Scope determines which products count toward the bundle:
  - CATEGORY — items from a specific category (best for focused cross-sell)
  - ITEMS — specific complementary products (best for curated bundles)
  - SITE — any items in the store (broadest reach)
- Discount percentage scaled to margin (10-20%)
- Higher item thresholds for lower-priced catalogs, lower thresholds for premium catalogs

**Catalog profile matching:**

| Catalog Type | minItemQuantity | Scope | Example |
|---|---|---|---|
| Accessories + main products | 2 | CATEGORY (accessories) | "Buy 2+ accessories, save 15%" |
| Wide catalog, many categories | 3 | SITE | "Buy any 3 items, save 10%" |
| Curated complementary items | 2 | ITEMS (specific products) | "Buy these together, save 15%" |
| Low-price items (avg < price_p25) | 3-4 | CATEGORY or SITE | "Buy 4+, save 20%" |
| High-price items (avg > price_p75) | 2 | CATEGORY | "Buy 2 premium items, save 10%" |

---

## Measurement Plan

### Before campaign launch

1. Record baseline items per order
2. Record baseline category distribution per order
3. Identify current cross-sell rate (orders with 2+ categories)

### During campaign (weekly check-ins)

1. Track items per order vs baseline
2. Monitor bundle redemption rate
3. Check margin impact — multi-item discounts compound with quantity
4. Verify the minItemQuantity threshold is appropriate:
   - Redemption rate > 70% — threshold may be too low
   - Redemption rate < 5% — threshold may be too high or scope too narrow

### After campaign (30-day assessment)

1. Calculate items-per-order lift: `(new_items_per_order - baseline) / baseline * 100`
2. Measure new category penetration — did customers discover categories they had not purchased from before?
3. Assess AOV impact — bundling often increases AOV as a side effect
4. Evaluate whether specific product combinations drove the most bundle completions
5. Target benchmarks:
   - Items per order increase > 15% = strong result
   - Cross-sell rate increase > 10% = successful discovery

---

## Decision Matrix

| Scenario | Approach | Rationale |
|---|---|---|
| Store has clear accessory categories | CATEGORY scope on accessories, minItemQuantity: 2 | Natural cross-sell with main products |
| Broad catalog, no clear bundles | SITE scope, minItemQuantity: 3 | Encourages exploration across the entire catalog |
| Merchant names specific products | ITEMS scope with those products | Curated bundle matching merchant's intent |
| Low average price catalog | Higher minItemQuantity (3-4) | Lower price per item makes larger bundles feasible |
| High average price catalog | Lower minItemQuantity (2) | Customers less likely to buy 3+ expensive items |
| Merchant specifies quantities or discounts | Honor merchant input | User overrides always take priority |
