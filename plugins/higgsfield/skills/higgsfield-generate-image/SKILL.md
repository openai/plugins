---
name: higgsfield-generate-image
description: Generate or edit images with Higgsfield MCP. Use when the user asks for image creation, image-to-image, product visuals, posters, thumbnails, references, or model/cost selection.
---

# Higgsfield Generate Image

Use the OpenAI MCP profile tools only. The core path is model discovery, optional media upload, optional cost estimate, `generate_image`, then `job_status`.

## Workflow

1. Clarify only genuinely missing creative inputs. Do not ask for model details unless the user wants control.
2. Pick a model:
   - If the user names a model, call `models_get`.
   - Otherwise call `models_recommend` with a short `query` describing the goal and input context, plus `type: "image"` and `input: "image"` when references are provided, else `input: "text"`.
   - Call `models_get` for the chosen model to inspect `aspect_ratios`, model-specific `parameters`, and `medias[].roles`.
3. Prepare references:
   - For local/OpenAI file objects, call `media_upload_and_confirm` with `type: "image"` and pass the returned `media_id` in `params.medias`.
   - Authorized HTTPS image URLs may be passed directly as `params.medias[].value` for image roles; the server imports them.
   - Completed generation job UUIDs may be reused as media values.
   - Use the role declared by `models_get`, usually `image`.
4. Estimate cost only when the user asks, credits seem important, or you need a read-only preflight: call `estimate_image_cost`.
5. Submit with `generate_image`. Put all generation arguments inside `params`; keep model-specific parameters as top-level fields inside `params`, not nested under another object.
6. Poll with `job_status`. For non-terminal jobs, wait `poll_after_seconds` before calling again. Typical image jobs finish in about 10-20 seconds.
7. Present the result URL or rendered resource. Mention any server `adjustments` briefly when they changed user intent.

## Model Defaults

- Prefer `gpt_image_2` for general high-fidelity image generation, design, typography, logos, banners, and text rendering.
- Prefer Nano Banana models for characterful, stylized, or reference-heavy image work.
- Prefer Seedream or Flux-style models for edits, remixing, or style transfer when `models_recommend` points there.

## Notes

- Use `estimate_image_cost` for credit preflight, then `generate_image` for submission.
- `media_upload_and_confirm` returns a ready-to-use `media_id`; pass it directly to generation references.
- Keep reusable identity workflows explicit. If the user asks for a reusable person or character, confirm whether they want Soul training or reference elements.
- If an error includes `request_id`, include it in the user-facing failure summary.
