---
name: "CMS eCommerce Catalog Integration"
description: The recommended way to sell existing CMS collection items (tickets, bookings, memberships) through Wix checkout. Add the CATALOG plugin to convert any CMS collection into purchasable products with cart and payment integration.
---
# CMS eCommerce Catalog Integration

This recipe documents how to convert CMS collections into sellable product catalogs that integrate with Wix eCommerce (cart, checkout, orders).

## Overview

Converting a CMS collection to a catalog enables:
- Items in the collection become purchasable products
- Integration with Wix Cart and Checkout APIs
- Real-time price and availability from your CMS data

## Prerequisites

Your collection needs these fields (or mappable equivalents):
- **Name field** (TEXT) - Product display name
- **Price field** (NUMBER) - Product price

Optional catalog fields:
- **Description** (TEXT) - Product description
- **Image** (IMAGE) - Product image
- **URL** (URL) - Product link
- **Quantity** (NUMBER) - Inventory quantity

## Step 1: Add CATALOG Plugin to Collection

### API Endpoint

```
POST https://www.wixapis.com/wix-data/v2/collections/add-plugin
```

### Example: Convert Collection with Custom Field Names

```json
{
  "dataCollectionId": "Products",
  "plugin": {
    "type": "CATALOG",
    "catalogOptions": {
      "name": "title",
      "price": "price",
      "description": "description"
    }
  }
}
```

### Example: Full Catalog with All Optional Fields

```json
{
  "dataCollectionId": "Products",
  "plugin": {
    "type": "CATALOG",
    "catalogOptions": {
      "name": "itemName",
      "price": "itemPrice",
      "description": "itemDescription",
      "image": "itemImage",
      "url": "itemUrl",
      "quantity": "itemQuantity"
    }
  }
}
```

## Step 2: Verify eCommerce App is Installed

Most Wix sites with Stores, Bookings, or similar apps already have eCommerce installed. Check by querying the Cart API:

```
POST https://www.wixapis.com/ecom/v1/carts
```

## Step 3: Use Catalog Items in Cart

### CMS App ID (for catalogReference)

```
e593b0bd-b783-45b8-97c2-873d42aacaf4
```

### Add CMS Catalog Item to Cart

```
POST https://www.wixapis.com/ecom/v1/carts/{cartId}/add-to-cart
```

```json
{
  "lineItems": [
    {
      "catalogReference": {
        "appId": "e593b0bd-b783-45b8-97c2-873d42aacaf4",
        "catalogItemId": "<cms-item-id>"
      },
      "quantity": 1
    }
  ]
}
```

## Removing CATALOG Plugin

```
POST https://www.wixapis.com/wix-data/v2/collections/delete-plugin
```

```json
{
  "dataCollectionId": "Products",
  "pluginType": "CATALOG"
}
```

## Differences from Wix Stores

| Feature | CMS Catalog | Wix Stores |
|---------|-------------|------------|
| Product management | CMS collections | Stores dashboard |
| Variants | Manual (separate items) | Built-in variant system |
| Inventory tracking | Manual via quantity field | Automatic |
| Product options | Not supported | Full support |
| Discounts | Manual price changes | Built-in discount system |

CMS Catalogs are best for simple product catalogs. For complex eCommerce needs, consider Wix Stores.

## See Also

- [CMS Schema Management](cms-schema-management.md)
- [CMS Data Operations](cms-data-items-crud.md)
- [Wix Cart API](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/purchase-flow/cart/cart/introduction)
