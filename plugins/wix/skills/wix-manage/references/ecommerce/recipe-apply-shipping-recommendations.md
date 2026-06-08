---
name: "Recipe: Apply Shipping Recommendations"
description: Applies AI-generated shipping recommendations to a Wix e-commerce store. Reads the current delivery profile and shipping options, then creates or updates shipping options based on recommendation data. Supports creating new options with conditional rates, updating existing options, and querying delivery profiles for region/carrier context.
---
# Apply Shipping Recommendations

## Prerequisites

- Wix Stores (or another eCommerce business solution) installed on the site
- Shipping recommendations data available (from the AI recommendation system or provided directly)

## Required APIs

- [Query Delivery Profiles](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-delivery-profiles)
- [Get Delivery Profile](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#get-delivery-profile)

---

## Step 1: Query the current shipping configuration

Call [Query Delivery Profiles](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-delivery-profiles) to understand the site's delivery setup — profiles, regions, carriers, and backup rates.

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

Save the profile `id`, `revision`, and each region's `id` and `active` status. Identify which regions have carriers with missing backup rates (`backupRate` absent or `backupRate.active: false`).

---

## Step 2: Query existing shipping options

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

Note: The response uses `deliveryRegionId` (singular) as the primary field linking an option to a region.

---

## Step 3: Apply recommendation — Create a new shipping option

When the recommendation action is `create_shipping_option`, create a new option linked to a specific delivery region.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options`

**Request** — flat rate example:
```json
{
  "shippingOption": {
    "title": "Express Shipping",
    "estimatedDeliveryTime": "1-2 business days",
    "deliveryRegionId": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
    "rates": [
      {
        "amount": "12.99",
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
    "id": "dece6160-4e72-4fcc-adcc-7607215edab0",
    "revision": "1",
    "createdDate": "2026-04-15T13:14:01.214Z",
    "updatedDate": "2026-04-15T13:14:01.214Z",
    "deliveryRegionId": "42b0ed3b-fc54-4ac0-89cf-5d2d17ec441c",
    "deliveryRegionIds": [],
    "title": "Express Shipping",
    "estimatedDeliveryTime": "1-2 business days",
    "rates": [
      {
        "amount": "12.99",
        "conditions": [],
        "multiplyByQuantity": false
      }
    ]
  }
}
```

**Request** — free shipping with price threshold:
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
            "value": "75"
          }
        ]
      }
    ]
  }
}
```

**Key field rules:**

| Field | Required | Notes |
|---|---|---|
| `title` | Yes | Display name at checkout |
| `estimatedDeliveryTime` | Yes | Free text shown to customers |
| `deliveryRegionId` | Yes | Region UUID from Step 1. Must use **singular** field, not `deliveryRegionIds` |
| `rates` | Yes | Array of rate objects |
| `rates[].amount` | Yes | Decimal string (`"5.99"`, `"0"` for free) |
| `rates[].multiplyByQuantity` | Yes | Almost always `false` |
| `rates[].conditions` | Yes | Empty array for flat rate; see condition types below |

**Condition types** (for tiered/conditional rates):

| Type | Description | Example |
|---|---|---|
| `BY_TOTAL_PRICE` | Cart total threshold | `"operator": "GTE", "value": "75"` |
| `BY_TOTAL_WEIGHT` | Weight threshold | `"operator": "LTE", "value": "10"` |
| `BY_TOTAL_QUANTITY` | Item count threshold | `"operator": "GTE", "value": "3"` |

Operators: `EQ`, `GT`, `GTE`, `LT`, `LTE`

---

## Step 4: Apply recommendation — Update an existing shipping option

When the recommendation action is `update_shipping_option`, update an existing option's title, delivery time, or rates.

**Endpoint**: `PATCH https://www.wixapis.com/ecom/v1/shipping-options/{shippingOptionId}`

Replace `{shippingOptionId}` with the option's `id` from Step 2.

**Request**:
```json
{
  "shippingOption": {
    "id": "c0e5be8f-5266-4720-a732-5f571e4750db",
    "revision": "1",
    "title": "Updated Standard Shipping",
    "estimatedDeliveryTime": "3-5 business days",
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
    "title": "Updated Standard Shipping",
    "estimatedDeliveryTime": "3-5 business days",
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

The `revision` field is required and must match the current revision. The response returns the incremented revision.

---

## Step 5: Verify the changes

After applying recommendations, query shipping options again (Step 2) to confirm the changes took effect. Verify:

- New options appear in the list with the correct title, rates, and region link
- Updated options reflect the new values and incremented revision
- The option is linked to the correct `deliveryRegionId`

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `deliveryRegionId is not a valid GUID` | Used `deliveryRegionIds` (plural) instead of `deliveryRegionId` (singular) in create request | Use the singular `deliveryRegionId` field |
| `SHIPPING_OPTION_NOT_FOUND` | The shipping option ID doesn't exist | Re-query shipping options to get current IDs |
| `REVISION_MISMATCH` | The `revision` doesn't match the current version | Re-fetch the option to get the latest revision, then retry |

## References

- [API: Shipping Delivery](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping)