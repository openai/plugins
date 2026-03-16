---
name: sprite-pipeline
description: Generate and normalize 2D sprite animations. Use when the user asks for full-strip generation from approved source frames, consistent anchor and scale normalization, or preview assets for browser-game animation.
---

# Sprite Pipeline

## Overview

Use this skill for 2D sprite generation and normalization. This workflow is intentionally anchored around one approved frame and a whole-strip generation pass because frame-by-frame generation drifts too easily.

This skill is 2D-specific. If the request is for 3D characters, meshes, or materials, route back through `../game-studio/SKILL.md`.

## Core Workflow

1. Start from an approved in-game seed frame.
   - The seed frame should already reflect the right silhouette, palette, costume, and proportions.
2. Build a larger transparent reference canvas around that frame.
   - Use `../../scripts/build_sprite_edit_canvas.py`.
3. Ask for the full animation strip in one edit request.
   - Do not generate each frame independently unless the user explicitly accepts lower consistency.
4. Normalize the result into fixed-size game frames.
   - Use `../../scripts/normalize_sprite_strip.py`.
   - Use one shared scale across the whole strip.
   - Align frames with one shared anchor, typically bottom-center.
5. Optionally lock frame 01 back to the shipped seed frame.
   - Do this when the animation should begin from the exact idle or base pose already in game.
6. Render a preview sheet and inspect the animation in-engine before approving it.
   - Use `../../scripts/render_sprite_preview_sheet.py`.

## Prompting Rules

Always preserve these invariants in the prompt:

- same character
- same facing direction
- same palette family
- same silhouette family
- same readable face or key features
- same outfit proportions
- transparent background
- exact frame count and slot layout

Always ask for:

- one strip at once
- a transparent canvas
- no scenery, labels, or poster composition
- crisp pixel-art clusters for pixel work
- production asset tone, not concept art

## Using Image Generation

For live asset generation or edits, use the installed `imagegen` skill in this workspace. This skill defines the game-specific process; `imagegen` handles the API-backed generation or edit execution.

## Script Recipes

Create a reference canvas:

```bash
python3 scripts/build_sprite_edit_canvas.py \
  --seed output/sprites/idle-01.png \
  --out output/sprites/hurt-edit-canvas.png \
  --frames 4 \
  --slot-size 256 \
  --canvas-size 1024
```

Normalize a raw strip:

```bash
python3 scripts/normalize_sprite_strip.py \
  --input output/sprites/hurt-raw.png \
  --out-dir output/sprites/hurt \
  --frames 4 \
  --frame-size 64 \
  --anchor output/sprites/idle-01.png \
  --lock-frame1
```

Render a preview sheet:

```bash
python3 scripts/render_sprite_preview_sheet.py \
  --frames-dir output/sprites/hurt \
  --out output/sprites/hurt-preview.png \
  --columns 4
```

## Quality Gates

- proportions stay stable across frames
- frame-to-frame size does not drift
- action reads clearly at game scale
- transparency is preserved
- frame 01 matches the shipped sprite when lockback is enabled
- preview looks correct before any in-engine asset index update

## References

- Detailed workflow: `../../references/sprite-pipeline.md`
- Shared frontend context: `../game-ui-frontend/SKILL.md`
