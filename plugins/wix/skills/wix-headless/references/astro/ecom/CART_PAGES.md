# Phase 4 Cart Pages — Ecom

Scope: `ecom-pages`. Launched in **Step 7**. Mounts `CartView` island on the cart page, wires the thank-you page, and mounts `CartBadge` in Navigation.

## Scope

Files this agent OWNS (rewrites from designer output):

- `src/pages/cart.astro` — mount `CartView.tsx` (client-only, no server-side cart fetch)
- `src/pages/thank-you.astro` — read `orderId` from URL, fire `Purchase` event

Files this agent PATCHES (does NOT rewrite):

- `src/components/Navigation.astro` — mount `CartBadge` in the `nav-actions` area

Files this agent MUST NOT touch:
- `src/components/CartView.tsx` — owned by `ecom-shared` (already written)
- `src/components/CartBadge.tsx` — owned by `ecom-shared`
- Any product page, home page, or stores-specific component
- `global.css`, any designed component

## Critical rules

1. **No server-side cart fetch** — cart is per-visitor and must not break SSR caching. `CartView` fetches its own data on mount.
2. **Mount `CartView` with `client:load`** — no props needed, the island is self-contained.
3. **Fire `Purchase` event in `thank-you.astro`** only when `?orderId=` is present.
4. **Mount `CartBadge` in `Navigation.astro`** (not Layout.astro, not a page-specific header).
5. **No HTML comments in `.astro` frontmatter** — frontmatter is TypeScript.
6. **Preserve designer layout and classes.** Only mount islands and wire data; do not restructure markup.
7. **Do NOT add static HTML alongside `<CartView>`** — the island handles empty/loading/cart states internally.

## Implementation

### 1. `src/pages/cart.astro`

Use template `templates/cart.astro`.

Mounts `CartView` as a client-only island. **No server-side cart fetch** — cart data is per-visitor and would break SSR caching. CartView fetches the cart client-side on mount. Key requirements:

- **No `currentCart` import in frontmatter** — do not fetch cart data server-side
- Mount `<CartView client:load />` — no props needed, the island fetches its own data
- Preserve whatever the designer wrote around the mount (headings, breadcrumbs, section wrappers)
- Do NOT add static HTML alongside `<CartView>` — the island handles empty/loading/cart states internally

### 2. `src/pages/thank-you.astro`

Use template `templates/thank-you.astro`.

Wix redirects here after successful checkout with `?orderId=<id>`. Fires `Purchase` analytics event when orderId is present. Preserve whatever the designer wrote around the order confirmation content (headings, layout wrappers). The key requirements:

- Read `orderId` from URL search params
- Display order confirmation with the orderId
- Fire `Purchase` event via the analytics helper (client-side script)
- Only fire when `orderId` is present — refreshing without it should not re-fire

### 3. Mount CartBadge in `Navigation.astro`

Mount `CartBadge` inside the `nav-actions` area. The designer creates this with a `<slot name="actions" />` or similar placeholder. Because Navigation is in the shared Layout, the badge appears on every page.

```astro
---
// Add to Navigation.astro frontmatter:
import CartBadge from "./CartBadge.tsx";
---

<!-- Replace the nav-actions slot with the CartBadge island: -->
<div class="nav-actions">
  <CartBadge client:only="react" />
</div>
```

Use `client:only="react"` — never SSR the badge. SSR would render `count: 0` (sessionStorage is a browser-only API), then hydration would read the cached count and flip to the real number, causing a visible blink on every page navigation. Skipping SSR means the badge renders once on the client with the cached count already populated. No flash.

## Checkout flow summary

CartView's `handleCheckout` runs:

```
Cart page → "Proceed to Checkout"
  → currentCart.createCheckoutFromCurrentCart({ channelType: WEB })
  → redirects.createRedirectSession({ ecomCheckout: { checkoutId }, callbacks: { thankYouPageUrl, cartPageUrl } })
  → window.location.href = redirectSession.fullUrl
  → User completes payment on Wix-hosted checkout
  → Redirect back to /thank-you?orderId=<id>
```

**Going-live note** (emitted by the skill, not this agent):
> Checkout is hosted by Wix and will show "we aren't accepting payments" until: (1) upgrade to premium eCommerce plan, (2) connect a payment provider.

## Analytics fired from this scope

| Event | Fires from | When | Payload |
|-------|------------|------|---------|
| `Purchase` | `thank-you.astro` | On mount when `?orderId=` is present | `{ id: orderId, origin: "Thank You Page" }` |

`RemoveFromCart` and `InitiateCheckout` fire from `CartView.tsx` (owned by `ecom-shared`).

## Return format

```json
{
  "status": "complete",
  "phase": "ecom-pages",
  "scope": "ecom-pages",
  "summary": "Mounted CartView (client-only fetch); wired Purchase event; mounted CartBadge in Navigation",
  "data": {
    "pagesWired": 2,
    "cartViewMounted": true,
    "purchaseEventWired": true,
    "cartBadgeMounted": true,
    "analyticsEvents": ["Purchase"]
  },
  "files": [
    "src/pages/cart.astro",
    "src/pages/thank-you.astro",
    "src/components/Navigation.astro"
  ],
  "errors": []
}
```