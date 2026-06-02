---
name: "Flow: Bundle and Save"
description: Creates a discount campaign promoting product discovery and cross-selling by requiring minimum item quantities. Targets high-margin categories with complementary products.
layer: flow
references:
  - name: "Guardrail: Discount Conflicts"
    path: ecommerce/guardrail-discount-conflicts.md
    load: true
  - name: "Setup: Discount Rules"
    path: ecommerce/setup-discount-rules.md
    load: true
---
# Flow: Bundle & Save Campaign

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Guardrail: Discount Conflicts](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-discount-conflicts)
> - [Setup: Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/setup-discount-rules)

Creates a discount that rewards customers for purchasing multiple items, encouraging product discovery and cross-selling. The discount activates when the cart contains a minimum number of items, and targets categories or products where bundling makes strategic sense.

## Prerequisites

- Wix Stores installed on the site
- Products exist in the catalog across multiple categories
- Access to `getCatalogAnalytics` and `getProductCatalogData` tools
- Categories with 2+ products suitable for bundling

## Required APIs

- [Create Discount Rule](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/create-discount-rule)
- [Query Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/query-discount-rules)

---

## Step 1: Gather catalog data

Call `getCatalogAnalytics` and `getProductCatalogData` concurrently to assess the catalog's bundle potential.

**getCatalogAnalytics** call:
```
aggregates: min(price), max(price), avg(profitMargin), count
```

**getProductCatalogData** call:
```
ordered: price DESC, ordersCount DESC
```

Save the following values:
- `min_price`, `max_price` — price range determines viable bundle combinations
- `avg_profit_margin` — sets the discount ceiling
- `count` — catalog breadth; more products = more bundling options
- Top products by price and order count — identifies popular items for bundle anchoring

---

## Step 2: Analyze cross-sell patterns

Evaluate the catalog for bundling opportunities:

1. **Category diversity**: Look for categories with multiple products at complementary price points (e.g., a $50 main item + $15 accessories).
2. **Price range suitability**: Wide price ranges (large gap between min_price and max_price) suggest tiered bundles. Narrow ranges suggest quantity-based bundles.
3. **High-margin categories**: Categories with above-average profit margin are better candidates because the discount erodes less absolute profit.
4. **Popular + discoverable**: Pair best-selling products (high ordersCount) with lower-visibility products to drive discovery.

---

## Step 3: Set minimum item quantity

Determine the `minItemQuantity` based on catalog characteristics:

| Catalog Profile | Recommended minItemQuantity | Rationale |
|---|---|---|
| High-price items (avg price > price_p75) | 2 | Customers are less likely to buy 3+ expensive items |
| Medium-price items | 2-3 | Standard bundle size |
| Low-price items (avg price < price_p25) | 3-4 | Lower price per item makes larger bundles feasible |
| Many items in category (count > 10) | 3 | More products to choose from |
| Few items in category (count <= 5) | 2 | Limited selection constrains bundle size |

Default to `minItemQuantity: 2` if data is ambiguous.

---

## Step 4: Select discount percentage

Scale the discount to the average margin, rewarding multi-item purchases without eroding profitability:

| Margin Tier | Condition | Recommended Discount |
|---|---|---|
| Low margin | `avg_profit_margin < 25%` | 10% |
| Medium margin | `25% <= avg_profit_margin <= 50%` | 15% |
| High margin | `avg_profit_margin > 50%` | 20% |
| No data | Margin unavailable | 10% |

Verify that the discount respects the global cap of 25% and the minimum margin threshold of 15% (`discount <= avg_profit_margin - 15%`).

---

## Step 5: Determine discount scope

Select the scope based on bundling analysis:

- **CATEGORY** (preferred): When analytics show a clear category with cross-sell potential — multiple products, high margin, complementary items. Target that category.
- **ITEMS**: When specific complementary products are identified for bundling (max 5 productIds). Use when cross-sell pairs are specific rather than category-wide.
- **SITE**: When the goal is store-wide multi-buy incentive. Less targeted but simpler.

---

## Step 6: Convert category names to GUIDs (if CATEGORY scope)

If scope is CATEGORY, call `getCategoryIds` to convert category names to GUIDs.

- Never use category names as scope IDs — always use the GUID.
- Exclude the "All Products" system category.
- Max 3 categoryIds per discount rule.

---

## Step 7: Run guardrail checks

**Run the Guardrail: Discount Conflicts checks before creating the rule.**

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

2. Check for scope overlap with existing rules. Bundle discounts are especially prone to stacking — a customer buying 3 items in a category with both a bundle discount and a catalog-wide sale would get both.
3. Check for coupon stacking risks.
4. If conflicts found, present to merchant and get confirmation.

---

## Step 8: Create the discount rule with minItemQuantity condition

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/discount-rules`

**Request** — Buy 2+ items from a category, get 15% off:
```json
{
  "discountRule": {
    "name": "Buy 2+, Save 15% on Accessories",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 15
        },
        "scope": {
          "id": "accessories-category-guid",
          "type": "COLLECTION"
        }
      }
    ],
    "conditions": {
      "itemQuantityRange": {
        "from": 2
      }
    }
  }
}
```

**Response**:
```json
{
  "discountRule": {
    "id": "d4e5f6a7-b8c9-0123-def0-234567890123",
    "revision": "1",
    "name": "Buy 2+, Save 15% on Accessories",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 15
        },
        "scope": {
          "id": "accessories-category-guid",
          "type": "COLLECTION"
        }
      }
    ],
    "conditions": {
      "itemQuantityRange": {
        "from": 2
      }
    }
  }
}
```

**Request** — Buy 3+ specific items, get 10% off:
```json
{
  "discountRule": {
    "name": "Bundle 3 Best Sellers, Save 10%",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 10
        },
        "scope": {
          "id": "product-uuid-1",
          "type": "SPECIFIC_PRODUCTS"
        }
      },
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 10
        },
        "scope": {
          "id": "product-uuid-2",
          "type": "SPECIFIC_PRODUCTS"
        }
      },
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 10
        },
        "scope": {
          "id": "product-uuid-3",
          "type": "SPECIFIC_PRODUCTS"
        }
      }
    ],
    "conditions": {
      "itemQuantityRange": {
        "from": 3
      }
    }
  }
}
```

Save the returned `id` and `revision` for later management.

---

## Step 9: Verify the rule is active

1. Query discount rules to confirm the new rule exists and is `active: true`
2. Verify the minItemQuantity condition is correctly set
3. Report to the merchant:
   > "Bundle discount is live: {discount}% off when buying {minItemQuantity}+ items from {scope description}. This encourages customers to explore more products and increases items per order."

---

## Branching logic

| Merchant intent | Scope | minItemQuantity | Discount |
|---|---|---|---|
| "Encourage people to buy more" | Determined by analytics | 2-3 | Margin-tiered |
| "Bundle accessories together" | COLLECTION with category GUID | 2 | Margin-tiered |
| "Buy 3 get 20% off these products" (explicit) | SPECIFIC_PRODUCTS with product GUIDs | 3 (user override) | 20% (user override) |
| "Multi-buy deal on everything" | CATALOG (site-wide) | 2 | Margin-tiered |
| "Promote these 4 items as a set" | SPECIFIC_PRODUCTS (max 5) | 2-4 | Margin-tiered |

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `DISCOUNT_RULE_NOT_FOUND` | Rule ID doesn't exist | Re-query discount rules for current IDs |
| `REVISION_MISMATCH` | Revision doesn't match | Re-fetch rule for latest revision, then retry |
| Too few products in category | Category has only 1 product — bundling not viable | Switch to SITE scope or suggest a different category |
| Margin data unavailable | No profit margin data in catalog | Default to 10% discount |
| Category GUID not found | Category name doesn't match any collection | Re-query categories or fall back to SITE scope |
| Max items exceeded | More than 5 productIds specified | Reduce to top 5 by ordersCount or switch to CATEGORY scope |

## References

- [Discount Rules API](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/introduction)
