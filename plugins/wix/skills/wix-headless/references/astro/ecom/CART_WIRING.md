# Phase 3 Components — Ecom (TSX)

Scope: `components`. Launched in **Step 4.5** (after Phase 2 Design System completes, parallel to stores components and the `components-css` sibling). Writes code that depends on the **design tokens** but NOT on Phase 4 page markup.

> **CSS lives in a sibling scope.** `src/styles/components-ecom.css` is owned by the `components-css` scope (see `./COMPONENTS_CSS.md`), which runs concurrently with this one in the same Step 4.5 batch. This scope does NOT write the CSS file. Reference contract class names from the design tokens here; the CSS sibling defines the rules.

## Scope

Files this agent OWNS (creates fresh):

- `src/components/CartView.tsx` — React island; full cart display + checkout redirect
- `src/components/CartBadge.tsx` — React island; nav-wide cart count badge

Files this agent MUST NOT touch:
- `src/styles/components-ecom.css` — owned by the **`components-css`** sibling scope (see `./COMPONENTS_CSS.md`). Reference its class names; do not write the file.
- Any `.astro` page — designed and later rewritten by other scopes
- `src/styles/global.css` — owned by designer foundation
- `src/layouts/Layout.astro` — owned by designer foundation
- Any stores-specific component (AddToCartButton, ProductPurchase, etc.)

## Coordination: design tokens

Your parent prompt includes the design tokens inline. Use it directly — do not read `.wix/design-tokens.css` + `.wix/site.d.ts` from disk.

For layout/spacing/typography, compose Tailwind utilities derived from `@theme` tokens at the call site (`<div class="grid grid-cols-1 md:grid-cols-[1fr_22rem] gap-2xl">`). For published global semantic classes (`cart-summary`, `cart-total`, `checkout-btn`, `cart-empty` — the compound + interactive-state patterns), use the ACTUAL class name verbatim. Row-internal class names (`cart-item-qty`, `qty-btn`, etc.) come from the template — keep them as-is and live in `components-ecom.css`. See `references/shared/STYLING.md` and `references/shared/IMPLEMENTER.md` § "Styling: tokens-first, classes as exception".

## Template files

This scope uses **template files** instead of inline code. For each file below:

1. Read the template from `<Agent location>/templates/<filename>`
2. Write it to the project at the target path
3. Adapt CSS class names if the design tokens maps them differently than the defaults

Do NOT modify logic, imports, or component structure.

## Implementation

### 1. `src/components/CartView.tsx`

Use template `templates/CartView.tsx`.

Full cart display with two-column layout, quantity editing, remove, unavailable item detection, and checkout redirect. **No server-side props** — cart is per-visitor and fetched client-side on mount to keep pages SSR-cache-friendly. Key behaviors:

- **Always use `currentCart` APIs** — never the `cart` namespace that requires a cart ID
- **Image resolution** — `resolveCartImage()` handles `wix:image://` strings (SDK returns image as a string, not an object)
- **Description lines** — `formatDescriptionLine()` handles both `plainText` and `colorInfo` types
- **Per-line price display** — `fullPrice` and `price` are per-unit (shown side by side; `fullPrice` is struck through when an automatic discount is applied to that line); `lineItemPrice` is total (shown below only when qty > 1)
- **Clickable product link** — the image and product name link back to the product detail page. `item.url` shape varies by caller: the `@wix/ecom` SDK returns it as an absolute URL **string** (e.g. `https://<site>.wixsite.com/<name>/product-page/<slug>`), while REST returns an object `{ relativePath, url }`. `resolveProductHref` accepts both, extracts the slug after `/product-page/`, and rewrites to the headless `/products/<slug>` route. Link is suppressed on unavailable lines (nothing to navigate to for NOT_FOUND/NOT_AVAILABLE items).
- **Cart-level totals + discount surfaces (API-sourced)** — `extractSummary()` reads `cart.priceSummary.{subtotal, discount, total}` and `cart.appliedDiscounts[].discountName` in one pass. Three distinct surfaces, each sourced directly from the API (no client-side amount math):
   1. `cart-discount` row — amount + optional name — rendered when `priceSummary.discount` is populated (coupons, cart-level promos).
   2. `cart-applied-discounts` row — name-only — rendered when `priceSummary.discount` is empty but `appliedDiscounts[].discountName` is populated. This is the common case for **line-item automatic discounts**, where Wix bakes the discount into each line's `price` (with `fullPrice` preserved for the strikethrough). The per-line savings amount already shows inline via the `cart-item-full-price`/`cart-item-unit-price` strikethrough; the summary row just names the promotion.
   3. `cart-total` row — rendered when `priceSummary.total` differs from `priceSummary.subtotal`.
  If `priceSummary.subtotal` is missing (some early-stage carts return an empty summary before checkout creation), the subtotal is computed client-side from `lineItemPrice.amount` — do not leave the slot blank. Do NOT aggregate line-item savings into a summary row; shoppers see the strikethrough inline and that is the API's canonical visualization.
- **Availability** — `isItemUnavailable()` checks for `NOT_AVAILABLE` and `NOT_FOUND` status; hides qty selector, blocks checkout
- **Optimistic UI** — quantity changes and item removal update local state immediately before the API responds. Quantity changes are debounced (300ms) so rapid clicks coalesce into a single request. On API error, the cart reconciles from the server via `loadCart()`
- **Instant re-render via sessionStorage snapshot** — every successful cart fetch/update writes `{ lineItems, summary }` to `sessionStorage[CART_CACHE_KEY]`. On mount, CartView reads the snapshot synchronously and renders it before the authoritative fetch completes. Eliminates the empty/loading flash when re-navigating to `/cart`. Per-tab scope (sessionStorage not localStorage) so logout / shared-device scenarios can't leak stale carts to a different identity.
- **Dispatches `cart-updated`** events so CartBadge updates instantly
- **LineItem type** — local structural type mirroring the fields the component consumes. `_id` is declared `string | null | undefined` to match `@wix/ecom`'s `currentCart` return so `cart.lineItems as LineItem[]` type-checks cleanly. If you add new fields, mirror the SDK nullability or narrow at the use site.

Class names used (template provides them — do not invent):
- **Global semantic classes** (in `global.css`, designer-owned): `cart-summary`, `cart-total`, `checkout-btn`, `cart-empty` — compound patterns + interactive states
- **Row-internal classes** (in `components-ecom.css`, written by this scope): `cart-item-qty`, `qty-btn`, `qty-value`, `cart-item-unavailable`, `cart-item-actions`, `cart-item-prices`, `cart-item-full-price`, `cart-item-unit-price`, `cart-item-line-total`, `cart-item-remove`, `cart-item-image-link`, `cart-item-name-link`, `cart-discount`, `cart-discount-name`, `cart-discount-amount`, `cart-applied-discounts`, `cart-applied-discounts-name`, `cart-item-option`, `cart-item-modifiers`
- **Layout/spacing in markup as utilities**: `cart-grid` → `<div class="grid grid-cols-1 md:grid-cols-[1fr_22rem] gap-2xl md:gap-3xl md:items-start">`; `cart-items` → `<div class="flex flex-col gap-lg">`; `cart-item` → `<div class="flex gap-lg pb-lg border-b border-rule last:border-0">`; `cart-subtotal` → `<div class="flex justify-between items-baseline">`; `cart-item-image` → utilities; `cart-item-info` → utilities; `cart-item-name` → `class="font-display text-lg leading-tight"`

### 2. `src/components/CartBadge.tsx`

Use template `templates/CartBadge.tsx`.

Mounted once in `Navigation.astro` (by `ecom-pages` scope). Shows cart item count; listens for `cart-updated` custom event.

**No `initialCount` prop.** Cart is per-visitor — server-rendering the count breaks SSR caching. On mount, CartBadge reads the sessionStorage snapshot that CartView maintains (same `CART_CACHE_KEY`) to seed the initial count without a visible zero-flash between page navigations, then fetches fresh from the SDK and reconciles. If no snapshot exists (first-ever page load), count starts at 0 like before.

**Mount with `client:only="react"`, never `client:load`.** sessionStorage is browser-only, so SSR would render `count: 0`, then hydration would read the cache and flip to the real number — a visible blink on every page navigation. `client:only` skips SSR entirely; the badge renders once on the client with the cached count already populated.

Contract keys: `cartBadge`, `cartBadgeCount`

### 3. `src/utils/analytics.ts` — not owned by this scope

> `analytics.ts` is a shared utility (see `references/shared/analytics.ts`). Import from it (`import { trackEvent } from "../utils/analytics"`) but do not write it.

### 4. `src/styles/components-ecom.css` — not owned by this scope

> Owned by the **`components-css`** sibling scope. See `./COMPONENTS_CSS.md`. Reference the contract class names from the design tokens in your TSX files; the CSS sibling defines the rules.

## Return format

```json
{
  "status": "complete",
  "phase": "ecom-components",
  "scope": "components",
  "summary": "Wrote CartView and CartBadge from templates (CSS handled by components-css sibling)",
  "data": {
    "islands": ["CartView.tsx", "CartBadge.tsx"]
  },
  "files": [
    "src/components/CartView.tsx",
    "src/components/CartBadge.tsx"
  ],
  "errors": []
}
```