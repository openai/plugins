---
name: "adobe-batch-edit-photos"
description: >
  Apply consistent photo adjustments across a set of images so they look
  like they were edited together. Use this skill whenever the user says
  "make my photos look cohesive", "give all these the same style", "apply
  a warm and golden feel to all of these", "make this cinematic", "match
  the look across my photos", "edit all my travel photos the same way",
  "batch edit these", "make these consistent", "fix my phone photos",
  or uploads a folder of photos and wants a unified, polished result.
  Also triggers for requests like "apply a preset to all of these",
  "make these look professional", or "they were shot in mixed lighting
  — can you fix them all". Outputs direct final image URLs plus an in-chat
  preview grid and optional Firefly Board link.
  Access: 🔐 Signed-In required | Gen AI: ❌
license: Apache-2.0
compatibility: "Runs on both widget-capable surfaces (e.g. Claude Cowork, which supports the asset_add_file picker and asset_preview_file preview widgets) and non-UI agents (e.g. Codex, where those widgets are unavailable). The default flow uses the widgets; each widget step has a text-only fallback. Local files reach Creative Cloud via the asset_add_file picker or (no-widget) asset_initialize_file_upload -> PUT -> asset_finalize_file_upload; raw local paths are never passed to image tools."
allowed-tools: adobe_mandatory_init image_list_presets asset_add_file read_widget_context asset_initialize_file_upload asset_finalize_file_upload image_auto_straighten image_apply_auto_tone image_apply_adjustments image_apply_preset image_select_subject image_apply_gaussian_blur image_crop_and_resize asset_preview_file create_firefly_board
metadata:
  version: 3.1.0
  visibility: public
  surface: [claude, codex]
---

# Adobe Batch Edit Photos

A batch editing pipeline focused on **visual cohesion** — making a set of
photos look like they were edited together. The user picks a look (or
describes one), and the agent applies it consistently across every image using
Adobe creativity tools.

The core insight: users who want "cohesion" care less about per-image
perfection and more about the whole set reading as intentional. Prioritize
consistency of tone and color over squeezing the best out of any single image.

> **Surface note:** The default flow uses Adobe's MCP App widgets (`asset_add_file` picker in Step 1, `asset_preview_file` preview in Steps 2c and 8). Follow it as written. Only if a widget tool is **not available on this surface** (e.g. Codex) use the *No-widget fallback* attached to that step. Present `AskUserQuestion` prompts as plain-text labeled options wherever no question widget exists.

---

## Tool Reference

| Step                | Tool                                              | Notes                                          |
| ------------------- | ------------------------------------------------- | ---------------------------------------------- |
| Ingest              | `asset_add_file` (+ `read_widget_context`)        | Interactive file picker; resolve picker results via `read_widget_context` |
| Ingest *(no-widget fallback)* | `asset_initialize_file_upload` + `asset_finalize_file_upload` | Only when `asset_add_file` is unavailable — stage local files to CC programmatically |
| Discover presets    | `image_list_presets`                              | Once at startup; builds look→preset map        |
| Straighten          | `image_auto_straighten`                           | Per image                                      |
| Auto-tone           | `image_apply_auto_tone`                           | Per image, `type: "cameraRawFilter"`           |
| Look adjustments    | `image_apply_adjustments`                         | Batch — color temp + vibrance/sat + brightness/contrast in one call |
| Fine-tune tweaks    | `image_apply_adjustments`                         | Batch — all selected tweaks in one call        |
| Look preset         | `image_apply_preset`                              | Per image, core style vehicle                  |
| Element detection   | `image_select_subject` with full bodyParts array  | Per image, Step 5e opt-in; also crop focus     |
| Background blur     | `image_apply_gaussian_blur`                       | Per image, only if explicitly requested        |
| Crop                | `image_crop_and_resize`                           | Per image, optional                            |
| Sample preview      | `asset_preview_file`                              | Before/after on image[0] only *(no-widget fallback: present the 2 URLs directly)* |
| Final preview       | `asset_preview_file`                              | Batch assets array *(no-widget fallback: present the URLs directly)* |
| Firefly Board       | `create_firefly_board`                            | All edited outputs                             |

---

## Step 0 - prereq: Initialize Adobe Tools
Call `adobe_mandatory_init` first. This returns file handling rules and tool routing guidance required for the rest of the workflow.

```json
{ "skill_name": "adobe-batch-edit-photos", "skill_version": "3.1.0" }
```

---

## Step 0b: Discover Available Presets

Call `image_list_presets` immediately after init — before ingestion or user questions. This gives you the full pool of presets available on this user's plan, so Step 5b can select the best match for each look rather than relying on hardcoded names.

```
Tool: image_list_presets
Params: {}
```

From the returned list, build a **Look→Preset Map** by classifying each preset into the look category it best serves. Use the naming signals below as heuristics:

| Look | Naming signals to match |
|------|------------------------|
| **Auto (balanced)** | `Auto`, `Balanced`, `Natural`, `Neutral`, `Default`, `Adobe Color`, `Standard` |
| **Warm & Golden** | `Warm`, `Golden`, `Glow`, `Sunset`, `Cozy`, `Amber`, `Warm Pop` |
| **Bright & Airy** | `Airy`, `Bright`, `Light`, `Clean`, `Pop`, `Lift`, `Fresh` |
| **Moody & Cinematic** | `Moody`, `Cinematic`, `Dark`, `Drama`, `Dramatic`, `Shadow`, `Deep` |
| **Cool & Fresh** | `Cool`, `Blue`, `Clear`, `Crisp`, `Sky`, `Azure` |
| **Vibrant & Punchy** | `Vibrant`, `Punchy`, `Bold`, `Vivid`, `Pop`, `Saturate` |
| **Muted & Film** | `Film`, `Muted`, `Fade`, `Faded`, `Analog`, `Grain`, `Vintage`, `Matte` |

**Rules:**
- Assign each preset to at most one look. When a name matches multiple looks (e.g. "Pop" could be Bright or Vibrant), assign it to the look with the closest overall character — a soft warm pop belongs in Warm & Golden, a punchy high-contrast pop belongs in Vibrant.
- Prefer `Adaptive:` prefixed presets for look-driving since they respond to image content.
- Pick at most **2 presets per look** — one primary (strong match) and one optional secondary (complementary). Apply primary first, secondary only if it adds something different (e.g. adds a color grade the primary doesn't cover).
- If no preset matches a look, that look runs with color-temperature and manual adjustments only (no preset applied).
- If `image_list_presets` returns empty or 403: skip Step 5b for all images; note "Presets unavailable on this plan" in the summary. The rest of the look pipeline (color temp, manual adjustments) still runs.

Store the completed Look→Preset Map before Step 2. You'll reference it in Step 5b.

### Selective Adaptive Preset Buckets (for Step 5e)

From the same preset list, also build a **Selective Adaptive Map** — a separate set of buckets used only when the user opts into selective enhancements (Step 5e). These presets target specific detected scene elements rather than the whole image:

| Bucket | Naming signals | Applied when |
|--------|---------------|--------------|
| **Subject / Person** | `Subject`, `Person`, `Pop`, `Warm Pop`, `Portrait`, `Skin`, `Body` | Face, Torso, or Skin detected |
| **Sky** | `Sky`, `Blue Drama`, `Dark Drama`, `Cloud`, `Horizon`, `Outdoor` | Sky detected |
| **Background** | `Background`, `BG`, `Blur Background`, `Bokeh`, `Depth`, `Defocus` | Background detected |
| **Body Parts / Clothes** | `Clothing`, `Outfit`, `Clothes`, `Hair`, `Torso`, `Body Part` | Clothing or Hair detected |

- Pick at most **1 preset per bucket**.
- If no preset matches a bucket, leave it empty — do not force a poor fit.
- These buckets are separate from the Look→Preset Map; a preset can appear in both if it genuinely fits.

---

## Step 1: Image Ingestion

Call `asset_add_file` with no parameters to open the file picker:

```
Tool: asset_add_file
Params: {}
```

`asset_add_file` always returns `imageURIs: []` — this is expected and NOT an
error. Wait for the user to select files; the real URIs arrive in the next
message. Then call `read_widget_context` with `asset_add_file` to get the
correct presigned S3 URLs. Use those for all subsequent tool calls.
`dcx-stage.adobe.io` URIs are network-blocked; resolve them via `read_widget_context` first.

Collect the resulting presigned URLs as `sourceURIs[]` and continue to Step 2.

> **No-widget fallback** *(only if `asset_add_file` is unavailable on this surface, e.g. Codex)* — don't open a picker; get the source URIs from where the files already are. `image_*` tools only accept Creative Cloud storage URIs, never raw local paths, so any local file must be staged to CC first.
>
> **Egress check first:** check egress status from `adobe_mandatory_init` (Step 0). If egress is disabled — do NOT call `asset_initialize_file_upload` / `asset_finalize_file_upload`.
>
> | Source | Action |
> |--------|--------|
> | File(s) at a local path AND egress **enabled** | Stage each file programmatically: get its size and MIME type, call `asset_initialize_file_upload({ path: "<filename>", media_type: "<mime>" })`, PUT the file bytes to the returned upload URL, then `asset_finalize_file_upload({ filename: "<filename>", transfer_document: <from the initialize response> })`. Use each returned presigned CC URL as a source URI. |
> | File(s) already in Creative Cloud | Reference them directly by their CC URI. |
> | File(s) at a local path AND egress **disabled**, no picker on this surface | Programmatic staging is blocked and there is no file picker here — tell the user staging isn't possible on this surface and ask them to run the workflow where the `asset_add_file` picker is available. |

---

## Step 2: Understand the Desired Look

Once URIs are obtained, scan the conversation to infer as many preferences
as possible before asking anything:

- **Look**: inferrable from words like "warm", "golden", "cinematic", "moody",
  "bright and airy", "muted", "film", "cool", "vibrant", "punchy"
- **Fine-tune tweaks**: inferrable from "recover highlights", "lift shadows",
  "more contrast", "blown out", "too dark", "more vibrant", "desaturate"
- **Crop**: inferrable from "no crop", "square", "1:1", "portrait crop", "keep framing", etc.
- **Selective AI enhancements**: inferrable from "adaptive presets", "selective enhancements", "apply to detected elements", "sky presets", "subject pop", or any phrase requesting element-aware processing. If inferred as Yes, treat it as Q5 = Yes — Step 5e will run. If inferred as No or not mentioned, treat it as Q5 = No — skip Step 5e entirely.

**Three cases:**

**A — Everything clear from context:** Skip `AskUserQuestion` entirely. Post the confirmation message, then proceed directly to Step 2c (sample preview). Do NOT start the full batch — the preview and confirm gate always runs regardless of how clearly preferences were stated.

**B — Some things clear, some not:** Confirm what you've inferred upfront,
then call `AskUserQuestion` with only the questions that remain unanswered.
For example, if the look and a tweak are clear but crop isn't, post:
```
📷 Got [N] photo(s)! Based on what you said, I'll go with:
- Look: Moody & Cinematic
- Tweaks: Recover blown highlights

Just one thing — do you want a crop?
```
Then call `AskUserQuestion` with Question 3 only.

**C — Nothing specified:** Post the full intro and show all 5 questions:
```
📷 Got [N] photo(s)! I'll apply consistent edits across all of them so
the set looks cohesive.

What kind of look are you going for? 👇
```

The full `AskUserQuestion` questions (use only the ones that are still open):

```
Question 1 (single_select):
  question: "🎨 Pick a base look"
  options:
    - "Auto (balanced, neutral)"
    - "Warm & Golden — cozy, travel, golden hour"
    - "Bright & Airy — clean, light, lifestyle"
    - "Moody & Cinematic — dramatic, contrasty, desaturated"
    - "Cool & Fresh — clear skies, travel, blue tones"
    - "Vibrant & Punchy — vivid, bold, social-ready"
    - "Muted & Film — faded, analog, editorial"

Question 2 (multi_select):
  question: "🎛️ Fine-tune (optional)"
  options:
    - "Recover blown highlights"
    - "Lift dark shadows"
    - "Boost contrast"
    - "Boost color intensity"
    - "Desaturate / muted tones"
    - "Adjust exposure (brighter/darker)"
    - "Tune bright areas"
    - "Blur background (heavy)"
    - "None"

Question 3 (single_select):
  question: "✂️ Crop ratio? (optional)"
  options:
    - "No crop — keep original framing"
    - "1:1 square"
    - "4:5 portrait"
    - "16:9 wide"
    - "4:3 standard"

Question 4 (single_select):  [only ask if Q3 is not "No crop"]
  question: "🎯 How should the crop be framed?"
  options:
    - "Center — crop from center of image"
    - "Smart crop — detect subject/face and frame around it"

Question 5 (single_select):
  question: "✨ Selective AI enhancements? Detects sky, subjects, background & body parts — applies adaptive presets only to elements found in each photo"
  options:
    - "Yes — apply adaptive presets to detected elements"
    - "No — skip selective enhancements"
```

Wait for the user's reply before proceeding.

**If the user opts into selective enhancements (Q5 = Yes):** Step 5e runs per image after the look is applied. If the user declines or it wasn't asked, skip Step 5e entirely.

**Note on Question 4:** If the user's message already implies a framing preference
(e.g. "center crop", "crop to my face", "frame around the subject"), skip Q4 and
infer directly. If the user specifies a ratio but not a framing method, default to
Smart crop — it almost always produces a better result than a pure center cut.

### Look → Parameter Mapping

**Base look → `image_apply_adjustments` (color temp + vibrance/sat + brightness/contrast, Step 5a) + `image_apply_preset` (from Look→Preset Map, Step 5b):**

Combine ALL columns for the selected look into a **single `image_apply_adjustments` call** — do not make separate calls for color temp, vibrance, and contrast. Omit any parameter whose column says "none".

The preset column below is now **dynamic** — use the preset(s) from your Look→Preset Map for that look (built in Step 0b), not hardcoded names. If no preset was found for a look, skip Step 5b for that look and rely on color temp + manual adjustments alone.

⚠ **Deprecated tools are never used.** All adjustments go through `image_apply_adjustments`. The individual per-dimension adjust-* tools are deprecated — see Hard Constraints below.

| Look              | Color Temp (tempA, tempB, tempLuminance) | Preset (from Look→Preset Map) | Saturation/Vibrance          | Brightness/Contrast |
| ----------------- | ---------------------------------------- | ----------------------------- | ---------------------------- | ------------------- |
| Auto (balanced)   | **none** — omit tempA/tempB/tempLuminance | Auto (balanced) bucket preset | none                         | none                |
| Warm & Golden     | tempA=32, tempB=120, tempLuminance=67    | Warm & Golden bucket preset   | vibrance +15                 | none                |
| Bright & Airy     | tempA=20, tempB=60, tempLuminance=62     | Bright & Airy bucket preset   | saturation -10, vibrance +10 | brightness +15      |
| Moody & Cinematic | tempA=20, **tempB=-50** (negative — cool shift), tempLuminance=45 | Moody & Cinematic bucket | saturation -20 | contrast +25 |
| Cool & Fresh      | tempA=18, tempB=-123, tempLuminance=45   | Cool & Fresh bucket preset    | vibrance +10                 | none                |
| Vibrant & Punchy  | **none** — omit tempA/tempB/tempLuminance | Vibrant & Punchy bucket      | vibrance +30, saturation +15 | contrast +10        |
| Muted & Film      | **none** — omit tempA/tempB/tempLuminance | Muted & Film bucket preset   | saturation -35, vibrance -10 | contrast +10        |

**For looks with "none" in the Color Temp column** (Auto, Vibrant & Punchy, Muted & Film): do NOT include `tempA`, `tempB`, or `tempLuminance` in the `image_apply_adjustments` call. Adding color temp params to a look that has none will produce incorrect results.

**Fine-tune → `image_apply_adjustments` parameters** (all combined in one call in Step 6):
- "Recover blown highlights" → `highlights: -60`
- "Lift dark shadows" → `darks: +40` (positive = lifts/brightens dark areas)
- "Boost contrast" → `contrast: +30` in the Step 6 call. Step 5a already applied the look's contrast to the pixels — Step 6 is a separate call on the Step 5 output, so pass only the fine-tune delta (`contrast: +30`); do not sum it with the look's contrast value
- "Boost color intensity" → `vibrance: 30`
- "Desaturate / muted tones" → `saturation: -30`
- "Adjust exposure (brighter/darker)" → `exposure: +0.5` (brighter) or `exposure: -0.5` (darker); infer direction from context, default to `+0.3` if unspecified
- "Tune bright areas" → `lights: +20`
- "Blur background (heavy)" → `image_apply_gaussian_blur` → `blurRadius: 12, blurTarget: "background"` (separate call — not part of `image_apply_adjustments`)
- "None" → skip fine-tune step entirely

**Crop:**
- "No crop" → skip Step 7 entirely
- Ratio + "Center" → `image_crop_and_resize` with `fit: "reframe"`, that ratio as `output`, `align: { x: 0.5, y: 0.5 }` (pure center cut)
- Ratio + "Smart crop" → `image_crop_and_resize` with `fit: "reframe"`, that ratio as `output`, `focus: "face"` if portraits/people likely, else `focus: "subject"` (smart reframe around detected subject at the chosen ratio)

After receiving selections, confirm the settings back to the user:
```
✅ Got it — running with:
- Look: [selected look]
- Selective AI enhancements: [yes — will apply adaptive presets per detected element / no]
- Tweaks: [list if any, including "Blur background" if selected in Q2, or "none"]
- Crop: [ratio or "no crop"] + [Center / Smart crop]
```

Then proceed immediately to Step 2c (sample preview) — do not start the full batch yet.

---

## Step 2b: Large Batch Warning (N > 5)

Include this as part of the Step 2c confirmation prompt (after the before/after preview) when N > 5:
```
⏱ Estimated time for [N] images:
  6–10 → ~3–5 min
  11–20 → ~5–10 min
  20+ → 10+ min

Feel free to step away — I'll post a ✅ summary with download links when done.
```

---

## Step 2c: Sample Preview (Before/After on Image 1)

Before running the full batch, process the **first image only** through the complete pipeline (Steps 3–7, including Step 5e if selected) using the confirmed settings. This gives the user a real preview of exactly what will be applied to every image.

To keep the preview fast, **first downscale image 1** to a long-edge of 1200px before running it through the pipeline. Use the original full-resolution source only for the final batch.

```
Tool: image_crop_and_resize
Params:
  imageURI: "<sourceURIs[0]>"
  options:
    output: { width: 1200, height: 1200 }   # caps both dimensions at 1200px; fit:contain preserves aspect ratio, so the long edge (width on landscape, height on portrait) is capped at 1200px
    fit: "contain"
  outputFileType: "jpeg"
```

Store the result as `preview_source_url`. Use `preview_source_url` (not `sourceURIs[0]`) as the input to Steps 3–7 (including Step 5e if selected) for the preview pass only.

1. Run the full pipeline on `preview_source_url` only (straighten → tone → look → selective enhancements → fine-tune → blur → crop).
2. Call `asset_preview_file` with the original full-res source as "Before" and the processed downscaled output as "After" — `asset_preview_file` handles its own thumbnailing so the size difference is invisible to the user:
```javascript
asset_preview_file({
  assets: [
    { name: "Before", presignedAssetUrl: sourceURIs[0] },
    { name: "After",  presignedAssetUrl: processed_preview_url }
  ]
})
```

> **No-widget fallback** *(only if `asset_preview_file` is unavailable on this surface, e.g. Codex)* — present the two URLs directly in the message, labeled:
> ```
> Before: <sourceURIs[0]>
> After:  <processed_preview_url>
> ```
> UI clients that render image URLs inline show both automatically. In Codex or other non-UI agents, download both to the workspace (`curl -L -o before.jpg "<sourceURIs[0]>"`, `curl -L -o after.jpg "<processed_preview_url>"`) and reference those local paths instead.

3. Post this message (append the large-batch timing note here if N > 5):
```
👆 Here's a before/after preview using your first photo and the settings you selected.

Please confirm before I apply this to all [N] images.
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

**Processing is fully paused here.** Do not start the full batch until the user explicitly selects "Yes". This gate is mandatory — it runs every time, even when all preferences were stated upfront.

**If "Yes":** Start the full batch on **all** images (`sourceURIs[0…N-1]`) at full resolution (Steps 3–7, including Step 5e if selected). Do not reuse the 1200px preview result — it was for confirmation only and must not appear in the final deliverables.

**If "No — adjust settings":** Re-show the full `AskUserQuestion` set from Step 2. Once new settings are confirmed, **always repeat the preview** — process image[0] again with the new settings, show the new before/after, and require explicit confirmation again before proceeding. Never skip the preview gate after an adjustment.

**If "Cancel":** Acknowledge and stop. Do not process any images.

---

## Step 3: Auto-Straighten (per image)

```
Tool: image_auto_straighten
Params:
  imageURIs: ["<source_uri_N>"]
  options:
    uprightMode: "auto"
    constrainCrop: true
```

Output: `results[0].outputUrl` → `straightened_urls[]`

On failure: use original URI, note "straighten skipped" for that image.

---

## Step 4: Auto-Tone (per image)

```
Tool: image_apply_auto_tone
Params:
  imageURI: "<straightened_url_N>"
  options:
    type: "cameraRawFilter"
  outputFileType: "jpeg"
```

Use `type: "cameraRawFilter"` for `image_apply_auto_tone`. Output: `results[0].outputUrl` → `toned_urls[]`

---

## Step 5: Apply the Look

Apply the look in this order, chaining outputs:

**5a: Look Adjustments** — combine color temperature, vibrance/saturation, and brightness/contrast into a **single `image_apply_adjustments` call** per batch. Include only the params required by the selected look (see mapping table):

```
Tool: image_apply_adjustments
Params:
  imageURIs: ["<toned_url_1>", "<toned_url_2>", ...]
  options:
    # Color temperature (if look requires it — all three required together):
    tempA: <value>          # e.g. 32 for Warm & Golden
    tempB: <value>          # e.g. 120 for Warm & Golden
    tempLuminance: <value>  # e.g. 67 for Warm & Golden
    # Vibrance / saturation (if look requires it):
    vibrance: <value>
    saturation: <value>
    # Brightness / contrast (if look requires it):
    brightness: <value>
    contrast: <value>
  outputFileType: "jpeg"
```

Output: `results[N].outputUrl` → `look_adjusted_urls[]`

The goal is consistency: apply the same parameter values to every image — cohesion beats per-image perfection.

**5b: Look Preset** (if the Look→Preset Map has a match for the selected look)

Apply the primary preset first, then the secondary (if one exists), chaining outputs. Use the exact preset names from the Look→Preset Map built in Step 0b — never hardcode names here.

```
Tool: image_apply_preset
Params:
  imageURI: "<look_adjusted_url_N>"   # or previous preset output if chaining
  options:
    presetName: "<preset from Look→Preset Map>"
```

**On 403 (entitlement) for `image_apply_preset`:** Skip the preset for all images. Note in the delivery summary: "[Preset name] was skipped — not included in your Adobe plan." Continue to Step 5e (if selective enhancements were selected) or Step 6 (fine-tune adjustments) — do not re-apply Step 5a look adjustments, which already ran before this step.

---

## Step 5e: Selective Adaptive Enhancements (per image, opt-in only)

**Skip this step entirely** if the user answered "No" to Question 5 or if the Selective Adaptive Map has no populated buckets.

For each image, detect what scene elements are present, then apply only the adaptive presets for elements that were actually found. The result is per-image — some images may get sky presets, others may not, depending on what's in the frame. This is intentional and correct.

### 5e-1: Detect Scene Elements

```
Tool: image_select_subject
Params:
  imageURI: "<last_look_chain_url_N>"   # last output for this image: Step 5b preset output if presets ran; otherwise Step 5a look_adjusted_url
  options:
    bodyParts: ["Face", "Torso", "Clothing", "Skin", "Hair", "Sky", "Background"]
```

Map detection results to Selective Adaptive buckets:
- **Face / Torso / Skin detected** → apply Subject/Person bucket preset
- **Clothing / Hair detected** → apply Body Parts/Clothes bucket preset
- **Sky detected** → apply Sky bucket preset
- **Background detected** → apply Background bucket preset
- **Nothing detected** → skip all selective presets for this image; use the last look chain output (Step 5b preset output if presets ran, otherwise Step 5a `look_adjusted_url`) as the input to Step 6

### 5e-2: Apply Detected-Element Presets (chained)

Apply only the presets whose bucket conditions were met above, in this order: Subject → Body Parts → Sky → Background. Chain each output into the next.

```
Tool: image_apply_preset
Params:
  imageURI: "<previous_output_url>"
  options:
    presetName: "<preset from Selective Adaptive Map>"
```

**Output:** collect as `selective_urls[]` — feed into Step 6.

**On 403:** Skip that preset, note "[preset name] skipped — not on your plan." Continue with remaining selective presets.
**On detection failure:** Skip all selective presets for that image; use look output as input to Step 6.

---

## Step 6: Fine-Tune Adjustments (batch, if selected)

Combine **all selected fine-tune tweaks into a single `image_apply_adjustments` call** on the Step 5 outputs. Step 5a's look adjustments are already baked into the pixels — pass only the fine-tune delta values here. Pass all URLs at once:

```
Tool: image_apply_adjustments
Params:
  imageURIs: ["<step5_output_url_1>", "<step5_output_url_2>", ...]
  # Use selective_urls[] if Step 5e ran; otherwise the last preset output from Step 5b; otherwise look_adjusted_urls[] from Step 5a.
  options:
    # include only params for tweaks the user selected:
    highlights: -60       # "Recover blown highlights"
    darks: +40            # "Lift dark shadows" (positive lifts dark areas)
    contrast: +30         # "Boost contrast" fine-tune delta only (look contrast already applied by Step 5a)
    vibrance: 30          # "Boost color intensity"
    saturation: -30       # "Desaturate / muted tones"
    exposure: +0.5        # "Adjust exposure" (brighter) or -0.5 (darker)
    lights: +20           # "Tune bright areas"
  outputFileType: "jpeg"
```

Omit any parameter the user did not select. One call handles all tweaks simultaneously.

**Background blur** (if selected, per image):
```
Tool: image_apply_gaussian_blur
Params:
  imageURIs: ["<url_N>"]
  options:
    blurRadius: 12
    blurTarget: "background"
```

---

## Step 7: Crop (per image, if requested)

If "No crop" was selected, skip this step entirely.

Both crop modes use the same `fit: "reframe"` at the chosen ratio — the
difference is in how the frame is positioned within the image.

**Center crop** — cuts to the target ratio from the geometric center:
```
Tool: image_crop_and_resize
Params:
  imageURI: "<adjusted_url_N>"   # Step 6 output if fine-tunes ran; otherwise last Step 5 chain output (selective_urls[N] if Step 5e ran, last preset output from Step 5b if presets ran, otherwise look_adjusted_urls[N] from Step 5a)
  options:
    output: "<ratio>"        # "1:1", "4:5", "16:9", "4:3"
    fit: "reframe"
    align: { x: 0.5, y: 0.5 } # geometric center
  outputFileType: "jpeg"
```

**Smart crop** — same ratio, but positions the frame around the detected
subject or face rather than the geometric center. The subject stays in frame
even if they're off-center in the original:
```
Tool: image_crop_and_resize
Params:
  imageURI: "<adjusted_url_N>"   # Step 6 output if fine-tunes ran; otherwise last Step 5 chain output (selective_urls[N] if Step 5e ran, last preset output from Step 5b if presets ran, otherwise look_adjusted_urls[N] from Step 5a)
  options:
    output: "<ratio>"   # "1:1", "4:5", "16:9", "4:3"
    fit: "reframe"
    focus: "face"       # or "subject" for non-portrait scenes
  outputFileType: "jpeg"
```

Collect as `final_urls[]`. If no crop: `final_urls[]` = Step 6 outputs if fine-tunes ran; otherwise the last Step 5 chain outputs (selective_urls[] if Step 5e ran, last preset outputs from Step 5b if presets ran, otherwise look_adjusted_urls[] from Step 5a).

---

## Step 8: Preview

Pass the final output URLs directly to `asset_preview_file` — do NOT run them through `image_crop_and_resize` first. Adding a resize step introduces white bars (from `fit: "pad"`) or crops subjects (from `fit: "reframe"`). `asset_preview_file` handles its own thumbnailing correctly.

```javascript
asset_preview_file({
  assets: [
    { name: "photo_1.jpg", presignedAssetUrl: final_url_1 },
    // ... one per image
  ]
})
```

If `asset_preview_file` fails, present the final output URLs as plain text links in the completion summary.

> **No-widget fallback** *(only if `asset_preview_file` is unavailable on this surface, e.g. Codex)* — list the final output URLs directly in the completion message (one per image; Step 8 templates below). UI clients that render image URLs inline display them automatically; in Codex or other non-UI agents they will not, so download each to the workspace (`curl -L -o photo_1.jpg "<final_url_1>"`, etc.) and reference those local paths instead. The per-photo download links are the deliverable in every client either way.

**Before/after preview (Step 2c):** Step 2c first downscales image 1 to 1200px, then runs the pipeline on that downscale. Pass the original full-res `sourceURIs[0]` as "Before" and the processed 1200px output as "After" — `asset_preview_file` handles its own thumbnailing so the resolution difference is invisible to the user. Do not add an extra resize step.

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

- `create_firefly_board` returns a board URL. Extract it and store as `board_url`.
- If `board_url` is present and non-empty, include it in the completion message.
- If the call throws an error or returns no URL: omit the board link and note "Firefly Board unavailable" in the summary (retrying does not help).
Then post the completion message. The per-photo download links are included in every completion message. The board link is included whenever `board_url` was returned.

**If N ≤ 3:**
```
✅ Done! [N] photos edited with a consistent [look name] look.

📥 Download:
• Photo 1 → <final_url_1>
• ...

🎨 View in Firefly Board → <board_url>   ← always include if board_url is set

Look applied: [look name] → [brief description of what was applied]
```

**If N > 3:**
```
✅ Done! [N] photos edited with a consistent [look name] look.

📥 Your edited photos:
• Photo 1 → <final_url_1>
• Photo 2 → <final_url_2>
• ...

🎨 View in Firefly Board → <board_url>   ← always include if board_url is set

Look applied: [look name] → [brief description of what was applied]
```

---

## Verbosity Rule

Report only: major stage starts, per-image failures (logged once), and the final summary.
- When a major stage starts (e.g. "Applying Warm & Golden look to [N] images…")
- Any per-image failure (log once, continue)
- Final summary with grid + download links

---

## Output Extraction

All pipeline tools return:
```json
{ "results": [{ "success": true, "outputUrl": "https://..." }] }
```

Read `results[N].outputUrl`. On `success: false` → see Error Handling.

---

## Error Handling

| Situation                                           | Action                                                                                                                                                                                                   |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `image_list_presets` returns empty or 403           | Skip Steps 5b and 5e for all images. Note in summary: "Presets unavailable on this plan." Color temp and manual adjustments still run.                                                                 |
| `image_select_subject` fails in Step 5e             | Skip all selective presets for that image; use look output as input to Step 6. Note once in summary.                                                                                                    |
| `image_apply_preset` returns 403                    | Skip preset for all images. Note in summary: "[Preset name] was skipped — not included in your Adobe plan." Continue with other look steps.                                                             |
| Any tone/color tool returns 403                     | Skip that step. Note in summary. Continue.                                                                                                                                                               |
| Any tool returns "No approval received"             | Treat the same as a 403 entitlement error. For optional steps (presets, fine-tune adjustments, preview), skip and note in summary. Retrying does not help for this error — continue per the rules above. |
| Any tool returns 401                                | Ask user to re-authenticate via Adobe OAuth and retry.                                                                                                                                                   |
| Any tool returns "file too large or corrupted"      | Stop processing that image immediately. Do not retry. Tell the user: "I couldn't process [filename] — it's either too large or the file may be damaged. Try re-uploading a smaller version, or check that the file opens correctly on your end." Flag the image in the summary and continue with remaining images. |
| Programmatic upload fails (PUT 5xx / no egress)     | Fall back to the `asset_add_file` picker (default ingest path) and tell the user you're opening it to stage the file(s).                                                                                  |
| `asset_add_file` shows no files (picker path)       | Remind the user to select files in the picker.                                                                                                                                                           |
| URI starts with `dcx-stage.adobe.io` (picker path)  | Resolve it via `read_widget_context` to the real presigned S3 URL.                                                                                                                                       |
| `image_auto_straighten` fails                       | Use original URI; note "straighten skipped".                                                                                                                                                             |
| `image_apply_auto_tone` fails                       | Use straightened URI; note in summary.                                                                                                                                                                   |
| Any adjustment tool fails                           | Use previous step's output; note in summary.                                                                                                                                                             |
| `image_apply_gaussian_blur` fails                   | Use previous output; note "blur skipped".                                                                                                                                                                |
| `image_crop_and_resize` fails                       | Use blur/adjusted output as final; note in summary.                                                                                                                                                      |
| `asset_preview_file` returns "No approval received" | Present final output URLs as plain text links in the summary instead.                                                                                                                                    |
| All steps fail on one image                         | Return original URI; flag clearly in summary.                                                                                                                                                            |

---

## Hard Constraints

- Every image in the batch is processed; failures are flagged rather than silently skipped.
- Never pass a raw local filesystem path to any `image_*` tool. Local files must reach Creative Cloud first — selected via the `asset_add_file` picker, or (no-widget fallback) staged via `asset_initialize_file_upload` → PUT → `asset_finalize_file_upload`; only the resulting presigned CC URI is a valid source for image tools.
- `image_apply_auto_tone` is called with `type: "cameraRawFilter"`.
- Apply the **same parameter values** to every image in the batch (cohesion over perfection).
- Preset selection is always dynamic: call `image_list_presets` at runtime and build both the Look→Preset Map and Selective Adaptive Map; never hardcode preset names.
- All tonal/colour adjustments (color temperature, vibrance, saturation, brightness, contrast, exposure, highlights, shadows, darks, lights) use `image_apply_adjustments` — the individual tools (`image_adjust_color_temperature`, `image_adjust_vibrance_and_saturation`, `image_adjust_highlights`, etc.) are deprecated and must not be used.
- Combine all look adjustments (Step 5a) into one `image_apply_adjustments` call and all fine-tune tweaks (Step 6) into one `image_apply_adjustments` call — never chain multiple adjustment calls.
- Selective adaptive enhancements (Step 5e) are **off by default** — only run when the user explicitly opts in via Question 5.
- Step 5e applies presets only to detected elements — an image with no sky gets no sky preset, an image with no person gets no subject preset. Per-image variation here is correct.
- The preview pass uses a 1200px downscaled version of image 1; full-resolution is used for the final batch.
- Background blur uses `image_apply_gaussian_blur` with `blurTarget: "background"` (`image_apply_lens_blur` is not used here).
- The before/after preview gate (Step 2c) is **mandatory and cannot be skipped** — the full batch never starts without explicit user confirmation, regardless of how clearly preferences were stated upfront.
- After the user adjusts settings, the preview always repeats with the new settings before the batch runs. There is no "run all now without preview" escape path.
- Completion is posted as a clear in-chat message (no push notifications).
