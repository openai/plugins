---
name: "Setup: Coupons"
description: Creates and manages coupon codes using the Coupons V2 API. Covers coupon types (percentage, fixed amount, fixed price, free shipping), scope targeting, usage limits, and the mapping from discount recommendations to coupon API payloads.
layer: config
---
# Setup Coupons

## Prerequisites

- Wix Stores (or another eCommerce business solution) installed on the site

## Required APIs

- [Create Coupon](https://dev.wix.com/docs/api-reference/business-solutions/coupons/coupons/create-a-coupon) — `POST /v2/coupons`
- [Update Coupon](https://dev.wix.com/docs/api-reference/business-solutions/coupons/coupons/update-a-coupon) — `PATCH /v2/coupons/{id}`
- [Query Coupons](https://dev.wix.com/docs/api-reference/business-solutions/coupons/coupons/query-coupons) — `POST /v2/coupons/query`
- [Delete Coupon](https://dev.wix.com/docs/api-reference/business-solutions/coupons/coupons/delete-a-coupon) — `DELETE /v2/coupons/{id}`

---

## Step 1: Query existing coupons

Before creating a coupon, check for code conflicts and existing promotions on the same scope.

**Endpoint**: `POST https://www.wixapis.com/v2/coupons/query`

**Request**:
```json
{
  "query": {
    "paging": {
      "limit": 100
    }
  }
}
```

**Response**:
```json
{
  "coupons": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "specification": {
        "name": "Summer Sale",
        "code": "SUMMER20",
        "percentOffRate": 20,
        "scope": {
          "namespace": "stores",
          "group": {
            "name": "product"
          }
        },
        "startTime": 1717200000000,
        "expirationTime": 1719792000000,
        "usageLimit": 100,
        "limitPerCustomer": 1,
        "active": true
      },
      "numberOfUsages": 12,
      "expired": false
    }
  ]
}
```

Check for: duplicate codes, overlapping scopes with active coupons, and cross-mechanism stacking with active automatic discount rules.

---

## Step 2: Create a percentage-off coupon

**Endpoint**: `POST https://www.wixapis.com/v2/coupons`

**Request** — 15% off all store products:
```json
{
  "specification": {
    "name": "Spring Sale 15%",
    "code": "SPRING15",
    "percentOffRate": 15,
    "scope": {
      "namespace": "stores",
      "group": {
        "name": "product"
      }
    },
    "startTime": 1714521600000,
    "usageLimit": 200,
    "limitPerCustomer": 1,
    "active": true
  }
}
```

**Response**:
```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
}
```

**Request** — 20% off a specific collection:
```json
{
  "specification": {
    "name": "Electronics Deal",
    "code": "ELEC20",
    "percentOffRate": 20,
    "scope": {
      "namespace": "stores",
      "group": {
        "name": "collection",
        "entityId": "collection-uuid-here"
      }
    },
    "startTime": 1714521600000,
    "expirationTime": 1717200000000,
    "usageLimit": 50,
    "limitPerCustomer": 1,
    "active": true
  }
}
```

**Request** — 10% off a specific product:
```json
{
  "specification": {
    "name": "VIP Product Discount",
    "code": "VIP10",
    "percentOffRate": 10,
    "scope": {
      "namespace": "stores",
      "group": {
        "name": "product",
        "entityId": "product-uuid-here"
      }
    },
    "startTime": 1714521600000,
    "limitPerCustomer": 1,
    "active": true
  }
}
```

---

## Step 3: Create a fixed-amount coupon

**Request** — $10 off all products:
```json
{
  "specification": {
    "name": "Save $10",
    "code": "SAVE10",
    "moneyOffAmount": 10,
    "scope": {
      "namespace": "stores",
      "group": {
        "name": "product"
      }
    },
    "startTime": 1714521600000,
    "active": true
  }
}
```

---

## Step 4: Create a minimum subtotal coupon

Instead of targeting a scope, you can require a minimum cart subtotal. This is a **oneOf** with scope — you set EITHER `scope` OR `minimumSubtotal`, not both.

**Request** — 15% off orders over $100:
```json
{
  "specification": {
    "name": "Spend $100, Save 15%",
    "code": "SPEND100",
    "percentOffRate": 15,
    "minimumSubtotal": 100,
    "startTime": 1714521600000,
    "usageLimit": 500,
    "limitPerCustomer": 1,
    "active": true
  }
}
```

---

## Key field rules

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Display name shown to customers |
| `code` | Yes | Unique coupon code. Max 20 characters. Case-insensitive at checkout. |
| `startTime` | Yes | UNIX epoch in **milliseconds** (not seconds). E.g., `1714521600000` for 2024-05-01T00:00:00Z |
| `expirationTime` | No | UNIX epoch in milliseconds. Omit for no expiration. |
| `scope` OR `minimumSubtotal` | One required | **OneOf** — set scope to target items, OR minimumSubtotal for cart threshold. Cannot set both. Exception: freeShipping type ignores scope. |
| `usageLimit` | No | Total uses across all customers. Omit for unlimited. |
| `limitPerCustomer` | No | Max uses per customer. Omit for unlimited. |
| `limitedToOneItem` | No | If true, discount applies only to lowest-priced item when customer buys multiple. |
| `active` | No | Default `true`. Set `false` to create as draft. |

## Coupon types (oneOf — set exactly one)

| Type | Field | Value | Example |
|---|---|---|---|
| Percentage off | `percentOffRate` | Double (e.g., `15` for 15%) | `"percentOffRate": 15` |
| Fixed amount off | `moneyOffAmount` | Double (e.g., `10` for $10 off) | `"moneyOffAmount": 10` |
| Fixed price | `fixedPriceAmount` | Double (e.g., `29.99`) | `"fixedPriceAmount": 29.99` |
| Free shipping | `freeShipping` | Boolean `true` | `"freeShipping": true` |
| Buy X Get Y | `buyXGetY` | Object with `x` and `y` fields | `"buyXGetY": {"x": 2, "y": 1}` |

## Scope values for Wix Stores

| Scope target | `namespace` | `group.name` | `group.entityId` |
|---|---|---|---|
| All store products | `"stores"` | `"product"` | Omit (applies to all) |
| Specific product | `"stores"` | `"product"` | Product UUID |
| Specific collection | `"stores"` | `"collection"` | Collection UUID |

---

## Recommendation → Coupon API Mapping

When the recommendation output has `mechanism: "COUPON"`, use this mapping to convert it into a Coupons API payload.

### Scope mapping

| Recommendation `scope` | Coupon `scope` |
|---|---|
| `SITE` | `{ "namespace": "stores", "group": { "name": "product" } }` (all products, no entityId) |
| `CATEGORY` | `{ "namespace": "stores", "group": { "name": "collection", "entityId": "<first categoryId>" } }` |
| `ITEMS` | `{ "namespace": "stores", "group": { "name": "product", "entityId": "<first productId>" } }` |

**Important limitation**: The Coupons API scope supports only **one entityId** (one product or one collection). If the recommendation targets multiple products or categories:
- For CATEGORY with multiple categoryIds: Create one coupon per collection, or pick the primary collection.
- For ITEMS with multiple productIds: Create one coupon per product, or use `minimumSubtotal` instead of `scope` if the intent is cart-level.

### Discount type mapping

| Recommendation `discountType` | Coupon field |
|---|---|
| `PERCENTAGE` | `"percentOffRate": <value>` |
| `FIXED_AMOUNT` | `"moneyOffAmount": <value>` |
| `FIXED_PRICE` | `"fixedPriceAmount": <value>` |

### Condition mapping

| Recommendation condition | Coupon approach |
|---|---|
| `minSubTotal > 0` | Use `minimumSubtotal` instead of `scope` (they are oneOf — cannot use both) |
| `minItemQuantity > 0` | **Not natively supported by Coupons API**. Mention in the coupon name (e.g., "Buy 3+, use code BUNDLE15") but the API cannot enforce item quantity. |
| `startDate` | Convert to UNIX epoch milliseconds: `Date.parse("2026-06-01") → 1748736000000`. Set as `startTime`. |
| `endDate` | Convert to UNIX epoch milliseconds. Set as `expirationTime`. |

### Code generation

| Recommendation field | Coupon field | Rules |
|---|---|---|
| `code` from recommendation | `specification.code` | Max 20 characters. Must be unique on the site. Suggest memorable, brand-relevant codes (e.g., `SUMMER25`, `SAVE15`, `VIP20`). |
| `usageLimit` from recommendation | `specification.usageLimit` | Total times the coupon can be used. `0` in recommendation → omit (unlimited). |
| `limitPerCustomer` from recommendation | `specification.limitPerCustomer` | Max per customer. `0` → omit (unlimited). Recommend setting to `1` for most campaigns. |

### Full mapping example

**Recommendation output**:
```json
{
  "mechanism": "COUPON",
  "scope": "CATEGORY",
  "categoryIds": ["electronics-collection-uuid"],
  "name": "Tech Insider Deal",
  "discountType": "PERCENTAGE",
  "discount": 20,
  "code": "TECH20",
  "usageLimit": 100,
  "limitPerCustomer": 1,
  "conditions": {
    "startDate": "2026-06-01",
    "endDate": "2026-06-30"
  }
}
```

**Coupon API request**:
```json
{
  "specification": {
    "name": "Tech Insider Deal",
    "code": "TECH20",
    "percentOffRate": 20,
    "scope": {
      "namespace": "stores",
      "group": {
        "name": "collection",
        "entityId": "electronics-collection-uuid"
      }
    },
    "startTime": 1748736000000,
    "expirationTime": 1751328000000,
    "usageLimit": 100,
    "limitPerCustomer": 1,
    "active": true
  }
}
```

### Key differences from Automatic Discounts

| Aspect | Automatic Discount (Discount Rules API) | Coupon (Coupons API) |
|---|---|---|
| Scope supports multiple items | Yes (multiple IDs in arrays) | No (one entityId per scope) |
| minSubTotal + scope together | Yes (scope + trigger) | No (oneOf — choose one) |
| minItemQuantity enforcement | Yes (ITEM_QUANTITY_RANGE trigger) | Not supported by API |
| Date format | ISO 8601 timestamps | UNIX epoch milliseconds |
| Created state | `active: false`, `status: PENDING` | `active: true` by default |
| Triggers/conditions | Separate trigger object with typed ranges | Only minimumSubtotal (simple threshold) |

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| Duplicate code | Another coupon uses the same code | Generate a different code |
| Invalid startTime | Value too low (must be epoch ms, not seconds) | Multiply by 1000 if in seconds |
| Both scope and minimumSubtotal set | These are oneOf — cannot use both | Choose scope OR minimumSubtotal |
| Code exceeds 20 characters | Code is too long | Shorten the code |

## References

- [Coupons API](https://dev.wix.com/docs/api-reference/business-solutions/coupons/coupons/create-a-coupon)
- [Valid Scope Values](https://dev.wix.com/docs/api-reference/business-solutions/coupons/coupons/valid-scope-values)
