---
name: "Create Product (Catalog V1)"
description: Create products using the Catalog V1 Products API. Use this recipe when the site's catalog version is CATALOG_V1. Covers simple product creation, product with options, and key V1 request structure differences from V3.
---
# RECIPE: Business Recipe - Create Product (Catalog V1)

## STEP 1: Create a Simple Product

Use `POST https://www.wixapis.com/stores/v1/products` to create a product.

**CRITICAL: Description accepts an HTML string in V1** (unlike V3 which requires rich text nodes).

```bash
curl -X POST 'https://www.wixapis.com/stores/v1/products' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "product": {
    "name": "Air Max Runner",
    "description": "<p>Premium running sneaker with advanced cushioning technology.</p>",
    "visible": true,
    "productType": "physical",
    "priceData": {
      "price": 129.99
    }
  }
}'
```

**Key V1 fields:**

| Field | Type | Notes |
|---|---|---|
| `name` | string | Required. Max 80 characters |
| `description` | string | HTML string — NOT rich text nodes (e.g. `"<p>text</p>"`) |
| `productType` | string | `"physical"` only (digital not supported via API) |
| `priceData.price` | number | Product base price |
| `visible` | boolean | Whether the product is visible to customers |

---

## STEP 2: Create a Product with Options

In V1, options are defined via `productOptions`. Variants are **auto-generated** from the choices — you do not need to define them manually.

```bash
curl -X POST 'https://www.wixapis.com/stores/v1/products' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
  "product": {
    "name": "Colombian Arabica",
    "description": "<p>The best organic coffee that Colombia has to offer.</p>",
    "visible": true,
    "productType": "physical",
    "priceData": {
      "price": 35
    },
    "productOptions": [
      {
        "name": "Weight",
        "optionType": "drop_down",
        "choices": [
          { "value": "250g", "description": "250g", "inStock": true, "visible": true },
          { "value": "500g", "description": "500g", "inStock": true, "visible": true }
        ]
      },
      {
        "name": "Ground for",
        "optionType": "drop_down",
        "choices": [
          { "value": "Stovetop", "description": "Stovetop", "inStock": true, "visible": true },
          { "value": "Filter", "description": "Filter", "inStock": true, "visible": true }
        ]
      }
    ]
  }
}'
```

**V1 Options structure:**
- `optionType`: `"drop_down"` for text choices, `"color"` for color swatches
- `choices[].description`: Display name shown to customers
- `choices[].value`: Internal value (use hex color code for `color` type, e.g. `"#000000"`)
- `choices[].inStock`: Whether this choice is in stock
- `choices[].visible`: Whether this choice is visible to customers

**Variants in V1 responses** are returned as an object with option name keys:
```json
"choices": {
  "Weight": "250g",
  "Ground for": "Stovetop"
}
```
This is different from V3 which uses an array structure.

---

## Key Differences from V3

| Feature | Catalog V1 | Catalog V3 |
|---|---|---|
| Create endpoint | `POST /stores/v1/products` | `POST /stores/v3/products` |
| Description | HTML string (`"<p>text</p>"`) | Rich text nodes object |
| Options field | `productOptions` | `options` |
| Option type field | `optionType` (`drop_down`, `color`) | `optionRenderType` (`TEXT_CHOICES`, `SWATCH_CHOICES`) |
| Choice visibility | `choices[].visible` | `choices[].isVisible` |
| Variants | Auto-generated from choices | Must be explicitly defined in `variantsInfo.variants` |
| Variant choices | Object: `{"Weight": "250g"}` | Array of `optionChoiceNames` |
| Price field | `priceData.price` (number) | `price.actualPrice.amount` (string) |

---

## Important Notes

- **Never use `/stores/v3/` endpoints on a CATALOG_V1 site** — they return `428 Precondition Required`.
- Check the site's catalog version in dynamic context before choosing endpoints.
- `productType` only supports `"physical"` via the API.
- To add media to a product, use the separate **Add Product Media** endpoint after creation.
- To query products on a V1 site, see [Query Products (Catalog V1)](query-products-catalog-v1.md).

## References

- [V1 Create Product](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v1/catalog/create-product)
- [Catalog Versioning Overview](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-versioning/introduction)
