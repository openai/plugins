---
name: "Setup Online Store (Catalog V3)"
description: Initializes a Stores catalog with Catalog V3 Products API, bulk products endpoint, and Categories API. Covers product creation, option configuration, variant management, and category assignment.
---
**RECIPE**: Business Recipe – Initial Setup for a Wix Online Store (Catalog V3)

> **Standard call shape (every curl below).** The `<AUTH>` placeholder is shorthand for `Authorization: Bearer <TOKEN>` only. Every actual call ALSO needs `wix-site-id: <SITE_ID>` and (for body-bearing requests) `Content-Type: application/json`. **POST/PATCH against `stores/v3/*` and `categories/v1/*` returns 403 without `wix-site-id`** — recipe examples below show `<AUTH>` only for brevity, but the header is required on every call you make. Token: `npx @wix/cli@latest token --site "$SITE_ID"`.

A concise checklist for preparing any new Wix site that uses the Online Stores app with Catalog V3.
**Notice** that this recipe is **NOT** meant for coding purposes and is **ONLY** meant for initial catalog setup.

---

## Article: Steps for Setting Up a Wix Online Store
**YOU MUST** Complete all the following steps **in the given order** (1 -5) without skipping any and **without requiring additional user input**.
**YOU MUST** remind yourself as many times as needed throughout the process that you most complete all the steps and not stop at all in the middle.


**⚠️ CRITICAL ORDER REQUIREMENT: You MUST start with creating products FIRST (Steps 1-2), then categories (Steps 3-5). Categories API might take some time to be fully available after Stores installation, so always create products before attempting category operations.**

### STEP 1: Confirm Catalog V3 & Stick to V3 APIs

- **Check if the site uses Catalog V3.**
 This can be done using the [Get Catalog Version](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-versioning/get-catalog-version) endpoint.
 path: `https://www.wixapis.com/stores/v3/provision/version`


- From this point forward, as long as the result is V3, use only Catalog V3 REST endpoints.
All API calls should be directed to endpoints starting with `/stores/v3/....` Do not mix V3 calls with earlier versions.


- Exception for Categories:
The Categories API is an exception. It uses a v1 endpoint, as it replaces the older Collections API. For example, to create a category in V3, use the following endpoint:
`https://www.wixapis.com/categories/v1/categories`


### STEP 2: Create 5 new products based on the format specified in the Bulk Create Products with Options recipe (4 in stock, 1 out of stock)
1. First *YOU MUST* pull up the [Bulk Create Wix Store Products with Options](bulk-create-products-with-options.md) recipe to understand the exact format required for creating products.
2. Create 5 products according to this format using bulk creation (use a single bulk request). 4 of the created products **MUST** have ALL there variants in-stock, and the last (5th) product **MUST** have all its variants be out-of-stock.
3. **Make sure** to add in image (using media) using  a url from the web that matches each product.
4. **YOU MUST** use the price formatting as seen in the example, meaning using actualPrice and compareAtPrice.
5. **ALL** products **MUST** be created **EXACTLY** from the same format as the full example in the Bulk Create Wix Store Products with Options recipe. **ONLY** information within the strings of the given fields may differ based on the products.


**⚠️ CRITICAL: EXACT FORMAT REQUIREMENTS**
**YOU MUST** use the following recipe to create ALL products with the EXACT same format:
- **Bulk Create Wix Store Products with Options**
 [Recipe: Bulk Create Products with Options](bulk-create-products-with-options.md)


### STEP 3: Prepare Three Store Categories
1. Determine how many categories the user requested.
2. If fewer than **3** are provided, create additional categories until the total equals **3** which are relevant for the type of store.
3. Examples for different types of stores:
  - **Book store** → Drama, Kids, Sci-Fi
  - **Fashion** → Men, Women, Kids
  - **Other industries** → any logical grouping that fits the catalog.
4. Use the Categories API to create each category. **YOU MUST USE** the endpoint: [Create Category](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/categories/create-category) based on the example below. Endpoint path: `POST https://www.wixapis.com/categories/v1/categories`. **There is no bulk-create endpoint for `/categories/v1/`** (the `events/v1/bulk/categories/create` URL is for the Events product, not Stores).
5. **Fire all N category-create calls as a single concurrent batch.** Each call is independent (creates a different category), so issue them as siblings in one assistant message — do not serialize. For 3 categories this saves ~6–8 s of wall vs. sequential calls.

When calling the endpoint, make sure the request body includes a top-level `treeReference` field. It must **not** be nested inside the `category` object.

Use the following example format:

```json
{
  "category": {
    "name": "Drinkware",
    "description": "The Drinkware category includes a wide range of containers designed for holding beverages",
    "visible": true
  },
  "treeReference": {
    "appNamespace": "@wix/stores",
    "treeKey": null
  }
}
```


### STEP 4: Add Each Product to a Category
1. **YOU MUST** add each existing product to at least one category that most makes sense.
2. First acquire the product's ids to use for this action.
3. Then adding a product to a category **MUST** be done using the Category API, specifically [Bulk Add Items To Category](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/categories/bulk-add-items-to-category), where products are referred to as items. This endpoint enables adding multiple products at once to a category.
4. **Fire all N add-items calls as a single concurrent batch.** Each call targets a different `categoryId` (the path parameter is single, so one call per category is unavoidable), but the calls are independent and run as siblings in one assistant message. For 3 categories this saves another ~6–8 s of wall.

**⚠️ CRITICAL: Use correct endpoint `/categories/v1/bulk/categories/{categoryId}/add-items` with `catalogItemId`, `appId: "215238eb-22a5-4c36-9e7b-e7c08025e04e"`, and `treeReference` object.**
**Make Sure** you pass the treeReference correctly at the same level as "items".


### STEP 5: (Optional) Verify Each Product was Added to a Category
**Skip this step in trusting flows.** Step 4's bulk add-items endpoint returns an `itemMetadata` array per call — check each result there for failures (`itemMetadata[i].success === false`). The `list-items` round-trip is a defense-in-depth that adds ~10 s of wall and rarely surfaces a failure that the metadata didn't already report.

If you keep the verification (e.g., for high-stakes catalogs):
1. Use [List Items In Category](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-v3/categories/list-items-in-category) for each category. Path: `https://www.wixapis.com/categories/v1/categories/{categoryId}/list-items`.
2. **Fire all N list-items calls as a single concurrent batch** — they're independent.
3. Body must include a top-level `treeReference` field (not nested inside `category`).
4. If a list is empty for a category that should have items, repeat STEP 4 for that category only.

---

## Conclusion
Following these steps **in order** guarantees the creation flow for new V3 Wix Online Store sites:
- Contains exactly **3** categories
- Contains exactly **5** products (unless the user explicitly requests fewer)
- Each product is connected to at least one category.
- All products follow the correct Catalog V3 API format as specified in the referenced recipe.
