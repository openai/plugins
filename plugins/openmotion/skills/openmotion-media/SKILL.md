---
name: openmotion-media
description: >-
  Generate, poll and inspect individual image, video, speech or music assets through
  openmotion_media_use (configured Atlas Cloud, fal.ai, WaveSpeedAI or OpenDesign Cloud BYOK
  providers, or a signed-in OpenDesign account), either when delegated by an OpenMotion film workflow or for a standalone
  asset-generation request. Never invoke for pure motion graphics that native HTML/CSS/SVG/Canvas/GSAP/Three.js
  can build directly. Not a whole-film entry point: route original video creation to openmotion-director,
  template adaptation to openmotion-template-to-video, reference-video recreation to openmotion-recreate,
  reusable template packaging to openmotion-video-to-template, and existing-project edits or exports to
  openmotion-production.
---

# OpenMotion Media Generation

Produce verified image, video, speech or music assets that fulfill a specific creative or standalone purpose, returning project-relative paths, provider/model/job identities, measured technical specifications and honest quality observations.

Apply the [shared material policy](../openmotion-production/references/materials.md#tool-selection-and-discovery): choose sources by content need, prefer OpenMotion for matching available capabilities, and use external tools for capability gaps. Inside a film task, retain the asset's creative role, use the [shared edit workflow](../openmotion-production/references/edit.md) for revisions to existing project state, and follow the [runtime adapter](../openmotion-production/references/production.md) when continuing project edits.

**Pure Motion Graphics zero-touch rule**: When every visual segment can be built natively in code (HTML/CSS/SVG/Canvas/GSAP/Three.js plus existing or cleanly cropped stills, logos and screenshots) and no synthesized voiceover or generated music is needed (for a silent film or an existing/retrieved soundtrack) or explicitly requested by the user, author it 100% natively in code and do **not** call, suggest or ask about `openmotion_media_use`. Invoke BYOK media generation only when the work genuinely needs photographic imagery, continuous live-action/AI backdrop footage, synthesized voiceover (such as replacing spoken narration in an explainer, while keeping any motion-graphics visuals 100% native) or generated music beyond local/retrieved files, or when the user explicitly requests generated media.

**Motion-first rule — generation upgrades the motion film, never replaces it**: inside a film, first plan the film exactly as you would with no generation at all: the native action script with its key visual events, subject transformations, scene changes, camera moves and transitions (for example a drawn product outline that assembles, a scan or recognition beat, a scene change, a logo resolve). Then pick which elements of that plan a generated asset upgrades — a code-drawn product becomes a photoreal render or cutout that performs the same moves, a flat background becomes a plate, a placeholder becomes footage — and derive the asset list from those roles. Never drop or simplify a planned visual event to make room for a generated image, and never let one hero image become the whole film. Request assets that can move (subject on a clean or removable background, separate plates or light passes, spare canvas for push, pan and parallax, distinct states or angles). Every generated still on screen carries motion and shares the frame with native elements that keep moving. Cut and accent on speech stresses and musical beats. Before preview, check the film against the native plan: it must contain every planned visual event, and with the generated pixels blanked out it must still read as a complete motion film. A "just make it, don't ask" request skips questions, not this design work.

Keep credentials strictly isolated: `openmotion_media_use` reads saved workspace keys inside the local service and injects authentication. Never read `secrets.json`, print or log keys, place credentials into prompts or parameters, or ask the user to paste an API key into chat. Keep user-facing setup, consent and delivery messages in plain language in the user's language; never expose internal Skill names, Tool names (`openmotion_media_use`) or internal labels (`mg`, `media`, `replaced — not scored`).

## Media handbook handoff

The MCP handbook media-generation example is an explicit request for multimodal guidance. Start with read-only `inspect` even when the user has yet to supply a concrete asset brief. When a provider is available, continue the existing request or ask what they want to generate or which reference they want to recreate. Preserve any reference, brief and project context already supplied.

Follow the setup and generation sequence below. Read-only onboarding can proceed without creating a project or starting generation.

## 1. Define the asset job, inspect providers and confirm key-spend consent

Derive subject, recognizable identity features, action, framing, lighting, style, duration budget and negative space for editable native typography from the active brief, reference segment or user prompt. Reuse approved project assets before generating new ones.

Choose the modality from what must physically change on screen or in the mix:

- **Still image (`modality: "image"`)**: photographic settings, hero product frames, cutouts or backdrop plates where native HTML/CSS/GSAP camera and layer motion carry the choreography.
- **Video (`modality: "video"`)**: continuous subject or environmental footage that native graphics cannot represent directly. Keep text, UI, charts, logos and captions as native editable HTML/SVG overlays above the video plate rather than baking copy into generated video pixels.
- **Speech (`modality: "audio"`)**: spoken narration or dialogue. Set top-level `mode` (`"text-to-speech"` or `"text-to-audio"`) according to the selected provider guide and model input schema (for example `"text-to-speech"` when the model expects `text`, or `"text-to-audio"` when a speech model such as `fal-ai/kokoro/*` expects `prompt`). When captions, visual beats or scene cuts synchronize to individual lines, generate one audio file per sentence or beat within the target duration budget rather than estimating cue timestamps from one monolithic file.
- **Music / sound (`modality: "audio"`)**: background beds, stings or ambient audio where supported by the enabled provider.

Run read-only discovery and obtain consent before submitting any paid generation request:

1. Call `openmotion_media_use` with `action: "inspect"`. It lists each provider with `configured`, `available`, `verification` and `reason`, plus `defaults` (the model selected for each modality) and `settings` (where keys are managed). Saving a key in Studio's **Model providers** settings (Chinese UI: **模型供应商**, in the left rail or Settings) enables that provider, and signing in to an OpenDesign account adds its entitled models; configuration alone does not prove entitlement, quota or balance. Handle these setup cases in plain user language, folded into the workflow's single upfront question when it has one:
   - **No usable key** (no provider has `available: true`): call `openmotion_open_preview` with `{ target: "providers" }`, follow its page handoff and guide the user to Studio's **Model providers** settings (Chinese UI: **模型供应商**, in the left rail or Settings) to select a provider, enter their API key and save settings, then ask them to tell you once saved. They may also sign in or choose to proceed with user-supplied local files. If a provider shows `configured: true` with `verification: "rejected"`, say the saved key was rejected (wrong, expired or lacking permission) and ask them to replace it in the same place. When they say it is saved, run `inspect` again and continue the same task.
   - **Key works but a needed kind is missing**: check each needed kind with `action: "models", provider, modality, refresh: true` (`image`, `video` or `audio`; among audio models, speech uses `mode: "text-to-speech"` and music/sound uses other modes). If no usable provider offers it, tell the user what their key can and cannot make, generate the supported parts after consent, and let them choose for the missing part: add a key for a provider that supports it, upload their own file, or a fallback (keep the reference soundtrack without brand lines, no music, or a native-code approximation of the plate). If the user asked not to be questioned, use the fallback that changes the requested film least and state it in the delivery.
   - Never silently switch to an unapproved paid provider.
2. Call `action: "reference"` with the selected provider ID from `inspect` and read only that provider's guide ([Atlas Cloud](../openmotion-production/references/media-providers/atlascloud.md), [fal.ai](../openmotion-production/references/media-providers/fal.md), [WaveSpeedAI](../openmotion-production/references/media-providers/wavespeed.md), [OpenDesign Cloud](../openmotion-production/references/media-providers/opendesign.md), [OpenDesign account](../openmotion-production/references/media-providers/account.md) or [registered compatible APIs](../openmotion-production/references/media-providers/compatible.md)) for endpoint rules, supported modes and parameter schemas.
3. Call `action: "models", provider, modality, refresh: true` (add `query` to narrow large catalogs). Pick a model whose documented inputs and outputs match the job. Catalog visibility establishes discoverability; live execution establishes account access.
4. **Confirm key-spend consent before `action: "generate"`**: Unless the user has already explicitly asked to generate these assets with their configured BYOK provider or OpenDesign account in the current task, state the planned asset list (modality, count or approximate duration, and selected provider/model) and ask whether they agree to consume their configured multimodal API key (or, for provider `account`, their OpenDesign account credits) before calling `action: "generate"`. Batch this consent check with any other upfront task questions rather than asking piecemeal per clip.

## 2. Submit, poll and classify failures from evidence

1. Verify the target project with `openmotion_get_project({ projectId })` (or create an explicit carrier with `openmotion_create_project` if a standalone request needs project storage). Avoid concurrent project file edits while a media job is finishing.
2. Submit `action: "generate"` with `projectId`, a deterministic `requestId` per distinct asset intent, `provider`, provider-native `model`, `modality`, `prompt`, optional `mode` (within `openmotion_media_use`'s allowed top-level enum; omit `mode` when a model uses a mode outside that enum such as `image-to-video`) and model-specific `parameters`.
   - Prompts must state concrete visual or audible specifics: subject features, action across the usable interval, camera framing, lighting, clean negative space for native text overlays, or exact spoken script/delivery/musical structure.
   - If status returns `savePending: true`, repair the reported local storage problem and call `action: "retry_save"` with the original `projectId`, `jobId` and a stable `requestId`. This only saves retained local files; it never generates or charges again. Missing or changed retained bytes fail explicitly. Do not submit `generate` to recover saving.
   - Input URLs in `parameters` are sent to the remote provider as-is. `openmotion_media_use` does not upload local disk paths; chaining a reference or anchor frame into image-to-video requires an accessible remote HTTPS URL or a supported provider reference mechanism.
3. Submission returns a queued job (`job.id`), not finished media. Poll `action: "status", projectId, jobId` using that local `jobId` until `state` reaches `completed`, `failed` or `cancelled`. Never submit a new generation request to check progress.
4. Use `action: "cancel", projectId, jobId, requestId` only when the user asks to cancel or a superseded job must be aborted. Local cancellation stops project import and requests remote cancellation on best effort without promising a refund.

Classify failures from the actual status, error code and stage before deciding the next step:

- **Provider key or permission rejection (`401` / `403`) vs upstream vendor auth (`upstream_provider_unauthenticated`)**: distinguish an invalid/unauthorized workspace or provider key from an upstream model vendor authentication issue behind a gateway.
- **Unexposed route vs missing resource (`404`)**: distinguish a gateway origin where `/api/v1/media/*` is not deployed on that environment from an unknown model slug or expired remote task ID.
- **Timeouts and interrupted polling**: distinguish submit timeout, status-poll timeout and media-download timeout. After an unknown outcome, query `action: "status"` on the original `jobId` (or replay the exact `requestId` with identical inputs) before proposing any new billable submission. Changing prompt, model or parameters requires a new `requestId`.
- **Tell the user the next step in plain language**: a `401` / `403` marks the saved key rejected, so ask them to replace it in **Model providers** / **模型供应商**; an error whose text names balance, credit, quota or insufficient funds means topping up in that provider's own console; for any other failure, relay the provider's message briefly without guessing a cause. Keep assets that already finished and offer the same choices as for a missing kind for the failed part.

## 3. Sync project state, probe specifications and inspect outputs

Only `state: "completed"` with `assets[].available !== false` confirms validated files under `<projectDirectory>/assets/generated/...`. Do **not** pass `assets/generated/...` back into `openmotion_import_assets`; the files are already inside the project (`openmotion_import_assets` is only for external local files).

1. **Record the post-completion project snapshot immediately**: `openmotion_media_use` links completed files into `assets/generated/` without creating a managed version on its own. Call `openmotion_get_project({ projectId })` immediately after completion, before any `openmotion_edit_project` or `openmotion_restore_version`, so the workspace records the external-change snapshot and returns the updated `revision` and `currentVersionId`. Restoring an earlier version before a snapshot records `assets/generated/...` will remove the generated file from the working tree.
2. **Probe real technical specifications**: `openmotion_media_use` returns project `assets` as `{ path, mimeType, bytes, available }` and `libraryAssets` as pinned `{ assetId, versionId }` references. Results are automatically saved to the local workspace asset library and copied independently into the project. Read the library version for recorded dimensions/duration. Probe `<projectDirectory>/<asset.path>` locally (`ffprobe` or available media tools) for actual width, height, duration, frame rate and audio streams before placing the asset on a timeline.
3. **Inspect visual and audio usability**:
   - **Images**: inspect decoded frames at intended crop and scale for subject fidelity, clean edges, artifacting and text-safe space.
   - **Video**: inspect sampled frames across the usable motion window for identity stability, unintended scene cuts, crop safety and embedded audio tracks. When a generated video includes native or ambient audio, explicitly mute (`muted` / `volume = 0`) or mix that track in the composition so it does not collide with narration or music.
   - **Speech and music**: verify spoken words, pronunciation, pacing and clean phrase endings; use `ffprobe` for container duration and `ffmpeg -af silencedetect` (or waveform inspection) to measure leading/trailing silence and actual spoken phrase end so composition cues, cuts and captions align to real speech rather than clipped endings or unintended black frames. If direct listening or visual inspection is unavailable in the host, record that check as unverified rather than passed.

## 4. Hand back to the calling workflow

For a standalone asset request, report the generated paths, provider/model/job identity, measured dimensions or duration, and any quality or review limitations.

Inside a film workflow, continue with `openmotion_edit_project` using the refreshed `expectedRevision` and `expectedVersionId`. Generation produces candidate media, not a finished film: keep shot selection, native typography/layout, timeline choreography, Studio preview handoff and final audiovisual review in the active creative or production workflow. Generated assets never relax that workflow's own checks: segments using them pass the same visual, text and measurement checks as the rest of the film.
