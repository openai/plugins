---
name: "CMS References And Relationships"
description: "Add, replace, or remove items from MULTI_REFERENCE fields. Use insert-references, replace-references, remove-references endpoints. Required for managing multi-reference relationships - these CANNOT be set via regular insert/update/patch operations. Also covers single references and querying with expanded references."
---
# CMS References & Relationships

> **Standard call shape (every curl below).** The `<AUTH>` placeholder is shorthand for `Authorization: Bearer <TOKEN>` only. Every actual call ALSO needs `wix-site-id: <SITE_ID>` and (for body-bearing requests) `Content-Type: application/json`. **POST/PATCH against `wix-data/*` returns 403 without `wix-site-id`** — recipe examples below show `<AUTH>` only for brevity, but the header is required on every call you make. Token: `npx @wix/cli@latest token --site "$SITE_ID"`.

This recipe covers linking CMS collections together using reference fields.

## Prerequisites

1. Wix CMS enabled on the site
2. At least two collections to link together
3. API access with CMS permissions

## Required APIs

- **Collections API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-collections/introduction)
- **Data Items API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/cms/data-items/introduction)

## Reference Types

| Type | Field Type | Relationship | Example |
|------|------------|--------------|---------|
| Single Reference | `REFERENCE` | One-to-one, Many-to-one | Product → Category |
| Multi-Reference | `MULTI_REFERENCE` | One-to-many, Many-to-many | Product → Tags |

## Add a Single Reference Field

**Endpoint**: `POST /wix-data/v2/collections/create-field`

```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/collections/create-field' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "Products",
  "field": {
    "key": "category",
    "displayName": "Category",
    "type": "REFERENCE",
    "typeMetadata": {
      "reference": {
        "referencedCollectionId": "Categories"
      }
    }
  }
}'
```

## Add a Multi-Reference Field

**Endpoint**: `POST /wix-data/v2/collections/create-field`

```bash
curl -X POST \
'https://www.wixapis.com/wix-data/v2/collections/create-field' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "dataCollectionId": "Products",
  "field": {
    "key": "tags",
    "displayName": "Tags",
    "type": "MULTI_REFERENCE",
    "typeMetadata": {
      "multiReference": {
        "referencedCollectionId": "Tags",
        "referencingFieldKey": "products",
        "referencingDisplayName": "Products"
      }
    }
  }
}'
```

## Insert Multi-Reference Links

**Endpoint**: `POST /wix-data/v2/bulk/items/insert-references`

```json
{
  "dataCollectionId": "Products",
  "dataItemReferences": [
    {
      "referringItemId": "product-item-id",
      "referringItemFieldName": "tags",
      "referencedItemId": "tag-1-item-id"
    },
    {
      "referringItemId": "product-item-id",
      "referringItemFieldName": "tags",
      "referencedItemId": "tag-2-item-id"
    }
  ],
  "returnEntity": true
}
```

## Replace All References

**Endpoint**: `POST /wix-data/v2/items/replace-references`

```json
{
  "dataCollectionId": "Products",
  "referringItemId": "product-item-id",
  "referringItemFieldName": "tags",
  "newReferencedItemIds": ["new-tag-1-id", "new-tag-2-id", "new-tag-3-id"]
}
```

> **Note**: To remove all references, pass an empty array for `newReferencedItemIds`.

## Remove References (Bulk)

**Endpoint**: `POST /wix-data/v2/bulk/items/remove-references`

```json
{
  "dataCollectionId": "Products",
  "dataItemReferences": [
    {
      "referringItemId": "product-id-1",
      "referringItemFieldName": "tags",
      "referencedItemId": "tag-to-remove-id"
    }
  ]
}
```

## Query with Referenced Items Expanded

**Endpoint**: `POST /wix-data/v2/items/query`

```json
{
  "dataCollectionId": "Products",
  "query": {
    "filter": {
      "inStock": true
    }
  },
  "includeReferencedItems": ["category", "tags"]
}
```

## Reference Query Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Exact match (single reference) | `{ "category": "id" }` |
| `$hasSome` | Has at least one of | `{ "tags": { "$hasSome": ["id1", "id2"] } }` |
| `$hasAll` | Has all of | `{ "tags": { "$hasAll": ["id1", "id2"] } }` |

## Related Documentation

- [Data Items API Reference](https://dev.wix.com/docs/api-reference/business-solutions/cms/data-items/introduction)
- [Collections API Reference](https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-collections/introduction)
- [CMS Schema Management Recipe](cms-schema-management.md)
