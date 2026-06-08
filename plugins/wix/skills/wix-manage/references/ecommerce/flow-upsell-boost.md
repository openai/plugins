---
name: "Flow: Upsell Boost"
description: Creates a discount campaign to increase average order value by setting minimum subtotal conditions above current AOV. Uses margin-based discount tiers and targets high-margin categories.
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
# Flow: Upsell Boost Campaign

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Guardrail: Discount Conflicts](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-discount-conflicts)
> - [Guardrail: Margin Protection](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-margin-protection)
> - [Setup: Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/setup-discount-rules)

Creates a discount that incentivizes customers to spend more per order by setting a minimum subtotal threshold above the store's current AOV. The discount percentage is scaled to the store's average profit margin, and the scope targets high-margin categories or products.

## Prerequisites

- Wix Stores installed on the site
- Products exist in the catalog with price data
- Access to `getCatalogAnalytics` and `getProductCatalogData` tools
- AOV data available from site metrics (revenue / ordersCount)

## Required APIs

- [Create Discount Rule](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/create-discount-rule)
- [Query Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/query-discount-rules)

---

## Step 1: Gather catalog data and site metrics

Call `getCatalogAnalytics` and `getProductCatalogData` concurrently to collect pricing, margin, and product data.

**getCatalogAnalytics** call:
```
aggregates: count, quantiles([0.5, 0.75, 0.9], price), avg(profitMargin)
```

**getProductCatalogData** call:
```
ordered: price DESC, ordersCount DESC
```

Also retrieve site-level AOV from `getSiteData` (AOV = revenue / ordersCount). Run the AOV sanity check: if AOV < price_p25, override with price_p50 as the effective AOV.

Save the following values:
- `effective_aov` — the validated average order value
- `avg_profit_margin` — average profit margin across the catalog
- `price_p50`, `price_p75`, `price_p90` — pricing quantiles
- Top products by price and order volume

---

## Step 2: Determine margin tier and calculate discount + minSubTotal

Use the average profit margin to select the appropriate discount and threshold tier.

| Margin Tier | Condition | Max Discount | minSubTotal Formula |
|---|---|---|---|
| Low margin | `avg_profit_margin < 25%` | 10% | `1.15 x effective_aov` |
| Medium margin | `25% <= avg_profit_margin <= 50%` | 15% | `1.3 x effective_aov` |
| High margin | `avg_profit_margin > 50%` | 20% | `1.5 x effective_aov` |
| No data | Margin data unavailable | 10% | `1.15 x effective_aov` |

Example: If `effective_aov` = $150 and `avg_profit_margin` = 35% (medium), then max discount = 15% and raw minSubTotal = $195.

---

## Step 3: Round minSubTotal (CRITICAL)

**minSubTotal MUST be rounded UP to the nearest $5 increment** (the result mod 5 must equal 0). Always round UP, never down.

| Raw Value | Rounded Value |
|---|---|
| $195 | $195 (already divisible by 5) |
| $217 | $220 |
| $223 | $225 |
| $199 | $200 |
| $172.50 | $175 |
| $201 | $205 |

Formula: `minSubTotal = ceil(raw_value / 5) * 5`

---

## Step 4: Determine discount scope

Select the scope based on analytics data:

- **CATEGORY** (preferred): When analytics show a clear high-margin category opportunity. Target the category with the highest profit margin that also has sufficient product count.
- **ITEMS**: When specific high-margin products stand out as upsell candidates (max 5 productIds).
- **SITE** (fallback): When no single category or product group dominates, apply catalog-wide.

---

## Step 5: Convert category names to GUIDs (if CATEGORY scope)

If scope is CATEGORY, call `getCategoryIds` to convert human-readable category names into GUIDs. **Never output category names directly as scope IDs.**

Exclude the "All Products" system category — it contains every product and would effectively make the discount site-wide.

Max 3 categoryIds per discount rule.

---

## Step 6: Run guardrail checks

**IMPORTANT: Run both guardrail checks before creating the discount rule.**

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

2. Check for scope overlap, time overlap, and coupon stacking risks with the planned upsell discount.
3. If conflicts found, present to merchant and get confirmation before proceeding.

### 6b: Margin Protection

Verify that `discount_percentage <= avg_profit_margin - 15%` (minMarginPct). If the discount would push effective margin below 15%, warn the merchant.

The global discount cap is 25%. Do not exceed this unless the merchant explicitly overrides it.

---

## Step 7: Create the discount rule

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/discount-rules`

**Request** — 15% off orders over $195, scoped to a category:
```json
{
  "discountRule": {
    "name": "Spend $195+, Get 15% Off",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 15
        },
        "scope": {
          "id": "category-guid-here",
          "type": "COLLECTION"
        }
      }
    ],
    "conditions": {
      "subtotalRange": {
        "from": "195.00"
      }
    }
  }
}
```

**Response**:
```json
{
  "discountRule": {
    "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "revision": "1",
    "name": "Spend $195+, Get 15% Off",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 15
        },
        "scope": {
          "id": "category-guid-here",
          "type": "COLLECTION"
        }
      }
    ],
    "conditions": {
      "subtotalRange": {
        "from": "195.00"
      }
    }
  }
}
```

**Request** — site-wide fallback example:
```json
{
  "discountRule": {
    "name": "Spend $175+, Get 10% Off Everything",
    "active": true,
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 10
        },
        "scope": {
          "id": "catalog",
          "type": "CATALOG"
        }
      }
    ],
    "conditions": {
      "subtotalRange": {
        "from": "175.00"
      }
    }
  }
}
```

Save the returned `id` and `revision` for later management.

---

## Step 8: Verify the rule is active

1. Query discount rules to confirm the new rule exists and is `active: true`
2. Verify the minSubTotal condition is correctly set
3. Report to the merchant:
   > "Upsell discount is live: {discount}% off on orders over ${minSubTotal} for {scope description}. This threshold is {percentage}% above your current average order value of ${effective_aov}, designed to incentivize higher spending."

---

## Branching logic

| Merchant intent | Scope | Discount | minSubTotal |
|---|---|---|---|
| "Increase average order value" | Determined by analytics (CATEGORY preferred) | Margin-tiered | Calculated from AOV |
| "Get people to spend more on electronics" | COLLECTION with electronics category GUID | Margin-tiered | Calculated from AOV |
| "20% off orders over $200" (explicit) | As specified by merchant | 20% (user override) | $200 (user override) |
| "Reward big spenders" | CATALOG (site-wide) | Margin-tiered | Calculated from AOV |

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `DISCOUNT_RULE_NOT_FOUND` | Rule ID doesn't exist | Re-query discount rules for current IDs |
| `REVISION_MISMATCH` | Revision doesn't match | Re-fetch rule for latest revision, then retry |
| AOV unavailable | No revenue or order data | Use price_p50 from catalog analytics as AOV proxy |
| Margin data unavailable | No profit margin data in catalog | Default to low-margin tier (10% discount, 1.15x AOV) |
| Category GUID not found | Category name doesn't match any collection | Re-query categories or fall back to SITE scope |

## References

- [Discount Rules API](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/introduction)
