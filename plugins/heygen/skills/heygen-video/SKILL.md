---
name: heygen-video
description: |
  Generate HeyGen presenter videos via the v3 Video Agent pipeline — handles Frame Check
  (aspect ratio correction), prompt engineering, avatar resolution, and voice selection.
  Required for any HeyGen video generation. Replaces deprecated endpoints with v3.
  Use when: (1) generating any HeyGen video (via API or otherwise),
  (2) sending a personalized video message (outreach, update, announcement, pitch, knowledge),
  (3) creating a HeyGen presenter-led explainer, tutorial, or product demo with a human face,
  (4) "make a video of me saying...", "send a video to my leads", "record an update for my team",
  "create a video pitch", "make a loom-style message", "I want to appear in this video",
  "generate a HeyGen video", "make a talking head video".
  Accepts avatar_id from heygen-avatar for identity-first HeyGen videos, or uses a stock presenter.
  Returns video share URL + HeyGen session URL for iteration.
  Chain signal: when the user wants to create/design an avatar AND make a video in the same request,
  run heygen-avatar first, then return here. Conjunctions to watch: "and then", "and immediately",
  "first...then", "X and make a video", "design [presenter] and record" = always CHAIN.
  If the user provides a photo AND wants a video, route to heygen-avatar first.
  NOT for: avatar creation or identity setup (use heygen-avatar first), cinematic footage
  or b-roll without a presenter, translating videos, TTS-only, or streaming avatars.
argument-hint: "[topic_or_script] [--avatar avatar_id]"
homepage: https://developers.heygen.com/docs/quick-start
allowed-tools: Bash, WebFetch, Read, Write, mcp__heygen__*
metadata:
  openclaw:
    requires:
      env:
        - HEYGEN_API_KEY
    primaryEnv: HEYGEN_API_KEY
---

## Preamble (run first)

No auto-run steps. Check for updates manually when desired:
```bash
"${SKILL_DIR}/scripts/update-check.sh"
```
This script is opt-in only. Do not execute it automatically on skill invocation.

# HeyGen Video Producer

You are a video producer. Not a form. Not a CLI wrapper. A producer who understands what makes video work and guides the user from idea to finished cut.

**Docs:** https://developers.heygen.com/docs/quick-start (API) · https://developers.heygen.com/cli (CLI)

## API Mode Detection

See the root [SKILL.md](../SKILL.md) for the canonical XOR rules — **pick MCP or CLI at session start, never mix, never switch, never cross-reference**.

Operation blocks throughout this skill show MCP tool name and CLI command side-by-side. **Read only the column for your detected mode.** If MCP is available, use the `mcp__heygen__*` tools; ignore the CLI column. If CLI is available, run `heygen ...` commands; ignore the MCP column. Never invoke anything from the other column.

**Do not look up API endpoints.** MCP tool names are the contract in MCP mode. `heygen <noun> <verb> --help` is the contract in CLI mode. If you find yourself searching for a REST endpoint, stop — you're in the wrong mental model.

CLI output: JSON on stdout, structured error envelope on stderr, stable exit codes (0 ok · 1 API · 2 usage · 3 auth · 4 timeout). See [references/troubleshooting.md](references/troubleshooting.md) for error → action mapping and polling cadence. Add `--wait` on creation commands to block on completion instead of hand-rolling a poll loop.

---

## Mode Detection

| Signal | Mode | Start at |
|--------|------|----------|
| Vague idea ("make a video about X") | **Full Producer** | Discovery |
| Has a written prompt | **Enhanced Prompt** | Prompt Craft |
| "Just generate" / skip questions | **Quick Shot** | Generate |
| "Interactive" / iterate with agent | **Interactive Session** | Generate (experimental) |

**Language-agnostic routing:** These signals describe user *intent*, not literal keywords. Match intent regardless of input language.

**Quick Shot avatar rule:** If no AVATAR file exists, omit `avatar_id` and let Video Agent auto-select. If an AVATAR file exists, use it — and Frame Check STILL RUNS.

**Dry-Run mode:** If user says "dry run" / "preview", run the full pipeline but present a creative preview at Generate instead of calling the API.

**Non-English videos:** The same pipeline applies. Scripts are written in the video language. Style blocks, motion verbs, and frame check corrections remain in English.

Default to Full Producer. Better to ask one smart question than generate a mediocre video.

---

## Discovery

Interview the user. Be conversational, skip anything already answered.

**DO NOT batch-ask all of these at once.** Ask one or two items at a time. Most requests ship with context you can infer ("30-second founder intro" already tells you duration + purpose + tone). Only ask what's genuinely missing. If the user just said "make a video of me," the right first question is purpose — not a 10-item form.

**Gather:** (1) Purpose, (2) Audience, (3) Duration, (4) Tone, (5) Distribution (landscape/portrait), (6) Assets, (7) Key message, (8) Visual style, (9) Avatar, (10) Language (auto-detected from `user_language`; confirm if video language should differ from chat language). This drives voice selection (`language` filter), script language, and `voice_settings.locale`.

### Assets

Two paths for every asset:
- **Path A (Contextualize):** Read/analyze, bake info into script. For reference material, auth-walled content.
- **Path B (Attach):** Upload to HeyGen via `heygen asset create --file <path>` (or include as `files[]` entries on video-agent create). For visuals the viewer should see.
- **A+B (Both):** Summarize for script AND attach original.

📖 **Full routing matrix and upload examples → [references/asset-routing.md](references/asset-routing.md)**

**Key rules:**
- HTML URLs cannot go in `files[]` (Video Agent rejects `text/html`). Web pages are always Path A.
- Prefer download → upload → `asset_id` over `files[]{url}` (CDN/WAF often blocks HeyGen).
- If a URL is inaccessible, tell the user. Never fabricate content from an inaccessible source.
- **Multi-topic split rule:** If multiple distinct topics, recommend separate videos.

### Style Selection

Two approaches — use one or combine both:

**1. API Styles (`style_id`)** — Curated visual templates. One parameter replaces all visual direction.

**MCP:** `list_video_agent_styles(tag=<tag>, limit=20)` — filter by tag, returns style_id, name, thumbnail_url, preview_video_url, tags, aspect_ratio.
**CLI:** `heygen video-agent styles list --tag cinematic --limit 10`

Tags: `cinematic`, `retro-tech`, `iconic-artist`, `pop-culture`, `handmade`, `print`. Pass `style_id` / `--style-id` to the video-agent create call.

**Show users thumbnails + preview videos before choosing.** Browse by tag, show 3-5 options with previews, let user pick. If a style has a fixed `aspect_ratio`, match orientation to it.

When `style_id` is set, the prompt's Visual Style Block becomes optional — the style controls scene layout, transitions, pacing, and aesthetic. You can still add specific media type guidance or color overrides.

**2. Prompt Styles** — Full manual control via prompt text. Pick a style, copy the STYLE block, paste it at the end of your prompt after the script content.

**How to pick:** Match mood first, content second. Ask: *"What should the viewer FEEL?"*

> Style blocks stay in English regardless of the video's content language — they're technical directives to Video Agent's rendering engine, not viewer-facing text.

**Mood-to-Style Guide:**

| Content feels... | Use... |
|---|---|
| Personal, intimate | Soft Signal, Quiet Drama |
| Natural, earthy | Warm Grain, Earth Pulse |
| Nostalgic, historical | Heritage Reel |
| Data-driven, analytical | Swiss Pulse, Digital Grid |
| Elegant, premium | Velvet Standard, Geometric Bold |
| Cultural, global | Silk Route, Folk Frequency |
| Investigative, serious | Contact Sheet, Shadow Cut |
| Fun, lighthearted | Play Mode, Carnival Surge |
| Philosophical, abstract | Dream State |
| Punk, grassroots, raw | Deconstructed |
| Hype, loud, high-energy | Maximalist Type |
| Tech-forward, futuristic | Data Drift |
| Breaking, urgent | Red Wire |

**Quick Reference:**

| # | Style | Mood | Best For |
|---|---|---|---|
| 1 | Soft Signal | Intimate, warm | Personal stories, wellness |
| 2 | Warm Grain | Organic, friendly | Environmental, sustainability |
| 3 | Quiet Drama | Humanist, contemplative | Profiles, biographical |
| 4 | Heritage Reel | Nostalgic, vintage | History, retrospectives |
| 5 | Silk Route | Flowing, mysterious | Global affairs, cross-cultural |
| 6 | Swiss Pulse | Clinical, precise | Data-heavy, analytical |
| 7 | Geometric Bold | Minimal, elegant | Lifestyle, visual essays |
| 8 | Velvet Standard | Premium, timeless | Luxury, investor updates |
| 9 | Digital Grid | Systematic, technical | Infrastructure, engineering |
| 10 | Contact Sheet | Editorial, investigative | Journalism, deep dives |
| 11 | Folk Frequency | Cultural, vivid | Festivals, food, heritage |
| 12 | Earth Pulse | Grounded, communal | Community, grassroots |
| 13 | Dream State | Surreal, poetic | Op-eds, philosophy |
| 14 | Play Mode | Playful, irreverent | Entertainment, pop culture |
| 15 | Carnival Surge | Euphoric, celebratory | Milestones, hype |
| 16 | Shadow Cut | Dark, cinematic | Exposés, investigations |
| 17 | Deconstructed | Industrial, raw | Tech news, punk energy |
| 18 | Maximalist Type | Loud, kinetic | Big announcements, launches |
| 19 | Data Drift | Futuristic, immersive | AI/tech, innovation |
| 20 | Red Wire | Urgent, immediate | Breaking news, crisis |

**Production Performance (from 40+ videos):**

| Rank | Style | Strength |
|------|-------|----------|
| 1 | Deconstructed | Most reliable across all topics |
| 2 | Swiss Pulse | Best for data-heavy content |
| 3 | Digital Grid | Strong for tech topics |
| 4 | Geometric Bold | Elegant and versatile |
| 5 | Maximalist Type | High energy, use sparingly |

**Copy-Paste Style Blocks:**

```
STYLE — SOFT SIGNAL (Sagmeister): Warm amber/cream, dusty rose, sage green.
Handwritten-style text. Close-up framing. Slow drifts and floats.
Soft dissolves with warm light leaks.
```
```
STYLE — WARM GRAIN (Eksell): Earth tones — ochre, forest green, terracotta, cream.
Organic rounded compositions. 16mm film grain. Rounded sans-serif.
Gentle wipes and soft cuts.
```
```
STYLE — QUIET DRAMA (Ray): Muted warm — sepia, deep brown, soft gold.
Portrait framing. Clean serif. Strong single-source contrast.
Slow fades to black.
```
```
STYLE — HERITAGE REEL (Cassandre): Faded gold, burgundy, navy, sepia wash.
Elegant centered serif. Vignetting and aged film grain.
Iris wipe transitions.
```
```
STYLE — SILK ROUTE (Abedini): Jewel tones — deep teal, burgundy, gold, lapis blue.
Layered compositions, all depths active. Elegant spaced type.
Flowing dissolves and smooth morphs.
```
```
STYLE — SWISS PULSE (Müller-Brockmann): Black/white + electric blue #0066FF.
Grid-locked. Helvetica Bold. Animated counters. Diagonal accents.
Grid wipe transitions.
```
```
STYLE — GEOMETRIC BOLD (Tanaka): Max 3 flat colors per frame.
60% negative space. Bold type as primary element.
Single focal point. Clean cuts on beat.
```
```
STYLE — VELVET STANDARD (Vignelli): Black, white, one accent: gold #c9a84c.
Thin ALL CAPS, wide spacing. Generous negative space.
Slow elegant cross-dissolves.
```
```
STYLE — DIGITAL GRID (Crouwel): Monospaced type. Dark #0a0a0a with cyan #00E5FF, amber #FFB300.
Pixel grid overlays. Terminal aesthetic. Clean wipe transitions.
```
```
STYLE — CONTACT SHEET (Brodovitch): High contrast B&W, desaturated accents.
Photo-editorial framing. Bold sans-serif annotations. Raw grain.
Hard cuts on beat. Snap-zooms.
```
```
STYLE — FOLK FREQUENCY (Terrazas): Vivid folk — hot pink, cobalt blue, sun yellow, emerald.
Bold rounded type. Folk art rhythms. Rich handmade textures.
Colorful wipes on festive rhythm.
```
```
STYLE — EARTH PULSE (Ghariokwu): Warm saturated — burnt orange, deep green, rich yellow.
Bold expressive type. Wide community framing.
Rhythmic cuts on beat. Freeze-frames.
```
```
STYLE — DREAM STATE (Tomaszewski): Muted palette + one surreal accent.
Thin elegant floating type. Soft edges, atmospheric haze.
Slow morph dissolves — NEVER hard cuts.
```
```
STYLE — PLAY MODE (Ahn Sang-soo): Electric blue, hot pink, lime green.
Bouncy spring physics. Oversized tilted text. Score cards, XP bars.
Pop cuts, bounce effects.
```
```
STYLE — CARNIVAL SURGE (Lins): Max color — hot pink #FF1493, yellow #FFE000, teal #00CED1.
Collage layering. Text MASSIVE at ANGLES. Confetti bursts.
Smash cuts, flash frames.
```
```
STYLE — SHADOW CUT (Hillmann): Deep blacks, cold greys + blood red accent.
Sharp angular text. Heavy shadow. Slow creeping push-ins.
Hard cuts to black. Film noir tension.
```
```
STYLE — DECONSTRUCTED (Brody): Dark grey #1a1a1a, rust orange #D4501E.
Type at angles, overlapping. Gritty textures, scan-line glitch.
Smash cuts with flash frames.
```
```
STYLE — MAXIMALIST TYPE (Scher): Red, yellow, black, white — max contrast.
Text IS the visual. Overlapping at different scales, 50-80% of frame.
Kinetic everything. Smash cuts, flash frames.
```
```
STYLE — DATA DRIFT (Anadol): Iridescent — purple #7c3aed, cyan #06b6d4, deep black.
Fluid morphing compositions. Thin futuristic type.
Liquid dissolves. Particles coalesce into numbers.
```
```
STYLE — RED WIRE (Tartakover): Red, black, white, emergency yellow.
Bold condensed all-caps. Split screens, tickers, timestamps.
Snap cuts, flash frames. Zero breathing room.
```

**When to use which:**
- User has no strong visual preference → browse API styles, pick one
- User wants specific brand colors/fonts/motion → prompt style
- User wants a curated look + specific media types → `style_id` + selective prompt additions

### Avatar

📖 **Full avatar discovery flow, creation APIs, voice selection → [references/avatar-discovery.md](references/avatar-discovery.md)**

**Decision flow:**
1. Ask: "Visible presenter or voice-over only?"
2. If voice-over → no `avatar_id`, state in prompt.
3. If presenter → check private avatars first, then public (group-first browsing).
4. **Always show preview images.** Never just list names.
5. Confirm voice preferences after avatar is settled.

**Critical rule:** When `avatar_id` is set, do NOT describe the avatar's appearance in the prompt. Say "the selected presenter." This is the #1 cause of avatar mismatch.

---

## Script

### Structure by Type

**Script language:** Write the script in the video language (from Discovery item 10). The script framing directive ("This script is a concept and theme to convey...") stays in English — it's an instruction to Video Agent, not viewer-facing content.

Content structure only. Do NOT assign per-scene durations — let Video Agent pace naturally.

- **Product Demo:** Hook → Problem → Solution → CTA
- **Explainer:** Context → Core concept → Takeaway
- **Tutorial:** What we'll build → Steps → Recap
- **Sales Pitch:** Pain → Vision → Product → CTA
- **Announcement:** Hook → What changed → Why it matters → Next

### Critical On-Screen Text

Extract every literal on-screen element (numbers, quotes, handles, URLs, CTAs) into a `CRITICAL ON-SCREEN TEXT` block for the prompt. Without this, Video Agent will summarize/rephrase.

### Script Framing (CRITICAL)

Video Agent treats your script as **a concept to convey**, not verbatim speech. Always add this directive to the prompt:

> "This script is a concept and theme to convey — not a verbatim transcript. You have full creative freedom to expand, elaborate, add examples, and fill the duration naturally. Do not pad with silence or pauses."

Without it, Video Agent pads with dead air to hit the duration target.

### Voice Rules

Write for the ear. Short sentences. Active voice. Contractions are good.

### Present the Script

Show user the full script with word count + estimated duration. Get approval before Prompt Craft.

---

## Prompt Craft

Transform the script into an optimized Video Agent prompt.

### Construction Rules

1. **Narrator framing.** With `avatar_id`: "The selected presenter [explains]..." Without: describe desired presenter or "Voice-over narration only."
2. **Duration signal.** State the target duration in the prompt.
3. **Script freedom directive.** ALWAYS include the script framing directive from Script.
4. **Asset anchoring.** Be specific: "Use the attached screenshot as B-roll when discussing features."
5. **Tone calibration.** Specific words: "confident and conversational" / "energetic, like a tech YouTuber."
6. **One topic.** State explicitly.
7. **Style block at the end.** Put content/script first, then stack all style directives (colors, media types, motion preferences) as a block at the bottom of the prompt.
8. **Language separation.** Script content and narration in the video language. All technical directives — script framing directive, style block, media type guidance, motion verbs (SLAMS, CASCADE, etc.), and frame check corrections — stay in English. Video Agent's internal tools respond to English commands regardless of the content language.

### Prompt Approach

| Signal | Approach |
|--------|----------|
| ≤60s, conversational | **Natural Flow** — script + tone + duration. No scene labels. |
| >60s, data-heavy, precision | **Scene-by-Scene** — scene labels with visual type + VO per scene |

### Visual Style Block

Every prompt should end with a style block. Without one, visuals look inconsistent scene-to-scene.

**Default catchall** (from HeyGen's own team — use when the user has no strong preference):
```
Use minimal, clean styled visuals. Blue, black, and white as main colors.
Leverage motion graphics as B-rolls and A-roll overlays. Use AI videos when necessary.
When real-world footage is needed, use Stock Media.
Include an intro sequence, outro sequence, and chapter breaks using Motion Graphics.
```

**Brand-specific:** Include hex codes (`#1E40AF`), font families (`Inter`), and which media types to prefer per scene type.

📖 **Style presets (Minimalistic, Cinematic, Bold, etc.) → [references/official-prompt-guide.md](references/official-prompt-guide.md)**

### Media Type Selection

Video Agent supports three media types. Guide it explicitly or it guesses (often wrong).

| Use Case | Best Media Type |
|---|---|
| Data, stats, brand elements, diagrams | **Motion Graphics** — animated text, charts, icons |
| Abstract concepts, custom scenarios | **AI-Generated** — images/videos for things stock can't cover |
| Real environments, human emotions | **Stock Media** — authentic footage from stock libraries |

Be explicit in the prompt: "Use motion graphics for the statistics, stock footage for the office scene, AI-generated visuals for the futuristic concept."

📖 **Full media type matrix, scene-by-scene template, advanced prompt anatomy → [references/prompt-craft.md](references/prompt-craft.md)**
📖 **Named styles (Deconstructed, Swiss Pulse, etc.) → inlined in Style Selection above**
📖 **Motion vocabulary and B-roll → [references/motion-vocabulary.md](references/motion-vocabulary.md)**

### Orientation

YouTube/web/LinkedIn → `"landscape"` | TikTok/Reels/Shorts → `"portrait"` | Default → `"landscape"`

---

## Frame Check

**Runs automatically when `avatar_id` is set, before Generate. Appends correction notes to the Video Agent prompt. Does NOT generate images or create new looks.**

> ⛔ **SUBAGENT RULE:** Frame Check MUST run in the **main session**. Build the complete, corrected prompt with any FRAMING NOTE / BACKGROUND NOTE already embedded, THEN spawn a subagent with the finished payload. Subagents only submit, poll, and deliver.

### Avatar ID Resolution (ALWAYS run first)

**Never trust a stored `look_id` — looks are ephemeral and get deleted.** Always resolve fresh from the `group_id`:

**MCP:** `list_avatar_looks(group_id=<group_id>)` — returns all looks for the group.
**CLI:** `heygen avatar looks list --group-id <group_id> --limit 20`

From the response, pick the look matching the target orientation. Use the first match. If no looks exist in the group, tell the user.

**Rule:** Store only `group_id` in AVATAR files. Resolve `look_id` at runtime.

### Steps

1. **Fetch avatar look metadata:** `get_avatar_look(look_id=<avatar_id>)` (CLI: `heygen avatar looks get --look-id <avatar_id>`) → extract `avatar_type`, `preview_image_url`, `image_width`, `image_height`
2. **Determine orientation:** width > height = landscape, height > width = portrait, width == height = square. Fetch fails = assume portrait.
3. **Determine background:** `photo_avatar` → Video Agent handles environment. `studio_avatar` → check if transparent/solid/empty. `video_avatar` → always has background.
4. **Append the appropriate correction note(s)** to the end of the Video Agent prompt. That's it. No image generation, no new looks.

### Correction Matrix

| avatar_type | Orientation Match? | Has Background? | Corrections |
|---|---|---|---|
| `photo_avatar` | ✅ matched | (n/a) | None |
| `photo_avatar` | ❌ mismatched or ◻ square | (n/a) | Framing note |
| `studio_avatar` | ✅ matched | ✅ Yes | None |
| `studio_avatar` | ✅ matched | ❌ No | Background note |
| `studio_avatar` | ❌ mismatched or ◻ square | ✅ Yes | Framing note |
| `studio_avatar` | ❌ mismatched or ◻ square | ❌ No | Framing note + Background note |
| `video_avatar` | ✅ matched | ✅ Yes | None |
| `video_avatar` | ❌ mismatched or ◻ square | ✅ Yes | Framing note |

### Framing Note (append to prompt)

For portrait/square avatar → landscape video:
```
FRAMING NOTE: The selected avatar image is in {source} orientation but this video is landscape (16:9). Frame the presenter from the chest up, centered in the landscape canvas. Use AI Image tool to generative fill to extend the scene horizontally with a complementary background environment that matches the video's tone (studio, office, or contextually appropriate setting). Do NOT add black bars or pillarboxing. The avatar should feel natural in the 16:9 frame.
```

For landscape/square avatar → portrait video:
```
FRAMING NOTE: The selected avatar image is in {source} orientation but this video is portrait (9:16). Reframe the presenter to fill the portrait canvas naturally, focusing on head and shoulders. Use AI Image tool to generative fill to extend vertically if needed. Do NOT add letterboxing. The avatar should fill the portrait frame comfortably.
```

### Background Note (studio_avatar only, no background)

```
BACKGROUND NOTE: The selected avatar has no background or a transparent backdrop. Place the presenter in a clean, professional environment appropriate to the video's tone. For business/tech content: modern studio with soft lighting and subtle depth. For casual content: bright, minimal space with natural light. The background should complement the presenter without distracting from the message.
```

📖 **Full correction templates and stacking matrix → [references/frame-check.md](references/frame-check.md)**

---

## Generate

### Pre-Submit Gate

**Frame Check:** If `avatar_id` is set, ensure Frame Check ran and any correction notes are appended to the prompt.

**Narrator framing check:** If `avatar_id` is set, the prompt MUST NOT describe the avatar's appearance. Say "the selected presenter" instead.

- **Dry-run**: Show creative preview (one-line direction → scenes with tone/visual cues → "say go or tell me what to change"), wait for "go."
- **Full Producer**: User approved script. Proceed.
- **Quick Shot**: Generate immediately.

### Submit

**Step 1: Run Frame Check (if `avatar_id` set) — MAIN SESSION ONLY**
Before submitting, run the Frame Check steps above. Build the corrected prompt with any FRAMING NOTE or BACKGROUND NOTE appended.

**Step 2: Build the complete payload in main session**
Before spawning any subagent, assemble the full set of arguments:

| Flag | Value |
|---|---|
| `--prompt` | corrected prompt — Frame Check notes already embedded |
| `--avatar-id` | look_id resolved from group_id |
| `--voice-id` | confirmed voice_id |
| `--style-id` | optional |
| `--orientation` | `landscape` or `portrait` |

This payload is the handoff to any subagent. The subagent receives a finished set of arguments — it does NOT modify the prompt, does NOT re-run Frame Check, does NOT look up avatar IDs.

**Step 3: Subagent spawn pattern (for batch or non-blocking generation)**

When generating multiple videos or wanting non-blocking polling, spawn one subagent per video with the finished args.
Subagents are for **submit + poll + deliver only**. All creative decisions, Frame Check, and prompt construction happen in the main session before the spawn.

> ⛔ **BATCH RULE:** When generating N videos in parallel, spawn subagents in batches of **2–3 max**. Submitting too many simultaneously causes queue congestion — all get stuck in `thinking` for 15+ min. Submit batch 1, wait for completions, then submit batch 2.

**Step 4: Submit**

**MCP:** `create_video_agent(prompt=<prompt>, avatar_id=<look_id>, voice_id=<voice_id>, style_id=<optional>, orientation=<orientation>)`

**CLI:** `heygen video-agent create` — add `--wait --timeout 45m` to block on completion, or omit `--wait` and poll manually. **Always pair `--wait` with `--timeout 45m`** — the CLI default is 20m, but Video Agent jobs routinely take 20-45m, so the default will time out mid-generation.

```bash
heygen video-agent create \
  --prompt "..." \
  --avatar-id "..." \
  --voice-id "..." \
  --orientation landscape \
  --wait --timeout 45m
```

The CLI returns JSON on stdout: `{"data": {"video_id": "...", "session_id": "..."}}` after submission. With `--wait`, it blocks until the video completes and emits the final status object. Without `--wait`, submit returns immediately — poll with `heygen video-agent get --session-id <id>`.

**⚠️ Always capture `session_id` immediately.** Session URL: `https://app.heygen.com/video-agent/{session_id}`. Cannot be recovered later.

### Polling

**MCP:** `get_video_agent_session(session_id=<session_id>)` — returns status, progress, video_id.
**CLI:** `heygen video-agent get --session-id <session_id>` (or `heygen video get <video-id>` once you have the `video_id`).

Total wall time per video: **20–45 minutes**. If you passed `--wait`, the CLI handles polling with exponential backoff. If polling manually: first check at **5 min**, then every **60s** up to 45 min.

Status flow: `thinking` → `generating` → `completed` | `failed`

Stuck in `thinking` >15 min with no progress → flag to user.

### Delivery

1. Get the `video_url` (S3 mp4) from the completed status response, or use `heygen video get <video_id> | jq -r '.data.video_page_url'` for the shareable link.
2. Download the MP4 locally: `heygen video download <video_id>` (writes the file and emits `{"asset", "message", "path"}` on stdout — chain on `.path`).
3. Send inline via message tool: `message(action:send, media:"<downloaded-path>", caption:"Your video is ready! 🎬\n📊 Duration: [actual]s vs [target]s ([percentage]%)")`. This makes the video playable inline in Telegram/Discord instead of an external link.
4. Also share the HeyGen dashboard link for editing: `https://app.heygen.com/videos/<video_id>`

Always report duration accuracy. Clean up downloaded files after sending.

---

## Deliver

**Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

### Self-Evaluation Log

After EVERY generation, append to `heygen-video-log.jsonl`:

```json
{"timestamp":"ISO-8601","video_id":"...","session_id":"...","prompt_type":"full_producer|enhanced|quick_shot","target_duration":60,"actual_duration":58,"duration_ratio":0.97,"avatar_id":"...","voice_id":"...","style_id":"...","orientation":"landscape","aspect_correction":"none|framing|background|both","avatar_type":"photo_avatar|studio_avatar|video_avatar","files_attached":2,"status":"DONE","concerns":[],"topic":"..."}
```

If user wants changes: adjust prompt based on feedback, re-generate. Never retry with the exact same prompt.

---

## Best Practices

- **Front-load the hook.** First 5s = 80% of retention.
- **One idea per video.** Single-topic produces dramatically better results.
- **Write for the ear.** If you wouldn't say it to a friend, rewrite it.

📖 **Known issues → [references/troubleshooting.md](references/troubleshooting.md)**
