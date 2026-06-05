# Phase 3 Components-CSS — Stores

Sibling of the `components` scope. Launched in **Step 4.5** in the same concurrent batch — runs in parallel with the TSX/Astro work, ecom and gift-cards components, and Image Phase 2.

## What this scope owns

Exactly one file:

- `src/styles/components-stores.css` — scoped CSS for stores-specific contract keys (option pills, quantity stepper, stock status, modifier free-text input, product card, product grid, offer callout panel). Imported by `Layout.astro` (the designer foundation sets up the import).

## What this scope does NOT own

- Any `.tsx` or `.astro` file. Those are the `components` sibling scope (`./SHARED_WIRING.md`).
- `src/styles/global.css` — owned by the designer foundation. **You read it (to audit for stores-class leaks) but never write it.**
- `src/styles/components-ecom.css`, `src/styles/components-gift-cards.css` — owned by other packs' `components` (or `components-css`) scopes.
- `src/utils/back-in-stock.ts` — pre-copied by the orchestrator before this dispatch; not your concern.

## Reading set

You only need:

1. **`<SKILL_ROOT>/references/astro/templates/stores/components-stores.css`** — the canonical template. Read it once.
2. **`<SKILL_ROOT>/references/shared/STYLING.md`** — the styling-contract conventions (how to use `@apply`, the `@theme` token utilities, the no-default-Tailwind-colors rule, and the global-vs-scoped CSS ownership boundary).
3. **`<SKILL_ROOT>/references/shared/RETURN_CONTRACT.md`** — the return JSON shape.
4. **`src/styles/global.css`** in the project — read to audit for stores-class leaks (see § "Global-CSS leak audit" below).
5. **Design tokens (inline in your prompt)** — the parent skill pastes the full `designTokens` JSON into your dispatch prompt. Use it directly; do NOT read `.wix/design-tokens.css` or `.wix/site.d.ts` from disk.

You do NOT need to read `INSTRUCTIONS.md`, `SHARED_WIRING.md`, `BACK_IN_STOCK.md`, the TSX templates, the back-in-stock util, or any other reference. Skipping those reads is the point of the split — they would consume tokens for context this scope doesn't use.

## Implementation

### 1. Read the template

```
<SKILL_ROOT>/references/astro/templates/stores/components-stores.css
```

This is the canonical scoped CSS for the stores pack. Adapt sizing/spacing to the brand's aesthetic — use the design tokens from your prompt (`--color-bark`, `--color-cream`, `--spacing-md`, `--font-display`, etc.). **Do not rename the class names or state modifiers** — they must match the contract keys the TSX components reference.

### 2. Use `@apply` with brand `@theme` utilities

The `@theme` block in `global.css` (written by the designer foundation) exposes the brand tokens as Tailwind utilities (e.g., `bg-bark`, `text-cream`, `font-body`). They are globally available because `global.css` is imported first in `Layout.astro`.

Use `@apply` for color, font, and spacing properties. Drop to `var(--color-bark)` directly when `@apply` doesn't cover a property (e.g., border-color via custom property).

Do **NOT** use default Tailwind colors (`bg-green-50`, `text-red-600`). The brand palette is the only allowed source.

### 3. Class ownership

Classes you own (define rules in `components-stores.css`):

- **`.product-card`, `.product-card-media`, `.product-card-ribbon`, `.product-card-index`** — the product card itself, including the `overflow: hidden` + `border-radius` clipping context. Whoever writes the `border-radius` here also writes any inner padding required to keep child content inside the rounded edges. Without inner padding, a price `<p>` sits flush against the rounded bottom corner and descenders get clipped. Add `padding-bottom: var(--spacing-md)` on the card plus horizontal padding on each text block when you set the radius.
- **`.product-grid`** — the layout that lists product cards. Both `/products` (pages-products scope) and `/category/[slug]` (pages-categories scope) consume it from one place. Include `display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--spacing-xl);` plus the View-Transitions opacity fade for in-flight navigations.
- **`.offer-callout` family (`.offer-callout`, `-item`, `-badge`, `-name`, `-detail`, `-foot`)** — discount panel rendered above `<ProductPurchase>` on `/products/[slug]`.
- **Option-selector contract classes** — `option-group`, `option-label`, `option-choices`, `option-pill` (with `.selected` state modifier).
- **Quantity-stepper contract classes** — `quantity-selector`, `quantity-btn`, `quantity-value`.
- **Stock status** — `stock-status`.
- **Back-in-stock form** (`.back-in-stock-form` and child classes) — append the rules from `./BACK_IN_STOCK.md` § 3 to the end of `components-stores.css`. The TSX form island is written by the `components` sibling; this file owns its styling.

Classes you do NOT own:

- `.btn`, `.btn-primary`, `.btn-secondary` — designer's `global.css`.
- `addToCartButton` → `.add-to-cart-btn` — designer's `global.css` (it's a global contract key).
- `productPurchase` → `.product-purchase` outer wrapper — designer's `global.css`.
- Anything in `components-ecom.css` (CartBadge, CartView, CartLine) — owned by ecom pack.

The boundary: **rules referenced by exactly one pack's TSX live in that pack's scoped CSS; rules referenced by every page (buttons, links, type) live in the designer's `global.css`.**

### 4. Global-CSS leak audit

Before writing your file, **read `src/styles/global.css`** and grep for any class your scope owns. Stores-specific rules sometimes leak into the designer's foundation:

- `.product-grid` and `body[data-navigating="true"] .product-grid` — designer drift; should be in `components-stores.css`, not `global.css`.
- Any `.product-card-*` rule.
- Any `.offer-callout-*` rule.
- Any contract class that maps to a key in `contractKeys.scoped.stores`.

If you find a leak, do NOT edit `global.css` (the designer owns it). Instead:

1. Override the rule with the complete declaration in `components-stores.css` (later imports win in CSS cascade because Layout.astro imports `components-stores.css` AFTER `global.css`).
2. Add `{code: "GLOBAL_CSS_LEAK", class: "<name>", file: "src/styles/global.css"}` to your return JSON's `errors` array — non-fatal but tracked.

### 5. Write the file

Write the adapted CSS to `src/styles/components-stores.css`. The first line must be `@reference "./global.css";` so Tailwind's `@apply` resolves the `@theme` utilities. The orchestrator's post-Phase-3 manifest check verifies the file exists; it does not verify the `@reference` line.

## Coordination: design tokens

Your parent prompt includes the design tokens JSON inline. Use it directly — do **not** read `.wix/design-tokens.css` or `.wix/site.d.ts` from disk and do not poll for them.

## Return format

```json
{
  "status": "complete",
  "phase": "stores-components-css",
  "scope": "components-css",
  "summary": "Wrote components-stores.css from template, adapted to brand tokens",
  "data": {
    "scopedCssFile": "src/styles/components-stores.css",
    "scopedCssRules": 18,
    "scopedContractClassesDefined": [
      "option-group", "option-label", "option-choices", "option-pill",
      "quantity-selector", "quantity-btn", "quantity-value",
      "stock-status",
      "product-card", "product-card-media", "product-card-ribbon", "product-card-index",
      "product-grid",
      "offer-callout", "offer-callout-item", "offer-callout-badge", "offer-callout-name", "offer-callout-detail", "offer-callout-foot"
    ]
  },
  "files": [
    "src/styles/components-stores.css"
  ],
  "errors": []
}
```

If a leak was found and overridden, include `errors: [{code: "GLOBAL_CSS_LEAK", class: "<name>", file: "src/styles/global.css"}]`.

## Anti-patterns

| WRONG | CORRECT |
|-------|---------|
| Read `INSTRUCTIONS.md`, `SHARED_WIRING.md`, or any `.tsx` template | Not needed — this scope only writes CSS |
| Edit `src/styles/global.css` to fix a leak | Override in `components-stores.css`; report the leak in `errors` |
| Use default Tailwind colors (`bg-green-50`, `text-red-600`) | Brand `@theme` utilities (`bg-bark`, `text-cream`) or `var(--color-...)` |
| Write rules for `.add-to-cart-btn` here | That's a global contract class — owned by the designer's `global.css` |
| Rename a class because the brand is "more elegant" with kebab-cased variants | Class names are contract keys; renaming breaks every TSX import that references them |
| Skip the leak audit | Skipping ships double-defined rules; the audit is < 5 s and prevents downstream visual regressions |