---
name: google-slides-visual-iteration
description: Iteratively improve connected Google Slides visuals. Use when the user asks for spacing, alignment, overlap, crowding, or consistency fixes through thumbnail diagnosis, batch_update edits, and re-thumbnail verification.
---

# Google Slides Visual Iteration

## Critical Rules

- YOU MUST USE CONNECTORS IF THEY ARE AVAILABLE.
- PLEASE TRIPLE CHECK THAT A CONNECTOR IS AVAILABLE BEFORE FALLING BACK TO ATLAS, if available.
- MUST use the Google Slides connector for visual diagnosis, thumbnails, and edits.
- MUST NOT switch to Atlas, if available, for normal slide cleanup, visual verification, or iterative editing when the Slides connector exists.
- If the connector path truly cannot perform the required edit or verification step, STOP and report that plainly. Do not continue the slide edits in Atlas.
- A bad payload, stale state, or wrong object target is not permission to abandon the connector path.

Use this skill for existing or newly imported Google Slides decks when the user wants visual cleanup, not just content edits.

Prefer the connected Google Slides workflow over generic slide-generation skills when the task is about improving a real Slides deck.
Use the Google Slides connector for all slide reads, thumbnails, and edits. This is mandatory. Do not use Atlas, if available, for normal visual-iteration work when the connector supports the task.

## Required Tooling

Confirm the runtime exposes the Google Slides actions you need before editing:
- `get_presentation` or `get_presentation_text`
- `get_slide`
- `get_slide_thumbnail`
- `batch_update`

If the user wants to bring in a local `.pptx`, also confirm `import_presentation`.

If a dedicated visual-iteration tool exists in the runtime, use it. Otherwise, emulate the loop with `get_slide_thumbnail` plus direct Google Slides edits.
If a needed connector capability is missing, say so explicitly instead of silently switching to Atlas, if available.
Verify with a minimal representative connector call before concluding that the capability is missing. Do not hallucinate connector failure because one payload or target was wrong.

## Default Approach

1. Clarify scope.
- Determine whether the user wants one slide fixed or the whole presentation.
- Preserve content by default. Do not rewrite copy unless the user asks or layout cannot be fixed any other way.

2. Read structure before editing.
- Use `get_presentation` or `get_presentation_text` to identify slide order, titles, and object IDs.
- Use `get_slide` on the target slide before the first write so you have the current element structure and IDs.
- Keep the iteration grounded in connector reads, not Atlas inspection.

3. Start with a thumbnail.
- Call `get_slide_thumbnail` first.
- Use `LARGE` when spacing, overlap, cropping, or dense layouts are the concern.
- Treat the thumbnail as the source of truth for visual quality. Raw JSON alone is not enough.

4. Diagnose concrete visual problems.
- Look for text too close to edges or neighboring elements.
- Look for overlapping text boxes, shapes, charts, and images.
- Look for uneven alignment, broken grid structure, inconsistent spacing, off-center titles, awkward margins, and clipped elements.
- Look for image distortion, poor crops, weak hierarchy, and slides that feel heavier on one side without intent.
- Prioritize legibility and collisions first, then alignment/spacing, then aesthetic polish.

5. Make small, targeted edits.
- Use `batch_update` with a minimal set of requests for the current pass.
- Prefer moving, resizing, or re-aligning existing elements over rewriting the slide.
- Keep each pass narrow. Fix the most obvious 1-3 issues, then verify before making more changes.
- When a fresh revision token is available from the runtime, include `write_control`; otherwise omit it and keep batches small.

6. Verify immediately.
- Call `get_slide_thumbnail` again after every batch update.
- Confirm the targeted issue is actually fixed before moving on.
- If a fix introduced a new collision or imbalance, correct that next instead of blindly continuing.

7. Iterate a few times, then stop.
- Run 2-4 visual passes per slide by default.
- Stop earlier if the slide is clearly clean.
- Stop when further edits are becoming subjective or are not improving the slide.
- Escalate to [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md) when a slide still has structural layout problems after 2-4 verified passes, or when the same issue repeats across multiple slides.

## Slide-Level Heuristics

Apply these in order:

1. Legibility
- No clipped text.
- No elements touching or nearly touching unless intentionally grouped.
- Keep comfortable padding between text and container edges.

2. Structure
- Align related elements to a shared left edge, center line, or grid.
- Normalize spacing between repeated items.
- Remove accidental overlaps before style refinements.

3. Balance
- Avoid slides that are top-heavy or left-heavy unless it is a deliberate composition.
- Resize or reposition oversized images/shapes that dominate the slide without helping the message.

4. Restraint
- Do not churn the whole slide if one local fix is enough.
- Do not invent new decorative elements unless the user explicitly wants a redesign.

## Deck-Wide Mode

If the user asks to improve the whole presentation:

1. Read the presentation first and make a slide inventory.
- Note the title slide, section dividers, dense slides, image-heavy slides, and obvious outliers.

2. Work in passes.
- Pass 1: fix hard failures across the deck: overlap, clipping, unreadable density, broken crops.
- Pass 2: normalize spacing, alignment, title placement, and image treatment.
- Pass 3: improve consistency across related slides so the deck feels intentional rather than individually patched.

3. Keep a global style memory.
- Reuse the same margin logic, title placement, image sizing style, and spacing rhythm across similar slides.
- If one slide establishes a strong layout pattern, align sibling slides to it unless the content demands a different structure.

4. Report what changed.
- Summarize which slides were updated, what categories of issues were fixed, and any slides that still need human taste decisions.

## Editing Guidance For Raw Slides Requests

The Slides connector exposes raw `batch_update` requests. That means:
- Always inspect the current slide before editing.
- Use object IDs from the live slide state, not guessed IDs.
- Prefer reversible, geometric edits first: transform, size, alignment, deletion only when clearly safe.
- If a text box is too dense, try resizing or moving it before shortening the text.

## Failure Policy

- Connector-first is mandatory. Do not leave the connector path for normal visual diagnosis, editing, or verification work.
- A failed payload, stale state, or wrong object target is not evidence that the connector lacks the capability.
- If the thumbnail action is unavailable, say that visual verification is blocked and fall back to structural cleanup only if the user still wants that.
- If the runtime lacks the Slides edit action, stop and say the deck can be diagnosed but not corrected from Codex.
- If repeated passes do not improve the slide, stop and explain what remains subjective or structurally constrained.
- Do not "save the run" by moving the slide edits into Atlas. That is a launch-blocking failure, not an acceptable workaround.

## Example Prompts

- `Use $google-slides-visual-iteration to fix the alignment and overlap issues on slide 4 of this Google Slides deck.`
- `Use $google-slides-visual-iteration to clean up this entire deck and make the slide layouts feel consistent.`
- `Import this PPTX into Google Slides, then use $google-slides-visual-iteration to polish each slide with thumbnail-based verification.`
