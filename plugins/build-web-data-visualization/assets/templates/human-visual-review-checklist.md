# Human Visual Review Checklist

Use this after producing an editorial infographic or interactive visual story. The goal is to catch outputs that are technically correct but visually generic, over-decorated, or lacking editorial judgment.

## First Impression

- Can a reader state the main takeaway from the default view?
- Does the visual feel specific to this dataset and subject?
- Does the composition have a clear place to look first?
- Does the title state an insight rather than a topic?
- Would this still make sense as a screenshot?

## Story and Evidence

- Is the strongest visual encoding assigned to the main comparison?
- Are supporting details visibly subordinate?
- Are annotations explaining significance rather than repeating values?
- Are source, method, uncertainty, and caveats present where trust requires them?
- Is hover optional for the main point?

## Art Direction

- Does imagery, illustration, 3D, or animation carry analytical meaning?
- Would the story be weaker if the visual substrate were removed?
- Does the background improve orientation, scale, place, mechanism, motion, texture, or label-safe context rather than just adding mood?
- Does the design avoid generic AI atmosphere such as broad brush strokes, wispy ribbons, bokeh/orbs, cinematic wallpaper, stock-photo haze, and decorative gradients?
- If motion, flow, density, intensity, or spread is shown, is it encoded as measured or clearly schematic contours, sampled fields, trajectories, or particles with defined meaning?
- Are generated assets factually plausible and consistent in perspective, scale, and lighting?
- Are data marks and labels integrated with the substrate rather than pasted on top?
- Does the page avoid a generic grid of bordered chart cards?

## Meaning-Preserving Concept Review

- If Codex image generation produced a concept set, are the approved large-screen and mobile concept paths or screenshot references recorded?
- Were the generated large-screen and mobile portrait concept images shown with concise plan and interaction bullets before asking for approval?
- Was a mobile landscape concept shown when a wide handheld orientation was analytically useful?
- Did the user approve the generated design direction before project changes or implementation code began?
- If the user requested changes, were the concept iterations shown and resolved before implementation?
- Has the approved concept been converted into a binding semantic design contract before implementation?
- Are locked concept elements, flexible production details, and approved deviations recorded?
- Does the implementation preserve the claim, comparison, denominator, scale, source, caveat, and evidence hierarchy?
- Does the implementation preserve the approved layout, visual hierarchy, interaction staging, label-safe regions, and mobile/export continuation?
- Does the implementation preserve the approved mobile portrait and optional landscape reading path rather than merely stacking the desktop DOM?
- Are labels, values, axes, source notes, caveats, and essential data marks editable or data-bound unless a static poster was explicitly requested?
- Are visual deviations from the concept documented as meaning-preserving choices?
- For existing-page integration, was the surrounding page, report, deck, or app surface inspected before concepting?

## Embedded Visualization Self-Use

- Did every meaningful embedded chart, map, table-graphic, swarm, distribution, flow layer, particle layer, media overlay, key, or fallback get a mini-brief before layout?
- Does each layer show visible evidence of its specialist owner in chart choice, encoding, labels, interaction, fallback, accessibility, or QA?
- Were high-risk layers handled by authorized delegated fresh context or an explicit local fresh specialist pass?
- Are generic cards or plain tables used only where the mini-brief says that simple treatment is analytically right?
- Are color semantics, units, baselines, caveats, source notes, and accessibility summaries consistent across layers?
- Did the parent story or report integrate the specialist guidance without flattening every visual into the same template?

## Motion and Interaction

- Can every animation be named with a useful verb?
- Are first and final frames meaningful stills?
- Is there a reduced-motion path?
- Are interactions obvious from layout and affordance, not instructional prose?
- Are keyboard, touch, and narrow-screen paths supported?
- Are hover-only values replaced by tap, focus, selection, visible labels, or step-through controls?
- Are drag-only actions supported by buttons, steppers, search, or direct inputs?
- Does pinch, wheel, drag, or map panning avoid fighting native page scroll?
- Does the current configured view have a copyable URL or saved-view path when sharing would matter?
- Do refresh and back/forward navigation preserve committed filters, ranges, selections, tabs, zoom, or drill-down state?
- Are configuration, filter-builder, detail, or drill-down areas collapsed by default or closable when they are not the main evidence?
- When panels are collapsed, are active filters, selections, caveats, and source context still visible?

## Mobile Experience

- Does the first mobile screen show the main visualization or an insight summary with the visualization immediately available?
- Are filters, settings, inspectors, and detail panels secondary to the main evidence unless they are the primary task?
- After Apply, Cancel, Reset, close, or back, does the user return to the affected visualization?
- Does the on-screen keyboard avoid covering the only critical action or permanently obscuring the main evidence?
- Are text, labels, marks, hit targets, controls, and legends legible at 360-430 px widths?
- Does mobile portrait preserve the same claim, caveat, source context, and primary comparison as large screen?
- Is mobile landscape supported when the visualization needs a wide handheld substrate, and is portrait still useful?
- Are stale, live, offline, partial, reconnecting, and error states clear for streaming or remote data?
- Are AR, camera, motion, vibration, notifications, or geolocation used only with analytical purpose, user-initiated permission timing, and fallback paths?
- Does the mobile screenshot preserve the claim without hover, autoplay, permissions, or a strong network?

## Accessibility

- Is there a concise accessible summary of the chart type, takeaway, and caveat?
- Does meaning survive color-deficiency and grayscale?
- Do meaningful marks, focus/selection states, and control affordances have enough contrast against adjacent colors?
- Is text large enough at mobile and export sizes?
- Do touch targets meet WCAG 2.2 minimum sizing and use larger hit areas for primary mobile controls when practical?
- Are generated images described without overstating data?
- Are source data or tabular equivalents available when appropriate?

## SVG Polish

- Are axis tick labels mostly 10-12 px, direct labels 11-13.5 px, and source notes at least 9.5-10 px at the target size?
- Are gridlines, axis domains, borders, map outlines, and connector lines 0.5-1 px unless they carry data emphasis?
- Are data lines and selected outlines stronger than non-data structure, without defaulting everything to thick strokes?
- Are tick labels aligned and padded consistently, with fewer ticks or better formatting used before rotation or tiny type?
- Are in-chart icons 12-16 px, annotation icons 16-20 px, and control icons 20 or 24 px?
- Do zoomable SVG layers keep labels, icons, axes, and annotation strokes screen-stable where appropriate?
- Does the visual remain crisp at 375 px, 768 px, desktop width, and export size without clipped labels?

## Sensitive Subject Review

Use this section for conflict, disaster, civilian harm, displacement, migration, political violence, or humanitarian need.

- Are dates, source notes, and method caveats visible near the evidence they support?
- Can a reader distinguish measured facts, estimates, and schematic explanation?
- Does the visual avoid decorative violence, sensational motion, or team-color framing?
- Are human-impact figures presented with dignity and proportion?
- Does the map clarify scale, location, and change without feeling like a tactical interface?
- Would a static screenshot preserve the claim, caveat, and source context?

## Decision

- Publishable with minor edits:
- Needs redesign:
- Needs data/method review:
- Needs asset regeneration:
- Needs semantic contract revision:
- Specific edits:
