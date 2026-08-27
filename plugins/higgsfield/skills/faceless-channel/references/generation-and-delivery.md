# Generation and delivery

This reference contains the complete Phase 4–8 contract. The caller must resolve
the helper-root variables defined by `faceless-channel` before following any
cross-skill path below.

## Contents

- Block video generation and review
- Narration through `narrator`
- Native assembly and QC
- Subtitles through `subtitles`
- Platform reporting and failure handling

### Phase 4 — Generate blocks (one job per block, submitted in batches)
For each block 1..N, create one request for `generate_video_batch`:
`model:"gemini_omni"`, `duration:10`, `resolution:"720p"`,
`aspect_ratio`: chosen aspect, `medias` = location →
characters → props using the canonical tool role `image`. **HARD LIMIT: at most 7 image
references
per call** — the model rejects 8+ with `"at most 7 image_references are allowed"`. Send
ONLY the assets that appear in THIS block; if a block still exceeds 7, trim in reverse
priority (extra props first, then the spare coverage view) — NEVER drop the block's
location or an on-screen character. If the response is a preset recommendation
instead of a job → resubmit the same call with `declined_preset_id` from it (rule 5).
The prompt contains the
FIVE timed hard-cut shots (`SHOT 1 0.0–2.0s … HARD CUT … SHOT 2 2.0–4.0s … HARD CUT
… SHOT 5 8.0–10.0s`; Kids: the 4-cut pattern) + "characters only emote, do NOT talk"
+ diegetic-audio-only + the NEGATIVE line. Full template →
`${FACELESS_STYLES_DIR}/references/prompts.md §3`. Submit sequential groups of at most six using the
block number as `index`, then wait each group with `jobs_wait`. Apply the RETRY
LADDER on `nsfw`/`failed`, resubmitting only failed block indices.
**A `completed` block is FINAL.** Never pause the run to "re-taste" a finished block:
regenerate ONLY on `failed`/`nsfw` (RETRY LADDER) or on a NAMED gate/QC violation (style
drift vs the assets, static head/tail WARN from the assembler, wrong aspect) — and only
AFTER the whole batch is collected. Do not stop mid-batch to redo a block on preference;
do not resubmit blocks the checklist has no complaint about.
After all N blocks are complete, interactive mode calls
`show_generation_by_ids` with the exact final `{index, job_id}` block ledger
(one call for up to 24 blocks; consecutive groups of at most 24 only when
larger), renders the VIDEO review question, and ends the turn; enter the route's
next stage only after `Continue`. Auto/headless mode proceeds immediately
without the list.
**GATE 4 (completeness):** all N blocks are `completed` and downloaded (`block01..N.mp4`),
one per script block, no gaps. Never proceed with a missing block.

### Phase 5 — Voiceover — INVOKE THE `narrator` SKILL (do not hand-roll TTS)
Voice work is NOT done inline. **Invoke the `narrator` skill** and hand it the job:

- the N block lines, numbered, in order (you wrote them in Phase 3);
- the LOCKED voice pair from `voice.lock` (written at GATE 0) — `voice_id` +
  `voice_type`, the same pair for the whole video;
- the timing target: **9.4–9.8s of measured speech for every full 10s block**;
- the delivery direction: ONE `{DELIVERY}` phrase for the whole video (channel +
  topic — see `${FACELESS_FLOW_DIR}/references/vo_and_captions.md`), plus optional per-block mood;
- the density target: **30–34 dense words** per full-block line; Kids use **34–38**
  with an EXCITED delivery cue and carefully bounded performed brackets;
- for a SHORT final block (non-multiple-of-10 duration): that block's own window.

The narrator skill owns the mechanics and the guarantees: the timecode prompt
format that paces the TTS, one voice everywhere (it re-reads the locked pair before
every call), the speech-length gate measured on SPEECH not file length, rewriting a
line denser/shorter and regenerating when it misses the window (NEVER `atempo`,
never `speech_rate`), no internal pause ≥0.8s, RETRY SET LAW (only failing lines
are regenerated, passing takes are immutable), and a per-line attempt budget.

It returns completed audio job IDs plus result URLs and, when local download is
available, `voice01.wav … voiceNN.wav`, measured speech length and final wording.
Keep final wording synchronized with `script_manifest.json`.

The narrator MUST use `generate_audio_batch` + `jobs_wait` per its own contract
and must not render progress widgets. If this run requires a music bed, generate
it now through the same headless audio batch contract (before review), not during
assembly. After every take and due bed passes its bounded checks, interactive
mode calls `show_generation_by_ids` with the exact final audio ledger (give a
due bed its own unique stage index), renders the AUDIO review question, and ends
the turn; enter assembly only after `Continue`.
Auto/headless mode proceeds immediately without the list.

**GATE 5:** N completed voice jobs, ONE voice throughout; when local files are
measurable, verify the 9.4–9.8s target and no internal pause ≥0.8s. After the
bounded attempt budget, keep the closest completed non-overrunning take and record
the miss rather than looping.

**Picture Story voice = ONE continuous narration, then Whisper (NOT per-beat takes).**
Invoke `narrator` in its CONTINUOUS mode (it handles the 2048-char chunking and the
lossless join) to get one `narration.wav`, then the frame timeline comes from Whisper
word timestamps per `${FACELESS_MODES_DIR}/references/picture-flow.md` Phase 5 / 5b: segments every
~0.7–1.2s, and at each framing change; no frame
segment >1.5s). Those Whisper timings set every frame's duration in Phase 6.
NOTE (feedback to backend): `validate_picture_story_audio.py` is the OLD per-beat audio
gate (rejects takes >3.0s, expects one take per beat) — it does NOT apply to a single
continuous narration and is NOT run in this model. It needs a rewrite to validate the
frame timeline (sum of frame durations ≈ narration length, max-hold ≤2.5s) — the
assembler's `--audio` mode already asserts exactly that, so the check is covered until
the validator is updated.

### Phase 6 — Assemble in the Higgsfield sandbox → ONE final video

**Canonical ordinary ChatGPT motion-video route:**

1. Keep every completed video and audio job's result URL in block order.
2. Before starting the sandbox assembly, call:
   ```
   media_upload({filename:"final.mp4", content_type:"video/mp4"})
   ```
   Keep the returned `uploads[0].upload_url` and `uploads[0].media_id`. This is
   the sandbox-output route. Never pass `work/output/final.mp4` to
   `media_upload_and_confirm`; that tool accepts only ChatGPT attachments.
3. In one `sandbox_exec` background command, write ordered `clips.txt` and
   `voices.txt` URL lists plus `script_manifest.json`, run the preinstalled
   wrapper exactly once, verify the MP4, and PUT it before the ephemeral command
   exits:
   ```
   sandbox_exec({
     background:true,
     command:"set -e; printf '%s\\n' '<clip01 url>' '<clip02 url>' > clips.txt; " +
             "printf '%s\\n' '<voice01 url>' '<voice02 url>' > voices.txt; " +
             "bash ${HF_WORKFLOWS}/faceless-channel-video/scripts/finish_video.sh " +
             "--blocks N --clips-file clips.txt --voices-file voices.txt " +
             "--script script_manifest.json --subs clean; " +
             "test -s work/output/final.mp4; " +
             "code=$(curl -sS -o /dev/null -w '%{http_code}' -X PUT " +
             "--upload-file work/output/final.mp4 '<upload_url>'); " +
             "echo \"PUT -> $code\"; [ \"$code\" = \"200\" ]"
   })
   ```
   Omit `--subs` when captions are off; replace `clean` with `paper` or `bold`
   when selected. Add `--music URL|FILE` and `--stepped 12` only when applicable.
   Poll its returned `log_path` immediately through `sandbox_exec`. Do not stop
   until the process is terminal and the log contains `PUT -> 200`.
4. The wrapper downloads `block01.mp4 … blockNN.mp4` and
   `voice01.wav … voiceNN.wav`, writes `pairs.txt` in strict numeric order, runs
   the canonical assembler, optionally captions, verifies every output, and the
   same command uploads the final MP4.
5. Only after `PUT -> 200`, call:
   ```
   media_confirm({type:"video", media_id:"<media_id>"})
   ```
   Deliver its confirmed hosted URL. Preserve the generated
   `final_poster.jpg` and `final.mp4.assembly.json` as assembly receipts. If the
   PUT fails, do not confirm: create a fresh upload slot and rerun the same
   idempotent finish-and-PUT command.

Do not call `explainer_video` for ordinary stitching, even when it appears in a tool
registry: sandbox FFmpeg assembly is self-contained and does not need a remote
generation record. Do not call `job_display` for a sandbox file or uploaded-media id.
The confirmed hosted MP4 is the deliverable.

**Canonical motion / Picture Story scripts under the wrapper:** run
`bash ${HF_WORKFLOWS}/faceless-channel-video/scripts/assemble_final.sh` once
for motion blocks or
`bash ${HF_WORKFLOWS}/faceless-channel-video/scripts/assemble_slides.sh` once
for Picture Story. Every motion run
writes a MANIFEST first (one
`blockNN.mp4 voiceNN.wav` pair per line, in order) and passes the expected block
count — `--blocks N` is REQUIRED (the script refuses to start without it) and a
missing, extra, or number-mismatched pair is a hard fail:
```
sandbox_exec({
  background:true,
  command:"bash ${HF_WORKFLOWS}/faceless-channel-video/scripts/assemble_final.sh --out work/output/final.mp4 --blocks N --manifest pairs.txt"
})
```
Add `--music bed.mp3` and `--stepped 12` only when applicable.
(**pass `--stepped 12` for Fairy Tale & Myth / any Cinematic Storybook run — the
on-twos cadence**; positional pairs remain for ad-hoc debugging only. Subtitles are
NOT part of assembly any more — Phase 7 invokes the `subtitles` skill on the
assembled file.)
**NO chunked assembly** — never split a long run into "chunks of 10" with your own
ffmpeg, never build the audio track separately, never re-mux by hand: one script call
does all N blocks, however many there are. **NO invented progress reports:** the only
legitimate assembly status is the script's own stderr (per-block lines + asserts) —
paste it; fabricating "chunk 6 assembling, ~7 minutes remaining" tables while nothing
runs is lying to the user and grounds for a failed run.
Run the assembler with `background:true`, then poll its returned log immediately
with the next `sandbox_exec` call. If it is demonstrably alive, keep polling that
process; never launch a duplicate assembly.
The script does everything and guarantees the hard parts: fixed **N×10s** length, each
voice CENTERED in its 10s block, NO atempo, NO leading freeze, ONE output file, + optional
low music bed and `loudnorm -16 LUFS`. Diegetic SFX already live in the clips. Music bed
when the user supplied a file or explicitly asked — PLUS any KIDS-LOOK run (the Kids
channel, or ANY channel in a Kids-catalog style) AND every FAIRY TALE & MYTH /
Cinematic Storybook run, where a wordless bed is ON BY DEFAULT. No file needed: a due
bed was GENERATED before the AUDIO review with `sonilo_music` at the VIDEO's exact
duration (one request covers
up to 600s — verified; longer runs join ≤600s parts into one file — mechanism in
`${FACELESS_STYLES_DIR}/references/kids-styles.md §Kids music bed`). **Mood by channel: Kids = playful/bouncy;
Fairy Tale & Myth = MYSTERIOUS-CALM dark-enchanted ambient** (never bouncy —
`${FACELESS_STYLES_DIR}/references/style-cinematic-storybook.md §Music`). user file → generated bed →
generation failed = ship without + say so in one line. The generic audio router accepts
`sonilo_music` even though its default description focuses on speech; never substitute
`seed_audio` for music. **Default-bed level: `--music-vol
0.05` for Kids, `0.09` for Fairy Tale & Myth** (the narration must never fight the bed)
— and the assembler additionally DUCKS the bed under speech (sidechain keyed by the voice). Never block delivery on a bed, never
synthesize music with the speech model. Do NOT split into parts, do NOT re-encode by
hand, do NOT trim to the audio.
Besides the MP4 the script writes two platform artifacts next to it — keep both:
`final_poster.jpg` (the result thumbnail) and `final.mp4.assembly.json` (the machine-
readable ASSEMBLY SIDECAR: block count, per-block speech metrics, gates passed — the
proof the final went through the script; `assemble_slides.sh` writes the same pair).
**GATE 6:** exactly ONE `final.mp4`, duration = N×10s (±1s, the script asserts this),
narration present in EVERY window (the script asserts this too — a "silent second half"
cannot pass), plays from frame 1 (no static head), one voice, SFX under the voice (music
only if provided), poster + assembly sidecar present next to the MP4.

**Picture Story assembly command** (frame-by-frame `--audio` mode; `--blocks` = the
FRAME count, not the billing count):
```
sandbox_exec({
  background:true,
  command:"bash ${HF_WORKFLOWS}/faceless-channel-video/scripts/assemble_slides.sh --out work/output/final.mp4 --audio work/voices/narration.wav --blocks {FRAME_COUNT} --manifest frames.txt"
})
```
Add `--music bed.mp3` only when applicable.
`frames.txt` = one `frameNNN.png <seconds>` per line **in STRICT ascending timeline
order** (`frame001.png 0.9` / `frame002.png 1.1` / …), durations from the Whisper
timeline. Download every frame as `frameNNN.png` where NNN is its Phase-5b timeline
number (SPOKEN order — never job-finish/ls order), and build the manifest by looping
1..N. The one continuous narration is laid over the whole cut. The script asserts the
per-frame durations sum to the narration length (±1.5s), **frame numbers strictly
ascending with no gaps (a jumble hard-fails — the "assembled out of order" bug)**,
max-hold ≤2.5s/frame, **a DENSITY FLOOR
of `ceil(narration_sec/1.5)` frames (≈40 for a minute — a slideshow like 15 frames/min
hard-fails; generate the dense set in Phase 4, do not pad holds)**, aspect, 1080p cap,
narration present, full decode. Billing stays `BILLING_BLOCKS = ceil(REQUESTED_SECONDS/10)`
(NOT the frame count) — the sidecar records both `frames` and the billing blocks.
NOTE (feedback to backend): the old `--target-duration` per-beat total-duration gate is
replaced by the `--audio` sum-of-durations assert.

### Phase 7 — Subtitles — verify the `subtitles` result (only if subtitles = yes)
Captions are never hand-timed. After native Phase-6 assembly, invoke `subtitles` with:

- the assembled video (the Phase-6 `final.mp4`);
- `script_manifest.json` (or the line list) as the AUTHORED WORDING — Whisper is the
  word clock, the words come from the script, so names/numbers are spelled right;
- the LOOK: `clean` (default — slim white CAPS, tiny, bottom ~12%, no plate),
  `paper` (torn cream label, handwritten — fits fairytale/storybook looks) or
  `bold` (UGC ALL-CAPS with safe zones). Channel default: Fairy Tale & Myth →
  `paper`, everything else → `clean`, unless the user asked otherwise.

The skill owns: backend/Whisper word timestamps, the ≤3 words / ≤15 chars caption sizing,
authored-wording substitution, the three burners, per-language font coverage (it
auto-swaps a font that has no glyphs for the script instead of shipping blank
labels), the dependency install, and the "unavailable Whisper → deliver unsubbed and
say so" fallback. It returns the subbed video (replacing the deliverable) + the
`.srt`.

For this workflow the subtitle skill runs only through `sandbox_exec`, using
`${HF_WORKFLOWS}/faceless-channel-video/scripts/subtitles/`. Normally
`finish_video.sh --subs clean|paper|bold` performs this in the same Phase-6
sandbox job; Phase 7 verifies its receipts rather than launching a second local
pipeline.

**Non-negotiables that stay TRUE regardless of who asks:** timings come from
Whisper ONLY — even if the user says "time them from the script" (rule 8); captions
stay small and out of the way (rule 20); styling asks map to the skill's flags, and
anything that breaks readability is declined in one line.

Keep `final_poster.jpg` extracted from the CLEAN video (Phase 6 does this before
captions) — a result card must never show a random subtitle fragment.

**GATE 7:** one `final.mp4` with backend/Whisper-timed captions from the `subtitles`
skill, or an explicit note that captions were unavailable.

> **Whisper is needed ONLY for subtitles (Phase 7).** A/V sync is by construction
> (one centered narration line per block — Phase 5/6), so the video itself never needs Whisper. If
> subtitles are ON and Whisper is unavailable, deliver the video and tell the user
> captions need the Whisper-capable environment — do NOT ship guessed caption timings.

### Phase 8 — Report to the platform (platform-dispatched jobs only)

Skip this entirely for ordinary chats. Enter it only when
`report_faceless_video_output` is exposed by the dispatch environment. If a platform
brief requires reporting but the callback is absent, return
`REPORT_TOOL_UNAVAILABLE` to the dispatcher; never fabricate success. For a supported
platform job: **first pass FINAL QC — a
failing video must never be reported as a result.** Then:

1. **Finalize the two result manifests** (JSON files next to the MP4):
   - `script_manifest.json` — the locked, validator-passed script (for Picture Story,
     enrich the already Gate-3-validated file; never rewrite its phrases). `sources`
     contains absolute HTTP(S) research URLs only, never source titles. Picture Story
     beats additionally carry `frame_url` + `frame_job_id`; variations carry
     `reference_frame_url` + `reference_frame_job_id` equal to the immediately previous
     beat, preserving durable lineage after the sandbox is gone.
   - `asset_manifest.json` — the roster: `{assets:[{name, kind:
     character|location|prop|style_key, era?, url, job_id}]}`. Both `url` and `job_id`
     are mandatory for every newly generated entry. A legacy asset reused from Channel
     DNA may omit an unavailable historical job id only when it declares
     `reused_from_channel_dna:true`; its durable URL remains mandatory.
   - Do NOT add `generation_metrics` to `script_manifest.json`. Accurate elapsed time,
     recovery retries and tool counts belong to runtime telemetry, which the model
     cannot author reliably. The manifest validator rejects this field instead of
     accepting estimated metrics.
   Before upload, run:
   ```
   sandbox_exec({
     command:"python3 ${HF_WORKFLOWS}/faceless-channel-video/scripts/validate_result_manifests.py --script script_manifest.json --assets asset_manifest.json"
   })
   ```
   Exit code 1 blocks upload/report. Fix only the listed manifest fields; do not
   regenerate media merely to repair metadata.
   The assembler already wrote the third one — `final.mp4.assembly.json`.
2. **Upload the complete result set** in ONE upload call: the final MP4,
   `final_poster.jpg`, `script_manifest.json`, `asset_manifest.json`, and
   `final.mp4.assembly.json` — every file gets a public url. The assembly script MUST
   have produced the poster and sidecar; if either is missing, rerun the script (or
   report `ASSEMBLY_FAILED`). Never hand-roll a poster with ffmpeg.
   The report tool downloads and validates all three uploaded manifests before recording
   success. A noncanonical sidecar, a motion script that fails its word budget, or a
   Picture Story whose frame-by-frame assembly does not match the script is rejected.
3. **Build and verify the complete success payload BEFORE the first tool call.** It must
   already contain non-empty `url`, `thumbnail_url`, `script_manifest_url`,
   `asset_manifest_url`, `assembly_manifest_url`, positive `duration_seconds` and
   `requested_duration_seconds` (copied from immutable `REQUESTED_SECONDS`),
   `block_count`, `sources` (use `[]` when none), and the `channel_dna` object. If any
   upload URL is missing, do not call the report tool — finish the upload or report the
   appropriate terminal failure. A validation-rejected trial call is a contract bug.
   Then **call `report_faceless_video_output` exactly ONCE** with those fields inside
   the top-level `success` object. Its `url` is the MP4's public url (required), and
   `block_count` is `blocks` from the assembly sidecar. For Picture Story that field is
   derived from immutable `REQUESTED_SECONDS` (`BILLING_BLOCKS`), NOT from actual output
   duration and NOT from the beat count. Assert it equals the intake
   `BILLING_BLOCKS` before reporting.
   Also include
   `duration_seconds` (actual, from the sidecar), `thumbnail_url` (the uploaded poster),
   `requested_duration_seconds` (the original run-brief value),
   `script_manifest_url`, `asset_manifest_url`, `assembly_manifest_url`, `sources`
   (string list), and `channel_dna` (the object below). Never use
   `report_video_explainer_output` for this skill.
4. **Channel DNA** — always pass it to the report tool AND put it in
   `script_manifest.json` under `channel_dna`: `{channel_type, style:{name,
   preset_id?, style_key_urls, formula_file, palette_lock}, voice:{voice_id, voice_type,
   name}, aspect, subtitles, assets:[{name, kind, url}]}` — everything the next run
   needs to make video #2 look like the same channel.

**On unrecoverable failure** (retry ladder exhausted on a block, assembly assert failed,
no MP4): do NOT fabricate a url and do NOT report a partial file — call
`report_faceless_video_output` exactly once with the top-level `failure` object containing
`failure_code` and `failure_detail` (and no `success` branch). Failure codes:
`VOICE_RESOLVE_FAILED`, `STYLE_ANCHOR_FAILED`,
`ASSET_GEN_FAILED`, `CLIP_GEN_FAILED`, `AUDIO_GEN_FAILED`, `ASSEMBLY_FAILED`,
`QC_FAILED`, `UPLOAD_FAILED`, `BUDGET_CAP`. Subtitles failing is NOT a job failure —
deliver unsubbed and note it.

---
