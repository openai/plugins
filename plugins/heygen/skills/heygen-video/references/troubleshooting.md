# Known Issues & Troubleshooting

## Known Bug: Video Agent "Talking Photo Not Found"

**Error message:** "The Talking Photo for the current narrator could not be found."

**Root Cause:** Confirmed as a Video Agent backend bug by HeyGen engineering (Jerry Yan). Affects `video_avatar` type narrators and stock avatar auto-selection.

**Workaround:**
- Prefer explicit `avatar_id` over auto-selection
- If `video_avatar` fails, retry with a `studio_avatar` or `photo_avatar`

**Status:** Fix in progress at HeyGen.

---

## Weird Pauses / Unnatural Silence in Videos

**Symptom:** Video has awkward pauses or breaks between sentences. Narrator stops speaking but video continues with dead air before next line.

**Root Cause:** When Video Agent receives a script shorter than the target duration, it treats the script as verbatim speech and inserts silence/breaks to stretch it to the exact requested duration. It won't ad-lib or expand — it just pads with dead air.

**Fix:** Add this directive to EVERY prompt:
> "This script is a concept and theme to convey — not a verbatim transcript. You have full creative freedom to expand, elaborate, add examples, and fill the duration naturally. Do not pad with silence or pauses."

This tells Video Agent it can expand the script naturally instead of treating it as a fixed speech transcript. Per Jerry Yan: "If you tell it it's not a script to be strictly followed but concept or theme or give it green light to expand the script it will do well."

**Status:** Skill-side fix (prompt directive). HeyGen is also tuning the default behavior but the explicit directive is the reliable workaround.

---

## Duration Variance (Expected Behavior)

Video Agent controls final video timing internally. Duration accuracy ranges from 79-174% of target across testing. This is NOT a bug.

**Mitigation:** Variable padding multipliers (Script):
- ≤30s target: 1.6x padding
- 31-119s target: 1.4x padding
- ≥120s target: 1.3x padding

With explicit `avatar_id`: ~97% duration accuracy average.
Without `avatar_id`: ~80% accuracy average.

---

## Frame Check: Video Agent Not Applying Framing

If the Video Agent ignores the FRAMING NOTE or BACKGROUND NOTE and produces black bars, letterboxing, or mismatched framing:

1. **Ensure the note is appended at the END of the prompt**, after all other content (script, style block, etc.). Video Agent processes instructions sequentially and late-prompt directives have the strongest effect.
2. **Check that the correction note was actually appended.** Log the final prompt text and verify the FRAMING NOTE / BACKGROUND NOTE block is present.
3. **photo_avatar does NOT need BACKGROUND NOTE.** Video Agent generates avatar + environment together for photo_avatars. Only append framing notes for orientation mismatches. Background notes are for studio_avatars with transparent/empty backgrounds only.

---

## Stock Avatar Auto-Selection Unreliable

When no `avatar_id` is provided, Video Agent uses narrator tags (`{{@narrator_l0ug91}}`) that sometimes fail to resolve during render.

**Fix:** Always use explicit `avatar_id` from discovery. The only exception is Quick Shot mode where the user explicitly wants speed over reliability.

---

## HTML URLs in files[] Rejected

Video Agent rejects `text/html` content type in the `files[]` array. Web pages (blogs, docs sites, articles) must be handled via Path A (contextualize) only.

**What works in files[]:** Direct file URLs (PDFs, images, videos) — but prefer download→upload→asset_id since CDN/WAF often blocks HeyGen's servers.

---

## Avatar Not Ready for Video Generation

**Symptom:** Video generation fails or produces errors immediately after creating a new avatar. The avatar exists in the HeyGen dashboard but videos referencing it fail.

**Root Cause:** Avatar creation is asynchronous. `heygen avatar create` (and `create_photo_avatar` / `create_prompt_avatar` the app tools) return success immediately, but the avatar image is still being processed. If you submit a video request before processing completes, it fails.

**Detection:** Poll with `heygen avatar looks list --group-id <group_id>` (or check the avatar-looks view in the HeyGen app). The avatar is NOT ready until:
- `preview_image_url` is non-null
- `image_width` and `image_height` are non-zero

At the group level (`heygen avatar list`), an unready avatar will have no `preview_image_url` on the group object.

**Fix:** Poll every 10 seconds after creation, wait for preview URL to appear. Typical: 30-90s for photo avatars, 1-3 min for prompt avatars. Timeout at 5 min.

**The heygen-avatar skill handles this automatically.** If you bypass the skill, you must implement this polling yourself.

---

## Interactive Sessions Reliability

Interactive sessions (created without `--wait` and iterated via `heygen video-agent send`) have known issues:
- Sessions frequently stuck at `processing` status
- `reviewing` state may never be reached
- Follow-up messages fail with timing errors
- Stop command may not trigger video generation

**Recommendation:** Use one-shot mode for production. Interactive sessions documented for future use once HeyGen stabilizes the API.

---

## Error Code → Action

Stable CLI exit codes tell you what to do without parsing messages:

| Exit | Class | Action |
|------|-------|--------|
| `0` | ok | Continue |
| `1` | API / network | Retry with backoff. If persistent, check `--verbose` or contact HeyGen support. |
| `2` | usage | You passed a bad flag. Run `--help` on the command, fix the args, retry. |
| `3` | auth | Re-auth: `heygen auth login` or set `HEYGEN_API_KEY`. Verify with `heygen auth status`. |
| `4` | timeout under `--wait` | Operation still running server-side. stdout contains the partial resource (with `session_id` or `video_id`) — resume polling with `heygen video-agent get <id>` or `heygen video get <id>`. Do NOT re-submit. |

Common API-error hints (surfaced in stderr envelope `{error:{code,message,hint}}`):

- `402` / insufficient credits → tell the user their HeyGen plan is out of credits.
- `403` / forbidden → the resource is not owned by the caller (wrong `group_id`, private avatar).
- `404` / not found → ID is stale. Re-fetch via `heygen avatar list`, `heygen video-agent get`, etc.

---

## Polling Cadence

When `--wait` isn't an option (e.g., you want to return control to the user between polls), use a back-off schedule rather than a fixed interval:

| Age of job | Poll interval |
|------------|---------------|
| 0–2 min | every 10s |
| 2–5 min | every 30s |
| 5–10 min | every 60s |
| > 10 min | surface "taking longer than usual" once, keep polling at 60s, give up at 15 min |

If a job is stuck at the same status for >5 min, that's a signal to surface a status update or check the dashboard.

**Prefer `--wait`** on creation commands. It handles the polling internally and returns the final resource or exits `4` with a resumable `session_id` / `video_id` on timeout.

---

## Direct Video vs Video Agent — Which Endpoint?

Two ways to generate a video. Different pricing, different trade-offs.

| | **Direct Video** | **Video Agent** |
|---|-------------------|-----------------|
| Command / Tool | `heygen video create` / no app equivalent documented here | `heygen video-agent create` / app-based Video Agent flow |
| Input | Full script + avatar + voice + scene JSON | Prompt + optional avatar/voice/style |
| Control | You author every scene | Video Agent plans scenes, pacing, motion |
| Pricing | ~$0.0333/sec | ~$0.10/sec |
| When to use | Deterministic multi-scene videos, tight control, bulk generation | Creative intros, messages, "make a video about X" requests |

The default in this skill is **Video Agent** — it's what `heygen-video` is built around. Drop to Direct Video only for batch or highly scripted workflows where Agent's autonomy is overhead.
