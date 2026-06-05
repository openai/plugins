# Phase 3 Components — Gift Cards

Launched in **Step 4.5** alongside other verticals' `components` scopes (after Phase 2 Design System). Writes the runtime probe utility, the buy-flow React island, and scoped CSS. Finishes before the Phase 4 Pages scopes run in Step 7.

## Scope

Files this agent OWNS:

- `src/utils/gift-cards.ts` — runtime probe of the dashboard's eGift Card template + types
- `src/components/GiftCardPurchase.tsx` — React island; recipient form + variant pills + add-to-cart
- `src/styles/components-gift-cards.css` — scoped CSS for the form fields, amount pills, hero image frame, and home teaser

Files this agent MUST NOT touch:
- `src/utils/wix-image.ts`, `src/utils/analytics.ts` — shared utilities. Import from them; do not write copies.
- `src/components/AddToCartButton.tsx`, `src/components/CartBadge.tsx`, `src/components/CartView.tsx` — owned by stores/ecom; gift-cards uses `currentCart.addToCurrentCart` directly inside the buy-flow island, not via `AddToCartButton`.
- Any `.astro` page or layout — those are written by other scopes.
- `src/styles/global.css` — owned by designer foundation.

## Coordination: design tokens

Your parent prompt includes the design tokens inline. Reference token CSS variables (`var(--color-cream)`, `var(--spacing-lg)`, etc.) from `components-gift-cards.css`. Do NOT read `.wix/design-tokens.css` from disk.

## Critical rules

1. **`httpClient.fetchWithAuth` from `@wix/essentials`** — the JS SDK's gift-vouchers package only exposes redemption methods; the buy-template query is reachable only via REST.
2. **Module-level memoization** — hold one in-flight `Promise<GiftCardProduct | null>` at module scope so Navigation, home, and `/gift-cards` calls within the same request coalesce. The plugin's `discounts.ts` skips memoization for simplicity but the gift-card template is far more cacheable, so this pack pays the small cost.
3. **Return `null` on every failure** — non-2xx, empty `giftCardProducts[]`, network/JSON error. The page/nav/teaser callers branch on `null` to hide gracefully. Never throw.
4. **Hardcoded `WIX_GIFT_CARDS_APP_ID`** — `d80111c5-a0f4-47a8-b63a-65b54d774a27`. Captured from a real Wix-Editor order; not in the public registry. Export it as a named constant with a provenance comment so future maintainers can find the source.
5. **`wixGiftCardsAppNewCatalog: true`** in the cart `options` is mandatory — without it, the cart line item type is wrong and `ORDER_PAID` won't trigger gift-card issuance.
6. **No HTML comments in `.astro` frontmatter** — frontmatter is TypeScript; use `//` or `/* */`. (Not relevant to this scope's `.ts`/`.tsx` files but mentioned because gift-cards.ts is imported into `.astro` frontmatter elsewhere.)

## Template files

This scope uses **template files** instead of inline code. For each file below:

1. Read the template from `<Agent location>/templates/<filename>`
2. Write it to the project at the target path
3. Adapt CSS class names if the design tokens map them differently than the defaults

Do NOT modify logic, imports, or component structure.

## Implementation

### 1. `src/utils/gift-cards.ts`

Use template `templates/gift-cards.ts`.

Exports:
- `WIX_GIFT_CARDS_APP_ID` — string constant.
- `GiftCardImage`, `GiftCardPresetVariant`, `GiftCardProduct` — TypeScript interfaces.
- `getGiftCardProduct(): Promise<GiftCardProduct | null>` — memoized probe. Returns the first gift-card product or null on any failure.

The probe uses `httpClient.fetchWithAuth(ENDPOINT, { method: "POST", body: JSON.stringify({ query: { paging: { limit: 1 } } }) })`.

### 2. `src/components/GiftCardPurchase.tsx`

Use template `templates/GiftCardPurchase.tsx`.

Props: `{ product: GiftCardProduct }`.

State machine: `"idle" | "adding" | "added" | "error"`. Submit handler:
1. Validate selected `variantId`, `recipientFirstName`, `recipientEmail` (regex).
2. Call `currentCart.addToCurrentCart` with the catalogReference shape from gift-cards.md ("Wix Gift Card app reference data" section).
3. Dispatch `cart-updated` CustomEvent (so CartBadge updates).
4. `trackEvent("AddToCart", { … })` — fire-and-forget; same pattern as stores.
5. `window.location.href = "/cart"` on success.

Class names from contract:
- `.gift-card-form`, `.gift-card-fieldset`, `.gift-card-amounts`, `.gift-card-grid`, `.gift-card-field`, `.gift-card-field-wide`, `.gift-card-counter`, `.gift-card-error` — defined in `components-gift-cards.css`.
- `.option-label`, `.option-pill`, `.option-pill.selected` — shared across packs (also used by stores `ProductPurchase`).
- `.add-to-cart-btn` — shared with stores AddToCartButton; same brand styling.

### 3. `src/styles/components-gift-cards.css`

Use template `templates/components-gift-cards.css`.

Scoped styles for:
- Buy-form layout (grid, fields, counter, error message).
- `/gift-cards` page sections (`.gift-card-page`, `.gift-card-grid-wrap`, `.gift-card-hero-image`, `.gift-card-body`, `.gift-card-lede`, `.gift-card-fineprint`).
- Home teaser (`.gift-card-teaser`, `.gift-card-teaser-link`, `.gift-card-teaser-image`, `.gift-card-teaser-body`, `.gift-card-teaser-lede`).

The page-section and teaser styles live here (not inside the .astro `<style>` blocks) so the same separation as `components-stores.css` / `components-ecom.css` holds. The pages-scope agent imports this stylesheet via `Layout.astro`'s existing CSS chain (designer foundation already wires up the `components-*.css` import).

Use brand `@theme` utilities (`bg-cream`, `text-ink`, etc.) where natural; fall back to `var(--color-*)` / `var(--spacing-*)` directly when a property isn't covered. Do not introduce new design-token names.

## Return format

```json
{
  "status": "complete",
  "phase": "gift-cards-components",
  "scope": "components",
  "summary": "Wrote runtime probe util, GiftCardPurchase island, and scoped gift-cards CSS",
  "data": {
    "utils": ["gift-cards.ts"],
    "islands": ["GiftCardPurchase.tsx"],
    "scopedCssFile": "src/styles/components-gift-cards.css",
    "globalContractClassesReferenced": ["addToCartButton"],
    "scopedContractClassesReferenced": ["optionLabel", "optionPill"]
  },
  "files": [
    "src/utils/gift-cards.ts",
    "src/components/GiftCardPurchase.tsx",
    "src/styles/components-gift-cards.css"
  ],
  "errors": []
}
```

## Anti-patterns

| WRONG | CORRECT |
|-------|---------|
| Use `@wix/auto_sdk_ecom_gift-vouchers` to query the buy template | That SDK only exposes redemption — use `httpClient.fetchWithAuth` against the REST endpoint |
| Wrap `getGiftCardProduct()` in `auth.elevate(...)` | Visitor-scope is correct; elevation breaks the probe |
| Throw or log+rethrow on probe failure | Return `null`; callers gate the UI on null |
| Hardcode denomination amounts (€10, €25, etc.) | Always render from `product.presetVariants` |
| Skip `wixGiftCardsAppNewCatalog: true` in cart options | Required — without it the cart line is the wrong item type and `ORDER_PAID` does not issue a gift card |
| Write your own `wix-image.ts` / `analytics.ts` | Import from the shared utilities |