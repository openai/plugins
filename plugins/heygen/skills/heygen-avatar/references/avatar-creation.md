# Avatar Creation API Surface

This guide expands `heygen-avatar` Phase 2 (avatar creation) and Phase 3
(voice selection) with the full API surface, field mappings, and file
input formats. The SKILL.md gives the high-level workflow; this file is
the reference when you need exact arguments, edge cases, or alternative
creation paths.

For *avatar discovery* (finding an existing avatar at video time), see
[`heygen-video/references/avatar-discovery.md`](https://github.com/heygen-com/skills/blob/master/heygen-video/references/avatar-discovery.md).

---

## Avatar Creation: Three Types

`heygen-avatar` Phase 2 supports three creation types. Pick based on what
the user provides:

| User input | Type | API |
|---|---|---|
| A photo of a real person | `photo` | `create_photo_avatar` |
| A description of an appearance | `prompt` | `create_prompt_avatar` |
| A short video recording of a real person | `video` | `create_digital_twin` |

All three accept an optional `avatar_group_id`:
- **Omit it** to create a new character (new group).
- **Include it** to add a new look (variation) to an existing character.

Always use Mode 2 (with `avatar_group_id`) when the avatar already exists
and you're creating a variant (different outfit, orientation fix, bg
change). Only use Mode 1 (new character) for genuinely new identities.

### Photo avatar (from user's photo)

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

Photo requirements:
- JPEG or PNG
- Min 512x512
- Clear front-facing face
- Good lighting

### AI-generated avatar (from text prompt)

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

Prompt limit: 1000 characters (the API spec says 200 but the actual
enforced limit is 1000). Be descriptive — include style, features,
expression, lighting.

Optional: up to 3 `reference_images` to anchor the generated appearance.

### Video avatar / digital twin (from a short recording)

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

---

## File Input Formats

`file` accepts three forms:

```jsonc
// Public URL (no auth, no paywall)
{ "type": "url", "url": "https://example.com/headshot.jpg" }

// Pre-uploaded asset (from `heygen asset create --file <path>`)
{ "type": "asset_id", "asset_id": "<id>" }

// Inline base64
{ "type": "base64", "data": "<base64>", "content_type": "image/png" }
```

For when each is appropriate, see
[`references/asset-routing.md`](asset-routing.md).

---

## Response Shape

All three types return:
```jsonc
{
  "avatar_item": {
    "id": "<look_id>",         // ephemeral — the specific look
    "group_id": "<group_id>"   // stable — the character identity
  }
}
```

- `id` is the **look_id** — what you pass downstream as `avatar_id` to
  `create_video_agent` for video generation.
- `group_id` is the **character identity** — stable across looks. Save
  this in the AVATAR-<NAME>.md file. Always resolve fresh look_ids at
  video time via `list_avatar_looks(group_id=<id>)` rather than caching
  a specific look_id.

---

## Identity Field → HeyGen Enum Mapping

When building a prompt-based avatar, map identity attributes to these
HeyGen enums:

- **age**: Young Adult | Early Middle Age | Late Middle Age | Senior | Unspecified
- **gender**: Man | Woman | Unspecified
- **ethnicity**: White | Black | Asian American | East Asian | South East Asian | South Asian | Middle Eastern | Pacific | Hispanic | Unspecified
- **style**: Realistic | Pixar | Cinematic | Vintage | Noir | Cyberpunk | Unspecified
- **orientation**: square | horizontal | vertical
- **pose**: half_body | close_up | full_body

---

## Voice Selection (during avatar setup)

After the avatar look is created, pair it with a voice. Two paths:

### Path A — Voice Design (preferred)

Find matching voices via semantic search using the Voice section from
the AVATAR file. This searches HeyGen's full voice library. No new
voices are generated and no quota is consumed.

**Language matching:** The voice design prompt should specify the target
language from `user_language`. Example for Japanese: `"A calm, warm
female voice. Professional but approachable. Japanese speaker."` This
ensures semantic search returns voices in the correct language.

### Path B — Voice Browse (fallback)

For manual catalog browsing:

**MCP:** `list_voices(type=private)` then `list_voices(type=public, language=<lang>, gender=<gender>)`

**CLI:**
```bash
heygen voice list --type private --limit 20
heygen voice list --type public --engine starfish --language en --gender female --limit 20
```

**ALWAYS show a playable voice preview.** Each voice response includes
`preview_audio_url` — share it before committing.

**Handling missing/broken previews:** Some voices return bare `s3://`
paths or `null`. When this happens: note "(no preview available)" and
offer to generate a short TTS sample via `create_speech` (MCP) or
`heygen voice speech create --text "<sample>" --voice-id <id>
--input-type plain_text --language en --locale en-US` (CLI).
