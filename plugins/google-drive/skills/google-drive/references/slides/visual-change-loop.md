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
- If two adjacent text boxes are colliding, wrapping into each other, or visually fighting for the same lane, treat them as one cluster and fix their geometry together.
- For overflow or collision-sensitive work, use both signals from the start: the slide thumbnail for rendered appearance and the live slide structure for text-box geometry and neighboring object placement.

2. Start with a thumbnail.
- Fetch a `LARGE` thumbnail when spacing, clipping, or shape alignment matters.
- Inspect the image returned by `get_slide_thumbnail` directly. That may appear as an `image_asset_pointer`, an image content part, or another rendered image artifact in the tool response; do not require base64 bytes before starting visual review.
- If the thumbnail response only provides a thumbnail URL or `contentUrl`, save the rendered image locally with `curl -L "$contentUrl" -o /tmp/slides-thumb-<slide-id>.png` before visual review.
- Use the returned image artifact or the saved local PNG as the visual source of truth for overlap, clipping, padding, footer collisions, text rendering, and shape alignment.
- Use that thumbnail as the primary visual signal, but not as the only signal for overflow or collision checks.
- After overlap and overflow checks, apply the Text Alignment Guideline below to the slide.
- Write down the 2-4 concrete visible issues you are fixing in the next pass.

3. Choose the correct raw edit family.
- Use text requests for text content.
- Use `updateShapeProperties` for fills and borders on existing shapes.
- Use `updateLineProperties` for connector or line strokes.
- If the element is the wrong shape type, or too broken to patch safely, delete and recreate it in the same footprint.
- Do not call an element blocked until you have classified it as a shape, line or connector, or image.
- When moving or creating a text box, remember Slides transforms are upper-left-based. Do not aim a new text box at another object's center without converting that desired center into the new box's top-left corner.

4. Make one coherent write pass.
- Batch the related fixes for that local issue cluster together.
- Include `write_control` when a fresh revision token is available.
- Prefer geometry and styling fixes that materially improve the slide over tiny nudges that leave obvious problems behind.
- When two neighboring text boxes collide, prefer resizing, repositioning, or redistributing both boxes before shrinking the text. Do not "fix" one box while leaving the adjacent one still cramped.
- Do not stop at "technically updated." The target is a slide that looks intentionally arranged and presentation-ready, not merely one with fewer defects than before.

5. Verify immediately.
- Fetch another thumbnail right after the write.
- If the fresh thumbnail is URL-backed, curl it to a new local PNG and inspect that new file before declaring the pass verified.
- Confirm both text and non-text visual targets actually changed.
- Re-read the live slide structure after the write when text boxes, wrapping, or neighboring layout relationships were in scope.
- If the write fixed the main text but left stale bars, arrows, borders, wrapping, or collisions, the slide is not done.
- If text from one box still overlaps, crowds, or visually crashes into text from an adjacent box, the slide is not done.
- If a new small label looks one line low, visually offset, or miscentered relative to its neighbors, the slide is not done. Re-read the slide and tighten the text box geometry before moving on.
- After overlap and overflow verification, re-check text alignment using the Text Alignment Guideline below before declaring the pass clean.
- If the thumbnail looks cleaner but the refreshed slide structure still suggests narrow, colliding, or suspiciously adjacent text boxes, err on the side of caution and keep working the slide.

6. Run a second and third fresh review loop.
- Start each additional loop from a fresh thumbnail review, not from memory.
- Re-read the live slide structure before any additional pass.
- Run at least 3 full write-and-verify loops whenever this recipe is triggered, even if pass 1 or pass 2 already looks acceptable.
- Do not call the slide done after pass 2, even if it looks close.
- Treat pass 2 as an alignment-and-spacing pass, not a victory lap.
- Treat pass 3 as a polish pass: look for anything that still feels slightly off, uneven, cramped, weakly grouped, or visually unbalanced, even if the slide is already functional.
- Only stop after the third fresh review finds nothing materially worth changing.

## Text Alignment Guideline

Check every slide for text alignment after overlap and overflow checks.

Constants:
- `alignment_tolerance = 4 pt`
- `repeated_size_tolerance = 6 pt`
- `min_internal_padding = 8 pt`

Use `alignment_tolerance` for left/right/top/bottom edges, centerlines, text-box tops, and visible baselines.
Use `repeated_size_tolerance` for peer text boxes, cards, rules, bars, and other repeated layout elements that should share the same width or height.
Use `min_internal_padding` for text inside cards, shapes, table cells, labels, callouts, and buttons.

1. Title / Subtitle Group
- FAIL if title, subtitle, eyebrow, accent rule, or section label left edges differ by more than `alignment_tolerance` unless clearly intentional.
- FAIL if centered title/subtitle text does not share the same visual centerline within `alignment_tolerance`.
- FAIL if title/subtitle vertical gaps differ noticeably from equivalent slides.
- FAIL if a title/subtitle group appears unintentionally shifted relative to the main content grid.

2. Repeated Text Blocks
- For peer cards, rows, columns, timeline items, table cells, or callouts:
- FAIL if heading text-box tops differ by more than `alignment_tolerance`.
- FAIL if body text-box tops differ by more than `alignment_tolerance`.
- FAIL if heading/body left edges differ across peer elements by more than `alignment_tolerance`.
- FAIL if centered text boxes do not share the visual centerline of their card, shape, icon, or peer group within `alignment_tolerance`.
- FAIL if peer text baselines appear uneven, even when box geometry is aligned.
- FAIL if peer text boxes that should match differ in width or height by more than `repeated_size_tolerance`.

3. Text-To-Container Alignment
- FAIL if text intended to be centered in a shape/card is visibly off-center horizontally or vertically by more than `alignment_tolerance`.
- FAIL if text intended to be left-aligned does not share a consistent inset from the container edge within `alignment_tolerance`.
- FAIL if text touches or nearly touches its container edge with less than `min_internal_padding`.
- FAIL if card heading, body, icon, and decorative rule use different alignment anchors without a clear hierarchy reason.

4. Multi-Line Text
- FAIL if wrapped lines create uneven visual starts in repeated peers.
- FAIL if one peer has a very different line count that makes the group feel misaligned.
- FAIL if text-box width changes only to force wrapping but breaks card/grid alignment.
- ALLOW wider text boxes only when centerline or intended inset remains aligned within `alignment_tolerance`.

5. Tables / Lists
- FAIL if row labels, numeric values, bullets, or list text do not share consistent x positions within `alignment_tolerance`.
- FAIL if bullets and their text have inconsistent hanging indents.
- FAIL if numbers meant to compare vertically are not right-aligned or decimal-aligned.
- FAIL if table headers and body cells use visibly different alignment anchors without a clear reason.

6. Deck-Wide Consistency
- FAIL if equivalent slide titles shift x/y positions across normal content slides by more than `alignment_tolerance`.
- FAIL if repeated footer/source/page-number text shifts inconsistently across slides by more than `alignment_tolerance`.
- WARN if a hero/title slide intentionally uses different alignment but still feels balanced.

Preferred Fix Direction
- Align peer text boxes using exact x/y coordinates, not visual nudging.
- Preserve consistent text insets inside repeated cards.
- Match title/subtitle anchors across equivalent slides.
- Center text by matching centerlines, not by eyeballing left edges.
- If wrap fixes require wider text boxes, keep the same centerline or same intended inset as peer elements.
- After edits, verify both geometry and rendered thumbnails.

## Mini Example

- Pass 1: fix the obvious issue cluster, such as clipped text, stale styling, or objects that collide.
- Pass 2: normalize the structure, such as aligning sibling cards, equalizing spacing, or separating rows that still crowd each other.
- Pass 3: polish the slide so it feels deliberate, such as strengthening hierarchy, softening secondary text, or balancing whitespace after the functional fixes are already done.

## Stop Or Escalate

- Stop when the third fresh review finds no meaningful remaining issue.
- Continue to a fourth loop only if the slide still has visible defects after the third review.
- Escalate to [google-slides-template-surgery](./template-surgery.md) when repeated passes still cannot cleanly fix the structure or when the same defect repeats across multiple slides.
