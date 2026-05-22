# Art-Directed Interactive Visual Stories

## Purpose

This reference extends the editorial infographic system for ambitious visual stories that combine data visualization with animation, generated imagery, custom illustration, maps, WebGL, particle or flow effects, 3D scenes, and human editorial judgment.

The goal is not to copy any publication's layout or visual identity. The goal is to internalize the craft behind memorable interactive graphics: the visual object, motion, annotation, and data marks are composed as one explanation.

## Inspiration, Not Replication

Reference images, newsroom projects, award winners, and publication roundups are research material, not layout recipes. Analyze them for transferable principles, then design an original artifact for the user's subject, data, and audience.

For every visual reference, write down:

- Principle learned: the underlying craft move, such as object-as-coordinate-system, staged reveal, subdued base map, or direct-label small multiple.
- Original transformation: how that principle changes for this dataset, including new geometry, imagery, pacing, labels, palette, and interaction.
- What will not be copied: publication typography, color identity, composition, subject-specific scene, illustration style, annotation placement, or interaction cadence.

If an output still resembles a reference after the data has changed, revise the visual form until the resemblance is only conceptual. The correct result should feel like it came from the story's evidence, not from a screenshot.

## What the Screenshot Audit Shows

1. 3D yield-curve surface
   - The camera is justified because the data has three meaningful axes: time, term, and rate.
   - The chart reads like terrain. Depth cues, surface bands, and a guided stepper help the reader notice ridges, cliffs, and recoveries.
   - Rule: use 3D only when spatial structure makes a relationship easier to understand, then choreograph camera states as annotations.

2. Middle-class jobs small multiples
   - The page uses a print-like editorial hierarchy, lots of whitespace, and direct labels.
   - Small multiples let each occupation category keep its own readable slope while sharing scale and comparison logic.
   - Rule: when many related stories exist, compose a field of small explanations instead of one tangled master chart.

3. Personal water-use food portions
   - Object imagery makes an invisible unit tangible. The repeated objects are the scale system.
   - The white space is not empty decoration; it gives each portion room to be inspected.
   - Rule: when the metric is abstract but the subject is physical, use generated or photographed object marks with precise labels.

4. Tanks adapted for drones
   - The object is the coordinate system. The reader learns by seeing the vehicle change layer by layer.
   - Red linework acts as editorial emphasis over neutral technical drawing.
   - Rule: for mechanisms, draw the thing and attach the data or chronology to its parts.

5. Shipping through a chokepoint
   - The map is a subdued stage. The routes are the active evidence.
   - Motion is meaningful because the subject is movement through constrained geography.
   - Rule: animate flow, direction, accumulation, or reveal. Do not animate because static charts feel plain.

6. Wildfire risk to structures
   - Raster texture, terrain, streets, and heat colors make the data feel attached to place.
   - The legend is compact and embedded near the evidence.
   - Rule: for spatial risk, fuse the data layer with a physical substrate so the reader trusts where values apply.

7. Household imports from China
   - An isometric room turns trade percentages into object-level callouts.
   - Labels are anchored to visible things, so the reader does not decode a separate chart inventory.
   - Rule: for inventory stories, build or generate the scene first, then bind data hotspots to objects.

## What The Ukraine War Infographic Taught

The Ukraine editorial demo added a different kind of lesson: an ambitious visual story can be visually composed and still fail if the evidence hierarchy, dates, caveats, and human stakes are not clear. For sensitive geopolitical or humanitarian stories, use `./sensitive-geopolitical-and-humanitarian-stories.md` alongside this reference.

- Layer the story deliberately. A territorial-control map, a trend line, a technology timeline, and a human-impact panel each answer different reader questions.
- Put source hierarchy into the design. Basemap, control data, humanitarian figures, research claims, and method caveats should be visible and auditable.
- Treat every map frame as a dated claim. A control shape, frontline trace, or displaced-population estimate needs time context and evidence status.
- Keep cinematic tools subordinate. Motion, map transitions, and technical diagrams should reveal change or mechanism, not dramatize violence.
- Preserve dignity in human-impact sections. The visual language should make harm legible without making it decorative.
- Validate the screenshot. A static capture should carry the main claim, date, source, and caveat even when the interactive layer is gone.

## NYT Year-in-Graphics Page Notes

The requested page (`https://www.nytimes.com/interactive/2025/12/22/us/2025-year-in-graphics.html`) returns a metered interactive shell over curl. The available metadata identifies it as "2025: The Year in Visual Stories and Graphics" and describes it as selected Times graphics, visualizations, and multimedia stories published that year. The page is marked as not freely accessible in the embedded structured data, so use the page as a public signal of format and standards, not as a source to clone.

## Editorial Artifact Modes

Choose one primary artifact mode before choosing a renderer:

- Data-first chart: the data marks themselves can carry the argument.
- Generated object marks: physical objects make the unit or comparison memorable.
- Illustrated substrate: a room, device, body, vehicle, machine, or system becomes the coordinate plane.
- Cartographic flow field: routes, positions, densities, or movement are staged over geography.
- WebGL-accelerated 2D or particle scene: density, flow, focus, or interaction needs GPU rendering while remaining mostly flat.
- 3D or camera-led surface: depth or volume is intrinsic to the claim.
- Scrollytelling or parallax sequence: the reader needs paced reveal, state changes, scroll-driven timelines, rich-media synchronization, or guided comparison. Use `../../skills/scrollytelling-and-parallax-data-visualization/SKILL.md` for scene contracts, browser behavior, reduced-motion paths, and performance checks.

## Fictional And Simulated Stories

For invented, illustrative, or synthetic stories, use `./fictional-data-story-simulation.md` before art direction. For composite stories with charts, maps, flows, media overlays, or static fallbacks, also use `./embedded-visualization-self-use.md` so each visual layer gets specialist guidance before composition. A fictional story still needs evidence density: entities, time, spatial or physical structure, events, outcomes, and derived comparisons.

- Build the deterministic data-generating world before generating images or choreographing motion.
- Make every embedded visualization name its specialist owner, mini-brief, QA check, and delegated or local fresh-pass status before composition.
- Treat sparse data as a design failure. Add meaningful simulation fields, event windows, and derived metrics instead of compensating with long prose or decorative parallax.
- Label fictional values honestly and preserve the seed or regeneration path.
- Use generated imagery to reveal place, mechanism, scale, motion, or stakes; keep data layers editable and data-bound.

## Image Generation Rules

- Use image generation when a story needs objects, cutaways, textures, scenes, or backgrounds that are specific enough that generic stock imagery would weaken trust. For advanced visual-design prompts where the user asks to see the page, layout, key frame, scene, or concept direction, this is mandatory before a text-only design handoff or implementation. Use `./mobile-first-responsive-visualization.md` so the concept pass includes large-screen and mobile portrait images by default, plus mobile landscape when the evidence or interaction needs it.
- When image generation is used for a design concept, show the generated concept set to the user, summarize the plan and any interactions in concise bullets, ask for approval or specific changes, and iterate until the user agrees on the design before project changes or implementation code begins. Treat the approved concepts as a binding contract for composition, visual hierarchy, label-safe regions, asset roles, interaction staging, mobile continuation, and static fallback, not as loose visual inspiration.
- Generate assets as neutral substrates unless the image itself is the data mark.
- Keep data, labels, axes, legends, and uncertainty as editable HTML, SVG, Canvas, or data-bound layers whenever possible.
- Never bake exact numbers, source notes, or dense labels into generated images unless the user explicitly asks for a single static poster and review has confirmed legibility.
- Ask for transparent-background cutouts when object marks need to repeat in a data layout.
- Ask for consistent angle, lighting, and scale across batches when using image marks in small multiples or inventories.
- Validate generated imagery with human review: does it accurately represent the object, avoid misleading scale, and support the claim?

## Motion Rules

- Every animation needs a verb: reveal, move, accumulate, compare, transform, zoom, rotate, or highlight.
- The first frame and final frame must both make sense as still images.
- Provide a reduced-motion version that shows the final state, key frames, or numbered steps.
- Prefer staged transitions tied to annotations over looping decoration.
- Use camera movement only when it clarifies spatial structure.
- Use particles only when they explain flow, direction, accumulation, recency, focus, anomaly, risk, or state. State what one particle represents and what it must not imply.
- For sparkles, fire, glow, pulse, or other attention effects, tie the effect to selection, anomaly, change, alert, or narrative focus, not generic importance.
- Do not hide the main evidence behind an intro animation.
- Do not use parallax, scroll-scrubbed motion, or sticky full-viewport scenes unless the motion reveals evidence and the same claim survives a static key frame.

## Human Visual Review

Before accepting an editorial visual story, review it like an editor:

- What is the one sentence the reader should carry away?
- Does the default view communicate that sentence?
- Does the imagery earn its place analytically, or is it just attractive?
- Is the chart still truthful if the visual metaphor is removed?
- Are labels placed by judgment, or do they look auto-dropped?
- Is any element visually impressive but analytically idle?
- If WebGL or particles are used, could the editor explain why Canvas2D, SVG, static arrows, labels, or small multiples were insufficient?
- Does the mobile portrait version preserve the reading path, main visualization visibility, caveat, and source context?
- Is mobile landscape provided when a wide handheld view carries the evidence better?
- Do touch, keyboard, stale/offline, and permission-denied paths preserve the story?
- Would a screenshot be intelligible in a social preview, slide, or print clipping?
- For fictional stories, can the reviewer tell what was simulated, why the simulation is coherent, and which deterministic data fields support each visual layer?

## Red Flags

- Bordered chart cards arranged as a gallery when the task asked for an editorial story.
- Generated background art with a normal chart pasted on top.
- Scrolljacking or decorative parallax that makes the reader fight native scrolling.
- Animation that loops without revealing evidence.
- Particles, sparkles, fire, glow, or motion used as visual texture instead of evidence.
- 3D perspective used for ordinary categorical comparison.
- Gorgeous imagery that prevents data labels from being read.
- A visual metaphor that changes the perceived denominator or scale.
- The page needs instructions because the composition has no reading path.
- Fictional data is too sparse to support the promised visual density, leaving the story dependent on walls of text, atmospheric art, or unsupported claims.

## Source Links

- [2025: The Year in Visual Stories and Graphics](https://www.nytimes.com/interactive/2025/12/22/us/2025-year-in-graphics.html)
- [D3: Data-Driven Documents](https://idl.uw.edu/papers/d3)
- [Mike Bostock: How To Scroll](https://bost.ocks.org/mike/scroll/)
- [Scrolling into the Newsroom](https://www.benjamins.com/catalog/idj.22005.oes)
- [The Truthful Art by Alberto Cairo](https://www.oreilly.com/library/view/the-truthful-art/9780133440492/ch05.html)
- [Amanda Cox on visualization's "Aha!" moments](https://hbr.org/2013/03/power-of-visualizations-aha-moment)
- [Jen Christiansen](https://www.jenchristiansen.com/about)
