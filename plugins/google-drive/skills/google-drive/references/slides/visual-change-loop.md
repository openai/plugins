# Visual Change Loop

Use this recipe whenever a Slides write can change anything the user will see, even if the request started as a content update instead of a formatting cleanup.

## Use When

- A `batch_update` can change text flow, geometry, spacing, alignment, fills, borders, connector strokes, arrow direction, accent bars, chart placement, or other rendered styling.
- The task updates both text and nearby non-text elements such as arrows, bars, borders, or icons.
- A write is supposed to preserve the current layout, but the visible result could still drift because text reflow, shape replacement, or geometry changes are involved.

## Loop

1. Ground the slide before the first write.
- Read the current slide structure with live object IDs.
- Identify the full local edit cluster, not just the most obvious text box.
- For metric cards or scorecards, treat the main value, target value, delta text, arrow, accent bar, and nearby border or connector as one cluster.

2. Start with a thumbnail.
- Fetch a `LARGE` thumbnail when spacing, clipping, or shape alignment matters.
- Use that thumbnail as the source of truth for visual quality.
- Write down the 2-4 concrete visible issues you are fixing in the next pass.

3. Choose the correct raw edit family.
- Use text requests for text content.
- Use `updateShapeProperties` for fills and borders on existing shapes.
- Use `updateLineProperties` for connector or line strokes.
- If the element is the wrong shape type, or too broken to patch safely, delete and recreate it in the same footprint.
- Do not call an element blocked until you have classified it as a shape, line or connector, or image.

4. Make one coherent write pass.
- Batch the related fixes for that local issue cluster together.
- Include `write_control` when a fresh revision token is available.
- Prefer geometry and styling fixes that materially improve the slide over tiny nudges that leave obvious problems behind.

5. Verify immediately.
- Fetch another thumbnail right after the write.
- Confirm both text and non-text visual targets actually changed.
- If the write fixed the main text but left stale bars, arrows, borders, wrapping, or collisions, the slide is not done.

6. Run a second and third fresh review loop.
- Start each additional loop from a fresh thumbnail review, not from memory.
- Re-read the live slide structure before any additional pass.
- Do not call the slide done after pass 2, even if it looks close.
- Only stop after the third fresh review finds nothing materially worth changing.

## Stop Or Escalate

- Stop when the third fresh review finds no meaningful remaining issue.
- Continue to a fourth loop only if the slide still has visible defects after the third review.
- Escalate to [google-slides-template-surgery](./template-surgery.md) when repeated passes still cannot cleanly fix the structure or when the same defect repeats across multiple slides.
