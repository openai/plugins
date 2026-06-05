# Recipe: Portfolio / Projects Showcase

Build a visual portfolio using `@wix/data` — project grid with category filtering, image galleries, and project detail pages. Use for work samples, case studies, creative projects, or any visual showcase.

> Read `CMS_FOUNDATIONS.md` (this folder — service module, query patterns, image resolution, elevation) for page-rendering patterns, and `../../cms/CMS_FOUNDATIONS.md` for REST-based seeding.

## Collection Schema

Create a collection in the Wix dashboard → CMS with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `title` | Text | Project name |
| `slug` | Text | URL-friendly identifier |
| `category` | Text | Project category (e.g., "Branding", "Web Design") |
| `description` | Rich Text | Project writeup (HTML) |
| `client` | Text | Client or company name |
| `year` | Text | Year completed |
| `coverImage` | Image | Main project image (`wix:image://` — resolve with `media.getScaledToFillImageUrl()`) |
| `galleryImages` | Image Gallery | Additional project images (multi-image array) |
| `tags` | Text | Comma-separated tags |
| `featured` | Boolean | Show on home page |
| `orderIndex` | Number | Manual sort order |

## Files to Create

| File | Purpose |
|------|---------|
| `src/lib/portfolio.ts` | Service module — queries, category filtering, featured projects |
| `src/pages/work/index.astro` | Project grid with category filter tabs |
| `src/pages/work/[slug].astro` | Project detail with image gallery |
| `src/components/ProjectCard.astro` | Visual card for grid layout |
| `src/components/CategoryFilter.astro` | URL-param-based pill buttons |
| `src/components/ImageGallery.tsx` | React island for lightbox/carousel |

## Implementation

### 1. Portfolio Service Module (`src/lib/portfolio.ts`)

```typescript
import * as items from "@wix/wix-data-items-sdk";
import { auth } from "@wix/essentials";
import { media } from "@wix/sdk";

const COLLECTION_ID = "Projects";

export interface Project {
  _id: string;
  title: string;
  slug: string;
  category: string;
  description?: string;
  client?: string;
  year?: string;
  coverImage?: string;
  galleryImages: string[];
  tags: string[];
  featured: boolean;
  orderIndex: number;
}

function resolveImage(url: string | undefined, width = 800, height = 600): string | undefined {
  if (!url) return undefined;
  return media.getScaledToFillImageUrl(url, width, height, {});
}

function resolveImages(urls: string[] | undefined, width = 1200, height = 800): string[] {
  if (!urls || urls.length === 0) return [];
  return urls.map((url) => media.getScaledToFillImageUrl(url, width, height, {}));
}

function mapProject(item: Record<string, any>): Project {
  return {
    _id: item._id,
    title: item.title ?? "",
    slug: item.slug ?? "",
    category: item.category ?? "",
    description: item.description,
    client: item.client,
    year: item.year,
    coverImage: resolveImage(item.coverImage),
    galleryImages: resolveImages(item.galleryImages),
    tags: item.tags ? item.tags.split(",").map((t: string) => t.trim()) : [],
    featured: item.featured ?? false,
    orderIndex: item.orderIndex ?? 0,
  };
}

export async function queryProjects(): Promise<Project[]> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .ascending("orderIndex")
    .limit(50)
    .find();

  return results.map(mapProject);
}

export async function getProjectBySlug(slug: string): Promise<Project | null> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .eq("slug", slug)
    .limit(1)
    .find();

  const item = results[0];
  if (!item) return null;
  return mapProject(item);
}

export async function queryFeaturedProjects(limit = 3): Promise<Project[]> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .eq("featured", true)
    .ascending("orderIndex")
    .limit(limit)
    .find();

  return results.map(mapProject);
}
```

Key details:
- `resolveImages()` handles the multi-image gallery field — iterates and resolves each URL
- `tags` stored as comma-separated text, split into array at query time
- `queryFeaturedProjects()` is for home page sections — query `featured === true`
- Update `COLLECTION_ID` to match the exact collection name from the Wix dashboard (no namespace prefix for native collections)

### 2. Category Filter (`src/components/CategoryFilter.astro`)

```astro
---
interface Props {
  categories: string[];
  activeCategory: string | null;
  basePath: string;
}

const { categories, activeCategory, basePath } = Astro.props;
---

<nav>
  <a href={basePath} class:list={[!activeCategory && "active"]}>All</a>
  {categories.map((cat) => (
    <a
      href={`${basePath}?category=${encodeURIComponent(cat)}`}
      class:list={[activeCategory === cat && "active"]}
    >{cat}</a>
  ))}
</nav>
```

> **Styling note:** CategoryFilter styling is created by the design skill. See `COMPONENT_PATTERNS.md` → Category Filter.

> Server-rendered, no JavaScript. Category is read from `Astro.url.searchParams` in the page.

### 3. Project Card (`src/components/ProjectCard.astro`)

```astro
---
interface Props {
  project: {
    title: string;
    slug: string;
    category: string;
    coverImage?: string;
    client?: string;
    year?: string;
  };
}

const { project } = Astro.props;
---

<a href={`/work/${project.slug}`}>
  <div>
    {project.coverImage ? (
      <img src={project.coverImage} alt={project.title} />
    ) : (
      <div>No image</div>
    )}
  </div>
  <div>
    <span>{project.category}</span>
    {project.year && <span>&middot; {project.year}</span>}
  </div>
  <h3>{project.title}</h3>
  {project.client && <p>{project.client}</p>}
</a>
```

> **Styling note:** ProjectCard styling is created by the design skill. See `COMPONENT_PATTERNS.md` → Project Card.

### 4. Project Grid Page (`src/pages/work/index.astro`)

```astro
---
import Layout from "../../layouts/Layout.astro";
import ProjectCard from "../../components/ProjectCard.astro";
import CategoryFilter from "../../components/CategoryFilter.astro";
import { queryProjects } from "../../lib/portfolio";

const activeCategory = Astro.url.searchParams.get("category");
const allProjects = await queryProjects();
const filtered = activeCategory
  ? allProjects.filter((p) => p.category === activeCategory)
  : allProjects;
const categories = [...new Set(allProjects.map((p) => p.category).filter(Boolean))];
---

<Layout title="Work">
  <main>
    <div>
      <h1>Work</h1>

      <CategoryFilter categories={categories} activeCategory={activeCategory} basePath="/work" />

      <div>
        {filtered.map((project) => (
          <ProjectCard project={project} />
        ))}
      </div>

      {filtered.length === 0 && (
        <p>No projects found.</p>
      )}
    </div>
  </main>
</Layout>
```

### 5. Project Detail Page (`src/pages/work/[slug].astro`)

```astro
---
import Layout from "../../layouts/Layout.astro";
import ImageGallery from "../../components/ImageGallery";
import { getProjectBySlug } from "../../lib/portfolio";

const { slug } = Astro.params;
const project = await getProjectBySlug(slug!);
if (!project) return Astro.redirect("/404");
---

<Layout title={project.title}>
  <main>
    <div>
      <a href="/work">
        &larr; Back to work
      </a>

      {project.coverImage && (
        <div>
          <img
            src={project.coverImage}
            alt={project.title}
          />
        </div>
      )}

      <div>
        <span>{project.category}</span>
        {project.client && (
          <>
            <span>&middot;</span>
            <span>{project.client}</span>
          </>
        )}
        {project.year && (
          <>
            <span>&middot;</span>
            <span>{project.year}</span>
          </>
        )}
      </div>

      <h1>{project.title}</h1>

      {project.description && (
        <article set:html={project.description} />
      )}

      {project.galleryImages.length > 0 && (
        <ImageGallery client:only="react" images={project.galleryImages} alt={project.title} />
      )}

      {project.tags.length > 0 && (
        <div>
          {project.tags.map((tag) => (
            <span>{tag}</span>
          ))}
        </div>
      )}
    </div>
  </main>
</Layout>
```

### 6. Image Gallery React Island (`src/components/ImageGallery.tsx`)

```tsx
import { useState } from "react";

interface Props {
  images: string[];
  alt: string;
}

export default function ImageGallery({ images, alt }: Props) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  if (images.length === 0) return null;

  return (
    <>
      <div className="gallery-grid">
        {images.map((src, i) => (
          <button
            key={i}
            onClick={() => setActiveIndex(i)}
            className="gallery-item"
          >
            <img
              src={src}
              alt={`${alt} — image ${i + 1}`}
            />
          </button>
        ))}
      </div>

      {activeIndex !== null && (
        <div
          className="lightbox-overlay"
          onClick={() => setActiveIndex(null)}
        >
          <button
            className="lightbox-close"
            onClick={() => setActiveIndex(null)}
          >
            &times;
          </button>

          {images.length > 1 && (
            <>
              <button
                className="lightbox-nav prev"
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveIndex((activeIndex - 1 + images.length) % images.length);
                }}
              >
                &#8249;
              </button>
              <button
                className="lightbox-nav next"
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveIndex((activeIndex + 1) % images.length);
                }}
              >
                &#8250;
              </button>
            </>
          )}

          <img
            src={images[activeIndex]}
            alt={`${alt} — image ${activeIndex + 1}`}
            className="lightbox-image"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
```

> **Styling note:** Uses `.gallery-grid`, `.gallery-item`, `.lightbox-overlay`, `.lightbox-image`, `.lightbox-nav`, `.lightbox-close` from the designed component's `<style is:global>` block. See `COMPONENT_PATTERNS.md` → Image Gallery / Lightbox.

Key details:
- Renders as a grid; clicking opens a lightbox overlay
- Previous/next navigation wraps around
- `client:only="react"` — requires client-side rendering for `useState`
- No external dependencies — pure React

## Home Page Integration

To show featured projects on the home page, import `queryFeaturedProjects`:

```astro
---
import ProjectCard from "../components/ProjectCard.astro";
import { queryFeaturedProjects } from "../lib/portfolio";

const featured = await queryFeaturedProjects(3);
---

<section>
  <div>
    <h2>Featured Work</h2>
    <div>
      {featured.map((project) => (
        <ProjectCard project={project} />
      ))}
    </div>
  </div>
</section>
```

## Seed with Images

After seeding projects via REST, generate cover images (and optionally gallery images) following `../../shared/IMAGE_GENERATION.md` and `../../cms/CMS_FOUNDATIONS.md` → "Seeding with Images".

**Cover image prompt template:**

```
Project showcase image for [TITLE]. [BRAND AESTHETIC]. Color palette: [BRAND COLORS]. Editorial style. No text, no watermarks
```

**Patch field:** `coverImage`

**Optional gallery images** — generate 2-3 additional images per project for the `galleryImages` array. Note: this is slow (each image takes ~10-15s), so only do this if the user wants a fully populated portfolio.

```
Gallery image [N] for [TITLE]: [describe a specific aspect/angle of the project]. [BRAND AESTHETIC]. [BRAND COLORS]. No text, no watermarks
```

**Patch fields:** `coverImage`, optionally `galleryImages` (as an array of wixstatic URLs)

Example patch:

```
REST: PATCH https://www.wixapis.com/wix-data/v2/items/{projectId}
body: {
  "dataCollectionId": "Projects",
  "dataItem": {
    "data": {
      "coverImage": "<wixstatic-url>",
      "galleryImages": ["<wixstatic-url-1>", "<wixstatic-url-2>"]
    }
  }
}
```

## Testing

1. Create a "Projects" collection in the Wix dashboard → CMS with the schema above
2. Add 3+ projects with cover images, categories, and at least one with gallery images
3. Mark 1–2 as `featured: true`
4. Run `npx @wix/cli@latest dev`
5. `/work` — grid with category filter tabs
6. Click a category — filters projects
7. Click a project — detail page with gallery lightbox