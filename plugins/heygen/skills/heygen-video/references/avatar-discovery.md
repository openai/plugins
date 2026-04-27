# Avatar Discovery & Voice Selection

## Path A: Discover Existing Avatars

### A1: Check for private avatars first

**If user specifies an avatar by name** (e.g. "use Eve's Podcast look"), take the fast path:

**MCP:** `list_avatar_looks(ownership=private)` — filter client-side by name match.
**CLI:**
```bash
heygen avatar looks list --ownership private --limit 50
```
Avoids the 2-call group→looks pattern.

**If user wants to browse**, use the group-first flow:

**MCP:**
1. `list_avatar_groups(ownership=private)` — list groups (each group = one person)
2. `list_avatar_looks(group_id=<group_id>)` — show looks for chosen group

**CLI:**
```bash
heygen avatar list --ownership private --limit 50
heygen avatar looks list --group-id <group_id> --limit 50
```

Each look has an `id` — this is the `avatar_id` you pass downstream.

Avatar types: `studio_avatar`, `video_avatar`, `photo_avatar`. Photo avatars support `motion_prompt` and `expressiveness`.

**ALWAYS show the preview image** when presenting an avatar look. Each look response includes `preview_image_url` — display inline.

### A2: Check last-used avatar

Check `heygen-video-log.jsonl` for last used avatar_id. If found:

**MCP:** `get_avatar_look(look_id=<look_id>)`
**CLI:** `heygen avatar looks get --look-id <look_id>`

Show preview image: "Last time you used [Avatar Name]. Use her again?"

### A3: Avatar conversation

Ask: "Do you want a visible presenter, or voice-over only?"

If voice-over only → no `avatar_id`. State in prompt: "Voice-over narration only."

If presenter wanted, present private avatars first. For public/stock avatars, browse by group:

**MCP:** `list_avatar_groups(ownership=public)`
**CLI:**
```bash
heygen avatar list --ownership public --limit 20
```

Show group names + one representative image. Let the user pick a person.

**MCP:** `list_avatar_looks(group_id=<group_id>)`
**CLI:**
```bash
heygen avatar looks list --group-id <group_id> --limit 10
```

**Why group-first:** The flat `heygen avatar looks list --ownership public` call returns 50+ results for only 3 unique people per page. Group-level browsing (2 calls) gives much better discovery UX.

### A4: Voice direction

After avatar is settled, confirm voice preferences (accent, delivery style, language).

**ALWAYS show a playable voice preview.** Each voice response includes `preview_audio_url` — share it.

**Handling missing/broken previews:** Some voices return bare `s3://` paths or `null`. When this happens: note "(no preview available)" and offer to generate a short TTS sample via `create_speech` (MCP) or `heygen voice speech create --text "<sample>" --voice-id <id> --input-type plain_text --language en --locale en-US` (CLI).

---

## Path B: Create a New Avatar

Two modes:

**Mode 1 — New character** (omit `avatar_group_id`): Creates a new person with their own group.
**Mode 2 — New look** (include `avatar_group_id`): Adds a variation to an existing character.

Always use Mode 2 when the avatar already exists and you're creating a variant (different outfit, orientation fix, bg change). Only use Mode 1 for genuinely new characters.

Three creation types:

**Photo avatar (from user's photo):**

**MCP:** `create_photo_avatar(name=<name>, file=<file_object>, avatar_group_id=<optional>)`
**CLI:**
```bash
heygen avatar create -d '{
  "type": "photo",
  "name": "My Avatar",
  "file": {"type": "url", "url": "https://example.com/headshot.jpg"},
  "avatar_group_id": "<optional>"
}'
```
Photo requirements: JPEG or PNG, min 512x512, clear front-facing face, good lighting.

**AI-generated avatar (from text prompt):**

**MCP:** `create_prompt_avatar(name=<name>, prompt=<appearance>, avatar_group_id=<optional>)`
**CLI:**
```bash
heygen avatar create -d '{
  "type": "prompt",
  "name": "Tech Presenter",
  "prompt": "Young professional woman, modern workspace, confident smile",
  "avatar_group_id": "<optional>"
}'
```
Prompt max: 1000 characters. Optional: up to 3 `reference_images`.

**Video avatar (from user's video recording):**

**MCP:** `create_digital_twin(name=<name>, file=<file_object>, avatar_group_id=<optional>)`
**CLI:**
```bash
heygen avatar create -d '{
  "type": "video",
  "name": "My Video Avatar",
  "file": {"type": "asset_id", "asset_id": "<uploaded_asset_id>"},
  "avatar_group_id": "<optional>"
}'
```

All three return `avatar_item` with `id` (look_id) and `group_id` — use `id` as `avatar_id` for videos.

Files: `{"type": "url", "url": "..."}`, `{"type": "asset_id", "asset_id": "..."}` (from `heygen asset create --file <path>`), or `{"type": "base64", "data": "...", "content_type": "..."}`.

---

## Path C: Direct Image (Simplest for One-Off)

Skip avatar creation. Pass `image_url` directly:

**MCP:** `create_video_from_image(image_url=<url>, script=<script>, voice_id=<voice_id>, aspect_ratio="16:9")`
**CLI:**
```bash
heygen video create -d '{
  "image_url": "https://example.com/headshot.jpg",
  "script": "<script>",
  "voice_id": "<voice_id>",
  "aspect_ratio": "16:9"
}'
```
Also accepts `image_asset_id`. Fastest path for one-off talking-head video.

---

## Voice Selection

**MCP:** `list_voices(type=private)` then `list_voices(type=public, language=<lang>, gender=<gender>)`
**CLI:**
```bash
heygen voice list --type private --limit 20

# Public voices with filters
heygen voice list --type public --engine starfish --language en --gender female --limit 20
```

---

## How Avatar/Voice Are Passed

**MCP:** `create_video_agent(prompt=<prompt>, avatar_id=<look_id>, voice_id=<voice_id>, style_id=<optional>, orientation=<orientation>)`

**CLI:** `heygen video-agent create` with flags:
```bash
heygen video-agent create \
  --prompt "..." \
  --avatar-id "<look_id_from_discovery>" \
  --voice-id "<voice_id_from_discovery>" \
  --style-id "<optional_style_id>" \
  --orientation landscape
```

- **Custom/stock avatar with known ID** → pass `--avatar-id`. Do NOT describe avatar's appearance in prompt. Only delivery style + background/environment.
- **No avatar_id (auto-select)** → describe desired presenter in prompt. Less reliable (~80% vs ~97%).
- **Voice-over only** → omit `--avatar-id`, state in prompt.

> Always provide explicit `--avatar-id` for presenter videos. 97.6% duration accuracy vs ~80% without.
