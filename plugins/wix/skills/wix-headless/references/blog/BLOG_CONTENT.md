# Recipe: Seed Initial Blog Posts via REST

Create 3 on-brand blog posts so the blog has real content on first preview.

> **Critical Rules — Read Before Starting**
> 1. **Seed content is required** — a blog with zero posts on first preview is a build failure. Do not skip this section.
> 2. **Re-publish after PATCH** — updating a published post sets `hasUnpublishedChanges: true`. Call `publish` again or visitors see the old version.
> 3. **Use `@wix/blog`, not `@wix/data`** — blog posts are NOT CMS collections.
> 4. **`RICH_CONTENT` fieldset required** — without it, `post.richContent` is undefined and rendering fails.

> **Required in the Seed phase.** When dispatched with `Scope: seed`, the CLI-minted REST token and discovery context are guaranteed available. Always execute this section — do not skip. A blog with zero posts on first preview is a build failure.
>
> **Skip only for standalone invocations** where the Blog skill is invoked directly AND CLI token mint fails after recovery. In that case, the user can create posts manually in the Wix dashboard.

## Step 0: Ensure Blog App Is Installed

Before querying blog data, verify the Blog app is installed:

1. **Probe** — `REST: POST https://www.wixapis.com/blog/v3/posts/query`
2. **If the API returns a "REQUIRED_APP_NOT_INSTALLED" error** → install the Wix Blog app:
   ```
   REST: POST https://www.wixapis.com/apps-installer-service/v1/app-instance/install
   body: {
     "tenant": { "tenantType": "SITE", "id": "<siteId>" },
     "appInstance": { "appDefId": "14bcded7-0066-7c35-14d7-466cb3f09103", "enabled": true }
   }
   ```
   > Translate this prose-HTTP form into the full `curl` tool-call shape — pass `body` as JSON in `-d` (NOT a stringified JSON). See `../shared/AUTHENTICATION.md` for the standard REST headers.

   Then retry the probe query to confirm installation succeeded.
3. **If the probe succeeds** → proceed to Step 1.

---

## Step 1: Get Member ID

Blog posts require a `memberId` (the post author). Fetch the first site member:

```
REST: GET https://www.wixapis.com/members/v1/members
```

Extract the first member's `_id` from the response. This will be used as the author for all posts.

## Step 2: Design 3 On-Brand Blog Posts

No API call — use discovery context (business type, brand name, tone, industry) to plan 3 posts:

- Titles, summaries, and rich content appropriate for the business
- Content should demonstrate different Ricos node types (paragraphs, headings, code blocks, lists, blockquotes)
- Posts should feel like real content a reader would engage with, not placeholder text

**Post design guidelines by business type:**

| Business Type | Post 1 | Post 2 | Post 3 |
|--------------|--------|--------|--------|
| AI / tech blog | Architecture deep-dive | Practical comparison (X vs Y) | Lessons learned / field report |
| Skincare / beauty | Ingredient science spotlight | Routine guide (morning/evening) | Myth-busting or FAQ |
| Food / restaurant | Behind the recipe | Seasonal menu spotlight | Sourcing / farm-to-table story |
| Fitness / wellness | Training methodology breakdown | Nutrition or recovery guide | Client transformation story |
| Fashion / retail | Trend analysis | Styling guide | Behind the brand / process |
| General business | Industry insight | How-to guide | Company news / milestone |

Adapt titles, tone, and content to match the brand's voice and style.

## Step 3: Create Posts

For each post, call `POST /blog/v3/draft-posts` with `publish: true` to create and immediately publish.

> Do not include the `media` field — cover images are handled separately by the image agent after post creation.

```
REST: POST https://www.wixapis.com/blog/v3/draft-posts
body: {
  "draftPost": {
    "title": "<Post Title>",
    "memberId": "<member-id-from-step-1>",
    "richContent": {
      "nodes": [
        {
          "type": "HEADING",
          "id": "<unique-id>",
          "nodes": [
            { "type": "TEXT", "id": "", "nodes": [], "textData": { "text": "Section Heading", "decorations": [] } }
          ],
          "headingData": { "level": 2 }
        },
        {
          "type": "PARAGRAPH",
          "id": "<unique-id>",
          "nodes": [
            { "type": "TEXT", "id": "", "nodes": [], "textData": { "text": "Paragraph content here.", "decorations": [] } }
          ],
          "paragraphData": {}
        }
      ]
    }
  },
  "publish": true
}
```

### Ricos JSON Node Reference

Use these node types to build rich, varied content:

| Node Type | Structure | Use For |
|-----------|-----------|---------|
| `PARAGRAPH` | `{ type: "PARAGRAPH", id, nodes: [TEXT], paragraphData: {} }` | Body text |
| `HEADING` | `{ type: "HEADING", id, nodes: [TEXT], headingData: { level: 2 } }` | Section headers (level 2–4) |
| `CODE_BLOCK` | `{ type: "CODE_BLOCK", id, nodes: [TEXT], codeBlockData: { language: "javascript" } }` | Code snippets |
| `BULLETED_LIST` | `{ type: "BULLETED_LIST", id, nodes: [LIST_ITEM] }` | Unordered lists |
| `LIST_ITEM` | `{ type: "LIST_ITEM", id, nodes: [PARAGRAPH] }` | Items inside BULLETED_LIST |
| `BLOCKQUOTE` | `{ type: "BLOCKQUOTE", id, nodes: [PARAGRAPH] }` | Pull quotes, callouts |
| `TEXT` | `{ type: "TEXT", id: "", nodes: [], textData: { text: "...", decorations: [] } }` | Inline text (leaf node inside paragraphs, headings, etc.) |

**Tips:**
- Container nodes (PARAGRAPH, HEADING, etc.) need a unique `id` (use any string, e.g., `"n1"`, `"n2"`). TEXT nodes can use an empty string `""` for `id`.
- TEXT nodes are always leaf nodes inside PARAGRAPH, HEADING, CODE_BLOCK, etc.
- LIST_ITEM nodes contain PARAGRAPH nodes (not TEXT directly)
- Mix at least 3 different node types per post for visual variety
- Create all 3 posts in sequence (one `curl` call per post)
- **Best practice:** include all fields (title, content, media) in the initial creation call to avoid needing a re-publish

> **Re-publish after PATCH:** If you update a published post (e.g., adding a cover image via PATCH after creation), it becomes `hasUnpublishedChanges: true`. You must call `POST /blog/v3/draft-posts/{draftPostId}/publish` to re-publish. To avoid this, include media in the initial creation call.

## Step 4: Verify

Query published posts to confirm all 3 exist:

```
REST: POST https://www.wixapis.com/blog/v3/posts/query
body: {
  "query": {
    "paging": { "limit": 10 }
  }
}
```

Confirm 3 posts are returned. Report post titles to the user.

### Step 5: Log Results

Write a sidecar file at `.wix/logs/blog-data.md` (see `../../shared/LIFECYCLE_LOG.md` for the sidecar contract). Do **not** append to `.wix/lifecycle.log.md` directly — the orchestrator concatenates all sidecars at the end. Use a `####` heading so the entry nests under `### features-orchestrator` in the assembled log:

```markdown
## blog
- Status: complete
- Content: {n} posts published ({post titles})
- Images: {generated (n/n attached) | skipped (user declined) | not attempted}
```
