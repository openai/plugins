---
name: gift-cards-implementer
description: "Implements the passive Wix Gift Cards vertical — runtime probe util, GiftCardPurchase island, /gift-cards page, and conditional nav/home contributions. Scopes: components, pages. Extends references/shared/IMPLEMENTER.md."
---

# Gift Cards Implementer

Extends `references/shared/IMPLEMENTER.md`. Read that file first for phase routing, REST auth + doc lookups, prompt-inlined inputs (no site.json reads), return contract, style conventions, and common failure modes.

## Scope routing

| Scope | Phase | Reference |
|-------|-------|-----------|
| `components` | Components (probe util, React island, scoped CSS) | `../astro/gift-cards/COMPONENTS.md` |
| `pages` | Pages (gift-cards landing + Navigation/index patches) | `../astro/gift-cards/PAGES.md` |

This pack has **no `seed` scope** — the dashboard's eGift Card template is the source of truth and we never seed denominations from code.

## Files this vertical creates / contributes

See `<SKILL_ROOT>/references/verticals/gift-cards.md` frontmatter (`creates:` and `contributes:` blocks).

## Pre-return file-existence assertion (pages scope)

Before returning `status: "complete"` from the `pages` scope, verify every file in `creates:` (phase: pages) plus the patched files in `contributes:` exists on disk. If a declared file is missing, return `status: "partial"` with `errors: [{ code: "PHASE4_FILE_MISSING", path: "<expected path>" }]` rather than claiming success.

## Templates

Canonical templates live at `<SKILL_ROOT>/references/astro/templates/gift-cards/`. Your `components` and `pages` scopes read these and adapt them — don't invent markup or logic.

Components (`components` scope):
- `<SKILL_ROOT>/references/astro/templates/gift-cards/gift-cards.ts`
- `<SKILL_ROOT>/references/astro/templates/gift-cards/GiftCardPurchase.tsx`
- `<SKILL_ROOT>/references/astro/templates/gift-cards/components-gift-cards.css`

Pages (`pages` scope):
- `<SKILL_ROOT>/references/astro/templates/gift-cards/gift-cards.astro`
- `<SKILL_ROOT>/references/astro/templates/gift-cards/_nav-snippet.astro` — exact contribution to insert at `<!-- nav:links -->` in `Navigation.astro`
- `<SKILL_ROOT>/references/astro/templates/gift-cards/_home-teaser-snippet.astro` — exact contribution to insert at `<!-- home:gift-cards -->` in `index.astro`

## Gift-cards-specific failure modes

| Wrong | Right |
|---|---|
| Hardcode denominations in code | Always read `presetVariants` from the live API (`getGiftCardProduct()`) |
| Call `createGiftCardProduct` or any seeding op | Never seed; the dashboard owns the template |
| Wrap calls in `auth.elevate(...)` | The probe is visitor-scoped already; elevation breaks it |
| Forget to import `getGiftCardProduct` when patching `Navigation.astro` or `index.astro` | When inserting at a marker, also add the corresponding import + frontmatter call to that file |
| Drop or rename the marker comment after inserting | Preserve the marker line — future re-runs and other verticals depend on it |
| Render the page when probe returns `null` | Redirect to `/` (`Astro.redirect("/", 302)`) so users following stale links never see a broken page |
| Skip memoization of `getGiftCardProduct()` | Module-level cache promise — Navigation, home, and page render in the same request and must coalesce to one fetch |