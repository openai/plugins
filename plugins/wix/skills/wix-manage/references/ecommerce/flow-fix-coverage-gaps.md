---
name: "Flow: Fix Coverage Gaps"
description: Detects active delivery regions with zero shipping options and creates standard shipping for them. Cross-references delivery profiles with shipping options to find regions where customers cannot complete checkout.
layer: flow
references:
  - name: "Guardrail: Shipping Health"
    path: ecommerce/guardrail-shipping-health.md
    load: true
  - name: "Setup: Shipping Regions"
    path: ecommerce/setup-shipping-regions.md
    load: true
---
# Flow: Fix Shipping Coverage Gaps

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Guardrail: Shipping Health](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-shipping-health)
> - [Setup: Shipping Regions](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/setup-shipping-regions)

Detects delivery regions where customers cannot see any shipping options at checkout and creates standard shipping to fill the gaps. A coverage gap is a HIGH priority blocking issue -- customers in affected destinations literally cannot complete a purchase.

## Prerequisites

- Wix Stores (or another eCommerce business solution) installed on the site
- Site metrics available for AOV-based rate calculation (effective_aov)
- Delivery profiles configured with at least one region

## Required APIs

- [Query Delivery Profiles](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-delivery-profiles)
- [Query Shipping Options](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-shipping-options)
- [Create Shipping Option](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#create-shipping-option)

---

## Step 1: Query all delivery profiles

Retrieve all delivery profiles to build a complete map of regions and their carriers.

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

**Response**:
```json
{
  "deliveryProfiles": [
    {
      "id": "6a9b2f9b-533a-4d0d-ac8d-64ec3f32fcbd",
      "name": "General profile",
      "default": true,
      "deliveryRegions": [
        {
          "id": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
          "name": "Domestic",
          "active": true,
          "deliveryCarriers": [
            {
              "appId": "45c44b27-ca7b-4891-8c0d-1747d588b835",
              "additionalCharges": []
            }
          ],
          "destinations": [
            {
              "countryCode": "GB",
              "subdivisions": []
            }
          ]
        },
        {
          "id": "a1c2d3e4-f5a6-7890-bcde-f12345678901",
          "name": "International",
          "active": true,
          "deliveryCarriers": [
            {
              "appId": "45c44b27-ca7b-4891-8c0d-1747d588b835",
              "additionalCharges": []
            }
          ],
          "destinations": []
        }
      ],
      "revision": "43",
      "createdDate": "2025-10-26T11:05:10.774Z",
      "updatedDate": "2026-04-14T14:43:25.397Z"
    }
  ],
  "pagingMetadata": {
    "count": 1,
    "cursors": {},
    "hasNext": false
  }
}
```

Save every region `id`, `name`, `active` status, and carrier `appId` values.

---

## Step 2: Query all shipping options

Retrieve all shipping options to determine which regions already have coverage.

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
      "createdDate": "2026-04-14T14:43:24.804Z",
      "updatedDate": "2026-04-14T14:43:24.804Z",
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

Build a map of `deliveryRegionId` to the count of shipping options linked to it.

---

## Step 3: Cross-reference regions and options to find gaps

For each `deliveryRegion` across all profiles, apply these checks in order:

### 3a: Skip externally managed regions

If ALL carriers in the region have an external appId (e.g., Shippo `appId: "2b1943e2-3fc2-47bc-be56-3d402e5966d7"`), skip the region entirely. External carriers manage their own rates.

### 3b: Skip inactive regions

If `active=false`, skip. Inactive regions are not shown at checkout regardless of shipping options.

### 3c: Count linked shipping options

Count how many shipping options have this region's `id` in their `deliveryRegionId` field. If the count is **zero**, this is a **coverage gap**.

**Severity**: HIGH -- blocking. Customers shipping to this region's destinations cannot see any shipping options and cannot complete checkout.

### 3d: Check for options linked only to inactive regions

For each shipping option, check if ALL of its linked regions have `active=false`. If so, the option exists but is invisible at checkout. This is a configuration issue worth flagging.

### 3e: Check for orphaned options

For each shipping option, verify that its `deliveryRegionId` actually exists in one of the delivery profiles. If the region no longer exists, the option is orphaned -- it exists in the system but is never shown to customers.

---

## Step 4: Create shipping options for each gap

For each region identified as having zero coverage, create a standard shipping option and a free shipping tier.

### 4a: Calculate rates

- **Standard rate**: 5-10% of `effective_aov` (e.g., if effective_aov is $60, rate is $3.00-$6.00)
- **Free shipping threshold**: `effective_aov x 1.2` (e.g., if effective_aov is $60, threshold is $72)
- **Always set `estimatedDeliveryTime`** -- never leave it empty. Use "5-7 business days" for domestic, "7-14 business days" for international.

### 4b: Create standard shipping option

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options`

**Request**:
```json
{
  "shippingOption": {
    "title": "Standard Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "deliveryRegionId": "a1c2d3e4-f5a6-7890-bcde-f12345678901",
    "rates": [
      {
        "amount": "4.99",
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
    "id": "b2c3d4e5-f6a7-8901-cdef-234567890abc",
    "revision": "1",
    "createdDate": "2026-04-15T13:14:01.214Z",
    "updatedDate": "2026-04-15T13:14:01.214Z",
    "deliveryRegionId": "a1c2d3e4-f5a6-7890-bcde-f12345678901",
    "deliveryRegionIds": [],
    "title": "Standard Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "rates": [
      {
        "amount": "4.99",
        "conditions": [],
        "multiplyByQuantity": false
      }
    ]
  }
}
```

### 4c: Create free shipping option with threshold

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options`

**Request**:
```json
{
  "shippingOption": {
    "title": "Free Shipping",
    "estimatedDeliveryTime": "5-7 business days",
    "deliveryRegionId": "a1c2d3e4-f5a6-7890-bcde-f12345678901",
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

---

## Step 5: Verify the fix

After creating options for all gaps, re-query shipping options to confirm:

1. New options appear in the list with correct titles and rates
2. Each new option is linked to the correct `deliveryRegionId`
3. The `estimatedDeliveryTime` is populated (not empty)
4. No regions remain uncovered

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options/query`

Use the same request from Step 2 and verify the count now covers all active, non-external regions.

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `deliveryRegionId is not a valid GUID` | Used `deliveryRegionIds` (plural) instead of `deliveryRegionId` (singular) in create request | Use the singular `deliveryRegionId` field |
| `SHIPPING_OPTION_NOT_FOUND` | The shipping option ID doesn't exist | Re-query shipping options to get current IDs |
| `REVISION_MISMATCH` | The `revision` doesn't match the current version | Re-fetch the option to get the latest revision, then retry |
| Region appears covered but customers still can't check out | Region has `active=false` | Check region active status in the delivery profile; activate the region if intended |
| Option exists but not visible at checkout | Option linked to an inactive or deleted region | Verify region exists and `active=true` in the delivery profile |

## References

- [API: Shipping Delivery](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping)
