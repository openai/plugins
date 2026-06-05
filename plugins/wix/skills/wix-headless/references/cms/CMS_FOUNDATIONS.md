# CMS Foundations — Seeding via `@wix/data` REST (business track)

The **seeding** half of CMS foundations: create collections and insert + verify sample items via the Wix Data REST API. This is frontend-blind business-track work — a collection and its items are the same regardless of what renders them.

> **Rendering / page code lives in the astro frontend track.** The service-module template, `@wix/data` SDK query patterns, image resolution, Ricos rendering, and category filtering are **not** here — they are in `<SKILL_ROOT>/references/astro/cms/CMS_FOUNDATIONS.md` (the `pages` scope's doc). This file is consumed by the `seed` scope. The `cms/INSTRUCTIONS.md` router points each scope at the right half.

## Collection ID Format (seeding-relevant)

Native (user-created) CMS collections use **just the collection name** — no namespace prefix (e.g. `"about-content"`, `"faq"`, `"Projects"`). Only Wix App collections use a `<namespace>/<name>` format. Use the exact `id` you create here; verify with `GET /wix-data/v2/collections?fields=id` (standard REST headers from `../shared/AUTHENTICATION.md`). Never guess — the dashboard display name may differ from the ID.

## Seeding via REST (Conditional)

Check whether the collection already has data; seed sample items only if empty. Calls go through `curl` against `wixapis.com` with the site-scoped REST token (see `../shared/AUTHENTICATION.md`) — no SDK, no MCP.

1. Query the collection — if items exist, skip seeding
2. If empty, create the collection and insert sample items via the REST calls below
3. Design sample data that matches the business type from the functional plan

### Create collection (if it doesn't exist)

```
REST: POST https://www.wixapis.com/wix-data/v2/collections
body: {
  "collection": {
    "id": "about-content",
    "displayName": "About Content",
    "fields": [
      { "key": "heading", "displayName": "Heading", "type": "TEXT" },
      { "key": "body", "displayName": "Body", "type": "RICH_TEXT" },
      { "key": "image", "displayName": "Image", "type": "IMAGE" }
    ]
  }
}
```

### Insert item WITH field data

**This is the critical step that must include actual field values.** Creating an item without populating the `data` object results in an empty record — the collection schema exists but the item has no content.

```
REST: POST https://www.wixapis.com/wix-data/v2/items
body: {
  "dataCollectionId": "about-content",
  "dataItem": {
    "data": {
      "heading": "Our Story",
      "body": "<p>Founded on a belief that...</p><p>We source the finest...</p>"
    }
  }
}
```

The response returns the created item's `_id` — collect these for the Phase 1 return contract.

**Every text field must be populated in the `data` object.** Do not create items with empty `data: {}` and expect Phase 2 or the image agent to fill in text fields — they only handle their own scope (pages and images respectively).

For FAQ items, include both `question` and `answer` plus `sortOrder`:

```
REST: POST https://www.wixapis.com/wix-data/v2/items
body: {
  "dataCollectionId": "faq",
  "dataItem": {
    "data": {
      "question": "What is your return policy?",
      "answer": "We accept returns within 30 days of purchase...",
      "sortOrder": 1
    }
  }
}
```

### Verify inserts with a live query (mandatory)

After inserting all items, **query each collection once** and confirm every field you sent is present in the stored `data`. A POST without errors does NOT prove the content persisted — the API has accepted insert bodies with missing fields before, and the failure is invisible until a human opens the page.

```
REST: POST https://www.wixapis.com/wix-data/v2/items/query
body: { "dataCollectionId": "<collection>" }
```

For every returned item, confirm its `data` object contains every text field you POSTed (`heading`, `body`, `question`, `answer`, etc.). If any field is missing:

- Do NOT return `status: "complete"`.
- Re-insert the item (a DELETE then POST is safest — PUT replaces the whole record) and re-verify.
- If re-insert fails twice, return `status: "partial"` with `errors: [{code: "SEED_FIELD_MISSING", collection: "<c>", itemId: "<id>", missingFields: [...]}]`.

A CMS seeder can return `complete` for an about-content item, then Image Phase 2 silently wipes its `heading` + `body` via a destructive full-record PUT. The verify-after-insert step here plus the read-merge-PUT rule in the images agent makes that class of data loss unreachable.

### Seeding with Images

For use cases with image fields (`photo`, `coverImage`, `galleryImages`),
follow `../shared/IMAGE_GENERATION.md` (Steps 1–2) for Wix AI image
generation and Wix Media import. Image generation goes through the same
CLI-minted REST token as the rest of this skill — do not ask the user for
credentials.

**Workflow:**

1. Seed all items first (text fields only, no images) using `POST /wix-data/v2/items` as shown in § "Insert item WITH field data" above. Every text field must have a value in the `data` object — empty items cause "Content coming soon" placeholder pages.
2. Run the verify-after-insert query (see § "Verify inserts with a live query" above) before touching images.
3. Generate images via Wix AI (IMAGE_GENERATION.md Steps 1–2) using the prompt templates from each use-case reference
4. Attach each image by reading the existing item, merging, and writing the whole record back via PUT. Do NOT use PATCH here — the endpoint expects a JsonPatch `fieldModifications` array and rejects the `{dataItem:{data}}` body. Do NOT PUT with just `{image}` — PUT replaces the entire record and erases heading/body.

```
# Step a: read the existing item
REST: POST https://www.wixapis.com/wix-data/v2/items/query
body: {
  "dataCollectionId": "CollectionName",
  "query": { "filter": { "_id": { "$in": ["{itemId}"] } } }
}

# Step b: merge image into existing data and PUT the full record
REST: PUT https://www.wixapis.com/wix-data/v2/items/{itemId}
body: {
  "dataCollectionId": "CollectionName",
  "dataItem": {
    "id": "{itemId}",
    "data": { ...existingData, "{imageField}": "<wixstatic-url>" }
  }
}
```

`...existingData` must include every non-system field from step a (system fields `_id`, `_owner`, `_createdDate`, `_updatedDate` don't need to be echoed). Skipping the merge wipes seeded text fields and ships an empty About page.

**Prompt templates** — each use-case reference defines its own prompt template (see the "Seed with Images" section in `../astro/cms/TEAM_DIRECTORY.md`, `../astro/cms/PORTFOLIO.md`, `../astro/cms/RESOURCE_LIBRARY.md`). Always incorporate brand context from the discovery/design phases.

**Constraints:**
- Never block the main flow on image failures — text data is already seeded
- Runware image URLs are short-lived — import to Wix Media immediately after generation
- If image generation or import fails for a single item, skip that item and continue with others
- If all generation fails (credits exhausted, upstream Runware errors), write the sidecar with `Status: partial` and proceed — but always attempt first
- `../astro/cms/FAQ_KNOWLEDGE_BASE.md` has no image fields — skip image generation for FAQ use cases

## Return Results

Emit a structured JSON block at the end of your completion message per `../shared/RETURN_CONTRACT.md`. Do NOT write sidecar files.

```json
{
  "status": "complete",
  "phase": "cms-seed",
  "scope": "seed-seed",
  "summary": "Created {N} collections; seeded {M} items; verified every field persisted",
  "data": {
    "collections": [
      {
        "name": "<collection-slug>",
        "itemIds": ["<id>", "..."],
        "fields": ["<field>", "..."],
        "storedFields": ["<field>", "..."],
        "sampleValues": { "<field>": "<short sample value>" },
        "imageField": "<field name or null>"
      }
    ]
  },
  "files": [],
  "errors": []
}
```

- `storedFields` MUST match the real keys seen in the verify-after-insert query response's `data` object (see § "Verify inserts with a live query"). Downstream pages agents compare against this — if you return `fields: ["heading", "body"]` but only `heading` was actually stored, pages render empty bodies.
- `sampleValues` is a single example item's field-to-short-string map. Lets downstream agents spot-check that content is real without another REST round-trip. Truncate rich-text bodies to the first ~80 characters.
- For collections without image fields (e.g., FAQ), set `imageField: null`.
- The JSON block MUST be the last content in your message.

## Testing (seed-side)

1. Create a data collection in the Wix dashboard → CMS (or via the REST `POST /collections` above).
2. Add fields matching the use case schema (see the specific use case reference under `../astro/cms/`).
3. Add at least 2–3 items with all fields populated, including `slug` and `published` (if applicable).
4. Run the verify-after-insert query and confirm every field persisted.

Page rendering / SDK query patterns for these collections are in `../astro/cms/CMS_FOUNDATIONS.md`.
