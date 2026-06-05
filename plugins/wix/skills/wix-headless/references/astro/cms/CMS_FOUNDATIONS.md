# CMS Foundations — Code Patterns for `@wix/data` (astro)

The **rendering / code-patterns** half of CMS foundations: service module template, `@wix/data` SDK queries, image resolution, elevated access, and rich-text (Ricos) rendering — everything a CMS **page** scope needs to read collections and render them in Astro.

> **Seeding lives in the business track.** Creating collections and inserting/verifying items via REST is **not** here — it is in `<SKILL_ROOT>/references/cms/CMS_FOUNDATIONS.md` (the `seed` scope's doc). This file is consumed by the `pages` scope; that file by the `seed` scope. The `cms/INSTRUCTIONS.md` router points each scope at the right half.

> **Import note (read first).** Page code in this plugin uses `import * as items from "@wix/wix-data-items-sdk"` rather than the documented `import { items } from "@wix/data"`. The Wix-headless docs still show the `@wix/data` form, but `@wix/data` 1.0.448 dropped the `items` re-export — only sub-namespaces (`backups`, `collections`, `permissions`, …) remain, and the documented form fails the build with `'items' is not exported by '@wix/data'`. The actual `items` API (with `query`, `insert`, `update`, `remove`, `bulkInsert`, etc.) lives in `@wix/wix-data-items-sdk`, which `@wix/data` depends on transitively. Importing from there directly works on every current `@wix/data` version. SETUP.md's per-pack install table (Step 4c) installs `@wix/wix-data-items-sdk` (alongside `@wix/data` and `@wix/essentials`) for the cms pack so it's always present. Use the wix-data-items-sdk import everywhere.

## Rendering Ricos rich-text fields

Wix CMS stores `RICH_TEXT` / `RICH_CONTENT` fields as **Ricos JSON** — a structured node tree (PARAGRAPH, HEADING, BULLETED_LIST, etc.), not HTML. The dashboard's rich-text editor reads and writes this format.

For SSR Astro pages (about, faq, portfolio, team, resource), import the seeded `renderRicos` util from `src/utils/ricos.ts`. The util is shipped by `seed-utilities.sh` (copied from `<SKILL_ROOT>/shared-utilities/ricos.ts` during Setup), so it's already on disk — do NOT inline a Ricos walker in your page.

```astro
---
import * as items from "@wix/wix-data-items-sdk";
import { auth } from "@wix/essentials";
import { renderRicos } from "../utils/ricos";

const elevatedQuery = auth.elevate(items.query);
const { items: results } = await elevatedQuery("about-content")
  .limit(1)
  .find();
const about = results[0];
const bodyHtml = renderRicos(about?.body);
---

<article class="prose">
  <h1>{about?.heading}</h1>
  <div set:html={bodyHtml} />
</article>
```

The util covers the common subset (PARAGRAPH, HEADING 1-6, BULLETED_LIST / ORDERED_LIST / LIST_ITEM, BLOCKQUOTE, DIVIDER + BOLD / ITALIC / UNDERLINE / LINK decorations). Anything outside that set renders defensively as a `<p>` with the raw text — never throws.

> **Why not @wix/ricos?** The blog vertical uses `@wix/ricos`'s React `RicosViewer` as a client island because blog posts can carry the full Ricos feature set (galleries, polls, embedded media). For static CMS pages, that's ~80kb of React for paragraphs and lists — overkill. Use the seeded SSR walker instead.

> **Do NOT `set:html={item.body}` directly.** That ships JSON-encoded text into the page (e.g. `[object Object]` or `{"nodes":...}`). Always go through `renderRicos`.

> **Critical Rules — Read Before Starting**
> 1. **Collection IDs have NO namespace** — user collections use just the name (e.g., `"Projects"`). Only Wix App collections use `<namespace>/<name>`. Verify via `curl`: `GET /wix-data/v2/collections?fields=id`.
> 2. **SDK query pattern** — `items.query("CollectionId").find()`. There is no `items.queryDataItems()` in the SDK.
> 3. **`auth.elevate` on every query** — without it, restricted collections silently return no items.
> 4. **CMS only for user collections** — use `@wix/blog` for blog posts, `@wix/stores` for products, `@wix/forms` for form submissions.

## Prerequisites (page-side)

- `@wix/data` + `@wix/wix-data-items-sdk` + `@wix/essentials` installed (collected by SETUP.md Step 4c — do NOT install independently).
- The collections + items already created and seeded by the `seed` scope (see `../../cms/CMS_FOUNDATIONS.md`). Pages only **read**.

## Collection ID Format

Native (user-created) CMS collections use **just the collection name** — no namespace prefix.

Example: if the collection is called `Projects`, the collection ID is simply `"Projects"`.

Only Wix App collections (e.g., `Members/PublicData`, `Locations/Locations`) use a `<namespace>/<name>` format. User-created collections never use a namespace.

> **How to verify**: Call `GET /wix-data/v2/collections?fields=id` via `curl` (with the standard REST headers from `../../shared/AUTHENTICATION.md`) and use the exact `id` value from the response. Never guess — the dashboard name may differ from the ID.

## Quick Reference — Inline Query (Simple Pages)

For pages that just need to list items from a collection:

```astro
---
import * as items from "@wix/wix-data-items-sdk";
import { auth } from "@wix/essentials";

// Always elevate queries for permission safety
const elevatedQuery = auth.elevate(items.query);
const { items: results } = await elevatedQuery("MyCollection")
  .ascending("sortField")
  .limit(50)
  .find();

// Fields are directly on each item (NOT item.data.field)
const myItems = results.map((item) => ({
  name: item.name,        // correct
  // name: item.data.name  // wrong — REST pattern, not SDK
}));
---
```

> **Common mistake:** `items.queryDataItems(...)` does NOT exist in the
> `@wix/data` SDK. The REST API uses `/items/query` with a `dataCollectionId`
> body field, but the SDK uses `items.query("collectionId")` — a chainable
> QueryBuilder. Do not confuse REST and SDK patterns.

## Service Module Template

Every CMS use case follows the same `src/lib/{usecase}.ts` pattern — a typed interface and query functions that pages import.

```typescript
import * as items from "@wix/wix-data-items-sdk";
import { auth } from "@wix/essentials";
import { media } from "@wix/sdk";

// -- Collection ID (use exact name from Wix dashboard — no namespace for native collections) --
const COLLECTION_ID = "collection-name";

// -- Typed interface matching collection fields --
export interface CollectionItem {
  _id: string;
  title: string;
  slug: string;
  // ...add fields matching your collection schema
  coverImage?: string;
}

// -- Image resolution helper --
function resolveImage(wixImageUrl: string | undefined, width = 800, height = 600): string | undefined {
  if (!wixImageUrl) return undefined;
  return media.getScaledToFillImageUrl(wixImageUrl, width, height, {});
}

// -- Query all items --
// Wrap every Wix SDK await in try/catch. If the query throws at SSR, an empty
// array keeps the page renderable instead of crashing it. (Unguarded SSR
// awaits truncate Astro's response stream mid-body — nav renders, then blank.)
export async function queryItems(): Promise<CollectionItem[]> {
  try {
    const elevatedQuery = auth.elevate(items.query);
    const { items: results } = await elevatedQuery(COLLECTION_ID)
      .ascending("orderIndex")
      .limit(50)
      .find();

    return results.map((item) => ({
      ...item,
      coverImage: resolveImage(item.coverImage),
    })) as CollectionItem[];
  } catch (err) {
    console.error(`[cms:${COLLECTION_ID}] query failed:`, err);
    return [];
  }
}

// -- Get single item by slug --
export async function getItemBySlug(slug: string): Promise<CollectionItem | null> {
  try {
    const elevatedQuery = auth.elevate(items.query);
    const { items: results } = await elevatedQuery(COLLECTION_ID)
      .eq("slug", slug)
      .limit(1)
      .find();

    const item = results[0];
    if (!item) return null;

    return {
      ...item,
      coverImage: resolveImage(item.coverImage),
    } as CollectionItem;
  } catch (err) {
    console.error(`[cms:${COLLECTION_ID}] getItemBySlug failed:`, err);
    return null;
  }
}
```

Key details:
- `auth.elevate(items.query)` wraps the query for restricted collections — always use this by default since collection permissions vary
- `media.getScaledToFillImageUrl(url, w, h, {})` resolves `wix:image://` URLs to sized CDN URLs
- Sort by `orderIndex` (ascending) for manually ordered content, or `_createdDate` (descending) for chronological
- The interface must match the collection fields — check the dashboard, don't guess

## Multi-Image Resolution

For collections with image arrays (e.g., gallery images):

```typescript
function resolveImages(imageUrls: string[] | undefined, width = 800, height = 600): string[] {
  if (!imageUrls || imageUrls.length === 0) return [];
  return imageUrls
    .map((url) => media.getScaledToFillImageUrl(url, width, height, {}))
    .filter(Boolean);
}
```

## Category Filtering Pattern

Many use cases filter by category via URL search params (server-rendered, no client JS):

```astro
---
const activeCategory = Astro.url.searchParams.get("category");
const allItems = await queryItems();
const filtered = activeCategory
  ? allItems.filter((item) => item.category === activeCategory)
  : allItems;
const categories = [...new Set(allItems.map((item) => item.category).filter(Boolean))];
---

<nav>
  <a href="?" class:list={[!activeCategory && "active"]}>All</a>
  {categories.map((cat) => (
    <a
      href={`?category=${encodeURIComponent(cat)}`}
      class:list={[activeCategory === cat && "active"]}
    >{cat}</a>
  ))}
</nav>
```

> **Styling note:** Category filter pill styling composes `@theme` tokens as Tailwind utilities at the call site — see `../../shared/STYLING.md`.

## Testing

1. Confirm the collection exists in the Wix dashboard → CMS (the `seed` scope created it — see `../../cms/CMS_FOUNDATIONS.md`).
2. Run `npx @wix/cli@latest dev`.
3. Navigate to the listing page — should show items.
4. Click an item — should navigate to the detail page.
