---
name: google-slides-visual-iteration
description: Iteratively inspect and polish existing connected Google Slides presentations in Codex using slide thumbnails plus raw Slides edits. Use when a user asks to fix a slide visually, clean up formatting, improve slide quality, make a deck look better, fix alignment, spacing, overlap, overflow, crowding, awkward whitespace, or deck-wide visual consistency in an existing Google Slides deck or shared Slides link, especially when the work should follow a thumbnail -> diagnose -> batch_update -> re-thumbnail verification loop.
---

# Google Slides Visual Iteration

Use this skill for existing or newly imported Google Slides decks when the user wants visual cleanup, not just content edits.

Prefer the connected Google Slides workflow over generic slide-generation skills when the task is about improving a real Slides deck.
Treat this as the focused formatting workflow: work one slide at a time, and complete the thumbnail -> diagnose -> batch_update -> re-thumbnail loop before moving to the next slide.
Prefer this skill over [google-slides](../google-slides/SKILL.md) when the request is primarily about visual polish on an existing deck rather than content generation or general deck inspection.

## Use When

- The user wants to improve how an existing Google Slides deck looks, not just change its copy.
- The request includes phrases like "fix this slide," "make this deck look better," "clean up formatting," "fix overflow," "fix spacing," "fix alignment," or "visual iteration."
- The user shares a connected Google Slides deck or link and wants edits applied directly to that deck.

## Required Tooling

Confirm the runtime exposes the Google Slides actions you need before editing:
- `get_presentation` or `get_presentation_text`
- `get_slide`
- `get_slide_thumbnail`
- `batch_update`

If the user wants to bring in a local `.pptx`, also confirm `import_presentation`.

If a dedicated visual-iteration tool exists in the runtime, use it. Otherwise, emulate the loop with `get_slide_thumbnail` plus direct Google Slides edits.

## Default Approach

1. Clarify scope.
- Determine whether the user wants one slide fixed or the whole presentation.
- If multiple slides need cleanup, still process formatting slide by slide unless a single repeated structural fix is clearly safer.
- Preserve content by default. Do not rewrite copy unless the user asks or layout cannot be fixed any other way.

2. Read structure before editing.
- Use `get_presentation` or `get_presentation_text` to identify slide order, titles, and object IDs.
- Use `get_slide` on the target slide before the first write so you have the current element structure and IDs.

3. Start with a thumbnail.
- Call `get_slide_thumbnail` first.
- Use `LARGE` when spacing, overlap, cropping, or dense layouts are the concern.
- Treat the thumbnail as the source of truth for visual quality. Raw JSON alone is not enough.

4. Diagnose concrete visual problems.
- Look for text too close to edges or neighboring elements.
- Look for overlapping text boxes, shapes, charts, and images.
- Look for uneven alignment, broken grid structure, inconsistent spacing, off-center titles, awkward margins, and clipped elements.
- Look for image distortion, poor crops, weak hierarchy, and slides that feel heavier on one side without intent.
- Look for visual regressions introduced by the previous pass before adding more polish.
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

2. Prioritize the slide order.
- Start with slides that have overlap, clipping, unreadable density, or broken crops.
- Move to spacing, alignment, title placement, image treatment, and consistency after the hard failures are under control.

3. Finish each slide before moving on.
- For each target slide, run the full thumbnail -> diagnose -> batch_update -> re-thumbnail loop.
- Do 2-4 verified passes on that slide as needed before advancing to the next one.
- If the same formatting defect keeps recurring because of shared structure, escalate to [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md) instead of hand-patching every slide forever.

4. Keep a global style memory.
- Reuse the same margin logic, title placement, image sizing style, and spacing rhythm across similar slides.
- If one slide establishes a strong layout pattern, align sibling slides to it unless the content demands a different structure.

5. Report what changed.
- Summarize which slides were updated, what categories of issues were fixed, and any slides that still need human taste decisions.

## Editing Guidance For Raw Slides Requests

The Slides connector exposes raw `batch_update` requests. That means:
- Always inspect the current slide before editing.
- Use object IDs from the live slide state, not guessed IDs.
- Prefer reversible, geometric edits first: transform, size, alignment, deletion only when clearly safe.
- If a text box is too dense, try resizing or moving it before shortening the text.

## Failure Policy

- If the thumbnail action is unavailable, say that visual verification is blocked and fall back to structural cleanup only if the user still wants that.
- If the runtime lacks the Slides edit action, stop and say the deck can be diagnosed but not corrected from Codex.
- If repeated passes do not improve the slide, stop and explain what remains subjective or structurally constrained.

## Example Prompts

- `Use $google-slides-visual-iteration to fix the alignment and overlap issues on slide 4 of this Google Slides deck.`
- `Use $google-slides-visual-iteration to clean up this entire deck and make the slide layouts feel consistent.`
- `Import this PPTX into Google Slides, then use $google-slides-visual-iteration to polish each slide with thumbnail-based verification.`
- `Use $google-slides-visual-iteration to make this existing Google Slides deck look better and fix the formatting issues.`
- `Use $google-slides-visual-iteration to clean up spacing, overflow, and alignment in this shared Google Slides link.`
