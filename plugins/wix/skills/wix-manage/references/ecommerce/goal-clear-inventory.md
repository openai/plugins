---
name: "Goal: Clear Inventory"
description: Maps the STOCK_MOVER business goal to inventory turnover KPIs and clearance discount flows.
layer: goal
references:
  - name: "Flow: Stock Mover"
    path: ecommerce/flow-stock-mover.md
    load: true
  - name: "Guardrail: Margin Protection"
    path: ecommerce/guardrail-margin-protection.md
    load: false
---
# Goal: Clear Slow-Moving Inventory

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Flow: Stock Mover](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/flow-stock-mover)
>
> **Related skills** (read with `ReadFullDocsArticle` if needed):
> - [Guardrail: Margin Protection](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-margin-protection)

Automate clearance discounts for products with high stock levels and low sales velocity, converting stagnant inventory into revenue before it becomes a carrying cost liability.

---

## Business Goal

**Goal ID:** `STOCK_MOVER`

The merchant wants to reduce excess inventory for products that are not selling at an acceptable rate. This is achieved by creating targeted discounts on slow-moving products, with discount depth proportional to how overstocked the product is relative to its sales velocity.

---

## KPIs

| KPI | Definition | How to measure |
|---|---|---|
| Inventory turnover ratio | ordersCount / quantity for each product | `getProductCatalogData` — compare ordersCount to current quantity |
| Days of supply | Current stock / average daily sales rate | Estimate from ordersCount over the product's listing period |
| Clearance conversion rate | Units sold during clearance / units available at start | Track stock levels before and after campaign |
| Revenue recovered | Revenue from clearance sales that would not have occurred organically | Compare sales velocity before and during campaign |

---

## Triggers

Activate this goal when the merchant expresses any of the following intents:

- "clear inventory"
- "stock mover"
- "clearance sale"
- "old inventory"
- "overstocked"
- "slow sellers"
- "dead stock"
- "excess stock"
- "move old products"
- Any request mentioning inventory levels, stock clearance, or product velocity

---

## Recommended Actions

### Primary: Flow: Stock Mover Clearance

The sole action for this goal. Identifies slow-moving products using the velocity ratio (ordersCount / quantity) and creates targeted discounts with depth proportional to inventory urgency.

**When to use:** Whenever the merchant wants to reduce stock levels for underperforming products.

**Key mechanics:**
- Velocity analysis: products with low ordersCount relative to quantity are clearance candidates
- Discount depth scales with overstock severity (deeper discounts for more stagnant items)
- Scope is typically ITEMS (specific slow-moving products) or CATEGORY (if an entire category is underperforming)
- Margin protection is critical — clearance discounts push closer to cost, so the guardrail must verify effective margin stays above 15%

**Product selection criteria:**
- High quantity + low ordersCount = primary candidates
- Products with 0 orders in 30+ days = urgent candidates
- Products approaching seasonal irrelevance = time-sensitive candidates

---

## Measurement Plan

### Before campaign launch

1. Record baseline stock levels for all targeted products
2. Record current sales velocity (ordersCount over last 30 days)
3. Calculate starting inventory turnover ratio per product

### During campaign (weekly check-ins)

1. Track units sold per clearance product
2. Monitor margin impact — clearance discounts erode margins faster than other campaigns
3. Check if discount depth needs adjustment:
   - Products still not moving after 7 days — consider deepening discount
   - Products clearing too fast — margin may be too generous

### After campaign (30-day assessment)

1. Calculate clearance rate: `units_sold / starting_stock * 100`
2. Compare inventory turnover ratio before and after
3. Calculate revenue recovered from products that had near-zero velocity
4. Assess carrying cost savings from reduced inventory
5. Target benchmarks:
   - Clearance rate > 50% = successful
   - Clearance rate < 20% = discount may have been too conservative or products are truly unsellable

---

## Decision Matrix

| Scenario | Approach | Rationale |
|---|---|---|
| Few specific slow products | ITEMS scope, targeted discounts | Surgical clearance avoids discounting healthy inventory |
| Entire category underperforming | CATEGORY scope | Broader clearance when the problem is category-wide |
| Products near zero velocity | Deeper discounts (up to margin floor) | Aggressive clearance justified for truly stagnant stock |
| Seasonal items approaching end of season | Time-limited clearance with urgency | Combine with end date to create customer urgency |
| Merchant specifies products or percentages | Honor merchant input | User overrides always take priority |
