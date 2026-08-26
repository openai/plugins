---
name: canva-bulk-create
description: Bulk-create Canva designs from tabular data using a brand template with autofill fields, producing one design per row. Use when users say "bulk create designs from this CSV", "generate one design per row", "create a design for each product", "batch generate from a template", or "autofill a template from a spreadsheet". Accepts any tabular data source — uploaded files, pasted tables, JSON, or URLs.
---

# Canva Bulk Design Creation

Create one Canva design per row of data by autofilling a brand template with data tags.

## Workflow

### Step 1: Get the Data

Accept data in any form the user provides and extract a list of rows with named columns:

- **Uploaded file**: read the file and extract headers and rows
- **Pasted data**: parse markdown tables, tab-separated values, or JSON arrays directly from the chat
- **URL**: fetch the resource and parse the response as tabular data

If no data has been provided, ask the user to share it in whatever format is convenient for them.

Once parsed, show the user:
- Column headers found
- Number of rows (= number of designs that will be created)
- A preview of the first few rows

### Step 2: Select the Brand Template

If the user hasn't specified a template, search for autofill-capable ones:

```
Canva:search-brand-templates  dataset=non_empty
```

Show the results and ask the user to pick one. If they already named or described a template, search with that query.

### Step 3: Inspect the Template Schema

```
Canva:get-brand-template-dataset  template_id=<selected_id>
```

This returns the field names and types (text, image, chart) that the template expects.

### Step 4: Map CSV Columns to Template Fields

Present a mapping table to the user:

| Template Field | Type | Matched CSV Column | Notes |
|---|---|---|---|
| `product_name` | text | `Product Name` | auto-matched |
| `price` | text | `Price` | auto-matched |
| `hero_image` | image | *(none)* | no match — image fields need asset IDs |

**Matching rules:**
- Do case-insensitive, fuzzy matching between CSV headers and template field names
- Text fields can be filled directly from CSV string values
- Image fields require a Canva asset ID — see **Image Field Handling** below
- Chart fields require structured data — treat as advanced and ask the user for clarification

Confirm the mapping with the user before proceeding, especially if there are unmapped fields or ambiguous matches.

#### Image Field Handling

There are two ways a CSV can supply images for image-type template fields:

**Pattern A — CSV has a Canva asset ID column** (e.g. `image_asset_id`):
Use the asset ID value directly in the `autofill-design` call:
```json
{ "image": { "type": "image", "asset_id": "<value from CSV column>" } }
```

**Pattern B — CSV has an image URL column** (e.g. `image_url`):
URLs cannot be passed directly to `autofill-design`. Upload each URL to Canva first using `Canva:upload-asset-from-url`, capture the returned asset ID, then use it in the autofill call. Do the upload immediately before creating that row's design so failures stay localised.

**Pattern C — No image column in CSV:**
Ask the user whether to skip the image field (template default image stays) or abort. Skipping is safe — just omit the image key from the `data` payload entirely.

### Step 5: Bulk Create — One Design per Row

Loop through every CSV row and call `Canva:autofill-design` for each one. Call them **sequentially**, not all at once — the API may have rate limits and sequential calls are easier to debug.

For each row:

1. If the row has an image URL column (Pattern B), first call `Canva:upload-asset-from-url` to get a Canva asset ID.
2. Build the `data` payload from the confirmed field mapping:

```json
{
  "text_field_name": { "type": "text", "text": "<value from CSV>" },
  "image_field_name": { "type": "image", "asset_id": "<asset ID>" }
}
```

3. Call `Canva:autofill-design` with the template ID, data payload, and a descriptive title using the row number or a meaningful column value (e.g. `"Bulk Design - Row 3 - <identifier>"`).

Track results as you go:

```
Row 1 / 50: Created — <design_url>
Row 2 / 50: Created — <design_url>
Row 3 / 50: Failed — <error>
```

### Step 6: Report Results

After all rows are processed, summarise:

- Total rows attempted
- Successes (with links)
- Failures (with row number and reason)

Offer to save a summary CSV with columns: `row`, `status`, `design_url`, `error`.

## Notes

- Autofill requires a Canva Enterprise plan.
- For large CSVs (50+ rows), warn the user upfront that this will make N API calls and may take a while. Offer to do a test run on the first 3 rows before proceeding with the full batch.
- If some rows fail, continue with the rest — don't abort the whole batch.
- Skip rows where all mapped fields are empty and warn the user about them.
- If no CSV column matches a required template field, ask the user to confirm which column to use or whether to skip that field.
- Template field names are case-sensitive in the API — use the exact keys from `get-brand-template-dataset`.
- There is no "undo bulk create" — warn the user before starting large runs.
- Designs created this way are full Canva designs the user can further edit in their account.
