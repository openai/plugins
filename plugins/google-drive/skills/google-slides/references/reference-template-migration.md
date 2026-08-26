# Template Migration

When to read: moving source deck content onto a target template deck.

If the user asks for a new deck that follows a provided native Google Slides template or reference deck, read `reference-template-reference-deck-copy-workflow.md` first. Create the destination by copying the provided deck directly, then use this migration reference for content mapping details as needed.

Read `reference-slide-planning-and-layout-selection.md` and `reference-slide-archetype-mapping.md` before migrating beyond the first few slides.

## Workflow

1. Identify the source deck and template deck.
2. Read both decks, including thumbnails for template patterns.
3. Inventory each source slide's substantive text, evidence visuals, charts, tables, links, media objects, and non-empty speaker notes.
4. Define each target slide's narrative job, visual orientation, evidence type, and hierarchy before choosing a layout.
5. Map source slides to template archetypes by narrative job, density, orientation, hierarchy, and semantic intent; use sample labels and compositions as archetype metadata rather than treating slides as interchangeable slot collections.
6. Duplicate from the template, not from the source deck.
7. Port source content into the duplicated template slide by replacing existing template slots first, preserving meaningful style runs and speaker notes.
8. Verify each migrated slide with connector readback, source comparison, and thumbnails.
9. Choose a denser archetype rather than forcing content into a bad fit. Split a source slide only when the user's requested slide-count contract allows it.
10. Finish with a deck-wide consistency and fidelity pass.

## Mapping Rules

- Source deck is truth for substantive content, evidence, links, media intent, and speaker notes.
- Template deck is truth for layout, margins, hierarchy, and style.
- Match by narrative job first: title, section divider, agenda, dense content, metrics/dashboard, image-heavy, quote, or appendix.
- Treat template sample text and defining artwork as semantic signals. Presentation-title, section-opener, phone-demo, quote, summary, total, and status treatments are not interchangeable.
- Preserve claims, bullets, charts, evidence visuals, links, and non-empty speaker notes unless the user asks otherwise.
- For exact migrations, do not silently summarize, shorten, or omit source content.
- Keep repeated roles such as section dividers in a consistent template family.
- Match evidence frames by orientation and required readable area; do not force a landscape screenshot into a portrait frame merely because both use one image slot.
- Do not restyle the old deck slide by slide when a clean template pattern exists.
- Do not leave major template regions accidentally empty.
- Do not bypass usable template placeholders, image frames, tables, charts, or reusable non-placeholder text objects by placing primary content in new freeform objects.
- If the chosen template slide lacks the right content slots, choose another archetype or split the content.
- If no template archetype fits, split the content or flag the slide for human design judgment.

## Verification

Migration is complete only when every migrated slide is presentation-readable, visibly template-consistent, source-faithful, free of unintentional placeholder/sample scaffolding, and checked with both connector readback and a fresh thumbnail after visible writes. Final readback must reconcile text, visuals, charts, tables, links, media type, and non-empty speaker notes.
