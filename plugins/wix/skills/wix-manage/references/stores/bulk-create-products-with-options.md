---
name: "Bulk Create Products with Options (Catalog V3)"
description: Uses bulk products endpoint to create multiple products with inventory in a single request. Handles variant generation from options, media format requirements, and error handling for partial failures.
---
# RECIPE: Business Recipe - Bulk Creating Wix Store Products with inventory and options

> **Standard call shape (every curl below).** The `<AUTH>` placeholder is shorthand for `Authorization: Bearer <TOKEN>` only. Every actual call ALSO needs `wix-site-id: <SITE_ID>` and (for body-bearing requests) `Content-Type: application/json`. **POST against `stores/v3/bulk/*` returns 403 without `wix-site-id`** — recipe examples below show `<AUTH>` only for brevity, but the header is required on every call you make. Token: `npx @wix/cli@latest token --site "$SITE_ID"`.

Learn how to create multiple Wix store products with customizable options like colors, sizes, or other variants in a single bulk operation, allowing efficient creation of product catalogs.

---

## ⚠️ CRITICAL REQUIREMENTS - READ FIRST

**API ENDPOINT:** `https://www.wixapis.com/stores/v3/bulk/products-with-inventory/create`

**MEDIA FORMAT - MUST INCLUDE BOTH SECTIONS:**

```json
"media": {
    "main": {
        "url": "https://images.unsplash.com/photo-example?w=400&h=400&fit=crop&crop=center",
        "altText": "Product Name - Main Product Image"
    },
    "itemsInfo": {
        "items": [
            {
                "url": "https://images.unsplash.com/photo-example?w=400&h=400&fit=crop&crop=center",
                "altText": "Product Name - Product View"
            }
        ]
    }
}
```

**VARIANTS:** The recipe shows ALL possible variant combinations (Cartesian product) with 3 visible variants per product. Each product has 6 total variants: 3 visible + 3 hidden for future use.

**❌ COMMON FAILURES:**

* Missing `itemsInfo` section in media (media won't work)
* Missing URL parameters `?w=400&h=400&fit=crop&crop=center`

## Article: Steps for Bulk Creating Wix Store Products with Options

## STEP 1: bulk create products with options and variants

1. bulk create products with options and create variants for them - Wix REST API: [Bulk Create Products With Inventory](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/products-v3/bulk-create-products-with-inventory) **CRITICAL: USE THIS WORKING EXAMPLE - if more products are required copy the same format exactly to create more**

```bash
curl -X POST "https://www.wixapis.com/stores/v3/bulk/products-with-inventory/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: <AUTH>" \
  -d '{
    "products": [
        {
            "name": "Pro Basketball Sneaker",
            "description": {
                "nodes": [
                    {
                        "type": "PARAGRAPH",
                        "id": "desc1",
                        "nodes": [
                            {
                                "type": "TEXT",
                                "textData": {
                                    "text": "High-performance basketball sneaker with superior ankle support and responsive court feel."
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
                    "version": 1,
                    "id": "basketball-desc-001"
                }
            },
            "visible": true,
            "visibleInPos": true,
            "productType": "PHYSICAL",
            "physicalProperties": {},
            "media": {
                "main": {
                    "url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop&crop=center",
                    "altText": "Pro Basketball Sneaker - Main Product Image"
                },
                "itemsInfo": {
                    "items": [
                        {
                            "url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop&crop=center",
                            "altText": "Pro Basketball Sneaker - Product View"
                        }
                    ]
                }
            },
            "options": [
                {
                    "name": "Size",
                    "optionRenderType": "TEXT_CHOICES",
                    "choicesSettings": {
                        "choices": [
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "8"
                            },
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "9"
                            },
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "10"
                            }
                        ]
                    }
                },
                {
                    "name": "Color",
                    "optionRenderType": "SWATCH_CHOICES",
                    "choicesSettings": {
                        "choices": [
                            {
                                "choiceType": "ONE_COLOR",
                                "name": "Red",
                                "colorCode": "#FF0000"
                            },
                            {
                                "choiceType": "ONE_COLOR",
                                "name": "Blue",
                                "colorCode": "#0000FF"
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
                                    "optionName": "Size",
                                    "choiceName": "8",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "159.99"
                            },
                            "compareAtPrice": {
                              "amount": "200.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 25,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "8",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Blue",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "159.99"
                            },
                            "compareAtPrice": {
                              "amount": "200.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 25,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "9",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "159.99"
                            },
                            "compareAtPrice": {
                              "amount": "200.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 30,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "9",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Blue",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "159.99"
                            },
                            "compareAtPrice": {
                              "amount": "200.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 30,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "10",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "159.99"
                            },
                            "compareAtPrice": {
                              "amount": "200.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 20,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "10",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Blue",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "159.99"
                            },
                            "compareAtPrice": {
                              "amount": "200.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 20,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    }
                ]
            }
        },
        {
            "name": "Classic Canvas Shoes",
            "description": {
                "nodes": [
                    {
                        "type": "PARAGRAPH",
                        "id": "desc2",
                        "nodes": [
                            {
                                "type": "TEXT",
                                "textData": {
                                    "text": "Timeless canvas shoes with durable construction and comfortable fit for everyday wear."
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
                    "version": 1,
                    "id": "canvas-desc-002"
                }
            },
            "visible": true,
            "visibleInPos": true,
            "productType": "PHYSICAL",
            "physicalProperties": {},
            "media": {
                "main": {
                    "url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=400&h=400&fit=crop&crop=center",
                    "altText": "Classic Canvas Shoes - Main Product Image"
                },
                "itemsInfo": {
                    "items": [
                        {
                            "url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=400&h=400&fit=crop&crop=center",
                            "altText": "Classic Canvas Shoes - Product View"
                        }
                    ]
                }
            },
            "options": [
                {
                    "name": "Size",
                    "optionRenderType": "TEXT_CHOICES",
                    "choicesSettings": {
                        "choices": [
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "7"
                            },
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "8"
                            },
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "9"
                            }
                        ]
                    }
                },
                {
                    "name": "Color",
                    "optionRenderType": "SWATCH_CHOICES",
                    "choicesSettings": {
                        "choices": [
                            {
                                "choiceType": "ONE_COLOR",
                                "name": "White",
                                "colorCode": "#FFFFFF"
                            },
                            {
                                "choiceType": "ONE_COLOR",
                                "name": "Navy",
                                "colorCode": "#000080"
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
                                    "optionName": "Size",
                                    "choiceName": "7",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "89.99"
                            },
                            "compareAtPrice": {
                              "amount": "100.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 15,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "7",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Navy",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "89.99"
                            },
                            "compareAtPrice": {
                              "amount": "100.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 15,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "8",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "89.99"
                            },
                            "compareAtPrice": {
                              "amount": "100.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 18,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "8",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Navy",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "89.99"
                            },
                            "compareAtPrice": {
                              "amount": "100.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 18,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "9",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "89.99"
                            },
                            "compareAtPrice": {
                              "amount": "100.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 12,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "9",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Navy",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "89.99"
                            },
                            "compareAtPrice": {
                              "amount": "100.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 12,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    }
                ]
            }
        },
        {
            "name": "Running Track Shoes",
            "description": {
                "nodes": [
                    {
                        "type": "PARAGRAPH",
                        "id": "desc3",
                        "nodes": [
                            {
                                "type": "TEXT",
                                "textData": {
                                    "text": "Lightweight running shoes with responsive cushioning and breathable mesh construction for optimal performance."
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
                    "version": 1,
                    "id": "running-desc-003"
                }
            },
            "visible": true,
            "visibleInPos": true,
            "productType": "PHYSICAL",
            "physicalProperties": {},
            "media": {
                "main": {
                    "url": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400&h=400&fit=crop&crop=center",
                    "altText": "Running Track Shoes - Main Product Image"
                },
                "itemsInfo": {
                    "items": [
                        {
                            "url": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400&h=400&fit=crop&crop=center",
                            "altText": "Running Track Shoes - Product View"
                        }
                    ]
                }
            },
            "options": [
                {
                    "name": "Size",
                    "optionRenderType": "TEXT_CHOICES",
                    "choicesSettings": {
                        "choices": [
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "8"
                            },
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "9"
                            },
                            {
                                "choiceType": "CHOICE_TEXT",
                                "name": "10"
                            }
                        ]
                    }
                },
                {
                    "name": "Color",
                    "optionRenderType": "SWATCH_CHOICES",
                    "choicesSettings": {
                        "choices": [
                            {
                                "choiceType": "ONE_COLOR",
                                "name": "Black",
                                "colorCode": "#000000"
                            },
                            {
                                "choiceType": "ONE_COLOR",
                                "name": "Gray",
                                "colorCode": "#808080"
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
                                    "optionName": "Size",
                                    "choiceName": "8",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "119.99"
                            },
                            "compareAtPrice": {
                              "amount": "180.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 0,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "8",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Gray",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "119.99"
                            },
                            "compareAtPrice": {
                              "amount": "180.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 0,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "9",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "119.99"
                            },
                            "compareAtPrice": {
                              "amount": "180.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 0,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "9",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Gray",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "119.99"
                            },
                            "compareAtPrice": {
                              "amount": "180.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 0,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "10",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
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
                                "amount": "119.99"
                            },
                            "compareAtPrice": {
                              "amount": "180.00"
                            }
                        },
                        "visible": true,
                        "inventoryItem": {
                            "quantity": 0,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    },
                    {
                        "choices": [
                            {
                                "optionChoiceNames": {
                                    "optionName": "Size",
                                    "choiceName": "10",
                                    "renderType": "TEXT_CHOICES"
                                }
                            },
                            {
                                "optionChoiceNames": {
                                    "optionName": "Color",
                                    "choiceName": "Gray",
                                    "renderType": "SWATCH_CHOICES"
                                }
                            }
                        ],
                        "price": {
                            "actualPrice": {
                                "amount": "119.99"
                            },
                            "compareAtPrice": {
                              "amount": "180.00"
                            }
                        },
                        "visible": false,
                        "inventoryItem": {
                            "quantity": 0,
                            "preorderInfo": {
                                "enabled": false
                            }
                        },
                        "physicalProperties": {}
                    }
                ]
            }
        }
    ],
    "returnEntity": true
}'
```

### IMPORTANT NOTES:

* When bulk creating products with inventory YOU MUST follow the same format as single product creation but wrap all products in a "products" array. Each product MUST leave the physicalProperties and all other non required fields empty. for example: "physicalProperties": {}. In most cases the products will be physical products, and therefore MUST have the empty physicalProperties object ("physicalProperties": {}) and a corresponding "productType": "PHYSICAL".
* In case part of the request fails, retry bulk creating the failed products, by copying the exact format from the previous working example.
* When creating a Color option **YOU MUST** use the `"optionRenderType": "SWATCH_CHOICES"` and the appropriate choice type: `"choiceType": "ONE_COLOR"`, while also providing the relevant `colorCode`. This must be done similar to the example above.

**CRITICAL: Bulk Request Structure**The bulk create API requires a different endpoint and request structure:

* **URL**: `https://www.wixapis.com/stores/v3/bulk/products-with-inventory/create`
* **Body**: `{"products": [array of product objects]}`
* Each product in the array follows the exact same format as single product creation

**CRITICAL: Description Format**If you include a description, it MUST use Wix's rich text nodes structure, NOT a plain string. Plain strings will cause "Expected an object" API errors.

**WRONG:** `"description": "Your text here"` **CORRECT:**

```json
"description": {
    "nodes": [
        {
            "type": "PARAGRAPH",
            "id": "desc1",
            "nodes": [
                {
                    "type": "TEXT",
                    "textData": {
                        "text": "Your product description here"
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
        "version": 1,
        "id": "unique-desc-id"
    }
}
```

**CRITICAL: Media Format**To add product images, use the media object with main image and optional additional items.**YOU MUST** add an image to each product, with a url from the web which should be relevant to the product.

```json
"media": {
    "main": {
        "url": "https://images.unsplash.com/photo-example?w=400&h=400&fit=crop&crop=center",
        "altText": "Product Name - Main Product Image"
    },
    "itemsInfo": {
        "items": [
            {
                "url": "https://images.unsplash.com/photo-example?w=400&h=400&fit=crop&crop=center",
                "altText": "Product Name - Product View"
            }
        ]
    }
}
```

**CRITICAL: Options Structure**Each option MUST include:

* `optionRenderType`: "TEXT_CHOICES" for text-based choices
* `choicesSettings`: Object containing the choices array
* `choicesSettings.choices`: Array with at least one choice
* Each choice MUST have `choiceType`: "CHOICE_TEXT" and `name`

**CRITICAL: Variants Structure**

* Create one variant for EVERY combination of option choices (Cartesian product of all options)
* In these examples: Each product creates ALL possible combinations: Size options x Color options = 6 total variants each
* Each variant must reference ALL options defined on the product
* Use `optionChoiceNames` structure with `optionName`, `choiceName`, and `renderType`
* Price must use `price.actualPrice.amount` with string values
* Include inventory information with `inventoryItem.quantity`
* Use `visible: true` for variants you want customers to see, `visible: false` for variants you want to keep hidden but available for future use
* **Pro Basketball Sneaker**: 6 variants total (3 visible: Size 8+Red, Size 9+Blue, Size 10+Red)
* **Classic Canvas Shoes**: 6 variants total (3 visible: Size 7+White, Size 8+Navy, Size 9+Navy)
* **Running Track Shoes**: 6 variants total (3 visible: Size 8+Black, Size 9+Gray, Size 10+Black)

## Common Issues and Troubleshooting

### 1. "Expected an object" Error in Description
This occurs when using a plain string instead of the rich text nodes structure. Always use the nodes format shown above.

### 2. Media Not Displaying
Ensure both `main` and `itemsInfo` sections are included in the media object, and URLs include the required parameters.

### 3. Options Not Working
Verify that each option has the correct `optionRenderType` and `choicesSettings` structure.

### 4. Variants Missing Choices
Each variant must include choices for ALL options defined on the product.

### 5. Invalid Color Options
Color options must use `optionRenderType: "SWATCH_CHOICES"` and `choiceType: "ONE_COLOR"` with a valid `colorCode`.

### 6. Bulk Request Failures
If part of the bulk request fails, extract the failed products and retry them separately using the same format.
