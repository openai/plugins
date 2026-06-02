---
name: blog
description: "Blog — post listing, post detail with rich content, RSS feed, sitemap."
triggers: ["blog", "publish articles", "write posts", "content site", "editorial", "journal", "newsletter"]

features:
  - name: "Blog"
    description: "Publish posts with a listing page, individual post pages with rich content rendering, and an RSS feed."
  - name: "RSS and sitemap"
    description: "Auto-generated RSS feed and XML sitemap for search engine discovery."

apps:
  - name: "Wix Blog"
    appDefId: "14bcded7-0066-7c35-14d7-466cb3f09103"

routes:
  - route: "/blog"
  - route: "/blog/[slug]"
    name: "Blog Post"   # path-derivation would produce "Blog [slug]" — override with the user-facing label
  - route: "/rss.xml"

disabled: false
---

# Blog Pack

Loaded when the user's prompt mentions blogging, publishing, or editorial content.

> **Discovery contract.** Phase 1 reads only the frontmatter above. Phase 2+ implementation (post seeding, RSS, page composition, ricos rendering) lives in an upstream skill plus this skill's own `templates/blog/` + `references/blog/INSTRUCTIONS.md`:
>
> - `@skills/wix-manage` ships the seeding recipe — `references/blog/how-to-create-blog-posts.md`.