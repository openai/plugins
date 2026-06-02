---
name: "Update Product Pre-Order (Catalog V3)"
description: Manages pre-order settings for product variants using V3 Inventory API. Covers enabling/disabling pre-orders, setting messages, configuring limits, and handling trackQuantity requirements.
---
# Update Product Pre-Order Information (Catalog V3)

This recipe outlines the steps to manage pre-orders for product variants, including enabling/disabling pre-orders, setting messages, and configuring limits.

## Prerequisites

- Wix Stores app installed
- Product with variants already created
- API access with stores permissions

## Required APIs

- **Products Search API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/products-v3/search-products)
- **Query Inventory Items API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/inventory-items-v3/query-inventory-items)
- **Bulk Update Inventory Items API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/inventory-items-v3/bulk-update-inventory-items)
- **Update Inventory Item API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/inventory-items-v3/update-inventory-item)

---

## Step 1: Find the Product and Get Variant Information

### 1.1 Search for the Product

**Endpoint**: `POST https://www.wixapis.com/stores/v3/products/search`

```json
{
  "search": {
    "expression": "Product Name"
  }
}
```

### 1.2 Query Inventory Items for Variant Details

Use the `productId` from the search to get variant information:

**Endpoint**: `POST https://www.wixapis.com/stores/v3/inventory-items/query`

```json
{
  "query": {
    "filter": {
      "productId": {
        "$in": ["<PRODUCT_ID>"]
      }
    }
  }
}
```

The response includes:
- `product.variantName` - identifies each variant
- `inventoryItemId` - needed for updates
- `revision` - required for update operations
- `locationId` - inventory location
- Current `preorderInfo` settings

### IMPORTANT NOTES:
- I MUST get user input on which specific variant(s) to update
- I MUST NEVER update all variants without explicit user selection
- I MUST ask the user whether to enable or disable pre-orders for each variant
- If enabling, I MUST get the pre-order message from the user
- If setting a pre-order limit, I MUST ensure `trackQuantity: true` is set

---

## Step 2: Update Pre-Order Information

### Method A: Bulk Update (PREFERRED for multiple variants)

Use when applying the same pre-order settings to multiple variants:

**Endpoint**: `POST https://www.wixapis.com/stores/v3/bulk/inventory-items/update`

**Request Body (Enable Pre-Order)**:
```json
{
  "inventoryItems": [
    {
      "inventoryItem": {
        "id": "<inventoryItemId_variant1>",
        "revision": "<revision_as_integer>",
        "preorderInfo": {
          "enabled": true,
          "message": "Available for pre-order! Ships in 2 weeks."
        }
      }
    },
    {
      "inventoryItem": {
        "id": "<inventoryItemId_variant2>",
        "revision": "<revision_as_integer>",
        "preorderInfo": {
          "enabled": true,
          "message": "Available for pre-order! Ships in 2 weeks."
        }
      }
    }
  ],
  "returnEntity": true,
  "reason": "MANUAL"
}
```

**Request Body (With Pre-Order Limit)**:
```json
{
  "inventoryItems": [
    {
      "inventoryItem": {
        "id": "<inventoryItemId>",
        "revision": "<revision_as_integer>",
        "trackQuantity": true,
        "quantity": 100,
        "preorderInfo": {
          "enabled": true,
          "message": "Pre-order now!",
          "limit": 50
        }
      }
    }
  ],
  "returnEntity": true,
  "reason": "MANUAL"
}
```

### IMPORTANT NOTES:
- Pre-order limits ONLY work when `trackQuantity: true`
- If variant wasn't tracking quantity, I MUST ask user for initial quantity
- The `revision` field is required and must be an integer

---

### Method B: Individual Update (Single variant or unique settings)

**Endpoint**: `PATCH https://www.wixapis.com/stores/v3/inventory-items/{inventoryItemId}`

**Request Body (Enable Pre-Order)**:
```json
{
  "inventoryItem": {
    "id": "<inventoryItemId>",
    "revision": "<revision_as_integer>",
    "preorderInfo": {
      "enabled": true,
      "message": "Coming soon! Pre-order today."
    }
  },
  "reason": "MANUAL"
}
```

**Request Body (Disable Pre-Order)**:
```json
{
  "inventoryItem": {
    "id": "<inventoryItemId>",
    "revision": "<revision_as_integer>",
    "preorderInfo": {
      "enabled": false,
      "limit": null
    }
  },
  "reason": "MANUAL"
}
```

---

## Pre-Order Limit Behavior

When you set a `preorderInfo.limit`:
- It specifies how many units can be pre-ordered **after stock reaches zero**
- Example: 10 in stock + limit of 50 = customers can order up to 60 total (10 regular + 50 pre-order)

### CRITICAL: Enabling Quantity Tracking

If setting a limit on a variant that wasn't tracking quantity:

1. **Inform the user**: "`trackQuantity` will be enabled for this variant"
2. **Ask for initial quantity**: "What initial stock quantity should I set?"
3. **Include both in update**:
```json
{
  "inventoryItem": {
    "id": "<inventoryItemId>",
    "revision": "<revision_as_integer>",
    "trackQuantity": true,
    "quantity": "<USER_PROVIDED_QUANTITY>",
    "preorderInfo": {
      "enabled": true,
      "message": "Pre-order message",
      "limit": 50
    }
  },
  "reason": "MANUAL"
}
```

---

## Next Steps

After updating pre-order settings:
- Confirm the changes with the user
- Offer to update other products or variants
- Consider updating product descriptions to mention pre-order availability
