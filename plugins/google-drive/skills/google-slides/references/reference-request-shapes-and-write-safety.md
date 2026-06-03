# Request Shapes And Write Safety

When to read: any task that writes through Slides connector APIs.

## Batch Update Shape

Always pass `requests` as structured request objects, not stringified JSON.

Bad:

```json
{"requests":["{\"deleteObject\":{\"objectId\":\"shape1\"}}"]}
```

Good:

```json
{"requests":[{"deleteObject":{"objectId":"shape1"}}]}
```

## Live Object IDs

1. Read the presentation and target slide before writing.
2. Use object IDs from the live slide state.
3. For new objects, use valid Google Slides IDs: 5-50 characters, starting with an alphanumeric character or underscore.
4. If creating a slide and editing placeholders in one batch, create valid placeholder ID mappings first and reference those IDs later in the same batch.
5. For template/reference-deck work, build a slot map from the live slide state before creating new page elements. Prefer existing placeholder, text, image, chart, and table object IDs over new object IDs for primary content.

## Duplicated Slide Ordering

When duplicating slides that must land in a specific sequence, use a two-pass workflow:

1. First call `duplicateObject` only. Do not combine `duplicateObject` and `updateSlidesPosition` in the same batch.
2. Re-read the presentation outline after the duplicate batch completes. Record the actual slide order and the new slide object IDs returned or observed.
3. If the new slides are not already in the intended sequence, run a separate `updateSlidesPosition` batch using the observed slide object IDs in their current presentation order. Google rejects move requests when `slideObjectIds` are not listed in current presentation order.
4. Only rewrite slide content after the new slides exist and their order is grounded, unless the content rewrite does not depend on slide order.
5. Never change the requested story/content order to match an accidental duplicate order. Fix the slide order instead.

## Inserted Layout Placeholder Contract

This applies to any slide created from a layout, including existing-deck edits. It is not limited to template/reference-deck copy workflows.

1. After `createSlide` with `slideLayoutReference` or `predefinedLayout`, re-read the new slide before final handoff and inventory every inherited placeholder object exposed by the connector, including `shape.placeholder`, image placeholder metadata, table placeholder metadata, or equivalent layout/master placeholder fields.
2. Treat title, body, picture, chart, table, and other content-bearing placeholders as required slots unless they are clearly decorative, a slide number, a footer, or another non-content element.
3. Prefer `placeholderIdMappings` when you need to edit layout placeholders in the same batch as `createSlide`; otherwise use the generated placeholder object IDs from the post-create slide read.
4. Fill, replace, or intentionally delete every inherited content-bearing placeholder. Empty placeholder objects are unresolved even when they contain no visible prompt text.
5. Do not create new primary text, image, chart, table, or diagram objects while a suitable inherited placeholder remains empty. If the layout does not have the right slots for the intended content, choose a different layout/exemplar or split the content.
6. If a placeholder is not part of the intended final design, delete it explicitly with `deleteObject` after grounding the slide and confirming the object ID.
7. Thumbnail checks are necessary but insufficient for this contract because empty inherited placeholders may be invisible in rendered thumbnails. The final check must inspect connector JSON for unresolved placeholder metadata.

## Geometry Safety

1. Treat the slide page size as a hard boundary.
2. Keep text boxes, images, tables, and shapes inside the slide bounds unless intentionally full-bleed.
3. Slides transforms place an element's upper-left corner, not its center.
4. Before moving or resizing, classify the object as text box, shape, line/connector, image, table, or chart.
5. Use small batches and re-read the slide after writes that change text flow, geometry, or object membership.

## Destructive Writes

1. Before deleting, replacing, or rewriting multiple slides, state or record exactly which slides and objects will change.
2. Preserve slide order, titles, notes, charts, source evidence, and unrelated elements unless the user asked to change them.
3. Do not layer new primary content over stale placeholders. Delete or replace the obsolete placeholder once the target is grounded.

## New Object Restraint

1. Do not use `createShape` or `createImage` as the default way to add primary content to a copied template/reference slide or a slide inserted from a layout.
2. First look for an existing editable slot: a placeholder, text box, image frame, chart frame, table cell, or reusable non-placeholder object from the exemplar slide.
3. If the chosen slide lacks a suitable slot, choose a different exemplar/layout or split the content before adding freeform primary content.
4. When a new object is necessary, record its object ID and reason, keep it aligned to the selected slide pattern, and verify that no existing content-bearing placeholder or template scaffold was bypassed.
