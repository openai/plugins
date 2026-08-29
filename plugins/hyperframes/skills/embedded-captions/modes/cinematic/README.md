# Cinematic mode (pure embed) — one engine, six DNAs

> Cinematic mode compiles **[../../dna/](../../dna/README.md)** through
> **[engine.html](engine.html)** (`make-composition.cjs`). The old per-template HTML
> shells are retired — `cinematic-cream` maps to `dna: "cream"` automatically; the other
> archived templates (memory-wall / champion / portrait-header, in [\_archive/](_archive/))
> remain as design references only.

Use this mode for pure-embed asks (no rail): brand film, hype, social reel, showcase.
The **DNA** locks the visual language (type, palette scheme, blend, motion grammar, hero
three-act); **safe-zones v2** parameterizes it to the scene (sampled accent, light-
direction contact shadow, depth-match blur); **the agent decides layout only** (planes,
blocks, per-line typography within the DNA).

## Workflow

1. `bash scripts/prepare.sh <project>` → matte ∥ transcript ∥ envelope → safe-zones v2
2. Pick a DNA ([../../dna/README.md](../../dna/README.md)): bright hero band → `ink`,
   else by register (cream / editorial / keynote / documentary / loud). Recommend, let
   the user pick.
3. Author `<project>/cinematic.json` — `"dna": "<name>"` + thought-blocks (schema:
   `scripts/make-cinematic.cjs` header)
4. `node scripts/make-cinematic.cjs <project>` → plan.json → engine-compiled index.html
5. `node scripts/preview-frames.cjs <project>` → § Visual QA (failure checks + the 5
   positive checks in [../../references/reference-bar.md](../../references/reference-bar.md))
6. `bash scripts/render-and-composite.sh <project>` → gates → final.mp4

## What the engine generates (never author these)

- word timings from the transcript; accumulate-within-block / page-flip-between-blocks
- the hero hand-off + **three-act orchestration** (dim → RMS-coupled per-letter entrance
  → breathe + glow), per the DNA's `hero` block
- scene tokens: `--accent` (sampled), contact shadow, depth blur
- reading order, re-slot from measured heights, hero size/collision post-pass

## What you DON'T do

- Override `.cap` color / blend / shadow / filter / motion curves — that's the DNA.
  Scene fights the look → pick a different DNA (bright → `ink`), never recolor.
- Hand-position the hero into a clean margin (it belongs ON the subject, ~30–55%
  occluded — safe-zones `heroBands.best`).
- Add full-frame grades/textures over the footage (hard rule: the video ships untouched).

## Adding a DNA

`dna/<name>.json` — copy one, change the voice (see [../../dna/README.md](../../dna/README.md)
§ Adding). The engine consumes it with no code change. A DNA must be a distinct voice
with a reason to exist, not a recolor.
