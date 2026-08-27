---
name: adobe-create-social-variations
description: >
  Resize, crop, or export any image or video into platform-ready social media assets using Adobe Creative Cloud tools. Use this skill when a user wants to prepare a photo, image, or video for one or more social platforms — Instagram, TikTok, LinkedIn, Facebook, YouTube, Snapchat, Pinterest, Threads, or X/Twitter. Triggers on: "prepare my image for Instagram", "resize for TikTok", "get this ready to post", "make versions for all platforms", "social media sizes", "crop for stories", "export for LinkedIn", "resize my video for social", "make social media assets", or any request to adapt a photo or video for specific platforms. Handles subject-aware cropping, AI canvas expansion, test previews before full runs, and same-ratio video resizing.
license: Apache-2.0
compatibility: "Runs on both widget-capable surfaces (e.g. Claude Cowork, which supports the asset_add_file picker and asset_preview_file preview widgets) and non-UI agents (e.g. Codex, where those widgets are unavailable). The default flow uses the widgets; each widget step has a text-only fallback. Raw local paths are never passed to image or video tools."
allowed-tools: adobe_mandatory_init asset_initialize_file_upload asset_finalize_file_upload asset_add_file asset_inline_preview asset_preview_file image_crop_and_resize image_generative_expand video_resize resizeVideoPoll
metadata:
  version: 2.1.0
  visibility: public
  surface: [claude, codex]
---

# Adobe Create Social Variations

Produces platform-ready images and videos from a single source file. Uses AI canvas expansion and subject-aware cropping to keep the subject in focus across all aspect ratios. Shows a lightweight 3-crop preview before a full-set run so framing issues are caught early — those crops are then reused in the final output.

> **Surface note:** The default flow below uses Adobe's MCP App widgets — the `asset_add_file` file picker and the `asset_preview_file` preview. Follow it as written. Only if a widget tool is **not available on this surface** (e.g. Codex) use the *No-widget fallback* attached to that step. Likewise, present `AskUserQuestion` prompts as plain-text labeled options wherever no question widget exists.

---

## Supported Input Types

| Input                         | Supported       | Notes                                                                               |
| ----------------------------- | --------------- | ----------------------------------------------------------------------------------- |
| JPG / PNG                     | ✅ Full workflow |                                                                                     |
| Firefly-generated image       | ✅ Full workflow | For `.ffgenimg` assets, pass the `presignedRenditionUrl` field, not `presignedAssetUrl` |
| Express file                  | ⚠️ Partial       | Must be exported to JPG/PNG first — tell user before proceeding                     |
| PSD / AI (Illustrator)        | ⚠️ Partial       | Flatten first (see Error Handling if this fails)                                    |
| Video (MP4/MOV)               | ⚠️ Partial       | Resize only — no smart reframe. See VIDEO WORKFLOW                                  |
| Unsupported (DOCX, PDF, etc.) | ❌               | Inform user; list accepted formats                                                  |

---

## Step 0 - prereq: Initialize Adobe Tools
Call `adobe_mandatory_init` first. This returns file handling rules and tool routing guidance required for the rest of the workflow.

```json
{ "skill_name": "adobe-create-social-variations", "skill_version": "2.1.0" }
```

---

## Step 1 — Entitlement Check

Now that `adobe_mandatory_init` confirmed that the "Adobe for creativity" connector is live, check which tools are available through the connector and set capability flags.

### Image Workflow — Core Tools (required)

All of these must be present for the skill to run at all. If **any** are missing from the connector, output this message exactly and stop — make no further tool calls:

> "To access this skill, please disconnect and reconnect to the "Adobe for creativity" Connector to sign in using an Adobe account, or sign up."

| Tool | Purpose |
|------|---------|
| `asset_initialize_file_upload` | First call in two-step upload — stages a local file to CC |
| `asset_finalize_file_upload` | Second call in two-step upload |
| `asset_inline_preview` | Determines focus strategy before cropping |
| `image_crop_and_resize` | Per-platform, per-format cropping |

### Widget Tools (used when available; graceful fallback)

| Tool | Flag | If missing |
|------|------|------------|
| `asset_add_file` | `pickerWidget = true/false` | File picker — the default ingest on widget surfaces (e.g. Claude). If unavailable (e.g. Codex), stage local files programmatically via `asset_initialize_file_upload` → `asset_finalize_file_upload` (see the *No-widget fallback* in each Get-the-Source-File step). |
| `asset_preview_file` | `previewWidget = true/false` | Side-by-side/grid preview. If unavailable (e.g. Codex), present output URLs directly in the message instead — UI clients still render them inline; non-UI agents download each via curl. |

### Image Workflow — Enhanced Tools (optional, graceful fallback)

| Tool | Flag | If missing |
|------|------|------------|
| `image_generative_expand` | `expandAvailable = true/false` | Use `image_crop_and_resize` with `fit: "reframe"` from `sourceURI` instead. Do NOT mention "AI canvas expansion" to the user. Note in delivery summary: "Smart reframe was used for aspect ratio adaptation." |

### Video Workflow — Required Tools (optional workflow, all-or-nothing)

Only offer the video workflow if **both** tools below are available. If either is missing, set `videoCapable = false` — do NOT mention video resizing capabilities to the user at any point.

| Tool | Purpose |
|------|---------|
| `video_resize` | Same-ratio resize only |
| `resizeVideoPoll` | Deferred tool — load before calling |

If `videoCapable = false` and the user explicitly asks about video resizing, avoid verbosity and output this message exactly:

> "Video resizing isn't available with your current setup. Please disconnect and reconnect to the "Adobe for creativity" Connector to sign in using an Adobe account, or sign up. In the meantime, I can help with image crops and social media variants though."

---

## Tool Reference

| Step | Tool | Notes |
|------|------|-------|
| Get file (widget surfaces) | `asset_add_file` | File picker / CC browse |
| Stage file (no-widget fallback) | `asset_initialize_file_upload` + `asset_finalize_file_upload` | Two-step upload — stage a local file to CC when the picker is unavailable |
| Inspect source image | `asset_inline_preview` | Determines focus strategy before cropping |
| Expand canvas | `image_generative_expand` | Creates tall (9:16/4:5) and wide (~2:1/16:9) variants |
| Crop to platform dimensions | `image_crop_and_resize` | Per-platform, per-format; also 403 fallback for expand |
| Preview test crops or full set | `asset_preview_file` | Before full run (test) and at delivery *(no-widget fallback: present the URLs directly)* |
| Resize video | `video_resize` | Same-ratio resize only |
| Poll video resize job | `resizeVideoPoll` | Deferred tool — load before calling |

---

## IMAGE WORKFLOW

### Step 0 — Get the Source File

How you get the file depends on where it is:

| Source                                             | Action                                                                                                                                                                                                                                                                                    |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| File uploaded in chat (`/mnt/user-data/uploads/…`) | Check egress status from `adobe_mandatory_init` (Step 0). If egress is enabled, upload programmatically: get file size and MIME type via bash, call `asset_initialize_file_upload`, PUT the chunk(s), then `asset_finalize_file_upload`. If egress is disabled, use `asset_add_file()` (the picker) instead. |
| No file provided yet                               | Call `asset_add_file()` immediately — no need to ask first.                                                                                                                                                                                                                               |
| File already in Creative Cloud                     | Call `asset_add_file()` so the user can select it from their CC storage.                                                                                                                                                                                                                  |

> **No-widget fallback** *(only if `asset_add_file` is unavailable on this surface, e.g. Codex)* — don't ask the user to pick. Stage any local file programmatically (`asset_initialize_file_upload` → PUT → `asset_finalize_file_upload`) and use the returned presigned CC URL; for a file already in Creative Cloud, reference it directly by its CC URI. Staging requires egress — check egress status from `adobe_mandatory_init` first; if egress is disabled and no picker is available on this surface, tell the user staging isn't possible here and ask them to run the workflow on a surface with the `asset_add_file` picker.

After the file is available, detect image vs. video from `mediaType`. For images, proceed to Step 1.

---

### Step 1 — Ask: Which Platforms?

Ask in a single question using `AskUserQuestion` with multi-select:

> Full set / Instagram / TikTok / LinkedIn / Facebook / YouTube / Snapchat / X/Twitter / Pinterest / Threads

**Set the test flag based on the user's answer:**

- **If "Full set" is selected** → `runTestPreview = true`. Use all platforms. A 3-crop test preview will be shown before the full set is generated (see Step 4).
- **If any specific platform(s) are selected** → `runTestPreview = false`. Use only the selected platforms. Skip the test preview and go directly from Step 3 to Step 5.

> The test preview is a useful safety net for large cross-platform batches, but unnecessary friction for a targeted 1–2 platform run.

---

### Step 2 — Inspect Image & Set Focus Strategy

**Inspect the image first** using `asset_inline_preview` on the source file. Visual inspection produces far better focus decisions than guessing from the filename — and usually means you won't need to ask the user anything at all.

After inspecting, tell the user what you see and what focus strategy you're using, and invite a correction:

> "I can see this is a [e.g. 'product shot of a tote bag on a neutral background']. I'll use [focus strategy] to keep [subject] centred across all crops. Does that sound right, or would you like me to focus on something else?"

Only ask a follow-up question if the image is genuinely ambiguous (multiple equally prominent subjects, or a scene with no clear focal point).

| Image type                             | Focus strategy                         | Rationale                                                                           |
| -------------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------- |
| Portrait / headshot / person in scene  | `"face"`                               | Most reliable for people — facial detection anchors to the face even in tight crops |
| Upper body / chest-up portrait         | `"upper_body"`                         | Use when face + torso context matters (outfit, gesture, expression)                 |
| Product on clean background            | `{ prompt: "description of product" }` | Name the product explicitly for clean isolation (e.g. `{ prompt: "tote bag" }`)     |
| Non-human subject with busy background | `{ prompt: "description of subject" }` | More precise than generic `"subject"`                                               |
| Aerial / flat lay / no clear subject   | `{ x: 0.5, y: 0.5 }`                   | Centre crop is safest when nothing to detect                                        |
| User specifies a subject               | `{ prompt: "user's description" }`     | Pass their words directly                                                           |

> For images containing people, use `"face"` — prompt-based focus drifts to bodies rather than faces. Reserve `{ prompt: "..." }` for non-human subjects.

> ⚠️ If the source image is significantly wider than it is tall (landscape), use 2000px top & bottom for the tall expand (not the default 960px) — this gives the portrait crop enough canvas to reframe around the subject.
> ⚠️ For the same landscape sources, also use 1500px left & right for the wide expand (not the default 960px) — 960px doesn't give the reframe enough room to pull the subject into centre for the ~2:1 landscape crop.

If the user corrects your assessment, update the focus strategy and confirm before proceeding.

---

### Step 3 — Generative Expand (directly from source — no padding)

Expand the original image directly. Do not pad to square first — the AI produces better results extending real scene content than bridging across blank bars.

Run both expands before any crops:

```
// GROUP A — tall canvas (for 9:16 and 4:5 targets)
image_generative_expand(sourceURI, { top: 960, bottom: 960 }) → tallURI
// use 2000 top & bottom if source is significantly landscape

// GROUP B — wide canvas (for ~2:1 and 16:9 targets)
image_generative_expand(sourceURI, { left: 960, right: 960 }) → wideURI
// use 1500 left & right if source is significantly landscape
```

Square targets (1:1) crop directly from the source — no expand needed.

> Expands originate from the original `sourceURI` — chained expands degrade output.
> ⚠️ If `image_generative_expand` returns 403 (entitlement), fall back to `image_crop_and_resize` with `fit: "reframe"` from `sourceURI` for all variants in that group. Note the fallback in the delivery summary.

---

### Step 4 — Test Preview *(Full set only — skip if `runTestPreview = false`)*

**If `runTestPreview = false`** (specific platforms selected): skip this step and go directly to Step 5.

**If `runTestPreview = true`** (Full set): produce 3 representative test crops — one per aspect ratio family — before generating the full set.

| Test               | Source    | Dimensions | Ratio | Covers                                                    |
| ------------------ | --------- | ---------- | ----- | --------------------------------------------------------- |
| Test 1 — Square    | sourceURI | 1080×1080  | 1:1   | Instagram square, LinkedIn square, Facebook square        |
| Test 2 — Portrait  | tallURI   | 1080×1350  | 4:5   | Instagram portrait, Threads — bellwether for 9:16 quality |
| Test 3 — Landscape | wideURI   | 1200×627   | ~2:1  | LinkedIn landscape, Facebook landscape, X/Twitter         |

Show all 3 via `asset_preview_file` and ask:

> "Here are 3 test crops covering the main aspect ratios. Do the framing and expansion look good? I'll generate the full set once you approve."

> **No-widget fallback** *(only if `asset_preview_file` is unavailable, e.g. Codex)* — present all 3 URLs directly in the message and ask the same question; UI clients render them inline, and in Codex or other non-UI agents, download each to the workspace and reference the local paths.

These crops are reused in the final output — only the 9:16 story/reel crop needs to be generated after approval.

---

### Step 5 — Generate All Platform Variants

**If `runTestPreview = true`:** proceed only after user approves test crops in Step 4.
**If `runTestPreview = false`:** proceed immediately after Step 3.

Generate every variant in the Platform Specs table for each selected platform. Reuse test crop URIs only when dimensions are an exact match — for any different dimensions, run a fresh `image_crop_and_resize`.

**Per-platform variants to generate:**

| Platform  | Variants                                                  |
| --------- | --------------------------------------------------------- |
| Instagram | 1080×1080 (reuse test), 1080×1350 (reuse test), 1080×1920 |
| TikTok    | 1080×1920 only — no 4:5 variant for TikTok                |
| LinkedIn  | 1200×627 (reuse test), 1080×1080 (reuse test)             |
| Facebook  | 1200×630, 1080×1080, 1080×1920                            |
| X/Twitter | 1200×675, 1080×1080                                       |
| YouTube   | 1280×720                                                  |
| Snapchat  | 1080×1920                                                 |
| Pinterest | 1000×1500                                                 |
| Threads   | 1080×1350                                                 |

---

### Step 6 — Preview Full Set

Call `asset_preview_file` with all successfully generated URLs — including partial sets when some variants failed.

> **No-widget fallback** *(only if `asset_preview_file` is unavailable, e.g. Codex)* — list all successfully generated URLs directly in the message (including partial sets when some variants failed). UI clients render them inline; in Codex or other non-UI agents, download each to the workspace and reference the local paths.

---

### Step 7 — Delivery Summary

Present a clean summary table. Note any fallbacks or skipped steps clearly.

```
✅ Social media set complete!

| Platform  | Format         | Dimensions | Status        |
| --------- | -------------- | ---------- | ------------- |
| Instagram | Feed Square    | 1080×1080  | ✅ (from test) |
| Instagram | Feed Portrait  | 1080×1350  | ✅ (from test) |
| Instagram | Story / Reel   | 1080×1920  | ✅             |
| TikTok    | Video / Post   | 1080×1920  | ✅             |
| LinkedIn  | Post Landscape | 1200×627   | ✅ (from test) |
| LinkedIn  | Post Square    | 1080×1080  | ✅ (from test) |
```

If generative expand fell back to reframe:
> ⚠️ AI canvas expansion is not included in your current Adobe plan — smart reframe was used instead.

---

## Platform Specs (Image)

| #   | Platform  | Format         | Dimensions | Ratio | Quality | Source Canvas |
| --- | --------- | -------------- | ---------- | ----- | ------- | ------------- |
| 1   | Instagram | Feed Square    | 1080×1080  | 1:1   | 7       | sourceURI     |
| 2   | Instagram | Feed Portrait  | 1080×1350  | 4:5   | 7       | tallURI       |
| 3   | Instagram | Story / Reel   | 1080×1920  | 9:16  | 7       | tallURI       |
| 4   | TikTok    | Video / Post   | 1080×1920  | 9:16  | 7       | tallURI       |
| 5   | LinkedIn  | Post Landscape | 1200×627   | ~2:1  | 6       | wideURI       |
| 6   | LinkedIn  | Post Square    | 1080×1080  | 1:1   | 6       | sourceURI     |
| 7   | Facebook  | Feed Landscape | 1200×630   | ~2:1  | 7       | wideURI       |
| 8   | Facebook  | Feed Square    | 1080×1080  | 1:1   | 7       | sourceURI     |
| 9   | Facebook  | Story          | 1080×1920  | 9:16  | 7       | tallURI       |
| 10  | X/Twitter | In-stream      | 1200×675   | 16:9  | 6       | wideURI       |
| 11  | X/Twitter | Square post    | 1080×1080  | 1:1   | 6       | sourceURI     |
| 12  | YouTube   | Thumbnail      | 1280×720   | 16:9  | 5       | wideURI       |
| 13  | Snapchat  | Snap/Story     | 1080×1920  | 9:16  | 2       | tallURI       |
| 14  | Pinterest | Standard Pin   | 1000×1500  | 2:3   | 7       | tallURI       |
| 15  | Threads   | Feed Portrait  | 1080×1350  | 4:5   | 7       | tallURI       |

> ⚠️ Snapchat's 250 KB limit requires `quality: 2` — warn the user upfront when Snapchat is selected.

**File naming convention:** `[basename]_[platform]_[descriptor]_[ratio].jpg`
Example: `hero_instagram_story_9x16.jpg`

---

## VIDEO WORKFLOW

### Step 0 — Get the Source File

Video tools require an `assetId` — not a URL. How you get it depends on where the file is:

| Source                                             | Action                                                                                                                                                                                                                                                                                                                                     |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| File uploaded in chat (`/mnt/user-data/uploads/…`) | Check egress status from `adobe_mandatory_init` (Step 0). If egress is enabled, upload programmatically: get file size and MIME type via bash, call `asset_initialize_file_upload`, PUT the chunk(s), then `asset_finalize_file_upload`. The returned `assetId` is what video tools need. If egress is disabled, use `asset_add_file()` (the picker) instead. |
| No file provided yet                               | Call `asset_add_file()` immediately.                                                                                                                                                                                                                                                                                                       |
| File already in Creative Cloud                     | Call `asset_add_file()` so the user can select it.                                                                                                                                                                                                                                                                                         |

> If egress is disabled and the user has already dropped a video into chat, explain why it can't be used directly: "To resize your video I'll need you to select it via the file picker — this gives Adobe the asset ID it needs. I'll open it now."

> **No-widget fallback** *(only if `asset_add_file` is unavailable, e.g. Codex)* — stage the local video programmatically (`asset_initialize_file_upload` → PUT → `asset_finalize_file_upload`) and use the returned `assetId`; for a video already in Creative Cloud, reference it by its `assetId`. Staging requires egress — check egress status from `adobe_mandatory_init` first; if egress is disabled and no picker is available on this surface, tell the user staging isn't possible here and ask them to run the workflow on a surface with the `asset_add_file` picker.

---

### Step 1 — Determine Video Type

If the user has already described or implied the video orientation (e.g. "I shot this on my phone in portrait" → clearly 9:16), skip this question and proceed. Otherwise ask:

> "To suggest the best output sizes, it helps to know what kind of video this is. What type is it?"

Use `AskUserQuestion` with single-select:

| Option                 | Aspect Ratio | Common use                             |
| ---------------------- | ------------ | -------------------------------------- |
| Phone video — portrait | 9:16         | Shot on phone, vertical                |
| Phone video — square   | 1:1          | Shot in square mode                    |
| Screen recording       | 16:9         | Desktop or laptop capture              |
| Camera / DSLR          | 16:9         | Professional or mirrorless camera      |
| Other / not sure       | —            | Default to 1:1 (safest cross-platform) |

---

### Step 2 — Suggest Safe Output Sizes

Only suggest same-ratio resizes. Cross-ratio resizes (e.g. 16:9 → 9:16) produce black bars and are algorithmically penalised on TikTok and Instagram Reels. If a user asks for a cross-ratio resize, explain the limitation and offer same-ratio alternatives instead.

| Source ratio     | Safe output sizes            |
| ---------------- | ---------------------------- |
| 9:16 (portrait)  | 1080×1920, 720×1280, 540×960 |
| 1:1 (square)     | 1080×1080, 720×720           |
| 16:9 (landscape) | 1920×1080, 1280×720, 854×480 |

Present these as options with `AskUserQuestion` (multi-select).

---

### Step 3 — Resize

> ⚠️ `resizeVideoPoll` is a **deferred tool** — load it first before attempting to poll.
> Direct calls without loading will fail with "not loaded" error.

For each selected size, call `video_resize` with the asset ID:

```javascript
video_resize({ assetId: sourceAssetId, width: W, height: H }) → { statusId }
```

Poll with `resizeVideoPoll` until complete. Poll 3–4 times with brief pauses before reporting slow progress to the user.

---

### Step 4 — Preview

Call `asset_preview_file` with all completed outputs.

> **No-widget fallback** *(only if `asset_preview_file` is unavailable, e.g. Codex)* — list all completed output URLs directly in the message. UI clients render them inline; in Codex or other non-UI agents, download each to the workspace and reference the local paths.

---

### Step 5 — Delivery Summary

```
✅ Video resize complete!

| Size      | Ratio | Status |
| --------- | ----- | ------ |
| 1080×1920 | 9:16  | ✅      |
| 720×1280  | 9:16  | ✅      |
```

Note: Video resizing does not apply intelligent reframing — cross-ratio reformatting is out of scope for this skill.

---

## Error Handling

| Situation                                           | Action                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Egress upload fails (chunk PUT 5xx after retry)     | Stop upload. Fall back to `asset_add_file()` and tell the user: "Direct upload didn't work — I'll open the picker so you can select the file." *(No-widget surface: report the failure and ask the user to re-provide the file.)*                                                         |
| `image_generative_expand` returns 403 (entitlement) | Fall back to `image_crop_and_resize` with `fit: "reframe"` from `sourceURI`. Note in delivery summary: "AI canvas expansion is not included in your current Adobe plan — smart reframe was used instead." Retrying does not resolve a 403 entitlement — continue per the fallback rule. |
| `image_crop_and_resize` returns 403 (entitlement)   | Stop workflow. Tell the user: "Image cropping isn't available on your current Adobe plan — I can't complete this request here."                                                                                                                                                         |
| PSD/AI flattening returns 403                       | Stop workflow. Tell the user: "Flattening this file type isn't available on your current Adobe plan — export as JPG or PNG first, then try again."                                                                                                                                      |
| `.ffgenimg` file type fails expand                  | Retry using `presignedRenditionUrl` instead of `presignedAssetUrl`                                                                                                                                                                                                                      |
| 401 not authenticated                               | Ask user to re-authenticate via Adobe OAuth                                                                                                                                                                                                                                             |
| Image too large after crop                          | Re-run with lower quality setting                                                                                                                                                                                                                                                       |
| Express file uploaded                               | Ask user to export as JPG/PNG first                                                                                                                                                                                                                                                     |
| PSD / AI file uploaded                              | Flatten first (JPEG, 300 DPI). On 403, see entitlement row above.                                                                                                                                                                                                                       |
| `video_resize` fails                                | Report clearly; suggest user re-upload as MP4                                                                                                                                                                                                                                           |
| Unsupported file format (DOCX, PDF, etc.)           | Inform user. Accepted inputs: JPG, PNG, Firefly images, PSD/AI, MP4/MOV.                                                                                                                                                                                                                |

---

## Hard Constraints

- Never pass a raw local filesystem path to any `image_*` or video tool. Local files must reach Creative Cloud first — selected via the `asset_add_file` picker, or (no-widget fallback) staged via `asset_initialize_file_upload` → PUT → `asset_finalize_file_upload`; only the resulting presigned CC URI (for images) or `assetId` (for video tools) is valid.
