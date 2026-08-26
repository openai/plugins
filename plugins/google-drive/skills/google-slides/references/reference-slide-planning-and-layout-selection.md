# Slide Planning And Layout Selection

Use this reference for multi-slide creation, adding slides to an existing deck, following a template or reference deck, or adapting content from another source. Apply source-fidelity, notes, and media-parity rules only when source material exists and the request expects that content to carry forward.

## Planning Sequence

1. Read the content sources and the target deck, template, or design references that apply.
2. Draft or confirm an outline for what each target slide should communicate.
3. Inventory required content channels: text, images, charts, tables, links, media, and speaker notes when present.
4. Inventory available slide patterns or define the intended layout system, including hierarchy, visual orientation, evidence type, style runs, and semantic emphasis.
5. Map each outline item to the best slide archetype and layout family.
6. Build a representative subset first.
7. Validate the mapping with thumbnails.
8. Roll out to the remaining slides by family.
9. Do one deck-wide consistency pass at the end.

## Outline Before Layout

Before you choose or build a layout, define the target slide in words:
- what the slide is trying to do
- what content is required, including anything that must survive from source material
- what evidence, links, media, and speaker notes must carry forward when present
- what content can become secondary or move to another slide
- whether it needs a chart, image, grid, KPI, or mostly text
- whether its defining visual orientation is portrait, landscape, full-bleed, split, or multi-panel
- whether the content density is light, medium, or dense
- whether the chosen layout will feel intentionally filled rather than leaving large accidental empty areas

If a generated summary, changelog, or raw notes produce a messy slide brief, fix that in the outline first. Do not expect the layout choice to solve an unclear slide concept.

## Pick The Slide Archetype Before Populating

For each slide, answer these questions in order:
- Is this a title, section divider, summary, dense content, KPI, chart, image, or appendix slide?
- How much content should fit without crowding?
- Which existing slide, layout, or composition already does that job well? For net-new decks, which composition best expresses it?
- Does the candidate layout's hierarchy, sample labels, artwork, or highlighted state communicate the same semantic job?
- When existing objects are available, which text, image, chart, table, and placeholder slots will carry the content?

Only after that should you select or build the slide and populate it.

When populating:
- when editing or following an existing deck, replace content in suitable existing slots before creating new primary text or image boxes
- for genuinely net-new slides, create only the objects required by the selected composition and keep them consistent with the deck's design system
- avoid leaving major text boxes or card regions mostly empty unless that whitespace is intentional
- if the slide looks too empty, reconsider the archetype, combine related content, or tighten the outline before doing geometry tweaks
- if the slide needs content the chosen archetype does not support, choose another archetype or split the slide instead of adding ad hoc boxes
- use the same layout family for repeated narrative roles unless the content genuinely requires a different structure
- preserve mixed text-style runs and neutralize inherited or reference-specific emphasis that does not transfer to the new content

Common failure mode:
- taking a large blob of content
- dropping it into the visually nicest available layout
- trying to resize and nudge everything until it fits

That usually produces an on-brand but weak slide. The fix is to choose the right pattern first or split the content across multiple slides.

## Representative Subset

For larger decks or unfamiliar layout systems, do not bulk-build immediately. Start with:
- title slide
- one section divider
- one dense content slide
- one visual slide with an image or chart
- one high-risk slide with dense evidence, mixed styles, or source media/notes when present

This is the fastest way to discover whether the chosen layout system supports the content density and evidence types.

Validate two things in this subset:
- the content outline is correct
- the archetype mapping is correct

If either is wrong, fix that before scaling up.

## When To Split Content

Split one planned or source slide into multiple slides only when the request permits changing the slide count and:
- the selected pattern cannot fit the content without crowding
- the content mixes two different narrative jobs, like summary plus deep evidence
- the content would require breaking the deck's spacing and hierarchy to remain on one slide

When splitting:
- keep the deck style constant
- preserve the original order of ideas when adapting a source
- use the same title family or section logic so the split feels intentional

## Handling Images And Charts

- Prefer existing image and chart frames when they suit the content; otherwise use a composition that preserves the visual's information needs.
- Resize or crop visuals to fit the selected framing without sacrificing essential evidence.
- If a chart is too detailed for the selected frame, use a denser archetype or give the chart its own slide.
- Preserve the visual evidence, labels, legends, and footnotes that make an image or chart interpretable. Do not replace required chart-heavy evidence with prose-only content.
- When adapting a source deck, do not use a screenshot of the entire source slide as a shortcut for an ordinary slide. Reuse the actual assets and editable text where practical; use a source-faithful raster of a chart or evidence panel only when native reconstruction is impractical.

## Handling Source Speaker Notes And Media

These rules apply when adapting or migrating a source deck:

- Treat speaker notes as source content. Copy them to the corresponding destination slide and verify source/destination note-count parity plus exact spot checks.
- Preserve active, accessible video or other media as the same media type and source identifier when the API supports it.
- Establish media status from source object metadata, Drive readback, or the connector/API result. Do not infer availability from outline text, a thumbnail, or the presence of a poster image.
- If source media is trashed, inaccessible, or deprecated, use a source-faithful static fallback when appropriate. Do not invent a substitute or launch a recovery workflow unless the user asks.
- Summarize media handling only when something could not be migrated faithfully. If all media migrated successfully, a detailed media manifest is unnecessary.

## When No Existing Layout Fits

Not every slide concept will match an existing layout exactly.

In those cases:
- pick the closest archetype and adapt carefully
- duplicate the nearest strong completed slide instead of starting from an unsuitable raw layout
- for net-new decks, build a composition that follows the established design system
- if none of those paths works, say the slide needs human design judgment rather than over-automating a bad fit

## Deck-Wide Consistency Check

At the end, verify:
- title positions are consistent
- section dividers feel related
- recurring image treatments match
- chart slides use the same alignment logic
- repeated narrative roles use a consistent layout family
- margins and text density feel stable across the deck
- heading/body hierarchy and mixed emphasis remain intentional
- image crops and orientations preserve the important evidence
- table, card, and KPI emphasis matches the meaning of the current content
- there are no whitespace-only bullets or empty list items
- large text or content regions do not have accidental excessive whitespace
- placeholders, sample copy, and other inherited scaffolding have been populated or intentionally removed
- when editing or following an existing deck, newly created objects match the selected pattern and do not bypass suitable existing slots
- when adapting source material, source-to-destination checks account for text, images, charts, tables, links, media, and speaker notes without silent shortening
