---
name: "Flow: Optimize Shipping Rates"
description: Analyzes catalog price distribution and current rate structure to recommend optimal shipping rate strategy. Handles flat-to-tiered conversion, tier gap detection, and per-item penalty removal.
layer: flow
references:
  - name: "Guardrail: Rate Pricing Sanity"
    path: ecommerce/guardrail-rate-pricing-sanity.md
    load: true
  - name: "Setup: Shipping Rates"
    path: ecommerce/setup-shipping-rates.md
    load: true
---
# Flow: Optimize Shipping Rates

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Guardrail: Rate Pricing Sanity](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-rate-pricing-sanity)
> - [Setup: Shipping Rates](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/setup-shipping-rates)

Analyzes the site's catalog price distribution and current shipping rate structure to determine if the rate strategy is optimal. Recommends and applies changes when flat rates should become tiered, when tier gaps exist, or when per-item penalties are harming conversion.

## Prerequisites

- Wix Stores (or another eCommerce business solution) installed on the site
- Catalog stats available (product_count, price quantiles, price_stddev)
- Site metrics available for AOV calculation
- At least one shipping option configured

## Required APIs

- [Query Shipping Options](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-shipping-options)
- [Update Shipping Option](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#update-shipping-option)
- [Create Shipping Option](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#create-shipping-option)

---

## Step 1: Gather catalog price distribution

Retrieve catalog statistics for the "All Products" category group. Required fields:

| Metric | Description |
|---|---|
| `product_count` | Total number of products |
| `price_min` | Lowest product price |
| `price_max` | Highest product price |
| `price_avg` | Average product price |
| `price_stddev` | Standard deviation of prices |
| `price_p25` | 25th percentile price |
| `price_p50` | 50th percentile (median) price |
| `price_p75` | 75th percentile price |
| `price_p90` | 90th percentile price |

### 1a: Calculate price spread ratio

```
price_spread_ratio = price_max / price_min
```

This ratio indicates how diverse the catalog pricing is. A ratio of 3 means the most expensive product is 3x the cheapest; a ratio of 50 means extreme price diversity.

---

## Step 2: Query current shipping options

Retrieve all shipping options to analyze the existing rate structure.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options/query`

**Request**:
```json
{
  "query": {
    "cursorPaging": {
      "limit": 100
    }
  }
}
```

**Response**:
```json
{
  "shippingOptions": [
    {
      "id": "c0e5be8f-5266-4720-a732-5f571e4750db",
      "revision": "1",
      "deliveryRegionId": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
      "deliveryRegionIds": [],
      "title": "Standard Shipping",
      "estimatedDeliveryTime": "5-7 business days",
      "rates": [
        {
          "amount": "15.00",
          "conditions": [],
          "multiplyByQuantity": false
        }
      ]
    }
  ],
  "pagingMetadata": {
    "count": 1,
    "cursors": {},
    "hasNext": false
  }
}
```

For each option, classify its rate structure:
- **Flat rate**: `conditions[]` is empty
- **Tiered**: Multiple rates with `BY_TOTAL_PRICE`, `BY_TOTAL_WEIGHT`, or `BY_TOTAL_QUANTITY` conditions
- **Free shipping**: `amount="0"`
- **Per-item**: `multiplyByQuantity=true`

---

## Step 3: Apply the rate strategy decision tree

### 3a: Check for per-item penalty (highest priority)

If any shipping option has `multiplyByQuantity=true`, flag it immediately.

**Problem**: Per-item charging means shipping cost = `amount x cart quantity`. A $5 rate on a 5-item order charges $25 for shipping. This discourages larger carts and directly conflicts with AOV growth goals.

**Recommendation**: Switch to flat rate or tiered pricing. Update the option to set `multiplyByQuantity=false`.

### 3b: Evaluate flat-to-tiered conversion

Check ALL three conditions. If all are true, recommend converting flat rates to price-based tiers:

| Condition | Threshold |
|---|---|
| `price_spread_ratio > 10` | Catalog has extreme price diversity |
| `price_stddev > price_avg x 0.5` | High variance in pricing |
| Only flat rates currently exist | No tiered structure in place |

**If all three conditions are met**, recommend price-based tiers:

| Tier | Price Range | Rate Strategy |
|---|---|---|
| Tier 1 | Orders below `price_p50` | Lower flat rate |
| Tier 2 | Orders `price_p50` to `price_p75` | Standard rate |
| Tier 3 | Orders above `price_p75` | Higher rate or free shipping |

### 3c: Confirm flat rate is optimal

If ALL of the following are true, flat rate is the correct strategy -- no changes needed:

| Condition | Threshold |
|---|---|
| `price_spread_ratio <= 3` | Narrow price range |
| `price_stddev < price_avg x 0.3` | Low variance |

Report: "Your catalog has a narrow price range. Flat rate shipping is the optimal strategy. No changes recommended."

### 3d: Check for tier gaps in existing tiered options

For options that already use tiered pricing (weight-based or price-based conditions):

1. Sort all rates by their condition `value`
2. Look for gaps between tier boundaries

**Example gap**: Tier 1 has `LTE 5` (kg or $), Tier 2 has `GT 10`. A cart at 7 matches neither tier and gets no shipping rate for this option.

**Fix**: Adjust condition boundaries to ensure complete, contiguous coverage.

---

## Step 4: Apply recommended changes

### 4a: Fix per-item penalty

Update the shipping option to disable per-item multiplication.

**Endpoint**: `PATCH https://www.wixapis.com/ecom/v1/shipping-options/{shippingOptionId}`

**Request**:
```json
{
  "shippingOption": {
    "id": "c0e5be8f-5266-4720-a732-5f571e4750db",
    "revision": "1",
    "title": "Standard Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "rates": [
      {
        "amount": "9.99",
        "multiplyByQuantity": false,
        "conditions": []
      }
    ]
  }
}
```

**Response**:
```json
{
  "shippingOption": {
    "id": "c0e5be8f-5266-4720-a732-5f571e4750db",
    "revision": "2",
    "createdDate": "2026-04-14T14:43:24.804Z",
    "updatedDate": "2026-04-15T13:14:13.716Z",
    "deliveryRegionId": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
    "deliveryRegionIds": [],
    "title": "Standard Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "rates": [
      {
        "amount": "9.99",
        "conditions": [],
        "multiplyByQuantity": false
      }
    ]
  }
}
```

### 4b: Create tiered shipping option

When converting from flat to tiered, create a new option with price-based tiers. Use catalog quantiles to set tier boundaries.

**Example** with `price_p50=$35`, `price_p75=$80`:

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options`

**Request**:
```json
{
  "shippingOption": {
    "title": "Standard Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "deliveryRegionId": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
    "rates": [
      {
        "amount": "9.99",
        "multiplyByQuantity": false,
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "LTE",
            "value": "35"
          }
        ]
      },
      {
        "amount": "7.99",
        "multiplyByQuantity": false,
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "GT",
            "value": "35"
          },
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "LTE",
            "value": "80"
          }
        ]
      },
      {
        "amount": "0",
        "multiplyByQuantity": false,
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "GT",
            "value": "80"
          }
        ]
      }
    ]
  }
}
```

**Response**:
```json
{
  "shippingOption": {
    "id": "f3a4b5c6-d7e8-9012-fghi-345678901def",
    "revision": "1",
    "createdDate": "2026-04-15T14:00:00.000Z",
    "updatedDate": "2026-04-15T14:00:00.000Z",
    "deliveryRegionId": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
    "deliveryRegionIds": [],
    "title": "Standard Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "rates": [
      {
        "amount": "9.99",
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "LTE",
            "value": "35"
          }
        ],
        "multiplyByQuantity": false
      },
      {
        "amount": "7.99",
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "GT",
            "value": "35"
          },
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "LTE",
            "value": "80"
          }
        ],
        "multiplyByQuantity": false
      },
      {
        "amount": "0",
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "GT",
            "value": "80"
          }
        ],
        "multiplyByQuantity": false
      }
    ]
  }
}
```

**Tier logic**: Multiple conditions within the same rate use AND logic. The middle tier (`GT 35 AND LTE 80`) matches cart totals between $35 and $80.

---

## Step 5: Verify updated rates

Re-query shipping options to confirm changes took effect.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options/query`

Verify:
1. Per-item options now have `multiplyByQuantity=false`
2. Tiered options have contiguous tier boundaries with no gaps
3. All options have `estimatedDeliveryTime` populated
4. Rate amounts are reasonable (no single rate exceeds 15% of effective_aov)
5. Updated options show incremented `revision` values

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `SHIPPING_OPTION_NOT_FOUND` | Option ID doesn't exist | Re-query shipping options to get current IDs |
| `REVISION_MISMATCH` | Revision doesn't match the current version | Re-fetch the option for the latest revision, then retry |
| `deliveryRegionId is not a valid GUID` | Used `deliveryRegionIds` (plural) instead of `deliveryRegionId` (singular) | Use the singular `deliveryRegionId` field |
| Tier gap detected after update | Condition boundaries don't cover all ranges | Verify tier boundaries are contiguous: use LTE for upper bounds and GT for lower bounds of adjacent tiers |
| Rate exceeds 15% of AOV | Shipping cost is a cart abandonment risk | Lower the rate amount or add a free shipping tier for larger orders |

## References

- [API: Shipping Delivery](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping)
