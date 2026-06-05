---
name: ecom
description: "Vertical-agnostic ecommerce — cart page, checkout redirect, order confirmation. Co-loaded by packs that require it."
triggers: []   # never triggered independently — co-loaded via another pack's `requires:`

features:
  - name: "Cart & checkout"
    description: "Add items to cart, review order, check out via Wix's secure hosted checkout. Order confirmation on thank-you page."

apps: []   # no app to install — @wix/ecom works with any installed catalog app

routes:
  - route: "/cart"
  - route: "/thank-you"
  - route: "Hosted by Wix"   # Wix-hosted endpoint — no .astro file. Listed so the discovery plan's Section C table includes a Checkout row (omitting it created user anxiety in the 2026 dolls-store run; the cart appeared to "go nowhere"). The route cell renders the literal string "Hosted by Wix".
    name: "Checkout"

disabled: false
---

# Ecom Pack

Vertical-agnostic ecommerce cart, checkout, and order confirmation. Co-loaded by any pack that needs cart/checkout (today: `stores`, `gift-cards`; future: `bookings`, `events`) via the `requires:` field. Never user-triggered.

> **Discovery contract.** Phase 1 reads only the frontmatter above. Phase 2+ implementation (cart wiring, checkout redirect, discount codes) lives in this skill's own `templates/ecom/` + `references/ecom/INSTRUCTIONS.md`.