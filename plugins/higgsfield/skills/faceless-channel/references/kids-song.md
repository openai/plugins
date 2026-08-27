# kids-song.md — SONG MODE: the Kids music video

A Kids-only sub-direction: instead of a narrated explainer, the run produces a
MUSIC VIDEO — a real SUNG children's song (verses + repeating chorus) with the
video choreographed to it. **The song is generated FIRST; the video blocks are
then staged TO the song; assembly lays the one continuous song track over the
whole cut.**

## When SONG MODE turns on

- **The duration question (Round 3) on KIDS runs** (Kids channel, or any run in
  a Kids-catalog style) offers, alongside 1/2/3 min: **"Music video — a real
  sung song (1 or 2 min)"**. Picking it locks SONG MODE.
- Direct asks lock it from the prompt: "kids song", "nursery song video",
  "sing-along", "music video for kids/toddlers" (any language).
- **Kids-catalog styles ONLY** (Studio 3D / Pastel Flat 2D / Colorful 3D /
  Hand-drawn Ink / Poster Vector, or Fluffy Toy). A non-Kids style ask in SONG
  MODE → map to the closest Kids style and confirm in one line.

## What changes vs the normal Kids run

- **No narrator**: the song IS the voice. SKIP the voice widget (Round 4),
  skip `voice.lock` — rules 15/16/17 (per-block lines) do not apply; the audio
  is ONE continuous track.
- **No sonilo bed**: the song IS the music. Never add a second music layer.
- **Subtitles are not offered in SONG MODE v1** (Whisper on singing is
  unreliable); if the user insists, say lyrics captions aren't supported yet.
- Everything else holds: Kids key flow for the style, asset roster, 4-cut
  blocks, interplay staging, retry ladder, scripts-only assembly, no lip-sync.

## Pipeline order (SONG FIRST)

1. **Intake** as usual (type/style/topic/duration; duration = 1 or 2 min →
   target 6 or 12 blocks).
2. **Write the song** (lyrics + structure, template below) — lyrics in the
   USER'S language, themed on the topic, starring the main character.
3. **Generate the SONG** — `seed_audio`, **prompt-only: NO `voice_id`, NO
   `voice_type`** (the singing voice is described inside the prompt). Use a
   one-request `generate_audio_batch` call and wait with `jobs_wait`.
   `ffprobe` the result: duration must be within ±3s of the target (60/120s) —
   off-length → regenerate the song (tested: the template lands exactly on
   target). **Budget cap: max 3 song attempts**, then stop and surface (same
   spirit as the clip retry ladder — never burn credits in a loop). After a
   passing song, interactive mode calls `show_generation_by_ids` with its exact
   final `{index, job_id}`, asks whether to continue to images, and ends the turn.
4. **Style key + asset roster** (Phases 1–2, unchanged; start only after the
   song checkpoint). Roster = the MAIN CHARACTER + friends the lyrics name
   (birdies, bunny, puppy...), 2–3 locations (meadow, garden), prop = the
   through-object if the lyrics have one.
5. **Block plan mapped to the song timeline** (Phase 3): N = duration/10.
   Use the template's nominal map — 2 min / 12 blocks:
   B1 intro + verse 1 opens · B2 verse 1 · B3–B4 CHORUS #1 · B5–B6 verse 2 ·
   B7–B8 CHORUS #2 · B9–B10 verse 3 · B11–B12 FINAL CHORUS (fullest).
   (1 min / 6 blocks: B1 intro+verse · B2–B3 chorus · B4 verse · B5–B6 final
   chorus.) A few seconds of drift between render and plan is fine — the
   staging reads by vibe, not frame-sync.
   - **Verse blocks = story beats:** SHOW WHAT THE LYRICS NAME (the line sings
     birdies → birdies on screen; bunny hops → bunny hops).
   - **Chorus blocks = the SIGNATURE DANCE, repeated:** same location, main
     character + friends doing the same recognizable dance staging every
     chorus, escalating each time (more friends, more props, fuller frame on
     the final). The repetition IS the hook.
   - Characters DANCE, clap, jump, spin, sway ON THE BEAT — gesture only,
     mouths never articulate words (rule 7: no lip-sync; humming smiles are
     fine, articulated singing mouths are not).
   - Kids 4-cut pattern per block, order varied; every cut an action.
6. **Generate the 12 (or 6) blocks** (Phase 4 as usual,
   `generate_video_batch` groups of at most six + `jobs_wait`): prompts
   carry the block's lyric line meaning as choreography + "characters dance to
   an upbeat children's song, moving on a steady beat"; AUDIO line stays
   diegetic-only (claps, hops — the song is added in post). After all blocks
   complete, interactive mode calls `show_generation_by_ids` with the exact
   final block ledger, asks whether to assemble, and ends the turn.
7. **Assemble with `--song`** (Phase 6):
   ```
   sandbox_exec({
     background:true,
     command:"bash ${HF_WORKFLOWS}/faceless-channel-video/scripts/assemble_final.sh --out work/output/final.mp4 --blocks N --manifest clips.txt --song song.wav"
   })
   ```
   Manifest lines = ONE clip per line (no voice files). The script lays the
   song at 1.0 over the whole cut, keeps clip SFX barely-there (0.06 default
   in song mode), asserts song-vs-video length (±3s), N×10s duration,
   narration-in-every-window (the song), full decode, poster + sidecar
   (`"song":true`).
8. Deliver ONE `final.mp4`. For dispatched jobs, continue to Phase 8 reporting
   (billing `block_count` = N).

## The SONG PROMPT template (≤2048 chars — HARD LIMIT, count before sending)

Two proven moods; pick by topic energy (or the user's ask):

- **GENTLE** (lullaby-ish walks, nature, bedtime): C major, **100 BPM**, soft
  4/4; ukulele + acoustic guitar, glockenspiel, gentle bass, soft flute, light
  chorus handclaps; meadow ambience touches.
- **DANCE-ALONG** (party, exercise, action topics): G major, **112 BPM**,
  claps on every second beat, bouncy plucked ukulele + bass locked to the
  kick, marimba + sparkle bells; chorus packed with ACTION WORDS (clap, stomp,
  jump, spin).

Skeleton (fill {}, keep every law):

> A full {1|2}-minute children's {song|dance-along song}, SUNG by a warm
> bright {gentle|cheerful, energetic} female singer with a smile in her voice
> - a real melodic song with verses and a repeating chorus on a clear singable
> tune, not narration. THE BEAT IS STEADY AND CONSTANT from the first second
> to the last: {100|112} BPM, simple 4/4, NO tempo changes, NO slowdowns, NO
> pauses between sections. Every lyric line has 8 syllables in steady trochaic
> meter (stress on 1,3,5,7), sung one syllable per beat, and EVERY line starts
> exactly on beat one of its bar; each line is one 4-bar phrase. Melody:
> simple {sweet|bouncy} nursery tune in {C|G} major, small steps within one
> octave, verse lower and playful, chorus a little higher and brighter.
> Instruments: {mood set from above}; clean warm mix, voice clearly in front,
> everything locked to the same steady beat. Structure with NO gaps: 4s
> instrumental intro, Verse 1, Chorus, Verse 2, Chorus, Verse 3, Chorus
> (final, fuller, extra claps and bells), 4s outro on {bells + a happy
> character sound}.
> Verse 1: "{4 lines, 8 syllables each}" · Chorus: "{4 lines, catchy, action
> words, repeats verbatim}" · Verse 2 · Chorus: (repeat) · Verse 3 · Chorus:
> (repeat, final, fuller)
> Delivery: {soft and melodic | energetic but sweet}, perfectly in tune, every
> syllable landing right on the steady beat; innocent and age-appropriate for
> toddlers. Total length approximately {1|2} minutes.

**Laws learned in testing (violating these produced beatless mush):**
- ONE constant tempo. Never write a bridge/slow-down/speed-up — dynamics come
  ONLY from orchestration (the final chorus gets fuller: extra claps, bells,
  doubled melody). Tempo-change words are BANNED from the prompt.
- Keep the meter machinery verbatim: 8-syllable trochaic lines, one syllable
  per beat, line starts on beat one, 4-bar phrases — this skeleton is what
  holds the tune together.
- No groove jargon ("four-on-the-floor", "syncopation", "drop") — describe
  claps and instruments plainly.
- Chorus text repeats VERBATIM every time (that's the sing-along).
- Lyrics: concrete, visual, age-appropriate; the main character named; action
  words the video can stage. 1-minute songs: 2 verses + 2 choruses.
- Prompt ≤2048 chars TOTAL — count it; trim instrument adjectives first,
  never the meter laws or lyrics.
