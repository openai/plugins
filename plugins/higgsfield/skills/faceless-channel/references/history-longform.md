# history-longform.md — the LONG-FORM History documentary (10+ minutes)

History's SECOND dedicated direction: a full YouTube-length documentary — one
era, one campaign, one reign told end-to-end (think "the winter that rebuilt
an army", "the reign of a king from coronation to deathbed"). **Minimum 10
minutes (N ≥ 60 blocks); offer 10 / 15 / 20 min (+ Other).**

## Warn BEFORE starting (mandatory, in plain user language)

1. **Time & cost:** a 10-minute run is 60+ clips + 60+ voice takes + a large
   asset roster — generation takes a long time (often hours) and a
   proportionally large credit budget. Say this at intake, before Phase 1.
2. **Heavy run:** this preset is the heaviest thing in the skill. If the run
   visibly struggles (planning falls apart, repeated gate failures), tell the
   user this format may need a more capable agent mode and suggest retrying
   there — do not grind a failing run to the end. (Being verified — the note
   stays until long-form is proven on the standard agent.)

## Style — Watercolor Chronicle (v1; a realism variant may come later — do NOT improvise it)

**Intake one-liner (VERBATIM):** "Watercolor Chronicle — hand-painted
watercolor washes with fine ink sketch lines, muted period palette, soft paper
texture; a storybook documentary look."

### STYLE FORMULA (§0 form — paste byte-identical everywhere)

> hand-painted watercolor and ink documentary illustration: loose expressive
> watercolor washes over fine confident ink sketch linework with visible pen
> strokes, muted restrained period palette with sepia-leaning warmth, soft
> cotton-paper texture with washes bleeding at the edges, unfinished sketch
> edges fading into blank paper at the frame borders, period-accurate costume
> and architecture, painterly directional light with soft shadows, subtle
> paper grain, gentle painterly motion — washes breathing, lines alive,
> never mechanical — non-photorealistic, illustrated, no live-action.

**{MOTION} slot:** painterly-flat — use `gentle painterly motion, washes
breathing and lines alive, subtle parallax between painted planes`; KEEP `3D
render` in the NEGATIVE.

**PALETTE LOCK line:** `muted period watercolor palette of the reference
images with sepia-leaning warmth — no saturated modern colors, no neon, no
gradients outside the washes`.

In-clip text: NONE (standard rule; era titles and dates are carried by the VO
and the burned subtitles if enabled).

## Structure — the documentary skeleton (this is the product)

Model the script on the reference-grade YouTube history documentary:

1. **COLD OPEN, in medias res (blocks 1–2):** drop the viewer into the most
   dramatic minute of the story — mid-crisis, no setup ("He rode toward the
   gunfire expecting victory; he found his own army streaming back").
2. **THE REWIND (block 3):** one explicit pivot line — "to understand how he
   ended up on that road, you have to go back six months" — then chronology.
3. **CHAPTERS (the body):** 5–8 chronological chapters of 8–14 blocks each
   (~1.5–2.5 min). Every chapter has its OWN mini-arc (setup → pressure →
   turn) and its own through-line beat; chapters end on a hook that hands
   over to the next ("That answer was coming faster than anyone expected").
4. **HUMAN VIGNETTE (≥1 per chapter):** one zoomed-in human story per chapter
   — the drillmaster swearing in three languages, the water carrier at the
   guns — concrete, named where history names them, honest where it doesn't
   ("whether every detail is literal truth or a composite…").
5. **HONEST UNCERTAINTY:** where historians disagree, SAY SO in one line
   ("what happened next has been debated for two hundred years") — it builds
   trust and is non-negotiable for factual integrity.
6. **THE MEANING (last chapter):** why it mattered — the before/after
   contrast stated plainly ("the army that left was not the army that
   arrived").
7. **OUTRO + CTA (final block):** the ONE place the narrator may address the
   channel: subscribe / comment with the next topic / like. One block, warm
   and brief; characters never gesture at UI elements (no on-screen buttons —
   the words carry it).

## ERA MAP — the asset math (do this BEFORE Phase 2, show it at OUTLINE LOCK)

(Style-dependent depth: Watercolor Chronicle and Paper Diorama use the FULL
map below. **Mannequin collapses it to at most child/adult per character** —
no facial aging, no costume eras exist in that style; see
`style-mannequin.md`.)

Long history spans YEARS: people age, children grow, buildings burn. A single
character sheet per person WILL drift. Build the ERA MAP first:

1. Split the story into ERAS aligned with chapters (e.g. `1509-1515 young
   king`, `1530s break with Rome`, `1540s old age`).
2. For every recurring character, list the eras they appear in and WHAT
   CHANGES: age, build, hair, dress, status markers. **One character asset
   PER ERA in which they appear** — same face structure and recognizable
   features (the identity invariants, stated verbatim in every variant's
   prompt), plus the era's changes ("the same man, now in his fifties:
   heavier, grey-streaked beard, richer robes").
   **IDENTITY CHAIN (mandatory):** the FIRST incarnation is generated from
   the style anchor + formula as usual; **every LATER era variant MUST attach
   the first incarnation's image as a reference** (`medias` =
   [style anchor, base variant job_id], role `image`) with the
   prompt framed as "the SAME person as in the reference, now {era changes}"
   — never generate an aged version from the style ref alone (that is a new
   stranger in the same clothes). For gradual change across 3+ eras, also
   attach the immediately previous era's variant alongside the base.
3. Name variants explicitly: `henry_young`, `henry_old`, `anne_1530s` — and
   in every block use ONLY the variant matching that block's era. A young
   king in an old-age chapter is a continuity bug, not a style choice.
4. Locations get era variants too when the story changes them (the palace
   before/after the fire; the camp in winter vs spring). Otherwise locations
   are REUSED chapter to chapter — budget ~1–2 locations + coverage per
   chapter, and rotate back to earlier sets when the story returns there.
5. Sum the roster BEFORE generating: characters×eras + locations + coverage +
   props (through-line included). A 10-min run typically lands at 25–40
   assets — show the count and the ERA MAP at OUTLINE LOCK so the user sees
   the scale before credits are spent. Respect the ≤7 refs per block limit
   when assigning variants to blocks.

## Visual variety law (anti-repetition — long-form lives or dies by this)

Sixty blocks of the same three gestures reads as a screensaver. Hard rules:

- **SHOW WHAT THE LINE NAMES.** Every block's shots stage the CONCRETE nouns
  of its own VO line: the line says spices — spices are on screen (sacks,
  caravans, scales), not another wax seal. A block whose visuals could belong
  to any other line is a rewrite.
- **MOTIF BUDGET.** Keep a MOTIF LEDGER while writing the script: every
  recurring action beat (stamp slams, seal presses, document signings, troop
  marches) is logged; the same motif appears at most ONCE per chapter and ~3
  times per film (through-line beats exempt — they're SUPPOSED to recur, but
  each recurrence shows a NEW state). Two blocks may never share the same
  action beat back to back.
- **MANDATORY interleaves, because this is History:** every chapter contains
  at least ONE map beat (routes drawing, regions filling, pins pulsing —
  where did this happen) and at least ONE quantity beat whenever the VO cites
  money / resources / armies / years — shown as visual comparison (coin
  stacks growing, ship rows multiplying, a granary emptying), numerals still
  banned on screen, the VO carries the figures. Watercolor renders maps and
  charts beautifully — painted map washes, inked route lines, stacked painted
  coins.
- **Rotate the device class between blocks:** scene-with-characters → map →
  object/quantity → scene → vignette… never three of the same class in a row.

## Production notes (long-form deltas from the standard pipeline)

- **TWO-STAGE SCRIPT LOCK:** first show the CHAPTER OUTLINE (chapters + eras
  + cast/ERA MAP + through-line + vignette list) as an OUTLINE LOCK
  notification and proceed; then write and show the full block script
  (SCRIPT LOCK, standard notification-only rules). Neither stage waits for
  approval.
- **Research is mandatory and deeper:** per chapter hold 4–6 verified
  concretes (dates, numbers, names, places), cross-checked; keep the Sources
  list for delivery. Honest-uncertainty lines where sources conflict.
- **Generate chapter by chapter** (`generate_video_batch` groups of at most
  six + `jobs_wait` inside a chapter): collect a chapter's blocks, then move
  on — a failed block only stalls its chapter.
  Assembly stays ONE `assemble_final.sh` call at the very end with all N
  pairs (the command line is long; that is fine).
- **Through-line still rules:** one physical object/process spanning the
  whole film, escalating per chapter, resolved in the meaning chapter (the
  bloody footprints → the disciplined column; the fuse → the keg).
- **Music bed:** this format WANTS a quiet bed (the reference runs one
  throughout). Policy unchanged: ask the user for a file at intake (or
  proceed without) — never block on it; LEVEL LAW keeps it at 0.10.
- **Voice:** documentary narrator — measured but warm; the standard voice
  widget flow, one locked voice for all 60+ takes; the timecode line format
  and the exact 30–34-word density apply to every block including chapter openers.
