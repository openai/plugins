# Scene Types — picking the right template

The three templates differ in one thing: **what surface (if any) the text physically sits on**. Pick by reading the scene, not by the genre label.

## wall-embed — "text is printed on a real surface"

Original Memory Wall render used this. Text uses perspective transform + `mix-blend-mode: overlay` to look like it was silk-screened onto a wall behind the subject. The illusion is strong when it works and completely broken when forced.

### Four conditions — ALL must hold

1. **A flat or near-flat surface exists somewhere in the frame, larger than the caption block.** Good: acoustic foam panel, painted wall, door, stone facade, large backdrop cloth, blackboard. Bad: bookshelf (3D depth + decorative items), mic shield (too small), window (transparent, content behind it shifts), brick wall with mortar patterns (competes).
2. **The surface is at a non-zero angle to the camera.** Perspective is what sells "embedded". If the wall is perfectly parallel (0° rotation relative to camera), pasting rotateY:0 text onto it looks like a sticker, not embedded. Memory Wall's foam wall was tilted ~13° — perfect. A wall directly behind a centered frontal subject usually has no exploitable angle.
3. **The surface is mid-luminance.** Overlay blend neutralizes mid-tones — text keeps contrast against a mid-grey wall. On near-black surfaces (luminance < 60), overlay makes text vanish → switch to `mix-blend-mode: screen`. On near-white surfaces (> 180), overlay also fails → switch to `mix-blend-mode: normal` with opaque color.
4. **The surface has no competing graphical content.** Plain paint, uniform acoustic foam, blurred OOF background all work. Printed wallpaper, picture frames, text on signage, busy bookshelves all compete with the caption and ruin the embed illusion.

If **any** condition fails, **do not use wall-embed**. Pick another template.

### What memory-wall looked like

The acoustic foam wall to the right of the subject took ~40% of frame width, tilted ~13° toward the viewer, mid-grey color, uniform dimpled texture. Perfect. Text with `rotateY(-13deg)` and overlay blend sat on it like printed letters.

### Anti-examples (wall-embed would FAIL)

- **champion / demo1_avatarv** — bookshelf background with books, white vases, picture frames. Cluttered + 3D depth. Fails condition 1 and 4. Used corner-column-crown instead.
- **Jobs 60 Minutes** — blurry potted plant background. No flat surface at all. Fails condition 1.
- **Randy Pausch "Time is all we have"** — completely black backdrop. No perspective to exploit, no mid-tone surface. Fails 2 and 3. Used portrait-header.
- **Any vlog / selfie with handheld camera** — surface moves frame-to-frame, can't lock perspective. Even if conditions 1-4 hold briefly, motion breaks the illusion.

## corner-column-crown — "text sits in a clean region next to the subject"

The default for most talking-head content. Works when wall-embed doesn't.

### Conditions

1. **Single subject, fixed camera.** Handheld is tolerable if drift is small.
2. **At least one clean zone (≥ 15% of frame width) to the left or right of the subject** where captions can sit without continuous body occlusion.
3. **Background can be cluttered or 3D** — we're not relying on a flat surface, just readable contrast. Screen blend mode picks up darker backgrounds (bookshelves, dark walls) naturally.
4. **Landscape aspect** (16:9 or similar). For portrait, use `portrait-header`.

### When to add the crown vs when to skip it

- Add crown if there's a natural "title drop" line — the one phrase that lands the story (e.g. "WIMBLEDON CHAMPION", "BEATLES", "SHARP AGAIN"). Check [layout-heuristics.md § Crown placement](layout-heuristics.md) for the three geometric conditions.
- Skip crown for factual / neutral monologues where no phrase carries the climax. Short videos (<10s) often don't need it.

## portrait-header — "subject fills center, text lives in top banner"

For 9:16 aspect where the subject inevitably fills the middle.

### Conditions

1. **Portrait aspect** (9:16, 1080×1920 etc.).
2. **Subject occupies the vertical middle of frame**, leaving ~15-25% of the frame height clear at the top.
3. **Optional crown at bottom** — only works if there's also clean space beneath the subject's waist, which is rare in close-crop portrait.

### What to watch

- Subject's head top often approaches y=40 — top banner captions at `top: 30px` will get partially occluded by hair. Accept the partial occlusion (it reads as embed) or bump the caption size down to clear the hair.
- If the subject already has **baked-in captions** (like the burned-in subtitles test case with yellow subtitles burned in), the skill should refuse — two caption systems compete.

## Quick decision flow

```
START
  │
  ├─ Aspect is 9:16 / portrait?
  │    ├─ YES → portrait-header
  │    └─ NO ──▼
  │
  ├─ Does the scene have a flat uniform surface that passes
  │  ALL 4 wall-embed conditions?
  │    ├─ YES → wall-embed
  │    └─ NO ──▼
  │
  ├─ Single subject + fixed camera + ≥15% clean zone on one side?
  │    ├─ YES → corner-column-crown
  │    └─ NO ──▼
  │
  └─ Refuse with reason:
     "No flat surface for embed, no clean caption zone for column.
      Suggest a classic lower-third instead."
```

## Mode checklist (run this before committing to wall-embed)

Read 3 frames (start, mid, end). For each, honestly answer:

- [ ] Is there a single surface behind/beside the subject that occupies ≥ 30% of the frame?
- [ ] Is that surface relatively flat (not curved, not 3D-stacked shelving)?
- [ ] Does that surface angle at 5-20° to the camera (not perfectly parallel, not warped)?
- [ ] Is the surface mid-luminance (not near-black like dark bookshelves, not near-white like a sunny window)?
- [ ] Does the surface contain NO printed/decorative elements that compete with caption text?
- [ ] Does the surface remain visible across all 3 frames (subject doesn't step in front of it)?

**Need all six YES to use wall-embed.** Even one NO → step down to corner-column-crown or portrait-header.
