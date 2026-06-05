# Phase 3 Components — Back in Stock (Stores)

Split across the stores `components` scope (TSX/util files) and the `components-css` sibling (CSS rules). The matching Phase 4 wiring lives in `PRODUCT_PAGES.md` (SSR probe import + new props on `<ProductPurchase>`).

## Scope

Files written for back-in-stock, by scope:

**`components` scope** (see `./SHARED_WIRING.md`):
- `src/utils/back-in-stock.ts` — SSR-elevated probe of the Wix back-in-stock service, plus the canonical Stores app id constant
- `src/components/BackInStockForm.tsx` — React island that posts via `@wix/ecom`'s `backInStockNotifications.createBackInStockNotificationRequest`

**`components-css` scope** (see `./COMPONENTS_CSS.md`):
- `src/styles/components-stores.css` — appends the back-in-stock form CSS rules at the end of the file (see § 3 below)

This file is read by both scopes. Sections covering the SDK / probe / form island are for the `components` scope; § 3 (CSS append) is for the `components-css` scope.

## Critical rules

These come from live trials on Catalog-V3 sites. Encode them verbatim — none of them are in the public docs.

1. **Two app ids — pick the right one.**
   - The Wix Stores **install** app id is `215238eb-22a5-4c36-9e7b-e7c08025e04e` (used in `catalogReference.appId` for cart adds, app install, `Phase 1`).
   - The Wix Stores **back-in-stock** app id is `1380b703-ce81-ff05-f115-39571d94dfcd` (the Stores sub-page registration id).
   - The back-in-stock service rejects `215238eb-…` (`428 NOT_SUPPORTED_APP_DEF_ID` on `start-collecting`, `428 REQUEST_COLLECTION_DISABLED` on the create endpoint) and accepts `1380b703-…`. Both are correct in their own contexts; do not unify them.

2. **Bare-fields rule for the SDK subscribe call.** `backInStockNotifications.createBackInStockNotificationRequest(request, itemDetails)` throws an opaque `TypeError: Failed to construct 'URL': Invalid URL` when the optional `request.itemUrl` or `itemDetails.image` fields are present, even with browser-valid URLs. Send only the four required fields: `catalogReference`, `email`, `name`, `price`. The notification email and the dashboard view both work without them.

3. **Numeric price only.** `itemDetails.price` must be a numeric string (e.g. `"385"`). Currency-formatted strings (`"$385"`) fail with `400 DECIMAL_GTE`. The `normalizePrice` helper in the form template strips `$`/`,` and falls back to `"0"`.

4. **Visitor scope from the client; SSR-only elevation for the probe.**
   - The form's subscribe call uses `@wix/ecom` straight from the React island — no `auth.elevate`, no Astro API route. The visitor token is enough.
   - The settings probe uses `auth.elevate(httpClient.fetchWithAuth)` because `getSettings` requires Manage Stores. Run it in `[slug].astro` frontmatter, **never from the client**.
   - Do NOT invent an Astro `src/pages/api/...` POST route. The `@wix/cloud-provider-fetch-adapter` that ships with the scaffold returned 403 to the browser on app-defined POST routes during the trial. Stay on the SDK.

5. **Module-memoize the probe.** `getBackInStockEnabled()` holds one in-flight `Promise<boolean>` at module scope so multiple SSR awaits in the same request coalesce. Same pattern as `gift-cards.ts`'s `getGiftCardProduct()`.

## Template files

This scope uses **template files** instead of inline code. For each file below:

1. Read the template from `<Agent location>/templates/<path>`
2. Write it to the project at the target path
3. Adapt CSS class names if the design tokens map them differently

Do NOT modify logic, imports, the bare-fields request shape, or the app-id constants.

### 1. `src/utils/back-in-stock.ts`

Use template `templates/back-in-stock.ts`.

Exports:
- `WIX_STORES_BACK_IN_STOCK_APP_ID` — string constant. Use this for the `catalogReference.appId` in the form.
- `WIX_STORES_INSTALL_APP_ID` — string constant. Exported for completeness; unused by this file.
- `getBackInStockEnabled(): Promise<boolean>` — memoized SSR probe.
- `SETTINGS_URL` — the `getSettings` REST URL, exported in case future scopes need it.

The probe header comment block documents the app-id discrepancy in detail. Keep that block intact when copying — it's the only place the next maintainer will see the rationale.

### 2. `src/components/BackInStockForm.tsx`

Use template `templates/BackInStockForm.tsx`.

Props: `{ productId, variantId?, productName, productPrice: number | string, variantLabel? }`. The form accepts price as either a number or a numeric string and normalizes internally.

State machine: `idle → submitting → (success | error)` with `success` carrying an optional `alreadySubscribed` flag for the duplicate-detection branch (`BACK_IN_STOCK_NOTIFICATION_REQUEST_ALREADY_EXISTS` → "You're already on the list").

Class names:
- `.back-in-stock-form`, `.back-in-stock-headline`, `.back-in-stock-eyebrow`, `.back-in-stock-lede`, `.back-in-stock-label`, `.back-in-stock-row`, `.back-in-stock-input`, `.back-in-stock-submit`, `.back-in-stock-error`, `.back-in-stock-success`, `.back-in-stock-success-headline`, `.back-in-stock-success-detail` — defined in the CSS append below.

### 3. `src/styles/components-stores.css` — append

The `components-stores.css` template already covers options/quantity/modifiers/stock-status. Append the back-in-stock rules at the end. Use the existing pack token vocabulary (`bark`, `cream`, `parchment`, `ink`, `rule`) so the styling lands on every brand without per-site rewrites.

```css
/* --- Back-in-stock subscribe form (BackInStockForm.tsx) --- */
.back-in-stock-form {
  @apply flex flex-col gap-md mt-md p-lg border border-rule rounded;
  background-color: var(--color-cream);
}
.back-in-stock-headline {
  @apply flex flex-col gap-sm;
}
.back-in-stock-eyebrow {
  @apply font-heading text-xs uppercase tracking-wider text-bark/70;
}
.back-in-stock-lede {
  @apply font-body text-sm text-ink;
  line-height: 1.5;
}
.back-in-stock-label {
  @apply font-heading text-xs uppercase tracking-wider text-bark/70;
}
.back-in-stock-row {
  @apply flex flex-row flex-wrap gap-sm;
}
.back-in-stock-input {
  @apply flex-1 px-md py-sm font-body text-sm border border-rule rounded bg-parchment text-ink;
  min-width: 0;
  transition: border-color 0.15s ease;
}
.back-in-stock-input:focus {
  @apply outline-none border-ink;
}
.back-in-stock-input[aria-invalid="true"] {
  @apply border-rust;
}
.back-in-stock-submit {
  @apply px-lg py-sm font-heading text-xs uppercase tracking-wider bg-bark text-cream rounded cursor-pointer transition-colors;
  border: 1px solid var(--color-bark);
}
.back-in-stock-submit:hover:not(:disabled) {
  @apply bg-ink;
}
.back-in-stock-submit:disabled {
  @apply opacity-50 cursor-not-allowed;
}
.back-in-stock-error {
  @apply font-body text-sm text-rust;
}
.back-in-stock-success {
  @apply mt-md p-lg border border-rule rounded;
  background-color: var(--color-cream);
}
.back-in-stock-success-headline {
  @apply font-heading text-base text-ink;
  margin: 0 0 0.5rem 0;
}
.back-in-stock-success-detail {
  @apply font-body text-sm text-ink;
  line-height: 1.55;
  margin: 0;
}
.stock-status.back-in-stock-alt {
  @apply mt-sm font-body text-sm italic text-bark/70;
}
```

If the brand's design tokens don't include a `rust` (error) color, fall back to a neutral `text-ink` on the error state — the `aria-invalid` border still flags it visually.

## Return format

The full components scope return must mention back-in-stock:

```json
{
  "status": "complete",
  "phase": "stores-components",
  "scope": "components",
  "summary": "Wrote stores islands, scoped CSS, back-in-stock probe + form",
  "data": {
    "islands": ["ProductPurchase.tsx", "AddToCartButton.tsx", "BackInStockForm.tsx"],
    "utils": ["back-in-stock.ts"],
    "scopedCssFile": "src/styles/components-stores.css",
    "backInStockWired": true
  },
  "files": [
    "src/components/SeoTags.astro",
    "src/components/AddToCartButton.tsx",
    "src/components/ProductPurchase.tsx",
    "src/components/BackInStockForm.tsx",
    "src/utils/back-in-stock.ts",
    "src/styles/components-stores.css"
  ],
  "errors": []
}
```

## Anti-patterns

| WRONG | CORRECT |
|---|---|
| Use `215238eb-…` (Stores install id) as `catalogReference.appId` for back-in-stock | Use `WIX_STORES_BACK_IN_STOCK_APP_ID` (`1380b703-…`); the install id is rejected on V3 |
| Pass `itemUrl` or `image` to `createBackInStockNotificationRequest` | Send only `catalogReference`, `email`, `name`, numeric `price` — the SDK throws `Failed to construct 'URL': Invalid URL` on either optional field |
| Send `"$385"` as `price` | Numeric string `"385"` only; the API rejects formatted prices with `400 DECIMAL_GTE` |
| Wrap the subscribe call in `auth.elevate(...)` from the React island | Visitor scope is enough; elevation belongs only to the SSR probe |
| Add a custom `src/pages/api/back-in-stock-subscribe.ts` route | Not needed — SDK from the island works. The Wix cloud adapter returned 403 on app-defined POST routes during the trial. |
| Drop the module-memoization in `back-in-stock.ts` | Keep it; multiple SSR awaits in the same request coalesce into one `getSettings` call |