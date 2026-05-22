# Editorial Infographic System

## What Problem This Solves

This reference turns respected editorial visualization practice into repeatable defaults for original, high-quality explanatory graphics. It is not a house style and must not copy any publication's visual identity. It encodes the underlying craft: clear claims, truthful evidence, restrained composition, precise annotation, custom layouts shaped by the story, and, when useful, animation or imagery that makes the evidence more concrete.

## When To Use It

Use this whenever the user asks for an infographic, data story, report figure, publication-quality chart, executive visual, article graphic, mobile-friendly explanatory visual, or an upgrade away from dashboards and generic chart templates.

## Editorial Philosophy

Every figure must communicate a clear takeaway. The title states the insight, not the topic. The chart supplies the evidence. Annotations explain why the evidence matters. Color is an editorial signal, not decoration. Whitespace is structure. When imagery, illustration, 3D, or animation appears, it must carry scale, place, mechanism, motion, or stakes. The result should feel calm, trustworthy, and specific to the data.

## Practitioner Mapping

- Alberto Cairo: treat graphics as truthful, functional, beautiful, insightful, and enlightening. Verify data, methods, scales, and uncertainty before polishing.
- Amanda Cox and newsroom graphics practice: avoid "cool for cool's sake." Find the sharpest compelling thing the data can honestly say, then design a custom reading path around it.
- Mike Bostock and D3 practice: use data-bound, inspectable marks and custom geometry when templates cannot express the story. Let the data structure shape the document.
- Cole Nussbaumer Knaflic: separate exploratory analysis from explanatory communication. Know the audience, reduce clutter, focus attention, and make the intended point unmistakable.
- Edward Tufte: maximize evidence and minimize non-data noise, but do not erase necessary labels, context, or caveats.
- Jen Christiansen: use visual explanation to help readers navigate complex content, especially when illustration, diagrams, and data need to work together for specialist and non-specialist audiences.
- Journalism courses and graphics teams: sketch, iterate, prototype, critique, and choose the right form for each story instead of forcing data into a default chart inventory.

## Strict Defaults

1. Start with a one-sentence takeaway before choosing the chart.
2. Write the title as a claim, contrast, or finding. Avoid topic-only titles such as "Sales by Region."
3. Put the subtitle to work: define metric, unit, geography, time span, denominator, and relevant caveat.
4. Choose the editorial artifact mode before choosing the renderer: data-first chart, generated object marks, illustrated substrate, cartographic flow field, 3D surface, or scrollytelling sequence.
5. Prefer direct labels at line ends, bar ends, map regions, object callouts, or panel headers. Use legends only when direct labeling would genuinely overload the view.
6. Use one primary accent hue and one secondary accent hue at most. Everything else should recede through neutral ink, lightness, texture, or grouping.
7. Use color for meaning: emphasis, category, sign, status, uncertainty, or threshold. Do not color categories just because there are categories.
8. Keep gridlines hairline-light. Remove chart borders, heavy axis frames, shadows, decorative gradients, and redundant keys unless they carry meaning.
9. For SVG charts, set professional rendering tokens before drawing: 10-12 px axis ticks, 11-13.5 px direct labels, 0.5-1 px non-data strokes, 1.5-2.25 px normal data lines, and 2.5-3 px focus lines. Use `../../skills/d3-data-visualization/references/svg-polish-and-crispness.md` for the full defaults.
10. Treat annotations as evidence companions. Each annotation should name a turning point, exception, mechanism, caveat, consequence, or visual state change.
11. Use small multiples when repeated comparison is cleaner than a tangled multi-series chart.
12. Use imagery only when it reduces abstraction, supplies context, or creates a truthful explanatory substrate. Do not paste a generic chart on top of decorative art.
13. Use animation only when it has an explanatory verb: reveal, move, accumulate, compare, transform, zoom, rotate, or highlight.
14. Design mobile portrait separately, and add mobile landscape when the evidence or interaction needs a wide handheld view. If annotations collide on narrow screens, convert them to a numbered key below the chart and keep essential labels visible.
15. Keep source, method, uncertainty, and missingness visible enough to support trust.
16. Never imitate a specific publication layout, palette, type system, or visual brand. Borrow principles only.
17. When using visual references, document the principle learned and the original transformation for this dataset before rendering. If the result can be mistaken for the reference, redesign it.
18. For conflict, disaster, displacement, civilian harm, or humanitarian subjects, create a source and method ledger before rendering. Keep dates, evidence status, caveats, and humane language visible enough that the graphic cannot be mistaken for spectacle or false precision.

## Artifact Selection Rules

- Use data-first charts when the evidence is already clear through position, length, area, slope, or color.
- Use generated object marks when the metric is abstract but the subject is physical, such as water use, household goods, food, energy, materials, or medical devices.
- Use an illustrated substrate when the object or system is the natural coordinate plane: a room, vehicle, machine, body, supply chain, instrument, or exploded diagram.
- Use cartographic flow fields when the story depends on movement, chokepoints, routes, risk surfaces, or geography.
- Use 3D or camera-led scenes when depth, volume, terrain, or a multiaxis surface is intrinsic to the claim.
- Use scrollytelling when the reader needs staged reveal, state change, or paced comparison.

## Sensitive Story Rules

- Use `./sensitive-geopolitical-and-humanitarian-stories.md` for war, occupation, territorial control, displacement, disaster, civilian harm, migration, sanctions, or humanitarian need.
- Separate measured facts, estimates, and schematic explanation in both the data model and visual treatment.
- Pair map states with date, source, method caveat, and attribution.
- Present human-impact figures as consequences with dignity, not as decorative counters or dramatic effects.
- Avoid visual metaphors, colors, or motion that turn suffering into spectacle or imply unsupported certainty.
- Confirm that a static screenshot preserves the claim, caveat, and source context.

## Layout Patterns

- Lead figure: insight title, compact subtitle, one dominant chart, direct labels, one to three annotations, source note.
- Before/after transformation: left panel shows the current/problem view, right panel shows the editorial redesign, followed by a short rationale.
- Annotated trend: one emphasized line or area, muted comparison context, turning-point callout, direct end labels.
- Ranked evidence: horizontal bars or dots sorted by the argument, one emphasized item, labels at the point of comparison.
- Small multiples: repeated panels with identical scales, short panel titles that carry local takeaways, and a shared note for scale/unit.
- Infographic panel sequence: 2 to 5 panels where each panel answers one sub-question and advances the reading path.
- Immersive lead scene: one full-width visual substrate with data-bound labels and a title over or adjacent to the evidence, followed by staged explanatory sections.
- Exploded mechanism: neutral technical illustration with accent overlays for additions, removals, paths, or changes over time.
- Object inventory: generated or illustrated objects arranged by room, category, sequence, or scale, with callouts bound directly to the objects.
- Flow map: subdued geography with routes, density, or moving positions as the active evidence layer.
- Mobile stack: title, subtitle, chart, direct labels, active state summary, numbered annotation key, notes/source. Do not put a desktop control rail or prose column before the main chart merely because of DOM order.

## Annotation Patterns

- Turning point: label the moment where the slope, rank, or relationship changes.
- Outlier: label the point and explain the plausible mechanism or caveat.
- Threshold: draw a quiet reference line and explain why that level matters.
- Comparison: call out the difference between two values directly, preferably near the marks.
- Method note: disclose smoothing, rebasing, sampling, missingness, or estimates near the affected evidence.
- Consequence: explain what the reader should infer or decide, but keep the claim proportional to the data.

## Typography and Spacing

- Use a restrained type scale: title, subtitle, labels, notes. Avoid more than four text sizes in one figure.
- For SVG interiors, default to 11 px axis ticks, 12 px direct labels, 12.5 px annotation body, and 10 px source notes. Use fewer ticks, shorter labels, or a different layout before shrinking meaningful text below 10 px.
- Use sentence case for titles and annotations unless the local product style requires otherwise.
- Keep label text short. Move method details to notes, not mark labels.
- Align text and chart edges to the same grid. Whitespace should separate reading stages, not float randomly.
- Reserve label lanes for dense charts rather than placing text on top of marks.
- Do not rely on tiny type. Test common export sizes and mobile widths.

## SVG Rendering Defaults

- Style axes, ticks, domains, and gridlines explicitly. Do not leave D3 or browser defaults as the final visual treatment.
- Use 6-8 px tick padding, short 4-6 px tick marks, and `.tickSizeOuter(0)` for D3 axes unless a stronger reason exists.
- Remove chart borders and axis domains when gridlines, baselines, labels, or whitespace already establish the plot frame.
- Keep gridlines at 0.5-1 px and low contrast. A gridline should never be visually stronger than a data line.
- Use `shape-rendering: crispEdges` for straight axes, gridlines, and rectangular cells. Keep curves, circles, arcs, symbols, and diagonal marks antialiased.
- Use `vector-effect: non-scaling-stroke` for zoomable maps, outlines, annotation connectors, and icons whose stroke weight should remain stable on screen.
- Keep in-chart glyph icons at 12-16 px, annotation icons at 16-20 px, and UI/control icons at 20 or 24 px.
- Check SVG outputs at 375 px, 768 px, and desktop width, plus the target export size. Look specifically for oversized titles, undersized ticks, thick outlines, clipped labels, and icons that overpower their labels.

## Image and Illustration Rules

- Keep generated imagery, illustrations, and raster textures as substrates or data marks. Keep numerical labels and source notes editable whenever possible.
- Give image generation prompts a role, viewpoint, style, scale, lighting, and exclusion list. Ask for transparent backgrounds for repeatable object marks.
- Use consistent perspective across generated assets in a single story.
- Avoid photorealistic detail that implies unsupported precision.
- Validate generated assets for factual plausibility, legibility under labels, and accessibility text.

## Motion Rules

- Define the animation purpose in one phrase before implementing it.
- Start from a meaningful still frame and end on a meaningful still frame.
- Pair each staged transition with an annotation, label, or state indicator.
- Respect reduced-motion preferences with a static final state, key-frame sequence, or numbered steps.
- Avoid infinite loops unless they represent ongoing movement or live data and can be paused or ignored.

## Color Rules

- Default to neutral marks with a single emphasized series, region, rank, or interval.
- Use red/orange only for real risk, loss, heat, warning, or negative direction.
- Use blue/teal/green for main emphasis only when it does not imply a semantic conflict.
- For ordered data, use lightness or a perceptually ordered ramp, not rainbow hue.
- Check color-deficient and grayscale interpretation. Add direct labels, line style, pattern, or symbols when color is not enough.
- Avoid palettes dominated by one decorative hue family. Calm does not mean monochrome.

## Mobile and Narrow Layout Rules

- Design a narrow version explicitly at 360 to 430 px wide.
- Prefer designed vertical stacking to horizontal compression, with the main visualization visible before secondary controls.
- Keep direct end labels when possible; otherwise place a compact inline key directly below the chart.
- Convert nonessential annotations to numbered notes below the chart.
- Avoid rotated axis labels. Use title, subtitle, tick format, or inline unit labels instead.
- Preserve touch targets of at least 44 px for primary controls when practical and at least WCAG 2.2 minimum target sizing.
- Replace hover-only evidence with tap, focus, selection, direct labels, or a detail panel.
- Keep settings, filters, and inspectors collapsed or closable when they are secondary, and return the user to the affected chart after Apply, Cancel, Reset, or close.
- Account for on-screen keyboard real estate in search, filters, notes, and annotation forms.
- For streaming or remote data, preserve the last known good view and show stale/live/offline/partial status.
- Use AR, camera, motion, vibration, notifications, or geolocation only when they add analytical value and have permission fallbacks.
- Use `./mobile-first-responsive-visualization.md` for full mobile concept, interaction, capability, and QA rules.

## Evaluation Rubric

Score each category from 1 to 5:

- Clarity: the main comparison is immediately readable.
- Storytelling strength: the figure has a claim and a purposeful reading path.
- Hierarchy: the title, chart, labels, annotations, and notes have clear priority.
- Restraint: color, decoration, gridlines, and controls are limited to meaningful roles.
- Annotation quality: annotations explain why the data matters and do not merely restate values.
- Accessibility: the insight survives color-deficiency, grayscale, keyboard use, screen-reader summary, and export.
- Originality: the solution is specific to the dataset and audience, inspired by editorial practice without copying a brand or layout.

## Red Flags

- Title names only the dataset.
- The legend is more colorful than the chart is informative.
- Hover is required to understand the main point.
- Every panel, card, metric, and control has equal visual weight.
- The chart is a dashboard tile when the user asked for an explanation.
- Annotations say "high" or "low" without explaining significance.
- The mobile view is just the desktop chart squeezed narrower.
- The mobile view is just the desktop DOM stacked with settings above the evidence.
- The chart disappears behind settings, keyboard input, or a reconnect spinner.
- The page is a grid of bordered chart boxes when the story needs a composed visual sequence.
- Generated imagery is attractive but analytically idle.
- Animation exists without a reason the reader can name.
- A normal chart is pasted onto a scenic background instead of being integrated with it.

## Source Links

- [The Truthful Art by Alberto Cairo](https://www.oreilly.com/library/view/the-truthful-art/9780133440492/ch05.html)
- [Amanda Cox on visualization's "Aha!" moments](https://hbr.org/2013/03/power-of-visualizations-aha-moment)
- [D3: Data-Driven Documents](https://idl.uw.edu/papers/d3)
- [Storytelling with Data by Cole Nussbaumer Knaflic](https://www.oreilly.com/library/view/storytelling-with-data/9781119002253/f_02.xhtml)
- [Edward Tufte books](https://www.edwardtufte.com/books/)
- [Jen Christiansen](https://www.jenchristiansen.com/about)
- [2025: The Year in Visual Stories and Graphics](https://www.nytimes.com/interactive/2025/12/22/us/2025-year-in-graphics.html)
- [Columbia Journalism School Data Visualization course description](https://journalism.columbia.edu/content/cross-registration)
- [Datawrapper annotation guidance](https://www.datawrapper.de/academy/annotate-tab)
- [Datawrapper color restraint guidance](https://www.datawrapper.de/blog/10-ways-to-use-fewer-colors-in-your-data-visualizations)
