# Template Or Reference Deck Copy Workflow

When to read: the user provides a native Google Slides template deck or prior/reference Slides deck and asks for a new deck that follows its format, style, structure, or layout.

This workflow overrides the local `.pptx` creation and import path for this task class. The point is to preserve the template or reference deck's native masters, layouts, object styles, image frames, charts, page size, and repeated visual conventions by copying it first and editing only the copy.

Read `reference-slide-planning-and-layout-selection.md` and `reference-slide-archetype-mapping.md` for the general planning and layout rules. Read `reference-template-migration.md` as well only when substantive source slides are being migrated and source-to-destination fidelity is part of the request.

## Scope

Use this workflow when all are true:

1. The reference artifact is a native Google Slides URL or presentation id.
2. The requested deliverable is a new Google Slides deck.
3. The new deck should follow the provided deck's format, template, layout system, or prior-event structure.

If the provided reference is a local `.pptx`, `.ppt`, or `.odp`, first follow `reference-import-presentation.md` to create a native Google Slides deck, then continue here only after native conversion and readback have succeeded.

## Workflow

1. Identify the provided template/reference deck and the source material for new content.
2. Read the provided deck with `get_presentation` and, when helpful, `get_presentation_outline`; record presentation id, title, slide count, page size, slide object IDs, layout IDs, masters, revision id, media objects, links, and non-empty speaker notes when present.
3. Fetch and inspect thumbnails for representative template/reference slides before choosing exemplars. This is required: do not choose final exemplars from outline text or slot counts alone.
4. Create a new working deck by copying the provided deck directly in Google Drive. Prefer the current template-copy action if exposed; otherwise use the Drive copy action. Set the requested output title during copy when available.
5. Read back the copied deck and record its presentation id, title, URL when available, slide count, slide object IDs, layout IDs, and revision id. From this point on, the copied deck is the destination and the original deck is read-only reference material.
6. Build a slide plan mapping each target slide to an existing exemplar slide in the copied deck whenever possible. Classify by narrative role, content density, visual orientation, evidence type, and hierarchy before considering object count. Use a copied-deck layout only when the layout itself has been inspected and is sufficient for the intended content.
7. For each target slide, build a slot map before writing. Record the existing object IDs, placeholder metadata, object type, geometry, current text/image/chart/table role, mixed text-style runs, semantic emphasis, and whether each object is a reusable content slot, decorative element, footer/header, or obsolete source content.
8. Prefer `duplicateObject` for slides whose format depends on real page elements, image frames, chart frames, decorative shapes, custom footers, non-placeholder text styling, or any object structure beyond simple layout placeholders.
9. Use `createSlide` with `slideLayoutReference.layoutId` only when the copied deck exposes a suitable clean layout, placeholders are enough to recreate the slide, and you have verified the layout does not include visible construction guides or editor-only scaffolding. Use `predefinedLayout` only after verifying the layout exists in the copied deck's current master.
10. Use `placeholderIdMappings` when creating a slide from a layout and you need stable placeholder IDs for same-batch text edits. If creating from a layout, fill the mapped placeholders directly; do not add new freeform boxes while leaving usable placeholders empty.
11. Edit the duplicated or newly inserted slides with focused `batchUpdate` calls: clear and rewrite existing text boxes and table cells, preserve meaningful mixed style runs, replace placeholder or sample text scoped by `pageObjectIds`, replace images or charts in the intended existing footprint, copy non-empty speaker notes only when adapting source slides, and delete obsolete source/reference content including stale template notes.
12. Use `updateSlidesPosition` in a standalone reorder-only batch after creation/duplication when ordering is needed. Do not combine `duplicateObject` and `updateSlidesPosition` in the same batch. Re-read slide order first, then move the exact slide object IDs in their current presentation order. Do not include `deleteObject` or content edits in the same batch. For arbitrary final ordering, prefer moving one slide at a time, commonly from desired last-to-first into insertion index `0`, then re-read the order before cleanup. Do not change agenda/content to match an accidental order caused by a failed reorder.
13. Delete unused template/reference slides only after the target deck's desired slide set has been created, ordered, and verified. Do cleanup in a separate delete-only final batch rather than combining large destructive deletes with slide creation, content edits, or slide reordering.
14. Run connector readback and thumbnail verification for every touched slide after every visible write batch.
15. Maintain a content-coverage checklist for every delivered slide. When adapting source slides, extend it into a source-to-destination fidelity ledger covering substantive text, visuals, charts, tables, links, media type, and speaker notes.
16. Finish with full structural readback to verify the copied deck, not the source deck, is the final editable Google Slides deliverable. Use `get_presentation` or `get_slide` for every delivered slide; `get_presentation_outline` alone is not sufficient for the final template-use validator because it does not expose placeholder metadata, notes, media objects, or object structure.

## Batch Update Patterns

Use only live object IDs from the copied deck.

For duplicating a slide, provide object ID mappings when later same-batch requests need stable IDs:

```json
[
  {
    "duplicateObject": {
      "objectId": "source_exemplar_slide_id",
      "objectIds": {
        "source_exemplar_slide_id": "target_slide_03_metrics",
        "source_title_box_id": "target_slide_03_title",
        "source_body_box_id": "target_slide_03_body"
      }
    }
  }
]
```

If you do not provide mappings, re-read the copied deck after duplication and use the returned IDs for edits.

For creating from a copied deck layout:

```json
[
  {
    "createSlide": {
      "objectId": "target_slide_04",
      "insertionIndex": 3,
      "slideLayoutReference": {
        "layoutId": "layout_from_copied_deck"
      },
      "placeholderIdMappings": [
        {
          "layoutPlaceholderObjectId": "layout_title_placeholder_id",
          "objectId": "target_slide_04_title"
        },
        {
          "layoutPlaceholderObjectId": "layout_body_placeholder_id",
          "objectId": "target_slide_04_body"
        }
      ]
    }
  }
]
```

The `layoutId` and `layoutPlaceholderObjectId` values must come from the copied deck readback. Do not use layout IDs from a different deck unless they were observed on the copy.

## Mapping Rules

- The provided deck is truth for visual language, layout system, margins, recurring objects, and slide archetypes.
- The new content sources are truth for required claims, metrics, examples, dates, narrative, and evidence. When adapting source slides, their links, media intent, and speaker notes are also part of the fidelity contract unless the user says otherwise.
- Treat exemplar labels and sample copy as semantic metadata. A slide labeled or composed as a presentation title, phone demo, quote, summary, total, or section opener should not be repurposed for a different narrative job merely because it has the right number of slots.
- Keep repeated slide roles in a consistent template family unless the content genuinely requires a different archetype.
- Duplicate an exemplar slide when the visual format is richer than layout placeholders.
- Create from a layout only when the layout is sufficient and the desired slide can be populated through existing placeholders or straightforward page elements already supplied by that layout.
- Choose a different exemplar/layout or split the content when the planned content does not fit the chosen slide's existing slots. Do not turn a title-only, image-only, divider, or sparse layout into a dense content slide by adding new primary text boxes.
- For exact migrations, do not silently shorten, summarize, or omit source content. Choose a better archetype, restructure within the slide, or split only when the requested slide-count contract allows it.
- Match image and evidence frames by orientation and information need. Do not force a landscape UI screenshot into a portrait phone frame or crop away labels, thumbnails, source notes, axes, legends, or other essential proof.
- Preserve chart-heavy and evidence-heavy source material. If faithful native reconstruction is impractical, a cropped evidence image is acceptable when it remains readable; do not replace it with a prose-only summary unless the user asked for a rewrite.
- Keep a concise target-slide checklist with target role, source content, chosen exemplar/layout, destination slide object ID, slot map, newly created object IDs if any, and verification status.
- If a reference deck has event-specific content embedded in decorative text boxes, clear it explicitly. Do not leave prior-period titles, dates, speakers, footers, screenshots, notes, or metrics in the new deck unless the user requested them.
- Do not use broad `replaceAllText` across the full copied deck unless every instance should change. Prefer `pageObjectIds` or object-specific `deleteText`/`insertText`.
- When copying a prior-event deck, preserve recurring structure only when it still serves the new deck. Delete or replace stale agenda sections that are not in the new source material.

## Existing Slot First Rule

Primary slide content should land in existing template/reference objects.

- For text, prefer `deleteText` plus `insertText` on the existing text box, placeholder, or table cell. Preserve the object's transform and inherited style. For exact migrations, resolve fit through a better archetype, line breaks, or source-faithful restructuring rather than silently shortening the content.
- Before rewriting a text object, record its style runs and paragraph roles. Preserve heading/body/caption distinctions with explicit ranges; do not apply one style across `ALL` when the exemplar contains meaningful mixed styles.
- For images and charts, prefer replacing the existing image/chart/placeholder footprint. If the API requires creating a replacement image, create it in the same footprint and delete the obsolete object in the same focused batch after the replacement is grounded.
- For tables and cards, edit existing cells or text objects inside the copied slide structure rather than drawing a new grid over the old one.
- Preserve only semantic table/card emphasis that still applies. Neutralize highlighted rows, columns, totals, rankings, or status colors when the destination content does not support the same meaning.
- Treat `shape.placeholder` metadata as a strong sign that the object comes from the layout/master and should be populated or intentionally removed, not bypassed.
- Treat non-placeholder objects in an exemplar slide as reusable template objects when they are part of the slide's design. They may be the correct slots even though they do not have `shape.placeholder`.
- Avoid `createShape` for primary text. Use it only for small labels, annotations, or design elements that are part of the selected slide pattern and cannot be represented by an existing slot. Record the reason in the slide checklist and verify by thumbnail.
- If a slide still has an empty content-bearing placeholder or visible editor prompt after your edits, the slide is not complete. Either populate that placeholder, remove it intentionally, or choose a better exemplar/layout.

## Final Template-Use Validator

Before handoff on a copied template/reference deck, run full connector readback and inspect every delivered slide for template-use failures. Use `get_presentation` or `get_slide` on each delivered slide; do not use outline-only data for this validator.

1. A visible placeholder or reusable content region remains empty even though the slide is meant to carry content there.
2. Generic editor prompts, sample copy, lorem ipsum, TODO/TBD text, or old source-deck content remains in visible slide content unless explicitly requested.
3. Primary content sits in newly created freeform text/image boxes while an appropriate existing slot on the chosen slide remains unused.
4. The chosen slide archetype does not match the content density, causing extra content boxes, crowding, or large accidental empty regions.
5. New objects created during the workflow are not listed in the slide checklist or cannot be justified as small labels, annotations, replacements in an existing footprint, or intentional design elements.
6. Required content, evidence visuals, charts, tables, or links are missing or replaced by a weaker summary. When source-slide fidelity is expected, source text and non-empty speaker notes must not be silently shortened or omitted.
7. When adapting source media, an active and accessible media object changed type or ID without justification. If source media is trashed, inaccessible, deprecated, or intentionally removed, a source-faithful static fallback is acceptable and should be reported as an exception; do not silently substitute a different asset.
8. Mixed heading/body/caption styles were flattened, whitespace-only bulleted paragraphs render stray bullets, or inherited emphasis implies unsupported totals, ranking, grouping, status, or importance.
9. A proof visual is present but no longer interpretable because of crop, scale, orientation mismatch, or unreadable labels and footnotes.
10. Repeated roles such as section dividers or agenda transitions use inconsistent or semantically inappropriate template families.

If any validator item fails, fix the slide before final handoff by using the right existing slot, selecting a better exemplar/layout, splitting the content, or removing obsolete template scaffolding.

## Safety Rules

1. Never write to the provided source/template/reference deck.
2. The copied deck identity must be confirmed before every write batch.
3. Treat target identity as stale after the copy operation, after reading the source deck again, and after any connector error.
4. Do not return the source deck URL as the final deliverable.
5. Do not synthesize a Google Slides URL. Return only a URL or id observed in the copy result or connector readback.
6. Do not call the workflow complete until unused template/reference slides are removed or intentionally retained, final order is correct, the final template-use validator passes, and every changed slide has passed fresh thumbnail verification.

## Final Handoff

Report only the copied Google Slides deck as the deliverable. Name the template/reference deck and copied deck identities verified by connector readback, summarize the slide creation strategy used, and call out any remaining content, fidelity, or human-design exception. When source media was adapted, a brief success confirmation is enough if everything migrated normally; provide slide-specific details only for exceptions. State honestly when charts or complex evidence remain image-based rather than editable.
