---
name: "Create Product from Image"
description: "MANDATORY entry point for creating a product from an image. STEP 1 detects the site's catalog version (V1 / V3) automatically, then runs the appropriate flow inline. V3 supports up to 3 images, info sections, SEO, and options; V1 supports a single image. Use this for any 'create product from image' or 'create product from photo' request."
---
# RECIPE: Create Product from Image

> **ALWAYS use this recipe as the entry point** when the user wants to create a product from one or more images. Do NOT skip STEP 1 (version detection) — even if you believe you know the catalog version from dynamic context.
>
> **CRITICAL — IMAGE DESCRIPTION FIRST:** In your VERY FIRST response after seeing a product image, you MUST write a detailed text description of what you see in the image (product type, colors, materials, shape, branding). Output this description as text alongside your first tool call. This description will persist in conversation context and is the ONLY source of truth for product details in later steps. Do NOT attempt to re-analyze the image later — use the description you wrote here.

This recipe creates a Wix Store product from an image. It first detects the site's catalog version, then runs the appropriate flow:

- **V3 flow:** 6 interactive steps. Up to 3 images, multi-image variant detection, info sections (materials, care, specs), SEO meta, options/variants, atomic single-call create.
- **V1 flow:** 3 sequential steps. Single image, product details inferred from the image, separate media-attach call after create.

**Prerequisites:**
- The user MUST provide at least one product image — uploaded directly to the chat or as a publicly accessible URL.
- Up to 3 images are supported (V3 only — V1 supports only 1 image).

---

## STEP 1: Detect Catalog Version (no user interaction)

**API Endpoint:** `GET https://www.wixapis.com/stores/v3/provision/version`

No request body — this is a GET request.

**Expected response:**

```json
{
    "catalogVersion": "V3_CATALOG"
}
```

Possible values for `catalogVersion`:

| Value | Action |
|-------|--------|
| `V3_CATALOG` | Run the **V3 Flow** below (V3 STEP 2 through V3 STEP 6) |
| `V1_CATALOG` | Run the **V1 Flow** below (V1 STEP 2 through V1 STEP 4) |
| `STORES_NOT_INSTALLED` | Stop. Inform the user: "The Wix Stores app is not installed on this site. Please install Wix Stores first before creating products. You can install it using the [Install Wix Apps](https://dev.wix.com/docs/api-reference/business-management/app-installation/skills/install-wix-apps) recipe." |

---

# V3 Flow (catalogVersion = `V3_CATALOG`)

> Run this section ONLY if STEP 1 returned `V3_CATALOG`. Otherwise jump to the V1 Flow further below.

This is an interactive 5-step flow (STEP 2 through STEP 6). V3 STEP 4 and V3 STEP 5 require user interaction — do NOT skip them.

---

## V3 STEP 2: Collect Images and Upload to Wix Media Manager

Ask the user to provide **1 to 3 images** of their product:

> Upload 1-3 images of your product. If your product comes in different colors or sizes, feel free to upload images of those variants — I'll use them to set up product options automatically.
>
> You can upload images directly or provide public URLs.

**Rules:**
- Accept uploaded files (any image the user sends in the chat) OR publicly accessible URLs (`https://`).
- Minimum: 1 image. Maximum: 3 images.
- Supported formats: JPG, PNG, WEBP.
- All images must be of the **same product**. If the images appear to show completely different products, respond: "It looks like these images show different products. For now, I can create one product at a time. Please upload images of a single product."
- If an image is blurry or unrecognizable, respond: "I wasn't able to identify a product in this image. Try a clearer photo or add a description."

**Optional free-text:** The user may include a text note with context (e.g., "handmade ceramic mug, usually around $25, available in blue and green"). Use this to supplement the image analysis.

**Immediately upload each image** to the Wix Media Manager to get permanent public URLs:

**API Endpoint:** `POST https://www.wixapis.com/site-media/v1/files/import`

**For each image, send:**

```json
{
    "url": "<image_url>",
    "mimeType": "image/jpeg",
    "displayName": "product-image-1.jpg"
}
```

**Expected response:**

```json
{
    "file": {
        "id": "e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "displayName": "product-image-1.jpg",
        "url": "https://static.wixstatic.com/media/e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "parentFolderId": "media-root",
        "mediaType": "IMAGE",
        "operationStatus": "PENDING"
    }
}
```

**After uploading, save the `file.url` (wixstatic.com URL) for each image.** You need these in V3 STEP 3 and V3 STEP 6.

**Fallback:** If the upload fails (e.g., the source URL is not publicly accessible, or `operationStatus: "FAILED"`), ask the user: "I couldn't upload that image. Could you provide a publicly accessible URL for it (e.g., from Unsplash, Imgur, or any https:// link)?"

**Media assignment:**
- The **first** successfully uploaded image becomes `media.main`.
- **All** images go into `media.itemsInfo.items[]`.

---

## V3 STEP 3: Analyze Images and Generate Product Details

**Use the image description you wrote at the start of this conversation** (in your first response, per the CRITICAL instruction at the top of this recipe). That description is the source of truth for all product fields. Do NOT attempt to re-analyze the image — use the text description already in context.

**Use ONLY details from your earlier image description to generate the fields below.** Do NOT use generic names like "Product" or hallucinate new details. If you did not write an image description earlier, ask the user for clarification instead of guessing.

**Generate the following fields based on what you see in the image(s)** (and any free-text note from the user):

### 4a. Product Name
A concise, appealing product name optimized for e-commerce discoverability. Maximum 80 characters. Follow the naming convention: `[Brand/Style] [Material] [Product Type]`.

Example: `"Artisan Stoneware Ceramic Mug"` — not generic names like `"Mug"` or `"Product"`.

### 4b. Sample Existing Product Tone (silent — no user interaction)

Before writing the description, check whether the site already has products to match their tone:

**API Endpoint:** `POST https://www.wixapis.com/stores/v3/products/query`

```json
{
    "query": {
        "paging": {
            "limit": 2
        }
    }
}
```

- If the response contains products with non-empty `description` fields, analyze their writing style (casual, professional, playful, luxury, technical, etc.) and note it as the **site tone**.
- If no products exist or descriptions are empty, use a neutral e-commerce tone.
- This query is best-effort — if it fails, proceed with neutral tone. Do NOT block the flow.

### 4c. Product Description
A marketing description of 2-4 sentences. Highlight key features, materials, and use case. **Match the site tone detected in 4b** — if the existing products use casual language, write casually; if they use formal/luxury language, match that style. If no site tone was detected, adapt tone to the product type (artisanal for handmade, technical for electronics, warm for home goods). This will be formatted as rich text nodes in V3 STEP 7.

### 4d. Price with Market Range
- Suggest a retail price based on the product type and industry averages.
- Also determine an approximate **market range** for annotation (e.g., "avg. market: $28-$42"). This range is shown to the user in V3 STEP 5 but is NOT sent to the API.

### 4e. Info Sections (only if relevant)
Based on the product type and what's visible in the image, generate category-specific info sections. **Only include sections that are relevant — omit entirely if not applicable.**

| Product Category | Possible Info Sections |
|-----------------|----------------------|
| Clothing/Textiles | "Materials & Composition" (e.g., "100% Organic Cotton"), "Care Instructions" (e.g., "Machine wash cold, tumble dry low") |
| Candles/Fragrance | "Burn Time & Care" (e.g., "Approx. 45 hours burn time. Trim wick to 1/4 inch before each use.") |
| Furniture/Home | "Dimensions & Specs" (e.g., "Height: 30cm, Width: 15cm"), "Assembly" if applicable |
| Electronics | "Technical Specifications", "What's Included" |
| Food/Beverages | "Ingredients", "Nutritional Info", "Storage Instructions" |
| Jewelry | "Materials" (e.g., "Sterling Silver 925"), "Sizing Guide" |
| Skincare/Beauty | "Ingredients", "How to Use" |

Each info section needs: a `uniqueName` (lowercase-hyphenated, e.g., `"care-instructions"`), a `title` (display name, e.g., `"Care Instructions"`), and a description (2-3 sentences).

### 4f. SEO Meta Description
A short meta description (120-160 characters) optimized for search. Include the product type, key materials, and primary use case.

Example: `"Handcrafted stoneware ceramic mug with a matte glaze finish. Perfect for coffee and tea lovers. Microwave and dishwasher safe."`

### 4g. Suggested Options (from images)
Examine the images for visible product attributes that should become variant options.

**CRITICAL: Do NOT invent or infer attributes.** Only suggest options that meet **one** of these evidence thresholds:
- **Visually confirmed** in the image(s) — you can see distinct values (e.g., two different colors across two images, a size label printed on packaging)
- **Explicitly stated** by the user in their text note (e.g., "available in blue and green", "comes in S, M, L")

**Do NOT suggest standard industry options based on product category.** For example, do NOT suggest Size: S, M, L, XL, XXL for apparel just because it is a clothing item. If no size information is visible in the image and the user did not mention sizes, report no size options detected.

**Negative example:** Image shows a single t-shirt with no size labels visible and the user did not mention sizes → do NOT suggest a Size option. Report: "No variant options detected from the image."

**Multi-image variant detection:**
- If multiple images show the **same product in different colors** (e.g., one red shirt, one blue shirt), suggest a Color option with **only those visible colors** as choices.
- If multiple images show the **same product from different angles**, treat them as additional product media — NOT as separate variants.
- If only one image is provided and a distinctive color is visible, suggest that single color as a choice and ask the user if the product comes in other colors.

---

## V3 STEP 4: Present Review Card to User (INTERACTIVE)

**You MUST present ALL generated fields to the user and ask for confirmation before proceeding.**

Present a structured review card using the markdown format below. This provides a visual product-card-style layout:

```
---

### [Product Name]

**$[price]** · _avg. market: $[low]-$[high]_

> [Generated description text — the full 2-4 sentence description]

---

| Detail | Value |
|--------|-------|
| Images | [count] uploaded |
| SEO | [first 60 chars of meta description]… |
| Tone | [Matched from existing site products / Neutral e-commerce] |

**Info Sections**
- **[Title 1]:** [one-line summary]
- **[Title 2]:** [one-line summary]

**Detected Options:** [option summary, e.g. "Color: Slate Blue, Terracotta" or "None detected"]

---
```

After the card, present the action options:

> 1. **Refine** — tell me what to change (e.g., "make the description shorter", "the price should be lower")
> 2. **Regenerate** — I'll start the analysis over, optionally with additional context from you
> 3. **Approve** — proceed to options and product creation

If the user provided a text note that **contradicts** what's visible in the image (e.g., image shows blue but note says "available in red"), ask the user to clarify before proceeding.

**Wait for user confirmation.** Apply any corrections they request. Do NOT proceed until approved.

---

## V3 STEP 5: Suggest Options and Ask User (INTERACTIVE)

**Present the detected options from V3 STEP 4g and ask the user if they want to add product options.**

If options were detected:

> **Based on your image(s), I suggest the following product options:**
>
> - **[Option Name]:** [Choice 1], [Choice 2], ...
>
> Would you like to:
> 1. Use these options as suggested
> 2. Add more choices (e.g., additional colors or sizes)
> 3. Add entirely new options
> 4. Skip options and create a simple product (no variants)

If no options were detected:

> I didn't detect any variant attributes from the image(s). Would you like to add product options, or should I create a simple product without variants?

**Wait for user response.** Collect the final list of options and choices based on their answer.

---

## V3 STEP 6: Create the Product

**API Endpoint:** `POST https://www.wixapis.com/stores/v3/products`

Build the request body with all confirmed fields. The write must be **atomic** — either all fields save or none do.

---

### Path A: Simple Product (No Options)

Use this if the user chose to skip options in V3 STEP 6.

**Exact request example:**

```json
{
    "product": {
        "name": "Artisan Stoneware Ceramic Mug",
        "description": {
            "nodes": [
                {
                    "type": "PARAGRAPH",
                    "id": "desc1",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {
                                "text": "A beautifully handcrafted stoneware mug with a smooth matte glaze. Its generous 12oz capacity and comfortable handle make it perfect for your morning coffee or evening tea. Microwave and dishwasher safe."
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
                "id": "product-desc-001"
            }
        },
        "productType": "PHYSICAL",
        "physicalProperties": {},
        "media": {
            "main": {
                "url": "https://static.wixstatic.com/media/e6a89e_abc123~mv2.jpg",
                "altText": "Artisan Stoneware Ceramic Mug - Front View"
            },
            "itemsInfo": {
                "items": [
                    {
                        "url": "https://static.wixstatic.com/media/e6a89e_abc123~mv2.jpg",
                        "altText": "Artisan Stoneware Ceramic Mug - Front View"
                    },
                    {
                        "url": "https://static.wixstatic.com/media/e6a89e_def456~mv2.jpg",
                        "altText": "Artisan Stoneware Ceramic Mug - Side View"
                    }
                ]
            }
        },
        "infoSections": [
            {
                "uniqueName": "materials-composition",
                "title": "Materials & Composition",
                "description": {
                    "nodes": [
                        {
                            "type": "PARAGRAPH",
                            "id": "info-materials-1",
                            "nodes": [
                                {
                                    "type": "TEXT",
                                    "textData": {
                                        "text": "Made from high-fired stoneware clay with a food-safe matte glaze finish. Lead-free and cadmium-free."
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
                        "id": "info-materials"
                    }
                }
            },
            {
                "uniqueName": "care-instructions",
                "title": "Care Instructions",
                "description": {
                    "nodes": [
                        {
                            "type": "PARAGRAPH",
                            "id": "info-care-1",
                            "nodes": [
                                {
                                    "type": "TEXT",
                                    "textData": {
                                        "text": "Microwave and dishwasher safe. Hand washing recommended to preserve the glaze finish. Avoid sudden temperature changes."
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
                        "id": "info-care"
                    }
                }
            }
        ],
        "seoData": {
            "tags": [
                {
                    "type": "meta",
                    "props": {
                        "name": "description",
                        "content": "Handcrafted stoneware ceramic mug with matte glaze finish. 12oz capacity, microwave and dishwasher safe. Perfect for coffee and tea lovers."
                    }
                }
            ]
        },
        "price": {
            "actualPrice": {
                "amount": "34.99"
            }
        }
    }
}
```

---

### Path B: Product with Options

Use this if the user confirmed or provided options in V3 STEP 6. You MUST define both `options` and `variantsInfo.variants`.

**Rules for variants:**
- Generate ALL combinations of option choices as variants.
- Each variant uses the same price unless the user specified different prices.
- Set `visible: true` for all variants.

**Exact request example (product with Color option detected from two images):**

```json
{
    "product": {
        "name": "Artisan Stoneware Ceramic Mug",
        "description": {
            "nodes": [
                {
                    "type": "PARAGRAPH",
                    "id": "desc1",
                    "nodes": [
                        {
                            "type": "TEXT",
                            "textData": {
                                "text": "A beautifully handcrafted stoneware mug with a smooth matte glaze. Its generous 12oz capacity and comfortable handle make it perfect for your morning coffee or evening tea. Microwave and dishwasher safe."
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
                "id": "product-desc-001"
            }
        },
        "productType": "PHYSICAL",
        "physicalProperties": {},
        "media": {
            "main": {
                "url": "https://static.wixstatic.com/media/e6a89e_abc123~mv2.jpg",
                "altText": "Artisan Stoneware Ceramic Mug - Slate Blue"
            },
            "itemsInfo": {
                "items": [
                    {
                        "url": "https://static.wixstatic.com/media/e6a89e_abc123~mv2.jpg",
                        "altText": "Artisan Stoneware Ceramic Mug - Slate Blue"
                    },
                    {
                        "url": "https://static.wixstatic.com/media/e6a89e_def456~mv2.jpg",
                        "altText": "Artisan Stoneware Ceramic Mug - Terracotta"
                    }
                ]
            }
        },
        "options": [
            {
                "name": "Color",
                "optionRenderType": "TEXT_CHOICES",
                "choicesSettings": {
                    "choices": [
                        {
                            "choiceType": "CHOICE_TEXT",
                            "name": "Slate Blue"
                        },
                        {
                            "choiceType": "CHOICE_TEXT",
                            "name": "Terracotta"
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
                                "choiceName": "Slate Blue",
                                "renderType": "TEXT_CHOICES"
                            }
                        }
                    ],
                    "price": {
                        "actualPrice": {
                            "amount": "34.99"
                        }
                    },
                    "physicalProperties": {},
                    "visible": true
                },
                {
                    "choices": [
                        {
                            "optionChoiceNames": {
                                "optionName": "Color",
                                "choiceName": "Terracotta",
                                "renderType": "TEXT_CHOICES"
                            }
                        }
                    ],
                    "price": {
                        "actualPrice": {
                            "amount": "34.99"
                        }
                    },
                    "physicalProperties": {},
                    "visible": true
                }
            ]
        },
        "infoSections": [
            {
                "uniqueName": "materials-composition",
                "title": "Materials & Composition",
                "description": {
                    "nodes": [
                        {
                            "type": "PARAGRAPH",
                            "id": "info-materials-1",
                            "nodes": [
                                {
                                    "type": "TEXT",
                                    "textData": {
                                        "text": "Made from high-fired stoneware clay with a food-safe matte glaze finish. Lead-free and cadmium-free."
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
                        "id": "info-materials"
                    }
                }
            },
            {
                "uniqueName": "care-instructions",
                "title": "Care Instructions",
                "description": {
                    "nodes": [
                        {
                            "type": "PARAGRAPH",
                            "id": "info-care-1",
                            "nodes": [
                                {
                                    "type": "TEXT",
                                    "textData": {
                                        "text": "Microwave and dishwasher safe. Hand washing recommended to preserve the glaze finish. Avoid sudden temperature changes."
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
                        "id": "info-care"
                    }
                }
            }
        ],
        "seoData": {
            "tags": [
                {
                    "type": "meta",
                    "props": {
                        "name": "description",
                        "content": "Handcrafted stoneware ceramic mug with matte glaze finish. 12oz capacity, microwave and dishwasher safe. Perfect for coffee and tea lovers."
                    }
                }
            ]
        },
        "price": {
            "actualPrice": {
                "amount": "34.99"
            }
        }
    }
}
```

---

**Expected response (partial):**

```json
{
    "product": {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "name": "Artisan Stoneware Ceramic Mug",
        "visible": true,
        "productType": "PHYSICAL",
        "price": {
            "actualPrice": {
                "amount": "34.99"
            }
        }
    }
}
```

**On success:** Present a completion card summarizing what was created:

```
---

### Product Created

**[Product Name]** · **$[price]**

| | |
|---|---|
| Options | [option summary or "None"] |
| Info Sections | [list of section titles] |
| Images | [count] attached |

**View in dashboard:** `https://manage.wix.com/dashboard/[siteId]/store/products/[productId]`

---
```

Replace `[siteId]` with the site ID from the MCP context and `[productId]` with the `product.id` from the API response. This link lets the user immediately view and edit the product in the Wix dashboard.

**On failure:** Show an error message and offer to retry. Do NOT leave a partially created product.

---

## V3 Completion Checklist

Before reporting success to the user, verify ALL of the following:

- [ ] STEP 1 completed: Catalog version detected as `V3_CATALOG`.
- [ ] V3 STEP 2 completed: User provided 1-3 images, all uploaded to Media Manager with wixstatic.com URLs.
- [ ] V3 STEP 3 completed: Images analyzed from user's message, all product fields generated based on what's visible in the image(s).
- [ ] V3 STEP 4 completed: User reviewed and approved the generated details.
- [ ] V3 STEP 5 completed: User confirmed, modified, or skipped product options.
- [ ] V3 STEP 6 completed: Product was created via API and you received a product ID.

---

# V1 Flow (catalogVersion = `V1_CATALOG`)

> Run this section ONLY if STEP 1 returned `V1_CATALOG`. Otherwise use the V3 Flow above.

This is a 3-step sequential flow (STEP 2 through STEP 4). ALL steps MUST be completed in order. Do NOT report success until ALL steps have executed successfully.

**V1 prerequisites:**
- The user MUST provide at least one product image — uploaded directly to the chat or as a publicly accessible URL.
- Both chat uploads and public URLs are accepted. Chat-uploaded images have a wixmp URL that works for Media Manager import.

---

## V1 STEP 2: Upload the Image to Wix Media Manager (MANDATORY)

**API Endpoint:** `POST https://www.wixapis.com/site-media/v1/files/import`

**Request body fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | The image URL. Can be a publicly accessible HTTP/HTTPS URL OR a wixmp URL from a chat-uploaded image. Both work with the Media Manager import API. |
| `mimeType` | string | Recommended | The MIME type of the image. Use `image/jpeg` for .jpg/.jpeg files, `image/png` for .png files, `image/webp` for .webp files. |
| `displayName` | string | No | A display name for the file in Media Manager. Include the file extension (e.g., `product-image.jpg`). |

**Exact request example:**

```json
{
    "url": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=400",
    "mimeType": "image/jpeg",
    "displayName": "product-image.jpg"
}
```

**Expected response:**

```json
{
    "file": {
        "id": "e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "displayName": "product-image.jpg",
        "url": "https://static.wixstatic.com/media/e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg",
        "parentFolderId": "media-root",
        "mediaType": "IMAGE",
        "operationStatus": "PENDING"
    }
}
```

**After this step, save these values — you need them later:**
- `file.url` — the wixstatic.com URL (use in V1 STEP 4)
- `file.id` — the media file ID

**If the response contains `operationStatus: "FAILED"`:** The source URL is not accessible. Ask the user for a different image URL.

---

## V1 STEP 3: Create the Product (with image-based details)

**API Endpoint:** `POST https://www.wixapis.com/stores/v1/products`

**Use the image description you wrote at the start of this conversation** (in your first response, per the CRITICAL instruction at the top of this recipe). That description is the source of truth for the product name, description, and price. Do NOT attempt to re-analyze the image — use the text description already in context.

**Use ONLY details from your earlier image description to set the product name, description, and price below.** Do NOT use generic text like "Product from image" or hallucinate new details. If you did not write an image description earlier, ask the user for clarification instead of guessing.

**Request body fields:**

| Field | Type | Required | Value |
|-------|------|----------|-------|
| `product.name` | string | Yes | A concise, appealing name describing the ACTUAL product in the image (max 80 chars). Example: `"Premium Spinning Fishing Reel"` — NOT `"Product from image"`. |
| `product.description` | string | Yes | A 2-3 sentence marketing description of what you SEE in the image. MUST be wrapped in `<p>` tags. |
| `product.visible` | boolean | Yes | `true` |
| `product.productType` | string | Yes | `"physical"` |
| `product.priceData.price` | number | Yes | A reasonable retail price based on the product type visible in the image |

**Exact request example (using values from V1 STEP 3):**

```json
{
  "product": {
    "name": "Premium Spinning Fishing Reel",
    "description": "<p>A sleek black-and-gold spinning fishing reel designed for smooth retrieves and dependable performance. Ideal for anglers targeting freshwater or light saltwater species.</p>",
    "visible": true,
    "productType": "physical",
    "priceData": {
      "price": 79.99
    }
  }
}
```

**Expected response (partial):**

```json
{
  "product": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Premium Spinning Fishing Reel",
    "visible": true,
    "productType": "physical",
    "priceData": {
      "price": 79.99
    }
  }
}
```

**After this step, save this value — you need it in V1 STEP 4:**
- `product.id` — the product ID (a UUID string like `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`)

---

## V1 STEP 4: Attach the Image to the Product (MANDATORY — DO NOT SKIP)

**API Endpoint:** `POST https://www.wixapis.com/stores/v1/products/{id}/media`

Replace `{id}` in the URL with the `product.id` from V1 STEP 4.

**Request body fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `media` | array | Yes | Array of media objects to attach |
| `media[].url` | string | Yes | The `file.url` (wixstatic.com URL) from V1 STEP 2. Do NOT use the original image URL — use the wixstatic.com URL returned by the Media Manager. |

**Exact request example:**

URL: `POST https://www.wixapis.com/stores/v1/products/a1b2c3d4-e5f6-7890-abcd-ef1234567890/media`

```json
{
  "media": [
    {
      "url": "https://static.wixstatic.com/media/e6a89e_19dae9fef9bb48a6b5e392d0d2e5b95d~mv2.jpg"
    }
  ]
}
```

**Expected response:** Empty object `{}` — this means success.

**This step is MANDATORY.** The product is not complete without its image. Do NOT report success to the user before this step returns successfully.

---

## V1 Completion Checklist

Before reporting success to the user, verify ALL of the following:

- [ ] STEP 1 completed: Catalog version detected as `V1_CATALOG`.
- [ ] V1 STEP 2 completed: Image was uploaded to Wix Media Manager and you received a wixstatic.com URL.
- [ ] V1 STEP 3 completed: You looked at the image, identified the product, and created it with accurate name/description/price.
- [ ] V1 STEP 4 completed: Image was attached to the product using the Add Product Media endpoint.

Only after ALL 4 steps succeed (STEP 1 + V1 STEP 2-4), report to the user: the product name, price, and that it was created with the image attached.

---

# Troubleshooting and Error Handling

## Catalog version detection issues

### Get Catalog Version returns 404 or authorization error
The API key may not have permission to access Stores APIs, or Stores may not be installed. Verify Stores is installed and the auth token has the correct scopes.

### Unsure which flow to run
The response field is `catalogVersion`. Map it as follows:
- `V3_CATALOG` -> run V3 Flow (V3 STEP 2 onward)
- `V1_CATALOG` -> run V1 Flow (V1 STEP 2 onward)
- `STORES_NOT_INSTALLED` -> stop and ask user to install Wix Stores

## V3 issues

### Image is blurry or unrecognizable
Respond: "I wasn't able to identify a product in this image. Try a clearer photo or add a description."

### Images show different products
Respond: "It looks like these images show different products. For now, I can create one product at a time. Please upload images of a single product."

### User text contradicts images
If the user's free-text note conflicts with what's visible (e.g., image shows blue but note says "available in red"), ask the user to clarify before showing the review card.

### Description format error (V3)
V3 requires rich text nodes, NOT HTML strings. Ensure the description is an object with `nodes` array.

### Variant count mismatch
You must generate ALL combinations of option choices. For example, 2 colors x 2 sizes = 4 variants.

### V3 API write fails
Show an error and offer to retry. Do NOT leave a partially created product.

## V1 issues

### "The url field must be a publicly accessible URL"
The URL may be a local file path or invalid reference. Both public HTTPS URLs and wixmp URLs from chat uploads work. If the error persists, ask the user for a different image source.

### Product created but no image visible (V1)
You used the original external URL instead of the wixstatic.com URL in V1 STEP 4. Always use the `file.url` from V1 STEP 2's response.

## Cross-version errors

### Image import fails (operationStatus: FAILED)
The source server blocks external requests. Ask the user for a different image URL. Reliable sources: Unsplash (`images.unsplash.com`), Pexels (`images.pexels.com`), Imgur, public S3/GCS buckets.

### 428 Precondition Required on product creation
You called the wrong endpoint for the site's catalog version. Re-run STEP 1 to detect the version and use the matching flow:
- V3 sites must use `POST /stores/v3/products` (V3 STEP 6)
- V1 sites must use `POST /stores/v1/products` (V1 STEP 4)

# References

- [Get Catalog Version](https://dev.wix.com/docs/rest/business-solutions/stores/catalog-versioning/get-catalog-version)
- [Catalog Versioning Overview](https://dev.wix.com/docs/rest/business-solutions/stores/catalog-versioning/introduction)
- [Create Product (Catalog V3)](https://dev.wix.com/docs/rest/business-solutions/stores/catalog-v3/products-v3/create-product)
- [Create Product with Options (Catalog V3)](https://dev.wix.com/docs/api-reference/business-solutions/stores/skills/create-product-with-options-catalog-v3)
- [Info Sections API (Catalog V3)](https://dev.wix.com/docs/rest/business-solutions/stores/catalog-v3/info-sections-v3/introduction)
- [Create Product (Catalog V1)](https://dev.wix.com/docs/api-reference/business-solutions/stores/skills/create-product-catalog-v1)
- [Add Product Media (Catalog V1)](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v1/catalog/add-product-media)
- [Upload Media to Wix](https://dev.wix.com/docs/api-reference/assets/media/skills/upload-media-to-wix)
- [Install Wix Apps](https://dev.wix.com/docs/api-reference/business-management/app-installation/skills/install-wix-apps)