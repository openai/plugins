---
name: "Create Product with Options (Catalog V3)"
description: Single product creation with options using Catalog V3 Products API. Covers option types (TEXT_CHOICES, SWATCH_CHOICES), choice configuration, and automatic variant generation.
---
# RECIPE: Business Recipe - Creating a Wix Store Product with options (Catalog V3)

Learn how to create a Wix store product with customizable options like colors, sizes, or other variants, allowing customers to select their preferences when purchasing.

---

## Article: Steps for creating a Wix Store Product with Options

## STEP 1: create the product with options and variants

1. create the product with options and create variants for them - Wix REST API: [Create Product](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/products-v3/create-product) **CRITICAL: USE THIS WORKING EXAMPLE**

```bash
curl -X POST 'https://www.wixapis.com/stores/v3/products' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
    "product": {
        "name": "Air Max Runner",
        "description": {
            "nodes": [
                {
                    "type": "PARAGRAPH",
                    "id": "desc1",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {
                                "text": "Premium running sneaker with advanced cushioning technology and breathable mesh design for ultimate comfort."
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
                "id": "sneaker-desc-001"
            }
        },
        "productType": "PHYSICAL",
        "physicalProperties": {},
        "media": {
            "main": {
                "url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop&crop=center",
                "altText": "Air Max Runner - Main Product Image"
            },
            "itemsInfo": {
                "items": [
                    {
                        "url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop&crop=center",
                        "altText": "Air Max Runner - Product View"
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
                "optionRenderType": "TEXT_CHOICES",
                "choicesSettings": {
                    "choices": [
                        {
                            "choiceType": "CHOICE_TEXT",
                            "name": "Black"
                        },
                        {
                            "choiceType": "CHOICE_TEXT",
                            "name": "White"
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
                                "renderType": "TEXT_CHOICES"
                            }
                        }
                    ],
                    "price": {
                        "actualPrice": {
                            "amount": "129.99"
                        }
                    },
                    "physicalProperties": {},
                    "visible": true
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
                                "renderType": "TEXT_CHOICES"
                            }
                        }
                    ],
                    "price": {
                        "actualPrice": {
                            "amount": "129.99"
                        }
                    },
                    "physicalProperties": {},
                    "visible": false
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
                                "renderType": "TEXT_CHOICES"
                            }
                        }
                    ],
                    "price": {
                        "actualPrice": {
                            "amount": "129.99"
                        }
                    },
                    "physicalProperties": {},
                    "visible": false
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
                                "renderType": "TEXT_CHOICES"
                            }
                        }
                    ],
                    "price": {
                        "actualPrice": {
                            "amount": "129.99"
                        }
                    },
                    "physicalProperties": {},
                    "visible": true
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
                                "renderType": "TEXT_CHOICES"
                            }
                        }
                    ],
                    "price": {
                        "actualPrice": {
                            "amount": "129.99"
                        }
                    },
                    "physicalProperties": {},
                    "visible": true
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
                                "choiceName": "White",
                                "renderType": "TEXT_CHOICES"
                            }
                        }
                    ],
                    "price": {
                        "actualPrice": {
                            "amount": "129.99"
                        }
                    },
                    "physicalProperties": {},
                    "visible": false
                }
            ]
        }
    }
}'
```

### IMPORTANT NOTES:

When Creating a product YOU MUST leave the physicalProperties and all other non required fields empty. for example: "physicalProperties": {}. In most cases the product will be a physical product, and therefore MUST have the empty physicalProperties object ("physicalProperties": {}) and a corresponding "productType": "PHYSICAL".

**CRITICAL: variantsInfo is Always Required**
`variantsInfo.variants` must contain at least one variant, even for simple products without options. Omitting it causes: `"variantsInfo must not be empty"`.

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

**CRITICAL: Media Format**
To add product images, use the `media` object with `main` for the primary image and `itemsInfo.items` for additional gallery images. **YOU MUST** add an image to each product.

> **Important:** The V3 Products API requires **URLs** for media, not media IDs. Even when using files from the Media Manager, you must use the full wixstatic.com URL.

**Option 1: Using External URLs Directly**

You can reference images directly from external URLs that allow hotlinking (e.g., Unsplash, Pexels):

```json
"media": {
    "main": {
        "url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
        "altText": "Product Main Image"
    },
    "itemsInfo": {
        "items": [
            {
                "url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
                "altText": "Product View"
            }
        ]
    }
}
```

> **Warning:** Some external URLs may fail if the source server blocks requests or has hotlink protection. For reliable media, use Option 2.

**Option 2: Using Media Manager (Recommended)**

For reliable, permanent media storage, first upload the image to the site's Media Manager, then use the returned wixstatic.com URL.

**Step 1:** Upload the image to Media Manager using the Import File API:

```bash
curl -X POST 'https://www.wixapis.com/site-media/v1/files/import' \
-H 'Content-Type: application/json' \
-H 'Authorization: <AUTH>' \
-d '{
    "url": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=400",
    "mimeType": "image/jpeg",
    "displayName": "Product Image"
}'
```

Response includes the wixstatic.com URL:

```json
{
    "file": {
        "id": "e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "url": "https://static.wixstatic.com/media/e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "operationStatus": "PENDING"
    }
}
```

> **Note:** Wait for `operationStatus` to become `READY` before using the media. You can verify by calling the List Files API (`GET /site-media/v1/files`).

**Step 2:** Use the wixstatic.com **URL** (not the ID) when creating the product:

```json
"media": {
    "main": {
        "url": "https://static.wixstatic.com/media/e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "altText": "Product Image"
    },
    "itemsInfo": {
        "items": [
            {
                "url": "https://static.wixstatic.com/media/e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
                "altText": "Product Image"
            }
        ]
    }
}
```

> **Why use Media Manager?** External URLs can fail if the source server blocks requests. Once uploaded to Media Manager, the file is permanently stored on Wix servers and the wixstatic.com URL is always reliable.

**CRITICAL: Options Structure**Each option MUST include:

* `optionRenderType`: "TEXT_CHOICES" for text-based choices
* `choicesSettings`: Object containing the choices array
* `choicesSettings.choices`: Array with at least one choice
* Each choice MUST have `choiceType`: "CHOICE_TEXT" and `name` properties

**CRITICAL: Variants Structure**

* Create one variant for EVERY combination of option choices (Cartesian product of all options)
* In this example: 2 colors and 3 sizes creates 6 variants (2 x 3) - all combinations must be included
* Each variant must reference ALL options defined on the product
* Use `optionChoiceNames` structure with `optionName`, `choiceName`, and `renderType`
* Price must use `price.actualPrice.amount` with string values
* Use `visible: true` for variants you want customers to see and purchase
* Use `visible: false` for variants that exist but should be hidden from customers

The Create Product API can handle creating customizations and choices in a single call. There's no need to separately check for existing customizations, create new ones, or add choices to them—the API handles all of this automatically:

1. If you provide an option with a name that doesn't exist as a customization, a new customization will be created
2. If a customization with that name already exists, it will be associated with the product
3. New choices will be added to the customization if they don't exist
4. When creating variants, use optionChoiceNames rather than optionChoiceIds to reference the options and choices
5. Always include the choicesSettings object with the complete list of choices
6. You must create one variant for each combination of option choices

### Next Steps:

After Creating the product, verify that the options appear correctly in the store and that customers can select different variants.

> **Need to Update This Product Later?**
>
> See [Update Product with Options](update-product-with-options.md) for updating existing products.
>
> **Important:** All update operations (PATCH) require the current `product.revision` value. Always GET the product first to obtain the revision before updating.

## Troubleshooting Common Issues

### Issue 1: "ChoicesSettings must not be empty" error

* **Problem**: When creating a product with options, you get an error saying `choicesSettings must not be empty`. This can appear in several forms:
   * `"product is invalid: options [at index 0] is invalid: value choicesSettings must not be empty"`
   * `"product is invalid: options [at index 0] is invalid: value choicesSettings must not be empty"` with `"violatedRule":"REQUIRED_ONE_OF_FIELD"`
   * `"choicesSettings must not be empty"` with field violations showing `"supported":["choicesSettings"]`
* **Solution**: Always include the `choicesSettings` object with the full array of `choices` when creating a product with options. Every option MUST have a complete choicesSettings structure with at least one choice, even when using an existing customization.

**Common Causes:**

1. **Missing choicesSettings entirely** - The option object doesn't include any choicesSettings
2. **Empty choicesSettings object** - The choicesSettings exists but has no choices array or empty choices array
3. **Null or undefined choicesSettings** - The choicesSettings field is present but set to null/undefined

**Example of correct choicesSettings structure:**

```json
"options": [
    {
        "name": "Size",
        "optionRenderType": "TEXT_CHOICES",
        "choicesSettings": {
            "choices": [
                {
                    "choiceType": "CHOICE_TEXT",
                    "name": "Small"
                }
            ]
        }
    }
]
```

**What NOT to do:**

```json
// WRONG - Missing choicesSettings entirely
"options": [
    {
        "name": "Size",
        "optionRenderType": "TEXT_CHOICES"
    }
]

// WRONG - Empty choicesSettings
"options": [
    {
        "name": "Size",
        "optionRenderType": "TEXT_CHOICES",
        "choicesSettings": {}
    }
]

// WRONG - Empty choices array
"options": [
    {
        "name": "Size",
        "optionRenderType": "TEXT_CHOICES",
        "choicesSettings": {
            "choices": []
        }
    }
]
```

### Issue 2: "optionSettings.choicesSettings.choices must not be empty" error

* **Problem**: You get an error like `"product is invalid: options [at index 0] is invalid: optionSettings.choicesSettings is invalid: choices has size 0, expected 1 or more"` or `"choices must not be empty"`.
* **Solution**: This error occurs when using the incorrect nested structure `optionSettings.choicesSettings` instead of the correct `choicesSettings` directly under the option.

**WRONG Structure (causes the error):**

```json
"options": [
    {
        "name": "Size",
        "optionRenderType": "TEXT_CHOICES",
        "optionSettings": {
            "choicesSettings": {
                "choices": []
            }
        }
    }
]
```

**CORRECT Structure (use this instead):**

```json
"options": [
    {
        "name": "Size",
        "optionRenderType": "TEXT_CHOICES",
        "choicesSettings": {
            "choices": [
                {
                    "choiceType": "CHOICE_TEXT",
                    "name": "Small"
                }
            ]
        }
    }
]
```

**Key Points:**

* Use `choicesSettings` directly under the option object, NOT nested under `optionSettings`
* The `choicesSettings.choices` array MUST contain at least one choice
* Each choice MUST have `choiceType` and `name` properties
* Always include the complete choices array even when referencing existing customizations

### Issue 3: Variants not matching options

* **Problem**: The API returns errors about variants not matching the product's options.
* **Solution**:
* Create one variant for each possible combination of option choices
* Ensure each variant references all options defined on the product
* If the product has only one option with three choices, you need three variants
* Make sure each variant's option choice name exactly matches the corresponding option choice

### Issue 4: Conflicts when using existing customizations

* **Problem**: When attempting to use existing customizations, you encounter name conflicts or choice conflicts.
* **Solution**:
* If you need to use a specific existing customization ID, first query customizations to get the correct ID
* When working with existing customizations, ensure all choices you reference actually exist in that customization
* If you're creating a new customization with the same name as an existing one, the API will use the existing one
* Be aware that customizations are shared across all products in your store

### Issue 5: "Expected an object" error for description

* **Problem**: Using a plain string for the description field causes API failure.
* **Solution**: Always use the rich text nodes structure for descriptions as shown in the CRITICAL section above.

### Issue 6: Inconsistencies in documentation vs. actual API behavior

* **Problem**: Several API requirements are not well-documented or are documented differently from how the API actually behaves.
* **Solution**:
* Always include choicesSettings with all choices when creating a product
* Use optionChoiceNames rather than optionChoiceIds in variants for more reliable results
* Include the renderType in optionChoiceNames
* Use the exact same choice names as defined in the customization

## Conclusion

Creating a Wix store product with options involves understanding the relationship between store-wide customizations and product-specific options and variants. The key is to ensure consistency between customization definitions, product options, and product variants.

By following this recipe and being aware of the common pitfalls, you can successfully create a Wix store product with options.
