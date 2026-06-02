# Agent Return Contract

Coordination between agents uses **in-memory structured returns**, not sidecar files (`.wix/logs/*.md`, `.wix/seed-returns/*.json`, `.wix/image-urls.md`). Every agent returns a JSON block at the end of its completion message; the skill parses these returns directly from session context.

At end of run, the skill writes ONE file (`.wix/run.json`) aggregating every return. This is the only observability artifact on the project side.

## The JSON return is your sole output channel

Subagents MUST NOT write coordination files (`.wix/seed-returns/<pack>.json`, `.wix/image-urls.md`, `.wix/logs/*.md`, etc.). The orchestrator parses your fenced JSON block from the message body and either acts on the data directly or pipes it to a deterministic helper script via stdin (e.g. `emit-design-tokens.mjs`, `patch-decorative-slots.mjs`). Any data the orchestrator needs from you belongs under `data` in the return block — files in `.wix/` that aren't build-consumed (CSS, .d.ts) or external-system-owned (`wix.config.json`) are not part of the contract.

## Why structured returns, not files

Writing markdown files between agents assumes they're independent processes without shared memory. But subagents run as child model calls under the parent skill's context — they can return structured data directly. File-based coordination adds:

- ~10s per sidecar write (file I/O + narration)
- ~5s per sidecar read from the parent (another tool call)
- Coordination complexity (timing, status-line parsing, retry logic)

That overhead is pure critical-path cost with no benefit here.

## The contract

Every subagent's final message ends with a fenced JSON block (language tag: `json` or `jsonc`). Format:

~~~markdown
... agent's human-readable summary ...

```json
{
  "status": "complete" | "partial" | "failed",
  "phase": "<phase identifier — pack.seed / pack.components / pack.pages[*].name / design-system / image-phase-1-decorative / image-phase-2-entity>",
  "scope": "<scope string from the agent's prompt>",
  "summary": "<one-line description of what was done>",
  "data": { ... phase-specific structured data ... },
  "files": ["list", "of", "files", "written", "or", "modified"],
  "errors": [],
  "notes": "<optional — anything the parent skill should know>"
}
```
~~~

The JSON block MUST be the **last** content in the message. The parent skill parses the last fenced JSON block as the return.

### Timing is NOT the agent's responsibility

Prior versions of this contract asked agents to include `started` / `ended` ISO-8601 timestamps. **Remove those fields.** Agents fabricate placeholder timestamps (`T00:00:00Z` / `T00:05:00Z`) roughly 60% of the time, which makes `run.json` useless for perf comparison.

**Authoritative timing source is the runtime `duration_ms`** captured by the parent skill from task-notifications when the subagent completes. The orchestrator MUST prefer `duration_ms` over any agent-reported timing. If an older agent still emits `started`/`ended`, the orchestrator ignores them.

For Bash calls made by the skill itself (scaffold, env-pull, npm-install, app-install), wrap in `date -u` captures:

```bash
STARTED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# ... run the command ...
ENDED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# compute seconds and append to run.json
```

No LLM-generated timestamps anywhere in the observability pipeline.

### Observed failure mode — narrative ending instead of fenced JSON

Agents sometimes end with prose like:

> *"All three files are correctly written. Let me verify the key requirements… Everything looks good."*

…with no fenced JSON block at the end. The parent skill then has to reconstruct `data.products` etc. from narrative text — fragile, and when Phase 4 relies on pre-seeded data from Phase 1 Seed returns (see `SKILL.md` Step 7), a missing JSON block means Phase 4 agents don't get their pre-seeded data inline and fall back to re-querying the REST API, costing 5–15s each.

**Correct pattern — end with the fenced block, no trailing prose:**

~~~markdown
✅ CORRECT

All files written. Contract classes referenced: productCard, productGrid, optionPill, quantityBtn.

```json
{
  "status": "complete",
  "phase": "stores-components",
  "scope": "components",
  "summary": "Wrote React islands + utils; contract classes referenced: 11",
  "data": { ... },
  "files": [ ... ],
  "errors": []
}
```
~~~

~~~markdown
❌ WRONG — trailing prose after the block

```json
{ "status": "complete", ... }
```

All three files are correctly written. Let me verify the key requirements are met before returning.
~~~

~~~markdown
❌ WRONG — no JSON block at all

All three files are correctly written. The ProductPurchase island uses contract classes
throughout, AddToCartButton wires to @wix/ecom, and CartView handles the two-step
checkout redirect. Build should pass.
~~~

The parent skill looks for the **last** fenced JSON block in the message. A trailing sentence means it's no longer the last content; scanning falls back to heuristics. Just stop writing after the closing ` ``` `.

## Status semantics

| Status | Meaning | Parent action |
|--------|---------|---------------|
| `complete` | All work done successfully | Proceed to next phase |
| `partial` | Some work done, some failed — `errors` explains | Decide per-case: retry, work around, or fail the run |
| `failed` | Nothing usable produced — `errors` explains | Retry with corrective prompt or fail the run |

## Phase-specific `data` shapes

The skill uses `data` to carry information forward to later phases. Each phase has a known shape.

### Phase 1: stores seed

```json
{
  "status": "complete",
  "phase": "stores-seed",
  "scope": "seed",
  "summary": "Deleted 12 default products; created 3 on-brand products with variants",
  "data": {
    "products": [
      {
        "id": "2d1bce83-...",
        "name": "Tero Dining Table",
        "slug": "tero-dining-table",
        "variantId": "ffc1caa2-...",
        "price": 2890,
        "inventory": 12,
        "sku": "TAB-TERO-OAK"
      }
    ],
    "deletedCount": 12,
    "createdCount": 3
  },
  "files": [],
  "errors": []
}
```

Phase 4 agents consume `data.products[*].slug` and `data.products[*].variantId` to wire live SDK queries.

### Phase 1: CMS seed

```json
{
  "status": "complete",
  "phase": "cms-seed",
  "scope": "seed",
  "data": {
    "collections": [
      {
        "name": "about-content",
        "itemIds": ["665f3363-..."],
        "fields": ["heading", "body", "image"]
      },
      {
        "name": "faq",
        "itemIds": ["abc", "def", "ghi", "jkl", "mno", "pqr"],
        "fields": ["question", "answer", "sortOrder"]
      }
    ]
  }
}
```

Phase 4 CMS page agents reference these collection names; the image agent attaches entity images to CMS items by ID.

### Phase 2: shared wiring

```json
{
  "status": "complete",
  "phase": "stores-components",
  "scope": "components",
  "summary": "Wrote React islands + utils; wired analytics; contract classes referenced: 7",
  "data": {
    "islands": ["ProductPurchase.tsx", "CartView.tsx", "AddToCartButton.tsx", "CartBadge.tsx"],
    "utils": ["wix-image.ts", "analytics.ts"],
    "astroComponents": ["SeoTags.astro"]
  },
  "files": [
    "src/utils/wix-image.ts",
    "src/utils/analytics.ts",
    "src/components/SeoTags.astro",
    "src/components/AddToCartButton.tsx",
    "src/components/CartBadge.tsx",
    "src/components/ProductPurchase.tsx",
    "src/components/CartView.tsx"
  ]
}
```

### Phase 2: page rewrites

```json
{
  "status": "complete",
  "phase": "stores-pages-products",
  "scope": "pages-products",
  "data": {
    "pagesWired": 2,
    "wixMetadataExported": true,
    "seoTagsMounted": true,
    "analyticsEvents": ["AddProductImpression", "ClickProduct", "ViewContent"]
  },
  "files": [
    "src/pages/products/index.astro",
    "src/pages/products/[slug].astro",
    "src/components/ProductCard.astro"
  ]
}
```

### Designer foundation

```json
{
  "status": "complete",
  "phase": "design-system",
  "data": {
    "contractKeys": 19,
    "cssLines": 247,
    "fonts": ["Cormorant Garamond", "DM Sans"],
    "palette": {"cream": "#FFF8F0", "charcoal": "#1A1A1A", "roseGold": "#B76E79"}
  },
  "files": [
    "src/styles/global.css",
    "src/layouts/Layout.astro",
    "src/components/Navigation.astro",
    "src/components/Footer.astro",
    ".wix/design-tokens.css"
  ]
}
```

### Designer page groups

```json
{
  "status": "complete",
  "phase": "designer-store-pages",
  "data": {
    "pagesDesigned": ["/products", "/products/[slug]", "/cart", "/thank-you"],
    "placeholderDataUsed": true,
    "contractClassesHonored": 11
  },
  "files": [
    "src/pages/products/index.astro",
    "src/pages/products/[slug].astro",
    "src/pages/cart.astro",
    "src/pages/thank-you.astro",
    "src/components/ProductCard.astro",
    "src/components/ProductPurchase.astro",
    "src/components/CartView.astro"
  ]
}
```

### Images (split into two image phases, dispatched separately)

The image agent runs in two scopes dispatched by the parent in different steps. Each emits its own return block.

**`image-phase-1-decorative` — dispatched in `SEED.md` Step 2 Wave 3 batch (no dependencies):**

```json
{
  "status": "complete",
  "phase": "image-phase-1-decorative",
  "scope": "image-phase-1-decorative",
  "summary": "Generated 3 decorative images; uploaded to Wix Media; returned slot→URL map",
  "data": {
    "decorativeCount": 3,
    "purposes": ["hero", "about", "background"],
    "slots": {
      "hero":  "https://static.wixstatic.com/media/...",
      "about": "https://static.wixstatic.com/media/...",
      "background": "https://static.wixstatic.com/media/..."
    },
    "model": "google:4@2",
    "totalCredits": 0.297
  },
  "files": [],
  "errors": []
}
```

**`image-phase-2-entity` — dispatched in Step 7 (Phase 1 Seed return data inline in prompt):**

```json
{
  "status": "complete",
  "phase": "image-phase-2-entity",
  "scope": "image-phase-2-entity",
  "summary": "Generated + attached images for 6 products and 1 CMS item",
  "data": {
    "entityCount": { "products": 6, "cmsAboutContent": 1, "blogPosts": 0 },
    "model": "google:4@2",
    "totalCredits": 0.693
  },
  "files": [],
  "errors": []
}
```

(Image agent writes to Wix Media via REST, not to project files — Image Phase 2 `files` is empty.)

## Failure returns

On `failed` or `partial`, `errors` is populated and `data` may still contain partial results:

```json
{
  "status": "partial",
  "phase": "stores-pages-products",
  "errors": [
    {
      "file": "src/pages/products/[slug].astro",
      "code": "MISSING_SEO_DATA",
      "message": "product.seoData was null; fell back to product.name for <title>",
      "severity": "warning"
    }
  ],
  "data": {...}
}
```

Severity levels: `warning` (keep running), `error` (parent should retry), `fatal` (parent must stop).

## Final `.wix/run.json` (written once by the skill at end of run)

The skill aggregates every agent return into one file.

**Timing is required** — the `run` object MUST include `started`, `ended`, and `totalSeconds`, and every entry in `phases` MUST include `seconds`. All timing values are captured by the parent skill (from runtime `duration_ms` for subagents, from `date -u` wraps for its own Bash calls) — agents do not self-report. If timing is missing for any phase, record `seconds: null` + `errors: [{code: "MISSING_TIMING"}]` and investigate what broke capture. See `skills/wix-headless/SKILL.md` § "Timing — required in run.json" for the capture protocol.

Example:

```json
{
  "version": "1.0",
  "run": {
    "started": "2026-01-15T09:16:14Z",
    "ended": "2026-01-15T09:28:03Z",
    "totalSeconds": 709,
    "brand": "Acme Coffee",
    "prompt": "I want to sell tables online",
    "verticals": ["stores", "cms"],
    "packs": ["stores", "cms"]
  },
  "outcome": {
    "build": "success",
    "previewUrl": "https://goj5lj-tabula-...-alexp775.wix-host.com",
    "dashboardUrl": "https://manage.wix.com/dashboard/<siteId>"
  },
  "phases": [
    { "phase": "scaffold", "status": "complete", "seconds": 45 },
    { "phase": "app-install-stores", "status": "complete", "seconds": 6 },
    { "phase": "env-pull", "status": "complete", "seconds": 4 },
    { "phase": "npm-install", "status": "complete", "seconds": 42, "packageCount": 725 },
    { "phase": "stores-seed", "status": "complete", "seconds": 112, "data": { ... } },
    { "phase": "cms-seed", "status": "complete", "seconds": 98, "data": { ... } },
    { "phase": "stores-components", "status": "complete", "seconds": 134, "data": { ... } },
    { "phase": "design-system", "status": "complete", "seconds": 165, "data": { ... } },
    { "phase": "designer-home", "status": "complete", "seconds": 287, "data": { ... } },
    { "phase": "designer-static", "status": "complete", "seconds": 265, "data": { ... } },
    { "phase": "designer-store-pages", "status": "complete", "seconds": 298, "data": { ... } },
    { "phase": "stores-pages-products", "status": "complete", "seconds": 89, "data": { ... } },
    { "phase": "stores-pages-cart-checkout", "status": "complete", "seconds": 67, "data": { ... } },
    { "phase": "stores-pages-home-and-nav", "status": "complete", "seconds": 54, "data": { ... } },
    { "phase": "pages", "status": "complete", "seconds": 78, "data": { ... } },
    { "phase": "image-phase-1-decorative", "status": "complete", "seconds": 112, "data": { "decorativeCount": 3, ... } },
    { "phase": "image-phase-2-entity", "status": "complete", "seconds": 287, "data": { "entityCount": { "products": 6, "cmsAboutContent": 1 }, ... } },
    { "phase": "build", "status": "complete", "seconds": 9 },
    { "phase": "preview", "status": "complete", "seconds": 21 }
  ],
  "notes": []
}
```

Observations post-run (including this doc's example):
- Total serial wall time ≈ max parallel paths, not sum of seconds
- `data` blocks preserve what each agent returned — recoverable without re-reading agent transcripts
- `files` lists omitted from aggregate; query individual phase `data` if needed

## Common failure modes

Agents should check their output for these before returning `complete`:

### Astro/React

| Failure | How to detect | Fix |
|---------|---------------|-----|
| HTML-style comments in `.astro` frontmatter | `grep '<!--' *.astro frontmatter` | Use `//` or `/* */` — frontmatter is TypeScript |
| Missing `wixMetadata` on `/products/[slug]` | Check exports | Add the metadata export — required for Wix platform indexing |
| `import { products }` instead of `productsV3` | `grep 'from "@wix/stores"' -- import line` | V1 silently returns 0 on V3 catalogs |
| Missing `variantId` in cart operations | Check `catalogReference.options` | Always include — single-variant products have one |
| React island using default Tailwind color class | `grep 'bg-blue-\|bg-green-\|text-red-\|bg-gray-' *.tsx` | Use brand `@theme` utilities (`bg-bark`, `text-cream`) or contract class names |

### REST API

| Failure | How to detect | Fix |
|---------|---------------|-----|
| `UNSUPPORTED_FORM_NAMESPACE` after app install | Error on first REST call post-install | Wait 10s, retry up to 3x (namespace propagation) |
| `curl` with stringified `body` | Endpoint rejects the call shape | Pass `body` as a real JSON object via `-d` (not a stringified blob). See `AUTHENTICATION.md` for the standard REST headers. |
| 401/403 on Wix REST call | Expired or wrong token | Re-mint per `AUTHENTICATION.md` recovery ladder; one retry then surface body |

### Build

| Failure | How to detect | Fix |
|---------|---------------|-----|
| `Legacy HTML single-line comments` | `npx @wix/cli@latest build` stderr | See Astro/React row 1 above — Phase 2 agent emitted HTML comments |
| `Missing environment variable WIX_CLIENT_ID` | Build stderr | Run `npx @wix/cli@latest env pull --json` then retry |
| `Cannot find module '@wix/…'` | Build stderr | npm install didn't include that package; check pack's `packages` list |

## Notes for agent authors

When writing a new agent, include a **Returns** section in its `INSTRUCTIONS.md` that lists:

1. The `phase` identifier this agent emits
2. The exact `data` shape for successful returns
3. Known `error.code` values
4. Required `files` entries

Agents should produce the JSON return block deterministically — don't let creative prose overrun the fenced block. Parent skill parsing assumes the JSON is well-formed and complete.