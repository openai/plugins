# Asset Handling — The Classification Engine

When the user provides files, URLs, or references, route each asset to the right path. The user should NEVER have to think about this.

## Two Paths

| Path | What happens | When to use |
|------|-------------|-------------|
| **A: Contextualize → Prompt** | Read/analyze the asset, extract key info, bake into script. Video Agent never sees the original. | Reference material, auth-walled content, documents where the *information* matters more than the *visual*. |
| **B: Attach to API** | Upload the raw file via `files[]`. Video Agent analyzes, extracts graphics, uses as frames/B-roll. | Screenshots, branded assets, PDFs with important visual layouts, images the viewer should literally see. |
| **A+B: Both** | Contextualize for script quality AND attach for visual use. | Long docs where you need to summarize but Video Agent should also have the full source. |

## Classification Flow

```
1. Can Video Agent access this directly?
   - Public URL (no auth, no paywall) → YES
   - Private/internal URL → NO
   - Local file → NO (must upload first)

2. Should the viewer SEE this asset?
   - Screenshot, logo, product image, chart → YES → Path B
   - Research doc, article, context material → NO → Path A
   - Ambiguous → Path A+B

3. Is the content too long for the prompt?
   - Short (< 500 words) → fits in prompt
   - Long (> 500 words) → summarize key points, attach full doc
```

## Decision Matrix

| Asset Type | Publicly Accessible? | Show On Screen? | Route |
|-----------|---------------------|----------------|-------|
| Screenshot / image | N/A | Yes | **B: Attach** + describe in prompt as B-roll |
| Logo / brand asset | N/A | Yes | **B: Attach** + anchor to intro/outro |
| Public URL to file (PDF, image, video) | Yes | Maybe | **B: Download → upload via `/v3/assets` → pass `asset_id`** + summarize |
| Public URL to web page (HTML) | Yes | No | **A: Fetch and contextualize only.** Do NOT pass HTML URLs in `files[]`. |
| Auth-walled URL (requires login) | No | No | **A: Ask the user to paste the content.** Never fabricate. |
| PDF (short, text-heavy) | N/A | No | **A+B: Extract key points** + attach |
| PDF (long, visual-rich) | N/A | Maybe | **B: Attach** + summarize top points |
| Raw data / spreadsheet | N/A | Partially | **A: Analyze and describe** key stats. Attach if charts should appear. |

## Executing Routes

### Path A (Contextualize)
- URLs: retrieve publicly accessible content with the environment's standard web/content fetch capability
- For auth-walled content you cannot access: ask the user to paste the text directly
- Extract 3-5 most important points relevant to the video
- Weave naturally into the script. Don't dump. Integrate.

### Path B (Attach)
Upload to HeyGen:

**App:** upload through the HeyGen app's asset flow when available.
**CLI:** `heygen asset create --file /path/to/file.png`

Max 32MB per file. Returns JSON with the new `asset_id`.

Or pass inline in `files[]`:
```json
{"type": "url", "url": "https://example.com/image.png"}
{"type": "asset_id", "asset_id": "<from upload>"}
{"type": "base64", "data": "<base64>", "content_type": "image/png"}
```

### Describe Asset Usage in Prompt
Be SPECIFIC:
- "Use the uploaded dashboard screenshot as B-roll when discussing analytics"
- "Display the company logo in the intro and end card"

### Log Classification
In the learning log entry, record:
```json
"assets_classified": [{"type": "image", "route": "attach", "accessible": true, "reason": "product screenshot"}]
```

## Rules

- **Never ask the user which path unless genuinely 50/50.** You're the producer. Make the call.
- **When in doubt, do both (A+B).** Over-providing costs nothing.
- **Always describe attached assets in the prompt.** Uploading without description = ignored.
- **Auth-walled content is YOUR job.** Bridge the gap between your access and Video Agent's.
- **URLs that fail:** Try the environment's standard web/content fetch capability. If login/paywall/404 → tell the user, ask for content directly. Never silently fabricate.
- **HTML URLs cannot go in `files[]`.** Video Agent rejects `text/html`. Web pages are ALWAYS Path A only.
- **Prefer download→upload→asset_id** over `files[]{url}`. HeyGen's servers often blocked by CDN/WAF.
