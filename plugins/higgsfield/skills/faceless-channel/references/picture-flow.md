# picture-flow.md — the PICTURE STORY direction (narrated stills)

The fourth channel direction, PEER to Explainer / History / Kids: the video is
built from STILL IMAGES, not motion clips. One continuous narration is generated
first; Whisper word timestamps then define a dense sequence of ~0.7–1.2s
microframes, with a new frame at every framing change. The assembler holds each
frame for its timeline segment; there are no fixed 10s windows. Tone is free: a
Picture Story can be a kids bedtime tale, a history vignette, a deadpan
slice-of-life — the direction is the MECHANIC, not the audience.

Models stay locked: images `seedream_v5_pro`, voice `seed_audio`. NO
`gemini_omni` in this direction — nothing is animated.

**The "Frame by frame" preset card — or ANY explicit stills/picture preset ask —
LOCKS this direction, even when the channel/brief says History or Kids.** The
channel keeps its TONE (kids-warm, history-witty); the mechanics are this
file's. Never "correct" the pick back to a motion flow.

## Styles (offer these three chips; descriptions VERBATIM)

1. **Flat 2D Papercraft (recommended)** — "Layered cut-paper collage — flat
   colored paper shapes with crisp cut edges, subtle drop shadows between
   layers, textured construction paper." (Preset card: **"Frame by frame"** in the
   "Faceless channel presets" catalog — picking that card means this direction + this
   look.)

   FORMULA (§0 form, byte-identical everywhere):

   > flat 2D papercraft collage: characters and scenery cut from colored
   > construction paper with crisp scissor-cut edges, layered flat shapes
   > with subtle soft drop shadows between paper layers, visible paper grain
   > and fiber texture, slightly imperfect hand-cut silhouettes, matte
   > saturated paper palette, simple readable compositions on a plain paper
   > backdrop, handcrafted collage feel, non-photorealistic, no gradients
   > outside paper shadows, no outlines — shapes are defined by paper edges.

   PALETTE LOCK: `matte construction-paper palette of the reference images —
no neon, no gradients, colors read as physical paper`.

2. **Stickman Cartoon** — the generic webcomic formula from
   `${FACELESS_STYLES_DIR}/references/prompts.md §0` (crude paint-program webcomic), verbatim.

3. **Hand-drawn Ink** — the formula from `${FACELESS_STYLES_DIR}/references/kids-styles.md §4`
   (thin-line ink on pure white, greyscale), verbatim.

Something adjacent the user asks for ("crayon", "flat vector") → map to the
closest of the three and confirm in one line; uploads work as style donors as
usual.

## FRAME-BY-FRAME, not a slideshow (this direction's core)

The audio is ONE continuous narration of the whole story (Phase 5) — NEVER
2–3s per-beat snippets. Whisper then gives word timestamps, and FRAMES are
laid onto that timeline (Phase 5b/4/6). The point is animation-by-stills: a
single moment gets a SMALL BURST of near-identical frames that each change ONE
detail, so it reads as movement — not one static picture held while the
narrator talks.

**The mental model — a moment = a burst of edited frames of the SAME shot:**

> "woke up, on his back" → F1 WIDE: John flat on his back, eyes closed.
> (same shot) → F2: eyes OPEN. (same shot) → F3: head turned, squinting.
> "his face — a scowl" → F4 CLOSE-UP: John's face neutral.
> (same shot) → F5: brows knit, scowl lands.
> "he sat up on the bed" → F6 MEDIUM: sitting up, mid-rise.
> "shuffled down the hall" → F7: walking the hallway.
> (same shot) → F8: still walking, scratching his head.
> "brushing his teeth" → F9 INTERIOR: brush AT his mouth.
> (same shot) → F10: hand DOWN, done, foam on lip.

Every arrow is ONE image. Notice most moments are 2–3 frames of the SAME
composition with one change (eyes, brow, hand position) — THAT is the
frame-by-frame feel. A brand-new framing happens when the ACTION or PLACE
changes (bed → face → hall → bathroom), not on every frame.

- **A new SHOT (new framing) whenever the line changes** action, place or
  subject; WITHIN a shot, 2–3 micro-variation frames carry the little
  movement (open eyes, turn head, raise hand).
- **SHOT MIX (the cut rhythm):** each frame names its SHOT — WIDE / MEDIUM /
  CLOSE-UP — mixed RANDOMLY with exactly one hard ban: **two CLOSE-UPs never
  run back to back.** Everything else may repeat (WIDE WIDE is legal, MEDIUM
  MEDIUM is legal): a healthy run reads like
  `W M W C W W M C W`. The CLOSE-UP → MEDIUM handoff is the money transition —
  show the emotion close, then play the resulting movement on the medium.
  (A micro-variation frame keeps its base's shot size — that's the one legal
  same-framing repeat, and it still counts as a CU for the no-two-CUs rule.)
- **Frame cadence — a frame every ~0.7–1.2s.** Once Whisper gives the
  timeline, slice it so NO frame holds longer than ~1.5s (hard cap 2.5s in the
  assembler). A phrase that spans 2s = 2 frames; 3s = 3 frames — usually the
  base plus its micro-variations. The picture changes about twice per spoken
  beat; a frame lingering while the narrator keeps talking is the slideshow we
  are killing.
- **THE MICRO-VARIATION FRAME (the whole trick) — it is an EDIT, not a
  re-render:** most frames ARE the previous frame with ONE detail changed.
  Generate it by passing the previous rendered frame's job_id as the **ONLY**
  reference — **do NOT attach the character sheet, location or props** (those
  make the model rebuild the scene, producing a different picture instead of an
  edit). Prompt: "Take the reference image and keep it EXACTLY — same
  composition, crop, camera, character, colors, background, style. Change ONLY:
  {one detail — eyebrows knit / eyes open / hand lowers / foam appears}. Do not
  redraw anything else." A run of 2–4 such edits chained on ONE shot IS the
  animation; a genuinely new framing (from assets) only when the action or
  place changes. See Phase 4 for the KIND-A/KIND-B split.
- **Frame count is a HARD FLOOR, not a suggestion: at least one frame every
  ~1.5s of narration, target one every ~1s.** A 1-minute story = **45–70
  FRAMES** (never fewer than ~40); 2 minutes = 90–140. Plan the count from the
  target duration BEFORE generating and show it at SCRIPT LOCK. **The assembler
  REJECTS a run with fewer than `ceil(narration_sec / 1.5)` frames** (a 60s
  story with 15 frames is a slideshow and hard-fails) — so generate the full
  dense set up front, don't discover the shortfall at assembly.
- **Why this is cheap: MOST frames are micro-variations** — the previous frame
  with ONE detail changed (one ref image + one `change_only` line). A single
  spoken moment ("he woke up") is not one frame, it is a BURST: on his back →
  eyes open → head turns → sits up. Budget ~2–3 frames per spoken beat; if a
  beat has only one frame, you are under-generating. Generate variations
  liberally — they are one seedream call each and they ARE the animation.
- **SHOW WHAT THE LINE NAMES** (the variety law applies): the frame's nouns
  are IN the picture.
- Characters recur across frames (John in every frame) — identity comes from
  the asset roster refs + the previous-frame ref, same as the video flow.

## Pipeline deltas (vs the video flow)

Phases keep their numbers; what changes:

- **Phase 2 — assets (MANDATORY, FIRST — frames are composed FROM them):**
  characters (2:3) + key locations (chosen aspect) + props (1:1), style
  formula byte-identical, ≤7 refs per image call. Assets are REFERENCES
  ONLY — an asset sheet NEVER appears in the final as a slide (the assembler
  hard-fails on any wrong-aspect image). Locations are cheap here — a beat
  reuses its location REF with a different composition, never the same
  rendered frame. Submit independent assets through `generate_image_batch` in
  sequential groups of at most six and wait each group with `jobs_wait`.
- **Phase 3 — script = ONE continuous narration + a shot outline.** Write the
  whole story as flowing narration (the text the singer/narrator will actually
  read end to end), PLUS a shot outline naming the framings in order
  (bed-wide → face-CU → hall-medium → bathroom) and, per framing, which
  micro-variation frames it will spawn (eyes open, brow knits, hand lowers).
  SCRIPT LOCK shows the narration + the outline + the estimated FRAME count.
- **Phase 5 — voice FIRST, ONE CONTINUOUS TRACK (not per-beat):** generate the
  ENTIRE narration as ONE `seed_audio` take (the locked voice pair), read
  straight through — NEVER 2–3s snippets per phrase (that was the old bug).
  Long stories exceed the 2048-char prompt limit → split into a FEW LARGE
  chunks (whole paragraphs, ~1800 chars each, same voice pair + same
  {DELIVERY} verbatim) and losslessly join them into ONE `narration.wav`
  (`ffmpeg -f concat -c copy` — legal input prep). One flowing read, natural
  pacing; regenerate a chunk on wrong timbre or garbled reads. The `narrator`
  skill submits chunks with `generate_audio_batch` and waits with `jobs_wait`.
  After all chunks pass, interactive mode calls `show_generation_by_ids` with
  the exact final audio ledger, asks whether to continue to images, and ends the
  turn.
- **Phase 5b — Whisper the narration → the NUMBERED FRAME TIMELINE.** Run
  the preinstalled sandbox script through `sandbox_exec`:
  `${HF_WORKFLOWS}/faceless-channel-video/scripts/subtitles/audio_to_captions.py narration.wav --json words.json` (word
  timestamps). Group the words into FRAME SEGMENTS: walk the shot outline and
  cut a new segment at each micro-beat — every ~0.7–1.2s of speech, and
  ALWAYS at a framing change. **NUMBER the segments 1..N in strict narration
  order (the order they are SPOKEN)** — this number is the frame's identity for
  the rest of the run. Each segment = {n, start, end (from Whisper), the frame
  it shows}. This timeline (not per-take lengths) sets every frame's duration.
  No frame segment longer than ~1.5s — split it (the split halves keep
  sequential numbers). Write the timeline down; every later step keys off `n`.
- **Phase 4 — images AFTER the timeline exists. TWO frame kinds, and MOST are
  EDITS (this is the whole point — read carefully):**

  **KIND A — NEW-FRAMING frame (`image_mode:"new"`):** a fresh `seedream_v5_pro`
  render composed FROM the Phase-2 assets. `medias` = the segment's location →
  character sheet(s) → props (role `image`); prompt = the SHOT +
  scene in THIS EXACT style {FORMULA}. Use this ONLY when the ACTION or PLACE
  changes (bed → face → hallway → sink). These are the MINORITY — roughly one
  per real scene change.

  **KIND B — EDIT / micro-variation frame (`image_mode:"variation"`) — the
  MAJORITY (~2 of every 3 frames):** DO NOT re-render from assets. Take the
  PREVIOUS rendered frame's job_id and pass it as the **ONE and ONLY**
  reference on the call — **NO asset sheets, NO location, NO props** (adding
  them makes the model rebuild the scene from scratch — the exact bug that
  yields different pictures instead of an edit). Prompt VERBATIM shape:
  > "Take the reference image and keep it EXACTLY: same composition, same crop,
  > same camera, same character, same colors, same background, same style.
  > Change ONLY: {one small detail — eyes open / brows knit / hand lowers /
  > mouth opens / foam appears}. Do not redraw or re-stage anything else."
  The result is the previous frame with ONE thing moved — THAT is the
  animation. A burst on one shot = KIND A once, then 2–4 KIND-B edits CHAINED,
  each editing the frame before it (frame3 edits frame2 edits frame1). **If two
  consecutive frames look like different photos of the same moment, KIND B was
  done wrong — assets were sent and the scene got re-rendered instead of the
  previous frame edited.**

  Both kinds: `aspect_ratio` = the CHOSEN aspect (never square/2:3/1:1 — the
  assembler rejects wrong-aspect), 1080p-class not 2k/2.7k, no in-frame text.
  Submit independent KIND-A frames through `generate_image_batch` in groups of
  at most six. KIND-B edits run in chain order because each needs its
  predecessor; use a one-request headless batch for a single chain step, or
  batch up to six steps from different chains whose predecessors are already
  complete. Wait every group with `jobs_wait`. **Generate the FULL dense set to clear the
  assembler floor (`ceil(narration_sec/1.5)`, ~40 for a minute) AND make ~2/3
  of them KIND-B edits. Mostly-KIND-A is the "every frame is a different
  picture" bug — regenerate the in-between frames as edits of their
  predecessor, do not pad holds.**
  - **NAMING — STRICT, this is how the video stops being a jumble:** the
    moment a frame's job completes, download it to **`frameNNN.png` where NNN
    is its 3-digit TIMELINE number from Phase 5b** (`frame001.png`,
    `frame002.png`, … in SPOKEN order — NOT the order jobs happen to finish).
    Jobs return out of order and their job_ids are meaningless to the cut;
    the `frameNNN` name is the ONLY thing that carries sequence. Keep a
    `n → job_id → frameNNN.png` ledger. A KIND-B edit still edits the frame
    whose number is one LESS than its own (frame007 edits frame006). NEVER
    name by finish order, timestamp, or job_id.
- **IMAGE REVIEW — after every frame is terminal:** interactive mode calls
  `show_generation_by_ids` with the exact final frame ledger, split into
  consecutive display groups of at most 24 because dense Picture Stories
  normally exceed one widget, asks whether to assemble the final video, and
  ends the turn. There is no video generation or video review in Picture Story.
  Auto/headless runs continue directly to Phase 6 without the list.
- **Phase 6 — `${HF_WORKFLOWS}/faceless-channel-video/scripts/finish_video.sh --stills --frames-file frames.txt --narration <narration-url>` in `sandbox_exec`** (internally
  `${HF_WORKFLOWS}/faceless-channel-video/scripts/assemble_slides.sh`; NOT
  assemble_final.sh): the ONE continuous narration is laid over the whole cut;
  the manifest is FRAMES with per-frame durations (from the Whisper timeline),
  **one per line in STRICT timeline order: `frameNNN.png <seconds>`, ascending
  by NNN** (`frame001.png 0.9` / `frame002.png 1.1` / …). Build it by looping
  the numbered timeline 1..N — never by `ls` (which sorts unpredictably) and
  never in job-finish order. `--blocks N` = the frame count (REQUIRED). The
  script asserts: count, **frame numbers strictly ascending with no gaps
  (frame001,002,… — a jumble or a missing number hard-fails)**, per-frame
  ASPECT (a wrong-aspect image = an asset leaked into the frames = hard fail),
  **MAX HOLD — no frame on screen longer than 2.5s (grammar targets ~1s); split
  it**, the sum of durations ≈ the narration length (±1.5s), 1080p-class cap,
  the narration is present (not silent), full decode, and the LEVEL LAW (narration 1.0; optional music bed
  0.10 generic / 0.05 kids, DUCKED under the voice; NO clip SFX in this
  direction — a quiet bed is RECOMMENDED: kids-tone stories follow the Kids
  default-bed rule, others take a user file or explicit ask; never blocking).
- **Phase 7 — subtitles:** invoke the **`subtitles` skill** on the assembled cut
  (pass `script_manifest.json` as the authored wording; look = `clean` by
  default, `paper` for storybook tones). Never hand-time or hand-burn captions;
  if the skill reports Whisper unavailable, deliver unsubbed and say so.
- The assembled cut is the final video deliverable. For dispatched jobs, continue
  to Phase 8 reporting.

## What does NOT apply here

10s windows, 3/4-cut templates, {MOTION} tokens, freeze/tail probes, omni
retry specifics, impact beats. Everything else (golden rules on models,
voice lock, palette lock, no on-screen text, scripts-only assembly, no
invented progress) applies in full.
