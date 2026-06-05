# Phase 4 Product Pages — Stores

Scope: `product-pages`. Launched in **Step 7** after designer page scopes have written placeholder `.astro` files. This scope rewrites the product listing, product detail, and ProductCard component with live `productsV3` queries.

## Scope

Files this agent OWNS (rewrites from designer output):

- `src/pages/products/index.astro` — product listing
- `src/pages/products/[slug].astro` — product detail with `wixMetadata` + SEO tags
- `src/components/ProductCard.astro` — reusable card used by listing + home

Files this agent MUST NOT touch:
- `src/components/ProductPurchase.tsx`, `src/components/AddToCartButton.tsx` — owned by `components`
- `src/pages/cart.astro`, `src/pages/thank-you.astro` — owned by `pages-cart-checkout`
- `src/pages/index.astro`, `src/components/Navigation.astro` — owned by `pages-home-and-nav`
- `src/components/CategoryRail.astro` — owned by `pages-categories`. **Import** from `../../components/CategoryRail.astro`; never `Write` it. If it's not on disk yet when you go to mount it, that means the orchestrator dispatched scopes out of order — return `status: "partial"` with `errors: [{ code: "MISSING_PAGES_CATEGORIES_OUTPUT", path: "src/components/CategoryRail.astro" }]` (never defensively `Write` it yourself — `pages-categories` is the only writer, and racing it trips the harness staleness guard).
- `src/utils/categories.ts` — pre-copied by the orchestrator before Phase 4 (BUILD.md Step 7 pre-batch). **Import** `listStoreCategories`/etc. from `../../utils/categories`; never `Write` it.
- `global.css`, any other `.astro` page, any other component — owned by designers

## Inputs (from parent prompt)

- **Phase 1 return data** — `products: [{id, name, slug, variantId, price, inventory, sku}]` — use slugs when needed (rarely; `queryProducts` returns them already).
- **Design tokens** — the full `designTokens` JSON is inlined in your prompt for the published color/spacing/typography vocabulary; compose Tailwind utilities derived from those tokens (`class="py-4xl flex flex-col gap-md font-display"`) at the call site rather than inventing semantic classes for layout/spacing/typography. Retained global semantic classes are limited to compound patterns (`offer-callout`, `cart-summary`), interactive primitives (`btn-primary`, `product-card`), and JS targets — see `references/shared/STYLING.md`.
- **Designer output summary** — paths of existing `products/index.astro`, `products/[slug].astro`, `ProductCard.astro` with placeholder data.

## Critical rules (all must be honored)

1. **Use `productsV3`, not `products`** — V1 silently returns 0 on V3 catalogs.
2. **Product detail MUST use `getProductBySlug()`**, not `queryProducts()`. `queryProducts` omits variant data (`options`, `variantsInfo`), making add-to-cart silently fail.
3. **Product detail MUST export `wixMetadata`** — required for Wix sitemap, SEO editor, and dashboard deep links. Without it, the sitemap has zero product entries.
4. **Mount `SeoTags` on the detail page** — pipe `product.seoData.tags` through `Layout`'s `head` slot so merchant SEO edits in the Wix dashboard reach the live site. `seoData` is returned by default — no `fields` flag needed.
5. **Mount `ProductPurchase` with `client:load` and a single `product` prop, plus the back-in-stock probe + price props.** `<ProductPurchase client:load product={product} inventoryByVariant={inventoryByVariant} backInStockEnabled={backInStockEnabled} priceAmount={priceAmount} />`. The component destructures internally; passing flat props (`productId={product._id}`, `options={product.options}`, …) silently renders nothing because the new contract expects `product`. The `backInStockEnabled` boolean comes from `await getBackInStockEnabled()` (template imports it from `../../utils/back-in-stock`); `priceAmount` is the numeric price already computed in the frontmatter. See `BACK_IN_STOCK.md` for why both are needed.
6. **SSR only — do NOT add `export const prerender = true` or `getStaticPaths()`.** The productsV3 SDK depends on request-context auth (tenant resolution, site headers). At prerender time there is no request, and `.queryProducts().limit()` short-circuits to `"is not a function"`. Keep `[slug].astro` server-rendered with `Astro.params.slug`.
7. **No HTML comments in `.astro` frontmatter.** Build fails with "Legacy HTML single-line comments are not allowed".
8. **Default to tokens-as-utilities for layout/spacing/typography.** When you need a section padding, a flex column, a typographic treatment — write Tailwind utilities derived from `@theme` tokens (`<section class="py-4xl flex flex-col gap-md">`, `<h1 class="font-display text-4xl">`). Do NOT invent semantic classes like `.featured-section`, `.page-header`, `.products-header-image` — Tailwind v4 silently drops undeclared classes. Use a global semantic class only when one is published in designer `INSTRUCTIONS.md`'s always-required list (`product-card`, `product-card-ribbon`, `offer-callout` family). For one-off page decoration, write a co-located `<style>` block at the bottom of the same `.astro` file using `var(--color-foo)` token references.
9. **Preserve designer classes.** When the designer used a published global semantic class on existing markup, keep it; don't rename. Add Tailwind utilities alongside if you need additional layout adjustment.

## Wix Site Structure — `wixMetadata` + `@wix/astro-pages`

`@wix/astro-pages` is already wired into the blank scaffold's `astro.config.mjs` as `wixPages()`. It injects a `/_wix/pages.json` endpoint enumerating every page and reading each page's `wixMetadata` export. Wix platform services use this JSON to:

- Generate server-side sitemap entries for dynamic product URLs (via `@wix/auto_sdk_seo_seo-sitemap-entries`)
- Power the dashboard SEO editor ("Edit SEO for Product pages")
- Resolve deep links from dashboard / email / analytics surfaces back to the right headless URL

> **Two different Stores appDefIds — do not confuse:**
> - `215238eb-22a5-4c36-9e7b-e7c08025e04e` — for `catalogReference.appId` in cart operations (same value used for app install in Phase 1).
> - `1380b703-ce81-ff05-f115-39571d94dfcd` — for **`wixMetadata.appDefId`** on Stores sub-pages (product, category).
>
> Both are correct. They identify different entities.

## Template files

This scope uses **template files** instead of inline code. For each file below:

1. Read the template from `<Agent location>/templates/<path>`
2. Write it to the project at the target path
3. Adapt class names only if the styling contract maps them differently than the defaults

Do NOT modify logic, imports, SDK calls, `wixMetadata` export, or prop-passing. The templates encode non-negotiable Wix platform integrations (sitemap registration, inventoryItemsV3 OOS truth, SSR-only constraint, analytics payloads).

## Implementation

> Every Wix SDK `await` in the templates is already wrapped in try/catch — keep those guards when adapting. See `references/shared/IMPLEMENTER.md` § "SSR error guards" for the underlying rule and rationale.

### 1. `src/pages/products/index.astro` — product listing

Use template `templates/products/index.astro`.

Preserves the designer's page structure (class names, layout) and replaces the placeholder products array with a guarded, **cursor-paginated** `productsV3.queryProducts({ fields: ["CURRENCY"] }).limit(24).skipTo(cursor).find()` (cursor read from `?cursor=` on the URL; Prev/Next anchors built from `result.cursors.next` / `.prev`). Mounts the shared `<CategoryRail/>` (written by `pages-categories`) above the grid, passing `activeSlug={null}` and the prev/next hrefs. Emits the `AddProductImpression` analytics event from a client-side script that reads a JSON payload serialized at SSR.

> **Imports written by `pages-categories`.** Both `<CategoryRail/>` and `listStoreCategories` come from files this scope must NOT write — they're owned by the `pages-categories` scope. Import paths: `../../components/CategoryRail.astro` and `../../utils/categories`. If either import fails to resolve, return `status: "partial"` with `errors: [{ code: "MISSING_PAGES_CATEGORIES_OUTPUT", path: "<missing path>" }]` — that means the orchestrator dispatched scopes out of order.

> **Page size 24** — multiple of the 2/3/4-column grid, well under Wix's per-request cap of 100. Do not change without updating `CATEGORY_PAGES.md` to match.

> **No client-side filter.** Do not ship every product and hide non-matching cards via JS — it doesn't scale and breaks SEO. Do not add `data-category-ids` on `<ProductCard>` or any DOM-hide script. Filtering is done by navigating to `/category/<slug>` (a real route), and `<ClientRouter />` from the designer's Layout handles the swap.

> **Why the double-script pattern:** Listing page is server-rendered but `AddProductImpression` must fire in the browser. The server-computed payload is serialized into an inert JSON `<script>` (`is:inline`) and read by a separate processed `<script>` (bundled by Astro — has ES `import`). `define:vars` + inline-script combinations cannot do ES imports.

> **Gift-card mirror filter (do not remove).** The template applies `productList = productList.filter(p => p.ribbon?.name !== "Gift Card")` after building the result list. When the dashboard's Wix Gift Card app is enabled, it auto-creates 5 mirror Stores products (one per denomination, `productType: "DIGITAL"`, ribbon name `"Gift Card"`). Buying a mirror yields a dud DIGITAL line item that does NOT trigger gift-card issuance — the customer-facing surface for gift cards is `/gift-cards` (gift-cards pack), not `/products`. The filter holds whether or not the gift-cards pack is loaded for this site, so a future site that drops gift-cards but still has the dashboard app stays clean.

### 2. `src/components/ProductCard.astro` — reusable card

Use template `templates/ProductCard.astro`.

The template:
- Accepts a single `{ product }` prop — the full Wix product object from `productsV3`
- Resolves product images via `resolveWixImageUrl` (imported from the seeded shared util at `../utils/wix-image`)
- Applies `product-card` contract class
- Includes delegated click analytics (`ClickProduct` event via data attributes)

Class from contract: `productCard` → `"product-card"`. If the designer already added the class, don't duplicate.

### 3. `src/pages/products/[slug].astro` — product detail

Use template `templates/products/[slug].astro`.

The template:
- Exports `wixMetadata` with the Stores sub-page appDefId (`1380b703-…`) and `STORES.PRODUCT.SLUG` token for platform expansion
- Uses `getProductBySlug()` (NOT `queryProducts()` — it omits variant data)
- Queries `inventoryItemsV3.queryInventoryItems({ filter: { productId } })` and builds a `variantId → { quantity, trackQuantity, preorderEnabled }` map. This is the AUTHORITATIVE OOS signal; `variantsInfo[].inventoryStatus.inStock` is a stale cached flag.
- Pipes `product.seoData.tags` through Layout's `head` slot via `<SeoTags slot="head" tags={seoTags} />` (rendered only when any tag is visible)
- Calls `await getBackInStockEnabled()` from `../../utils/back-in-stock` to learn whether the dashboard's "Start Collecting Requests" toggle is on for Wix Stores; passes the boolean and `priceAmount` to `<ProductPurchase>`. The back-in-stock subscribe form renders inside ProductPurchase's three OOS branches when the prop is true. See `BACK_IN_STOCK.md` for the app-id discrepancy and the bare-fields rule.
- Mounts `<ProductPurchase client:load product={product} inventoryByVariant={inventoryByVariant} backInStockEnabled={backInStockEnabled} priceAmount={priceAmount} />` with the canonical `{ product }` contract
- Wraps both SDK awaits in try/catch so an SDK error produces a 404 redirect (product fetch) or an empty inventory map (inventory fetch), never a torn page (the back-in-stock probe is internally wrapped — it returns `false` on any failure, so it doesn't need an outer try/catch)

**Critical details on `wixMetadata`:**

- **Required for Wix platform indexing.** Without it, the product detail route is invisible to Wix's sitemap generator, SEO editor, and deep-link resolver.
- **`appDefId`: `1380b703-ce81-ff05-f115-39571d94dfcd`** is the Stores page-registration defId — do NOT confuse with the Stores install/catalog defId (`215238eb-...`) used in Phase 1 and `catalogReference.appId`.
- **`pageIdentifier`: `"wix.stores.sub_pages.product"`** is the canonical Wix identifier — constant.
- **`identifiers.slug`**: maps the Astro route param to Wix's identifier token. Route is `[slug].astro`, so key is `slug`. Value `"STORES.PRODUCT.SLUG"` tells Wix to expand with each product's slug.

**Layout `head` slot** — the `Layout.astro` written by the Design System phase must accept a `head` slot and a `hasSeoTags` prop. When `hasSeoTags` is true, the Layout omits its default `<title>`/`<meta description>` and instead renders the `head` slot contents into `<head>`. This lets `SeoTags` entirely replace the default metadata. If the Layout signature doesn't match, the Design System brief is missing it — flag this in the return's `errors` array and continue with a fallback (non-merchant-editable) title.

## Live offers (discount-rule indicators)

The promotion ribbon on each product card is **owned by `ProductCard.astro` itself** — the component imports `fetchLiveOffers` + `offersForProduct` from `src/utils/discounts.ts` (shipped by the ecom `components` scope) and renders its own ribbon. Pages that mount `ProductCard` do NOT pass an `offers` prop and do NOT fetch offers themselves. This concentrates the wiring in one place — page-level wiring forced every page that renders ProductCard to remember it, and category pages would silently ship without ribbons.

`fetchLiveOffers` is memoized per request via `auth.elevate`'s caching, so rendering N ProductCards in one page does NOT fan out N discount-rule queries.

**Listing (`products/index.astro`)** — just `<ProductCard product={product} index={idx} />`. No offers wiring required.

**Detail (`products/[slug].astro`)** — the detail page renders a richer offer callout above `<ProductPurchase>`. That callout still belongs to this scope (it's not part of the card). After the product is loaded:

```ts
import { fetchLiveOffers, offersForProduct } from "../../utils/discounts";
const offers = await fetchLiveOffers();
const productOffers = offersForProduct(offers, product._id);
```

```astro
{productOffers.length > 0 && (
  <div class="offer-callout">
    {productOffers.map((o) => (
      <div class="offer-callout-item">
        <span class="offer-callout-badge">Offer</span>
        <div>
          <p class="offer-callout-name">{o.name}</p>
          {o.offer && o.offer !== o.name && (
            <p class="offer-callout-detail">{o.offer}</p>
          )}
        </div>
      </div>
    ))}
    <p class="offer-callout-foot">Applied automatically at checkout.</p>
  </div>
)}

<ProductPurchase client:load product={product} inventoryByVariant={inventoryByVariant} />
```

The `.offer-callout*` classes are owned by `src/styles/components-stores.css` (written by the stores Phase 3 components agent), NOT by the designer. Use `{o.offer}` for the body text — that's the dashboard-authored offer string (e.g. `"Buy 1 item\nAll products\n\nGet 1 item for free"`) which Wix formats with `\n` line breaks; the CSS includes `white-space: pre-line` so those render as line breaks.

**Do NOT** hit `discountRules.queryDiscountRules` directly from this scope — always go through `fetchLiveOffers()`. The helper wraps the call with `auth.elevate()` (the endpoint requires `ECOM.DISCOUNT_RULES_READ`, visitor clients return nothing silently) and normalizes the scope-id field (`_id` vs `id`) which trips up naive matching.

When the site has no active rules (first deploys, or the user hasn't created any in the dashboard yet), `offers` comes back as `[]`, `offersForProduct(...)` returns `[]`, the ribbon and callout both render nothing — no code path to guard for.

## Analytics fired from this scope

| Event | Fires from | When | Payload |
|-------|------------|------|---------|
| `AddProductImpression` | `products/index.astro` | Listing page load | `{ contents: [{id, name, price, currency, position}], origin: "Product Listing" }` |
| `ClickProduct` | `ProductCard.astro` | Delegated click on any card | `{ id, name, price, currency, origin: "Product Listing" }` |
| `ViewContent` | `products/[slug].astro` | Detail page load | `{ id, name, price, currency, origin: "Product Page" }` |

`AddToCart` fires from `AddToCartButton.tsx` (written by `components`) — not this scope.

## Return format

```json
{
  "status": "complete",
  "phase": "stores-pages-products",
  "scope": "product-pages",
  "summary": "Wired product listing + detail + ProductCard to productsV3; wixMetadata + SeoTags mounted",
  "data": {
    "pagesWired": 2,
    "wixMetadataExported": true,
    "seoTagsMounted": true,
    "useGetProductBySlug": true,
    "analyticsEvents": ["AddProductImpression", "ClickProduct", "ViewContent"]
  },
  "files": [
    "src/pages/products/index.astro",
    "src/pages/products/[slug].astro",
    "src/components/ProductCard.astro"
  ],
  "errors": []
}
```

If any of `wixMetadataExported`, `seoTagsMounted`, `useGetProductBySlug` ends up `false`, set `status: "partial"` and populate `errors` with the specific issue. These three are non-negotiable for a merchant-grade site.

## Anti-patterns

| WRONG | CORRECT |
|-------|---------|
| `import { products }` from `@wix/stores` | `productsV3` |
| Use `queryProducts()` on detail page | `getProductBySlug()` — `queryProducts` omits variant data |
| `export const prerender = true` + `getStaticPaths()` on `[slug].astro` | SSR only — productsV3 needs request-context auth; prerender short-circuits it |
| Pass flat props to `<ProductPurchase>` (`productId`, `options`, `variantsInfo`, …) | Pass the whole product: `<ProductPurchase client:load product={product} inventoryByVariant={inventoryByVariant} />` |
| Hardcode `<title>` from `product.name` | Pipe `product.seoData.tags` through `SeoTags` slot, fall back to `product.name` only when tags are empty/disabled |
| Omit `wixMetadata` export | Required — platform indexing breaks silently without it |
| Add `fields: ["SEO_DATA"]` | `seoData` is returned by default — no such enum value exists |
| Write `src/utils/wix-image.ts` inline | Import `resolveWixImageUrl` from `../utils/wix-image` — shared util already exposes it |
| `ls src/` to find designer output | Parent prompt lists every existing `src/` file — read directly |
| Rename designer class names | Keep them; use contract classes when ADDING new markup |
| HTML `<!-- comment -->` in `.astro` frontmatter | `//` or `/* */` — frontmatter is TypeScript |
| Mount React island without `client:load` | Options + cart state needs hydration |
| Pass `"INVENTORY"` in the `fields` array | No such enum value exists for `productsV3`. Valid values: `URL`, `CURRENCY`, `INFO_SECTION`, `MERCHANT_DATA`, `PLAIN_DESCRIPTION`, `INFO_SECTION_PLAIN_DESCRIPTION`, `SUBSCRIPTION_PRICES_INFO`, `BREADCRUMBS_INFO`, `WEIGHT_MEASUREMENT_UNIT_INFO`, `VARIANT_OPTION_CHOICE_NAMES`, `MEDIA_ITEMS_INFO`, `DESCRIPTION`, `DIRECT_CATEGORIES_INFO`, `ALL_CATEGORIES_INFO`, `INFO_SECTION_DESCRIPTION`, `THUMBNAIL`, `PRODUCT_CHOICES_MEDIA_REFERENCES`. Passing an invalid value makes the query throw. |
| Trust `variantsInfo[].inventoryStatus.inStock` as the OOS gate | It's a stale cached flag — a variant with real quantity 0 can still report `inStock: true`. Query `inventoryItemsV3.queryInventoryItems({ filter: { productId } })` at SSR and pass a `variantId → { quantity, trackQuantity, preorderEnabled }` map into `ProductPurchase`. The template already does this. |
| Skip the `backInStockEnabled` prop on `<ProductPurchase>` | Always pass it (template already imports `getBackInStockEnabled`). When the prop is missing, the OOS subscribe form never renders even if the merchant has enabled collecting requests. |
| Pass the formatted price string (`"$695"`) as `priceAmount` | Pass the numeric `priceAmount` already computed in frontmatter. The Wix back-in-stock service rejects formatted prices with `400 DECIMAL_GTE`. |