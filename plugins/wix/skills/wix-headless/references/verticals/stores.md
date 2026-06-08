---
name: stores
description: "Ecommerce — product catalog with add-to-cart. Co-loads ecom (cart/checkout) and gift-cards (passive)."
triggers: ["sell", "ecommerce", "store", "shop", "products", "merchandise", "catalog", "merch", "buy"]
requires: ["ecom", "gift-cards"]

features:
  - name: "Product catalog"
    description: "Browse products with images, prices, and variants. Click through to detailed product pages with add-to-cart."

apps:
  - name: "Wix Stores"
    appDefId: "215238eb-22a5-4c36-9e7b-e7c08025e04e"

routes:
  - route: "/products"
  - route: "/products/[slug]"
    name: "Product Detail"   # path-derivation would produce "Products [slug]" — override with the user-facing label
  - route: "/category/[slug]"
    name: "Category"

disabled: false
---

# Stores Pack

Loaded when the user's prompt implies selling products.

> **Discovery contract.** Phase 1 reads only the frontmatter above to compose the plan's Pages table. Phase 2+ implementation (seeding, page composition, theming) lives in an upstream skill plus this skill's own `templates/stores/` + `references/stores/INSTRUCTIONS.md`:
>
> - `@skills/wix-manage` ships the seeding recipes — `references/stores/setup-online-store-catalog-v3.md`, `bulk-create-products-with-options.md`, `create-product-from-image.md`.
>
> No per-pack `seed`, `components`, `componentsCss`, or `pages` blocks live in this skill anymore.