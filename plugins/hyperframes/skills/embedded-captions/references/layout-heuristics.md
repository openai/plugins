# Layout Heuristics

How to pick `wall_position` / `crown_position` in plan.json.

## Step 1: Sample 3 frames

```bash
ffmpeg -y -ss 0.5 -i source.mp4 -vframes 1 frame0.jpg
ffmpeg -y -ss <mid> -i source.mp4 -vframes 1 frame1.jpg
ffmpeg -y -ss <end-0.5> -i source.mp4 -vframes 1 frame2.jpg
```

Read all three. Note: subject's head bbox, shoulder top line, and wherever hands move during gestures. Worst-case foreground envelope = union across all 3.

## Step 2: Find the clean zone

The caption plane should live in pixels that are **always background** across the clip. Never where the body lands.

Annotate approximate ranges:

- Head bbox: `head_x_min`, `head_x_max`, `head_y_min`, `head_y_max`
- Hand gesture envelope (if any): usually below `y = shoulder_top ≈ head_y_max + 40`
- Props (mic, cup): typically static, note bbox

**Clean zones**, in priority order:

1. **Corner farthest from head** (usually opposite the gaze direction)
2. **Upper strip above head_y_min minus 30px margin**
3. **Lower-third** if upper is occupied (last resort — breaks "embedded" aesthetic)

## Step 2.5: Which side of the subject?

Once you know where the subject and baked graphics are, decide which side (left or right of the subject) hosts the caption column. Order of precedence:

### 1. Hard constraints first — baked graphics

Logos, watermarks, date stamps, "60 Overtime"-style lower-thirds are already in the source. They occupy permanent zones you must avoid. Map them out from frame samples:

- Jobs 60 Minutes: "2003" at upper-left (x=280-460, y=30-90); "60 Overtime" at bottom-left (x=280-770, y=960-1080). Left side partially constrained; still usable above/below these.
- TikTok re-uploads: username watermark that rotates corners every few seconds — hard to plan around, often a refusal reason.

If one side has a hard constraint that eats > 60% of that side's clean zone, default to the other side.

### 2. Subject body bias — pick the bigger clean zone

Compute clean-zone widths on both sides:

```
left_clean_width  = body_x_min − safe_left_margin
right_clean_width = safe_right_margin − body_x_max
```

Pick the side where clean zone is wider. If the difference is within 10% of frame width, the sides are ~equivalent → fall through to step 3.

Worked examples:

- **Champion** (Djokovic, 1920×1080): body x ≈ 550-1200. Left clean = 510, right clean = 720. Right is wider → but we put captions LEFT because of gaze (see step 3). The narrow difference made either workable.
- **Jobs**: body x ≈ 700-1480 (right-of-center). Left clean = 420, right clean = 160. Left wins decisively. Captions went LEFT.
- **Memory Wall**: surface location dictated the side (see note below about wall-embed).

### 3. Gaze direction — the "looking room" rule (tiebreaker and aesthetic)

Classic cinematic framing: leave more empty space on the side the subject is **looking toward**. This preserves their gaze path and feels uncluttered. **Captions go to the OPPOSITE side** (the side the subject is facing away from), so they don't steal looking room.

Quick check: sample 3 frames. Estimate the eye-line vector. Does it point more left or right?

- Looking screen-right → captions on LEFT
- Looking screen-left → captions on RIGHT
- Looking forward at camera → no preference from gaze, use step 2 only

The champion / Djokovic shot has him addressing camera slightly from the left — captions on LEFT actually read like text he's looking toward, which can feel like he's acknowledging them. That's fine here but is a flavor choice; generally prefer gaze-opposite.

### 4. Narrative emphasis (for optional crown)

If you're using a **center-stage crown**, it sits across the subject — no left/right choice for it. But the other captions (the column) still follow steps 1-3.

If you're using a **clean-zone crown** (shrunk, placed in one clean zone instead of crossing the body), put it in the **same side as the main column** for visual consistency. Don't split crown and column on opposite sides — it creates ping-pong.

### Special case — wall-embed

When the template is `wall-embed`, the side is **dictated by where the usable surface is**, not by body bias or gaze. Memory Wall's foam panel was on the right, so captions went right even though the subject was slightly left-of-center. Surface location wins because the whole effect depends on the text sitting ON that specific surface.

### Decision summary

```
Side = f(baked graphics, body bias, gaze, surface)

priority:
1. Hard constraints (baked logos)    — never place here
2. Wall-embed surface location       — wins if using wall-embed
3. Bigger clean zone                 — default for corner-column
4. Gaze direction (looking room)     — tiebreaker when both sides similar
```

If the subject actively swings their gaze across the clip (turning head L→R), pick a side that works for both extremes, not just the most frequent. Or accept that looking room will briefly be violated — it's a 10-second video, nobody cares.

## Step 3: Pick template + position

### If scene has a flat back wall (acoustic foam, plaster, fabric backdrop)

→ `wall-embed.html`

```
wall_position: {
  top:       max(40, head_y_min - 40),
  right:     20-60 (hug outer edge),
  width:     video_width * 0.35 – 0.50,
  height:    shoulder_top - top,
  rotateY:   -10 to -16 deg if wall angles away on the left,
             +10 to +16 deg if mirrored, 0 if wall is parallel,
  rotateX:   0-3 deg subtle downtilt only
}
```

`mix-blend-mode: overlay` in this template — works on mid-tone walls. If wall is near-black (luminance < 60), switch CSS to `screen`.

### If scene has a cluttered but dark backdrop (bookshelf, plants, set dressing)

→ `corner-column-crown.html`

```
wall_position: {
  top:       40,
  left:      40,               // anchor to clean corner opposite head
  width:     video_width * 0.40,
  height:    clamp(360, 520),  // don't reach below shoulder top
  rotateY:   3-6 deg (subtle, not flashy)
}
crown_position: {
  top:       video_height * 0.40   // center-ish; body will cut middle letters
}
```

`mix-blend-mode: screen` is correct here (bookshelf is dark).

### If subject fills >70% of frame

Template doesn't matter — there's nowhere clean. **Refuse**, suggest classic lower-third.

## Step 3.5: Crown placement (when using `corner-column-crown`)

**Default preference: center-stage crown.** A big, centered crown word (think "WIMBLEDON CHAMPION", "BEATLES", "SHARP AGAIN") that crosses the subject is the most powerful embed move — body occludes the middle letters, clean zones on both sides hold the outer letters, and the word reads as a title drop. **Use this whenever conditions allow.**

### Conditions where a centered crown works

Sample 3 frames, eyeball the subject's horizontal envelope across the clip. Let `body_x_min / body_x_max` = tightest horizontal bounds that contain the head+shoulders+arms in any frame.

A centered crown at font size F (where `crown_width ≈ F × 0.55 × char_count`) reads as dramatic IF:

1. **Subject is roughly centered**: `|body_center_x − frame_width/2| < frame_width × 0.10`. The body sits in the middle third.
2. **Clean zones on both sides are non-trivial**: `body_x_min > frame_width × 0.15` AND `body_x_max < frame_width × 0.85`. There's ≥15% of frame width clean on each side.
3. **The crown word is wide enough to poke out both sides**: `crown_width > body_width + 400px`. If the word ends before reaching the body's right edge, most letters just get swallowed — ugly.

If all three hold, centered crown is right. Go big — font sized so the word spans `0.8 × frame_width` or more. "BEATLES" at 140px (~500px wide) fails condition 3 on an 1920 frame with Jobs-sized body (780px wide). "WIMBLEDON CHAMPION" at 140px (~1700px) on the same frame passes easily.

### When center fails — move crown to the clean zone

If any of the three conditions fails, center-stage eats too much and the word becomes illegible ("THE BEATLES" → "THE" and a sliver of "S"). Two strategies:

**Option A — shrink crown to fit cleanly in the larger clean zone.** Pick the side opposite the subject's bias. Compute `clean_zone_width` on that side. Pick crown font such that the word wraps to 1-2 lines inside it. Tail letters can touch the subject edge for a hint of embed, but the body of the word lives on backdrop.

```
// Jobs: subject center ≈ x=1100 (right of frame center 960). Left clean zone is larger.
crown_plane: { left: 200, width: 560, text-align: center }
font-size: 118px  →  "THE / BEATLES" wraps to 2 lines, fits in x=230-770
                      leaving "S" tail at x~760 lightly touching Jobs's shoulder
```

**Option B — drop the crown entirely, promote the word to `emph` in the main column.** Simpler when the phrase doesn't deserve dramatic center-stage treatment. Works fine for 2-word emph like "the Beatles" or "incredible things" — they become large bold text in the left column with body occluding their tails.

### Rules of thumb for choosing

| Subject occupies center X%+ of frame | Clean zones L/R          | Crown approach                                  |
| ------------------------------------ | ------------------------ | ----------------------------------------------- |
| < 50%, roughly centered              | both ≥ 15% of width      | Centered crown, go BIG (frame_w × 0.8+)         |
| 50-70%, slightly offset              | one side ≥ 25%           | Crown shifted to larger clean zone              |
| > 70%, fills most of frame           | neither side wide enough | Drop crown, use `emph` in column                |
| Close-crop face, fills > 80%         | essentially none         | No crown. All captions in a header/footer strip |

## Step 4: Respect these invariants

1. **Never cover the eyes.** Eye bbox is sacred. Add 20px margin around it when checking caption bbox intersection.
2. **Caption bbox must not exit frame.** Reserve 4% broadcast-safe margin on all edges.
3. **Large emphasis words should have horizontal slack.** At `cap-emph` (92px), an 8-char word ≈ 580px. Plane needs ≥ 620px width OR rely on wrapping at 2 lines.
4. **Crown lives at `top ≈ shoulder_top − crown_font_size/2`** so it sits across the upper body, not the face.
5. **If aspect ratio is portrait (9:16), rotate layout**: wall-plane becomes a **top band** (full width, height ≈ 20%), crown goes below it if used at all.

## Step 5: Validate before render

Before calling `render-and-composite.sh`, sanity check:

- Did you place the plane in the opposite quadrant from the face? ✓
- Does the plane exit the frame anywhere? If yes, shrink.
- Is the font too big for the plane width? Calculate: longest word in words[] × 0.55 × font_size < plane_width - padding\*2.
- For `corner-column-crown`, did you set `crown_position.top` so the crown actually crosses the body (not above the head, not below the torso)?
- **Pillarbox / letterbox hard check.** If the source has black bars (see pre-flight probe in SKILL.md), compute `leftmost_text_x` using the correct formula for the text alignment:

  | Alignment                   | Formula                                            |
  | --------------------------- | -------------------------------------------------- |
  | Left-aligned                | `plane_left + padding_left`                        |
  | Right-aligned (main column) | `plane_right − padding_right − longest_word_width` |
  | Center-aligned (crown)      | `plane_center − longest_word_width / 2`            |

  Where `longest_word_width ≈ font_size × char_count × 0.55` (adjust 0.55 down to ~0.50 for italic, up to ~0.62 for uppercase bold). **All** of these must be ≥ `pillarbox_left_edge + 10–20px` (safety margin). Mirror for the right bar.

  **Gotcha from past iteration**: setting `plane_left = 180` with a right-aligned column on a Jobs 60 Minutes clip (pillarbox at 280) looked "inside the plane" but the right-aligned text at font 108px produced `leftmost = plane_right − padding − 468 = 180 + 700 − 36 − 468 = 376` … wait, that IS past pillarbox. The actual bug was different: for a 3-line wrap ("four very / talented / guys") the widest line is "talented" at ~468px, not the whole phrase. Compute against the longest **single line** after wrap, not total phrase width.

  **Re-check after font-size changes** — bumping font 84→104 shifts right-aligned text leftward by ~30px. If the budget was already tight, the bump blows through the pillarbox.

  **Empirical target**: leftmost text at pillarbox + 10-20px looks "anchored" to the bar (visually grounded). Pushing it much deeper (50px+) makes captions feel floaty in the middle of the frame.

## Worked examples

### memory-wall (1280×720, acoustic foam wall)

```json
{
  "template": "wall-embed",
  "wall_position": {
    "top": 40,
    "right": 30,
    "width": 720,
    "height": 520,
    "rotateY": -13,
    "rotateX": 1
  }
}
```

### champion (1920×1080, bookshelf backdrop)

```json
{
  "template": "corner-column-crown",
  "wall_position": { "top": 40, "left": 40, "width": 720, "height": 420, "rotateY": 4 },
  "crown_position": { "top": 440 }
}
```
