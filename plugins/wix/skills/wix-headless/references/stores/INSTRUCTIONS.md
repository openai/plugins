---
name: stores-implementer
description: "Implements Wix Stores vertical — product catalog, categories, add-to-cart, product pages. Scopes: seed, components, components-css, pages-products, pages-categories, pages-home-and-nav. Extends references/shared/IMPLEMENTER.md."
---

# Stores Implementer

Extends `references/shared/IMPLEMENTER.md`. Read that file first for phase routing, REST auth + doc lookups, prompt-inlined inputs (no site.json reads), return contract, style conventions, and common failure modes.

## Scope routing

| Scope | Phase | Reference |
|-------|-------|-----------|
| `seed` | Seed (REST catalog setup — products only; categories are merchant-driven, not seeded) | `./PRODUCT_CATALOG_DATA.md` |
| `components` | Components (React islands + SeoTags + back-in-stock util — TSX/Astro only, **no CSS**) | `../astro/stores/SHARED_WIRING.md` |
| ~~`components-css`~~ | **Do not dispatch.** `src/styles/components-stores.css` is copied from `<SKILL_ROOT>/references/astro/templates/stores/components-stores.css` by the orchestrator's pre-Step-4.5 batch (see BUILD.md § Step 4.5). The template uses direct `var(--token)` CSS, so it works against any designer-published vocabulary without per-run rewrites. `COMPONENTS_CSS.md` documents that CSS for reference — there is no `components-css` subagent to dispatch. | — |
| `pages-categories` | Pages (`/category/[slug]` listing + shared CategoryRail + `utils/categories.ts`) | `../astro/stores/CATEGORY_PAGES.md` |
| `pages-products` | Pages (products listing + detail + ProductCard; mounts the rail written by `pages-categories`) | `../astro/stores/PRODUCT_PAGES.md` |
| `pages-home-and-nav` | Pages (home-page contribution + Shop submenu in Navigation) | `../astro/stores/HOME_AND_NAV.md` |

> **Why `components` is split.** A single agent writing five .tsx/.astro files plus the scoped CSS dominated Phase 3 wall time (228 s on a 3-product run, 320 s on an 8-product run). The CSS file has no runtime coupling to the TSX components — it's referenced only by class name at build time — so it splits cleanly into a sibling agent that runs in the same dispatch batch. Each scope gets a smaller reading set and a smaller write list. See `../astro/stores/COMPONENTS_CSS.md` § "What this scope owns".

## Files this vertical creates / contributes

See `<SKILL_ROOT>/references/verticals/stores.md` frontmatter (`creates:` and `contributes:` blocks).

## Pre-return file-existence assertion (all page scopes)

Before returning `status: "complete"` from any `pages-*` scope, verify every file listed in your scope's `files:` block (see verticals/stores.md) exists on disk. Silently dropping a file (e.g. `[slug].astro` from `pages-products`) reports `complete` to the orchestrator, but every product link 404s at runtime.

If a declared file is missing, return `status: "partial"` with `errors: [{ code: "PHASE4_FILE_MISSING", path: "<expected path>" }]` rather than claiming success. The orchestrator's Step 8.0.5 manifest check will also catch this, but an agent-side assertion gives a faster and more precise failure.

## Templates

Canonical templates live at `<SKILL_ROOT>/references/astro/templates/stores/`. Your `components` and `pages-*` scopes read these and adapt them — don't invent markup or logic.

Components (`components` scope — TSX/Astro only):
- `<SKILL_ROOT>/references/astro/templates/stores/AddToCartButton.tsx`
- `<SKILL_ROOT>/references/astro/templates/stores/ProductPurchase.tsx`
- `<SKILL_ROOT>/references/astro/templates/stores/BackInStockForm.tsx`
- `<SKILL_ROOT>/references/astro/templates/stores/SeoTags.astro`

Components CSS (`components-css` scope — scoped CSS only):
- `<SKILL_ROOT>/references/astro/templates/stores/components-stores.css`

Pages (`pages-products` scope):
- `<SKILL_ROOT>/references/astro/templates/stores/ProductCard.astro`
- `<SKILL_ROOT>/references/astro/templates/stores/products/index.astro`
- `<SKILL_ROOT>/references/astro/templates/stores/products/[slug].astro`

Pages (`pages-categories` scope):
- `<SKILL_ROOT>/references/astro/templates/stores/CategoryRail.astro`
- `<SKILL_ROOT>/references/astro/templates/stores/category/[slug].astro`

### Pre-copied by the orchestrator (do NOT write these yourself)

The following utility files are deterministically copied by the orchestrator BEFORE your phase dispatches (`components` for the first, `pages` for the second). They are mechanical SDK wrappers with no brand-specific content; reading or rewriting them as part of your scope wastes tokens and risks drift. Just import the helpers at the listed paths:

- `src/utils/back-in-stock.ts` — pre-copied from `<SKILL_ROOT>/references/astro/templates/stores/back-in-stock.ts` before `components` dispatches.
- `src/utils/categories.ts` — pre-copied from `<SKILL_ROOT>/references/astro/templates/stores/categories.ts` before `pages` dispatches.

If you find one of these missing at runtime, that's an orchestrator-side bug — return `status: "partial"` with `errors: [{code: "UTILITY_TEMPLATE_NOT_PRECOPIED", path: "<missing>"}]` and continue. Do NOT write your own version; the post-phase manifest check will recover by template-copy and the right helper lands on disk.

## CSS ownership — stores pack

Stores-specific component CSS lives in `src/styles/components-stores.css` (written by the `components-css` scope — see `../astro/stores/COMPONENTS_CSS.md`), NOT in the designer's `global.css`. The classes the pack owns:

- `.product-card`, `.product-card-media`, `.product-card-ribbon`, `.product-card-index` — the product card itself, including the `overflow: hidden` + `border-radius` clipping context. Whoever writes the `border-radius` here also writes any inner padding required to keep child content inside the rounded edges. Without inner padding, a price `<p>` sits flush against the rounded bottom corner and descenders get clipped. Add `padding-bottom: var(--spacing-md)` on the card plus horizontal padding on each text block when you set the radius. See `references/shared/STYLING.md` § "Component-specific CSS is owned by the component, not the designer".
- `.product-grid` — the layout that lists product cards. Both `/products` (pages-products scope) and `/category/[slug]` (pages-categories scope) consume it from one place. Include `display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--spacing-xl);` plus the View-Transitions opacity fade for in-flight navigations.
- `.offer-callout` family (`.offer-callout`, `-item`, `-badge`, `-name`, `-detail`, `-foot`) — discount panel rendered above `<ProductPurchase>` on `/products/[slug]`.

The designer's `global.css` declares only tokens, the `.btn` family, decorative slots, the editorial-rule, and the site-shell shells. If `global.css` ships with a partial rule for any class above, that's a designer bug — flag it in your return JSON's `errors` array (`{code: "GLOBAL_CSS_LEAK", class: "<name>"}`) and override with the complete rule in `components-stores.css`.

## Back-in-stock subscribe — components + pages wiring split

Back-in-stock is a dashboard-toggleable feature: it ships in every stores build but only lights up when the merchant clicks "Start Collecting Requests" in the Back in Stock dashboard. The implementation is split across the two scopes the same way every other stores feature is:

- **`components` scope** writes the SSR probe (`src/utils/back-in-stock.ts`) and the React form island (`src/components/BackInStockForm.tsx`). See `../astro/stores/BACK_IN_STOCK.md` for the full rules — especially the two app ids (use `1380b703-…` for back-in-stock, NOT the Stores install id `215238eb-…`) and the bare-fields rule (no `itemUrl`, no `image` on the SDK call).
- **`components-css` scope** appends the back-in-stock form rules to `src/styles/components-stores.css` as part of writing that file. See `../astro/stores/BACK_IN_STOCK.md` § 3 for the CSS append.
- **`pages-products` scope** imports `getBackInStockEnabled` in `[slug].astro`, awaits the probe, and passes `backInStockEnabled` + `priceAmount` to `<ProductPurchase>`. ProductPurchase renders the form in its three OOS branches when the prop is true.

If the merchant hasn't enabled "Start Collecting Requests", the probe returns `false`, the prop stays `false`, and the form never mounts — no rebuild needed when the merchant flips the toggle in the dashboard.

## Stores-specific failure modes

| Wrong | Right |
|---|---|
| `import { products }` | `import { productsV3 }` — V1 silently returns 0 on V3 catalogs |
| Skip `variantId` on cart add | Always include — single-variant products have one |
| Omit `wixMetadata` on `/products/[slug]` | Required for Wix sitemap/SEO/deep-link routing |
| Mount CartBadge on a page component | Mount via ecom's `contributes:` marker in `Navigation.astro` so it appears on all pages |
| Hit `/stores/v3/categories/...` for category endpoints | Categories live under `/categories/v1/` — `POST /categories/v1/categories`, `POST /categories/v1/bulk/categories/{id}/add-items`, `POST /categories/v1/categories/query` |
| Use the back-in-stock app id `1380b703-…` when adding items to a category | Use the **Stores install id** `215238eb-22a5-4c36-9e7b-e7c08025e04e` for `appId` on `bulkAddItemsToCategory` items — it's the same id Wix Stores writes to its products |
| Call `categories.queryCategories(...).limit(N).find()` with no filter | The SDK builder rejects empty filter expressions with `INVALID_FILTER`. Always chain at least `.eq("visible", true)` before `.find()` |
| Call `categories.listCategoriesForItems(items, ...)` from the SDK | The SDK function ships items via GET querystring and breaks on arrays. Use `POST /categories/v1/categories/list-categories-for-items` directly, or fan out per-category via `listItemsInCategory` |
| Ship a client-side filter (`data-category-ids` + JS hide) on the product grid | Filter server-side via `/category/[slug]` routes; client-side filtering doesn't scale past ~100 products and breaks SEO. The `<CategoryRail/>` swaps cards via `<ClientRouter />`, not by hiding them |