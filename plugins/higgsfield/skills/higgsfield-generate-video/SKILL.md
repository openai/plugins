---
name: higgsfield-generate-video
description: Generate or animate videos with Higgsfield MCP. Use when the user asks for text-to-video, image-to-video, start/end frames, cinematic clips, model/cost selection, or job polling.
---

# Higgsfield Generate Video

Use the OpenAI MCP profile tools only. The core path is model discovery, optional media upload, optional cost estimate, `generate_video`, then `job_status`.

## Workflow

1. Clarify only missing creative intent, duration/aspect ratio when important, or required reference media.
2. Pick a model:
   - If the user names a model, call `models_get`.
   - Otherwise call `models_recommend` with a short `query` describing the goal and input context, plus `type: "video"` and `input: "image"` for image-to-video/reference work, else `input: "text"`.
   - Call `models_get` to inspect `durations`, `duration_range`, `aspect_ratios`, model-specific `parameters`, and `medias[].roles`.
3. Prepare references:
   - For local/OpenAI file objects, call `media_upload_and_confirm`; use `type: "image"` for start/end/reference images, `type: "video"` for video references, and `type: "audio"` for audio references.
   - Authorized HTTPS image URLs may be passed directly for image roles such as `start_image`, `end_image`, or `image`.
   - Non-image roles require UUIDs from upload/confirm or completed generation jobs.
   - Use roles from `models_get`; image-to-video usually uses `start_image` or `image`.
4. Estimate cost only when the user asks, credits seem important, or you need a read-only preflight: call `estimate_video_cost`.
5. Submit with `generate_video`. Put all generation arguments inside `params`; keep model-specific parameters as top-level fields inside `params`.
6. Poll with `job_status`. For non-terminal jobs, wait `poll_after_seconds`; typical video jobs take about 60-180 seconds.
7. Present the result URL or rendered resource. Mention any server `adjustments` when they materially changed duration, aspect ratio, or parameters.

## Model Defaults

- Prefer `seedance_2_0` for strong general video, image-to-video, identity consistency, product references, and multi-reference work when the catalog supports it.
- Prefer `kling3_0` when the brief emphasizes advanced motion transfer, multi-shot motion, or Kling specifically; if reference elements are involved, it needs an explicit `start_image`.
- Prefer Cinema Studio video models for premium cinematic output.

## Notes

- Use `estimate_video_cost` for credit preflight, then `generate_video` for submission.
- Upload local/OpenAI file objects first and pass the returned `media_id` to generation references.
- For `video` or `audio` reference roles, use uploaded media IDs or completed job UUIDs.
- Use `job_status` for polling and `show_generations` when the user asks to browse history.
- If an error includes `request_id`, include it in the user-facing failure summary.
