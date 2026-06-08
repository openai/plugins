---
name: "Setup: Store Pickup Location"
description: Configures a pickup option for an online store so customers can choose in-store pickup at checkout. Uses the Delivery Profiles API to discover the Pickup carrier, add a delivery region, and attach the carrier with a free pickup rate.
---
# Set Up Store Pickup Location

## Prerequisites

- Wix Stores (or another eCommerce business solution) installed on the site
- The **Pickup** carrier must be installed on the site (it is a built-in carrier, not a third-party app)

## Required APIs

- [List Installed Delivery Carriers](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#list-installed-delivery-carriers)
- [Query Delivery Profiles](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-delivery-profiles)
- [Add Delivery Region](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#add-delivery-region)
- [Add Delivery Carrier](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#add-delivery-carrier)

---

## Step 1: Discover the Pickup carrier

Call [List Installed Delivery Carriers](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#list-installed-delivery-carriers) to find the Pickup carrier's `id`.

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

Look for the carrier with `"displayName": "Pickup"` and save its `id`. This is the `appId` you will use in Step 4.

If no Pickup carrier appears in the list, the Pickup app is not installed on the site and must be installed before proceeding.

---

## Step 2: Find the default delivery profile

Call [Query Delivery Profiles](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#query-delivery-profiles) to retrieve the site's default delivery profile.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/query`

**Request**:
```json
{}
```

The response contains an array of `deliveryProfiles`. Find the one where `"default": true`. Save its `id` and `revision`. Inspect its `deliveryRegions` array.

**Decision point:**
- **Region exists for the user's country** (match on `destinations[].countryCode`): save that region's `id` → skip to Step 4.
- **No matching region**: proceed to Step 3.

---

## Step 3: Add a delivery region for the pickup country

If no region exists for the user's country in the default profile, call [Add Delivery Region](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#add-delivery-region) to create one.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/{deliveryProfileId}/delivery-region`

Replace `{deliveryProfileId}` with the default profile's `id` from Step 2.

**Request**:
```json
{
  "deliveryRegion": {
    "name": "US Pickup",
    "active": true,
    "destinations": [
      {
        "countryCode": "US"
      }
    ]
  },
  "revision": "3"
}
```

- `name`: descriptive, e.g. `"{Country} Pickup"`.
- `countryCode`: [ISO-3166 alpha-2](https://www.iso.org/obp/ui/#search/code/) code (e.g. `"US"`, `"IL"`, `"DE"`, `"GB"`).
- `revision`: from the profile returned in Step 2.

**Response**:
```json
{
  "deliveryProfile": {
    "id": "02625bf4-70b4-49b7-93f0-5c9d72608937",
    "name": "General profile",
    "default": true,
    "deliveryRegions": [
      {
        "id": "23823d4a-0ad2-4f92-a48a-467497a9470a",
        "name": "US Pickup",
        "active": true,
        "deliveryCarriers": [],
        "destinations": [
          {
            "countryCode": "US",
            "subdivisions": []
          }
        ]
      }
    ],
    "revision": "4"
  }
}
```

Save the new region's `id` from the response.

---

## Step 4: Add the Pickup carrier to the region

Call [Add Delivery Carrier](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping#add-delivery-carrier) to attach the Pickup carrier to the delivery region.

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/delivery-profiles/add-delivery-carrier`

**Request**:
```json
{
  "deliveryRegionId": "<REGION_ID>",
  "deliveryCarrier": {
    "appId": "50d8c12f-715e-41ad-be25-d0f61375dbee",
    "backupRate": {
      "title": "Pickup at 123 Main St, New York",
      "amount": "0",
      "active": true
    }
  }
}
```

- `deliveryRegionId`: from Step 2 (existing region) or Step 3 (new region).
- `appId`: the Pickup carrier `id` from Step 1.
- `backupRate.title`: the pickup address customers see at checkout.
- `backupRate.amount`: `"0"` for free pickup, or a price string like `"5.00"`.
- `backupRate.active`: must be `true` for the option to appear at checkout.

**Response**:
```json
{
  "deliveryProfile": {
    "id": "02625bf4-70b4-49b7-93f0-5c9d72608937",
    "name": "General profile",
    "default": true,
    "deliveryRegions": [
      {
        "id": "23823d4a-0ad2-4f92-a48a-467497a9470a",
        "name": "US Pickup",
        "active": true,
        "deliveryCarriers": [
          {
            "appId": "50d8c12f-715e-41ad-be25-d0f61375dbee",
            "backupRate": {
              "title": "Pickup at 123 Main St, New York",
              "amount": "0",
              "active": true
            },
            "additionalCharges": []
          }
        ],
        "destinations": [
          {
            "countryCode": "US",
            "subdivisions": []
          }
        ]
      }
    ],
    "revision": "5"
  }
}
```

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `DESTINATIONS_COLLISION` | The country is already assigned to another region in the same profile. | Skip Step 3 — use the existing region's `id` and add the carrier to it in Step 4. |
| `CARRIER_ALREADY_EXISTS_IN_REGION` | The Pickup carrier is already configured in this region. | The pickup option is already set up. No action needed. |
| `DELIVERY_CARRIER_MISSING_BACKUP_RATE` | The `backupRate` or `backupRate.amount` field is missing. | Ensure `backupRate` includes `title`, `amount`, and `active`. |

---

## Related Documentation

- [API: Shipping Delivery](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/api-shipping)
