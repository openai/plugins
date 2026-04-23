# Read Before Write And Deck Scope

When to read: deck summaries, evidence searches, multi-slide edits, translation, or any deck-wide change.

## Read First

1. Use connector reads to capture slide order, titles, object IDs, and the requested scope.
2. Use `get_slide` before slide-level writes so object IDs and geometry come from the live deck.
3. For Q&A or evidence-finding, build a candidate slide list and inspect every plausible slide in the relevant section.
4. For charts, screenshots, diagrams, or image-heavy slides, pair text/structure reads with thumbnails.

## Multi-Slide Checklist

1. Build an ordered checklist before the first write.
2. Record slide numbers, slide object IDs, and short titles or roles.
3. Do not infer coverage from object ID numbering.
4. Work in one slide or a small contiguous span at a time.
5. Re-read each edited slide or span before advancing.
6. Confirm the last slide in a span actually changed.
7. Before handoff, reconcile the final deck against the original checklist.

## Source And Destination

When using multiple decks, identify source decks and slides before writing to the destination. Re-confirm the destination deck before every write batch.
