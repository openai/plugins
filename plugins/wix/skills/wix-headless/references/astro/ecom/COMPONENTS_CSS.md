# Phase 3 Components-CSS — Ecom

Sibling of the `components` scope. Launched in **Step 4.5** in the same concurrent batch — runs in parallel with the TSX work, stores components, gift-cards components, and Image Phase 2.

## What this scope owns

Exactly one file:

- `src/styles/components-ecom.css` — scoped CSS for cart/checkout: cart-summary panel, cart-total row, checkout button (with `:disabled` and `:hover` states), empty state, cart-item line layout (image, name, qty controls, prices, modifiers, unavailable state, remove button), discount/applied-discount rows, and the cart-badge nav element. Imported by `Layout.astro` (the designer foundation sets up the import).

## What this scope does NOT own

- Any `.tsx` or `.astro` file. Those are the `components` sibling scope (`./CART_WIRING.md`).
- `src/styles/global.css` — owned by the designer foundation. **You read it (to audit for ecom-class leaks) but never write it.**
- `src/styles/components-stores.css`, `src/styles/components-gift-cards.css` — owned by other packs' `components-css` (or `components`) scopes.
- `src/utils/discounts.ts` — pre-copied by the orchestrator before this dispatch; not your concern.

## Reading set

You only need:

1. **`<SKILL_ROOT>/references/astro/templates/ecom/components-ecom.css`** — the canonical template. Read it once.
2. **`<SKILL_ROOT>/references/shared/STYLING.md`** — the styling-contract conventions (how to use `@apply`, the `@theme` token utilities, the no-default-Tailwind-colors rule, and the global-vs-scoped CSS ownership boundary).
3. **`<SKILL_ROOT>/references/shared/RETURN_CONTRACT.md`** — the return JSON shape.
4. **`src/styles/global.css`** in the project — read to audit for ecom-class leaks (see § "Global-CSS leak audit" below).
5. **Design tokens (inline in your prompt)** — the parent skill pastes the full `designTokens` JSON into your dispatch prompt. Use it directly; do NOT read `.wix/design-tokens.css` or `.wix/site.d.ts` from disk.

You do NOT need to read `INSTRUCTIONS.md`, `CART_WIRING.md`, the TSX templates, the `discounts.ts` util, or any other reference. Skipping those reads is the point of the split.

## Implementation

### 1. Read the template

```
<SKILL_ROOT>/references/astro/templates/ecom/components-ecom.css
```

This is the canonical scoped CSS for the ecom pack. Adapt sizing/spacing to the brand's aesthetic — use the design tokens from your prompt (`--color-bark`, `--color-cream`, `--spacing-md`, `--font-display`, etc.). **Do not rename the class names or state modifiers** — they must match the contract keys the TSX components reference.

### 2. The two `@reference` directives are mandatory

The first two non-comment lines of `components-ecom.css` MUST be:

```css
@reference "tailwindcss";
@reference "./global.css";
```

Without these, Tailwind v4 fails the build with `"Cannot apply unknown utility class"` on any `@apply` rule that uses a utility like `size-6` or `gap-md`. The template ships them; do not remove.

### 3. Class ownership

Classes defined in `components-ecom.css` (this is the **single source of truth** — the designer's `global.css` does NOT publish these):

- **`.cart-summary` / `.cart-total` / `.cart-empty`** — the `/cart` page summary panel (sticky on desktop), total row, and empty-state. The `.cart-empty .checkout-btn` rule scopes the empty-state CTA to inline-flex with a max-width so it doesn't render full-width.
- **`.checkout-btn`** — primary checkout button, with `:disabled` and `:hover:not(:disabled)` states. **Composes from `.btn-primary`** (which IS a designer-owned plain-CSS rule in `global.css`). Do **NOT** use `@apply btn-primary` here — Tailwind v4 only `@apply`s utilities declared with `@utility` (which `btn` is in `global.css`), not plain custom classes. The build fails with `Cannot apply unknown utility class 'btn-primary'` if you try. Use `composes` via flat property repetition or extend manually.
- **`.cart-item-*`** — full row primitives: `cart-item-qty`, `qty-btn`, `qty-value`, `cart-item-unavailable`, `cart-item-actions`, `cart-item-prices`, `cart-item-full-price`, `cart-item-unit-price`, `cart-item-line-total`, `cart-item-remove`, `cart-item-image-link`, `cart-item-name-link`, `cart-item-option`, `cart-item-modifiers`. CartView.tsx references these by name; renaming breaks the page.
- **`.cart-discount` / `.cart-discount-name` / `.cart-discount-amount`** — the discount row in the summary.
- **`.cart-applied-discounts` / `.cart-applied-discounts-name`** — the name-only applied-discounts row (line-item automatic discounts).
- **`.cart-badge` / `.cart-badge-count`** — the nav badge (mounted in `Navigation.astro` via the ecom `pages` scope's CartBadge).

Classes you do NOT own:

- `.btn`, `.btn-primary`, `.btn-secondary` — designer's `global.css` (`.btn` is a Tailwind v4 `@utility`).
- Anything in `components-stores.css` (option pills, product card, product grid, offer callout) — owned by stores pack.
- Anything in `components-gift-cards.css` — owned by gift-cards pack.

### 4. Global-CSS leak audit

Before writing your file, **read `src/styles/global.css`** and grep for any class your scope owns. Ecom-specific rules sometimes leak into the designer's foundation:

- Any `.cart-summary`, `.cart-total`, `.cart-empty`, `.checkout-btn` rule.
- Any `.cart-item-*` rule.
- Any `.cart-badge` rule.
- Any `.cart-discount` / `.cart-applied-discounts` rule.

If you find a leak, do NOT edit `global.css` (the designer owns it). Instead:

1. Override the rule with the complete declaration in `components-ecom.css` (later imports win in CSS cascade because Layout.astro imports `components-ecom.css` AFTER `global.css`).
2. Add `{code: "GLOBAL_CSS_LEAK", class: "<name>", file: "src/styles/global.css"}` to your return JSON's `errors` array — non-fatal but tracked.

### 5. Write the file

Write the adapted CSS to `src/styles/components-ecom.css`. The orchestrator's post-Phase-3 manifest check verifies the file exists.

## Coordination: design tokens

Your parent prompt includes the design tokens JSON inline. Use it directly — do **not** read `.wix/design-tokens.css` or `.wix/site.d.ts` from disk and do not poll for them.

## Return format

```json
{
  "status": "complete",
  "phase": "ecom-components-css",
  "scope": "components-css",
  "summary": "Wrote components-ecom.css from template, adapted to brand tokens",
  "data": {
    "scopedCssFile": "src/styles/components-ecom.css",
    "scopedCssRules": 22,
    "scopedContractClassesDefined": [
      "cart-summary", "cart-total", "cart-empty", "checkout-btn",
      "cart-item-qty", "qty-btn", "qty-value", "cart-item-unavailable",
      "cart-item-actions", "cart-item-prices", "cart-item-full-price",
      "cart-item-unit-price", "cart-item-line-total", "cart-item-remove",
      "cart-item-image-link", "cart-item-name-link",
      "cart-item-option", "cart-item-modifiers",
      "cart-discount", "cart-discount-name", "cart-discount-amount",
      "cart-applied-discounts", "cart-applied-discounts-name",
      "cart-badge", "cart-badge-count"
    ]
  },
  "files": [
    "src/styles/components-ecom.css"
  ],
  "errors": []
}
```

If a leak was found and overridden, include `errors: [{code: "GLOBAL_CSS_LEAK", class: "<name>", file: "src/styles/global.css"}]`.

## Anti-patterns

| WRONG | CORRECT |
|-------|---------|
| Read `INSTRUCTIONS.md`, `CART_WIRING.md`, or any `.tsx` template | Not needed — this scope only writes CSS |
| Edit `src/styles/global.css` to fix a leak | Override in `components-ecom.css`; report the leak in `errors` |
| Use default Tailwind colors (`bg-green-50`, `text-red-600`) | Brand `@theme` utilities (`bg-bark`, `text-cream`) or `var(--color-...)` |
| `@apply btn-primary` on `.checkout-btn` | Tailwind v4 only `@apply`s `@utility` declarations, not plain CSS rules — build fails. Either repeat the properties manually or compose via `composes` |
| Rename a class because the brand is "more elegant" with kebab variants | Class names are contract keys; renaming breaks every TSX import that references them |
| Skip the leak audit | Skipping ships double-defined rules; the audit is < 5 s and prevents downstream visual regressions |
| Drop the `@reference` directives | Tailwind v4 needs both — without them, `@apply size-6` and similar fail at build |