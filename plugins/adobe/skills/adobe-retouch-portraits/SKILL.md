---
name: adobe-retouch-portraits
description: >
  Bulk-retouch a folder of portrait photos using Adobe tools —
  designed for wedding photographers and event photographers who need fast,
  walk-away batch processing. Use this skill when the user says "retouch my
  photos", "batch process these portraits", "process my wedding photos",
  "clean up this folder of images", "run my headshots through Adobe", or
  uploads/selects a folder of photos and wants them polished and ready to
  review. Automatically applies auto-straighten, auto-tone, and auto-light
  to every image. Outputs a preview grid and download folder.
  Access: 🔐 Signed-In required | Gen AI: ❌ by default — optional background-only cleanup only where the surface permits generative AI (e.g. Codex); none on Claude
license: Apache-2.0
compatibility: "Runs on both widget-capable surfaces (e.g. Claude Cowork, which supports the asset_add_file picker and asset_preview_file preview widgets) and non-UI agents (e.g. Codex, where those widgets are unavailable). The default flow uses the widgets; each widget step has a text-only fallback. Local files are staged to Creative Cloud first; raw local paths are never passed to image tools."
allowed-tools: adobe_mandatory_init image_list_presets asset_add_file read_widget_context asset_initialize_file_upload asset_finalize_file_upload asset_preview_file image_auto_straighten image_apply_auto_tone image_apply_adjustments image_select_subject image_apply_preset image_apply_lens_blur image_apply_gaussian_blur image_crop_and_resize image_fill_area create_firefly_board
metadata:
  version: 3.1.0
  visibility: public
  surface: [claude, codex]
---

# Adobe Retouch Portraits

A walk-away bulk retouching pipeline for photographers. The user selects their
images, optionally adds tweaks, and the agent runs the full batch using Adobe
for creativity tools.

> **Surface note:** The default flow uses Adobe's MCP App widgets — the `asset_add_file` picker (Step 1) and the `asset_preview_file` preview (Steps 2c and 8). Follow it as written. Only if a widget tool is **not available on this surface** (e.g. Codex) use the *No-widget fallback* attached to that step. Present `AskUserQuestion` prompts as plain-text labeled options wherever no question widget exists.

---

## Generative AI Policy

**This retouching pipeline is fully non-generative by default.** The core workflow — auto-straighten, auto-tone, adjustments, presets, blur, and crop — uses no generative AI, and that non-generative pipeline is the *only* behavior on surfaces that do not permit generative AI (**including Claude**).

**Generative editing runs only where the surface permits it.** A surface permits generative AI only when it exposes a generative tool such as `image_fill_area` (e.g. Codex). Where no such tool is available (e.g. Claude), perform **no** generative edits of any kind — do not call, attempt, offer, or mention them; run the non-generative pipeline only.

**Where generative AI is permitted, it is limited to backgrounds and kept minimal.** Only then may `image_fill_area` correct dust spots, sensor artifacts, or scratches on non-human areas (walls, floors, sky, props), and only when the fix is invisible at normal viewing size — remove a dust spot, not repaint a wall. **Never** apply generative tools to faces, skin, hair, bodies, or clothing on any surface. Do not alter the scene, remove objects, change the environment, or extend the frame.

If the user asks you to generatively modify a person (e.g. "change her hair color", "make him look younger"), clarify that this skill does not perform generative edits on people — and, on a surface with no generative capability at all, that generative editing isn't available here — then suggest a dedicated generative workflow instead.

---

## Tool Reference (Adobe for creativity connector)

| Step                  | Tool                                                        | Notes                                              |
| --------------------- | ----------------------------------------------------------- | -------------------------------------------------- |
| Ingest                | `asset_add_file` + `read_widget_context`                    | Interactive file picker; resolve URIs via `read_widget_context` |
| Ingest *(no-widget fallback)* | `asset_initialize_file_upload` + `asset_finalize_file_upload` | Only when `asset_add_file` is unavailable — stage a local file to CC |
| Discover presets      | `image_list_presets`                                        | Once at startup; builds the smart preset plan      |
| Straighten            | `image_auto_straighten`                                     | Per image                                          |
| Auto-Tone             | `image_apply_auto_tone` (cameraRawFilter)                   | Per image                                          |
| Tone adjustments      | `image_apply_adjustments`                                   | Batch — all tweaks in one call                     |
| Subject/body detect   | `image_select_subject`                                      | Face + body parts + clothes detection              |
| Adaptive Enhancements | `image_apply_preset`                                        | Per image, opt-in (see Step 5)                     |
| Background blur       | `image_apply_lens_blur`                                     | Per image, preferred — depth-aware bokeh           |
| Heavy/stylized blur   | `image_apply_gaussian_blur`                                 | Per image, only if user explicitly requests heavy  |
| Background cleanup    | `image_fill_area` (optional; generative)                    | Only where the surface permits generative AI (tool available, e.g. Codex) — backgrounds only, never people; **not used on Claude** |
| Crop                  | `image_crop_and_resize`                                     | Per image                                          |
| Sample preview        | `asset_preview_file`                                        | Before/after on image[0] only *(no-widget fallback: present the URLs directly)* |
| Final preview         | `asset_preview_file`                                        | All final URLs directly, no resize step *(no-widget fallback: present the URLs directly)* |
| Firefly Board         | `create_firefly_board`                                      | Source presigned URLs from ingestion               |

---

## Step 0 - prereq: Initialize Adobe Tools
Call `adobe_mandatory_init` first. This returns file handling rules and tool routing guidance required for the rest of the workflow.

```json
{ "skill_name": "adobe-retouch-portraits", "skill_version": "3.1.0" }
```

This also tells you which widgets this surface supports and whether egress is enabled. If `asset_add_file` and `asset_preview_file` are available, follow the default flow (Steps 1, 2c, and 8 as written). If one is not available (e.g. Codex), use that step's *No-widget fallback*. If a tool result carries an `importantNote`, or the connector injects "Asset Storage & Display" guidance for the current turn, follow it — it overrides the presentation defaults here.

---

## Step 0b: Discover Available Presets

Call `image_list_presets` immediately after init — before ingestion or user questions. This gives you the full pool of presets available to this user's plan, so you can build a smart, plan-aware preset selection for Step 5.

```
Tool: image_list_presets
Params: {}
```

From the returned list, build a **Preset Plan** by categorizing presets into four buckets. Use the naming signals below to classify each preset — these are heuristics, not hardcoded names, so apply judgment:

### Preset Plan Buckets

**1. Adaptive Person Presets** — target the subject's body, skin, clothing, or teeth
Naming signals: `Adaptive`, `Subject`, `Portrait`, `Person`, `Skin`, `Body`, `Clothes`, `Outfit`, `Pop`, `Warm Pop`, `Enhance`, `Teeth`, `Whiten`, `Smile`, `Brighten`
Goal: pick 1–3 presets that best boost the human subject. Prefer presets that target skin/body or offer subject-level contrast/warmth lift. Avoid presets that affect only sky or background. Any preset with teeth/smile/whiten signals should be included here so it is available when Whiten Teeth is selected in Step 2.

**2. Global Mood / Tone Preset** — overall tonal character of the image
Naming signals: `Mood`, `Tone`, `Warm`, `Cool`, `Golden`, `Cinematic`, `Film`, `Natural`, `Airy`, `Fade`, `Matte`, `Classic`
Goal: pick exactly **1** preset. Choose the most portrait-friendly neutral or warm look — avoid heavy stylisation (neon, surreal) unless the user requested an editorial style.

**3. Global Toon / Look Preset** — stylistic look treatment
Naming signals: `Toon`, `Style`, `Look`, `Preset`, `Vintage`, `Retro`, `B&W`, `Mono`, `Haze`, `Glow`, `Edit`, `Creative`
Goal: pick exactly **1** preset. Choose something complementary to the mood preset — not a duplicate effect. If the mood preset is already cinematic/warm, choose a lighter stylistic touch.

**4. Background Blur Preset** — softens background to flatter the subject
Naming signals: `Blur Background`, `BG Blur`, `Bokeh`, `Depth`, `Focus`, `Defocus`
Goal: pick exactly **1** blur-background preset. This replaces `image_apply_gaussian_blur` when the user opts into it.

**Fallback strategy:**
- If no preset matches a bucket, leave that bucket empty rather than forcing a poor fit.
- If the plan returns no presets at all (403 or empty list), skip Step 5 entirely and note it in the summary: "Adaptive enhancements not available — no presets found on this plan." **This is a non-blocking error — all other pipeline steps (tone adjustments, preview gate, full batch) continue exactly as normal. Only Step 5 is skipped.**
- Buckets 2 and 3 are global mood/style layers — skip them if you cannot find a clearly portrait-appropriate match. It's better to skip than to apply an ill-fitting preset.

Store the chosen presets as your **Preset Plan** before Step 2. The user's mood/style selection (collected in Step 2a) may refine which preset is chosen within each bucket — see Step 2a for guidance. Show the final plan to the user in the confirmation message (Step 2).

---

## Step 1: Image Ingestion

Call `asset_add_file` with no parameters. This renders an interactive UI where
the user can:
- **Browse CC storage** and select a folder or individual files
- **Upload from device** (local files)
- **In Cowork**: select a local folder path directly
```
Tool: asset_add_file
Params: {}
```

**Important:** `asset_add_file` returns `imageURIs: []` — this is expected and
NOT an error. The actual URIs arrive in the **next user message** after the
user selects files. Wait for that follow-up before continuing.

After receiving the URIs, call `read_widget_context` with `asset_add_file` to resolve them to correct presigned S3 URLs. Use those resolved URLs for all subsequent tool calls — `dcx-stage.adobe.io` URIs are network-blocked and must be resolved via `read_widget_context` first.

Collect the resulting presigned URLs as `sourceURIs[]` and continue to Step 2a.

> **No-widget fallback** *(only if `asset_add_file` is unavailable on this surface, e.g. Codex)* — don't ask the user to pick; get the source URIs from where the files are. `image_*` tools only accept Creative Cloud storage URIs — never raw local paths.
>
> | Source | Action |
> |--------|--------|
> | File(s) at a local path (e.g. `/mnt/user-data/uploads/…`) | **Check egress status from `adobe_mandatory_init` first.** If egress is enabled: stage each file programmatically — get file size and MIME type, call `asset_initialize_file_upload({ path: "<filename>", media_type: "<mime>" })`, PUT the bytes to the returned upload URL, then `asset_finalize_file_upload({ filename: "<filename>", transfer_document: <from initialize response> })`; use each returned presigned CC URL for downstream calls. If egress is disabled or programmatic upload fails, this fallback cannot proceed on this surface — surface the limitation to the user. |
> | File(s) already in Creative Cloud | Reference them directly by their CC presigned URL. |
>
> The programmatic path uses neither `asset_add_file` nor `read_widget_context`. Collect the resulting presigned CC URLs as `sourceURIs[]`.

---

## Step 2a: Mood & Style Selection

Before presenting the pipeline plan, ask the user what mood and style they want for their portraits. This drives which presets are prioritised within the Preset Plan buckets.

**If the user's message already states a clear mood/style** (e.g. "warm and glowing", "dark and moody", "clean headshots", "editorial"), infer it directly — skip this question and map it using the table below.

**If no mood/style is specified**, post this message and ask:
```
📸 Got [N] photo(s)! Before I build your retouching plan — what kind of look are you going for?
```

```
Question (single_select):
  question: "🎨 What mood or style do you want for these portraits?"
  options:
    - "Natural & Clean — true-to-life, polished, minimal"
    - "Warm & Glowing — golden, soft, flattering"
    - "Moody & Dramatic — dark, contrasty, editorial"
    - "Bright & Airy — light, fresh, lifestyle"
    - "Cinematic — film-inspired, desaturated, storytelling"
    - "Bold & Vibrant — punchy, vivid, social-ready"
```

**Hold** — do not proceed to Step 2 until the user replies. (This hold applies only when the question was asked. If mood/style was already inferred from the user's message, skip this hold and proceed directly to Step 2.)

### Mood → Preset Plan guidance

Use the selected mood to refine your Preset Plan (built in Step 0b). Within each bucket, prefer presets whose names align with the chosen mood:

| Mood | Favour in Mood/Tone bucket | Favour in Toon/Look bucket |
|------|---------------------------|---------------------------|
| Natural & Clean | `Natural`, `Clean`, `Classic`, `Neutral` | light/subtle look |
| Warm & Glowing | `Warm`, `Golden`, `Glow`, `Sunset`, `Amber` | warm complementary |
| Moody & Dramatic | `Moody`, `Dark`, `Cinematic`, `Shadow`, `Drama` | `Matte`, `Fade`, `Vintage` |
| Bright & Airy | `Airy`, `Bright`, `Light`, `Fresh` | soft, bright look |
| Cinematic | `Cinematic`, `Film`, `Fade`, `Classic` | `Matte`, `Grain`, `Retro` |
| Bold & Vibrant | `Vibrant`, `Pop`, `Bold`, `Vivid` | punchy look |

If the Preset Plan has multiple candidates in a bucket, pick the one that best matches the chosen mood. If only one preset exists in a bucket, use it regardless of mood.

---

## Step 2: Announce Pipeline + Offer Options

Once the mood/style is confirmed, check whether the user's message **already fully specifies** their enhancement, tweak, and crop preferences.

**If preferences are fully stated upfront** (e.g. "retouch with subject pop, no tweaks, crop 1:1"), skip `AskUserQuestion` entirely and go straight to the confirmation message, then proceed directly to Step 2c (sample preview). The preview gate is mandatory — it runs even when all preferences are stated upfront. Do NOT start the full batch without it. Map their stated preferences using the button→parameter table below.

**If preferences are not fully stated** (e.g. "please retouch them" with no further detail), post this message first:
```
📸 Got [N] photo(s)! The default pipeline will auto-straighten and auto-tone every image.

Let me know if you'd like any extras 👇
```

Then call `AskUserQuestion` with these three questions:

```
Question 1 (multi_select):
  question: "✨ Adaptive AI enhancements (select any — or none to skip)"
  options:
    - "All"
    - "Enhance Subject — adaptive preset boosts on the person, skin & clothes"
    - "Mood & Tone — apply a portrait-flattering global tone look"
    - "Toon & Style — apply a stylistic look treatment"
    - "Blur Background — soft bg blur preset, respects edges"
    - "Whiten Teeth — brightens teeth (smiles only)"
    - "None"

Question 2 (multi_select):
  question: "🎛️ Manual tweaks (select any — or none to skip)"
  options:
    - "Recover highlights"
    - "Lift shadows"
    - "More contrast"
    - "More vibrant"
    - "Desaturate (muted tones)"
    - "Blur background — depth-aware bokeh (standard)"
    - "Heavy background blur — stylized gaussian blur"
    - "None"

Question 3 (single_select):
  question: "✂️ Crop ratio"
  options:
    - "Auto (landscape→4:3, portrait→3:4)"
    - "1:1 square"
    - "4:5 portrait"
    - "16:9 wide"
```

**Hold processing until the user replies with their selections.**

### Mapping button selections to parameters

**Adaptive enhancements (mapped to Preset Plan built in Step 0b):**
- "All" → run all four buckets (Adaptive Person + Mood + Toon + Blur BG), plus Whiten Teeth if face detected
- "Enhance Subject" → apply all presets in the **Adaptive Person Presets** bucket
- "Mood & Tone" → apply the single preset from the **Global Mood / Tone** bucket
- "Toon & Style" → apply the single preset from the **Global Toon / Look** bucket
- "Blur Background" → apply the preset from the **Background Blur** bucket (skip Step 6 for that image)
- "Whiten Teeth" → apply the Whiten Teeth preset from the Adaptive Person Presets bucket (skip if no face detected; see body detection in Step 5)
- "None" → skip Step 5 entirely
**Manual tweaks** (all combined into one `image_apply_adjustments` call in Step 4b — use diagnostic ranges, not hardcoded defaults):
- "Recover highlights" → `highlights: -40 to -70` (use -40 for mildly blown; -70 for heavily overexposed highlights)
- "Lift shadows" → `darks: +30 to +50` (positive lifts shadow detail; use +30 for slight lift; +50 for very crushed shadows; prefer `vibrance` to compensate if skin goes dull)
- "More contrast" → `contrast: +15 to +30` (use +15 for slight pop; +30 only if image is very flat)
- "More vibrant" → `vibrance: +15 to +30` (prefer `vibrance` over `saturation` for portraits — vibrance protects skin tones)
- "Desaturate" → `saturation: -20 to -40` (use -20 for muted; -40 for near-monochrome look)
- "Blur background — depth-aware bokeh (standard)" → `image_apply_lens_blur` → `blurRadius: 8` (depth-aware, realistic bokeh; skip Step 6 if adaptive blur preset also applied)
- "Heavy background blur — stylized gaussian blur" → `image_apply_gaussian_blur` → `blurRadius: 12, blurTarget: "background"` (use only when user explicitly requests heavy/stylized blur; do not combine with Blur Background adaptive preset)
- "None" → skip Step 4b entirely
**Crop:**
- "Auto" → landscape → `"4:3"`, portrait → `"3:4"`, focus: `"face"`
- "1:1 square" → `output: "1:1"`, focus: `"face"`
- "4:5 portrait" → `output: "4:5"`, focus: `"face"`
- "16:9 wide" → `output: "16:9"`, focus: `"face"`
All crop modes use `focus: "face"`. If no face is detected, fall back to `focus: "subject"`.

After receiving button selections, confirm the settings back to the user **and show the Preset Plan**:
```
✅ Got it — here's your retouching plan:
- Style: [selected mood/style from Step 2a]
- Auto-straighten + auto-tone + auto-light
- Adaptive enhancements: [list selected categories]
  - Person presets: [preset names from bucket 1, or "none"]
  - Mood preset: [preset name, or "none"]
  - Toon preset: [preset name, or "none"]
  - Blur BG preset: [preset name, or "none"]
- Manual tweaks: [list if any, or "none"]
- Crop: [ratio or "auto 4:3/3:4"]
- Blur: [adaptive / heavy / none]

I'll preview the first image so you can confirm before I apply this to all [N] photos.
```

---

## Step 2b: Large Batch Warning (N > 5)

Include this in the confirmation when N > 5:

```
⏱ Estimated time for [N] images:
  6–10 → ~3–5 min
  11–20 → ~5–10 min
  20+ → 10+ min

Feel free to step away — I'll post a ✅ completion summary with your
download links when done. (No Slack/email notifications available from here.)
```

---

## Step 2c: Sample Preview (Before/After on Image 1)

Before running the full batch, process the **first image only** through the complete pipeline (Steps 3–7) using the confirmed settings. This gives the user a real preview of exactly what will be applied to every image.

To keep the preview fast, **first downscale image 1** to a long-edge of 1200px before running it through the pipeline. After confirmation, the final batch (Step 3) processes **all** images at full resolution — including image 1, which must not be reused from the 1200px preview output.

```
Tool: image_crop_and_resize
Params:
  imageURI: "<sourceURIs[0]>"
  options:
    output: { width: 1200, height: 1200 }   # caps both dimensions at 1200px; fit:contain preserves aspect ratio, so the long edge (width on landscape, height on portrait) is capped at 1200px
    fit: "contain"
  outputFileType: "jpeg"
```

Store the result as `preview_source_url`. Use that downscaled URL — not `sourceURIs[0]` — as the input to Steps 3–7 for the preview pass only.

1. Run the full pipeline on `preview_source_url` only (straighten → tone → tweaks → adaptive → blur → crop).
2. Call `asset_preview_file` with the original full-res source as "Before" and the processed downscaled output as "After" — `asset_preview_file` handles its own thumbnailing so the size difference is invisible to the user:
```javascript
asset_preview_file({
  assets: [
    { name: "Before", presignedAssetUrl: sourceURIs[0] },
    { name: "After",  presignedAssetUrl: processed_preview_url }
  ]
})
```

> **No-widget fallback** *(only if `asset_preview_file` is unavailable on this surface, e.g. Codex)* — present the two labeled URLs directly in the message:
> ```
> Before: <sourceURIs[0]>
> After:  <processed_preview_url>
> ```
> UI clients that render image URLs inline will show both automatically. In Codex or other non-UI agents, download both to the workspace (`curl -L -o before.jpg "<sourceURIs[0]>"`, `curl -L -o after.jpg "<processed_preview_url>"`) and reference those local paths instead.

3. Post this message:
```
👆 Here's a before/after preview using your first photo and the settings you selected.

Please confirm this looks right before I apply it to all [N] images.
```

4. Call `AskUserQuestion` with a single question:
```
Question (single_select):
  question: "Does the preview look good?"
  options:
    - "✅ Yes — apply to all [N] images"
    - "🎛️ No — adjust settings first"
    - "❌ Cancel"
```

**Processing is fully paused here.** Do not start the full batch until the user explicitly selects "Yes". This gate is mandatory and runs every time regardless of how clearly preferences were stated.

**If "Yes":** proceed to Step 3 for **all** images (`sourceURIs[0…N-1]`) at full resolution. Do not reuse the 1200px preview result — it was for confirmation only and must not appear in the final deliverables.

**If "No — adjust settings":** return to Step 2a to re-collect mood/style if needed, then Step 2 (`AskUserQuestion`) to re-collect other preferences. Once new settings are confirmed, **always repeat the preview** — reprocess image 1 with the new settings, show the new before/after, and require explicit confirmation again before proceeding. Never skip the preview gate after an adjustment.

**If "Cancel":** stop and let the user know they can restart any time.

---

## Step 3: Auto-Straighten (per image)

Loop one image at a time (no batch support):

```
Tool: image_auto_straighten
Params:
  imageURIs: ["<source_uri_N>"]
  options:
    uprightMode: "auto"
    constrainCrop: true
```

**Output:** `results[0].outputUrl` → collect as `straightened_urls[]`

On failure: use original URI, note "straighten skipped" for that image.

---

## Step 4: Auto-Tone (per image)

```
Tool: image_apply_auto_tone
Params:
  imageURIs: ["<straightened_url_N>"]
  options:
    type: "cameraRawFilter"
```

**Output:** `results[0].outputUrl` → collect as `toned_urls[]`

---

## Step 4b: Optional Tone Adjustments (batch)

If the user requested tonal tweaks, combine **all selected tweaks into a single `image_apply_adjustments` call** — no need to chain multiple calls:

```
Tool: image_apply_adjustments
Params:
  imageURIs: [all toned_urls]
  options:
    # Include only the params for tweaks the user selected.
    # Pick a SINGLE numeric value from the diagnostic ranges in Step 2 — do not pass the range string itself.
    # Example values shown; actual values must be chosen based on image severity:
    exposure: 0.4           # "Adjust exposure" — e.g. +0.3 to +0.7 (lift) or -0.3 to -0.5 (reduce)
    highlights: -55         # "Recover highlights" — range: -40 to -70 (severity-matched)
    darks: 40               # "Lift shadows" — range: +30 to +50 (positive lifts dark areas)
    brightness: 10          # if requested — range: +5 to +20
    contrast: 20            # "More contrast" — range: +15 to +30 (lower end unless very flat)
    vibrance: 20            # "More vibrant" — range: +15 to +30 (prefer over saturation for portraits)
    saturation: -30         # "Desaturate" — range: -20 to -40 (lower end unless heavy muting desired)
  outputFileType: "jpeg"
```

Omit any parameter the user did not select. One call handles all requested tweaks simultaneously.
---

## Step 5: Adaptive Enhancements (per image, opt-in only)

Only run this step if the user selected one or more adaptive enhancements. The presets to apply come from your **Preset Plan** built in Step 0b — not hardcoded names.

### 5a: Subject & Body Detection

Before applying person or teeth presets, call `image_select_subject` to understand what's in the frame. This drives two decisions: which adaptive person presets to apply, and whether Whiten Teeth is appropriate.

```
Tool: image_select_subject
Params:
  imageURI: "<tweaked_url_N>"   # Step 4b output if tweaks ran; otherwise toned_url_N
  options:
    bodyParts: ["Face", "Torso", "Clothing", "Skin", "Hair"]
```

Use the detection results as follows:
- **Face detected** → include any teeth/smile preset if user selected Whiten Teeth
- **Torso / Skin / Hair detected** → include body-targeted adaptive person presets (e.g. skin smoothing, body pop)
- **Clothing detected** → include clothing/outfit-targeted adaptive presets if present in bucket 1
- **No subject detected** → skip all Adaptive Person Presets for this image; still apply Mood and Toon presets

### 5b: Apply Preset Plan (in order)

Apply the applicable presets from your Preset Plan in this sequence, chaining each output into the next. **Only run buckets the user selected in Step 2** — use the mapping table there to determine which buckets are active for this run. Skip any bucket the user did not select, and skip any preset within an active bucket whose detection condition was not met (see 5a).

**Order (run only the buckets that were selected):**
1. **Adaptive Person Presets** (bucket 1) — only if "Enhance Subject", "Whiten Teeth", or "All" was selected. Within the bucket: skip body/clothes presets if only a face was detected and no body was found; skip Whiten Teeth if no face detected.
2. **Global Mood / Tone Preset** (bucket 2) — only if "Mood & Tone" or "All" was selected; apply once
3. **Global Toon / Look Preset** (bucket 3) — only if "Toon & Style" or "All" was selected; apply once
4. **Background Blur Preset** (bucket 4) — only if "Blur Background" or "All" was selected; apply once; if applied, **skip Step 6** for this image

```
Tool: image_apply_preset
Params:
  imageURI: "<previous_output_url>"   # for first preset: tweaked_url_N (Step 4b output) or toned_url_N if no tweaks ran; for subsequent presets: output of prior preset
  options:
    presetName: "<exact preset name from Preset Plan>"
```

**Output:** `results[0].outputUrl` → chain as input to next preset or Step 6.

**On 403 (entitlement):** Skip the preset. Note in delivery summary: "[Preset name] was skipped — not included in your Adobe plan." Continue with remaining presets.
**On other failure:** Use previous step's output; note "[preset name] skipped" in summary.

---

## Step 6: Background Blur (per image)

**Skip this step entirely** if the Background Blur Preset (bucket 4) was applied in Step 5 — the adaptive preset already handled it.

**No blur selected:** skip this step entirely.

**Standard background blur** (user selected "Blur background" and adaptive blur preset was not applied):

Prefer `image_apply_lens_blur` — it produces depth-aware, realistic bokeh by automatically detecting the subject and keeping it sharp:
```
Tool: image_apply_lens_blur
Params:
  imageURI: "<url_N>"
  options:
    blurRadius: 8    # 6–10 for subtle separation; higher for stronger bokeh
```

On failure: fall back to `image_apply_gaussian_blur` below, note "lens blur unavailable — using gaussian".

**Heavy/stylized blur** (user explicitly requested "Heavy background blur"):
```
Tool: image_apply_gaussian_blur
Params:
  imageURIs: ["<url_N>"]
  options:
    blurRadius: 12
    blurTarget: "background"
```

On failure: use previous step's output, note "blur skipped" for that image.

**Output:** `results[0].outputUrl`

---

## Step 7: Crop (per image)

**Default behavior:**
- Landscape image → crop to `"4:3"`, focus: `"face"`
- Portrait image → crop to `"3:4"`, focus: `"face"`
- User-specified ratio (1:1, 4:5, 16:9, etc.) → use that, focus: `"face"`
- If no face is detected by the crop tool, fall back to `focus: "subject"`
```
Tool: image_crop_and_resize
Params:
  imageURI: "<blur_url_N>"
  options:
    output: "4:3"          # or "3:4" / user choice
    fit: "reframe"
    focus: "face"          # falls back to "subject" if no face detected
  outputFileType: "jpeg"
```

**These are the final full-resolution deliverables.** Collect as `final_urls[]`.

---

## Step 8: Final Preview + Download Links + Firefly Board

Pass the final output URLs directly to `asset_preview_file` — do NOT run them through `image_crop_and_resize` first, as that introduces white bars or unwanted cropping. `asset_preview_file` handles its own thumbnailing correctly.

Call `asset_preview_file` for every run, regardless of batch size:

```javascript
asset_preview_file({
  assets: [
    { name: "portrait_1.jpg", presignedAssetUrl: final_url_1 },
    { name: "portrait_2.jpg", presignedAssetUrl: final_url_2 },
    // ... one entry per image
  ]
})
```

> **No-widget fallback** *(only if `asset_preview_file` is unavailable on this surface, e.g. Codex)* — list the final output URLs directly in the completion message, one entry per image:
> ```
> portrait_1.jpg → <final_url_1>
> portrait_2.jpg → <final_url_2>
> // ... one entry per image
> ```
> UI clients that render image URLs inline will display them automatically. In Codex or other non-UI agents, download each to the workspace (`curl -L -o portrait_1.jpg "<final_url_1>"`, etc.) and reference those local paths instead.

### Create Firefly Board

Call the firefly board tool with the final output urls as follows:

```javascript
create_firefly_board({
  import_adobe_storage: [
    final_output_url_1,
    final_output_url_2,
    // ...
  ]
})
```

**Board link handling:**
- Extract the returned URL and store as `board_url`.
- If `board_url` is present and non-empty, include it in the completion message.
- If the call fails or returns no URL: note "Firefly Board unavailable" in the summary (retrying does not help).
Then post the completion message. The preview grid is included in every completion message. The board link is included whenever `board_url` was returned.

**If N ≤ 3** — list individual links:
```
✅ All done! [N] portraits retouched and ready.

📥 Download your full-resolution portraits:
• Portrait 1 → <final_url_1>
• Portrait 2 → <final_url_2>

🎨 View in Firefly Board → <board_url>   ← always include if board_url is set

Pipeline applied: Auto-straighten → Auto-tone (Camera Raw) → [tweaks if any]
→ [adaptive enhancements if any] → [blur if any] → Crop [ratio]
```

**If N > 3** — list all links:
```
✅ All done! [N] portraits retouched and ready.

📥 Your retouched portraits:
• Portrait 1 → <final_url_1>
• Portrait 2 → <final_url_2>
• ...

🎨 View in Firefly Board → <board_url>   ← always include if board_url is set

Pipeline applied: Auto-straighten → Auto-tone (Camera Raw) → [tweaks if any]
→ [adaptive enhancements if any] → [blur if any] → Crop [ratio]
```

---

## Verbosity Rule

Built for large batches — report only: per-stage start, individual failures (logged once), and the final summary.
- When a pipeline stage begins for the whole batch (e.g. "Straightening [N] images...")
- If an individual image fails (log once, continue)
- Final completion summary with grid + download links
---

## Output Extraction Reference

All pipeline tools return:
```json
{ "results": [{ "success": true, "outputUrl": "https://..." }] }
```

Output is read from `results[N].outputUrl`. On `success: false` see Error Handling.

---

## Error Handling

| Situation                                                 | Action                                                                                                                                                                                                           |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `image_list_presets` returns empty or 403                 | Skip Step 5 entirely (non-blocking — all other steps continue). Note in summary: "Adaptive enhancements unavailable — no presets found on this plan."                                                            |
| `image_apply_preset` returns 403 (entitlement)            | Skip that preset. Note in delivery summary: "[Preset name] was skipped — not included in your Adobe plan." Continue with remaining presets.                                                                     |
| Any tool returns 401 (not authenticated)                  | Ask the user to re-authenticate via Adobe OAuth and retry                                                                                                                                                        |
| `asset_add_file` shows no files                           | Wait; remind user to select files in the picker                                                                                                                                                                  |
| `image_auto_straighten` fails                             | Pass original URI to Step 4; note "straighten skipped"                                                                                                                                                           |
| `image_apply_auto_tone` fails                             | Pass straightened URI forward; note in summary                                                                                                                                                                   |
| Any tone adjustment fails                                 | Log and continue with previous step's output                                                                                                                                                                     |
| `image_select_subject` fails                              | Skip all body-gated presets (Whiten Teeth, body-targeted adaptive); apply Mood and Toon presets normally                                                                                                        |
| `image_apply_preset` fails (non-403)                      | Use previous step's output; note "[preset name] skipped" in summary                                                                                                                                             |
| No portrait-appropriate preset found for a bucket         | Leave that bucket empty; do not force an ill-fitting preset                                                                                                                                                     |
| `image_apply_lens_blur` fails                             | Fall back to `image_apply_gaussian_blur` with `blurRadius: 8, blurTarget: "background"`; note "lens blur unavailable" in summary                                                                                |
| `image_apply_gaussian_blur` fails                         | Use previous step's output; note "blur skipped"                                                                                                                                                                  |
| `image_crop_and_resize` fails                             | Use blur output as final; note in summary                                                                                                                                                                        |
| `asset_preview_file` fails or is unavailable              | Present final output URLs as plain text links in the summary (see Step 8 no-widget fallback).                                                                                                                    |
| All steps fail on one image                               | Return original URI; flag clearly in summary                                                                                                                                                                     |
| Dead end                                                  | Report the failure clearly and offer to retry.                                                                                                                                                                   |

---

## Hard Constraints

- Every image in the batch is processed; failures are flagged rather than silently skipped.
- Mood/style is always collected (Step 2a) before the plan is presented — it influences Preset Plan bucket selection.
- The before/after preview gate (Step 2c) is **mandatory** — the full batch never starts without the user explicitly confirming "Yes". After any settings adjustment, the preview always repeats with the new settings before the batch runs.
- **Prefer `vibrance` over `saturation`** for portrait boosts — vibrance intelligently protects skin tones from oversaturation.
- **Prefer `image_apply_lens_blur` over `image_apply_gaussian_blur`** for background separation — lens blur is depth-aware and produces more realistic bokeh without masking. Use gaussian only for heavy/stylized blur explicitly requested by the user.
- **Tweak values are diagnostic, not hardcoded** — choose values from the reference ranges based on image content; `contrast: +15` for mildly flat images, `+30` only for very flat; `highlights: -40` for mild blow, `-70` for severe.
- **Group/condition awareness** — if the batch contains images from clearly different shooting conditions (e.g. mixed indoor/outdoor, or very different exposures), note this in the confirmation message and apply the same user-selected settings to all. For a future enhancement, per-group pipelines could be run separately.
- `image_apply_auto_tone` is called with `type: "cameraRawFilter"`.
- Adaptive enhancements are **off by default** — only run them if the user explicitly selects them.
- Preset selection is always dynamic: call `image_list_presets` at runtime; never hardcode preset names.
- All tonal/colour adjustments use `image_apply_adjustments` — the individual tools (`image_adjust_highlights`, `image_adjust_dark_portions`, `image_adjust_vibrance_and_saturation`, etc.) are deprecated and must not be used.
- Background blur is handled by the Background Blur preset from the Preset Plan (or `image_apply_lens_blur` for standard blur / `image_apply_gaussian_blur` for heavy blur); the adaptive preset and Step 6 are mutually exclusive per image.
- Whiten Teeth and body-targeted presets only run when the relevant body part is detected via `image_select_subject`.
- The pipeline is non-generative by default. Generative tools (`image_fill_area`, `image_generative_expand`) run ONLY where the surface permits generative AI (the tool is available, e.g. Codex) — never on a surface without it (e.g. Claude), and never on people even where permitted. See the Generative AI Policy above.
- Never pass a raw local filesystem path to any `image_*` tool. Local files must reach Creative Cloud first — selected via the `asset_add_file` picker, or (no-widget fallback) staged via `asset_initialize_file_upload` → PUT → `asset_finalize_file_upload`; only the resulting presigned CC URI is valid.
- Push notifications (Slack/email/text) are not available from here; completion is communicated through an in-chat summary.
