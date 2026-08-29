# Template: portrait-header

**Look:** 9:16 portrait talking-head with captions on a horizontal strip
across the top of the frame, above the subject's head. Optional crown at
the bottom for shots that include the subject's waist or below.

**Visual identity (LOCKED):**

- 5 typography slots: intro / phrase / emph / dream / crown (centered)
- `mix-blend-mode: screen` over warm bone color (#fff5df)
- Single-caption swap (caps stack at one position in the header strip)
- Per-word fade with subtle Y-drift (soft) or pop+scale (present)

## When to apply

✅ **Good fit:**

- 9:16 portrait video (1080×1920 typical)
- Single subject filling the center of the frame
- Clean band visible above the head
- Speech is relatively dense (many short phrases) — crown only for the
  one true climax

❌ **Wrong fit:**

- Subject's head crops to the very top of frame (no header band exists)
- 16:9 landscape → use `champion` or `memory-wall` instead
- Multiple speakers / cuts

## Layout decisions

| Field           | What                                                                                                                    | Example (1080×1920)                  |
| --------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| `header.top`    | Y of the header strip. Should sit above the subject's head with ~30px breathing room.                                   | `30` if hair top is around y=200     |
| `header.height` | Height of the strip. Bigger for longer captions / 2-line wraps.                                                         | `280`                                |
| `crown_top`     | Y of the crown line (bottom of frame). Skip if no waist visible.                                                        | `1620` for a near-full-body shot     |
| `crown_enabled` | Whether to render a bottom crown. Skip if subject body fills the lower half completely (matte will block crown anyway). | `false` for tight head-and-shoulders |
| `font_scale`    | Scale multiplier on locked sizes.                                                                                       | `1.0` for 1080×1920                  |

## Slot assignment

Same arc as champion: intro / phrase / emph / dream / crown.

For portrait-header specifically, header band is narrow (one strip), so:

- Most groups fit on 1-2 lines
- Don't use crown if it'd be hidden by the body matte (Pausch-style portraits
  often need to skip crown entirely and promote the climax to `emph` in the
  header instead)

## Plan.json shape

```json
{
  "mode": "template",
  "template": "portrait-header",
  "duration": 25.3, "fps": 24, "width": 1080, "height": 1920,
  "header": { "top": 30, "height": 280 },
  "crown_top": 1620,
  "font_scale": 1.0,
  "groups": [
    { "id": "cg-0", "slot": "intro", "tone": "soft",
      "in": 0.10, "out": 3.20, "words": [...] },
    { "id": "cg-1", "slot": "phrase", "tone": "soft",
      "in": 3.55, "out": 5.80, "words": [...] },
    { "id": "cg-2", "slot": "emph", "tone": "present",
      "in": 17.85, "out": 22.10,
      "words": [
        {"text": "Time", "start": 17.94, "end": 18.26},
        {"text": "is",   "start": 18.38, "end": 18.54},
        {"text": "all",  "start": 18.66, "end": 18.80},
        {"text": "we",   "start": 18.92, "end": 19.02},
        {"text": "have", "start": 19.12, "end": 19.38}
      ]}
  ],
  "crown_group": null
}
```

Set `crown_group: null` if you've checked that a crown would be blocked by
the subject body or the shot composition.
