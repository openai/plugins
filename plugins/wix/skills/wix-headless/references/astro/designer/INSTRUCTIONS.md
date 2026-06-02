---
name: page-designer
description: "The page-design specification for Wix Managed Headless Phase 4 routes: home, static (about/faq), store-pages, blog-pages, contact-page. This is the visual-design guidance the merged Phase 4 `pages` scopes (vertical packs, BUILD.md Step 7) apply when they write each route ONCE with both visual design and live SDK data. It defines layout, contract classes, decorative-slot conventions, responsive rules, and anti-patterns — not a separate placeholder-writing pass. The design-system phase (tokens + global.css + Layout/Nav/Footer shells) is NOT here — it is split across DESIGN_SYSTEM.md (Designer) and astro/COMPOSE.md (Composer)."
---

# Page Designer — Scope-Based Page Design

> **Single-write merged model (BUILD.md Step 7 is authoritative).** Phase 4 routes are written **once**, by the per-vertical `pages` scopes, with both visual design **and** live SDK queries in the same pass — there is no separate "write a design placeholder, then rewrite it with data" dispatch (that double-write was eliminated). This doc is the **visual-design specification** the merged author applies: the layout, typography, color, spacing, contract classes, decorative slots, and component composition each route should have. Where a section below says "placeholder data," read it as *the data shape* the live query maps onto — and the safe fallback to render if a query returns empty. The merged scope binds real SDK data into this structure; it does not ship hardcoded arrays as the final output.

Your prompt will contain a `Scope:` line naming exactly one of the page scopes below. **Read only the section for your scope. Do not read sections for other scopes — wastes context and blurs ownership.**

You own **page-level visual output**: the layout, typography, color, spacing, and component composition of one route group. The same merged scope also binds the live SDK data into that structure (the per-vertical reference under `references/astro/<vertical>/` supplies the exact queries).

> **The design-system phase is not in this doc.** Tokens (`data.designTokens`), `global.css`, `astro.config.mjs`, `Layout.astro`, `Navigation.astro`, and `Footer.astro` are produced earlier in the run by a two-role split:
> - **Designer** (`<SKILL_ROOT>/references/DESIGN_SYSTEM.md`) — returns the framework-agnostic design spec (tokens + brand-voice strings) as JSON only.
> - **Composer** (`<SKILL_ROOT>/references/astro/COMPOSE.md`) — applies that spec to the astro skeletons and writes the 6 design-system files.
>
> By the time the Phase 4 routes are written, the `@theme` token contract, the `.astro` shells, and `.wix/design-tokens.css` already exist. You consume them; you do not write them.

## Self-Loading

1. Read `../../shared/RETURN_CONTRACT.md` — structured return format.
2. Read `../../shared/STYLING.md` — three styling categories (tokens-as-utilities, global semantic classes, co-located styles). Pages compose `@theme` tokens at call sites as Tailwind utilities; the inlined `designTokens` contract in your prompt tells you which tokens this run published.

No REST calls required. Page-design scopes are frontend-only — no `curl`, no MCP tool-discovery.

**Do NOT `Read .wix/site.json`.** Every input you need (brand, the published `designTokens` contract, pages to design, pack home-section snippets) is inlined in your prompt.

## Scope Routing

| Scope | Phase | Output (files) |
|-------|-------|----------------|
| `home` | Phase 4 — Step 7 | `src/pages/index.astro` (composes pack home-sections + brand hero/CTA into the Composer-written shell) |
| `static` | Phase 4 — Step 7 | `src/pages/about.astro`, `src/pages/faq.astro` |
| `store-pages` | Phase 4 — Step 7 | `src/pages/products/index.astro`, `src/pages/products/[slug].astro`, `src/components/ProductCard.astro`, `src/pages/cart.astro`, `src/pages/thank-you.astro` |
| `blog-pages` | Phase 4 — Step 7 | `src/pages/blog/index.astro`, `src/pages/blog/[slug].astro` |
| `contact-page` | Phase 4 — Step 7 | `src/pages/contact.astro` |

If your prompt's `Scope:` line names `design-system`, you have the wrong doc — that work lives in `DESIGN_SYSTEM.md` (Designer) and `astro/COMPOSE.md` (Composer). Stop and tell the parent.

If your prompt is missing a `Scope:` line, stop and ask the parent — do not guess.

**Disabled-pack route discipline.** Loaded packs with `disabled: true` (today: only `gift-cards`) ship dormant — their surfaces are runtime-gated and only appear once the user enables the matching app. Do NOT add hero CTAs, footer links, brand-story callouts, closing-CTA buttons, or ANY entry point pointing at a `disabled: true` pack's route in your page output. Users click through and the feature doesn't exist. The pack's own markers are the only acceptable touchpoint, and those get gated by the pack's runtime probe in Phase 4, not by you.

---

## Page Designer Scopes (Phase 4 — Step 7, background)

All page scopes share common inputs and rules. Scope-specific details follow.

### Common inputs (from your prompt)

- **Brand context** — name, vibe, aesthetic direction, colors, fonts, mood.
- **Published token contract** — the `designTokens` JSON (same shape the Designer returned, written into `@theme` by the Composer). Compose these tokens as Tailwind utilities; if a token you need is absent, flag it in your return (`MISSING_TOKEN`) — do not invent a class.
- **Pages to design** — list of routes and their contract class associations.
- **Pack home-section snippet** (home scope only) — section stubs from every loaded pack.
- **Placeholder data instruction** — use plausible brand-contextual placeholder text, prices, images where live data is not yet available.

### Common rules for all page scopes

1. **Use contract classes.** Every component that corresponds to a contract key uses that class name. Do not invent replacements.
2. **Use the Layout.** Every page wraps content in `<Layout>`:
   ```astro
   ---
   import Layout from '../layouts/Layout.astro';
   ---
   <Layout title="Page Title">
     <!-- page content -->
   </Layout>
   ```
3. **Never empty — render real data, fall back gracefully.** Bind the live SDK query into the designed structure. When a query legitimately returns empty (collection not seeded, OOS, etc.), render a brand-contextual fallback (plausible copy / a tasteful empty state) so the page still looks complete and reviewable — never a blank section.
4. **SDK queries belong in the route frontmatter.** The merged `pages` scope imports the relevant SDK (`@wix/stores`, `@wix/data`, `@wix/blog`, …) in the route's frontmatter and queries live data — see the per-vertical reference under `references/astro/<vertical>/` for the exact queries. Wrap every SSR `await` in try/catch with a safe fallback (an unguarded SSR throw truncates Astro's response stream mid-body). Do **not** ship hardcoded arrays as the final page output.
5. **No React islands authored here.** Do not write `.tsx` components — Phase 3 Components writes the islands. Phase 4 routes **mount** the already-written islands (`client:load`, etc.) but never author them.
6. **Scoped page styles allowed.** Pages may add `<style>` blocks for page-specific ornamental styling (section backgrounds, decorative elements, page-specific spacing adjustments). These are local to the page — do not override contract class rules from `global.css`.
7. **Image placeholders — decorative slot convention.** Every decorative image (hero, about visual, page-header art) MUST be emitted as a `<div>` placeholder carrying a `data-decorative-slot="<key>"` attribute. **Use ONLY canonical slot keys from this fixed vocabulary:**

    | Key | Where it lives | Required when |
    |---|---|---|
    | `hero` | Homepage hero image | Always |
    | `about` | About-page (or home brand-story) editorial visual | Always |
    | `productsHeader` | `/products` listing header decorative | Stores pack loaded |
    | `cmsHeader` | `/about` or `/faq` page header decorative | CMS pack loaded (optional) |

    Do NOT invent keys like `aboutFeature`, `background`, `heroAlt`, etc. The image agent receives this canonical list as its `decorativeSlots` input and generates exactly those keys — invented keys will not have images, and orphan generated images go unused. If a page needs more visual interest, use scoped CSS / SVG / brand-color blocks instead of additional generated images. The orchestrator runs a post-Phase-2 Edit pass that injects the actual `<img>` for each slot once Image Phase 1 finishes; your job is to make the slot visible. Rules:
    - Use aspect-ratio + background-color on the placeholder so the page looks complete even if Image Phase 1 never completes.
    - Keep decorative overlays (stamps, rules, frames) as siblings of the slot `<div>` — the orchestrator injects the `<img>` as the FIRST child of the slot, so anything you want to layer over it must stay outside the slot `<div>` (or inside with explicit z-index).
    - Do NOT conditionally read any image-coordination file — Image Phase 1's slot→URL map flows to the orchestrator via its JSON return, and the orchestrator injects URLs into your slot placeholders. The slot mechanism is the contract; no file lookup is needed or correct.
    - Do not use external placeholder services (picsum, unsplash, etc.).

    Example:
    ```astro
    <section class="hero-section relative">
      <div
        class="hero-image"
        data-decorative-slot="hero"
        style="aspect-ratio: 4/5; background-color: var(--color-paper-warm);"
      >
        <!-- orchestrator injects <img src={decorativeImages.hero} …> here -->
      </div>
      <div class="hero-stamp">{/* decorative overlay, stays outside the slot */}</div>
    </section>
    ```
8. **Comments in frontmatter.** Use `//` or `/* */` — never HTML `<!-- -->` comments in `.astro` frontmatter (it's TypeScript, not HTML). HTML comments in the template section are fine.
9. **Responsive.** All pages must work at mobile (320px), tablet (768px), and desktop (1024px+). Use Tailwind responsive prefixes (`md:`, `lg:`) and the spacing scale from `@theme`.
10. **Use Tailwind utility classes in templates.** For layout, spacing, typography, and responsive design — use utility classes directly in the markup. Contract classes are still required for components referenced by Phase 3/4 agents. Mix both: `<div class="product-grid grid grid-cols-1 md:grid-cols-3 gap-lg">`. Always use brand `@theme` tokens (e.g., `bg-bark`, `text-cream`) — never default Tailwind colors.
11. **No duplicate files.** If two scopes list the same file (rare), the scope whose prompt explicitly names it as "owned" takes precedence. If unclear, write it and note the overlap in your return.
12. **Do NOT write to `src/styles/components-<pack>.css` or `src/styles/global.css`** — `components-<pack>.css` is owned by Phase 3 Components agents; `global.css` is owned by the Composer. Writing to either causes double-write conflicts.

### Scope: `home`

Composes the home page from every loaded pack's `homeSection` snippet plus brand-specific hero and CTA sections.

**Inputs (additional):**
- `Pack home-section snippets` — one per loaded pack. Each names a section (e.g., "Featured products", "Brand story", "Latest posts", "Contact CTA") with a description and contract classes.

**Structure:**
1. **Hero section** — full-width, impactful brand moment. Uses `hero-section` contract class. Emit a `data-decorative-slot="hero"` placeholder per Common rule #7 — do not inline an Image Phase 1 URL; the orchestrator injects the `<img>` after Image Phase 1 completes.
2. **Pack sections** — one section per loaded pack's `homeSection`, in a sensible order (typically: featured content first, then story, then CTA).
3. **Optional closing CTA** — if no pack contributes a CTA section, add a minimal brand-appropriate closing.

**Files:** `src/pages/index.astro`

**Return:**
```json
{
  "status": "complete",
  "phase": "designer-home",
  "scope": "home",
  "data": {
    "pagesDesigned": ["src/pages/index.astro"],
    "contractClassesHonored": ["hero-section", "product-grid", "product-card", "brand-story", ...]
  },
  "files": ["src/pages/index.astro"]
}
```

### Scope: `static`

About and FAQ pages — content pages with similar layout demands.

**Files:** `src/pages/about.astro`, `src/pages/faq.astro`

**About page:**
- Hero/header section with `about-hero` class
- Body content with `about-body` class
- Placeholder brand story text (2-3 paragraphs, brand-contextual)
- Image placeholder for brand/team visual

**FAQ page:**
- Section wrapper with `faq-section` class
- Individual Q&A items with `faq-item`, `faq-question`, `faq-answer` classes
- 4-6 placeholder FAQ items contextual to the business type
- Accordion or expandable pattern (CSS-only, using `<details>`/`<summary>` or checkbox hack)

**Return:**
```json
{
  "status": "complete",
  "phase": "designer-static",
  "scope": "static",
  "data": {
    "pagesDesigned": ["about", "faq"],
    "contractClassesHonored": ["about-hero", "about-body", "faq-section", "faq-item", "faq-question", "faq-answer"]
  },
  "files": ["src/pages/about.astro", "src/pages/faq.astro"]
}
```

### Scope: `store-pages`

All store-facing pages designed together for visual coherence.

**Files:** `src/pages/products/index.astro`, `src/pages/products/[slug].astro`, `src/components/ProductCard.astro`, `src/pages/cart.astro`, `src/pages/thank-you.astro`

**Products listing (`/products`):**
- Page heading
- Product grid using `product-grid` class
- 3-6 placeholder product cards using `ProductCard` component

**Product detail (`/products/[slug]`):**
- Product image (large, placeholder)
- Product info section with `product-detail` class
- Purchase area with `product-purchase` class — placeholder price, placeholder variant selector, Add to Cart button with `add-to-cart-btn` class
- Product description area

**ProductCard component:**
- Accepts a single `product` prop (object with name, price, slug, image fields)
- Uses `product-card` class
- Image, name, price, link to `/products/${product.slug}`
- **Important:** Phase 2 `product-pages` rewrites this to accept the full Wix product object. Design with a simple prop interface: `{ product: { name: string; slug: string; price: number; image?: string } }`

**Cart (`/cart`):**
- Two-column grid layout: `.cart-grid` — items column left, order summary right. Stacks vertically on mobile
- Items column with `.cart-items`, `.cart-item`, `.cart-item.unavailable` (reduced opacity), `.cart-item-image`, `.cart-item-info`, `.cart-item-name`, `.cart-item-option`, `.cart-item-modifiers` classes
- Quantity selector with `.cart-item-qty`, `.qty-btn`, `.qty-value` classes — include `:disabled` states (reduced opacity + `cursor: not-allowed`)
- Price display with `.cart-item-actions`, `.cart-item-prices`, `.cart-item-full-price` (strikethrough for discounts), `.cart-item-unit-price`, `.cart-item-line-total` classes
- Remove button with `.cart-item-remove` class (muted color, underline on hover)
- Summary column with `.cart-summary` (sticky on desktop), `.cart-subtotal`, `.checkout-btn` (with `:disabled` state), `.cart-empty` classes
- Unavailable item warning with `.cart-item-unavailable` class (red text)
- Empty state with `.cart-empty` class (centered, muted text + "Browse Products" link)
- **All cart CSS must be in `<style is:global>`** — `CartView` is a React island; scoped Astro styles do not reach its children
- Placeholder cart items (2-3)

**Thank you (`/thank-you`):**
- Confirmation message with `order-summary` class
- Placeholder order details

**Return:**
```json
{
  "status": "complete",
  "phase": "designer-store-pages",
  "scope": "store-pages",
  "data": {
    "pagesDesigned": ["products/index.astro", "products/[slug].astro", "ProductCard.astro", "cart.astro", "thank-you.astro"],
    "contractClassesHonored": <count>
  },
  "files": [
    "src/pages/products/index.astro",
    "src/pages/products/[slug].astro",
    "src/components/ProductCard.astro",
    "src/pages/cart.astro",
    "src/pages/thank-you.astro"
  ]
}
```

### Scope: `blog-pages`

Blog feed listing and post detail designed together.

**Files:** `src/pages/blog/index.astro`, `src/pages/blog/[slug].astro`

**Blog listing (`/blog`):**
- Page heading
- Post grid/list using `blog-feed` class
- 3 placeholder post cards using `blog-post-card` class (title, date, excerpt, cover image placeholder)

**Blog post detail (`/blog/[slug]`):**
- Post header with title, date, author, cover image placeholder
- Body area with `blog-post` and `blog-post-body` classes
- Meta section with `blog-post-meta` class (tags, share links)
- Good reading typography (max-width prose container, comfortable line height)

**Return:**
```json
{
  "status": "complete",
  "phase": "designer-blog-pages",
  "scope": "blog-pages",
  "data": {
    "pagesDesigned": ["blog/index.astro", "blog/[slug].astro"],
    "contractClassesHonored": ["blog-feed", "blog-post-card", "blog-post", "blog-post-body", "blog-post-meta"]
  },
  "files": ["src/pages/blog/index.astro", "src/pages/blog/[slug].astro"]
}
```

### Scope: `contact-page`

Contact page with form placeholder.

**Files:** `src/pages/contact.astro`

**Contact page:**
- Page heading and descriptive text
- Contact CTA section using `contact-cta` class (if on home, this mirrors the home CTA's visual language)
- Form placeholder area — a styled `<div>` where Phase 2 mounts the `ContactForm.tsx` island. Use a placeholder form layout (name, email, message fields, submit button) so the page looks complete, but Phase 2 replaces this with the real React island.
- Optional: map embed placeholder, business hours, address (if brand context suggests it)

**Return:**
```json
{
  "status": "complete",
  "phase": "designer-contact-page",
  "scope": "contact-page",
  "data": {
    "pagesDesigned": ["contact.astro"],
    "contractClassesHonored": ["contact-cta"]
  },
  "files": ["src/pages/contact.astro"]
}
```

---

## Return Contract

At the end of your work, emit a structured JSON block per `../../shared/RETURN_CONTRACT.md`. Do **not** write sidecar files to `.wix/logs/*`.

The JSON block MUST be the **last** content in your message — the parent parses it as the last fenced JSON. No trailing prose after the closing ` ``` `.

## Anti-Patterns (apply to all page scopes)

| WRONG | CORRECT |
|-------|---------|
| Author a `.tsx` React island in a page scope | Phase 3 Components writes the islands; the route only **mounts** them (`client:load`) |
| Ship hardcoded data arrays as the final page | Query live SDK data in frontmatter (per the vertical reference) and bind it; hardcoded shapes are only a fallback for empty queries |
| Write `global.css` or `@theme` tokens | The Composer owns `global.css`; you consume the published token contract |
| Invent global semantic classes for layout/spacing/typography (`.featured-section`, `.page-header`) | Use Tailwind utilities derived from `@theme` tokens at the call site (`<section class="py-4xl">`); see `../../shared/STYLING.md` |
| Override `global.css` rules from page `<style>` blocks | Pages can add co-located styles for one-off decoration; never override Composer-owned global classes |
| HTML `<!-- comment -->` in `.astro` frontmatter | Use `//` or `/* */` — frontmatter is TypeScript |
| Use external placeholder image services (picsum, unsplash) | Use colored `<div>` placeholders with `data-decorative-slot` — the orchestrator injects Image Phase 1 URLs later |
| Write `components-<pack>.css` | Phase 3 Components creates that file — page scopes must not write it |
| Leave a section empty when a query returns nothing | Render a brand-contextual fallback / empty state so the page is always reviewable |
| Use default Tailwind colors (`bg-blue-500`, `text-gray-200`) | Use brand `@theme` tokens (`bg-bark`, `text-cream`) — defaults expose that it's AI-generated |
| Generic unstyled HTML | Brand-first design — every element reflects the aesthetic direction |
| Fixed-width layouts | Responsive: mobile-first, breakpoints at 320/768/1024px |
| `ls src/`, `Glob src/**` to discover files | Your prompt lists every file and class contract. Write directly. |
| `Read .wix/site.json` to get brand or verticals | Every field is in your prompt |
| Hardcode an external `<img src="https://...">` for product/content images | Resolve entity images from the live record (`media.getScaledToFillImageUrl(...)`) in this same scope; **decorative** images use the `data-decorative-slot` mechanism |
| Omit `data-decorative-slot` on hero/about/background placeholders | Every decorative image placeholder MUST carry a slot attribute — the orchestrator's injection pass depends on it (common rule #7) |
| Add a hero CTA / footer link to a disabled-pack route | Disabled packs (gift-cards) are dormant — no entry points to their routes |
| ProductCard with flat props (`name`, `price`, `slug` as separate props) | Single `product` object prop: `{ product }` — Phase 4 passes the full Wix product object |
| Wrap CartBadge in `<a>` or add cart SVG icons in `nav-actions` | Leave `nav-actions` empty — CartBadge renders its own `<a>` link; nesting `<a>` tags produces duplicate icons |

## Coordination with other agents

| Agent | Relationship | Rule |
|-------|-------------|------|
| Composer (design-system) | Wrote `global.css`, `Layout.astro`, `Navigation.astro`, `Footer.astro`, the `@theme` tokens | You consume the token contract and wrap pages in its `Layout`; you never rewrite those files |
| Phase 3 Components (stores/blog/forms) | Writes React islands referencing contract classes + `components-<pack>.css` | They own islands + scoped CSS; the route references contract classes in markup and mounts the islands, no overlap |
| Per-vertical reference (`references/astro/<vertical>/`) | Supplies the exact SDK queries + wiring the merged route binds | Apply this design spec **and** that vertical's queries together in one write — there is no second pass |
| Image agent (Image Phase 1) | Returns decorative URLs in `data.slots` | Emit `data-decorative-slot="<key>"` placeholders; the orchestrator injects the `<img>` once Image Phase 1 returns |
| Image agent (Image Phase 2) | PATCHes entity images onto products/posts via REST | No direct interaction — images flow through product/post records that Phase 4 queries |

## File ownership

The merged Phase 4 `pages` scope owns each route file **end to end** — visual structure **and** data wiring, written in a single pass. There is no separate page-designer agent that writes a file for a later scope to rewrite; this doc is the visual-design spec the merged author applies alongside its vertical's SDK queries (`references/astro/<vertical>/`). Each route file therefore has exactly **one** writer (its `pages` scope), which removes the cross-phase double-write the older placeholder-then-rewrite model carried.

The shared shells the route composes into — `Layout.astro`, `Navigation.astro`, `index.astro`, `global.css`, `components-<pack>.css` — are owned by the Composer / Phase 3 Components, not by the route scope (see "Coordination" above and BUILD.md Step 7's shared-shell-patcher serialization rule).
