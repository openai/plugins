---
name: google-slides-template-surgery
description: Restructure connected Google Slides decks in Codex when local slide cleanup is not enough. Use when repeated alignment or overlap issues come from the slide structure itself, when the same fix must be applied across many slides, or when raw Slides batch_update requests need stricter recipes and verification to avoid hallucinated params or broken layouts.
---

# Google Slides Template Surgery

Use this skill for structural Google Slides cleanup. This is the escalation path after normal visual iteration fails to converge.

Start with local slide fixes first. Escalate to template surgery only when one of these is true:
- the same spacing or overlap problem repeats across multiple slides
- the slide structure is fundamentally bad and local nudges keep re-breaking the layout
- the user explicitly asks to rework the template, placeholders, or repeated layout pattern
- the deck needs a consistent structural reset, not just cosmetic polish

For simple cleanup, prefer [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md).

## Required Tooling

Confirm the runtime exposes:
- `get_presentation` or `get_presentation_text`
- `get_slide`
- `get_slide_thumbnail`
- `batch_update`

If any of those are missing, stop and explain that the deck cannot be safely restructured from Codex.

## Workflow

1. Read the deck before changing it.
- Inventory slide types, repeated layouts, title patterns, image-heavy slides, and broken outliers.
- Fetch the target slide structure with `get_slide` before writing.
- Use live object IDs only. Never guess them.

2. Decide whether to patch or rebuild.
- Patch in place when the slide has the right elements but the geometry is bad.
- Duplicate or recreate structure when the slide is too broken for safe incremental edits.
- Prefer one layout pattern at a time instead of broad deck-wide surgery in a single batch.

3. Plan the operation as a small structural batch.
- Keep each batch narrow and intentional.
- Do not mix unrelated edits just because they touch the same slide.
- Copy request shapes from `./references/batch-update-recipes.md` instead of inventing them from memory.

4. Verify on representative slides.
- After each structural batch, re-fetch thumbnails for the edited slide and 1-2 sibling slides that use the same pattern.
- Do not assume a successful write means the layout is improved.

5. Roll forward carefully.
- Once a structural pattern works, apply it to the next matching slides.
- Reuse the same margin logic, title placement, and content rhythm across sibling slides.

## Structural Rules

- Prefer duplicating a clean slide pattern over endlessly mutating a broken one.
- Prefer deleting or replacing redundant elements over stacking new ones on top of old ones.
- Preserve user content by default. Structural cleanup is not permission to rewrite the narrative.
- Keep batches reversible. If the slide gets worse after a pass, correct the structure before adding more edits.
- If repeated edits are failing, stop and explain what constraint is blocking clean automation.

## Common Surgery Cases

Use this skill for:
- rebuilding crowded title/content slides with a cleaner text-and-image split
- replacing a bad placeholder stack with a simpler repeated pattern
- deleting duplicate or stale decorative shapes that keep causing overlap
- normalizing title position, body width, and image frame placement across a section
- duplicating a strong “golden” slide structure and adapting it for sibling slides

Do not use this skill for:
- one-off typo fixes
- simple repositioning on a single slide
- content generation from scratch
- freeform redesign when the user only asked for cleanup

## Verification Standard

A structural pass is only done when:
- the target slide no longer has clipping or overlaps
- the new structure looks stable in the thumbnail, not just valid in raw JSON
- sibling slides using the same pattern still look coherent
- no stale elements remain hidden behind the new layout

## References

Read these before the first write:
- `./references/template-surgery-playbook.md`
- `./references/batch-update-recipes.md`
