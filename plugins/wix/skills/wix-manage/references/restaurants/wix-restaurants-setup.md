---
name: "Wix Restaurants Setup"
description: Configures restaurant menus, sections, and items using Menus API. Covers menu structure (Menu → Section → Item), modifiers, pricing, availability schedules, and ordering settings.
---
# Wix Restaurants Setup API Reference

This recipe covers setting up and configuring Wix Restaurants using the REST API, including menus, items, and ordering configuration.

## Prerequisites

1. Wix Restaurants app installed on the site
2. API access with restaurant management permissions

## Required APIs

- **Menus API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/restaurants/menus/menus/create-menu)
- **Menu Items API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/restaurants/menus/items/items/create-item)
- **Menu Sections API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/restaurants/menus/sections/create-section)
- **Item Modifier Groups API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/restaurants/menus/items/item-modifier-groups/create-modifier-group)
- **Item Variants API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/restaurants/menus/items/item-variants/bulk-create-variants)

## Overview

Wix Restaurants uses a hierarchical structure:
- **Menus** (e.g., Breakfast, Lunch, Dinner)
  - **Sections** (e.g., Appetizers, Main Courses, Desserts)
    - **Items** (e.g., Caesar Salad, Grilled Salmon)

## Step 1: Create a Menu

**Endpoint**: `POST https://www.wixapis.com/restaurants/menus-menu/v1/menus`

**Request Body**:
```json
{
  "menu": {
    "name": "Dinner Menu",
    "description": "Our evening dining selections",
    "visible": true
  }
}
```

**Response**:
```json
{
  "menu": {
    "id": "menu-id-123",
    "name": "Dinner Menu",
    "description": "Our evening dining selections",
    "visible": true,
    "createdDate": "2024-01-15T10:00:00.000Z"
  }
}
```

## Step 2: Create Menu Sections

**Endpoint**: `POST https://www.wixapis.com/restaurants/menus-section/v1/sections`

**Request Body**:
```json
{
  "section": {
    "name": "Appetizers",
    "description": "Start your meal with our delicious starters",
    "visible": true,
    "sortOrder": 1
  }
}
```

Create multiple sections:
```json
// Section 1: Appetizers
{
  "section": {
    "name": "Appetizers",
    "sortOrder": 1
  }
}

// Section 2: Main Courses
{
  "section": {
    "name": "Main Courses",
    "sortOrder": 2
  }
}

// Section 3: Desserts
{
  "section": {
    "name": "Desserts",
    "sortOrder": 3
  }
}
```

## Step 3: Create Menu Items

**Endpoint**: `POST https://www.wixapis.com/restaurants/menus-item/v1/items`

**Request Body**:
```json
{
  "item": {
    "name": "Caesar Salad",
    "description": "Fresh romaine lettuce with house-made Caesar dressing, croutons, and parmesan",
    "priceInfo": { "price": "14.99" },
    "visible": true,
    "labels": [],
    "modifierGroups": []
  }
}
```

## Step 4: Add Items to Sections

**Endpoint**: `PATCH https://www.wixapis.com/restaurants/menus-section/v1/sections/{sectionId}`

Each section update requires the latest section `revision`.

```json
{
  "section": {
    "id": "<SECTION_ID>",
    "revision": "<SECTION_REVISION>",
    "itemIds": ["item-id-1", "item-id-2", "item-id-3"]
  }
}
```

## Step 5: Configure Item Options and Modifiers

Create modifiers for customization (e.g., cooking temperature, add-ons):

**Endpoint**: `POST https://www.wixapis.com/restaurants/item-modifier-group/v1/modifier-groups`

```json
{
  "modifier": {
    "name": "Cooking Temperature",
    "required": true,
    "minSelections": 1,
    "maxSelections": 1,
    "options": [
      {
        "name": "Rare",
        "price": {
          "amount": "0",
          "currency": "USD"
        }
      },
      {
        "name": "Medium Rare",
        "price": {
          "amount": "0",
          "currency": "USD"
        }
      },
      {
        "name": "Medium",
        "price": {
          "amount": "0",
          "currency": "USD"
        }
      },
      {
        "name": "Well Done",
        "price": {
          "amount": "0",
          "currency": "USD"
        }
      }
    ]
  }
}
```

Add-on modifier with pricing:
```json
{
  "modifier": {
    "name": "Add-ons",
    "required": false,
    "minSelections": 0,
    "maxSelections": 5,
    "options": [
      {
        "name": "Extra Cheese",
        "price": {
          "amount": "2.00",
          "currency": "USD"
        }
      },
      {
        "name": "Bacon",
        "price": {
          "amount": "3.00",
          "currency": "USD"
        }
      },
      {
        "name": "Avocado",
        "price": {
          "amount": "2.50",
          "currency": "USD"
        }
      }
    ]
  }
}
```

## Step 6: Set Menu Structure (Attach Sections to Menu)

Attach section IDs to a menu. This call requires the latest menu `revision`.

**Endpoint**: `PATCH https://www.wixapis.com/restaurants/menus-menu/v1/menus/{menuId}`

```json
{
  "menu": {
    "id": "<MENU_ID>",
    "revision": "<MENU_REVISION>",
    "sectionIds": ["<SECTION_ID_1>", "<SECTION_ID_2>"]
  }
}
```

## Step 7: Bulk Operations for Large Menus

For restaurant setup flows with many sections/items, use bulk endpoints:

- **Bulk Create Sections**: `POST https://www.wixapis.com/restaurants/menus-section/v1/bulk/sections/create`
- **Bulk Create Items**: `POST https://www.wixapis.com/restaurants/menus-item/v1/bulk/items/create`
- **Bulk Create Variants**: `POST https://www.wixapis.com/restaurants/item-variants/v1/bulk/variants/create`

```json
{
  "sections": [
    { "name": "Appetizers", "visible": true },
    { "name": "Main Courses", "visible": true }
  ],
  "returnEntity": true
}
```

## Step 8: Query Menus / Sections / Items

Use query APIs for retrieval and UI display flows.

- **Query Menus**: `POST https://www.wixapis.com/restaurants/menus-menu/v1/menus/query`
- **Query Sections**: `POST https://www.wixapis.com/restaurants/menus-section/v1/sections/query`
- **Query Items**: `POST https://www.wixapis.com/restaurants/menus-item/v1/items/query`

```json
{
  "query": {
    "cursorPaging": {
      "limit": 50
    }
  }
}
```

## Query Menus

**Endpoint**: `GET https://www.wixapis.com/restaurants/menus-menu/v1/menus`

**Response**:
```json
{
  "menus": [
    {
      "id": "menu-1",
      "name": "Breakfast Menu",
      "visible": true,
      "sections": [...]
    },
    {
      "id": "menu-2",
      "name": "Lunch Menu",
      "visible": true,
      "sections": [...]
    }
  ]
}
```

## Recommended Setup Order

For complex restaurant menus, use this order to avoid dependency issues:

1. Create variants (sizes/options) if needed.
2. Create items (single or bulk).
3. Create sections (single or bulk).
4. Update each section with `itemIds`.
5. Update menu with `sectionIds`.

## Item Labels

Common dietary labels:
- `vegetarian`
- `vegan`
- `gluten-free`
- `gluten-free-option`
- `dairy-free`
- `nut-free`
- `spicy`
- `chef-recommendation`

## Best Practices

1. **High-Quality Images**: Use appetizing food photography
2. **Clear Descriptions**: Include ingredients and preparation methods
3. **Accurate Pricing**: Keep prices up-to-date
4. **Stock Management**: Update availability in real-time
5. **Modifier Organization**: Group related customizations logically
6. **Menu Structure**: Organize sections in logical dining order

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `MENU_NOT_FOUND` | Invalid menu ID | Verify menu exists |
| `ITEM_NOT_FOUND` | Invalid item ID | Verify item exists |
| `INVALID_PRICE` | Negative price | Use positive amounts |

## Related Documentation

- [Menus API Reference](https://dev.wix.com/docs/api-reference/business-solutions/restaurants/menus/menus/introduction)
- [Menu Items API Reference](https://dev.wix.com/docs/api-reference/business-solutions/restaurants/menus/items/items/introduction)
- [Menu Sections API Reference](https://dev.wix.com/docs/api-reference/business-solutions/restaurants/menus/sections/introduction)
- [Restaurant Orders API](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/orders/introduction)
