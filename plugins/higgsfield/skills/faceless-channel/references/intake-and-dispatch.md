# Intake and platform dispatch

This reference contains the complete Phase 0 contract. The caller must resolve
the helper-root variables defined by `faceless-channel` before following any
cross-skill path below.

## Contents

- Interactive ChatGPT intake and blocking popup rounds
- Style, voice, duration, aspect, and subtitle locks
- Platform-dispatched headless jobs

### Phase 0 — Intake · native ChatGPT path, fixed semantic order

**INTERACTIVE INTAKE IS A BLOCKING PRECONDITION.** At the start of every ordinary
ChatGPT run, classify the request as either interactive or explicitly hands-off.
Imperatives such as “make,” “create,” “generate,” “produce,” “run,” or “go for it”
do **not** mean hands-off. Lock every parameter explicitly supplied by the user and
collect every missing parameter through the popup rounds below.

Before calling any media-generation, research, narration, assembly, or subtitle tool,
evaluate this exact condition:

```text
interactive && missing(type | style | topic | duration | aspect | subtitles | voice)
```

If true, render the next missing intake round as an actual ChatGPT popup and
**immediately end the turn**. Do not continue Phase 0, announce production, apply
defaults, or enter Phase 1 in that turn. Resume only after the widget response is
present in conversation state, then repeat the same check. The only tools allowed
while satisfying this precondition are `get_faceless_channel_presets` for the style
picker and `list_voices` for the voice picker. Reaching any generation call with an
incomplete interactive intake is a workflow failure.

Collect only missing values in this order: (1) channel type, (2) style, (3) topic /
duration / aspect / subtitles, (4) voice. Use ChatGPT's unversioned GenUI
`ask_user_input` widget for every closed-choice intake question. Never substitute
Codex Plan mode's `request_user_input`: it is unavailable in normal ChatGPT answer
turns and causes the intake to collapse into prose. Never call legacy
`ask_user_question` or `AskUserQuestion`, and never write or call
`ask_user_input_v3` unless the current host explicitly exposes a callable tool with
that exact name.

When a callable `ask_user_input` elicitation tool exists, call it. Otherwise emit this
raw GenUI payload directly in the assistant response; ChatGPT renders it as the
interactive widget:

```text
genui{"ask_user_input":{"questions":[
  {
    "question":"...",
    "options":["...","..."],
    "type":"single_select",
    "free_text_placeholder":"..."
  }
]}}
```

The fenced form above is documentation only. During execution, never put the payload
inside a Markdown code fence. Every question requires `question`, at least two short
`options`, `type:"single_select"`, and a specific `free_text_placeholder`. Emit no
more than three questions per widget. Add one short conversational line before the
widget, then output the widget and end the turn; do not add questions or prose after
it. A tool result or raw payload that renders as a popup is the success condition;
printing question text or JSON as ordinary prose is not. If the current host exposes
the exact callable name `ask_user_input_v3`, it may be used for that host; never assume
or fabricate the name when it is absent. If raw GenUI is rejected by the host rather
than rendered, use one concise
normal-chat question as the last-resort fallback and state that the widget surface was
unavailable.

- **Ask ONLY for what's missing.** Parameters the user already stated in their message
  (duration, aspect, subtitles, style/preset name, topic, channel type) are LOCKED from
  the prompt: do NOT re-ask them and do NOT confirm them — restate the locked ones as a
  plain chat STATEMENT (no question mark, no "confirm or correct", no options) and ask
  only the gaps. A "here's what I gathered —
  all good?" round IS a re-ask and is forbidden. If a round has no missing parameter,
  SKIP that round entirely. Only a merely INFERRED value (e.g. type guessed from the
  topic) still gets confirmed — as a pre-selected option inside the relevant question,
  never as its own extra round.
- **The INTAKE question set is CLOSED.** During intake, the ONLY things this skill may
  ask are type, style, topic, duration, aspect, subtitles, and the voice widget.
  The three post-generation review questions defined above are the only later
  exceptions. NEVER invent extra intake
  questions — no cover/thumbnail image, no video title, no language (write narration in
  the user's language automatically), no character/mascot question, no "anything else?".
  If an idea like a cover feels useful, it is OUT OF SCOPE for this skill — do not offer it.
- **Round 1 — channel type (the niche), alone, first:** chips **Explainer
  (recommended)** first, then History, then Kids, then **Fairy Tale & Myth**
  (retellings of myths/fairy tales/legends — cinematic storybook look,
  `${FACELESS_STYLES_DIR}/references/style-cinematic-storybook.md`; also auto-locks when the user says
  "fairy tale / myth / legend / folklore", in any language incl. their local
  equivalents). Picture Story is NOT a
  chip — it auto-locks when the user says "picture story / stills / slideshow story /
  storybook video / frame-by-frame" or picks the "Frame by frame" card in Round 2
  (narrated stills — `${FACELESS_MODES_DIR}/references/picture-flow.md`). Render this round as one
  `ask_user_input` question with exactly those four options and
  `free_text_placeholder:"Choose a channel type"`, then end the turn.
- **Round 2 — style, IMMEDIATELY after the type:** call
  `get_faceless_channel_presets` to render the unified **Faceless channel presets** catalog.
  If the host can capture a structured selection, use it. Otherwise ask the user to
  reply with the visible card title; do not manufacture a separate preset list. The
  picked card is the LOCKED
  style for the run — lock it and move on (CROSS-CHANNEL PRESET RULE below; the
  "Frame by frame" card locks Picture Story). Skip the widget when the style is already
  decided: a style/preset NAMED in the prompt resolves by name (below), uploaded
  style images (≤3) take the custom path, and a long-form-locked run offers its own
  LONG-FORM style set instead (below). HOW a style was picked never changes its
  mechanics: house styles have no preset id and generate the key from their pinned
  FORMULA (stickman uses the generic webcomic formula in `${FACELESS_STYLES_DIR}/references/prompts.md §0`);
  Kids styles pin 2–3 canonical ref images. Pass authorized HTTPS references directly
  as `medias:[{role:"image",value:url}]`, or use `media_upload_and_confirm` for local
  images, then make ONE `seedream_v5_pro` style-key call with the FORMULA. Refs are
  style donors only, never final frames.
  - **Per-type DEFAULTS + long-form:** when nothing is picked (hands-off, briefs):
    Explainer → **Editorial Motion Graphics** (Stickman Cartoon = the second house
    direction); History → **Editorial Motion Graphics** (named alternates **Paper
    Diorama**, **Mannequin** — `${FACELESS_STYLES_DIR}/references/style-mannequin.md`, clay-render
    reenactment figures); Kids → **Studio 3D** (then Pastel Flat 2D / Colorful 3D /
    Hand-drawn Ink / Poster Vector — `${FACELESS_STYLES_DIR}/references/kids-styles.md`; Fluffy Toy is a
    legacy card in the same catalog); Picture Story → **Flat 2D Papercraft** (then
    Stickman / Hand-drawn Ink — one-liners verbatim from
    `${FACELESS_MODES_DIR}/references/picture-flow.md`; adjacent asks map to the closest and confirm in one
    line); Fairy Tale & Myth → **Cinematic Storybook** (the only style;
    `${FACELESS_STYLES_DIR}/references/style-cinematic-storybook.md`, canon-refs → unique seedream key like
    the Kids flow). **LONG-FORM AUTO-LOCK: if the request already says ≥10 minutes and/or
    "documentary", the LONG-FORM direction is LOCKED from the prompt** — never
    offered as an option (offering what the user already chose is a re-ask). A locked
    long-form run: duration options become 10/15/20 min (+ Other) if not already
    stated; the style round offers the LONG-FORM set — **Watercolor Chronicle
    (recommended, first)** / Paper Diorama / Editorial Motion Graphics / Upload —
    with descriptions VERBATIM from the style files (`history-longform.md` carries
    Watercolor's one-liner); and the mandatory time/cost warning + ERA-MAP flow from
    `${FACELESS_MODES_DIR}/references/history-longform.md` apply.
  - **ONE catalog — "Faceless channel presets"** (backend consolidation 2026-07-27: the
    12 channel cards were moved into the explainer catalog and it was renamed). List it
    with **`get_faceless_channel_presets`** and turn a card into a style-reference `media_id`
    with **`resolve_faceless_channel_preset`** — both work for every card, house styles
    included (verified live: `Fairy Tale & Myth` → `media_id`). There is no separate
    faceless catalog and no separate resolver any more.
    - **The 12 channel cards, mapped to their style files** (CMS title on the left —
      titles differ slightly from the file names, so fuzzy-map, same rules as
      user-typed names): Editorial Motion Graphics · Stickman Cartoon (generic §0
      formula) · Paper Diorama · Mannequin · Watercolor Chronicle · Studio 3D · Pastel
      Flat 2D · Colorful 3D · **Hand Drawn** = Hand-drawn Ink · Poster Vector ·
      **Frame by frame** = the Picture Story direction card · **Fairy Tale & Myth** =
      the Cinematic Storybook look (`${FACELESS_STYLES_DIR}/references/style-cinematic-storybook.md`).
    - **Two cards are DIRECTION cards, not just looks.** "Fairy Tale & Myth" locks
      channel type = Fairy Tale & Myth (on-twos `--stepped 12` + mysterious-calm bed).
      "Frame by frame" locks channel type = Picture Story with the Flat 2D Papercraft
      look (`${FACELESS_MODES_DIR}/references/picture-flow.md` — formula unchanged, only the card name differs).
    - **Legacy explainer cards live in the same catalog** (Fluffy Toy, 3D Papercraft,
      Mixed Media, Whiteboard Doodle, Pixel Art, Claymotion, Low Poly, Isometric Flat
      Vector, 3D Mix, 2D Illustrator, Dynamic Motion Design, Vintage Documentary,
      Custom Template). They are valid on any channel (CROSS-CHANNEL PRESET RULE) but
      have NO pinned style file: resolve the card to its `media_id`, use it as the look
      anchor, and write the locked formula from the card art's visible traits.
    - Where a card DOES have a style file, that file wins: the pinned FORMULA +
      canonical static.higgsfield.ai refs ARE the preset (self-sufficient — a
      `media_id` is optional extra anchoring). Kids styles always keep the
      canonical-refs → unique seedream key flow; the FORMULA goes byte-identical into
      every prompt regardless of anchor source.
  - **CROSS-CHANNEL PRESET RULE — any catalog preset is valid on ANY channel type.**
    A preset named on input (user message, brief `preset`, or a card pick) is the
    LOCKED style for the run even when it is not among that channel's defaults —
    History in Colorful 3D, Kids in Editorial, Explainer in Watercolor Chronicle are
    all legal. Never re-ask, never "correct" the choice, never silently substitute the
    channel's default. **A style brings ONLY its look, never its home channel's
    mechanics:** the style file contributes the FORMULA, canonical refs / anchor
    mechanism (Kids styles keep their unique-key flow anywhere), palette lock,
    {MOTION} + negatives, and style-inherent laws (e.g. Mannequin's cast/identity
    rules). Everything narrative stays with the CHOSEN channel type: cut pattern
    (Kids' 4-cut belongs to the Kids CHANNEL — a History run in Studio 3D cuts the
    standard 5), narrator↔character interplay, beat grammar, documentary skeleton,
    script rules. **Kids-catalog styles carry ONE style-inherent extra: the default
    wordless music bed** (`${FACELESS_STYLES_DIR}/references/kids-styles.md §Kids music bed`) — a history or
    explainer run in a Kids look still gets the bed, with the MOOD matched to the
    channel's tone (playful-light for the look, not babyish). **"Fairy Tale & Myth"
    (Cinematic Storybook) carries TWO style-inherent extras anywhere it is used: the
    on-twos cadence (`--stepped 12`) and a mysterious-calm music bed**
    (`${FACELESS_STYLES_DIR}/references/style-cinematic-storybook.md`).
    The ONE exception is **"Frame by frame"** (or any explicit stills/picture
    preset), which IS a direction card: it locks Picture Story MECHANICS even when
    the channel/brief says history or kids — the channel keeps only its TONE.
    Watercolor Chronicle outside long-form is just the watercolor look — no
    long-form skeleton, no ERA MAP unless the run is long-form.
  - **Pick another preset** → if the user has ALREADY NAMED a preset (in their message
    or by choosing a named option), resolve it BY NAME: `get_faceless_channel_presets` → exact
    match, else FUZZY match (case/word-order/partial — "fluffy toy" hits "Fluffy Toys",
    "3d paper" hits "3D Papercraft") → `resolve_faceless_channel_preset`, confirm in one line.
    If nothing plausibly matches, offer the 1–2 closest names in the SAME breath and only
    then fall back to the widget — never jump straight to the widget over a typo (asking
    twice for the same choice is a bug). Browsing = the Round-2 widget, which serves the
    same single catalog the resolver does. (Never enumerate presets as a plain text
    question.)
  - **Upload ≤3 style images** → collect via the media upload widget (style donors only).
- **Round 3 — compact intake for everything else (only the missing ones; skip when
  nothing is missing):** render `ask_user_input` widgets with no more than three
  questions each, then continue in the next compact round if necessary. Collect
  (a) topic — free text / channel-link /
  "randomizer"; (b) duration — 1 / 2 / 3 min (+ Other), **Fairy Tale & Myth offers
  2 / 3 min with 2 as the default** (a myth needs room to breathe); **on KIDS runs
  (Kids channel or a Kids-catalog style) the duration question ALSO offers "Music
  video — a real sung song (1 or 2 min)"** — picking it locks SONG MODE (`${FACELESS_MODES_DIR}/references/kids-song.md`:
  the song is generated FIRST, the blocks are staged to it; direct asks like "kids
  song / sing-along / music video" lock it from the prompt); (c) frame aspect —
  **16:9 (default)** / 9:16 and NOTHING ELSE (the video model supports only these
  two — never offer 1:1 or other ratios); (d) subtitles — yes / no (not offered in
  SONG MODE).
- **Round 4 — voice (the narrator), LAST — use the voice library (no generated
  samples):** SKIP in SONG MODE. Otherwise call `list_voices` so the user can see and
  preview current voices, then end the turn and wait for its selectable widget. If the
  host surfaces the voice list without selectable UI, render one `ask_user_input`
  question in the next turn using the returned voice names as options and
  `free_text_placeholder:"Choose a listed narrator voice"`; map the chosen name back to
  the exact returned id/type. Lead with a ONE-LINE RECOMMENDATION for the
  channel (plain chat text next to the widget): **History → Arthur or Callum; Kids → Remy; Explainer →
  Remy, Roxie or Cillian; Fairy Tale & Myth → Arthur or Callum (deep storyteller),
  or Remy for gentler tales; Picture Story → match the tone** (kids-warm → Remy,
  history-witty → Arthur/Callum, slice-of-life → Roxie/Cillian). The user still picks
  freely. Do NOT generate `seed_audio` audition samples (wasted
  credits, confuses the flow), do NOT list voices as text options with invented
  descriptions. **Record the picked voice's exact `voice_id` + `voice_type` — LOCKED for
  the whole video** (rule 17); never re-ask it later. **If the picked voice ERRORS on
  first use ("didn't resolve" / not found): do NOT re-open the widget** — look the id up
  via `list_voices` to recover the correct `voice_type` (preset vs element is the usual
  culprit) and retry with the exact pair; re-ask the user ONLY if the id truly does not
  exist in the library. Intonation and MOOD are not chosen
  by voice: the script shapes delivery to fit the channel type + topic (line writing +
  performed brackets — `${FACELESS_FLOW_DIR}/references/vo_and_captions.md`); the voice itself never changes.
- **Planning locks do not stop; media reviews do.** STYLE LOCK, SCRIPT LOCK, and
  long-form OUTLINE LOCK remain notification-only. ASSET LOCK is folded into the
  completed IMAGE review. In interactive mode the completed IMAGE, VIDEO, and AUDIO
  stages each show one list and stop on the review question from the batch contract.
  These are the only production approval stops. Named failures (retry ladder
  exhausted, assembly assert, BUDGET_CAP) also stop the run.
- **AUTO / hands-off mode** (a platform flag, or the user says "no approvals /
  end-to-end / don't ask" / "pick the voice yourself" / "surprise me"): SKIP the
  intake rounds INCLUDING the voice widget — missing parameters take the documented
  defaults: type Explainer, aspect 16:9, subtitles off, duration 1 min, the type's
  default style (Kids → Studio 3D). **VOICE IS NOT ASKED in this mode — do NOT open
  the voice widget. Auto-pick the CHANNEL'S RECOMMENDED voice by name via
  `list_voices` and lock it (record `voice.lock`), then name it in one line:**
  - History → **Arthur** (or Callum)
  - Kids → **Remy**
  - Explainer → **Remy** (or Roxie / Cillian)
  - Fairy Tale & Myth → **Arthur** (or Callum); Remy for gentler tales
  - Picture Story → by tone: kids-warm → Remy, history-witty → Arthur/Callum,
    slice-of-life → Roxie/Cillian
  These are preset voices — `list_voices` resolves the name to its `voice_id` +
  `voice_type`. Opening the widget in hands-off is a bug. **Stopping for a review
  approval in auto mode is a bug — auto mode exists precisely so the user gives no
  approvals; nothing in it waits.**
- **"Randomizer" topic path:** WebSearch what is trending NOW (2–3 angles: "trending
  topics this week {month year}", "most searched questions this week", plus one vertical
  the user cares about if known). A good pick has a **why/how question** at its core, one
  **surprising number or reversal**, strong **visual potential**, broad appeal ("Why X is
  suddenly everywhere", "The real reason X costs so much"). Avoid breaking tragedies and
  active disasters, gossip with no data angle, anything unverifiable by two sources.
  Present the pick + one runner-up on the topic step; proceed with the pick unless the
  user swaps.

**GATE 0:** you have {type, aspect, subtitles y/n, **voice_id+voice_type (the locked
pair — WRITE it to a `voice.lock` file next to the outputs, one line:
`voice_id voice_type`)**, topic, duration, style}. Compute **N = duration_seconds / 10,
rounded half-UP (45s → 5), minimum 3**. If a channel profile was saved earlier (memory /
project notes: style key + voice + type), reuse it and ask only the topic. Style option
descriptions come VERBATIM from the style files' intake one-liners — never improvised,
never naming third-party brands/studios, never promising on-screen text.

### Platform-dispatched jobs (headless) — skip Phase 0

When the run is a platform job, the RUN BRIEF is the intake. Do not wait on any picker
or question tool; read every parameter from the brief and proceed to Phase 1:

- **`topic`** (required) — free text; may say *derive it from the attached media* (then
  build the narration from the attachments; never fail the job for a missing topic).
- **`duration_seconds`** (required) — the brief states duration in **seconds**, not
  minutes. `N = ceil(seconds / 10)`; a non-multiple-of-10 request makes the LAST block
  short (size its line to fit). Picture Story converts the same seconds to a beat count
  (25–35 beats/min) — billing still counts 10s windows: `block_count = ceil(seconds/10)`.
  At intake, write down immutable `REQUESTED_SECONDS` and
  `BILLING_BLOCKS = ceil(REQUESTED_SECONDS/10)`. Never recompute billing blocks from an
  assembled file's actual duration.
- **`aspect`** (required) — `16:9` or `9:16`, nothing else.
- **`channel_type`** — explainer | history | kids | picture_story | fairytale; missing →
  infer from the topic, default explainer (a myth/fairy-tale/legend topic infers
  fairytale). `duration_seconds ≥ 600` on history auto-locks the long-form documentary
  direction (`${FACELESS_MODES_DIR}/references/history-longform.md`). `fairytale` uses the Cinematic Storybook
  style (`${FACELESS_STYLES_DIR}/references/style-cinematic-storybook.md`): on-twos `--stepped 12` + mandatory
  mysterious-calm bed. A stills/frame-by-frame `preset` OVERRIDES `channel_type`:
  Picture Story mechanics, the channel's tone.
- **`voice_id` + `voice_type`** — the locked pair for EVERY take; a binding setting, not
  a suggestion. If the brief carries `voice_id` without `voice_type`, recover the type
  via `list_voices` (never guess, never go voiceless, never submit `seed_audio` without
  the pair). No voice in the brief at all → pick the CHANNEL'S RECOMMENDED voice via
  `list_voices` (History → Arthur/Callum, Kids → Remy, Explainer → Remy/Roxie/Cillian,
  Picture Story → by tone), lock it, and name it in the final report.
- **`style_reference_urls`** (optional, ≤3) are the AUTHORITATIVE look whenever present,
  including when FNF resolved a CMS preset into image URLs. Import every URL with
  authorized HTTPS media values (or `media_upload_and_confirm` for local files), build
  the single style key from those donors, and derive the locked
  formula only from their visible rendering traits. Do NOT also apply, blend, or infer a
  house/channel default. A simultaneous **`preset` id is lineage metadata only**: never
  resolve it and never use its title/name to generate. Without reference URLs, resolve a
  **`preset`** id or name per Phase 0 (id-only → map it to its name with
  `get_faceless_channel_presets`, then use the pinned formula + canonical refs; a card without a
  style file resolves through `resolve_faceless_channel_preset` instead). Any catalog preset is valid
  with any `channel_type` (CROSS-CHANNEL PRESET RULE): apply its look, keep the channel's
  mechanics, and never substitute the default. With neither refs nor a preset, use the
  channel type's default style.
- **`subtitles`** (default false), **`music_url`** (optional — the bed file; policy
  unchanged: never block on it), **`channel_dna`** (optional — a previous run's DNA
  object: reuse its style key, voice pair and named assets so the new video matches the
  channel; only the topic changes).

Every planning lock posts as a notification and proceeds (auto-approve semantics);
all media review questions are skipped. A platform run MUST end with Phase 8 — the terminal report is
what completes the job; a run that never reports is a failed job regardless of how good
the local MP4 is.
