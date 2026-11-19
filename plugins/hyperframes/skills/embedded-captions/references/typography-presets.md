# Typography Presets

Five named styles corresponding to the `cap-*` CSS classes. Pick one per caption group in `plan.json` based on the line's semantic role.

| style    | CSS                         | Use when                                                                                                                  |
| -------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `intro`  | 66px italic 500             | First line, filler ("You know…", "So…"), contemplative openings. Low visual weight.                                       |
| `phrase` | 78px upright 600            | Main statement clauses. Default for most lines.                                                                           |
| `emph`   | 92px upright 800            | Lines with emotional peak or key achievement ("I've achieved incredible things").                                         |
| `dream`  | 82px italic 700             | Aspirational / "was dreaming of…" style lines. Italic signals memory/imagination.                                         |
| `crown`  | 140px upright 900 uppercase | **Only for the climax line.** Used in center-stage `crown-plane`. Maximum one per composition — ideally the last caption. |

## Tone field

Independent of style, each group has `tone`: `soft` or `present`.

- **soft** — gentle fade + 8px y-drift entrance, `power2.out` ease. Feels floaty, nostalgic. Use for memory, intro, dream.
- **present** — snappy 6px y + 1.04 scale pop, `power3.out`, transformOrigin center. Feels assertive, in-the-moment. Use for emphasis and crown.

## Picking automatically

Scan each group's words:

1. Does it contain superlatives (incredible, best, only, never, always) or brand/proper nouns? → `emph` + `present`
2. Does it start with discourse markers (you know, so, well, look) or is it short (≤3 words)? → `intro` + `soft`
3. Does it reference dreams, hopes, memory, past tense verbs like "was dreaming"? → `dream` + `soft`
4. Is it the final sentence-clinching line and feels like a title/headline? → `crown` + `present` (only one per video)
5. Otherwise → `phrase` + (match the group's neighbors' tone; default `soft`)

## Font-size scales with column width

The `.cap-*` defaults in each template are tuned for a **~560px column** (the original champion composition). When the caption plane is wider than that, the fonts feel underweight — too much negative space around text. Scale up accordingly.

| Plane width         | intro | phrase | emph | dream | crown (centered, full-frame) | crown (clean-zone only) |
| ------------------- | ----- | ------ | ---- | ----- | ---------------------------- | ----------------------- |
| 460-580 px (tight)  | 66    | 78     | 92   | 82    | 140                          | n/a                     |
| 600-760 px (medium) | 78    | 108    | 128  | 100   | 220                          | 118                     |
| 780+ px (wide)      | 90    | 128    | 150  | 116   | 260                          | 140                     |

Notes:

- Crown sizes assume landscape (1920×1080). For portrait 1080×1920, divide all crown sizes by 1.5.
- "full-frame crown" = centered, designed to span `0.8+ × frame_width` and cross the subject's body. Use only when [layout-heuristics.md § Crown placement](layout-heuristics.md) conditions pass.
- "clean-zone only crown" = crown positioned inside one clean zone, smaller font, tail letters lightly touch subject. Fallback when centered crown would eat too much.

Also: if a plane's `rotateY` is non-trivial (say > 8°), effective visible width shrinks. Scale fonts up ~10% to compensate.

## What NOT to do

- Don't use more than **one crown** per render. The whole point is that it's a singular payoff.
- Don't use `emph` on more than ~30% of groups. Emphasis loses meaning when everything is emphasized.
- Don't pick `intro` for the main content just because the words are short. "I won" (2 words) is `emph` or `crown`, not `intro`.
- Don't mix `soft` and `present` alternately for no reason. Tone should follow the story arc: soft opening → present build → emph peak → (optional crown climax).

## When scene luminance affects color choice

The default color is warm bone-white (`#fff5df`). Adjust in the template CSS:

- Wall is mostly warm wood / tan → keep default, or shift cooler `#e8f0ff`
- Wall is cool blue / tech-lab → push warmer `#fff0c0`
- Wall has strong primary color → desaturate default, luminance first

These adjustments happen in the HTML template, not plan.json. If you repeatedly need different palettes, make new template variants.
