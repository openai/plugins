# Template: champion

**Look:** podcast / interview, upper-side column with intro→phrase→emph
beats building toward a center-stage CROWN that crosses the subject's body.
"Wimbledon Champion" energy.

**Visual identity (LOCKED):**

- 5 typography slots: intro / phrase / emph / dream / crown
- `mix-blend-mode: screen` over warm bone color (#fff5df)
- Deep text-shadow + brightness boost
- Single-caption-swap layout (caps stack at one point in the column)
- Center-stage crown crosses the subject for cinematic occlusion

## When to apply

✅ **Good fit:**

- Podcast / interview style with a single seated subject
- Cluttered backdrop (bookshelf, props, dark) — screen blend reads through
- Subject roughly centered with clear clean zones on one or both sides
- Speech has a clear payoff line that can become a "crown" (1-3 short words)
- 16:9 landscape, 1920×1080 ideal

❌ **Wrong fit:**

- Bright/sky/window backdrop (screen blend washes out)
- Subject heavily off-center such that there's no clean column zone
- Speech has no clear climax line
- Portrait 9:16 → use `portrait-header` template instead

## Layout decisions agent makes

| Field                         | What                                                                                                                                        | Example (1920×1080)                            |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `plane.top/left/width/height` | Where the side column sits. Pick the side opposite the subject's gaze (looking room) and hug the cleanest backdrop zone.                    | `{top: 40, left: 40, width: 720, height: 420}` |
| `plane.rotateY`               | Slight perspective into the wall. Positive for left column (recedes right), negative for right column. Keep small (3-7°).                   | `4`                                            |
| `crown_top`                   | Y position of the crown. Should fall on the subject's chest/neck so the body occludes the middle letters.                                   | `420`                                          |
| `font_scale`                  | Multiplier on locked sizes.                                                                                                                 | `1.0` for 1920×1080                            |
| `crown_enabled`               | Whether to render a crown. Skip if the speech has no clean payoff line, or if the subject is too far off-center for a center crown to land. | `true`                                         |

### Crown placement rules

Before enabling the crown, verify all 3 conditions:

1. Subject body center within ±10% of frame horizontal center
2. Clean zones ≥15% of frame width on each side of subject
3. Crown text width (uppercase 140px × ~chars) > subject body width + 400px

If any fails: disable the crown OR use a smaller font + place it in the
larger clean zone instead of center. See `references/layout-heuristics.md`.

## Slot assignment

| Slot   | Use for                                                    |
| ------ | ---------------------------------------------------------- |
| intro  | Filler / discourse markers ("you know,", "for me,", "so…") |
| phrase | Main statement clauses                                     |
| emph   | Key achievement / superlative line                         |
| dream  | Aspirational lines, past-tense reflection                  |
| crown  | The single climax line — center-stage payoff               |

Aim for ≤3 slots per video (excluding crown). Don't use all 4 in a 12s clip.

## Plan.json shape

```json
{
  "mode": "template",
  "template": "champion",
  "duration": 12.08, "fps": 24, "width": 1920, "height": 1080,
  "plane": {
    "top": 40, "left": 40, "width": 720, "height": 420,
    "rotateY": 4
  },
  "crown_top": 420,
  "font_scale": 1.0,
  "groups": [
    { "id": "cg-0", "slot": "intro", "tone": "soft",
      "in": 0.10, "out": 1.45, "words": [...] },
    { "id": "cg-1", "slot": "phrase", "tone": "soft",
      "in": 1.55, "out": 4.20, "words": [...] },
    { "id": "cg-2", "slot": "emph", "tone": "present",
      "in": 6.50, "out": 8.30, "words": [...] }
  ],
  "crown_group": {
    "id": "cg-crown", "tone": "present",
    "in": 10.85, "out": 12.08,
    "words": [
      {"text": "Wimbledon", "start": 10.94, "end": 11.28},
      {"text": "Champion",  "start": 11.38, "end": 11.84}
    ]
  }
}
```

`crown_group` always uses the crown slot — no need to specify `slot`.
Set `crown_group: null` to disable.
