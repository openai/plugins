---
name: "Flow: Stock Mover"
description: Creates discount campaigns to clear slow-moving inventory by targeting products with high stock levels and low sales velocity. Uses deeper discounts proportional to inventory urgency.
layer: flow
references:
  - name: "Guardrail: Discount Conflicts"
    path: ecommerce/guardrail-discount-conflicts.md
    load: true
  - name: "Guardrail: Margin Protection"
    path: ecommerce/guardrail-margin-protection.md
    load: true
  - name: "Setup: Discount Rules"
    path: ecommerce/setup-discount-rules.md
    load: true
---
# Flow: Stock Mover Clearance

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Guardrail: Discount Conflicts](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-discount-conflicts)
> - [Guardrail: Margin Protection](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-margin-protection)
> - [Setup: Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/setup-discount-rules)

Creates a discount targeting slow-moving inventory — products with high stock levels and low sales velocity. The discount depth is proportional to how overstocked the product is, with deeper discounts for the most stagnant items. Margin protection guardrails are especially important here since clearance discounts tend to push closer to cost.

## Prerequisites

- Wix Stores installed on the site
- Products exist in the catalog with inventory (quantity) data
- Access to `getCatalogAnalytics` and `getProductCatalogData` tools
- Inventory tracking enabled for target products

## Required APIs

- [Create Discount Rule](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/create-discount-rule)
- [Query Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/query-discount-rules)

---

## Step 1: Gather inventory and sales data

Call `getCatalogAnalytics` and `getProductCatalogData` concurrently to assess stock levels and sales velocity.

**getCatalogAnalytics** call:
```
aggregates: sum(quantity), sum(ordersCount), avg(profitMargin)
```

**getProductCatalogData** call:
```
ordered: quantity DESC, ordersCount ASC
```

This sort order surfaces products with the most stock and the fewest sales first — the primary candidates for clearance.

Save the following values:
- `total_quantity` — total stock across catalog
- `total_orders` — total sales across catalog
- `avg_profit_margin` — average profit margin (sets discount ceiling)
- Per-product: `quantity`, `ordersCount`, `price`, `name`, `id`, `categoryId`

---

## Step 2: Identify slow-moving products

Calculate the velocity ratio for each product to identify overstocked items:

```
velocity_ratio = ordersCount / quantity
```

| Velocity Ratio | Classification | Action |
|---|---|---|
| < 0.1 | **Severely overstocked** — fewer than 1 sale per 10 units in stock | High priority for clearance discount |
| 0.1 - 0.3 | **Moderately overstocked** — slow but not stagnant | Medium priority |
| 0.3 - 0.7 | **Balanced** — reasonable sell-through rate | Not a clearance candidate |
| > 0.7 | **Fast-moving** — selling well relative to stock | Do NOT discount — unnecessary margin erosion |

Select products with velocity_ratio < 0.3 as clearance candidates.

If `quantity = 0` for a product, skip it (nothing to clear). If `ordersCount = 0`, the velocity ratio is 0 — this is the most urgent clearance case.

---

## Step 3: Calculate discount depth

Scale the discount based on inventory urgency. Deeper discounts for more overstocked items, constrained by margin:

| Velocity Ratio | Recommended Discount | Rationale |
|---|---|---|
| 0 (zero sales) | 20-25% | Maximum urgency — product is not moving at all |
| < 0.1 | 15-20% | Severely slow — needs aggressive pricing |
| 0.1 - 0.2 | 10-15% | Moderately slow — moderate discount |
| 0.2 - 0.3 | 5-10% | Slightly slow — gentle nudge |

**Margin constraint**: Always verify `discount <= avg_profit_margin - 15%` (minMarginPct). Clearance discounts are more likely to violate margin thresholds because they are deliberately deeper.

**Global cap**: Do not exceed 25% unless the merchant explicitly overrides. For clearance, merchants may accept deeper discounts to free up capital and shelf space.

---

## Step 4: Determine discount scope

Select the scope based on the distribution of slow movers:

- **ITEMS** (preferred for clearance): Target specific slow-moving products by ID (max 5 productIds). This is the most precise approach and avoids discounting fast sellers.
- **CATEGORY**: When multiple slow movers cluster in the same category, target the whole category. This is simpler but may discount some healthy-velocity products in the same category.
- **SITE**: Rarely appropriate for clearance — avoid discounting the entire catalog to clear a few items.

When selecting ITEMS scope, prioritize the products with the worst velocity ratios (lowest first), up to the max of 5 productIds.

---

## Step 5: Convert category names to GUIDs (if CATEGORY scope)

If scope is CATEGORY, call `getCategoryIds` to convert category names to GUIDs.

- Never use category names as scope IDs — always use the GUID.
- Exclude the "All Products" system category.
- Max 3 categoryIds per discount rule.

---

## Step 6: Run guardrail checks

**IMPORTANT: Run both guardrail checks before creating the discount rule. Clearance discounts are the most likely to trigger margin warnings.**

### 6a: Discount Conflicts

1. Query existing active discount rules:

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/discount-rules/query`

**Request**:
```json
{
  "query": {
    "filter": {
      "active": true
    },
    "paging": {
      "limit": 100
    }
  }
}
```

2. Check for scope overlap. Clearance items that already have an active discount would stack — warn the merchant about combined discount depth.
3. Check for coupon stacking risks. A customer combining a clearance discount with a coupon code could get an unexpectedly deep total discount.

### 6b: Margin Protection

This check is especially critical for clearance:

- Verify `discount_percentage <= avg_profit_margin - 15%` for each candidate product.
- If the discount would push effective margin below 15%, warn the merchant: "This clearance discount of {discount}% on {product_name} would reduce the effective margin to {remaining_margin}%. The minimum margin threshold is 15%. Proceed?"
- If margin data is unavailable, apply extra caution — cap at 15% unless the merchant explicitly overrides.

---

## Step 7: Create the discount rule

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/discount-rules`

**Request** — 20% off specific slow-moving products:
```json
{
  "discountRule": {
    "name": "Clearance - Overstock Items 20% Off",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        },
        "scope": {
          "id": "slow-mover-product-uuid-1",
          "type": "SPECIFIC_PRODUCTS"
        }
      },
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        },
        "scope": {
          "id": "slow-mover-product-uuid-2",
          "type": "SPECIFIC_PRODUCTS"
        }
      },
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        },
        "scope": {
          "id": "slow-mover-product-uuid-3",
          "type": "SPECIFIC_PRODUCTS"
        }
      }
    ]
  }
}
```

**Response**:
```json
{
  "discountRule": {
    "id": "e5f6a7b8-c9d0-1234-ef01-345678901234",
    "revision": "1",
    "name": "Clearance - Overstock Items 20% Off",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        },
        "scope": {
          "id": "slow-mover-product-uuid-1",
          "type": "SPECIFIC_PRODUCTS"
        }
      },
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        },
        "scope": {
          "id": "slow-mover-product-uuid-2",
          "type": "SPECIFIC_PRODUCTS"
        }
      },
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        },
        "scope": {
          "id": "slow-mover-product-uuid-3",
          "type": "SPECIFIC_PRODUCTS"
        }
      }
    ]
  }
}
```

**Request** — clearance on an entire category:
```json
{
  "discountRule": {
    "name": "Clearance - Winter Collection 15% Off",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 15
        },
        "scope": {
          "id": "winter-collection-category-guid",
          "type": "COLLECTION"
        }
      }
    ]
  }
}
```

Save the returned `id` and `revision` for later management.

---

## Step 8: Verify the rule is active

1. Query discount rules to confirm the new rule exists and is `active: true`
2. Verify the correct products or category are targeted
3. Report to the merchant:
   > "Clearance discount is live: {discount}% off {number_of_products} slow-moving items. These products had a velocity ratio of {avg_velocity}, indicating high stock relative to sales. Monitor inventory levels — once stock clears, consider deactivating the rule."

---

## Branching logic

| Merchant intent | Scope | Discount depth | Notes |
|---|---|---|---|
| "Clear out old inventory" | ITEMS — top 5 slowest movers | Velocity-based (15-25%) | Target worst performers |
| "Clearance sale on winter items" | COLLECTION with category GUID | 15-20% | Category-wide clearance |
| "Get rid of product X" (specific) | SPECIFIC_PRODUCTS with product UUID | 20-25% (user may override) | Single product clearance |
| "Move stale stock across the store" | ITEMS — 5 worst velocity products | Velocity-based | Avoid SITE scope for clearance |
| "25% off these 3 items" (explicit) | SPECIFIC_PRODUCTS | 25% (user override) | Honor explicit request |

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `DISCOUNT_RULE_NOT_FOUND` | Rule ID doesn't exist | Re-query discount rules for current IDs |
| `REVISION_MISMATCH` | Revision doesn't match | Re-fetch rule for latest revision, then retry |
| No slow movers found | All products have healthy velocity ratios (> 0.3) | Inform merchant that inventory is balanced; no clearance needed |
| Margin violation | Discount would push margin below 15% | Reduce discount percentage or get explicit merchant override |
| Quantity data missing | Products lack inventory tracking | Cannot identify slow movers; ask merchant to enable inventory tracking or specify products manually |
| Max items exceeded | More than 5 slow-moving products identified | Select the 5 with worst velocity ratios; consider CATEGORY scope if they share a category |

## References

- [Discount Rules API](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/introduction)
