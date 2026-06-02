# Seed recipe map

Per-vertical recipe lookup for the seed dispatch in `SEED.md`. Recipe paths are **relative to `<wix-manage-root>`**, the absolute path that `wix-manage`'s SKILL.md publishes when Phase 2 Step 4 loads it. The orchestrator joins `<wix-manage-root>` + the relative path at dispatch time. Do not pre-resolve, hardcode, or pre-validate the absolute paths at session start — fail at dispatch time if a recipe has moved.

| Pack | Recipes (relative to `<wix-manage-root>`) | Returns |
|---|---|---|
| stores | `references/stores/setup-online-store-catalog-v3.md` (idempotent catalog setup) + `references/stores/bulk-create-products-with-options.md` (single bulk call for N products) | `productIds[]`, `categoryIds[]` (when `intent.stores.categoriesNamed` is non-empty) |
| cms | `references/cms/cms-schema-management.md` (collection create) + `references/cms/cms-data-items-crud.md` (item create per collection) + `references/cms/cms-references-and-relationships.md` (only when a collection's `intent.cms.collections[N]` declares cross-references) | `collectionIds{}`, `itemIds{<collection>: []}` |
| blog | `references/blog/how-to-create-blog-posts.md` | `postIds[]`, `categoryIds[]` |
| forms | `references/forms/create-form.md` | `formIds[]` |
| gift-cards | — (no seed surface; activation lives in Phase 2 app-install) | `{status: "skipped"}` |
| ecom | — (cart/checkout vertical; no seed surface) | `{status: "skipped"}` |

The orchestrator dispatches one subagent per pack with a recipe. `gift-cards` and `ecom` get a phase entry of `{phase: "seed-<pack>", status: "skipped"}` recorded directly by the orchestrator without dispatching a subagent.

---

## Per-pack input notes

These notes reduce dispatch-time guesswork. The recipe itself is the source of truth for the API shape — these notes are about how to translate `intent.<pack>` + `brand` into the recipe's input.

### stores

- The bulk recipe wants `products: [{name, slug, sku, price, options?, variants?}]`. Populate `name` and `slug` from `intent.stores.productCount` and `brand` (e.g. for a coffee shop with `productCount: 3`, generate three product names that fit the brand vibe).
- `sku` defaults to `<slug>-001` when not otherwise constrained.
- `price` is a positive number; pick brand-appropriate values (don't default to $1).
- When `intent.stores.categoriesNamed` is non-empty, the subagent creates those categories via the Categories API after the bulk product create and assigns products into them. When the array is empty, skip categories entirely (do not invent a default set).
- The recipe documents a 5-product cap on the bulk endpoint. If `intent.stores.productCount` exceeds it, fan out into batches of 5.
- Text-only seeding: do not generate or attach product images. The `media` field follows the recipe's documented placeholder pattern.

### cms

- The schema recipe wants one `POST /wix-data/v2/collections` call per collection in `intent.cms.collections`. Field shape comes from `collection.purpose` — e.g. `purpose: "about"` → a single-row text collection with `title` + `body`; `purpose: "faq"` → repeated `question` + `answer` rows.
- After all collections exist, the items recipe (`cms-data-items-crud.md`) inserts `intent.cms.collections[N].itemCount` rows per collection, with content generated from `brand`.
- `cms-references-and-relationships.md` is consulted **only** when a collection's intent block declares cross-references (e.g. `references: ["products"]`). Otherwise skip it.
- Return shape: `collectionIds: { <purpose>: <id> }` and `itemIds: { <purpose>: [<id>, ...] }`. Keying by `purpose` (not by collection display name) lets Phase 4 wire pages without re-deriving slug ↔ id.

### blog

- The recipe's Part 0 (member ID lookup) is mandatory — third-party app installs require `draftPost.memberId`. The subagent issues one `GET /members/v1/members?paging.limit=1` and uses the returned id for every post.
- `intent.blog.postCount` posts are created. Topics come from `intent.blog.topics` when present; otherwise the subagent picks brand-appropriate topics from `brand.description`.
- Text-only seeding: cover images use the recipe's documented placeholder pattern; do not call Media Manager import.
- `categoryIds[]` returned only when the recipe creates categories during seeding (the recipe handles category-on-create automatically when the post payload references one).

### forms

- One `POST /form-schema-service/v4/forms` call per entry in `intent.forms.forms`. The subagent maps `intent.forms.forms[N].fields` (a string array like `["name", "email", "message"]`) into the recipe's `formFields` payload using the recipe's documented field templates (`CONTACTS_FIRST_NAME`, `CONTACTS_EMAIL`, etc.).
- `purpose` ("contact", "lead", "signup") drives the form's `name` field — e.g. `"contact"` → `"Contact Form"`.
- Wix Forms app is usually pre-installed via Phase 2 — the recipe notes this and the seeder does not need to install it again.
