# Migration Playbook

Use this reference after the skill triggers and you are ready to migrate slides.

## Migration Sequence

1. Read the source deck and template deck.
2. Draft or confirm an outline for what each target slide should communicate.
3. Inventory source slide types and content channels: text, images, charts, tables, links, media, and speaker notes.
4. Inventory template slide patterns, including hierarchy, visual orientation, evidence type, style runs, and semantic emphasis.
5. Map each outline item to the best template archetype.
6. Pick a representative subset and migrate those first.
7. Validate the mapping with thumbnails.
8. Roll out to the remaining slides by family.
9. Do one deck-wide consistency pass at the end.

## Outline Before Layout

Before you duplicate any template slide, define the target slide in words:
- what the slide is trying to do
- what content must survive
- what evidence, links, media, and speaker notes must survive
- what content can become secondary or move to another slide
- whether it needs a chart, image, grid, KPI, or mostly text
- whether its defining visual orientation is portrait, landscape, full-bleed, split, or multi-panel
- whether the content density is light, medium, or dense
- whether the chosen layout will feel intentionally filled rather than leaving large accidental empty areas

If a generated summary, changelog, or raw notes produce a messy slide brief, fix that in the outline first. Do not expect the template choice to solve an unclear slide concept.

## Pick The Template Archetype Before Populating

For each slide, answer these questions in order:
- Is this a title, section divider, summary, dense content, KPI, chart, image, or appendix slide?
- How much content should fit without crowding?
- Which template slide already does that job well?
- Does the template slide's hierarchy, sample labels, artwork, or highlighted state communicate the same semantic job?
- Which existing text, image, chart, table, and placeholder slots on that template slide will carry the content?

Only after that should you duplicate the template slide and populate it.

When populating:
- replace content in existing template slots first; avoid creating new primary text boxes or image boxes when a suitable slot exists
- avoid leaving major text boxes or card regions mostly empty unless that whitespace is an intentional part of the template
- if the slide looks too empty, reconsider the archetype, combine related content, or tighten the outline before doing geometry tweaks
- if the slide needs content the chosen archetype does not support, choose another archetype or split the slide instead of adding ad hoc boxes
- use the same layout family for repeated narrative roles unless the content genuinely requires a different structure
- preserve mixed text-style runs and neutralize template-specific emphasis that does not transfer to the new content

Common failure mode:
- taking a large blob of content
- dropping it into the visually nicest template slide
- trying to resize and nudge everything until it fits

That usually produces an on-brand but ugly slide. The fix is to choose the right template pattern first or split the content across multiple slides.

## Representative Subset

Do not bulk-migrate immediately. Start with:
- title slide
- one section divider
- one dense content slide
- one visual slide with an image or chart
- one high-risk slide with dense evidence, mixed styles, media, or speaker notes

This is the fastest way to discover whether the template actually supports the source content density.

Validate two things in this subset:
- the content outline is correct
- the archetype mapping is correct

If either is wrong, fix that before scaling up.

## When To Split A Source Slide

Split a source slide into multiple migrated slides only when the request permits changing the slide count and:
- the template pattern cannot fit the content without crowding
- the source mixes two different narrative jobs, like summary plus deep evidence
- the slide only works in the source because it ignores the template’s spacing and hierarchy

When splitting:
- keep the template style constant
- preserve the original order of ideas
- use the same title family or section logic so the split feels intentional

## Handling Images And Charts

- Prefer the template’s image and chart frames over the source geometry.
- Resize or crop source visuals to fit the template framing rather than stretching the template to fit the source.
- If a chart is too detailed for the template frame, either use a denser template archetype or split the chart onto its own slide.
- Preserve the visual evidence, labels, legends, and footnotes that make an image or chart interpretable. Do not replace a chart-heavy source slide with prose-only content.
- Do not use a screenshot of the entire source slide as a shortcut for an ordinary migrated slide. Reuse the actual assets and editable text where practical; use a source-faithful raster of a chart or evidence panel only when native reconstruction is impractical.

## Handling Speaker Notes And Media

- Treat speaker notes as source content. Copy them to the corresponding destination slide and verify source/destination note-count parity plus exact spot checks.
- Preserve active, accessible video or other media as the same media type and source identifier when the API supports it.
- Establish media status from source object metadata, Drive readback, or the connector/API result. Do not infer availability from outline text, a thumbnail, or the presence of a poster image.
- If source media is trashed, inaccessible, or deprecated, use a source-faithful static fallback when appropriate. Do not invent a substitute or launch a recovery workflow unless the user asks.
- Summarize media handling only when something could not be migrated faithfully. If all media migrated successfully, a detailed media manifest is unnecessary.

## Handling Oddball Slides

Not every source slide will match a template exactly.

For oddballs:
- pick the closest archetype and adapt carefully
- or duplicate the nearest good migrated slide instead of a raw template slide
- if neither works, say the slide needs human design judgment rather than over-automating a bad fit

## Deck-Wide Consistency Check

At the end, verify:
- title positions are consistent
- section dividers feel related
- recurring image treatments match
- chart slides use the same alignment logic
- repeated narrative roles use a consistent layout family
- margins and text density feel stable across the deck
- heading/body hierarchy and mixed emphasis remain intentional
- image crops and orientations preserve the source evidence
- table, card, and KPI emphasis still matches the meaning of the migrated content
- there are no whitespace-only bullets or empty list items
- large text or content regions do not have accidental excessive whitespace
- placeholders, sample copy, and other template scaffolding have been populated or intentionally removed
- newly created objects are exceptions that match the selected template pattern, not replacements for available template slots
- source-to-destination checks account for text, images, charts, tables, links, media, and speaker notes without silent shortening
