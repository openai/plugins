# Sensitive Geopolitical and Humanitarian Stories

## What Problem This Solves

Conflict, occupation, displacement, civilian harm, disaster, and humanitarian stories need more than a polished chart. They need source discipline, dated evidence, visual restraint, humane language, and clear boundaries between measured facts, estimates, and schematic explanation.

Use this reference when a visualization involves war, territorial control, frontline change, civilian casualties, displacement, humanitarian need, sanctions, migration, disaster response, political violence, or any story where people may be harmed by sensational framing or false precision.

## Lessons From The Ukraine War Infographic

- Treat the story as a layered evidence package, not a single heroic chart. The Ukraine work needed territorial-control change, map states, drone-system evolution, civilian harm, displacement, source notes, and an editorial review meter to support one bounded argument.
- Put the evidence hierarchy on the page. Readers need to see which layers come from map projects, humanitarian agencies, monitoring offices, research groups, or licensed basemaps.
- Every map state needs a date, source note, and method caveat. Occupation, frontline, and impact layers are temporal claims, not timeless geography.
- Separate measured, estimated, and schematic layers in both data and styling. A precise border path, an estimated control share, and a simplified technology diagram should not look equally certain.
- Use maps as evidence stages, not as battle-game interfaces. The map should help readers understand scale, location, and change without inviting tactical play or sensational interpretation.
- Human-impact panels need visible dignity and proportion. Civilian deaths, injuries, and displacement should be presented as consequences and lived stakes, not decorative counters.
- A strong screenshot matters. The default view, key map frame, and final state should each preserve the core claim without hover, autoplay, or lengthy instructions.

## Required Story Contract

Before rendering, write:

- One-sentence claim:
- Human stakes:
- Geography and time span:
- Primary evidence layer:
- Supporting evidence layers:
- What is known directly:
- What is estimated:
- What is schematic or illustrative:
- What the visual will deliberately not imply:

## Source And Method Ledger

Create a ledger for each evidence layer before designing the layout.

| Layer | Source | Date or update cadence | Unit and denominator | Evidence status | Caveat |
| --- | --- | --- | --- | --- | --- |
| Territorial control or affected area |  |  |  | measured / estimated / schematic |  |
| Events, attacks, routes, or movement |  |  |  | measured / estimated / schematic |  |
| Human impact |  |  |  | measured / estimated / schematic |  |
| Contextual basemap or imagery |  |  |  | measured / estimated / schematic |  |
| Research, policy, or technology context |  |  |  | measured / estimated / schematic |  |

Evidence status should affect visual treatment. Use crisp geometry and direct labels for high-confidence boundaries or points. Use texture, bands, note labels, or lower saturation for estimates. Use clearly labeled diagrams for schematic mechanisms.

## Composition Patterns

- Dated map sequence: small multiples or a stepper where every frame includes date, source note, and the same projection or viewBox.
- Map plus trend pairing: map states explain where change happened, while a line or area chart explains how much changed over time.
- Event-indexed timeline: a calm chronology of turning points, policy changes, technology shifts, or humanitarian milestones tied to the data frame they affect.
- System diagram: a neutral technical or institutional diagram for mechanisms such as supply chains, weapons adaptation, aid flows, evacuation routes, or infrastructure dependencies.
- Human-impact panel: proportional values, notes, and source caveats presented without spectacle. Use direct language and avoid imagery that aestheticizes suffering.
- Source evidence strip: a compact row of source cards or notes naming basemap, thematic data, humanitarian data, and method limitations.

## Map And Geography Rules

- Keep the basemap subdued. Borders, rivers, city labels, roads, or terrain should orient the reader without competing with the evidence layer.
- Preserve attribution and licensing for basemaps, map traces, and derived geometry.
- State whether boundaries or fronts are exact, estimated, generalized, or schematic.
- Use the same geographic frame for repeated map states unless a zoom change is itself part of the explanation.
- Do not use animated movement, explosions, pulses, or military iconography unless the motion or symbol is necessary evidence and has a static fallback.
- Avoid color choices that turn the story into team branding. Use semantic color for status, uncertainty, change, risk, or harm, and explain the role in the legend or labels.
- Pair spatial claims with non-map summaries when area comparison, trend, or ranking is easier off the map.

## Interaction And Fallback Rules

- Main claims must be visible without hover.
- Temporal controls should show the current date or event name beside the map, not hidden in a distant control.
- Stepper, slider, and thumbnail controls need keyboard and touch paths.
- Scroll or motion states need a reduced-motion equivalent: final state, key-frame sequence, or small multiples.
- A static export should include the title, map state or trend, source note, and caveat without relying on browser interaction.

## Language And Ethics Rules

- Use precise, sourced labels such as "territory under occupation," "reported civilian casualties," or "estimated displaced people" instead of emotionally inflated shorthand.
- Do not imply intent, responsibility, or military outcome beyond what the sources support.
- Do not use decorative casualty icons, skulls, fire, blood, blast effects, or celebratory color when describing human harm.
- Avoid ranking suffering as spectacle. If comparing harms, explain why the comparison is analytically necessary.
- Make uncertainty visible enough that readers do not mistake estimates for counts.

## Implementation Rules

- Keep sourced data, source notes, dates, units, and method caveats in structured data, not scattered through JSX or chart labels.
- Keep projection helpers, viewBox dimensions, derived paths, and map credits together so future maintainers can audit the geography.
- Prefer typed data modules for event frames, map frames, sources, and human-impact measures.
- Keep labels, annotations, source notes, legends, and accessibility summaries editable in HTML or SVG overlays, not baked into raster imagery.
- Add test or review checkpoints for narrow width, color-deficiency, reduced motion, keyboard step-through, source visibility, and screenshot intelligibility.

## Human Review Questions

- Does the first view make a bounded claim rather than trying to summarize the whole crisis?
- Can a reader distinguish measured facts, estimates, and schematic explanation?
- Are dates and source notes close to the evidence they support?
- Does the map clarify scale and change without becoming tactical entertainment?
- Does the human-impact section preserve dignity and proportion?
- Would the story remain truthful if one visual layer were removed?
- Does the mobile view preserve the same ethical and analytical reading path?

## Red Flags

- Frontlines, casualty figures, or displacement values shown without dates.
- A map layer with no source, attribution, or caveat.
- A slider that changes evidence states without exposing what changed and why it matters.
- Generated or decorative imagery that makes violence feel cinematic.
- National colors, flags, or military symbols doing more emotional work than analytical work.
- Exact-looking boundaries for approximate or disputed data.
- Hover-only source notes or caveats.
- A beautiful map that cannot be understood as a static screenshot.

## Adjacent References

- `./editorial-infographic-system.md`
- `./art-directed-interactive-visual-stories.md`
- `./domain-contextual-surfaces.md`
- `../../skills/geospatial-and-cartographic-visualization/SKILL.md`
- `../../skills/accessibility-and-inclusive-visualization/SKILL.md`
