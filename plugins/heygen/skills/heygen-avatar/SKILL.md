---
version: 3.1.0 # x-release-please-version
name: heygen-avatar
description: |
  Create a persistent HeyGen avatar — a reusable face + voice identity for the agent,
  the user, or any named character — powered by HeyGen Avatar V technology.
  Prompt-based creation by default (description → HeyGen builds it); photo upload is
  optional for real-person digital twins.
  Use when: (1) giving the agent a face + voice so it can present videos
  ("bring yourself to life", "create your avatar", "give yourself an avatar",
  "design a presenter", "set up an avatar", "let's make an avatar"),
  (2) the user wants to appear in videos as themselves ("create my avatar",
  "I want my face in a video", "digital twin of me", "build me an avatar"),
  (3) building a named character presenter ("create an avatar called Cleo",
  "design a character named X"), (4) establishing HeyGen identity before making videos —
  the correct FIRST step when no avatar exists yet.
  Chain signal: when the user says both an identity/avatar action AND a video action in the same
  request ("create an avatar AND make a video", "set up identity THEN create a video",
  "design a presenter AND immediately record"), run heygen-avatar first, then heygen-video.
  Returns avatar_id + voice_id — pass directly to heygen-video to create HeyGen videos.
  NOT for: generating videos (use heygen-video), translating videos, or TTS-only tasks.
argument-hint: "[name_or_description]"
allowed-tools: Bash, WebFetch, Read, Write, mcp__heygen__*
---

# HeyGen Avatar Designer

Create and manage HeyGen avatars for anyone: the agent, the user, or named characters. Handles identity extraction, avatar generation, voice selection, and saves everything to `AVATAR-<NAME>.md` for consistent reuse.

## Files & Paths

This skill reads and writes the following. No other files are accessed without explicit user instruction.

| Operation | Path | Purpose |
|-----------|------|---------|
| Read | `SOUL.md`, `IDENTITY.md` | Extract identity details when creating an avatar for the agent |
| Read | `AVATAR-<NAME>.md` | Load existing avatar identity (for variant looks, voice updates) |
| Write | `AVATAR-<NAME>.md` | Save new avatar identity after creation |
| Write | `AVATAR-AGENT.md`, `AVATAR-USER.md` (symlinks) | Role aliases, see Phase 5 |
| Temp write | `/tmp/openclaw/uploads/` | Voice preview audio (downloaded for user playback, deleted after session) |
| Remote upload | HeyGen (via `heygen asset create` or MCP) | User-provided photos uploaded to HeyGen for digital-twin creation |

Assets are only uploaded to HeyGen when the user explicitly provides them.

## Language Awareness

**Detect the user's language from their first message.** Store as `user_language` (e.g., `en`, `ja`, `es`, `ko`, `zh`, `fr`, `de`, `pt`).

1. **Communicate with the user in their language.** All questions, status updates, confirmations, and error messages should be in `user_language`.
2. **Voice design prompts and selection respect `user_language`.** When designing or selecting a voice, specify the target language so the voice library returns matches that speak it.
3. **Technical directives stay in English** — enum values (`Young Adult`, `Realistic`, `landscape`, etc.) are API-level and not translated.

## UX Rules

1. **Be concise.** No avatar IDs, group IDs, or raw API payloads in chat. Report the result (avatar created, ready to use) not the plumbing.
2. **No internal jargon.** Never mention internal phase names ("Phase 0", "Phase 5 Symlink Maintenance") to the user. The user sees natural conversation: "Setting up your avatar\u2026" not "Running Phase 2 avatar creation."
3. **One or two questions per phase.** Don't batch-ask. Walk phases in order, ask the smallest set of questions needed to proceed.
4. **Read workspace files before asking.** `SOUL.md`, `IDENTITY.md`, `AVATAR-*.md` at the workspace root contain identity. Check them first. Only ask the user for what's genuinely missing.
5. **Don't narrate skill internals.** Never say "let me read the workflow," "checking the reference files," "loading the avatar discovery guide." Read silently. The user sees questions and results, not internal navigation.
6. **Don't announce what you're about to do.** Skip meta-commentary like "Creating the avatar now." Just do the work. If a step takes time, the next thing the user hears should be the result (or a checkpoint question).
7. **Never narrate transport choice.** MCP vs CLI is internal. Pick the transport silently and never mention it. If both are unavailable, ask the user to configure one without explaining why.

## Start Here (Critical)

**Default target = the agent.** The primary use of this skill is giving the agent a face + voice so it can present videos. Route to "user" only on explicit "my avatar" / "me" / "my photo" language. When in doubt, make the agent's avatar.

**Do NOT batch-ask questions.** No "give me a photo, voice preference, duration, target platform, tone, key message" all at once. Walk phases in order. Each phase asks at most one or two things at a time.

**For agent avatars: read SOUL.md and IDENTITY.md first, then go straight to prompt-based creation.** Do NOT ask the user for a photo or appearance details first. The agent's identity lives in those workspace files. Only ask the user for traits that are genuinely missing.

**Prompt-based is the default creation path.** Photo is opt-in, only relevant when the user explicitly wants a real-person digital twin of themselves. Agents and named characters almost always use prompt-based creation.

## Before You Start (environment detection)

Try to read `SOUL.md` from the workspace root.

- **Found** → OpenClaw environment. Skip this entire section and go straight to Phase 0. Workspace-native identity (SOUL.md, IDENTITY.md) will drive agent onboarding.
- **Not found** → Claude Code environment, no workspace identity files. Still go to Phase 0 next — do NOT skip ahead to listing user avatars or asking the user for a photo.

**⚠️ AVATAR file caveat:** Ignore any AVATAR-*.md files found in the workspace that belong to a *different* person or agent (e.g., AVATAR-Eve.md when creating an avatar for Claude). Only use an AVATAR file if its name matches the subject you're creating for right now.

**⚠️ Do NOT fetch HeyGen avatars yet.** That's a Phase 0 sub-step (only after target detection). Fetching before Phase 0 causes the agent to frame the conversation around "your existing avatars" when the default should be creating one for the agent itself.

## API Mode Detection

**Mode selection is silent.** Detect once at the start of the session, pick a mode, move on. Never narrate transport choice ("CLI is broken", "switching to MCP") — the user doesn't care how calls are made.

**MCP (preferred):** If HeyGen MCP tools are available (tools matching `mcp__heygen__*`), use them. MCP authenticates via OAuth — no API key needed — and runs against the user's existing HeyGen plan credits.

**CLI fallback:** If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. Auth: `HEYGEN_API_KEY` env OR `heygen auth login` (persists to `~/.heygen/credentials`). If the CLI is missing, errors on `--version`, or auth is not set, silently skip it — do not retry MCP.

**Neither available:** Only if MCP is unavailable AND the CLI doesn't work, tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."

**API:** v3 only. Never call v1 or v2 endpoints.

**Docs-first rule:** Before calling any endpoint you're unsure about:
- **Index:** `GET https://developers.heygen.com/llms.txt` — full sitemap
- **Any page:** Append `.md` to the URL for clean markdown
- Or run `heygen <noun> <verb> --help`
- Read the spec, THEN build your request. Never guess field names.

## Avatar File Convention

Every avatar gets one file: `AVATAR-<NAME>.md` at the workspace root.

```
AVATAR-EVE.md      ← agent      (named, canonical)
AVATAR-KEN.md      ← user       (named, canonical)
AVATAR-CLEO.md     ← character  (named, canonical)
```

The skill also maintains two **role-based symlinks** alongside the named
files, for generic lookups by consumer skills (e.g., heygen-video) when the
request doesn't carry a specific name ("make a video of yourself" → read
the agent alias; "make a video of me" → read the user alias):

```
AVATAR-AGENT.md → AVATAR-<CURRENT-AGENT-NAME>.md   (symlink)
AVATAR-USER.md  → AVATAR-<CURRENT-USER-NAME>.md    (symlink)
```

Named files are the single source of truth; aliases are pointers and never
drift. Phase 5 of the workflow maintains them. Named characters get NO
role alias — they are referenced by name only.

Format:
```markdown
# Avatar: <Name>

## Appearance
- Age: <natural language>
- Gender: <natural language>
- Ethnicity: <natural language>
- Hair: <natural language>
- Build: <natural language>
- Features: <natural language>
- Style: <natural language>
- Reference: <optional workspace-relative path or URL>

## Voice
- Tone: <natural language>
- Accent: <natural language>
- Energy: <natural language>
- Think: <one-line analogy>

## HeyGen
- Group ID: <character identity anchor — THE stable reference, never changes>
- Voice ID: <matched or designed voice>
- Voice Name: <human-readable>
- Voice Designed: <true if custom-designed, false if picked from catalog>
- Voice Seed: <seed value used, if designed>
- Looks: landscape=<look_id>, portrait=<look_id>, square=<look_id>
- Last Synced: <ISO timestamp>

⚠️ look_ids are ephemeral — always resolve fresh from group_id at runtime via `heygen avatar looks list --group-id <id>` (or MCP `list_avatar_looks`). Never hardcode look_id as the primary avatar reference.
```

**Top sections** (Appearance, Voice) are portable natural language. Any platform can use them.
**HeyGen section** is runtime config with API IDs. Skills read this to make API calls.

## Skill Announcement

Start every invocation with:

> 🎭 **Using: heygen-avatar** — creating an avatar for [name]

## Workflow

**DO NOT batch-ask questions upfront.** Walk phases in order. Each phase asks at most one thing at a time, and only if needed.

### Phase 0 — Who Are We Creating?

See the Start Here block above for the default-to-agent rule. Only route to "user" or "named character" when the phrasing is unambiguous.

Routing signals (in priority order):

1. **User** (explicit only) — "create **my** avatar", "make **me** an avatar", "I want my face in a video", "a digital twin of **me**", "based on **my** photo". Requires a possessive pronoun referring to the user OR explicit mention of their photo. Ask for their name if not obvious.
2. **Named character** (explicit only) — "create an avatar called Cleo", "design a character named X", "build a presenter named Y" → use the given name.
3. **Agent** (default) — everything else: "create your avatar", "bring yourself to life", "set up an avatar", "let's make an avatar", "create an avatar", "design a presenter", "I want you to appear in videos", or any ambiguous phrasing. Read `IDENTITY.md` for name.

**When unsure, default to agent.** Do NOT ask the user for their name, appearance, or voice on an ambiguous request — that's the wrong first move. If after reading IDENTITY.md + SOUL.md the intent still feels ambiguous, ask one short clarifying question to disambiguate (phrase it naturally — something like "quick check: this avatar is for you, or for me?").

Then check `AVATAR-<NAME>.md` at the workspace root:

- **AVATAR file exists + HeyGen section filled in** → "You already have an avatar set up. Want to add a new look, update it, or start fresh?" Wait for answer.
- **AVATAR file exists but HeyGen section empty** → skip to Phase 2.
- **No AVATAR file** → proceed to Phase 1.

**Role alias staleness check.** Before proceeding, also check whether the
role alias for this target is already pointing at the right named file:

- For **agent target**: read `AVATAR-AGENT.md` (follow symlink) and
  compare to `AVATAR-<CURRENT-AGENT-NAME>.md`. If they differ (e.g.,
  `AVATAR-AGENT.md` → `AVATAR-OLD-NAME.md` because the agent identity
  changed since the last run), re-link in Phase 5 even if no other
  changes are made. The named file is canonical, but the alias must
  match the *current* identity, not the historical one.
- For **user target**: same check on `AVATAR-USER.md`.
- For **named character**: no alias to check.

**Optional existing-avatar check** (only useful on the user path when the user might already have avatars in their HeyGen account). If Phase 0 target = **user** AND no `AVATAR-<USER>.md` exists, list their HeyGen avatars first:

**MCP:** `list_avatar_groups(ownership=private)`
**CLI:** `heygen avatar list --ownership private`

If the list is non-empty, present the options and ask which to use or whether to create new. If empty, proceed to Phase 1. Skip this check entirely for agent and named-character targets — those live in AVATAR-*.md, not the HeyGen catalog.

### Phase 1 — Identity Extraction

**Order matters. Files first, questions second. Prompt-based creation is the default path — photo is an opt-in upgrade.**

**For the agent** (Phase 0 target = agent):
1. Read `SOUL.md`, `IDENTITY.md`, and any existing `AVATAR-<NAME>.md` from the workspace root.
2. If SOUL.md or IDENTITY.md is found → extract appearance and voice traits silently. Do NOT ask the user "describe your appearance" — the agent IS the subject, and its identity lives in those files. **If the files describe only personality / values with no physical description, do NOT hallucinate traits.** Ask the user conversationally for the missing appearance traits only (one or two at a time).
3. If neither file is found (e.g., Claude Code environment with no workspace identity) → ask the user to describe the agent's appearance and voice conversationally.
4. Proceed directly to **Type A (prompt) creation** in Phase 2 by default. Do NOT ask for a photo unless the user volunteers one or explicitly asks for photo realism — agents almost always use prompt-based creation.

**For users/named characters** (Phase 0 target = user or named):
- Conversational onboarding. Ask naturally about appearance and voice — one or two questions at a time, not a form. Communicate in `user_language`.
- **User path only:** after the onboarding Q&A, run the Reference Photo Nudge below.
- **Named character path:** skip the nudge, go straight to Type A (prompt) creation.

Write `AVATAR-<NAME>.md` with the Appearance and Voice sections filled in. Leave the HeyGen section empty until Phase 2 succeeds.

### Reference Photo Nudge (user path only)

Only run this step when Phase 0 target = **user** (real-person digital twin) OR when the user explicitly asks for photo realism.

- Check AVATAR file's Appearance → Reference field first. If a photo is already on file, skip asking and use it.
- Otherwise, ask one sentence: *"Got a headshot? It gives better face consistency for videos of you. I can also generate from your description — just say 'skip.'"*

Branch:
- **Photo provided** → upload via MCP `upload_asset` or `heygen asset create --file <path>`, then Type B (photo) creation in Phase 2.
- **Skip** → Type A (prompt) creation in Phase 2.

For agents and named characters, skip this entire step — go straight to Type A (prompt) creation.


### Phase 2 — Avatar Creation

📖 **Full creation API surface (photo / prompt / digital twin), file input formats, identity field → enum mapping, response shape → [references/avatar-creation.md](references/avatar-creation.md)**

Two modes:

**Mode 1 — New character** (omit `avatar_group_id`):
Creates a brand new character with its own group.

**Mode 2 — New look** (include `avatar_group_id`):
Adds a variation to an existing character. Read the Group ID from the AVATAR file.

Two creation types:

**Type A — From prompt (AI-generated appearance):**

**MCP:** `create_prompt_avatar(name=<name>, prompt=<appearance>, avatar_group_id=<optional>)`
**CLI:** `heygen avatar create -d '{"type":"prompt","name":"...","prompt":"...","avatar_group_id":"..."}'` (accepts inline JSON, a file path, or `-` for stdin)

Prompt limit is 1000 characters. Be descriptive — include style, features, expression, lighting. The API spec says 200 but the actual enforced limit is 1000.

**Type B — From reference image:**

**MCP:** `create_photo_avatar(name=<name>, file=<file_object>, avatar_group_id=<optional>)`
**CLI:** `heygen avatar create -d '{"type":"photo","name":"...","file":{"type":"url","url":"..."},"avatar_group_id":"..."}'`

File options for Type B:
- `{ "type": "url", "url": "https://..." }` — public image URL
- `{ "type": "asset_id", "asset_id": "<id>" }` — from `heygen asset create --file <path>`
- `{ "type": "base64", "media_type": "image/png", "data": "<base64>" }` — inline

📖 **When to use each (URL vs asset_id vs base64), upload routing, and edge cases → [references/asset-routing.md](references/asset-routing.md)**

**Response:** Returns `avatar_item.id` (look ID) and `avatar_item.group_id` (character identity).

Map identity fields to HeyGen enums for the prompt:
- **age**: Young Adult | Early Middle Age | Late Middle Age | Senior | Unspecified
- **gender**: Man | Woman | Unspecified
- **ethnicity**: White | Black | Asian American | East Asian | South East Asian | South Asian | Middle Eastern | Pacific | Hispanic | Unspecified
- **style**: Realistic | Pixar | Cinematic | Vintage | Noir | Cyberpunk | Unspecified
- **orientation**: square | horizontal | vertical
- **pose**: half_body | close_up | full_body

Show the prompt to the user before creating:
> **Appearance:** "[prompt]"
> **Settings:** Young Adult | Woman | East Asian | Realistic
> Look good? (yes / adjust / completely different)

⛔ **STOP. Wait for the user to approve or adjust. Do NOT call the avatar creation API until the user confirms.**

### Phase 3 — Voice

Two paths: **Design** (describe what you want, get matched voices) or **Browse** (filter the catalog manually).

Ask whether they want voice design (describe what they want) or catalog browsing. Communicate in `user_language`.

Default to **Design** if the AVATAR file has a Voice section with personality traits.

#### Path A — Voice Design (preferred)

Find matching voices via semantic search using the Voice section from the AVATAR file. This searches HeyGen's full voice library. No new voices are generated and no quota is consumed.

**Language matching:** The voice design prompt should specify the target language from `user_language`. Example for Japanese: `"A calm, warm female voice. Professional but approachable. Japanese speaker."` This ensures semantic search returns voices in the correct language.

**MCP:** `design_voice(prompt=<voice description>, seed=0)`
**CLI:** `heygen voice create --prompt "..." --seed 0` (also accepts `--gender`, `--locale`)

Returns 3 voice options per seed. Present all 3 with inline audio previews:
- Download each `preview_audio_url` to a temp path (any standard download method works — no HeyGen auth needed, these are public S3 URLs)
- Send as audio attachment: `message(action:send, media:"<path>", caption:"Option <n>: <voice_name> — <gender>, <language>")` so it plays inline in Telegram/Discord
- After all previews sent, present selection buttons

⛔ **STOP. Wait for the user to pick a voice via buttons or text. Do NOT select a voice yourself or proceed to Phase 4 until the user explicitly chooses.**

If none match:
> "None of these hitting right? I can try a different set (same description, different variations) or you can tweak the description."

Increment `seed` and call again. Different seeds give completely different voice options from the same prompt.

- Clean up /tmp files after user picks

#### Path B — Voice Browse (fallback)

Browse HeyGen's existing voice library:

**MCP:** `list_voices(type=private)` then `list_voices(type=public, language=<lang>, gender=<gender>)`
**CLI:** `heygen voice list --type private` / `heygen voice list --type public --language <lang> --gender <gender>`

1. Read the Voice section from the AVATAR file
2. Filter by gender and language
3. Pick top 3 candidates based on personality match
4. Present with inline audio previews (same download + send pattern as Path A)
5. ⛔ **STOP. Wait for the user to pick. Do NOT auto-select.**

### Phase 4 — Save to AVATAR File

Update the HeyGen section of `AVATAR-<NAME>.md` to match the canonical format:

```markdown
## HeyGen
- Group ID: <avatar_item.group_id — THE stable reference, never changes>
- Voice ID: <chosen voice_id>
- Voice Name: <voice name>
- Voice Designed: <true if custom-designed, false if picked from catalog>
- Voice Seed: <seed value used, if designed>
- Looks: <orientation>=<avatar_item.id> (e.g., landscape=<look_id>, portrait=<look_id>)
- Last Synced: <ISO timestamp>

⚠️ look_ids are ephemeral — always resolve fresh from group_id at runtime via `heygen avatar looks list --group-id <id>` (or MCP `list_avatar_looks`). Never hardcode look_id as the primary avatar reference.
```

Confirm the avatar is saved and that other skills (like heygen-video) will pick it up automatically. Communicate in `user_language`.

### Phase 5 — Maintain Role Alias

After writing the named `AVATAR-<NAME>.md`, create or update a role-based
symlink alongside it so other skills can do generic lookups without
resolving the agent / user name first.

Based on the Phase 0 target:

- **Agent target** → symlink `AVATAR-AGENT.md` → `AVATAR-<NAME>.md`
- **User target** → symlink `AVATAR-USER.md` → `AVATAR-<NAME>.md`
- **Named character** → no role alias. Named characters are referenced by
  name only (e.g., `AVATAR-CLEO.md`); they are not the agent or the user.

**Implementation (run from the workspace root, with fs-fallback):**

The `cd` to workspace root is mandatory — bare relative paths in `ln -s`
resolve from the agent's current working directory, not where SOUL.md
lives. The `|| echo` clause handles filesystems that reject symlinks
(Windows without dev mode, some cloud-mounted storage) without aborting
Phase 5.

```bash
# Agent
cd "$WORKSPACE_ROOT" && ln -sf AVATAR-<NAME>.md AVATAR-AGENT.md \
  || echo "role alias skipped: fs doesn't support symlinks"

# User
cd "$WORKSPACE_ROOT" && ln -sf AVATAR-<NAME>.md AVATAR-USER.md \
  || echo "role alias skipped: fs doesn't support symlinks"
```

Use a relative link target (just the filename, no path prefix) so the
alias survives if the workspace is moved or copied.

`ln -sf` is unlink-then-symlink under the hood, not strictly atomic.
Fine for single-user workspaces; if concurrent agents ever write the
same alias, expect interleaving and add explicit locking then.

**Why symlink, not copy:** removes the duplicate-file drift class
(content can never diverge between named file and alias). It does NOT
remove staleness drift — if `IDENTITY.md` changes the agent name without
re-running heygen-avatar, `AVATAR-AGENT.md` keeps pointing at the *old*
named file. Phase 0 mismatch-and-re-alias handles this on the next
invocation; until then, the alias is stale-but-pointing-somewhere-valid,
not broken.

**Multi-agent workspace caveat:** one role alias per workspace is
last-writer-wins. If two agents ever share a workspace and both run
heygen-avatar, only the most recent run's identity is reachable via
`AVATAR-AGENT.md`. Named files for both still exist. We accept this
limit — multi-agent shared workspaces are out of scope for v1.

### Phase 6 — Test (Optional)

If the user wants to see their avatar in action:

**MCP:** `create_video_agent(avatar_id=<avatar_id>, voice_id=<voice_id>, prompt=<greeting>)`
**CLI:** `heygen video-agent create --avatar-id <id> --voice-id <id> --prompt "..." --wait`

Generate a natural greeting in the video language (from `user_language`). Examples: English "Hi, I'm [name]. Nice to meet you!", Japanese "[name]です。はじめまして！", Spanish "Hola, soy [name]. ¡Mucho gusto!", Korean "안녕하세요, [name]입니다. 만나서 반갑습니다!"

## Iteration Flow

When the user wants to refine:

- **"Adjust the prompt"** → Mode 2 with existing group_id (keeps the character, adds a new look). Only Mode 1 if they say "start completely over."
- **"Add a new look"** / **"different outfit"** → Mode 2 with existing group_id. Add to Looks in AVATAR file.
- **"Try a different voice"** → back to Phase 3
- **"Start completely over"** → Mode 1, new character. Overwrite HeyGen section.

**Default to Mode 2 (new look under same group).** Only create a new group when the user explicitly wants a different character identity. This keeps the account clean and makes looks reusable across skills.

Each iteration updates the AVATAR file. The file is always the source of truth.

## UX Rules

**Be interactive at checkpoints, silent everywhere else.** Stop and wait at avatar approval and voice selection. Between checkpoints, work silently — don't narrate reasoning or explain next steps. After voice pick: save + confirm in one message.

## Video Producer Integration

`heygen-video` reads AVATAR files for group_id and voice_id. Resolution
order:

1. **Named request** ("Make a video with Eve") → read `AVATAR-EVE.md`.
2. **Agent self-reference** ("make a video of yourself", "give us a video
update") → read `AVATAR-AGENT.md` (symlink to current agent's named file).
3. **User self-reference** ("make a video of me", "my video update") → read
`AVATAR-USER.md` (symlink to current user's named file).
4. **No AVATAR file or symlink** → fall back to stock avatars or ask user.

The alias targets are resolved by the OS at read time, so consumer skills
simply `cat AVATAR-AGENT.md` and get whatever the current agent's avatar is.

## Error Handling

- Missing SOUL.md/IDENTITY.md → conversational onboarding, write AVATAR file from answers
- API fails → retry once, then ask user to check API key
- Voice match poor → show all available voices, let user browse
- Asset upload fails → skip reference image, try prompt-only creation
- Existing avatar file with stale HeyGen IDs → offer to regenerate or keep

📖 **Known issues, retry patterns, broken voice previews, error → action mapping → [references/troubleshooting.md](references/troubleshooting.md)**
