---
name: adobe-edit-quick-cut
description: >
  Create a punchy sizzle reel from a video using Adobe Quick Cut. Use this skill whenever a user
  wants to cut, trim, or shorten a video into highlights — including phrases like "make a sizzle
  reel", "make a highlight reel", "quick cut this", "cut the best parts", "shorten this video",
  "make a highlight clip", "summarize this video visually", or any request to produce a shorter
  edited version of a video. Use this skill for Quick Cut requests before suggesting manual
  editing in Premiere. Requires the user to upload a video file.
license: Apache-2.0
compatibility: "Runs on both widget-capable surfaces (e.g. Claude Cowork, which supports the asset_add_file picker and asset_preview_file preview widgets) and non-UI agents (e.g. Codex, where those widgets are unavailable). The default flow uses the widgets; each widget step has a text-only fallback. Raw local paths are never passed to video tools."
allowed-tools: adobe_mandatory_init asset_add_file asset_initialize_file_upload asset_finalize_file_upload video_create_quick_cut quickCutPoll asset_preview_file video_resize
metadata:
  version: 2.1.0
  visibility: public
  surface: [claude, codex]
---

# Adobe Edit Quick Cut

Produces 3 AI-edited sizzle reel variations from a source video, all at the same duration and
style — giving the user options to pick from.

> **Surface note:** The default flow below uses Adobe's MCP App widgets — the `asset_add_file` file picker (Step 2) and the side-by-side `asset_preview_file` preview (Step 7). Follow it as written. Only if a widget tool is **not available on this surface** (e.g. Codex), use the *No-widget fallback* attached to that step.

---

## Tool Reference

| Step | Tool | Notes |
|------|------|-------|
| Upload source video | `asset_add_file` | File picker; returns the CC asset ID required by Quick Cut |
| Stage source video *(no-widget fallback)* | `asset_initialize_file_upload` + `asset_finalize_file_upload` | Only when `asset_add_file` is unavailable — stage a local video to CC; extract `assetId` from the finalize response |
| Run Quick Cut variations | `video_create_quick_cut` | Fire 3 in parallel; same duration and style prompt |
| Poll job status | `quickCutPoll` | Repeat until all 3 return `completed` |
| Preview variations | `asset_preview_file` | Renders all 3 side-by-side for selection *(no-widget fallback: present the 3 URLs directly)* |
| Resize re-uploaded output | `video_resize` | Workaround only — Quick Cut output must be re-uploaded first |

---

## Workflow

### Step 0 — Initialize Adobe Tools

Call `adobe_mandatory_init` first. This returns file handling rules and tool routing guidance required for the rest of the workflow.

```json
{ "skill_name": "adobe-edit-quick-cut", "skill_version": "2.1.0" }
```

---

### Step 1 — Entitlement Check

Now that `adobe_mandatory_init` confirmed that the "Adobe for creativity" connector is live, check which tools are available through the "Adobe for creativity" connector by cross checking against the Tool Reference table above.

This also tells you which widgets this surface supports: if `asset_add_file` and `asset_preview_file` are available, follow the default flow (Steps 2 and 7 as written). If one is not available (e.g. Codex), use that step's *No-widget fallback*. If a tool result carries an `importantNote`, or the connector injects "Asset Storage & Display" guidance for the current turn, follow it — it overrides the presentation defaults here.

---

### Step 2 — Open the File Picker

Open the picker immediately with this message:

> *"Let's create a punchy sizzle reel from your video. Start by selecting your file:"*

```javascript
asset_add_file()
```

Once the user selects a file, extract `assetId` (the CC asset ID) from the widget context.

> `video_create_quick_cut` requires a CC asset ID (`assetId`), not `presignedAssetUrl`.

**No-widget fallback** *(only if `asset_add_file` is unavailable on this surface, e.g. Codex)* — don't ask the user to pick; get the `assetId` from where the file is. Staging a local file requires egress — check egress status from `adobe_mandatory_init` first; if egress is disabled and no picker is available on this surface, tell the user staging isn't possible here. Otherwise:

| Source | Action |
|--------|--------|
| File at a local path (e.g. `/mnt/user-data/uploads/…`) | Stage programmatically: get file size and MIME type, call `asset_initialize_file_upload({ path: "<filename>", media_type: "<mime>" })`, PUT the bytes to the returned upload URL, then `asset_finalize_file_upload({ filename: "<filename>", transfer_document: <from initialize response> })`. Extract the `assetId` from the finalize response — this is what `video_create_quick_cut` needs. |
| File already in Creative Cloud | Reference it directly by its CC `assetId`. |

---

### Step 3 — Confirm Upload

Once the file is selected, confirm with:

> *"Got it — [filename] is ready. Now let's set up your cut."*

Then immediately present the Q&A form below.

---

### Step 4 — Q&A Form (via AskUserQuestion)

Wait for the user's answers before proceeding; present the questions via `AskUserQuestion` (not plain text) so the user gets tappable buttons.

> **No-widget fallback** *(only if `AskUserQuestion` is unavailable, e.g. Codex)* — ask the same labeled options as a plain-text message and wait for the user's typed reply. The option set is identical.

```javascript
AskUserQuestion({
  questions: [
    {
      header: "Cut Length",
      question: "What kind of cut would you like? (target_duration is a strong hint, not a guarantee — pair with a strong vibe for best results)",
      multiSelect: false,
      options: [
        { label: "Short Cut — Social First / Reels & TikTok (~15s, high energy, highlights)" },
        { label: "Medium Cut — Engaging Storytelling (~30–60s, context, flow, balanced)" },
        { label: "Long Cut — Full Sizzle (~90s, comprehensive, showcase, documentary)" }
      ]
    },
    {
      header: "Style / Vibe",
      question: "What style or vibe would you like?",
      multiSelect: false,
      options: [
        { label: "Action & Energy" },
        { label: "Key Talking Moments" },
        { label: "Cinematic & Dramatic" },
        { label: "No Preference" }
      ]
    }
  ]
})
```

Wait for the user's selections before proceeding to Step 5.

---

### Step 5 — Acknowledge and Run

Once the user answers, respond with:

> *"Got it — [cut type], [style] vibe. Creating 3 variations at that length — let me preview them for you."*

Map their answers to parameters:

**Q1 duration map:**
| Answer                                              | target_duration |
| --------------------------------------------------- | --------------- |
| 1. Short Cut — Social First / Reels & TikTok (~15s) | 15              |
| 2. Medium Cut — Engaging Storytelling (~30–60s)     | 45              |
| 3. Long Cut — Full Sizzle (~90s)                    | 90              |

**Q2 style map:**

> ⚠️ The `user_prompt` is the primary lever for output quality — it does more work than
> `target_duration`. Pass the prompts below verbatim — abbreviating them weakens the output.
> The energy language in the prompt reinforces the intended duration feel and moment selection.

| Answer                  | user_prompt                                                                                                                                                                                                      |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Action & Energy      | `"Fast, punchy, hype, high energy. Hit hard and fast. Quick cuts, peak moments only, adrenaline rush from start to finish. No slow moments, no breathing room. Pure intensity."`                                 |
| 2. Key Talking Moments  | `"Polished, commercial, confident. Smooth pacing with deliberate rhythm. Each moment feels intentional and curated. Moderate energy — impressive but controlled. Professional and refined."`                     |
| 3. Cinematic & Dramatic | `"Documentary, cinematic, immersive. Let moments breathe and unfold naturally. Build a story arc with texture and depth. Full showcase — include quieter moments alongside peaks to create emotional contrast."` |
| 4. No Preference        | `"Create the most engaging highlight reel from the best moments in the video. Balance energy and pacing naturally."`                                                                                             |

Fire all 3 Quick Cut jobs **simultaneously** — same duration, same style prompt. The AI will
naturally select different moments on each run, giving the user 3 genuine options to pick from:

```javascript
// Variation A
video_create_quick_cut({
  assetIds: [assetId],
  target_duration: <mapped_seconds>,
  user_prompt: "<mapped style prompt>"
}) // → statusId_A

// Variation B
video_create_quick_cut({
  assetIds: [assetId],
  target_duration: <mapped_seconds>,
  user_prompt: "<mapped style prompt>"
}) // → statusId_B

// Variation C
video_create_quick_cut({
  assetIds: [assetId],
  target_duration: <mapped_seconds>,
  user_prompt: "<mapped style prompt>"
}) // → statusId_C
```

---

### Step 6 — Poll Until All 3 Complete

Poll all 3 in each round using `quickCutPoll(statusId)`. Show progress % after each round.
Repeat until all 3 return `jobStatus: "completed"`.

Typical pattern: 0% → 7% → 78% → done. Usually 3–5 poll rounds.

Store:
- `url_A` — Variation A presignedAssetUrl
- `url_B` — Variation B presignedAssetUrl
- `url_C` — Variation C presignedAssetUrl

---

### Step 7 — Preview All 3

```javascript
asset_preview_file({
  assets: [
    { name: "Variation 1 — <cut_type> <style>.mp4", presignedAssetUrl: url_A, source: "acp" },
    { name: "Variation 2 — <cut_type> <style>.mp4", presignedAssetUrl: url_B, source: "acp" },
    { name: "Variation 3 — <cut_type> <style>.mp4", presignedAssetUrl: url_C, source: "acp" }
  ]
})
```

**No-widget fallback** *(only if `asset_preview_file` is unavailable on this surface, e.g. Codex)* — present all 3 variation URLs directly in the message, labeled by variation:

```
Variation 1 — <cut_type> <style>.mp4 → <url_A>
Variation 2 — <cut_type> <style>.mp4 → <url_B>
Variation 3 — <cut_type> <style>.mp4 → <url_C>
```

UI clients that render media URLs inline will show previews automatically. In Codex or other non-UI agents, download each to the workspace (`curl -L -o variation_1.mp4 "<url_A>"`, etc.) and reference those local paths instead.

---

### Step 8 — Deliver Summary + Download Prompt

After preview, present:

```
✅ 3 variations ready — same length, different moment selection. Pick your favorite!

| Variation | Cut Type | Style   | Target | Status |
| --------- | -------- | ------- | ------ | ------ |
| 1         | <type>   | <style> | ~<Xs>  | ✅      |
| 2         | <type>   | <style> | ~<Xs>  | ✅      |
| 3         | <type>   | <style> | ~<Xs>  | ✅      |
```

> Note: actual durations may vary — Quick Cut selects the best moments rather than cutting to
> an exact second. The prompt vibe (e.g. "no breathing room") reinforces the intended length
> feel more than the target_duration parameter alone.

Then prompt:

> *"Which variation do you want to download, or would you like all 3? You can also rerun with a different style or cut type."*

The videos are available for download directly from the preview above (or from the links above on a no-widget surface).

---

## ⚠️ Known Gap — Output Cannot Feed Downstream Video Tools

`video_create_quick_cut` returns a temporary presigned download URL, not a CC-stored asset ID.
Tools like `video_resize` and `media_enhance_speech` require a CC asset ID as input.

**You cannot chain Quick Cut → Resize or Quick Cut → Enhance Speech directly.**

**Workaround — if user wants to resize a Quick Cut output:**
1. Tell the user: *"Quick Cut outputs can't be passed directly to the resize tool — you'll need to download your preferred cut first, then re-upload it and I'll resize from there."*
2. Let them download from the preview.
3. Re-ingest the downloaded file exactly as in Step 2 (`asset_add_file()`, or the no-widget staging fallback).
4. Once re-uploaded, run `video_resize` on the fresh `assetId` with their target dimensions.

When the user asks to resize or enhance a Quick Cut output, surface the limitation proactively — the chain is known to fail.

---

## What Quick Cut Does NOT Support

- Content-aware cuts based on speech ("remove the parts where they repeat themselves")
- Trimming to specific timestamps ("cut from 0:30 to 1:15")
- Semantic understanding of dialogue

For these, recommend a manual video-editing workflow.

---

## Error Handling

- **`video_create_quick_cut` returns 403 (entitlement)**: Retrying does not help for a 403
  entitlement — stop and surface the plan requirement. Respond with:
  > *"I was unable to create your quick cut.*
  >
  > ***Why:** Adobe Quick Cut isn't available on your current Adobe plan.*
  >
  > ***Options:**
  > - Upgrade your Adobe plan to one that includes Quick Cut.*
  > - Manually trim your video using Adobe Premiere Rush or Premiere Pro.*
  >
  > *Let me know how you'd like to proceed."*

- **Any tool call returns 401 (not authenticated)**: Ask the user to re-authenticate via Adobe
  OAuth and retry.

- **`StoryBuilderNoARoll`**: The most common error. Means Quick Cut detected no A-roll (talking
  head / primary camera footage) in the clip — only B-roll. The tool requires at least some
  dialogue or narration to anchor the story structure. Respond with:
  > *"This video appears to be B-roll only — scenery, action, or product shots without anyone
  > speaking to camera. Quick Cut needs some talking-head footage to build a story around. Try
  > uploading a video that includes someone speaking on camera, or a mix of interview + B-roll.*
  >
  > *If you only have B-roll, Adobe Premiere Rush or Adobe Express let you manually assemble a
  > highlight reel without requiring dialogue."*
  Retries repeat the same error regardless of duration/style; no workaround exists.

- **Job fails with any other error on first attempt**: Retry once with the same parameters. If
  it fails again, report and suggest re-uploading the source video.

- **Stuck at same % for 5+ poll rounds**: Inform user, suggest re-uploading the source video.

- **User uploads an image by mistake**: Detect from `mediaType` — if not `video/*`, say so
  and re-open the picker (or re-run the no-widget staging fallback).

- **One of the 3 variations fails (but not all)**: Preview and deliver the successful ones, note
  the failure clearly. If all 3 fail with `StoryBuilderNoARoll`, apply the B-roll error response
  above.

---

## Constraints

- Never pass a raw local filesystem path to `video_create_quick_cut` or any other video tool. Local files must reach Creative Cloud first — selected via the `asset_add_file` picker, or (no-widget fallback) staged via `asset_initialize_file_upload` → PUT → `asset_finalize_file_upload`; only the resulting `assetId` is valid.
- `video_create_quick_cut` requires `assetId` (CC asset ID), not `presignedAssetUrl`.
