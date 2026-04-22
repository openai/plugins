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

## Geometry Safety

1. Treat the slide page size as a hard boundary.
2. Keep text boxes, images, tables, and shapes inside the slide bounds unless intentionally full-bleed.
3. Slides transforms place an element's upper-left corner, not its center.
4. Before moving or resizing, classify the object as text box, shape, line/connector, image, table, or chart.
5. Use small batches and re-read the slide after writes that change text flow, geometry, or object membership.

## Destructive Writes

1. Before deleting, replacing, or rewriting multiple slides, state or record exactly which slides and objects will change.
2. Preserve slide order, titles, notes, charts, source evidence, and unrelated elements unless the user asked to change them.
3. Do not layer new charts or images over stale placeholders. Delete or replace the obsolete object once the target is grounded.
