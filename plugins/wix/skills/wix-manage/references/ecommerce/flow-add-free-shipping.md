---
name: "Flow: Add Free Shipping"
description: Creates a free shipping option with an AOV-calibrated threshold to reduce cart abandonment and increase average order value. Validates threshold against catalog price distribution.
layer: flow
references:
  - name: "Guardrail: Rate Pricing Sanity"
    path: ecommerce/guardrail-rate-pricing-sanity.md
    load: true
  - name: "Setup: Shipping Rates"
    path: ecommerce/setup-shipping-rates.md
    load: true
---
# Flow: Add Free Shipping

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Guardrail: Rate Pricing Sanity](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-rate-pricing-sanity)
> - [Setup: Shipping Rates](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/setup-shipping-rates)

Adds a free shipping option with an optimal threshold calibrated against the site's average order value and catalog price distribution. Free shipping is the single most effective lever for reducing cart abandonment at the delivery step.

## Prerequisites

- Wix Stores (or another eCommerce business solution) installed on the site
- Site metrics available (revenue, ordersCount) for AOV calculation
- Catalog stats available (price quantiles) for threshold calibration
- At least one active delivery region configured

## Required APIs

- [Query Shipping Options](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-shipping-options)
- [Create Shipping Option](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#create-shipping-option)
- [Update Shipping Option](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#update-shipping-option)
- [Query Delivery Profiles](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-delivery-profiles)

---

## Step 1: Check for existing free shipping

Query all shipping options and check if free shipping already exists.

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

Scan the response for any option matching either condition:
- `rates[].amount` equals `"0"`
- `title` contains "free" (case-insensitive match)

If free shipping already exists, proceed to Step 2 (threshold calibration check). If no free shipping exists, skip to Step 3.

---

## Step 2: Validate existing free shipping threshold

If a free shipping option already exists, extract its threshold and validate it.

### 2a: Extract the threshold

Find the `BY_TOTAL_PRICE` `GTE` condition value from the free rate's `conditions[]` array.

Example rate with threshold:
```json
{
  "amount": "0",
  "multiplyByQuantity": false,
  "conditions": [
    {
      "type": "BY_TOTAL_PRICE",
      "operator": "GTE",
      "value": "75"
    }
  ]
}
```

If there is no condition (unconditional free shipping), note this but do not flag it as an error -- the merchant may intentionally offer free shipping on all orders.

### 2b: Evaluate threshold against AOV

| Condition | Diagnosis | Recommendation |
|---|---|---|
| `threshold > AOV x 2` | Too high -- customers rarely qualify for free shipping | Lower the threshold to `AOV x 1.2` |
| `threshold < AOV x 0.8` | Too low -- margin erosion risk, most orders qualify automatically | Raise the threshold to `AOV x 1.2` |
| `AOV x 0.8 <= threshold <= AOV x 2` | Acceptable range | No change needed |

If the threshold needs adjustment, update the shipping option via PATCH (see Step 5 for the update pattern).

---

## Step 3: Run AOV sanity check

Before calculating a threshold, validate that AOV is reliable by comparing it against catalog price distribution.

### 3a: Get catalog price statistics

Use the catalog stats to retrieve price quantiles for the "All Products" category group:
- `price_p25` -- 25th percentile product price
- `price_p50` -- 50th percentile (median) product price
- `price_p75` -- 75th percentile product price
- `price_p90` -- 90th percentile product price

### 3b: Determine effective_aov

| Condition | Interpretation | Action |
|---|---|---|
| `AOV < price_p25` | Anomalous -- AOV is below 75% of product prices | Override: use `price_p50` as `effective_aov` |
| `AOV > price_p90` | Possible bulk/combo orders | Use AOV but note the discrepancy |
| `price_p25 <= AOV <= price_p90` | Reasonable | Use AOV as `effective_aov` |

---

## Step 4: Calculate optimal free shipping threshold

Apply enhanced calibration using both `effective_aov` and catalog stats:

| Condition | Threshold Formula | Rationale |
|---|---|---|
| `price_p75 > effective_aov x 1.5` | `price_p50 x 1.5` | High-price items skew the catalog; threshold encourages 2-item orders of mid-range products |
| `price_p75 < effective_aov` | `effective_aov x 1.2` | Most products are lower-priced; threshold encourages adding items to cart |
| Default (neither condition) | `max(effective_aov x 1.2, price_p75)` | Standard calibration balancing reach and margin |

**Example calculation**:
- `effective_aov` = $60
- `price_p50` = $35, `price_p75` = $55
- `price_p75 ($55) < effective_aov ($60)` --> use `effective_aov x 1.2` = $72
- Threshold = $72

---

## Step 5: Identify the target delivery region

Query delivery profiles to find the primary/domestic active region.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/query`

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

Select the region where:
1. `active=true`
2. `destinations[].countryCode` matches the site's primary country
3. Falls within the default delivery profile

Save the region's `id` as the `deliveryRegionId` for the new option.

---

## Step 6: Create the free shipping option

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options`

**Request**:
```json
{
  "shippingOption": {
    "title": "Free Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "deliveryRegionId": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
    "rates": [
      {
        "amount": "0",
        "multiplyByQuantity": false,
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "GTE",
            "value": "72"
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
    "id": "dece6160-4e72-4fcc-adcc-7607215edab0",
    "revision": "1",
    "createdDate": "2026-04-15T13:14:01.214Z",
    "updatedDate": "2026-04-15T13:14:01.214Z",
    "deliveryRegionId": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
    "deliveryRegionIds": [],
    "title": "Free Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "rates": [
      {
        "amount": "0",
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "GTE",
            "value": "72"
          }
        ],
        "multiplyByQuantity": false
      }
    ]
  }
}
```

**Key field rules**:

| Field | Value | Notes |
|---|---|---|
| `title` | `"Free Shipping"` | Display name at checkout |
| `estimatedDeliveryTime` | `"5-7 business days"` | Always populate -- never leave empty |
| `deliveryRegionId` | Region UUID | Use singular field, not `deliveryRegionIds` |
| `rates[].amount` | `"0"` | Decimal string for free |
| `rates[].multiplyByQuantity` | `false` | Always false for free shipping |
| `rates[].conditions[].type` | `"BY_TOTAL_PRICE"` | Cart total threshold |
| `rates[].conditions[].operator` | `"GTE"` | Greater than or equal to |
| `rates[].conditions[].value` | Threshold as string | Calculated in Step 4 |

---

## Step 7: Verify the option appears in checkout

Re-query shipping options to confirm the new free shipping option is live.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options/query`

Verify:
1. The new option appears with `title: "Free Shipping"` and `amount: "0"`
2. The condition shows the correct threshold value
3. The option is linked to the correct `deliveryRegionId`
4. The linked region has `active=true` in its delivery profile

Report to the merchant:
> "Free shipping created with a $[threshold] minimum order. Customers spending $[threshold] or more will see free shipping at checkout. This threshold is calibrated to your average order value to encourage larger carts while protecting margins."

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `deliveryRegionId is not a valid GUID` | Used `deliveryRegionIds` (plural) instead of `deliveryRegionId` (singular) | Use the singular `deliveryRegionId` field |
| `SHIPPING_OPTION_NOT_FOUND` | Option ID doesn't exist when trying to update | Re-query shipping options to get current IDs |
| `REVISION_MISMATCH` | Revision doesn't match the current version when updating | Re-fetch the option for the latest revision, then retry |
| Threshold seems unreasonable | AOV data is unreliable (too few orders, data anomaly) | Run the AOV sanity check (Step 3) and use `effective_aov` instead of raw AOV |
| Free shipping not visible at checkout | Region linked to the option has `active=false` | Check region active status and activate if intended |

## References

- [API: Shipping Delivery](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping)
