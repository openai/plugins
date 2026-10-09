# Typographic moves — a palette, not a cage

`cinematic-cream` template locks DNA only (font-family, motion, color
palette defaults). It does NOT enforce slot structure. The agent writes
each caption group's typography from scratch via the plan.json `css`
field.

This doc is a **palette** of tried combinations — pick what fits the
scene, invent new ones, skip these if the content demands. These are
recommendations, not rules.

## Size vs text length — DO THIS BEFORE PICKING SIZE

Bigger is NOT better if the word doesn't fit the frame width. Every time
you pick a font-size, sanity-check against word length:

**Rough rule for Inter 900 uppercase at -0.03em tracking:**
`max_font_px ≈ frame_width / (longest_word_chars × 0.72)`

The 0.72 multiplier is intentionally conservative — it targets the text
filling ~90% of the frame width so there's a small side margin. If you
want edge-to-edge, drop to 0.65, but you lose a bit of safety margin.

720px portrait:

- 3-char word (15%): max ~330px (a single big number like "15%")
- 5-char word (TAKE): max ~200px
- 7-char word (AUGMENT / QUANTUM / MATTERS): max ~143px
- 10-char word (CREATIVITY): max ~100px
- 13-char word (UNPRECEDENTED): max ~77px

1920px landscape:

- 7-char word: max ~380px
- 10-char word: max ~267px

For italic/upright 500-700 it's slightly narrower — increase max by ~10%.

**If you want the word bigger than it fits:**

- Split into multiple words per group (natural wrap), OR
- Add explicit `<br>` between syllables, OR
- Drop letter-spacing to -0.05em, OR
- Accept that the matte will cut part of it (Vogue-cover embed effect —
  only works when the cut area is exactly where the subject is)

Never let the text OVERFLOW the frame edge — that's not cinematic, that's
just broken. Use the heuristic.

## Sizing discipline (frame-height-relative)

Portrait 9:16 (720×1290) and landscape 16:9 (1920×1080) have very
different comfort ranges. Use `calc(<pct> * var(--h))` for responsive:

| Feel                   | % of frame height | Example calc            |
| ---------------------- | ----------------- | ----------------------- |
| Whisper / label        | 4-6%              | `calc(0.05 * var(--h))` |
| Soft opener            | 6-9%              | `calc(0.07 * var(--h))` |
| Narrative body         | 9-14%             | `calc(0.11 * var(--h))` |
| Emphasis               | 14-22%            | `calc(0.18 * var(--h))` |
| Climax / monumental    | 22-35%            | `calc(0.28 * var(--h))` |
| Title-bigger-than-face | 40%+              | `calc(0.48 * var(--h))` |

Use absolute px only when a specific scale needs to look identical
across frame sizes (rare). Prefer `calc` + `var(--h)`.

## Named moves — pick per group

**Italic contemplative opener** (memory-wall cap-1 lineage):

```css
font-weight: 600;
font-style: italic;
letter-spacing: -0.01em;
font-size: calc(0.075 * var(--h));
```

**Italic continuation / dreamier continuation** (cap-2 lineage):

```css
font-weight: 500;
font-style: italic;
letter-spacing: -0.005em;
font-size: calc(0.065 * var(--h));
```

**Upright pivot / statement** (cap-3 lineage — "but suddenly"):

```css
font-weight: 700;
letter-spacing: -0.015em;
font-size: calc(0.07 * var(--h));
```

**Uppercase climax / monumental** (cap-4 lineage — "EVERYTHING IS SHARP AGAIN"):

```css
font-weight: 900;
text-transform: uppercase;
letter-spacing: -0.03em;
line-height: 0.95;
font-size: calc(0.18 * var(--h));
```

**Chapter card / full-frame Adam Curtis manifesto**:

```css
font-weight: 700;
text-transform: uppercase;
letter-spacing: -0.015em;
line-height: 0.9;
font-size: calc(0.14 * var(--h));
```

**News chyron / broadcast label** (small, locked):

```css
font-weight: 500;
letter-spacing: 0.02em;
font-size: calc(0.038 * var(--h));
```

**Tiny side note / caption-on-surface**:

```css
font-weight: 400;
font-style: italic;
font-size: calc(0.045 * var(--h));
```

**Vogue-masthead monumental**:

```css
font-weight: 900;
text-transform: uppercase;
letter-spacing: -0.04em;
line-height: 0.85;
font-size: calc(0.32 * var(--h));
```

## Narrative arcs (suggestions, not required)

**Poem arc** — memory-wall canonical: italic opener → italic continuation
→ upright pivot → uppercase climax. Four steps.

**Question-answer arc**: italic question small → uppercase answer big.
Two steps.

**List-of-three arc**: three equal-weight narration segments, one
climactic uppercase. Four steps.

**Single-statement arc**: one monumental uppercase held long. One step.

**Whisper-hook arc** (short-form): tiny italic hook → massive uppercase
reveal. Two steps.

The **number** of groups comes from the **content**. A 25s Pausch talk
has ~8 beats. A 7s TikTok hook has 2-3 beats. Don't force 4 or 5 or 7 —
read the transcript and mark breath-groups.

## Position + layer vocabulary

**Position** is where the caption lives in frame. Use:

- `top / left / right / bottom` (percentages or px) for anchor
- `transform: translateX/Y` for fine offsets
- `text-align: center / left / right` for alignment

**Layer** per group:

- `bg` (default) — behind subject. Matte occludes. Cinematic embed. Works
  on clean zones (sky, walls) OR intentionally crosses subject for the
  Vogue-masthead effect.
- `fg` — on top of subject. Announcement. Use for climax breakthroughs or
  when bg would be 100% occluded by body.

**Tone** per group:

- `soft` — gentle per-word opacity+y drift (0.45s power2.out). Use for
  introspective, dreamy, or narrative content.
- `present` — snappy per-word opacity+y+scale pop (0.22s power3.out). Use
  for emphatic or declarative beats.

## Anti-patterns the DNA protects against

The DNA defaults prevent most ugly outcomes. But avoid in per-group CSS:

- Multiple different `font-family` within one video (DNA is one family)
- Multiple saturated colors (one accent at most; DNA defaults cream or
  deep warm)
- `letter-spacing` above ±0.05em unless there's a specific reason
- `font-weight` 300 or below — too light for screen
- `font-style: italic` on emphasis — italic is for lyricism, not stress

## When cinematic-cream is wrong

This DNA assumes mid-to-dark backgrounds (luminance 60-180). For:

- Bright white studios → cinematic-cream's cream + `screen` washes out, and the DNA is
  **locked** (you cannot recolour it) → use **Standard mode** (opaque rail) instead
- Documentary formal → Standard mode (documentary-dignified direction; see references/direction-catalog.md §1)
- Energetic vlog hooks → future `kinetic-vlog` DNA (not yet shipped)

## Example: memory-wall original, expressed in freeform

Same output as the canonical memory-wall.html, but using slot-free plan:

```json
{
  "template": "cinematic-cream",
  "caption_layer": "bg",
  "groups": [
    {
      "id": "cg-0",
      "tone": "soft",
      "in": 0.2,
      "out": 4.85,
      "css": "top: 14%; right: 6%; left: auto; text-align: right; font-size: calc(0.09 * var(--h)); font-weight: 600; font-style: italic; letter-spacing: -0.01em;",
      "words": [
        { "text": "Some", "start": 0.24, "end": 0.44 },
        { "text": "memories", "start": 0.48, "end": 0.82 },
        { "text": "feel", "start": 0.92, "end": 1.14 },
        { "text": "soft", "start": 1.2, "end": 1.64 }
      ]
    },
    {
      "id": "cg-1",
      "tone": "soft",
      "in": 2.55,
      "out": 4.85,
      "css": "top: 26%; right: 10%; left: auto; text-align: right; font-size: calc(0.075 * var(--h)); font-weight: 500; font-style: italic;",
      "words": [
        { "text": "like", "start": 2.66, "end": 2.78 },
        { "text": "old", "start": 2.88, "end": 3.02 },
        { "text": "film", "start": 3.16, "end": 3.46 }
      ]
    },
    {
      "id": "cg-2",
      "tone": "present",
      "in": 4.9,
      "out": 8.04,
      "css": "top: 18%; right: 6%; left: auto; text-align: right; font-size: calc(0.085 * var(--h)); font-weight: 700;",
      "words": [
        { "text": "but", "start": 5.04, "end": 5.18 },
        { "text": "suddenly", "start": 5.24, "end": 5.76 }
      ]
    },
    {
      "id": "cg-3",
      "tone": "present",
      "in": 6.7,
      "out": 8.04,
      "css": "top: 32%; right: 6%; left: auto; text-align: right; font-size: calc(0.11 * var(--h)); font-weight: 900; text-transform: uppercase; letter-spacing: -0.03em; line-height: 0.95;",
      "words": [
        { "text": "everything", "start": 6.82, "end": 7.14 },
        { "text": "is", "start": 7.18, "end": 7.28 },
        { "text": "sharp", "start": 7.32, "end": 7.52 },
        { "text": "again", "start": 7.58, "end": 7.92 }
      ]
    }
  ]
}
```

Same visual, no slot constraint. Each group owns its typography.
