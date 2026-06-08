---
name: "Setup: Discount Rules"
description: Configures automatic discount rules using the eCommerce Discount Rules API. Covers percentage and fixed-amount discounts, scope targeting (catalog-wide, specific collections, or individual products), scheduling active periods, and the find-by-name + update pattern.
layer: config
---
# Setup Discount Rules

## Prerequisites

- Wix Stores (or another eCommerce business solution) installed on the site
- At least one product in the catalog

## Required APIs

- [Create Discount Rule](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/create-discount-rule)
- [Get Discount Rule](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/get-discount-rule)
- [Query Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/query-discount-rules)
- [Update Discount Rule](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/update-discount-rule)
- [Delete Discount Rule](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/delete-discount-rule)

---

## Critical: `discounts` structure

**The API always returns the full normalized structure.** Never assume a simplified form. Each discount entry looks like:

```json
{
  "targetType": "SPECIFIC_ITEMS",
  "specificItemsInfo": {
    "scopes": [
      {
        "id": "all_215238eb-22a5-4c36-9e7b-e7c08025e04e",
        "type": "CATALOG_ITEM",
        "catalogItemFilter": {
          "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e"
        }
      }
    ]
  },
  "discount": {
    "discountType": "PERCENTAGE",
    "percentage": 20
  }
}
```

When updating a rule, always use the `discounts` array as returned from the query/get, modifying only the specific fields you need. **Do not reconstruct from scratch unless creating a new rule.**

---

## Step 1: Query existing discount rules

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/discount-rules/query`

> **Paging**: This API uses **cursor paging** (`cursorPaging`), not offset paging. Using `paging` instead of `cursorPaging` will fail.

**Request** — list all rules:
```json
{
  "query": {
    "cursorPaging": {
      "limit": 100
    }
  }
}
```

**Request** — find by name (exact match):
```json
{
  "query": {
    "filter": {
      "name": { "$eq": "Summer Sale" }
    },
    "cursorPaging": { "limit": 10 }
  }
}
```

Filterable fields: `id`, `name`, `active`, `revision`, `created_date`, `updated_date`, `active_time_info.start`, `active_time_info.end`

**Response**:
```json
{
  "discountRules": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "revision": "1",
      "name": "Summer Sale 10%",
      "active": true,
      "activeTimeInfo": {
        "start": "2026-06-01T00:00:00.000Z",
        "end": "2026-08-31T23:59:59.000Z"
      },
      "discounts": [
        {
          "targetType": "SPECIFIC_ITEMS",
          "specificItemsInfo": {
            "scopes": [
              {
                "id": "all_215238eb-22a5-4c36-9e7b-e7c08025e04e",
                "type": "CATALOG_ITEM",
                "catalogItemFilter": {
                  "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e"
                }
              }
            ]
          },
          "discount": {
            "discountType": "PERCENTAGE",
            "percentage": 10
          }
        }
      ]
    }
  ],
  "pagingMetadata": {
    "cursors": {},
    "hasNext": false
  }
}
```

Note existing rules and their scopes to avoid stacking conflicts.

---

## Step 2: Create a percentage discount rule

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/discount-rules`

**Request** — 20% off all products:
```json
{
  "discountRule": {
    "name": "Flash Sale 20% Off",
    "active": true,
    "activeTimeInfo": {
      "start": "2026-05-01T00:00:00.000Z",
      "end": "2026-05-03T23:59:59.000Z"
    },
    "discounts": [
      {
        "targetType": "SPECIFIC_ITEMS",
        "specificItemsInfo": {
          "scopes": [
            {
              "id": "all_215238eb-22a5-4c36-9e7b-e7c08025e04e",
              "type": "CATALOG_ITEM",
              "catalogItemFilter": {
                "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e"
              }
            }
          ]
        },
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        }
      }
    ],
    "settings": {
      "appliesTo": "ALL_ITEMS"
    }
  }
}
```

**Request** — 15% off a specific collection:
```json
{
  "discountRule": {
    "name": "Summer Collection Sale",
    "active": true,
    "discounts": [
      {
        "targetType": "SPECIFIC_ITEMS",
        "specificItemsInfo": {
          "scopes": [
            {
              "id": "collections_215238eb-22a5-4c36-9e7b-e7c08025e04e",
              "type": "CUSTOM_FILTER",
              "customFilter": {
                "appId": "215238eb-22a5-4c36-9e7b-e7c08025e04e",
                "params": {
                  "collectionIds": ["collection-uuid-here"]
                }
              }
            }
          ]
        },
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 15
        }
      }
    ],
    "settings": {
      "appliesTo": "ALL_ITEMS"
    }
  }
}
```

---

## Step 3: Create a fixed-amount discount rule

**Request** — $5 off specific products:
```json
{
  "discountRule": {
    "name": "$5 Off Selected Items",
    "active": true,
    "discounts": [
      {
        "targetType": "SPECIFIC_ITEMS",
        "specificItemsInfo": {
          "scopes": [
            {
              "id": "specific_215238eb-22a5-4c36-9e7b-e7c08025e04e",
              "type": "CATALOG_ITEM",
              "catalogItemFilter": {
                "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e",
                "catalogItemIds": ["product-uuid-here"]
              }
            }
          ]
        },
        "discount": {
          "discountType": "FIXED_AMOUNT",
          "fixedAmount": "5.00"
        }
      }
    ],
    "settings": {
      "appliesTo": "ALL_ITEMS"
    }
  }
}
```

---

## Step 4: Update a discount rule

Always fetch the rule first (via Get or Query), then modify only the fields you need. The `mask` field tells the API which fields to update — omit it to replace all writable fields.

**Endpoint**: `PATCH https://www.wixapis.com/ecom/v1/discount-rules/{discountRule.id}`

**Required**: `discountRule.id`, `discountRule.revision` (must match current revision)

**Request** — change percentage on an existing rule (full discounts replacement):
```json
{
  "discountRule": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "revision": "1",
    "discounts": [
      {
        "targetType": "SPECIFIC_ITEMS",
        "specificItemsInfo": {
          "scopes": [
            {
              "id": "all_215238eb-22a5-4c36-9e7b-e7c08025e04e",
              "type": "CATALOG_ITEM",
              "catalogItemFilter": {
                "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e"
              }
            }
          ]
        },
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 25
        }
      }
    ]
  },
  "mask": { "paths": ["discounts"] }
}
```

**Request** — change only `active` status (field mask for partial update):
```json
{
  "discountRule": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "revision": "2",
    "active": false
  },
  "mask": { "paths": ["active"] }
}
```

---

## Step 5: Find by name and update (complete pattern)

The safe pattern for "find a rule by name and update its percentage":

1. Query with name filter → get the rule's `id`, `revision`, and `discounts` array
2. Modify only the `discount.percentage` inside each discount entry, keeping all other fields intact
3. PATCH with the modified `discounts` and `mask: { paths: ["discounts"] }`

**Step 5a — Query by name**:
```json
POST https://www.wixapis.com/ecom/v1/discount-rules/query
{
  "query": {
    "filter": { "name": { "$eq": "My Rule Name" } },
    "cursorPaging": { "limit": 1 }
  }
}
```

Extract from response: `discountRules[0].id`, `discountRules[0].revision`, `discountRules[0].discounts`

**Step 5b — Update percentage** (modify the returned discounts in-place):

Take the `discounts` array from the query response and update only `discount.percentage` on each entry:
```json
PATCH https://www.wixapis.com/ecom/v1/discount-rules/{id}
{
  "discountRule": {
    "id": "<id from query>",
    "revision": "<revision from query>",
    "discounts": [
      {
        "targetType": "SPECIFIC_ITEMS",
        "specificItemsInfo": { "<scopes unchanged from query response>" },
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 10
        }
      }
    ]
  },
  "mask": { "paths": ["discounts"] }
}
```

> **Important**: Copy `targetType`, `specificItemsInfo.scopes` verbatim from the query response — do not reconstruct them. Only change `discount.discountType` and `discount.percentage`/`discount.fixedAmount`.

---

## Step 6: Deactivate or delete a discount rule

To deactivate without deleting:
```json
{
  "discountRule": {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "revision": "2",
    "active": false
  },
  "mask": { "paths": ["active"] }
}
```

To delete permanently:

**Endpoint**: `DELETE https://www.wixapis.com/ecom/v1/discount-rules/{discountRuleId}`

---

## Key field rules

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Internal name for the rule. Filterable in query. |
| `active` | Yes | Whether the rule is currently applied |
| `activeTimeInfo.start` | No | ISO 8601 start time. Omit for immediate activation |
| `activeTimeInfo.end` | No | ISO 8601 end time. Omit for no expiration |
| `discounts[].targetType` | Yes | Always `"SPECIFIC_ITEMS"` for standard rules |
| `discounts[].specificItemsInfo.scopes[]` | Yes | Array of scope objects — see Scope types below |
| `discounts[].discount.discountType` | Yes | `"PERCENTAGE"` or `"FIXED_AMOUNT"` or `"FIXED_PRICE"` |
| `discounts[].discount.percentage` | If PERCENTAGE | Integer 1-100 |
| `discounts[].discount.fixedAmount` | If FIXED_AMOUNT | Decimal string (e.g., `"5.00"`) |
| `settings.appliesTo` | Yes on create | Always `"ALL_ITEMS"` |
| `revision` | On update/delete | Must match current value — fetch first |
| `mask.paths[]` | On update | Recommended — list fields being changed (e.g., `["discounts"]`, `["active"]`) |

## Scope types

| Scope | `type` | `id` prefix | When to use |
|---|---|---|---|
| All products | `"CATALOG_ITEM"` | `all_<appId>` | `catalogItemFilter.catalogAppId` only, no `catalogItemIds` |
| Specific products | `"CATALOG_ITEM"` | `specific_<appId>` | `catalogItemFilter.catalogAppId` + `catalogItemFilter.catalogItemIds` |
| Collection | `"CUSTOM_FILTER"` | `collections_<appId>` | `customFilter.appId` + `customFilter.params.collectionIds` |

**Store catalog app ID** (required in all scopes): `215238eb-22a5-4c36-9e7b-e7c08025e04e`

## Recommendation → API Mapping

When creating a discount rule from a recommendation output, use this mapping to convert the recommendation's simplified JSON into the actual Discount Rules API payload.

### Constants

- **Store catalog app ID**: `215238eb-22a5-4c36-9e7b-e7c08025e04e` — used in all scope constructions below.
- **Initial state**: Recommendations create rules as `active: false` with `status: "PENDING"`. The merchant must approve before the rule goes live.

### Scope mapping

The recommendation's `scope` field maps to the API's internal scope structure. The scope ID uses a prefix convention:

| Recommendation scope | API scope type | Scope ID prefix | How to build |
|---|---|---|---|
| `SITE` | `CATALOG_ITEM` | `all_` | Set `catalogItemFilter.catalogAppId` to the store catalog app ID. No item IDs. |
| `ITEMS` | `CATALOG_ITEM` | `specific_` | Set `catalogItemFilter.catalogAppId` + `catalogItemFilter.catalogItemIds` to the product UUIDs from `productIds`. |
| `CATEGORY` | `CUSTOM_FILTER` | `collections_` | Set `customFilter.appId` to the store catalog app ID + `customFilter.params.collectionIds` to the category UUIDs from `categoryIds`. |

**Example — SITE scope**:
```json
{
  "scope": {
    "id": "all_215238eb-22a5-4c36-9e7b-e7c08025e04e",
    "type": "CATALOG_ITEM",
    "catalogItemFilter": {
      "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e"
    }
  }
}
```

**Example — ITEMS scope** (with product IDs):
```json
{
  "scope": {
    "id": "specific_215238eb-22a5-4c36-9e7b-e7c08025e04e",
    "type": "CATALOG_ITEM",
    "catalogItemFilter": {
      "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e",
      "catalogItemIds": ["product-uuid-1", "product-uuid-2"]
    }
  }
}
```

**Example — CATEGORY scope** (with collection IDs):
```json
{
  "scope": {
    "id": "collections_215238eb-22a5-4c36-9e7b-e7c08025e04e",
    "type": "CUSTOM_FILTER",
    "customFilter": {
      "appId": "215238eb-22a5-4c36-9e7b-e7c08025e04e",
      "params": {
        "collectionIds": ["collection-uuid-1"]
      }
    }
  }
}
```

### Discount type mapping

| Recommendation `discountType` | API field to set | Value format |
|---|---|---|
| `PERCENTAGE` | `discount.percentage` | Integer (e.g., `15`) |
| `FIXED_AMOUNT` | `discount.fixedAmount` | String (e.g., `"5.00"`) |
| `FIXED_PRICE` | `discount.fixedPrice` | String (e.g., `"29.99"`) |

All discount entries use `targetType: "SPECIFIC_ITEMS"` with the scope wrapped in `specificItemsInfo.scopes[]`.

### Trigger mapping (conditions)

Triggers determine WHEN the discount activates. They are built from the recommendation's `conditions` fields. **If no conditions exist (both minSubTotal and minItemQuantity are 0), do NOT set a trigger — the discount applies unconditionally.**

| Condition | Trigger type | How to build |
|---|---|---|
| `minItemQuantity > 0` only | `ITEM_QUANTITY_RANGE` | Set `itemQuantityRange.from` to the value. No upper bound. Include the same scope as the discount target. |
| `minSubTotal > 0` only | `SUBTOTAL_RANGE` | Set `subtotalRange.from` to the value as a string. No upper bound. Include the same scope. |
| Both conditions > 0 | `AND` | Combine both triggers in `and.triggers[]` array. |
| Neither condition | No trigger | Leave trigger field unset entirely. |

**Example — minSubTotal trigger** (upsell boost: spend $200+):
```json
{
  "trigger": {
    "triggerType": "SUBTOTAL_RANGE",
    "subtotalRange": {
      "from": "200",
      "scopes": [
        {
          "id": "all_215238eb-22a5-4c36-9e7b-e7c08025e04e",
          "type": "CATALOG_ITEM",
          "catalogItemFilter": {
            "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e"
          }
        }
      ]
    }
  }
}
```

**Example — minItemQuantity trigger** (bundle: buy 3+):
```json
{
  "trigger": {
    "triggerType": "ITEM_QUANTITY_RANGE",
    "itemQuantityRange": {
      "from": 3,
      "scopes": [
        {
          "id": "collections_215238eb-22a5-4c36-9e7b-e7c08025e04e",
          "type": "CUSTOM_FILTER",
          "customFilter": {
            "appId": "215238eb-22a5-4c36-9e7b-e7c08025e04e",
            "params": {
              "collectionIds": ["category-uuid"]
            }
          }
        }
      ]
    }
  }
}
```

**Example — AND trigger** (both conditions):
```json
{
  "trigger": {
    "triggerType": "AND",
    "and": {
      "triggers": [
        {
          "triggerType": "ITEM_QUANTITY_RANGE",
          "itemQuantityRange": { "from": 2, "scopes": [/* same scope */] }
        },
        {
          "triggerType": "SUBTOTAL_RANGE",
          "subtotalRange": { "from": "100", "scopes": [/* same scope */] }
        }
      ]
    }
  }
}
```

### Date handling

| Recommendation field | API mapping |
|---|---|
| `startDate` is a date string (e.g., `"2026-06-01"`) | Convert to ISO 8601 timestamp: `activeTimeInfo.start` |
| `startDate` is empty `""` | Default to current time (now) |
| `endDate` is a date string | Convert to ISO 8601 timestamp: `activeTimeInfo.end` |
| `endDate` is empty `""` | Omit `activeTimeInfo.end` — rule has no expiration |

### Settings

All recommendation-created rules use these fixed settings:
```json
{
  "settings": {
    "appliesTo": "ALL_ITEMS",
    "indexOptIn": true
  }
}
```

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `DISCOUNT_RULE_NOT_FOUND` | The discount rule ID doesn't exist | Re-query discount rules to get current IDs |
| `REVISION_MISMATCH` | The `revision` doesn't match the current version | Re-fetch the rule to get the latest revision, then retry |
| `INVALID_DISCOUNT_TYPE` | Unsupported discount type | Use `PERCENTAGE` or `FIXED_AMOUNT` |
| Both `productIds` and `categoryIds` set | Scope mutual exclusivity violation | Use only one: ITEMS with productIds OR CATEGORY with categoryIds |
| `productIds` empty when scope is ITEMS | Missing required IDs | Query products and provide at least 1 product UUID |
| `categoryIds` empty when scope is CATEGORY | Missing required IDs | Call getCategoryIds to convert category names to GUIDs |

## References

- [Discount Rules API](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/introduction)
- [Coupons API](https://dev.wix.com/docs/api-reference/business-solutions/coupons/coupons/introduction)
