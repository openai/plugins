---
name: "CMS Data Operations Extended"
description: Additional CMS data operations including count, upsert (bulk save), and update by filter patterns.
---
# CMS Data Operations Extended

This recipe covers additional CMS data operations not included in the basic CRUD recipe.

## Prerequisites

1. Wix CMS enabled on the site
2. Collections created with data
3. API access with CMS permissions

## Required APIs

- **Data Items API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/cms/data-items/introduction)

## Count Data Items

Count items in a collection, optionally with filters.

**Endpoint**: `POST /wix-data/v2/items/count`

**Count All Items**:
```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/items/count' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "Products"
}'
```

**Response**:
```json
{
  "totalCount": 42
}
```

**Count with Filter**:
```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/items/count' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "Products",
  "filter": {
    "inStock": true
  }
}'
```

**Count with Complex Filter**:
```json
{
  "dataCollectionId": "Products",
  "filter": {
    "$and": [
      { "inStock": true },
      { "price": { "$gte": 50 } }
    ]
  }
}
```

## Bulk Save (Upsert)

Insert new items or update existing items in a single operation. This is useful for syncing data.

**Endpoint**: `POST /wix-data/v2/bulk/items/save`

**Request Body**:
```json
{
  "dataCollectionId": "Products",
  "dataItems": [
    {
      "id": "existing-item-id",
      "data": {
        "title": "Updated Product",
        "price": 199.99,
        "inStock": true
      }
    },
    {
      "data": {
        "title": "New Product",
        "price": 79.99,
        "inStock": true
      }
    }
  ],
  "returnEntity": true
}
```

### Bulk Save Behavior

| Scenario | Action |
|----------|--------|
| No `id` provided | INSERT - Creates new item with generated ID |
| `id` provided, doesn't exist | INSERT - Creates new item with provided ID |
| `id` provided, exists | UPDATE - Replaces existing item |

> **Warning**: When updating, the entire item is replaced. Include all fields you want to keep.

## Update by Filter Pattern

Wix CMS doesn't have a direct "update by filter" API. Use this two-step pattern:

### 3.1: Query Items to Update

```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/items/query' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "Products",
  "query": {
    "filter": {
      "category": "electronics"
    }
  }
}'
```

### 3.2: Bulk Update Those Items

> **Important**: Use `id` (not `_id`) at the element level. The `data` object should NOT contain `_id`.

```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/bulk/items/update' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "Products",
  "dataItems": [
    {
      "id": "item-1-from-query",
      "data": {
        "title": "Updated Title 1",
        "price": 99.99,
        "onSale": true
      }
    },
    {
      "id": "item-2-from-query",
      "data": {
        "title": "Updated Title 2",
        "price": 149.99,
        "onSale": true
      }
    }
  ]
}'
```

### Alternative: Bulk Patch (Partial Update)

If you only want to update specific fields without replacing the entire item, use Bulk Patch:

**Endpoint**: `POST /wix-data/v2/bulk/items/patch`

> **Important**: This endpoint uses `patches` array with `fieldModifications`, NOT `dataItems`. Do not confuse with bulk update.

```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/bulk/items/patch' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "Products",
  "patches": [
    {
      "dataItemId": "item-1",
      "fieldModifications": [
        {
          "fieldPath": "onSale",
          "action": "SET_FIELD",
          "setFieldOptions": {
            "value": true
          }
        }
      ]
    }
  ]
}'
```

> **Common error**: If you get `WDE0080: patches must not be empty`, you sent `dataItems` instead of `patches`. Use the format above.

## Truncate Collection

Remove all items from a collection (dangerous operation).

**Endpoint**: `POST /wix-data/v2/items/truncate`

```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/items/truncate' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "TestCollection"
}'
```

> **Warning**: This permanently deletes ALL items in the collection. Use with extreme caution.

## Aggregate Data

Perform calculations on collection data using a pipeline of sequential stages.

**Endpoint**: `POST /wix-data/v2/items/aggregate-pipeline`

**Count by Category**:
```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/items/aggregate-pipeline' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "Products",
  "pipeline": {
    "stages": [
      {
        "group": {
          "groupIds": [
            {"key": "category", "expression": {"fieldPath": "category"}}
          ],
          "accumulators": [
            {
              "resultFieldName": "count",
              "sum": {"expression": {"numeric": 1}}
            }
          ]
        }
      }
    ]
  }
}'
```

## Operation Comparison

| Operation | Use Case | Behavior |
|-----------|----------|----------|
| **Bulk Insert** | Add new items only | Fails if ID exists |
| **Bulk Update** | Update existing items | Fails if ID doesn't exist, replaces entire item |
| **Bulk Save** | Upsert (insert or update) | Creates or updates based on ID |
| **Bulk Patch** | Partial update | Only modifies specified fields |

## Related Documentation

- [Data Items API Reference](https://dev.wix.com/docs/api-reference/business-solutions/cms/data-items/introduction)
- [CMS Operations Best Practices](cms-data-items-crud.md)
- [CMS Schema Management](cms-schema-management.md)
