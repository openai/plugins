# Thumbnail Visual Verification

When to read: always, before any Slides write and again after every `mcp__codex_apps__google_drive_batch_update_presentation` call. This is also required for slide summaries or inspections where visual content matters.

Do not call visual work done from API success alone. After any batch update, every touched slide is done only after a fresh thumbnail has been fetched, inspected as an image artifact or curled from `contentUrl`, checked against the visual criteria, patched if needed, and rechecked.

## Plan The Scope

Before the first visual write, make a plan of all slides that require visual checking.

Enumerate the slides with stable local labels and their live slide object IDs:

```md
- slide_0: title_slide_object_id
- slide_1: metrics_slide_object_id
- slide_2: appendix_slide_object_id
```

Use live slide object IDs from connector reads; do not guess element IDs. For multi-slide work, finish the loop for `slide_N` before starting `slide_N+1`.

## Fetch And Inspect Thumbnails

Fetch a large thumbnail before reviewing a slide:

```ts
const thumbnail = await tools.mcp__codex_apps__google_drive_get_slide_thumbnail({
  presentation_id,
  slide_object_id: "title_slide_object_id",
  thumbnail_size: "LARGE",
});
```

If the response includes an image artifact, inspect that image directly. If the response includes a `contentUrl`, always curl it to a fresh local PNG before visual judgment:

```bash
curl -L "$contentUrl" -o /tmp/slides-thumb-slide_0.png
```

After every patch, fetch a new thumbnail. If it includes a `contentUrl`, curl it to a new filename, for example:

```bash
curl -L "$contentUrl" -o /tmp/slides-thumb-slide_0-v2.png
```

Never reuse a pre-patch thumbnail as proof that a patch worked. Do not claim visual inspection from slide JSON, text extraction, geometry, or thumbnail metadata alone.

## Per-Slide Loop

For each planned slide, in order:

1. Fetch the thumbnail.
2. If the thumbnail has a `contentUrl`, curl it to a fresh local PNG; otherwise inspect the returned image artifact.
3. Check the slide against every criterion below.
4. Write down the visible issues and the focused patch.
5. Apply a focused `mcp__codex_apps__google_drive_batch_update_presentation` call.
6. Fetch a fresh thumbnail.
7. If the fresh thumbnail has a `contentUrl`, curl it to a new local PNG; otherwise inspect the returned image artifact.
8. Verify the slide against the original criteria.
9. If any criterion still fails, patch and recheck again.
10. Move to the next slide only after the current slide passes or has a concrete blocker.

## Release-Blocker Checklist

A deck is passed only when all slides passes the following:

A slide passes only when all are true:

1. No text is clipped, truncated, or cut off.
2. No text overlaps another text box, table row, chart, card, footer, or page edge.
3. Titles, subtitles, and kickers do not collide or crowd each other.
4. Table text stays inside row and column bounds.
5. KPI/card labels and values fit inside their cards.
6. Footnotes and source text are readable and inside the bottom safe margin.
7. Top and bottom spacing are even and ample; content does not feel crowded against either edge.
8. No element extends beyond the slide boundary unless intentionally full-bleed.
9. Repeated elements are aligned consistently.
10. Charts and images occupy the intended footprint and do not leave stale placeholders.

If any check fails, the task is not complete.

## Final Sweep

After the last slide passes, fetch fresh thumbnails for the full edited scope. A contact sheet is allowed as a final sanity check, but it does not replace the per-slide loop.
