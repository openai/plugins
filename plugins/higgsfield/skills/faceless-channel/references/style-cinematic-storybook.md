# House style — Cinematic Storybook (Fairy Tale / Myth)

**The Fairy Tale / Myth channel's default style** (published in the "Faceless channel
presets" catalog as the card **"Fairy Tale & Myth"**, id
`de5b38ca-9134-4987-9d7a-d5e9085f0480` — picking it locks this channel type): a
lush hand-painted 2D-animation-feature look — richly detailed semi-realistic
characters with expressive faces and ornate costumes, gothic and natural
fairytale settings, warm volumetric light against deep atmospheric shadow.
Reads instantly as "a beautiful animated legend" — for retellings of myths and
fairy tales (Greek, Slavic, European, world folklore).

**Intake one-liner (use VERBATIM as this option's / card's description — do not
improvise):** "Cinematic hand-painted storybook — lush 2D-animation fairytale
look, painterly light and deep shadow, ornate characters and enchanted
settings, told on twos like a classic cartoon."

## STYLE FORMULA (§0 form — paste byte-identical everywhere)

> cinematic hand-painted 2D animation, storybook fairytale look: soft painterly
> rendering with warm volumetric light and deep atmospheric shadows, richly
> detailed semi-realistic characters with expressive faces and ornate period
> costumes, gothic and natural enchanted settings, muted jewel-tone palette
> (deep burgundy, obsidian, forest green, dusk blue, candle gold), delicate
> linework under soft gradient shading, dramatic chiaroscuro lighting, dreamy
> enchanted mood, high-production 2D feature-film look, non-photorealistic, no
> film grain.

PALETTE LOCK: `muted jewel-tone palette of the reference images — deep
burgundy, obsidian, forest green, dusk blue, candle gold; warm key light
against deep shadow. No neon, no flat bright cartoon primaries.`

## {MOTION} slot — ANIMATE ON TWOS (this style's signature)

Fairy Tale / Myth is deliberately animated **"on twos" — ~12 drawings per
second, stepped**, like a classic hand-drawn cartoon. This both sells the
2D-animation feel and hides AI over-smoothness/morphing. Two layers, use BOTH:

1. **In every block prompt** put: `TRADITIONAL HAND-DRAWN 2D ANIMATION, animated
   ON TWOS (~12 drawings per second) — deliberate STEPPED / staggered motion
   with tiny holds between poses, snappy pose-to-pose keyframe animation, NOT
   smooth, NOT fluid interpolation, NOT slow-motion`; slow graceful dreamlike
   camera moves are fine. ADD to the NEGATIVE: `smooth motion, fluid
   interpolation, slow-motion, motion blur, 60fps look`. KEEP `3D render` in the
   NEGATIVE (this is 2D).
2. **In assembly** pass **`--stepped 12`** to `assemble_final.sh` — it re-times
   every block to update the image ~12×/sec (mathematically exact on-twos)
   while keeping the container fps and the audio untouched. The prompt sets the
   character of motion; `--stepped` guarantees the cadence. (Verified in test:
   prompt + `--stepped 12` together give the cleanest cartoon look.)

## Tone & voice

Enchanting STORYTELLER — hushed, warm, mysterious, unhurried and mythic; NOT
History's witty/sarcastic register, NO jokes. Cold-open still ≤8 words. Default
voice recommendation: **Arthur** (deep male storyteller) or **Callum**; a warm
female (**Remy**) also fits gentler tales. One voice locked as everywhere.

## Music — MANDATORY, mysterious & calm (default ON, like Kids)

A Fairy Tale / Myth video always ships WITH a music bed — generated per run with
`sonilo_music` at the video's exact duration (§ same mechanism as
`${FACELESS_STYLES_DIR}/references/kids-styles.md §Kids music bed`), but the MOOD is **dark-enchanted
ambient: mysterious, calm, hushed, dreamlike — soft sustained strings, distant
harp, faint music-box, low choir pad, a far-off bell; instrumental, no drums,
no vocals**. Ducked under the voice (`--music-vol 0.09`, sidechain). Never
bright or bouncy. User file always wins; generation failed → ship without + say so.

## Storybook-spread inserts (optional atmospheric blocks)

A block MAY be an illustrated BOOK SPREAD instead of a staged scene: an open
antique storybook whose two pages hold one continuous painted illustration in
gold vine borders (see the canon ref). Use sparingly — an opener, a chapter
turn, or the closing moral — for a "being read a tale" beat. Faint illegible
decorative script only, never readable text.

## Canon reference images (style donors — Kids-style flow)

Pass each authorized HTTPS URL directly as canonical `image` media (or upload local
files with `media_upload_and_confirm`) into ONE `seedream_v5_pro` style-key call with the FORMULA
(the user gets their own unique key, look-locked to the canon); the refs are
style donors only — take the render style, never the specific characters/scenes.
Live on the CMS ("Fairy Tale & Myth" card):
- https://cdn.higgsfield.ai/youtube_faceless_preset_image/d6c53fed-98a1-4c33-997f-949d4ac2bf74.webp
- https://cdn.higgsfield.ai/youtube_faceless_preset_image/7c7f56d2-f87e-4052-ac6d-a8bbba1a96cb.webp
- https://cdn.higgsfield.ai/youtube_faceless_preset_image/179930a1-f06d-4f65-877a-270969ec389e.webp

## NSFW / moderation notes (learned in testing)

The video model's NSFW filter trips on grim death imagery even in a painterly
fairytale. AVOID in prompts: `hooded figure / cloaked ferryman`, `souls of the
dead`, `corpses`, `river of the dead`, tight menacing shadow-claws, anything
reading as violence toward a person. Convey the dark/underworld mood through
ARCHITECTURE, LIGHT and NATURE instead — gateways, torches, mist, asphodel
flowers, ruins, moonlight (these passed first try). Keep characters clearly
adult; standard child-safety rules apply. Retry ladder as usual; if a grim beat
keeps failing, re-stage it as an empty atmospheric location.

## Everything else

Motion-video mechanics = the History channel: N×10s blocks, `gemini_omni`,
FIVE ~2s hard cuts per block (the on-twos cadence rides on top), 2–3 min
default (12–18 blocks), asset roster + style key, one continuous through-image,
`validate_motion_script.py` Gate 3. It is a look + tone + music
profile on the standard motion pipeline, not a new mechanic.
