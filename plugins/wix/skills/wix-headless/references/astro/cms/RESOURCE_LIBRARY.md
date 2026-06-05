# Recipe: Resource Library / Downloads

Build a downloadable resource library using `@wix/data` — file listings with category filtering, file type badges, and detail pages with download buttons. Use for documents, guides, templates, whitepapers, or any downloadable assets.

> Read `CMS_FOUNDATIONS.md` (this folder — service module, query patterns, image resolution, elevation) for page-rendering patterns, and `../../cms/CMS_FOUNDATIONS.md` for REST-based seeding.

## Collection Schema

Create a collection in the Wix dashboard → CMS with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `title` | Text | Resource name |
| `slug` | Text | URL-friendly identifier |
| `description` | Rich Text | Resource description (HTML) |
| `category` | Text | Resource category (e.g., "Guides", "Templates") |
| `fileType` | Text | File extension — `PDF`, `DOC`, `ZIP`, `XLS`, etc. |
| `fileUrl` | URL | Download URL (external link or Wix media URL) |
| `fileSize` | Text | Human-readable file size (e.g., "2.4 MB") |
| `coverImage` | Image | Thumbnail (`wix:image://` — resolve with `media.getScaledToFillImageUrl()`) |
| `published` | Boolean | Publish status |
| `_createdDate` | Date | Auto-populated creation date |

## Files to Create

| File | Purpose |
|------|---------|
| `src/lib/resources.ts` | Service module — queries, category filtering, related resources |
| `src/pages/resources/index.astro` | Listing with category filter + file type badges |
| `src/pages/resources/[slug].astro` | Detail page with download button + related resources |
| `src/components/ResourceCard.astro` | Card with file type icon, title, size |
| `src/components/FileTypeIcon.astro` | SVG switch for PDF/DOC/ZIP/generic |

## Implementation

### 1. Resources Service Module (`src/lib/resources.ts`)

```typescript
import * as items from "@wix/wix-data-items-sdk";
import { auth } from "@wix/essentials";
import { media } from "@wix/sdk";

const COLLECTION_ID = "Resources";

export interface Resource {
  _id: string;
  title: string;
  slug: string;
  description?: string;
  category: string;
  fileType: string;
  fileUrl: string;
  fileSize?: string;
  coverImage?: string;
  published: boolean;
  _createdDate?: string;
}

function resolveImage(url: string | undefined): string | undefined {
  if (!url) return undefined;
  return media.getScaledToFillImageUrl(url, 600, 400, {});
}

function mapResource(item: Record<string, any>): Resource {
  return {
    _id: item._id,
    title: item.title ?? "",
    slug: item.slug ?? "",
    description: item.description,
    category: item.category ?? "",
    fileType: (item.fileType ?? "FILE").toUpperCase(),
    fileUrl: item.fileUrl ?? "",
    fileSize: item.fileSize,
    coverImage: resolveImage(item.coverImage),
    published: item.published ?? false,
    _createdDate: item._createdDate,
  };
}

export async function queryResources(): Promise<Resource[]> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .eq("published", true)
    .descending("_createdDate")
    .limit(50)
    .find();

  return results.map(mapResource);
}

export async function getResourceBySlug(slug: string): Promise<Resource | null> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .eq("slug", slug)
    .eq("published", true)
    .limit(1)
    .find();

  const item = results[0];
  if (!item) return null;
  return mapResource(item);
}

export async function queryRelatedResources(category: string, excludeId: string, limit = 3): Promise<Resource[]> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .eq("published", true)
    .eq("category", category)
    .ne("_id", excludeId)
    .descending("_createdDate")
    .limit(limit)
    .find();

  return results.map(mapResource);
}
```

Key details:
- `queryRelatedResources()` finds same-category items excluding the current one
- `fileType` normalized to uppercase for consistent badge display
- Sorted by `_createdDate` descending (newest first)
- Update `COLLECTION_ID` to match the exact collection name from the Wix dashboard (no namespace prefix for native collections)

### 2. File Type Icon (`src/components/FileTypeIcon.astro`)

```astro
---
interface Props {
  type: string;
  class?: string;
}

const { type, class: className = "w-8 h-8" } = Astro.props;
const fileType = type.toUpperCase();

// File type colors are applied by the design skill's component styles
---

<div class={className}>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
    <polyline points="14 2 14 8 20 8" />
    <text x="12" y="17" text-anchor="middle" font-size="5" fill="currentColor" stroke="none" font-weight="bold">{fileType.slice(0, 4)}</text>
  </svg>
</div>
```

Key details:
- Color-coded by file type — red for PDF, blue for DOC, green for XLS, yellow for ZIP
- Falls back to neutral gray for unknown types
- File type label rendered inside the document icon SVG

### 3. Resource Card (`src/components/ResourceCard.astro`)

```astro
---
import FileTypeIcon from "./FileTypeIcon.astro";

interface Props {
  resource: {
    title: string;
    slug: string;
    category: string;
    fileType: string;
    fileSize?: string;
    coverImage?: string;
  };
}

const { resource } = Astro.props;
---

<a href={`/resources/${resource.slug}`}>
  {resource.coverImage ? (
    <div><img src={resource.coverImage} alt={resource.title} /></div>
  ) : (
    <div><FileTypeIcon type={resource.fileType} /></div>
  )}
  <div>
    <div>
      <span>{resource.fileType}</span>
      {resource.fileSize && <span>{resource.fileSize}</span>}
    </div>
    <h3>{resource.title}</h3>
    <p>{resource.category}</p>
  </div>
</a>
```

> **Styling note:** ResourceCard styling is created by the design skill. See `COMPONENT_PATTERNS.md` → Resource Card.

### 4. Resource Listing Page (`src/pages/resources/index.astro`)

```astro
---
import Layout from "../../layouts/Layout.astro";
import ResourceCard from "../../components/ResourceCard.astro";
import CategoryFilter from "../../components/CategoryFilter.astro";
import { queryResources } from "../../lib/resources";

const activeCategory = Astro.url.searchParams.get("category");
const allResources = await queryResources();
const filtered = activeCategory
  ? allResources.filter((r) => r.category === activeCategory)
  : allResources;
const categories = [...new Set(allResources.map((r) => r.category).filter(Boolean))];
---

<Layout title="Resources">
  <main>
    <div>
      <h1>Resources</h1>
      <p>Download guides, templates, and documents.</p>

      <CategoryFilter categories={categories} activeCategory={activeCategory} basePath="/resources" />

      <div>
        {filtered.map((resource) => (
          <ResourceCard resource={resource} />
        ))}
      </div>

      {filtered.length === 0 && (
        <p>No resources found.</p>
      )}
    </div>
  </main>
</Layout>
```

> Reuses the same `CategoryFilter.astro` component from the portfolio use case. If building both, no need to create it twice.

### 5. Resource Detail Page (`src/pages/resources/[slug].astro`)

```astro
---
import Layout from "../../layouts/Layout.astro";
import ResourceCard from "../../components/ResourceCard.astro";
import FileTypeIcon from "../../components/FileTypeIcon.astro";
import { getResourceBySlug, queryRelatedResources } from "../../lib/resources";

const { slug } = Astro.params;
const resource = await getResourceBySlug(slug!);
if (!resource) return Astro.redirect("/404");

const related = await queryRelatedResources(resource.category, resource._id);

const date = resource._createdDate
  ? new Date(resource._createdDate).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  : "";
---

<Layout title={resource.title}>
  <main>
    <div>
      <a href="/resources">
        &larr; Back to resources
      </a>

      <div>
        <FileTypeIcon type={resource.fileType} />
        <div>
          <div>
            <span>{resource.fileType}</span>
            {resource.fileSize && (
              <span>{resource.fileSize}</span>
            )}
          </div>
          {date && <p>Added {date}</p>}
        </div>
      </div>

      <h1>{resource.title}</h1>

      {resource.coverImage && (
        <div>
          <img
            src={resource.coverImage}
            alt={resource.title}
          />
        </div>
      )}

      {resource.description && (
        <article set:html={resource.description} />
      )}

      {resource.fileUrl && (
        <a
          href={resource.fileUrl}
          download
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Download {resource.fileType}
        </a>
      )}

      {related.length > 0 && (
        <section>
          <h2>Related Resources</h2>
          <div>
            {related.map((r) => (
              <ResourceCard resource={r} />
            ))}
          </div>
        </section>
      )}
    </div>
  </main>
</Layout>
```

Key details:
- `<a download>` triggers browser download for the file
- Related resources query pulls same-category items, excluding the current one
- File type icon and badge prominently displayed

## Seed with Images

After seeding resources via REST, generate cover images following `../../shared/IMAGE_GENERATION.md` and `../../cms/CMS_FOUNDATIONS.md` → "Seeding with Images".

**Prompt template:**

```
Cover image for [TITLE], a [FILE TYPE]. Abstract [BRAND AESTHETIC]. Color tones: [BRAND COLORS]. No text, no watermarks
```

**Patch field:** `coverImage`

Example patch:

```
REST: PATCH https://www.wixapis.com/wix-data/v2/items/{resourceId}
body: {
  "dataCollectionId": "Resources",
  "dataItem": {
    "data": {
      "coverImage": "<wixstatic-url>"
    }
  }
}
```

## Testing

1. Create a "Resources" collection in the Wix dashboard → CMS with the schema above
2. Add 4+ resources across 2+ categories with different file types (PDF, DOC, ZIP)
3. Include `fileUrl` links (can be any downloadable URL for testing)
4. Run `npx @wix/cli@latest dev`
5. `/resources` — shows all resources with category filters and file type badges
6. Click a category — filters resources
7. Click a resource — detail page with download button and related resources