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
Use the connector actions directly in the conversation workflow. Do not open a shell, `js_repl`, or local script just to inspect connector output shapes for this skill.

## Default Approach

1. Clarify scope.
- Determine whether the user wants one slide fixed or the whole presentation.
- If multiple slides need cleanup, still process formatting slide by slide unless a single repeated structural fix is clearly safer.
- Preserve content by default. Do not rewrite copy unless the user asks or layout cannot be fixed any other way.

2. Read structure before editing.
- Use `get_presentation` or `get_presentation_text` to identify slide order, titles, and object IDs.
- Use `get_slide` on the target slide before the first write so you have the current element structure and IDs.
- Before each additional write pass on that same slide, call `get_slide` again so the next `batch_update` uses fresh geometry and current element state rather than stale structure from the prior pass.

3. Start with a thumbnail.
- Call `get_slide_thumbnail` first.
- Fetch the thumbnail for the current slide only. Do not prefetch thumbnails for the rest of the deck before starting the current slide's edit loop.
- Use `LARGE` when spacing, overlap, cropping, or dense layouts are the concern.
- Treat the thumbnail as the source of truth for visual quality. Raw JSON alone is not enough.
- When the tool returns a thumbnail artifact, image content, or image-bearing URL/data wrapper, treat that as analyzable visual input for this workflow and inspect it directly.
- If `get_slide_thumbnail` succeeds, treat that as the visual verification path for this workflow even if the transcript view looks metadata-shaped. Do not abandon the thumbnail loop just because the runtime shows a thumbnail artifact, URL, or metadata wrapper instead of inline pixels in the message body.
- Do not run shell commands, `js_repl`, or ad hoc parsing code to "decode" the thumbnail response for this skill. Use the connector result directly.
- Do not switch to deck export, PDF rendering, or other fallback rendering paths when the thumbnail tool already succeeded. Only use a fallback path if the thumbnail action itself failed or is unavailable.

4. Diagnose concrete visual problems.
- Before editing a slide, list the specific visible issues back to the user for that slide.
- Do not keep the diagnosis implicit. The user should be able to see what you think is wrong before the first `batch_update` pass.
- Limit the issue list to the 2-4 most important issues on that slide for the current pass.
- Look for text too close to edges or neighboring elements.
- Look for text overflow, clipping, or density that makes the slide feel compressed.
- Look for overlapping text boxes, shapes, charts, and images.
- Look for misaligned images, cards, icons, and text blocks.
- Look for grouped boxes, cards, or sections whose header text, body starts, icons, or internal padding do not sit on the same visual plane.
- Look for inconsistent emphasis such as one label or bullet line being bolded differently from its siblings without intent.
- Look for uneven alignment, broken grid structure, inconsistent spacing, off-center titles, awkward margins, and clipped elements.
- Look for image distortion, poor crops, weak hierarchy, and slides that feel heavier on one side without intent.
- Look for visual regressions introduced by the previous pass before adding more polish.
- Prioritize legibility and collisions first, then alignment/spacing, then aesthetic polish.

5. Make one coherent edit pass.
- Use `batch_update` to fix the current issue cluster for that slide, not just a tiny nudge that leaves the main problems untouched.
- Be aggressive enough to materially improve the slide in each pass. Do not make timid edits that technically move elements but leave the slide still looking broken.
- Batch related fixes together when they affect the same slide structure, such as overflow plus alignment plus inconsistent spacing in one column or card set.
- Prefer moving, resizing, reflowing, redistributing, or re-aligning existing elements over rewriting the slide.
- If multiple boxes or sections are part of a visible group, align their headers, icons, top text baselines, and body starting positions unless the stagger is clearly intentional.
- Do not default to shrinking font size, tightening line spacing, or squishing elements closer together just to make the slide fit.
- If content still does not fit cleanly after a reasonable structural pass, split the content across slides or escalate to [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md) instead of repeatedly compressing the layout.
- Keep each pass narrow enough that the effect is understandable, but strong enough to visibly improve the slide.
- When a fresh revision token is available from the runtime, include `write_control`; otherwise omit it and keep batches small.

6. Verify immediately.
- Call `get_slide_thumbnail` again after every batch update.
- State which issues are now fixed, which issues remain, and whether the pass introduced any new regressions.
- Confirm the targeted issue cluster is actually fixed before moving on.
- If a fix introduced a new collision, imbalance, or cramped layout, correct that next instead of blindly continuing.
- After each verification thumbnail, do a fresh read of the current slide before the next write pass if more edits are needed.

7. Iterate a few times, then stop.
- Run at least 2 full visual loops per slide in this skill.
- Do not stop after a single pass just because the first verification looks acceptable.
- The second loop must start with a fresh thumbnail review and refreshed slide structure so you can catch residual spacing, alignment, padding, and balance issues that were easy to miss in the first pass.
- After the second verified loop, continue to a third or fourth loop only if the slide still has meaningful issues.
- Only stop after the second loop if that fresh review finds nothing materially worth changing.
- Stop when further edits are becoming subjective or are not improving the slide.
- Escalate to [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md) when a slide still has structural layout problems after 2-4 verified passes, or when the same issue repeats across multiple slides.

## Slide-Level Heuristics

Apply these in order:

1. Legibility
- No clipped text.
- No elements touching or nearly touching unless intentionally grouped.
- Keep comfortable padding between text and container edges.
- Text inside a box, card, or shape should not sit uncomfortably close to that container's border. If the padding looks cramped in the thumbnail, treat it as a defect and fix it.

2. Structure
- Align related elements to a shared left edge, center line, or grid.
- Normalize spacing between repeated items.
- Remove accidental overlaps before style refinements.
- When a container or shape is too small for its text, prefer resizing the container or redistributing the layout over tolerating cramped text padding.
- When multiple cards or panels are presented as siblings, keep their header text, icon blocks, and first body lines aligned on consistent horizontal and vertical planes.

3. Balance
- Avoid slides that are top-heavy or left-heavy unless it is a deliberate composition.
- Resize or reposition oversized images/shapes that dominate the slide without helping the message.

4. Consistency
- Keep repeated bullets, labels, captions, and card headings consistent in weight, alignment, and spacing unless the difference is intentional.
- If a row or family of elements should look parallel, treat one-off bolding, indentation, or sizing differences as defects to fix.
- If three or more boxes read as a set, treat mismatched header heights, top padding, or body-start positions as alignment defects even when the text itself is different lengths.

5. Restraint
- Do not churn the whole slide if one local fix is enough.
- Do not invent new decorative elements unless the user explicitly wants a redesign.
- Do not treat compression as polish. A slide that only fits because everything was squeezed tighter is still broken.
- Do not stop after a cosmetic near-fix. If the text is still cramped against a border, still visually crowded, or still obviously misaligned, keep editing.

## Deck-Wide Mode

If the user asks to improve the whole presentation:

Core rule:
- A whole-deck cleanup request still uses one-slide-at-a-time iteration. It does not mean "scan the whole deck first and then start editing."

1. Read the presentation first and make a slide inventory.
- Note the title slide, section dividers, dense slides, image-heavy slides, and obvious outliers.
- Keep that inventory lightweight. Do not present one giant deck-wide issue dump before editing.

2. Prioritize the slide order.
- If the user asked for the whole deck, start with slide 1 in the requested scope, finish slide 1, then move to slide 2, then slide 3, and continue in order until the last slide in scope.
- Do not skip ahead to later slides just because they look worse unless the user explicitly asked you to prioritize certain slides.
- Within each slide, address overlap, clipping, unreadable density, and broken crops before moving on to spacing, alignment, title placement, image treatment, and consistency.

3. Finish each slide before moving on.
- For each target slide, run the full thumbnail -> diagnose -> batch_update -> re-thumbnail loop.
- Work strictly sequentially: finish the current slide before starting issue diagnosis for the next slide.
- Do not fetch thumbnails for later slides while the current slide is still in progress unless the user explicitly asked for a separate audit.
- Start each slide with an explicit list of the 2-4 key issues on that slide only.
- Fix that slide before moving to the next one. Do not diagnose the whole rest of the deck in detail while the current slide is still unresolved.
- End each pass with a fixed-vs-remaining issue summary for that slide only.
- Do at least 2 verified loops on that slide before advancing to the next one.
- Do not say a slide needs no second pass until you have actually completed the second fresh review loop on that slide.
- Between loops, re-read the current slide structure so follow-up writes use fresh state rather than stale element geometry.
- If the same formatting defect keeps recurring because of shared structure, escalate to [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md) instead of hand-patching every slide forever.

4. Keep a global style memory.
- Reuse the same margin logic, title placement, image sizing style, and spacing rhythm across similar slides.
- If one slide establishes a strong layout pattern, align sibling slides to it unless the content demands a different structure.

5. Report what changed.
- Summarize which slides were updated, what categories of issues were fixed, and any slides that still need human taste decisions.

## Output Conventions

- Before the first edit pass on a slide, show a short issue list for that slide so the user can see what will be fixed.
- In deck-wide mode, narrate progress in strict slide order, for example `slide 1`, then `slide 2`, then `slide 3`, until the last slide in scope.
- Keep deck-wide work slide-scoped in the narration: talk about the current slide's issues, fixes, and remaining defects before moving on to another slide.
- After each pass, separate `fixed`, `remaining`, and `new regressions` clearly instead of giving a vague progress note.
- Do not announce `none that require a second pass` after pass 1. Complete the second slide-local loop first, then decide whether the slide is done.
- Keep the issue list concrete and visual, for example `text overflow in right card`, `image misaligned with left column`, or `middle bullet line is bolded inconsistently`.
- Do not open with a broad deck-wide cluster like `slides 3, 4, 7, 8, and 10 all have...` unless the user asked for an audit instead of an iteration workflow.
- Do not narrate a future-slide plan like `I am fetching the rest of the deck now` before finishing the current slide.
- Do not narrate internal runtime debugging like `I am probing the connector output shape` or `I am writing the export locally to inspect it` during this workflow.

## Editing Guidance For Raw Slides Requests

The Slides connector exposes raw `batch_update` requests. That means:
- Always inspect the current slide before editing.
- Keep the tool loop local to the current slide: one slide thumbnail in, one slide edit pass, one verification thumbnail out.
- Use object IDs from the live slide state, not guessed IDs.
- Prefer reversible, geometric edits first: transform, size, alignment, deletion only when clearly safe.
- If a text box is too dense, try resizing, redistributing, or reflowing the slide before shortening the text.
- If the only apparent fix is to compress all the content tighter, stop and reconsider the layout pattern instead of blindly applying that edit.

## Failure Policy

- If the thumbnail action is unavailable, say that visual verification is blocked and fall back to structural cleanup only if the user still wants that.
- If the thumbnail action succeeded, do not claim that visual verification is blocked just because the response was wrapped as metadata or a separate artifact in the runtime transcript.
- If the thumbnail action succeeded, do not switch into shell/REPL inspection, local export inspection, or connector-shape debugging. Stay in the slide-local thumbnail loop.
- If the runtime lacks the Slides edit action, stop and say the deck can be diagnosed but not corrected from Codex.
- If repeated passes do not improve the slide, stop and explain what remains subjective or structurally constrained.

## Example Prompts

- `Use $google-slides-visual-iteration to fix the alignment and overlap issues on slide 4 of this Google Slides deck.`
- `Use $google-slides-visual-iteration to clean up this entire deck and make the slide layouts feel consistent.`
- `Import this PPTX into Google Slides, then use $google-slides-visual-iteration to polish each slide with thumbnail-based verification.`
- `Use $google-slides-visual-iteration to make this existing Google Slides deck look better and fix the formatting issues.`
- `Use $google-slides-visual-iteration to clean up spacing, overflow, and alignment in this shared Google Slides link.`
