# Reference: Blog Setup

Prerequisites, dependencies, blog service module, and astro config changes for the Wix Blog app integration.

## Prerequisites

- A Wix Managed Headless project (has `wix.config.json` and `astro.config.mjs`)
- The **Wix Blog app** installed on the connected Wix site (installed via the apps-installer REST endpoint after scaffolding — see `../../blog/BLOG_CONTENT.md` Step 0)
- At least one published blog post in the Wix dashboard

## Package Installation

```bash
npm install @wix/blog @wix/ricos @astrojs/rss @astrojs/sitemap
```

## Files to Create / Modify

| File | Action | Purpose |
|------|--------|---------|
| `astro.config.mjs` | Modify | Add `site` property and `sitemap()` integration |
| `src/lib/blog.ts` | Create | Blog service — queries posts, resolves categories/tags/media |
| `src/consts.ts` | Create | Site-wide constants (title, description) |
| `src/components/RicosViewer.tsx` | Create | React wrapper for `@wix/ricos` RicosViewer |

---

## 1. Astro Config Changes (`astro.config.mjs`)

Add the `site` property (required for RSS and sitemap) and the `sitemap()` integration:

```javascript
// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import wix from "@wix/astro";
import wixPages from "@wix/astro-pages";

// https://astro.build/config
export default defineConfig({
  site: "https://example.com",
  integrations: [wix(), wixPages(), sitemap()]
});
```

> Replace `"https://example.com"` with the actual site URL. The `site` property is required for `@astrojs/rss` and `@astrojs/sitemap` to generate correct URLs.

> `wix()` and `wixPages()` should already be in the config from project scaffolding. Only add `sitemap()` and the `site` property.

---

## 2. Site Constants (`src/consts.ts`)

```typescript
// Place any global data in this file.
// You can import this data from anywhere in your site by using the `import` keyword.

export const SITE_TITLE = 'Astro Blog';
export const SITE_DESCRIPTION = 'Welcome to my website!';
```

> Update `SITE_TITLE` and `SITE_DESCRIPTION` to match the user's site.

---

## 3. RicosViewer React Wrapper (`src/components/RicosViewer.tsx`)

A thin React wrapper around `@wix/ricos` for use in Astro pages with `client:only="react"`.

```tsx
import { quickStartViewerPlugins, RicosViewer } from '@wix/ricos';
import '@wix/ricos/css/all-plugins-viewer.css';

const plugins = quickStartViewerPlugins();

export default function RicosContentViewer({ content }: { content: any }) {
  if (!content) return null;
  return (
    <div className="ricos-content">
      <RicosViewer content={content} plugins={plugins} />
    </div>
  );
}
```

Key details:
- `quickStartViewerPlugins()` is initialized at module level (once, not per render) — provides full content-type support (links, tables, galleries, embeds, etc.)
- The CSS import is bundled by Vite into the client chunk
- No key renaming needed — `@wix/ricos` accepts camelCase keys from the `@wix/blog` SDK directly
- Used in Astro pages as `<RicosViewer client:only="react" content={post.richContent} />`
- The `.ricos-content` wrapper div provides a CSS hook for theme color overrides — the Ricos library CSS hardcodes `color: rgb(0, 0, 0)` on paragraph and list elements, which is invisible on dark themes

---

## 4. Blog Service Module (`src/lib/blog.ts`)

This service module handles all Wix Blog SDK calls, resolving categories, tags, and media references into ready-to-use data.

```typescript
import { posts, categories, tags } from "@wix/blog";
import { media } from "@wix/sdk";

export interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  coverImageUrl?: string;
  date: string;
  pubDate: Date;
  category?: string;
  richContent: any;
  tags: Array<{ label: string; slug: string }>;
}

export async function queryBlogPosts(limit?: number): Promise<BlogPost[]> {
  let query = posts
    .queryPosts({ fieldsets: ["RICH_CONTENT", "CONTENT_TEXT"] })
    .descending("firstPublishedDate");

  if (limit) query = query.limit(limit);

  const { items } = await query.find();

  return Promise.all(
    items.map(async (item) => {
      const resolvedCategories = await Promise.all(
        (item.categoryIds || []).map(async (id) => {
          const { category } = await categories.getCategory(id);
          return category!;
        })
      );

      const resolvedTags = await Promise.all(
        (item.tagIds || []).map(async (id) => {
          const tag = await tags.getTag(id);
          return { label: tag.label!, slug: tag.slug! };
        })
      );

      const imageUrl = item.media?.wixMedia?.image
        ? media.getImageUrl(item.media.wixMedia.image).url
        : undefined;

      const pubDate = new Date(item.firstPublishedDate ?? "");

      return {
        slug: item.slug!,
        title: item.title!,
        excerpt: item.excerpt ?? "",
        coverImageUrl: imageUrl,
        date: pubDate.toLocaleDateString("en-us", {
          year: "numeric",
          month: "long",
          day: "numeric",
        }),
        pubDate,
        category: resolvedCategories[0]?.label,
        richContent: item.richContent,
        tags: resolvedTags,
      };
    })
  );
}

export async function getPostBySlug(slug: string): Promise<BlogPost | null> {
  const { items } = await posts
    .queryPosts({ fieldsets: ["RICH_CONTENT", "CONTENT_TEXT"] })
    .eq("slug", slug)
    .find();

  const item = items[0];
  if (!item) return null;

  const resolvedCategories = await Promise.all(
    (item.categoryIds || []).map(async (id) => {
      const { category } = await categories.getCategory(id);
      return category!;
    })
  );

  const resolvedTags = await Promise.all(
    (item.tagIds || []).map(async (id) => {
      const tag = await tags.getTag(id);
      return { label: tag.label!, slug: tag.slug! };
    })
  );

  const imageUrl = item.media?.wixMedia?.image
    ? media.getImageUrl(item.media.wixMedia.image).url
    : undefined;

  const pubDate = new Date(item.firstPublishedDate ?? "");

  return {
    slug: item.slug!,
    title: item.title!,
    excerpt: item.excerpt ?? "",
    coverImageUrl: imageUrl,
    date: pubDate.toLocaleDateString("en-us", {
      year: "numeric",
      month: "long",
      day: "numeric",
    }),
    pubDate,
    category: resolvedCategories[0]?.label,
    richContent: item.richContent,
    tags: resolvedTags,
  };
}
```

Key details:
- `categories.getCategory(id)` returns `{ category }` (envelope) — destructure it
- `tags.getTag(id)` returns the `BlogTag` directly — do NOT destructure as `{ tag }`
- `media.getImageUrl(ref).url` resolves Wix media references to real URLs
- `getPostBySlug` returns `null` for missing posts — pages must handle this with a redirect
- `queryBlogPosts()` sorts by `firstPublishedDate` descending (newest first)
- `RICH_CONTENT` fieldset is required to get renderable content for `RicosViewer`