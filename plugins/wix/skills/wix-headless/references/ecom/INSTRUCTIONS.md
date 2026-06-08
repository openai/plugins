---
name: ecom-implementer
description: "Implements vertical-agnostic ecommerce — cart page, checkout redirect, thank-you page, cart badge. Scopes: components, components-css, pages. Extends references/shared/IMPLEMENTER.md."
---

# Ecom Implementer

Extends `references/shared/IMPLEMENTER.md`. Read that file first for phase routing, REST auth + doc lookups, prompt-inlined inputs (no site.json reads), return contract, style conventions, and common failure modes.

## Scope routing

| Scope | Phase | Reference |
|-------|-------|-----------|
| `components` | Components (CartView, CartBadge — TSX only, **no CSS**) — `src/utils/discounts.ts` is pre-copied by the orchestrator | `../astro/ecom/CART_WIRING.md` |
| ~~`components-css`~~ | **Do not dispatch.** `src/styles/components-ecom.css` is copied from `<SKILL_ROOT>/references/astro/templates/ecom/components-ecom.css` by the orchestrator's pre-Step-4.5 batch (see BUILD.md § Step 4.5). The template uses direct `var(--token)` CSS, so it works against any designer-published vocabulary without per-run rewrites. `COMPONENTS_CSS.md` documents that CSS for reference — there is no `components-css` subagent to dispatch. | — |
| `pages` | Pages (cart.astro, thank-you.astro, Navigation CartBadge mount) | `../astro/ecom/CART_PAGES.md` |

> **Why `components` is split.** A single agent writing the .tsx islands plus the scoped CSS was Phase 3's critical path on the most recent run (204 s for ecom alone). The CSS file has no runtime coupling to the TSX components — it's referenced only by class name at build time — so it splits cleanly into a sibling agent that runs in the same dispatch batch. Mirrors the stores split. See `../astro/ecom/COMPONENTS_CSS.md` § "What this scope owns".

Note: `ecom` is never triggered independently — it's co-loaded by verticals that require it (`stores` today; `bookings`, `events` in the future). No `seed` scope — ecom has no data of its own; it works off line items from whichever catalog app is installed.

## Files this vertical creates / contributes

See `<SKILL_ROOT>/references/verticals/ecom.md` frontmatter.

## Templates

Components (`components` scope — TSX only):
- `<SKILL_ROOT>/references/astro/templates/ecom/CartView.tsx`
- `<SKILL_ROOT>/references/astro/templates/ecom/CartBadge.tsx`

Components CSS (`components-css` scope — scoped CSS only):
- `<SKILL_ROOT>/references/astro/templates/ecom/components-ecom.css`

### Pre-copied by the orchestrator (do NOT write this yourself)

- `src/utils/discounts.ts` — pre-copied from `<SKILL_ROOT>/references/astro/templates/ecom/discounts.ts` BEFORE your `components` scope dispatches. Wix Ecom Discount Rules fetch + per-product match utility; consumers are stores `pages-products` / `pages-home-and-nav` (ProductCard ribbon + product-detail offer callout). Uses `auth.elevate()` from `@wix/essentials` — `discountRules.queryDiscountRules` requires `ECOM.DISCOUNT_RULES_READ`, a visitor client returns empty silently without elevation.

  Just import from this path; never rewrite the file. Regenerating it has shipped a no-op stub that satisfied the manifest but caused the discount ribbon to silently never render. The pre-copy makes that regression structurally impossible.

## CSS ownership — ecom pack

Ecom-specific component CSS lives in `src/styles/components-ecom.css` (written by your `components` scope), NOT in the designer's `global.css`. The classes you own:

- `.cart-summary` — the bordered/sticky summary panel on `/cart`. Compound bordered card; sticky on desktop.
- `.cart-total` — the row inside the summary that anchors the total amount with a top rule and display-serif typography.
- `.cart-empty` — the centered empty-state on `/cart` when the cart is empty. Includes the inline override of `.checkout-btn` so the "Browse Products" CTA isn't a full-width brick.
- `.checkout-btn` — primary checkout button with `:disabled` and `:hover:not(:disabled)` states. Composes from `.btn-primary` (which IS designer-owned in `global.css`).
- `.cart-item-*` — row, image, name, qty controls — all live here. Most are utility-only; the few that need scoped rules (e.g. line-item separator borders) belong here, not in `global.css`.

The designer's `global.css` declares only tokens, the `.btn` family, decorative slots, the editorial-rule, and the site-shell shells. If `global.css` ships with a partial rule for any class above, that's a designer bug — flag it in your return JSON's `errors` array (`{code: "GLOBAL_CSS_LEAK", class: "<name>"}`) and override with the complete rule in `components-ecom.css`.

See `references/shared/STYLING.md` § "Component-specific CSS is owned by the component, not the designer" for the boundary rule.

## Cross-vertical event contract

`cart-updated` CustomEvent on `window`:
- **Dispatchers:** `AddToCartButton` (stores), `CartView` (ecom)
- **Listener:** `CartBadge` (ecom)