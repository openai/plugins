---
name: google-slides-template-migration
description: Migrate a Google Slides deck onto a target template. Use when the user wants to preserve source content while rebuilding slides from a branded template structure instead of making incremental in-place edits.
---

# Google Slides Template Migration

Use this skill when the user has:
- a source deck whose content should be kept
- a target template deck whose visual system should be adopted

This is not the same as cleanup or template surgery.
- For local polish, prefer [google-slides-visual-iteration](../google-slides-visual-iteration/SKILL.md).
- For fixing a broken repeated pattern inside one deck, prefer [google-slides-template-surgery](../google-slides-template-surgery/SKILL.md).
- Use this skill when the right answer is to rebuild slides from the template, not keep nudging the old layout.

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

2. Read both decks before editing.
- Build a slide inventory for the source deck.
- Build a pattern inventory for the template deck.
- Use thumbnails, not just JSON, to understand the template’s real visual system.

3. Map source slides to template archetypes.
- Classify source slides into a small set of types such as title, section divider, agenda, metrics, 2-column content, image-heavy, quote, or appendix.
- Find the closest matching template slide for each type.
- Read `./references/slide-archetype-mapping.md` when deciding the mapping.

4. Duplicate from the template, not from the source.
- Prefer duplicating the closest matching template slide and then adapting it.
- Do not try to “convert” the old slide in place when a clean template pattern already exists.

5. Port content into the duplicated template slide.
- Replace title and body text.
- Move charts, images, and supporting copy into the template structure.
- Preserve the message and evidence, but let the template control spacing, hierarchy, and visual rhythm.

6. Verify every migrated slide with thumbnails.
- Re-check the migrated slide after each content port.
- If content does not fit the template cleanly, split it into multiple slides instead of overcrowding the layout.

7. Finish with a deck-wide consistency pass.
- Normalize title treatment, image sizing, section-divider behavior, and spacing rhythm across the migrated deck.

## Migration Rules

- The template is the source of truth for layout, margins, hierarchy, and decorative style.
- The source deck is the source of truth for content.
- Preserve content by default; do not silently drop claims, bullets, data, or charts just to make the slide fit.
- When a source slide is denser than the template pattern allows, split the content across multiple template-based slides.
- Keep the migration deterministic. One source slide should map to one explicit template archetype or a deliberate split.

## Preferred Strategy

Use this order:

1. Migrate a small representative set first.
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
- Do not force all source slides into one template layout.
- Do not keep decorative source shapes unless they are required content.
- Do not accept a migrated slide that is on-brand but less legible than the source.

## Verification Standard

A migration pass is only done when:
- the migrated slide is visibly consistent with the company template
- the source content still exists and is readable
- no clipping, overlap, or awkward density was introduced
- sibling slides of the same type look like they belong in the same deck

## References

Read these before migrating beyond the first few slides:
- `./references/migration-playbook.md`
- `./references/slide-archetype-mapping.md`
