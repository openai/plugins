# Google Slides Template Migration

Use this reference when the user has:
- a source deck whose content should be kept
- a target template deck whose visual system should be adopted

This is not the same as cleanup or template surgery.
- For local polish, prefer [google-slides-visual-iteration](./visual-iteration.md).
- For fixing a broken repeated pattern inside one deck, prefer [google-slides-template-surgery](./template-surgery.md).
- Use this reference when the right answer is to rebuild slides from the template, not keep nudging the old layout.
- When the content comes from notes, a changelog, or another generated source, outline what each slide should say before choosing a template slide.

## Required Tooling

Confirm the runtime exposes:
- `get_presentation` or `get_presentation_text`
- `get_slide`
- `get_slide_thumbnail`
- `batch_update`

If the user is starting from a local `.pptx`, also confirm `import_presentation`.

## Core Workflow

1. Identify the two decks.
- Source deck: the content to preserve.
- Template deck: the company deck or branded presentation whose layout language should be reused.

2. Plan the target slide story before editing.
- Build or confirm an outline of what each migrated slide should communicate.
- For each slide, write down its narrative job, must-keep content, likely density, and whether it needs an image, chart, grid, or mostly text.
- If a source slide is trying to do two jobs at once, such as summary plus evidence, split it in the outline before choosing a template pattern.

3. Read both decks before editing.
- Build a slide inventory for the source deck.
- Build a pattern inventory for the template deck.
- Use thumbnails, not just JSON, to understand the template’s real visual system.

4. Map source slides to template archetypes.
- Classify source slides into a small set of types such as title, section divider, agenda, metrics, 2-column content, image-heavy, quote, or appendix.
- Match by narrative job and density first, then by visual similarity.
- Find the closest matching template slide for each type.
- Read `./references/slide-archetype-mapping.md` when deciding the mapping.

5. Duplicate from the template, not from the source.
- Prefer duplicating the closest matching template slide and then adapting it.
- Do not try to “convert” the old slide in place when a clean template pattern already exists.

6. Port content into the duplicated template slide.
- Replace title and body text.
- Move charts, images, and supporting copy into the template structure.
- Preserve the message and evidence, but let the template control spacing, hierarchy, and visual rhythm.
- Fill the template with intention. Do not leave a slide or major text box looking half-empty unless the template clearly calls for airy whitespace.

7. Verify every migrated slide with thumbnails.
- Re-check the migrated slide after each content port.
- If content does not fit the template cleanly, split it into multiple slides instead of overcrowding the layout.

8. Finish with a deck-wide consistency pass.
- Normalize title treatment, image sizing, section-divider behavior, and spacing rhythm across the migrated deck.

## Migration Rules

- Decide what each slide needs to say before deciding what template slide to use.
- The template is the source of truth for layout, margins, hierarchy, and decorative style.
- The source deck is the source of truth for content.
- Preserve content by default; do not silently drop claims, bullets, data, or charts just to make the slide fit.
- Choose the template slide that matches the slide's narrative job and content density, not the one that merely looks close at first glance.
- When a source slide is denser than the template pattern allows, split the content across multiple template-based slides.
- Avoid excessive whitespace inside major text or content regions. If a box or slide feels underfilled, choose a better template archetype, combine related content, or rewrite the outline rather than leaving a weak composition.
- If no template archetype fits cleanly, split the source content or flag the slide for human design judgment instead of forcing a bad fit.
- Keep the migration deterministic. One source slide should map to one explicit template archetype or a deliberate split.

## Preferred Strategy

Use this order:

1. Migrate a small representative set first.
- Start by validating the outline and archetype choices, not by bulk-copying content.
- Title slide
- One section divider
- One dense content slide
- One image or chart slide

2. Verify that the template mapping is working.
- If those look good, continue with the rest of the deck.
- If not, adjust the archetype mapping before bulk migration.

3. Roll out by slide family.
- Migrate all section dividers together.
- Then title/content slides.
- Then charts/images.
- Then appendix or oddballs.

## What To Avoid

- Do not restyle the old deck slide by slide with ad hoc geometry edits if the template already has a clean pattern.
- Do not paste fresh content into an arbitrary template slide before deciding the slide's job and density.
- Do not force all source slides into one template layout.
- Do not keep decorative source shapes unless they are required content.
- Do not accept a migrated slide that is on-brand but less legible than the source.

## Verification Standard

A migration pass is only done when:
- the migrated slide is visibly consistent with the company template
- the source content still exists and is readable
- no clipping, overlap, or awkward density was introduced
- the main content areas feel intentionally filled rather than sparse by accident
- sibling slides of the same type look like they belong in the same deck

## References

Read these before migrating beyond the first few slides:
- `./references/migration-playbook.md`
- `./references/slide-archetype-mapping.md`
