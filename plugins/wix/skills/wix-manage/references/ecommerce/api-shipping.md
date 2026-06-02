---
name: "API: Shipping Delivery"
description: REST API reference for Shipping Options and Delivery Profiles. Covers CRUD operations, region/carrier management, and query patterns for both services. Internal reference — these APIs are not yet published in public docs.
layer: config
---
# API: Shipping Delivery

Two services govern the shipping configuration of a Wix eCommerce store:

- **Delivery Profiles** — define geographic regions and which carriers serve each region. Each site has a default profile. Regions contain destinations (countries/subdivisions) and carriers.
- **Shipping Options** — define the rate entries customers see at checkout (flat, tiered, free). Each option is scoped to one or more delivery regions.

**Base URL**: `https://www.wixapis.com/ecom`

**How to call these APIs**: Use `CallWixSiteAPI`.

---

## Shipping Options

### Query Shipping Options

Retrieves all shipping options for the site. Up to 1,000 per request (cursor paging).

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options/query`

**Request**:
```json
{
  "query": {
    "cursorPaging": { "limit": 100 }
  }
}
```

**Filterable fields**: `id`, `delivery_region_id`, `delivery_region_ids`, `estimated_delivery_time`, `created_date`, `updated_date`

**Response**:
```json
{
  "shippingOptions": [
    {
      "id": "abc123",
      "revision": "1",
      "deliveryRegionId": "region-guid",
      "deliveryRegionIds": ["region-guid"],
      "title": "Standard Shipping",
      "category": "STANDARD",
      "estimatedDeliveryTime": "3-5 business days",
      "rates": [
        {
          "id": "rate-guid",
          "title": "Standard Shipping",
          "amount": "5.99",
          "multiplyByQuantity": false,
          "active": true,
          "conditions": []
        }
      ]
    }
  ],
  "pagingMetadata": { "count": 1, "hasNext": false }
}
```

---

### Create Shipping Option

Creates a new shipping option and associates it with one or more delivery regions.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options`

**Required fields**: `shippingOption.deliveryRegionId` (or `deliveryRegionIds`), `shippingOption.title`, `shippingOption.rates[]`

**Request**:
```json
{
  "shippingOption": {
    "deliveryRegionId": "region-guid",
    "title": "Free Shipping Over $75",
    "category": "FREE",
    "estimatedDeliveryTime": "5-7 business days",
    "rates": [
      {
        "title": "Free Shipping",
        "amount": "0",
        "multiplyByQuantity": false,
        "active": true,
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

**Response**: `{ "shippingOption": { ... } }` — the created option with `id` and `revision`.

**Error**: `INVALID_QUANTITY_VALUE` (400) — condition value cannot be fractional.

---

### Get Shipping Option

Retrieves a single shipping option by ID.

**Endpoint**: `GET https://www.wixapis.com/ecom/v1/shipping-options/{shippingOptionId}`

**Response**: `{ "shippingOption": { ... } }`

---

### Update Shipping Option

Updates a shipping option. Requires `id` and the current `revision`. Each update increments `revision`.

**Endpoint**: `PATCH https://www.wixapis.com/ecom/v1/shipping-options/{shippingOption.id}`

**Required fields**: `shippingOption.id`, `shippingOption.revision`

**Request**:
```json
{
  "shippingOption": {
    "id": "abc123",
    "revision": "1",
    "rates": [
      {
        "id": "rate-guid",
        "title": "Free Shipping",
        "amount": "0",
        "multiplyByQuantity": false,
        "active": true,
        "conditions": [
          {
            "type": "BY_TOTAL_PRICE",
            "operator": "GTE",
            "value": "85"
          }
        ]
      }
    ]
  }
}
```

**Response**: `{ "shippingOption": { ... } }` with updated `revision`.

---

### Delete Shipping Option

Permanently deletes a shipping option.

**Endpoint**: `DELETE https://www.wixapis.com/ecom/v1/shipping-options/{shippingOptionId}`

---

### Add Delivery Region (to Shipping Option)

Associates an additional delivery region with an existing shipping option.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options/{shippingOptionId}/add-delivery-region`

**Required fields**: `deliveryRegionId`, `revision`

**Request**:
```json
{
  "deliveryRegionId": "region-guid",
  "revision": "2"
}
```

---

### Remove Delivery Region (from Shipping Option)

Removes a delivery region association from a shipping option.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/shipping-options/{shippingOptionId}/remove-delivery-region`

**Required fields**: `deliveryRegionId`, `revision`

---

## Rate Configuration

Rate types are determined by the `conditions` array, not an explicit field:

| Rate Type | `amount` | `conditions` |
|-----------|---------|-------------|
| Flat rate | any | empty `[]` |
| Free shipping | `"0"` | optional `BY_TOTAL_PRICE GTE <threshold>` |
| Price-based tiers | any | one or more `BY_TOTAL_PRICE` conditions |
| Weight-based tiers | any | `BY_TOTAL_WEIGHT` conditions |
| Quantity-based | any | `BY_TOTAL_QUANTITY` conditions |

**Condition operators**: `EQ`, `GT`, `GTE`, `LT`, `LTE`

Multiple conditions in one rate combine with AND logic.

**`multiplyByQuantity: true`** charges `amount × cart quantity`. Flag this configuration — it penalizes large orders and should be replaced with flat or tiered pricing.

---

## Delivery Profiles

### Query Delivery Profiles

Retrieves all delivery profiles for the site. Typically one default profile exists.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/query`

**Request**: `{}`

**Response**:
```json
{
  "deliveryProfiles": [
    {
      "id": "profile-guid",
      "revision": "3",
      "name": "General profile",
      "default": true,
      "deliveryRegions": [
        {
          "id": "region-guid",
          "name": "United States",
          "active": true,
          "destinations": [
            { "countryCode": "US", "subdivisions": [] }
          ],
          "deliveryCarriers": [
            {
              "appId": "45c44b27-ca7b-4891-8c0d-1747d588b835",
              "backupRate": {
                "title": "Standard Shipping",
                "amount": "5.99",
                "active": true
              },
              "additionalCharges": []
            }
          ]
        }
      ]
    }
  ]
}
```

---

### Get Delivery Profile

Retrieves a single delivery profile by ID.

**Endpoint**: `GET https://www.wixapis.com/ecom/v1/delivery-profiles/{deliveryProfileId}`

**Response**: `{ "deliveryProfile": { ... } }`

---

### Get Delivery Profile by Region

Retrieves the profile that contains a given delivery region.

**Endpoint**: `GET https://www.wixapis.com/ecom/v1/delivery-profiles/delivery-regions/{deliveryRegionId}`

---

### Create Delivery Profile

Creates a new delivery profile (rarely needed — most sites use the default profile).

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles`

---

### Update Delivery Profile

Updates profile-level fields (name, etc.). Requires current `revision`.

**Endpoint**: `PATCH https://www.wixapis.com/ecom/v1/delivery-profiles/{deliveryProfile.id}`

---

### Add Delivery Region

Adds a geographic region to a delivery profile. Returns the updated profile with the new region's `id`.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/{deliveryProfileId}/delivery-region`

**Required fields**: `deliveryRegion.name`, `deliveryRegion.destinations[]`, `revision`

**Request**:
```json
{
  "deliveryRegion": {
    "name": "United States",
    "active": true,
    "destinations": [
      { "countryCode": "US" }
    ]
  },
  "revision": "3"
}
```

**Response**: `{ "deliveryProfile": { ... } }` — full updated profile with new region `id`.

**Error**: `DESTINATIONS_COLLISION` — country already assigned to another region in this profile. Use the existing region instead.

---

### Update Delivery Region

Updates name, active status, or destinations of an existing region.

**Endpoint**: `PATCH https://www.wixapis.com/ecom/v1/delivery-profiles/{deliveryProfileId}/delivery-region/{deliveryRegion.id}`

---

### Remove Delivery Region

Removes a delivery region from a profile.

**Endpoint**: `DELETE https://www.wixapis.com/ecom/v1/delivery-profiles/{deliveryProfileId}/delivery-region/{deliveryRegionId}`

---

### List Installed Delivery Carriers

Returns all carriers installed on the site (both built-in and third-party apps). Use this to find the `id` of a specific carrier (e.g., Pickup, Basic Shipping) before calling Add Delivery Carrier.

**Endpoint**: `GET https://www.wixapis.com/ecom/v1/delivery-profiles/installed-carriers`

**Response**:
```json
{
  "installedDeliveryCarriers": [
    {
      "id": "50d8c12f-715e-41ad-be25-d0f61375dbee",
      "displayName": "Pickup",
      "fallbackDefinitionMandatory": false,
      "toggleGetCarrierSettingsEnabled": true
    },
    {
      "id": "45c44b27-ca7b-4891-8c0d-1747d588b835",
      "displayName": "Basic Shipping",
      "description": "Manage shipping rates and options for this region",
      "fallbackDefinitionMandatory": false,
      "toggleGetCarrierSettingsEnabled": true
    }
  ]
}
```

---

### List Delivery Carriers (in a Profile)

Lists the carriers configured within a specific delivery profile.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/{deliveryProfileId}/delivery-carriers`

---

### Add Delivery Carrier

Adds a carrier to a delivery region within a profile. The carrier appears as a shipping option to customers in that region.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/add-delivery-carrier`

**Request**:
```json
{
  "deliveryRegionId": "region-guid",
  "deliveryCarrier": {
    "appId": "50d8c12f-715e-41ad-be25-d0f61375dbee",
    "backupRate": {
      "title": "Pickup at 123 Main St",
      "amount": "0",
      "active": true
    }
  }
}
```

**Response**: `{ "deliveryProfile": { ... } }` — full updated profile.

**Errors**:
| Error | Cause |
|-------|-------|
| `CARRIER_ALREADY_EXISTS_IN_REGION` | Carrier already in this region |
| `DELIVERY_CARRIER_MISSING_BACKUP_RATE` | `backupRate` or `backupRate.amount` missing |

---

### Remove Delivery Carrier

Removes a carrier from a delivery region.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/remove-delivery-carrier`

**Request**:
```json
{
  "deliveryRegionId": "region-guid",
  "appId": "carrier-app-id"
}
```

---

### Update Delivery Carrier

Updates `backupRate` or `additionalCharges` for a carrier in a region.

**Endpoint**: `PATCH https://www.wixapis.com/ecom/v1/delivery-profiles/update-delivery-carrier`

---

### Set Delivery Carrier Active Status

Activates or deactivates a carrier in a delivery region.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/delivery-carriers/set-active-status`

---

## Known Carrier IDs

| Carrier | App ID |
|---------|--------|
| Basic Shipping | `45c44b27-ca7b-4891-8c0d-1747d588b835` |
| Pickup | `50d8c12f-715e-41ad-be25-d0f61375dbee` |
