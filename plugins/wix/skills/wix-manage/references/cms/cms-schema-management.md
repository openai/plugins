---
name: "CMS Schema Management"
description: Create and modify CMS collection structures. Covers listing collections, creating collections with fields, adding/removing fields, and updating collection settings.
---
# CMS Schema Management

> **Standard call shape (every curl below).** The `<AUTH>` placeholder is shorthand for `Authorization: Bearer <TOKEN>` only. Every actual call ALSO needs `wix-site-id: <SITE_ID>` and (for body-bearing requests) `Content-Type: application/json`. **POST/PATCH against `wix-data/*` returns 403 without `wix-site-id`** — recipe examples below show `<AUTH>` only for brevity, but the header is required on every call you make. Token: `npx @wix/cli@latest token --site "$SITE_ID"`.

This recipe covers managing the structure (schema) of Wix CMS collections using the REST API.

## Prerequisites

1. Wix CMS enabled on the site
2. API access with CMS permissions (Manage Data Collections scope)

## Required APIs

- **Collections API**: [REST](https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-collections/introduction)

## List All Collections

**Lightweight listing (recommended for existence checks)**:
```bash
curl -X GET \
'https://www.wixapis.com/wix-data/v2/collections?fields=displayName' \
-H 'Authorization: <AUTH>'
```

**Full listing (includes all field schemas)**:
```bash
curl -X GET \
'https://www.wixapis.com/wix-data/v2/collections' \
-H 'Authorization: <AUTH>'
```

**Collection Types**: `NATIVE` (user-created), `WIX_APP` (Wix app collections), `BLOCKS_APP`, `EXTERNAL`

## Get Collection Schema

**Endpoint**: `GET /wix-data/v2/collections/{collectionId}`

```bash
curl -X GET \
'https://www.wixapis.com/wix-data/v2/collections/Products' \
-H 'Authorization: <AUTH>'
```

## Create a New Collection

**Endpoint**: `POST /wix-data/v2/collections`

```json
{
  "collection": {
    "id": "Products",
    "displayName": "Products",
    "fields": [
      {"key": "title", "displayName": "Title", "type": "TEXT", "required": true},
      {"key": "price", "displayName": "Price", "type": "NUMBER"},
      {"key": "description", "displayName": "Description", "type": "TEXT"},
      {"key": "inStock", "displayName": "In Stock", "type": "BOOLEAN"}
    ],
    "permissions": {
      "insert": "ADMIN",
      "update": "ADMIN",
      "remove": "ADMIN",
      "read": "ANYONE"
    }
  }
}
```

## Add a Field to Existing Collection

**Endpoint**: `POST /wix-data/v2/collections/create-field`

```json
{
  "dataCollectionId": "Products",
  "field": {
    "key": "sku",
    "displayName": "SKU",
    "type": "TEXT",
    "description": "Product SKU code"
  }
}
```

## Delete a Field from Collection

> **Warning**: This permanently deletes all data stored in this field across all items.

**Endpoint**: `POST /wix-data/v2/collections/delete-field`

```json
{
  "dataCollectionId": "Products",
  "fieldKey": "sku"
}
```

## Update Collection Settings

**Endpoint**: `PATCH /wix-data/v2/collections/{collectionId}`

```json
{
  "dataCollection": {
    "id": "Products",
    "displayName": "Product Catalog"
  }
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
| `IMAGE` | Image reference | `"wix:image://v1/..."` |
| `MEDIA_IMAGE` | Wix Media Image | `{ "url": "http://...", "height": 640, "width": 480, "alt": "Picture" }` |
| `MEDIA_VECTOR_ART` | Wix Media Vector Art | `{ "uri": "wix:vector://v1/...", "viewBox": "0 0 100 100", "contentType": "shape", "svgContent": "<svg>...</svg>" }` |
| `URL` | Web URL | `"https://example.com"` |
| `RICH_TEXT` | HTML content | `"<p>Rich text</p>"` |
| `ARRAY_STRING` | Array of strings | `["tag1", "tag2"]` |
| `OBJECT` | JSON object | `{"key": "value"}` |
| `REFERENCE` | Single reference | Item ID string |
| `MULTI_REFERENCE` | Multiple references | Array of IDs |

## Permission Levels

| Role | Description |
|------|-------------|
| `ANYONE` | All visitors (including anonymous) |
| `SITE_MEMBER` | Logged-in site members |
| `SITE_MEMBER_AUTHOR` | Members who created the item |
| `ADMIN` | Site admins only |

## Related Documentation

- [Data Collections API Reference](https://dev.wix.com/docs/api-reference/business-solutions/cms/collection-management/data-collections/introduction)
- [Data Types in Wix Data](https://dev.wix.com/docs/api-reference/business-solutions/cms/data-types-in-wix-data)
- [CMS Data Items CRUD Recipe](cms-data-items-crud.md)
