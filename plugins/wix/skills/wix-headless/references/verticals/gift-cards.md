---
name: gift-cards
description: "Conditional gift-card buy page + nav/home contributions. Detects the Wix Gift Card app at runtime; renders only when installed."
triggers: []   # never triggered independently — co-loaded by packs that include a storefront via `requires:`
requires: ["ecom"]   # buy flow uses currentCart.addToCurrentCart

features:
  - name: "Gift cards (when enabled in dashboard)"
    description: "Customers buy preset-amount gift cards on a dedicated page. Wix issues redeemable codes after payment and emails the recipient. The page, nav link, and home teaser only appear once the Wix Gift Card app is enabled in the dashboard — no rebuild needed."

apps: []   # do NOT auto-install; the user opts in via Catalog → Gift Cards in the dashboard

routes:
  - route: "/gift-cards"

# disabled: true → the pack's surfaces are inactive by default; they light up only when the user enables the matching Wix app from the dashboard. DISCOVERY.md Section B + C plan composition skips features and routes from disabled packs so the plan never promises a surface the user did not opt into.
disabled: true
---

# Gift Cards Pack

Passive vertical: code ships in every site that has a storefront, but every gift-card surface only renders if the **Wix Gift Card app** is enabled in the site's dashboard. Never user-triggered.

> **Discovery contract.** Phase 1 reads only the frontmatter above. Because `disabled: true`, the discovery plan never promises any gift-card surface to the user. Phase 2+ implementation (runtime probe, buy flow, nav/home contributions) lives in this skill's own `templates/gift-cards/` + `references/gift-cards/INSTRUCTIONS.md`; the `astro-stores-demo` includes a working `gift-card.astro` reference.