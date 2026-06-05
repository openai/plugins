# Reference: Blog Pages

Blog listing, post detail, RSS feed, layout, SEO head component, and date formatting.

## Files to Create

| File | Purpose |
|------|---------|
| `src/pages/blog/index.astro` | Blog listing page |
| `src/pages/blog/[...slug].astro` | Blog post detail page (with RicosViewer) |
| `src/pages/rss.xml.js` | RSS feed |
| `src/layouts/BlogPost.astro` | Blog post layout wrapper |
| `src/components/BaseHead.astro` | SEO head component (OG/Twitter cards) |
| `src/components/FormattedDate.astro` | Date formatting helper |

---

## 1. SEO Head Component (`src/components/BaseHead.astro`)

```astro
---
import '../styles/global.css';

interface Props {
  title: string;
  description: string;
  image?: string;
}

const canonicalURL = new URL(Astro.url.pathname, Astro.site);

const { title, description, image = '/blog-placeholder-1.jpg' } = Astro.props;
---

<!-- Global Metadata -->
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<meta name="generator" content={Astro.generator} />

<!-- Canonical URL -->
<link rel="canonical" href={canonicalURL} />

<!-- Primary Meta Tags -->
<title>{title}</title>
<meta name="title" content={title} />
<meta name="description" content={description} />

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website" />
<meta property="og:url" content={Astro.url} />
<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:image" content={new URL(image, Astro.url)} />

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image" />
<meta property="twitter:url" content={Astro.url} />
<meta property="twitter:title" content={title} />
<meta property="twitter:description" content={description} />
<meta property="twitter:image" content={new URL(image, Astro.url)} />
```

> If the project already has a `<head>` component or `Layout.astro` with SEO tags, adapt the existing component instead of creating a new one. The key additions are the OG/Twitter meta tags with `image` support.

---

## 2. Formatted Date Component (`src/components/FormattedDate.astro`)

```astro
---
interface Props {
  date: Date;
}

const { date } = Astro.props;
---

<time datetime={date.toISOString()}>
  {
    date.toLocaleDateString('en-us', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }
</time>
```

---

## 3. Blog Post Layout (`src/layouts/BlogPost.astro`)

```astro
---
import BaseHead from '../components/BaseHead.astro';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
import FormattedDate from '../components/FormattedDate.astro';

interface Props {
  title: string;
  description?: string;
  pubDate: Date;
  updatedDate?: Date;
  heroImage?: string;
  tags?: Array<{ label: string; slug: string }>;
}

const { title, description, pubDate, updatedDate, heroImage, tags = [] } = Astro.props;
---

<html lang="en">
  <head>
    <BaseHead title={title} description={description ?? ''} />
    <style is:global>
      /* All BlogPost layout styles are created by the design skill.
         See COMPONENT_PATTERNS.md → Blog Post Content for the complete
         styling contract: .hero-image, .prose, .title, .date, .tags,
         .ricos-content overrides, etc. */
    </style>
  </head>

  <body>
    <Header />
    <main>
      <article>
        <div class="hero-image">
          {heroImage && <img width={1020} height={510} src={heroImage} alt="" />}
        </div>
        <div class="prose">
          <div class="title">
            <div class="date">
              <FormattedDate date={pubDate} />
              {
                updatedDate && (
                  <div class="last-updated-on">
                    Last updated on <FormattedDate date={updatedDate} />
                  </div>
                )
              }
            </div>
            <h1>{title}</h1>
            {tags.length > 0 && (
              <div class="tags">
                {tags.map((tag) => (
                  <span class="tag">{tag.label}</span>
                ))}
              </div>
            )}
            <hr />
          </div>
          <slot />
        </div>
      </article>
    </main>
    <Footer />
  </body>
</html>
```

> Adapt `Header` and `Footer` imports to match the project's existing components. If the project uses a different layout pattern (e.g., `Layout.astro` wrapper), use that instead and incorporate the blog-specific elements (hero image, date, title, tags).

---

## 4. Blog Listing Page (`src/pages/blog/index.astro`)

```astro
---
import { queryBlogPosts } from "../../lib/blog";
import BaseHead from "../../components/BaseHead.astro";
import Footer from "../../components/Footer.astro";
import FormattedDate from "../../components/FormattedDate.astro";
import Header from "../../components/Header.astro";
import { SITE_DESCRIPTION, SITE_TITLE } from "../../consts";

const posts = await queryBlogPosts();
---

<!doctype html>
<html lang="en">
  <head>
    <BaseHead title={SITE_TITLE} description={SITE_DESCRIPTION} />
    <style>
      /* Listing page styles are created by the design skill.
         Feature skill only wires queryBlogPosts() data. */
    </style>
  </head>
  <body>
    <Header />
    <main>
      <section>
        {
          posts.length === 0 ? (
            <div>There are no posts available.</div>
          ) : (
            <ul>
              {posts.map((post) => (
                <li>
                  <a href={`/blog/${post.slug}/`}>
                    {post.coverImageUrl && (
                      <img
                        width={720}
                        height={360}
                        src={post.coverImageUrl}
                        alt=""
                      />
                    )}
                    <h4 class="title">{post.title}</h4>
                    <p class="date">
                      <FormattedDate date={post.pubDate} />
                    </p>
                  </a>
                </li>
              ))}
            </ul>
          )
        }
      </section>
    </main>
    <Footer />
  </body>
</html>
```

> Adapt the layout to match the project's existing design. The key pattern is: `queryBlogPosts()` from the blog service, linking to `/blog/${post.slug}/`.

---

## 5. Blog Post Detail Page (`src/pages/blog/[...slug].astro`)

```astro
---
import RicosViewer from '../../components/RicosViewer';
import { getPostBySlug } from "../../lib/blog";
import BlogPost from '../../layouts/BlogPost.astro';

export const wixMetadata = {
  appDefId: "14bcded7-0066-7c35-14d7-466cb3f09103",
  pageIdentifier: "wix.blog.sub_pages.post",
  identifiers: {
    slug: "BLOG.POST.SLUG",
  },
};

const { slug } = Astro.params;
const post = await getPostBySlug(slug!);

if (!post) {
  return Astro.redirect("/blog");
}
---

<BlogPost
  title={post.title}
  description={post.excerpt}
  pubDate={post.pubDate}
  heroImage={post.coverImageUrl}
  tags={post.tags}
>
  <RicosViewer client:only="react" content={post.richContent} />
</BlogPost>
```

Critical details:
- **`wixMetadata` export is required** — it tells the Wix platform this page is a blog post page. The `appDefId` is the Wix Blog app's ID (constant, do not change). `identifiers.slug` maps the URL param to the blog post slug.
- **`client:only="react"` is required** — `@wix/ricos` is a React component; `client:only="react"` ensures it renders only on the client, avoiding SSR issues with React-dependent code.
- **`[...slug]` (rest param)** — uses Astro's rest parameter syntax, not `[slug]`, to match the full slug path.
- **`RicosViewer`** renders the rich content from the Wix Blog editor (images, videos, text formatting, embeds, etc.) using `quickStartViewerPlugins()` for full content-type support.
- **No `getStaticPaths()`** — Wix headless projects use `output: "server"` (SSR on Cloudflare Workers), so pages use `Astro.params` directly instead of static path generation.
- **404 handling** — `getPostBySlug` returns `null` for missing posts; redirect to `/blog` listing.
- **Ricos color overrides** — The BlogPost layout's `<style is:global>` block includes `.ricos-content` overrides that force `var(--color-text)` on all Ricos elements. Without these, blog text is invisible on dark themes.

---

## 6. RSS Feed (`src/pages/rss.xml.js`)

```javascript
import rss from '@astrojs/rss';
import { queryBlogPosts } from '../lib/blog';
import { SITE_TITLE, SITE_DESCRIPTION } from '../consts';

export async function GET(context) {
  const posts = await queryBlogPosts();
  return rss({
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    site: context.site,
    items: posts.map((post) => ({
      title: post.title,
      pubDate: post.pubDate,
      description: post.excerpt,
      link: `/blog/${post.slug}/`,
    })),
  });
}
```

> Requires the `site` property in `astro.config.mjs` (set in BLOG_SETUP.md step 1).