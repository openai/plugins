---
name: "Update Product with Options (Catalog V3)"
description: Modifies existing products and variants using Catalog V3 Products API. Covers adding/removing option choices, variant-specific pricing, and revision-based updates to prevent conflicts.
---
**RECIPE**: Business Recipe - Updating a Wix Store Product (Catalog V3)

Use this recipe to update an existing Catalog V3 product: description, media, options, variants, prices, or stock-related inventory records.

## Before Any Product Update

Every Catalog V3 product update is revision-based:

- If the user gives a product name instead of a product ID, use [Search Products](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/products-v3/search-products) and choose the exact product name match.
- Use [Get Product](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/products-v3/get-product) to retrieve the current product and `product.revision`.
- Include `product.id` and the current `product.revision` in every [Update Product](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/products-v3/update-product) PATCH body.
- For simple text/HTML description updates, prefer `plainDescription`. Use `description` only when sending a Rich Content object.

### Find the product by name

```bash
curl -X POST "https://www.wixapis.com/stores/v3/products/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: <AUTH>" \
  -d '{
    "search": {
      "expression": "Product name"
    }
  }'
```

For product-name lookup, prefer Search Products before retrieving the product by ID.

### Get the current revision

```bash
curl -X GET "https://www.wixapis.com/stores/v3/products/{productId}" \
  -H "Authorization: <AUTH>"
```

## Common Update Patterns

### Update Description Only

For a normal user request like "set the product description to X", use `plainDescription` with valid HTML. The API converts it to rich content.

Do not send a plain string in `description`. `description` is a Rich Content object.

```bash
curl -X PATCH "https://www.wixapis.com/stores/v3/products/{productId}" \
  -H "Content-Type: application/json" \
  -H "Authorization: <AUTH>" \
  -d '{
    "product": {
      "id": "{productId}",
      "revision": "{currentRevision}",
      "plainDescription": "<p>A great product for everyone.</p>"
    }
  }'
```

Use `description` only when you intentionally need to send Rich Content:

```bash
curl -X PATCH "https://www.wixapis.com/stores/v3/products/{productId}" \
  -H "Content-Type: application/json" \
  -H "Authorization: <AUTH>" \
  -d '{
    "product": {
        "id": "{productId}",
        "revision": "{currentRevision}",
        "description": {
            "nodes": [
                {
                    "type": "PARAGRAPH",
                    "id": "description",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {
                                "text": "Updated product description."
                            }
                        }
                    ],
                    "paragraphData": {
                        "textStyle": {
                            "textAlignment": "AUTO"
                        }
                    }
                }
            ],
            "metadata": {
                "version": 1
            }
        }
    }
  }'
```

### Update Options and Variants

When adding or changing options and variants, send the full option definitions and one variant for each option-choice combination. Use `optionChoiceNames` to reference choices.

```bash
curl -X PATCH "https://www.wixapis.com/stores/v3/products/{productId}" \
  -H "Content-Type: application/json" \
  -H "Authorization: <AUTH>" \
  -d '{
    "product": {
      "id": "{productId}",
      "revision": "{currentRevision}",
      "options": [
        {
          "name": "Color",
          "optionRenderType": "SWATCH_CHOICES",
          "choicesSettings": {
            "choices": [
              {
                "name": "White",
                "choiceType": "ONE_COLOR",
                "colorCode": "#FFFFFF"
              },
              {
                "name": "Red",
                "choiceType": "ONE_COLOR",
                "colorCode": "#FF0000"
              },
              {
                "name": "Black",
                "choiceType": "ONE_COLOR",
                "colorCode": "#000000"
              }
            ]
          }
        }
      ],
      "variantsInfo": {
        "variants": [
          {
            "choices": [
              {
                "optionChoiceNames": {
                  "optionName": "Color",
                  "choiceName": "White",
                  "renderType": "SWATCH_CHOICES"
                }
              }
            ],
            "price": {
              "actualPrice": {
                "amount": "270.00"
              }
            }
          },
          {
            "choices": [
              {
                "optionChoiceNames": {
                  "optionName": "Color",
                  "choiceName": "Red",
                  "renderType": "SWATCH_CHOICES"
                }
              }
            ],
            "price": {
              "actualPrice": {
                "amount": "270.00"
              }
            }
          },
          {
            "choices": [
              {
                "optionChoiceNames": {
                  "optionName": "Color",
                  "choiceName": "Black",
                  "renderType": "SWATCH_CHOICES"
                }
              }
            ],
            "price": {
              "actualPrice": {
                "amount": "270.00"
              }
            }
          }
        ]
      }
    }
  }'
```

When updating existing variants, include each existing variant `id`. If no GUID is passed, a variant is created with a new GUID.

### Convert a Simple Product to Color Variants

When adding the first option to a simple product, do not preserve a choice-less default variant unchanged. A simple product often has one existing variant with price or stock but no `choices`. After you add a `Color` option, every variant in `variantsInfo.variants` must include choices that match the product options.

Use the existing default variant as source data only. For example, copy its price if the user did not ask to change price, then send a complete optioned variants list where each variant has:

```json
{
  "choices": [
    {
      "optionChoiceNames": {
        "optionName": "Color",
        "choiceName": "Red",
        "renderType": "SWATCH_CHOICES"
      }
    }
  ],
  "price": {
    "actualPrice": {
      "amount": "{existingOrRequestedPrice}"
    }
  }
}
```

After the product update returns the new variant IDs, use those IDs to set inventory.

### Set Stock for New Variants

Inventory is handled separately from product updates. After the product update returns variant IDs, use [Bulk Create Inventory Items](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/inventory-items-v3/bulk-create-inventory-items) with `productId`, `variantId`, and `quantity`.

If the store has multiple inventory locations, include `locationId`; otherwise the store's default location is used.
After bulk inventory create, check `bulkActionMetadata.totalSuccesses` and `results[].itemMetadata.success`. Returned inventory entities are under `results[].item`, not a top-level `inventoryItems` field; confirm stock from `results[].item.quantity`.

```bash
curl -X POST "https://www.wixapis.com/stores/v3/bulk/inventory-items/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: <AUTH>" \
  -d '{
    "inventoryItems": [
      {
        "productId": "{productId}",
        "variantId": "{redVariantId}",
        "quantity": 10
      },
      {
        "productId": "{productId}",
        "variantId": "{blueVariantId}",
        "quantity": 10
      }
    ],
    "returnEntity": true
  }'
```

### Update Media Only

```bash
curl -X PATCH "https://www.wixapis.com/stores/v3/products/{productId}" \
  -H "Content-Type: application/json" \
  -H "Authorization: <AUTH>" \
  -d '{
    "product": {
      "id": "{productId}",
      "revision": "{currentRevision}",
      "media": {
        "itemsInfo": {
          "items": [
            {
              "url": "https://static.wixstatic.com/media/your-image.jpg",
              "altText": "Product image"
            }
          ]
        }
      }
    }
  }'
```

### Update Variant Price Only

```bash
curl -X PATCH "https://www.wixapis.com/stores/v3/products/{productId}" \
  -H "Content-Type: application/json" \
  -H "Authorization: <AUTH>" \
  -d '{
    "product": {
      "id": "{productId}",
      "revision": "{currentRevision}",
      "variantsInfo": {
        "variants": [
          {
            "id": "{existingVariantId}",
            "price": {
              "actualPrice": {
                "amount": "29.99"
              }
            }
          }
        ]
      }
    }
  }'
```

## Important Notes

- To update array fields like `options`, `modifiers`, `variantsInfo.variants`, and any others, pass the entire existing array. Passing only the changed item overwrites the whole array.
- To update `variantsInfo.variants`, also pass `options`, and vice versa. Variants and options are mutually dependent and must stay aligned.
- When converting a simple product to an optioned product, rebuild the variants list so every variant has `choices`; do not keep an existing choice-less default variant unchanged.
- Always include `choicesSettings` with the complete list of choices when updating a product with options.
- Use `optionChoiceNames` rather than `optionChoiceIds` in variants for more reliable updates.
- Include the `renderType` in `optionChoiceNames`.

## Error Message Reference

| Error Message | Meaning | Fix |
|---------------|---------|-----|
| `revision must not be empty` | Missing optimistic lock | GET product first and include `product.revision` in PATCH |
| `revision mismatch` | Stale revision | Re-GET product and retry with the new revision |
| `Expected an object` for `description` | Sent `description` as a string | Use `plainDescription` for HTML strings, or send `description` as Rich Content |
| `choicesSettings must not be empty` | Missing choices array | Include full `choicesSettings.choices` array |
| `Missing product option choices` | Variant references non-existent option | Use `optionChoiceNames` with exact option and choice names |
| `price must not be empty` | A variant was created or replaced without a price | Include `price.actualPrice.amount` on every new variant |
| `Missing option choices` or `INVALID_DEFAULT_VARIANT` | Product has options but at least one variant has no matching choices | Rebuild `variantsInfo.variants` so every variant includes choices for all product options |
