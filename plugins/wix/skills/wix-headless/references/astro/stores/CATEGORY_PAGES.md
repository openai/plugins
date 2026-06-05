# Phase 4 Category Pages — Stores

Scope: `pages-categories`. Launched in **Step 7** alongside `pages-products` and `pages-home-and-nav`. This scope writes the dedicated category landing route and the shared `<CategoryRail/>`. The `categories.ts` helper that all three scopes import is **pre-copied by the orchestrator before this phase** (BUILD.md Step 7 pre-batch) — do NOT write it here.

**Dispatch:** all three stores Phase-4 scopes are dispatched in parallel — Astro resolves the cross-file imports at build time (Step 8). The orchestrator does not need to serialize them. Each scope only needs its own declared files to exist by the time `astro build` runs; `categories.ts` is already on disk from the pre-batch.

## Scope

Files this agent OWNS (writes):

- `src/pages/category/[slug].astro` — category landing (server-side filtered, cursor-paginated)
- `src/components/CategoryRail.astro` — shared rail + Prev/Next pagination, persisted across `<ClientRouter />` swaps

Files this agent imports but MUST NOT write:
- `src/utils/categories.ts` — TTL-cached helpers (`listStoreCategories`, `getCategoryBySlug`, `listProductsInCategory`). **Pre-copied by the orchestrator** before this phase (it's a static, brand-agnostic SDK wrapper); import the helpers, never author the file. Writing it races `pages-products`/`pages-home-and-nav`, which import the same path.

Files this agent MUST NOT touch:
- `src/pages/products/index.astro`, `[slug].astro`, `src/components/ProductCard.astro` — owned by `pages-products`
- `src/pages/index.astro`, `src/components/Navigation.astro` — owned by `pages-home-and-nav`
- `src/layouts/Layout.astro`, `global.css` — owned by designer (View Transitions + loading bar live there)
- `src/components/ProductPurchase.tsx`, `AddToCartButton.tsx`, `BackInStockForm.tsx` — owned by `components`

## Inputs (from parent prompt)

- **Phase 1 return data** — `categories: []`. Phase 1 does not seed categories (they're merchant-driven). This scope still writes the helper + rail + route — they're harmless when no categories exist, and they light up automatically once the merchant creates visible categories with items in the dashboard. `listStoreCategories()` queries the API live at SSR time (5-min TTL cache), so no redeploy is needed when categories are added later.
- **Design tokens** — the full `designTokens` JSON is inlined in your prompt (same shape Designer returned). Page header / breadcrumbs / pill / pagination styling should follow `references/shared/STYLING.md` (utilities derived from tokens, semantic classes only for primitives).
- **Designer output summary** — confirm `Layout.astro` already includes `<ClientRouter />`, `transition:persist` markers on nav/footer, and the `[data-nav-progress]` element + after-swap hook. If any of those is missing, return `status: "partial"` with `errors: [{ code: "DESIGNER_LAYOUT_MISSING_TRANSITIONS", path: "src/layouts/Layout.astro" }]`.

## Critical rules (all must be honored)

1. **Server-side filter only.** Do NOT ship a client-side filter that hides cards via `card.hidden = true` or `data-category-ids`. That pattern doesn't scale past a few hundred products and breaks SEO. Filtering is by URL: `/category/<slug>` is the canonical filter, server-renders only matching products. The rail click is a real navigation that `<ClientRouter />` swaps in place.
2. **Use `@wix/auto_sdk_categories_categories`**, not `@wix/categories` (the published name) — the auto_sdk package is already on disk via every other `@wix/*` package's transitive deps. Importing `@wix/categories` triggers a fresh `npm install`. The provided template uses `import * as categories from "@wix/auto_sdk_categories_categories"` already; do not rewrite.
3. **`queryCategories(...)` rejects empty filters.** The SDK builder's `.find()` validates that at least one predicate has been chained. Always include `.eq("visible", true)` (the constraint we want anyway). Provided template already does this.
4. **Filter out the auto-managed "All Products" category** by `handle === "online_stores_all_products"`. It's installed by Wix Stores automatically and contains every product; surfacing it in the rail makes the All pill duplicate.
5. **Filter out empty categories** by `itemCounter === 0` so the rail doesn't show buckets that 404 in practice (the route still works, but the pill leads to "Nothing in <name> just now").
6. **`STORES_APP_ID` lives in the pre-copied `categories.ts`** — the template already sets it to the Stores app id `215238eb-22a5-4c36-9e7b-e7c08025e04e` (same id used for cart ops and Phase 1 product seed; NOT the back-in-stock id `1380b703-…`). You do not write that file; this is documented so the helpers you import behave as expected.
7. **Cursor pagination** uses `productsV3.queryProducts().limit(24).skipTo(cursor)`. Cursor lives in `?cursor=…` on the URL, surfaced from `result.cursors.next` / `result.cursors.prev`. Prev/Next links use `data-astro-prefetch="hover"` so hovering them warms the cache.
8. **Module-level TTL cache (5 min)** in `categories.ts` is opportunistic; safe under the Cloudflare-style fetch adapter (each worker isolate is single-tenant). Errors don't poison the cache.
9. **Two-call pipeline** in `listProductsInCategory`: first `listItemsInCategory(categoryId, { appNamespace: "@wix/stores" })` for IDs, then `productsV3.queryProducts().in("_id", ids).limit(24).skipTo(cursor).find()`. There is no Wix endpoint that does category filter + cursor paging in one shot — don't attempt `listCategoriesForItems` from the SDK; it ships items via GET querystring and breaks on arrays. If you need product → categories mapping (e.g. for breadcrumbs on product detail), call the REST POST endpoint directly: `POST /categories/v1/categories/list-categories-for-items`.

## Writing the templates

Read each template at `templates/stores/` and write it verbatim to the corresponding `src/` path, with three small adjustments. (`categories.ts` is **not** in this list — the orchestrator pre-copies it; you only import its helpers.)

| Template path | Site path |
|---|---|
| `templates/CategoryRail.astro` | `src/components/CategoryRail.astro` |
| `templates/category/[slug].astro` | `src/pages/category/[slug].astro` |

Adjustments at the call site:

1. The category page header copy ("Shop", breadcrumbs, lede) should adapt to brand tone. The template ships generic ("Browse our X collection"); rewrite the breadcrumb middle anchor and the empty-state line to match the rest of the site's voice. Keep semantics — same elements, same classes, same `data-*` markers.
2. If the brand uses an editorial eyebrow pattern on `/products` (e.g. "Issue No. 01 · The Collection"), mirror it on `/category/[slug]` (e.g. "Category · Lounge Chairs"). Otherwise omit.
3. Page-header CSS class names (`page-header`, `page-header-title`, `page-header-lede`, `breadcrumbs`, `page-header-image`) must match what the designer published. If the designer used different names, rename inside the template — do NOT introduce new ones.

## Pre-return file-existence assertion

Before returning `status: "complete"`, verify the two files you write exist:

- `src/components/CategoryRail.astro`
- `src/pages/category/[slug].astro`

If either is missing, return `status: "partial"` with `errors: [{ code: "PHASE4_FILE_MISSING", path: "<expected path>" }]`. The orchestrator's manifest check will also catch this, but an agent-side assertion gives a faster and more precise failure. Also confirm the pre-copied `src/utils/categories.ts` is on disk (you import it); if it's missing, that's an orchestrator-side bug — return `status: "partial"` with `errors: [{ code: "UTILITY_TEMPLATE_NOT_PRECOPIED", path: "src/utils/categories.ts" }]` and do NOT write your own.

## Return contract

```json
{
  "status": "complete",
  "phase": "stores-pages",
  "scope": "pages-categories",
  "summary": "Wrote shared CategoryRail + /category/[slug] route (imports the pre-copied categories helper); route renders M categories.",
  "data": {
    "categoriesRendered": 0,
    "filesWritten": [
      "src/components/CategoryRail.astro",
      "src/pages/category/[slug].astro"
    ]
  },
  "files": [],
  "errors": []
}
```

Phase 1 always reports zero categories (it does not seed them). Set `categoriesRendered: 0` and return `status: "complete"` — the helper, rail, and route are still written so the storefront lights up automatically the first time the merchant creates a visible category with items in the dashboard, with no code change needed.