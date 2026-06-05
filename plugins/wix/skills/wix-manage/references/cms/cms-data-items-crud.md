---
name: "CMS Data Items CRUD"
description: "Add, query, update, and delete items in CMS collections. Use this to insert content, bulk insert/update/patch/delete items, query with filters, and manage collection data. Key endpoints: /wix-data/v2/items, /wix-data/v2/bulk/items/*."
---
# CMS Data Items CRUD

> **Standard call shape (every curl below).** The `<AUTH>` placeholder is shorthand for `Authorization: Bearer <TOKEN>` only. Every actual call ALSO needs `wix-site-id: <SITE_ID>` and (for body-bearing requests) `Content-Type: application/json`. **POST/PATCH against `wix-data/*` returns 403 without `wix-site-id`** — recipe examples below show `<AUTH>` only for brevity, but the header is required on every call you make. Token: `npx @wix/cli@latest token --site "$SITE_ID"`.

This recipe covers basic Create, Read, Update, Delete (CRUD) operations for Wix CMS data items.

## Prerequisites

1. Wix CMS enabled on the site
2. Collections already created (see [CMS Schema Management](cms-schema-management.md))
3. API access with CMS permissions

## Required APIs

- **Data Items API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/cms/data-items/introduction)

---

## Know the Schema First

Before inserting or updating items, you need to know the collection's field names and types. If you don't already know the schema:

1. **Query existing items** - Fetch a few items to infer field names from the data
2. **Get collection schema** - Use `GET /collections/{dataCollectionId}` for full field definitions
3. **List collections** - Use `GET /collections?fields=displayName` to see what collections exist (see [Schema Management](cms-schema-management.md))

It may be, that user refers to schema by its `displayName` rather than `id`, if collection is not found list all collections to find the right `id` (`dataCollectionId`) to use.

---

## Insert Data Item

**Endpoint**: `POST /wix-data/v2/items`

**Request Body**:
```json
{
  "dataCollectionId": "Products",
  "dataItem": {
    "data": {
      "title": "Wireless Headphones",
      "price": 149.99,
      "description": "Premium wireless headphones with noise cancellation",
      "inStock": true,
      "tags": ["wireless", "audio", "premium"]
    }
  }
}
```

**Response**:
```json
{
  "dataItem": {
    "id": "generated-item-id",
    "dataCollectionId": "Products",
    "data": {
      "_id": "generated-item-id",
      "title": "Wireless Headphones",
      "price": 149.99,
      "_createdDate": { "$date": "2024-01-15T10:00:00.000Z" },
      "_updatedDate": { "$date": "2024-01-15T10:00:00.000Z" }
    }
  }
}
```

## Bulk Insert Items

**Endpoint**: `POST /wix-data/v2/bulk/items/insert`

**Request Body**:
```json
{
  "dataCollectionId": "Products",
  "dataItems": [
    {
      "data": {
        "title": "Bluetooth Speaker",
        "price": 79.99,
        "inStock": true
      }
    },
    {
      "data": {
        "title": "USB-C Cable",
        "price": 12.99,
        "inStock": true
      }
    },
    {
      "data": {
        "title": "Laptop Stand",
        "price": 49.99,
        "inStock": false
      }
    }
  ],
  "returnEntity": true
}
```

## Query Data Items

**Endpoint**: `POST /wix-data/v2/items/query`

**Basic Query**:
```json
{
  "dataCollectionId": "Products",
  "query": {
    "filter": {
      "inStock": true
    },
    "sort": [
      {
        "fieldName": "price",
        "order": "ASC"
      }
    ],
    "paging": {
      "limit": 50,
      "offset": 0
    }
  }
}
```

**Advanced Query with Multiple Conditions**:
```json
{
  "dataCollectionId": "Products",
  "query": {
    "filter": {
      "$and": [
        { "inStock": true },
        { "price": { "$gte": 50, "$lte": 200 } }
      ]
    }
  }
}
```

**Text Search**:
```json
{
  "dataCollectionId": "Products",
  "query": {
    "filter": {
      "title": {
        "$contains": "wireless"
      }
    }
  }
}
```

## Get Single Item

**Endpoint**: `GET /wix-data/v2/items/{itemId}?dataCollectionId={collectionId}`

```bash
curl -X GET \
'https://www.wixapis.com/wix-data/v2/items/abc123?dataCollectionId=Products' \
-H 'Authorization: <AUTH>'
```

## Update Data Item

**Endpoint**: `PUT /wix-data/v2/items/{itemId}`

**Request Body**:
```json
{
  "dataCollectionId": "Products",
  "dataItem": {
    "data": {
      "title": "Wireless Headphones Pro",
      "price": 199.99,
      "description": "Updated premium wireless headphones",
      "inStock": true
    }
  }
}
```

## Patch Data Item (Partial Update - Single Item)

**Endpoint**: `PATCH /wix-data/v2/items/{dataItemId}`

Unlike Update, this only modifies the specified fields — all other fields remain unchanged.

> **Note**: Only works on user-created collections. Wix app collections (e.g. Wix Stores Products) cannot be patched.

```json
{
  "dataCollectionId": "Products",
  "patch": {
    "dataItemId": "item-guid",
    "fieldModifications": [
      {
        "fieldPath": "price",
        "action": "SET_FIELD",
        "setFieldOptions": {
          "value": 159.99
        }
      },
      {
        "fieldPath": "description",
        "action": "REMOVE_FIELD"
      },
      {
        "fieldPath": "viewCount",
        "action": "INCREMENT_FIELD",
        "incrementFieldOptions": {
          "value": 1
        }
      }
    ]
  }
}
```

## Bulk Update Items

**Endpoint**: `POST /wix-data/v2/bulk/items/update`

> **Important**: Use `id` (not `_id`) at the element level. The `data` object should NOT contain `_id`.

```json
{
  "dataCollectionId": "Products",
  "dataItems": [
    {
      "id": "item-guid-1",
      "data": {
        "price": 159.99,
        "inStock": true
      }
    },
    {
      "id": "item-guid-2",
      "data": {
        "price": 89.99,
        "inStock": false
      }
    }
  ]
}
```

> **Note**: This replaces the entire item. Include all fields you want to keep, not just the ones you're changing.

## Bulk Patch Items (Partial Update)

**Endpoint**: `POST /wix-data/v2/bulk/items/patch`

Unlike bulk update, this only modifies the specified fields - other fields remain unchanged. **Use this for partial updates.**

> **Important**: This endpoint uses `patches` array with `fieldModifications`, NOT `dataItems`. Do not confuse with bulk update.

```json
{
  "dataCollectionId": "Products",
  "patches": [
    {
      "dataItemId": "item-guid-1",
      "fieldModifications": [
        {
          "fieldPath": "price",
          "action": "SET_FIELD",
          "setFieldOptions": {
            "value": 159.99
          }
        }
      ]
    },
    {
      "dataItemId": "item-guid-2",
      "fieldModifications": [
        {
          "fieldPath": "price",
          "action": "SET_FIELD",
          "setFieldOptions": {
            "value": 89.99
          }
        }
      ]
    }
  ]
}
```

**Setting a reference field** (single REFERENCE only):
```json
{
  "dataCollectionId": "events",
  "patches": [
    {
      "dataItemId": "event-id",
      "fieldModifications": [
        {
          "fieldPath": "venue",
          "action": "SET_FIELD",
          "setFieldOptions": {
            "value": "venue-item-id"
          }
        }
      ]
    }
  ]
}
```

**Available actions**: `SET_FIELD`, `REMOVE_FIELD`, `INCREMENT_FIELD`, `APPEND_TO_ARRAY`, `REMOVE_FROM_ARRAY`

> **Common error**: If you get `WDE0080: patches must not be empty`, you sent `dataItems` instead of `patches`. Use the format above.

> **Recommended**: Use bulk patch instead of bulk update when you only need to change specific fields.

> **Reference Fields**:
> - **Single REFERENCE**: CAN be set during insert/update by providing the referenced item's ID as the field value (e.g., `"venue": "venue-item-id"`)
> - **MULTI_REFERENCE**: **STOP** - You cannot use this recipe for multi-reference fields. They cannot be set via insert/update/patch.
>
> **For MULTI_REFERENCE operations (add speakers, assign tags, link categories, etc.):**
> **READ [CMS References & Relationships](cms-references-and-relationships.md)** for the exact endpoints and request bodies:
> - `POST /wix-data/v2/bulk/items/insert-references` - add references
> - `POST /wix-data/v2/items/replace-references` - replace all references
> - `POST /wix-data/v2/bulk/items/remove-references` - remove references
>
> Error `WDE0303` occurs when attempting to set multi-reference fields via data operations.

## Delete Data Item

**Endpoint**: `DELETE /wix-data/v2/items/{itemId}?dataCollectionId={collectionId}`

```bash
curl -X DELETE \
'https://www.wixapis.com/wix-data/v2/items/abc123?dataCollectionId=Products' \
-H 'Authorization: <AUTH>'
```

## Bulk Delete Items

**Endpoint**: `POST /wix-data/v2/bulk/items/remove`

```json
{
  "dataCollectionId": "Products",
  "dataItemIds": ["item-id-1", "item-id-2", "item-id-3"]
}
```

## Field Types Reference

| Type | Description | Example Value |
|------|-------------|---------------|
| `TEXT` | String | `"Hello World"` |
| `NUMBER` | Numeric | `99.99` |
| `BOOLEAN` | True/false | `true` |
| `DATE` | Date only | `"2024-01-15"` |
| `DATETIME` | Date and time | `{ "$date": "2024-01-15T10:00:00.000Z" }` |
| `IMAGE` | Image reference (HTTP url or wix:image://v1/{mediaId}/{friendlyName}) | `"wix:image://v1/3f72369f2219e2ee853e9e3df0217ce1.jpg/Colorful%20Business%20Cards.jpg"` |
| `VIDEO` | Video reference (HTTP url or wix:video://v1/{mediaId}/{friendlyName}) | `"wix:video://v1/11062b_484182533ede4b9a81329daf20238867/Sketching%20Design%20Concepts#posterUri=11062b_484182533ede4b9a81329daf20238867f000.jpg&posterWidth=1920&posterHeight=1080"` |
| `DOCUMENT` | Document reference  (HTTP url or wix:document://v1/{mediaId}) | `"wix:document://v1/..."` |
| `MEDIA_IMAGE` | Wix Media Image | `{ "url": "http://...", "height": 640, "width": 480, "alt": "Picture" }` |
| `MEDIA_VECTOR_ART` | Wix Media Vector Art | `{ "uri": "wix:vector://v1/...", "viewBox": "0 0 100 100", "contentType": "shape", "svgContent": "<svg>...</svg>" }` |
| `URL` | Web URL | `"https://example.com"` |
| `RICH_TEXT` | HTML content | `"<p>Rich text</p>"` |
| `EMAIL` | Email | `"example@wix.com"` |
| `RICH_CONTENT` | Structured content | Complex object |
| `ADDRESS` | Address object | Address fields |
| `ARRAY_STRING` | Array of strings | `["tag1", "tag2"]` |
| `OBJECT` | JSON object | `{"key": "value"}` |
| `REFERENCE` | Single reference | Item ID string |
| `MULTI_REFERENCE` | Multiple references, use separate *reference* endpoints to manipulate, `include` to include in queries | Array of IDs |

---

## Query Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equal | `{ "status": { "$eq": "active" } }` |
| `$ne` | Not equal | `{ "status": { "$ne": "archived" } }` |
| `$gt` | Greater than | `{ "price": { "$gt": 100 } }` |
| `$gte` | Greater or equal | `{ "price": { "$gte": 100 } }` |
| `$lt` | Less than | `{ "price": { "$lt": 50 } }` |
| `$lte` | Less or equal | `{ "price": { "$lte": 50 } }` |
| `$in` | In array | `{ "status": { "$in": ["active", "pending"] } }` |
| `$contains` | Contains string | `{ "title": { "$contains": "pro" } }` |
| `$startsWith` | Starts with | `{ "title": { "$startsWith": "Wireless" } }` |
| `$and` | All conditions | `{ "$and": [{...}, {...}] }` |
| `$or` | Any condition | `{ "$or": [{...}, {...}] }` |

---

## Pagination

### Offset-Based (Simple)
```json
{
  "query": {
    "paging": {
      "limit": 50,
      "offset": 100
    }
  }
}
```

### Cursor-Based (Large Datasets)
```json
{
  "query": {
    "cursorPaging": {
      "limit": 50,
      "cursor": "cursor-from-previous-response"
    }
  }
}
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `COLLECTION_NOT_FOUND` | Invalid collection ID | Check collection exists |
| `ITEM_NOT_FOUND` | Invalid item ID | Verify item exists |
| `VALIDATION_ERROR` | Invalid field value | Check field types |
| `DUPLICATE_KEY` | Duplicate unique field | Use unique values |
| `PERMISSION_DENIED` | Insufficient access | Check API permissions |
| `WDE0007` | Bulk update: wrong ID field name | Use `id` not `_id` at element level |
| `WDE0080` | Validation failed (multiple causes) | Bulk update: don't include `_id` in `data`; Bulk patch: use `patches` array not `dataItems` |
| `WDE0303` | Can't set multi-reference field via data operations | Use reference endpoints: `insert-references`, `replace-references` |

---

## Related Documentation

- [Data Items API Reference](https://dev.wix.com/docs/api-reference/business-solutions/cms/data-items/introduction)
- [CMS Schema Management](cms-schema-management.md) - Creating and modifying collections
- [CMS References & Relationships](cms-references-and-relationships.md) - Linking collections
- [CMS Data Operations Extended](cms-data-operations-extended.md) - Count, upsert, aggregate
