# Recipe: Product Catalog Data Setup (Phase 1)

Replace the default sample products Wix Stores installs with on-brand products via the Stores REST API (`curl` against `wixapis.com/stores/v3/...` with the standard headers from `../shared/AUTHENTICATION.md`). This file covers the `seed-seed` scope — data seeding only. Frontend wiring lives in the astro scope references (`../astro/stores/SHARED_WIRING.md`, `../astro/stores/PRODUCT_PAGES.md`, `../astro/ecom/CART_PAGES.md`, `../astro/stores/HOME_AND_NAV.md`) and should not be read by `seed-seed`.

> **Critical Rules — Read Before Starting**
> 1. **V3 only** — all endpoints under `/stores/v3/...` for products.
> 2. **No improvised endpoints** — if an REST call returns 404, stop and report. Do not guess alternative URLs. Do not loop on `docs-search REST (see DOCS_SEARCH.md)` more than twice on the same topic.
> 3. **Do not seed categories.** Categories are merchant-driven — created in the Wix dashboard, not by this scope. The storefront's rail, Shop submenu, and `/category/[slug]` route are still wired (Phase 4) and light up automatically once the merchant adds at least one visible category with items (≤ 5 min after creation, the helper's TTL).

> **V3 Catalog:** New Wix sites use Catalog V3. All endpoints below live under `/stores/v3/...`. The V1 product endpoints should not be used — they silently return 0 results on V3 catalogs.

## Prerequisites

- Wix Stores app must be installed on the site (installed via the apps-installer REST endpoint after scaffolding — see Step 0)

## Setup: Replace Default Products via REST

> **Conditional:** This section only applies when ALL of these are true:
> - The Stores app was just installed (default sample products exist)
> - CLI auth works (`npx @wix/cli@latest token --site "$SITE_ID"` returns a token)
> - Discovery context is available in your prompt (business type, brand name, style)
>
> **If CLI auth is not available, skip this entire section.** The 12 default products remain and can be customized later in the Wix dashboard.

> **API error guard:** If any REST call in Phase 1 returns a 404 or an unexpected error, do **not** retry the same call with a guessed alternative URL or namespace. Report the failing endpoint, request body, and error verbatim to the user, then stop.

> **Stores appDefId** for install and `catalogReference.appId`: `215238eb-22a5-4c36-9e7b-e7c08025e04e`. (A different defId — `1380b703-ce81-ff05-f115-39571d94dfcd` — is used for `wixMetadata.appDefId` in Phase 2. Do not swap them.)

### Step 0: Ensure Stores App Is Installed

Before querying products, verify the Stores app is installed:

1. **Probe** — `REST: POST https://www.wixapis.com/stores/v3/products/query`
2. **If the API returns a "REQUIRED_APP_NOT_INSTALLED" error** → install the Wix Stores app:
   ```
   REST: POST https://www.wixapis.com/apps-installer-service/v1/app-instance/install
   body: {
     "tenant": { "tenantType": "SITE", "id": "<siteId>" },
     "appInstance": { "appDefId": "215238eb-22a5-4c36-9e7b-e7c08025e04e", "enabled": true }
   }
   ```
   > Translate this prose-HTTP form into the full `curl` tool-call shape — pass `body` as JSON in `-d` (NOT a stringified JSON). See `../shared/AUTHENTICATION.md` for the standard REST headers.

   Then retry the probe query to confirm installation succeeded.
3. **If the probe succeeds** → proceed to Step 1.

---

Replace the 12 generic sample products with 3 on-brand products that match the user's business before building any code.

### Step 1: Query Default Products

```
REST: POST https://www.wixapis.com/stores/v3/products/query
body: {
  "query": {
    "paging": { "limit": 50 }
  }
}
```

Collect all product IDs from the response.

### Step 2: Bulk Delete Defaults

```
REST: POST https://www.wixapis.com/stores/v3/bulk/products/delete
body: {
  "productIds": ["<id1>", "<id2>", ..., "<id12>"]
}
```

### Step 3: Design 3 On-Brand Products

No API call — use discovery context (business type, brand name, style, industry) to plan 3 products:

- Product names, descriptions, and pricing appropriate for the business
- Product type: `PHYSICAL`
- Options (size, color, etc.) if appropriate for the business type

**Product design guidelines by business type:**

| Business Type | Product 1 | Product 2 | Product 3 |
|--------------|-----------|-----------|-----------|
| Skincare / beauty | Signature serum or moisturizer | Cleansing product | Gift set or bundle |
| Clothing / fashion | Signature top or dress | Accessory item | Seasonal piece |
| Food / bakery | Signature item (cake, bread) | Sampler or variety pack | Gift box |
| Home / decor | Statement piece | Functional item | Set or collection |
| Fitness / wellness | Core product (mat, equipment) | Accessory | Starter kit |
| General retail | Best-seller item | Complementary item | Value bundle |

Adapt names, descriptions, and pricing to match the brand's tone and style. Use the brand name in product descriptions where natural.

### Step 4: Bulk Create Products

> **V3 bulk create body format:** Each item in the `products` array is a flat product object — do NOT wrap in a `"product"` key. Only include `options` and `variantsInfo` when the product has meaningful variants (multiple sizes, colors, etc.). Simple products with no real variants should omit these fields — the API creates a default variant automatically using the product-level price.

**Product with variants** (e.g., skincare with 30ml/50ml sizes):

```
REST: POST https://www.wixapis.com/stores/v3/bulk/products-with-inventory/create
body: {
  "products": [
    {
      "name": "<Product Name>",
      "productType": "PHYSICAL",
      "description": {
        "nodes": [
          {
            "type": "PARAGRAPH",
            "id": "<unique-id>",
            "nodes": [
              { "type": "TEXT", "textData": { "text": "<Product description>" } }
            ],
            "paragraphData": { "textStyle": { "textAlignment": "AUTO" } }
          }
        ],
        "metadata": { "version": 1, "id": "<unique-id>" }
      },
      "visible": true,
      "visibleInPos": true,
      "physicalProperties": {},
      "options": [
        {
          "name": "Size",
          "optionRenderType": "TEXT_CHOICES",
          "choicesSettings": {
            "choices": [
              { "choiceType": "CHOICE_TEXT", "name": "30ml" },
              { "choiceType": "CHOICE_TEXT", "name": "50ml" }
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
                  "choiceName": "30ml",
                  "renderType": "TEXT_CHOICES"
                }
              }
            ],
            "price": { "actualPrice": { "amount": "48.00" } },
            "visible": true,
            "inventoryItem": { "quantity": 50, "preorderInfo": { "enabled": false } },
            "physicalProperties": {}
          }
        ]
      }
    }
  ],
  "returnEntity": true
}
```

Add one more variant object per size in the `variants` array (one per choice combination). Use the Ricos format for descriptions (PARAGRAPH > TEXT > textData).

**Simple product without real variants** (e.g., a gift set with one price and no size/color choices):

Omit `options` and `variantsInfo` entirely. Set the price at the product level. The API creates a default variant automatically:

```json
{
  "name": "Complete Gift Set",
  "productType": "PHYSICAL",
  "visible": true,
  "visibleInPos": true,
  "physicalProperties": {},
  "priceData": { "price": 89.00 },
  "manageVariants": false,
  "inventoryItem": { "trackQuantity": true, "quantity": 30 }
}
```

> **Do NOT create dummy options** (e.g., "Type: Standard") for simple products. Only add `options` and `variantsInfo` when the product genuinely has multiple variants. Phase 2's `ProductPurchase` component detects products without meaningful options and renders just the "Add to Cart" button — no unnecessary selection step for the buyer.

Include all products in the same `products` array. Do not include `media` — product images are handled separately by the image agent after product creation.

### Step 5: Verify

```
REST: POST https://www.wixapis.com/stores/v3/products/query
body: {
  "query": { "paging": { "limit": 50 } }
}
```

Confirm exactly 3 products exist. Report the product names and prices to the user.

### Step 6: Categories are NOT seeded

This scope does **not** create categories. The default Wix Stores install ships one auto-managed category (`online_stores_all_products`) — leave it; the frontend filters it out by handle.

If the merchant later creates visible categories in the Wix dashboard and assigns products to them, the storefront wires up automatically:

- `<CategoryRail/>` renders pills above `/products` and `/category/[slug]`.
- The `Navigation` Shop submenu lists the categories.
- `/category/<slug>` becomes a reachable, server-side-filtered listing.

This works because the frontend (`src/utils/categories.ts`, pre-copied by the orchestrator before Phase 4 and imported by the `pages-*` scopes) live-queries the Wix API at SSR time with a 5-min cache — no redeploy or regen is needed.

### Step 7: Return Results

Emit a structured JSON block at the end of your completion message per `../shared/RETURN_CONTRACT.md`. Do NOT write a sidecar file.

```json
{
  "status": "complete",
  "phase": "stores-seed",
  "scope": "seed-seed",
  "summary": "Deleted {N} default products; created {N} on-brand products with variants",
  "data": {
    "products": [
      {
        "id": "<uuid>",
        "name": "<name>",
        "slug": "<slug>",
        "variantId": "<uuid>",
        "price": 0,
        "inventory": 0,
        "sku": "<sku>"
      }
    ],
    "categories": [],
    "deletedCount": 0,
    "createdCount": 0
  },
  "files": [],
  "errors": []
}
```

`data.categories` is always `[]` — this scope does not seed categories. The field is retained for shape stability so downstream consumers don't need a new schema.

The JSON block MUST be the last content in your message. Parent skill consumes `data.products[*].slug` and `data.products[*].variantId` for the Phase 4 Pages scopes.

### Phase 1 Boundary — Do Not Touch Other Site Data

Phase 1 is complete after Step 7. Do **not** attempt any of the following, even if they seem like reasonable polish:

- Cleaning up "orphan customizations", "All Products" containers, brand records, or any other catalog metadata you didn't create.
- Creating, renaming, or deleting any category — categories are merchant-driven (see Step 6). The auto-managed "All Products" category (handle `online_stores_all_products`) stays in place; the frontend filters it out by handle.
- Verifying your work via additional `query` calls beyond the Step 5 verification already performed.

Phase 2+ (frontend wiring) is covered in the astro scope references (`../astro/stores/SHARED_WIRING.md`, `../astro/stores/PRODUCT_PAGES.md`, `../astro/stores/CATEGORY_PAGES.md`, `../astro/ecom/CART_PAGES.md`, `../astro/stores/HOME_AND_NAV.md`) — do not read them during `seed-seed`.