# Meaning-Preserving Visual Design Workflow

## Purpose

Use this workflow when visual composition materially affects how a reader understands a data visualization. It adapts concept-first design practice for data visualization: Codex uses image generation to create visual design concepts when concepting is required, and the user-approved concept set is a binding semantic design contract, not a moodboard, loose design, or optional inspiration. The image-generation portion is collaborative: generate a large-screen and mobile concept set, review it with the user, revise or regenerate it from their feedback, and repeat until the user agrees on the design direction.

The contract must preserve the analytical claim, evidence hierarchy, source context, caveats, labels, animation purpose, layout intent, spatial relationships, visual hierarchy, interaction staging, mobile continuation, and output form. Visual fidelity matters because it is how the approved reasoning is carried into the final result. Do not proceed from a generated design concept set into implementation until the user has seen the large-screen and mobile concepts and explicitly approved the design direction or requested a targeted iteration. Do not make project changes or generate implementation code while concept approval is pending.

## When To Use It

Use this workflow for:

- editorial infographics, visual articles, reports, decks, and executive explanatory figures
- composite layouts with multiple charts, maps, diagrams, tables, insets, or media layers
- visualization placement inside an existing app page, report page, slide, or article surface
- scrollytelling, parallax, animated, 3D, WebGL, particle, flow, map, or illustrated data stories
- generated imagery, object marks, cutaways, textures, contextual scenes, or visual substrates
- redesigns where the current visualization is analytically valid but visually unclear, generic, or poorly integrated

Do not require it for routine single charts where the visual form, layout, labels, and audience fit are already clear. A simple bar chart, line chart, table with sparklines, or product dashboard tile should stay lightweight unless the composition itself is the hard problem.

## Mandatory Image Concept Triggers

When this workflow applies, Codex must invoke image generation before implementation or a text-only design handoff if the user asks for any of the following:

- visual design direction, visual page design, layout design, mockups, or concepts
- to "show me what we are considering," "help me design this," or "make this look" like a polished visualization
- advanced 3D, WebGL, map, cutaway, scrollytelling, parallax, generated-substrate, or composite infographic design where composition affects understanding
- key frames for animation, camera movement, scroll scenes, drill-down panels, or selected-state popovers
- existing-page integration concepts where a new visualization must fit into a specific app, report, slide, or article surface

If image generation is unavailable in the runtime, state that explicitly and provide the concept prompt and approval gate instead of presenting a text-only design as complete.

## Required Mobile Concept Pairing

When this workflow applies, generate at least two concepts by default:

- a large-screen concept
- a mobile portrait concept

Add a mobile landscape concept when the visualization uses a wide substrate, map, field/court, timeline, Gantt chart, matrix, network, video, WebGL/3D/camera scene, AR/camera/motion interaction, two-handed touch gestures, or keyboard-heavy controls. Use `mobile-first-responsive-visualization.md` for the design contract. Do not treat the mobile view as a crop of the large-screen concept unless the crop independently preserves the claim, labels, caveat, source context, interaction staging, and main visualization visibility.

## Core Stages

### 1. Evidence Lock

Before visual concepting, lock the evidence that the design must protect:

- one-sentence takeaway and insight title
- dataset, fields, metric, unit, denominator, geography, and time span
- required comparison, baseline, threshold, or reference state
- source and method notes
- uncertainty, missingness, aggregation, smoothing, or caveats
- truth invariants the concept and implementation must not violate
- for sensitive work, measured, estimated, schematic, disputed, and dated evidence states

If the evidence cannot support the promised claim, revise the claim or data model before generating concepts.

### 2. Page And Context Intake

When the visualization must live inside an existing page, app, report, slide, or article:

- inspect the existing surface before concepting
- capture or describe the current layout, grid, typography, palette, spacing, surrounding content, and interaction states
- identify the slot, viewport, scroll position, slide region, or report section where the visualization belongs
- preserve surrounding information architecture unless the user requested a redesign
- decide what the new visualization should change in the page's reading path

When a screenshot or reference is used as input for image generation, treat it as context. The generated concept must integrate the visualization into the actual surface, not invent an unrelated page.

### 3. Artifact And Layout Brief

Choose the artifact before the renderer:

- data-first chart
- generated object marks
- illustrated substrate
- cartographic flow field
- WebGL-accelerated 2D or particle scene
- 3D or camera-led surface
- scrollytelling or parallax sequence
- report, deck, or page layout with embedded figures

Write a short layout brief covering reading order, dominant evidence, annotations, direct labels, source/caveat placement, large-screen path, mobile portrait path, optional landscape path, main-visualization visibility around settings, and whether image generation is needed for the overall layout, individual figure, asset, or key animation frame.

For contextual substrates, state the substrate's evidence role before choosing style: orientation, scale, place, mechanism, motion, texture, or label-safe background. Reject substrates whose main contribution is generic mood. When motion, flow, density, intensity, or spread appears, define whether it is shown as measured data, modeled data, or schematic explanation, and prefer contours, sampled fields, trajectories, vector/particle fields with defined meaning, or annotated layers over decorative swaths.

### 4. Codex Image-Generated Concept Pass

When concepting is useful or required by the trigger list above, use Codex image generation from within Codex to produce the relevant visual design concept set.

Use the smallest concept pass that can answer the design question:

- one paired large-screen and mobile page, report, slide, or article layout concept set
- one paired large-screen and mobile visualization-only concept set
- one paired concept set for how the visualization fits into an existing surface
- per-layer or per-figure concepts for complex embedded visualizations
- key-frame concepts for animation, scrollytelling, parallax, camera moves, or progressive reveals
- asset-only concepts for object marks, cutaways, textures, contextual scenes, or substrates

Prompts must state the evidence role, intended reading path, target viewport or aspect ratio, data layers that remain editable, label-safe regions, source/caveat needs, mobile main-visualization visibility rule, touch/keyboard/spotty-connection constraints, and exclusions. Do not ask image generation to invent exact values, dense labels, axes, source notes, or factual claims unless the user explicitly wants a single reviewed static poster.

Reject or iterate on concepts that:

- make the data claim less clear
- hide essential values behind style
- bake factual labels into raster imagery unnecessarily
- imply unsupported precision, scale, causality, or geography
- look like a generic dashboard, wallpaper, or publication clone
- rely on generic AI atmosphere such as broad translucent brush strokes, wispy ribbons, bokeh/orbs, cinematic wallpaper, stock-photo haze, or decorative gradients that do not carry evidence
- depict motion, flow, density, intensity, or spread as painterly atmosphere when the story needs measured or clearly schematic contours, trajectories, sampled fields, particles, or annotated layers
- cannot preserve the claim as a still screenshot or reduced-motion state
- make the mobile version a squeezed desktop chart, hide the main visualization below controls, or drop essential source/caveat/context

### 5. User Design Approval Gate

After generating the concept image set or key-frame set, pause the workflow and show the design to the user before development continues.

- Ask whether the user is satisfied with the generated large-screen and mobile design direction.
- Describe the plan and interactions in concise bullet points, not a long prose proposal.
- Cover the plan bullets: concept scope, artifact mode, large-screen reading order, mobile portrait reading order, landscape rationale if present, editable data-bound layers, source/caveat placement, mobile or export path, and what would be built only after approval.
- Cover the interaction bullets when relevant: default state, hover replacement, tap/selection behavior, filters or controls, settings return path, animation or scroll states, reduced-motion behavior, keyboard/touch path, spotty-connection behavior, justified AR/camera/motion/vibration/notification capabilities, and what the interaction must not imply.
- Summarize what the concept is meant to preserve: claim, evidence hierarchy, visible data layers, labels/caveats/source placement, motion purpose, and page context.
- Ask for explicit approval or specific requested changes before doing any implementation work.
- Do not start implementation, renderer-specific coding, asset buildout, contract finalization, file edits, or code generation while approval is pending.
- If the user requests changes, revise or regenerate the concept, state what changed in concise bullets, show the revised concept, and repeat the approval gate until the user agrees on the design.
- If a composite story has separate page, figure, layer, asset, or key-frame concepts that govern implementation, each governing concept needs approval or an explicit user-scoped approval such as "approve the overall direction and let Codex tune the figure concepts."
- If the user is unavailable in a non-interactive run, stop with the concept images, concise plan/interactions bullets, evidence summary, and approval request instead of continuing.

Record:

- approval status: pending, approved, or rejected
- approved large-screen concept path or screenshot reference
- approved mobile portrait concept path or screenshot reference
- approved mobile landscape concept path or screenshot reference, if used
- approval response, date, or review note
- requested changes and whether they were resolved
- approval scope: overall layout, individual figure, existing-page placement, generated asset, motion key frames, or full implementation direction
- review summary bullets shown to the user before approval

### 6. Semantic Design Contract Extraction

After the user approves a concept set, extract a contract before implementation:

- approved large-screen concept path or screenshot reference
- approved mobile portrait concept path or screenshot reference
- approved mobile landscape concept path or screenshot reference, if used
- user approval status, response, and scope
- native aspect ratio, intended viewport or output size, and responsive continuation
- mobile portrait viewport, optional landscape viewport, and main-visualization visibility rule
- takeaway, title, subtitle, source/caveat placement, and evidence states
- chart, map, diagram, asset, media, annotation, control, and fallback inventory
- data fields and source layers bound to each visible element
- which labels, values, axes, legends, and notes must remain editable/data-bound
- generated assets, crops, label-safe regions, focal points, and alt text
- intentional deviations from the concept and why they preserve meaning
- mobile/narrow adaptation, touch/keyboard/spotty-connection/capability behavior, and export/static screenshot requirements

Treat the extracted contract as the implementation source of truth:

- Locked elements: artifact mode, reading path, dominant focal area, relative scale and placement of major regions, visual hierarchy, color roles, label-safe regions, source/caveat placement, editable data-bound layers, interaction or motion states, reduced-motion/static fallback, mobile portrait continuation, approved landscape continuation, and export continuation.
- Flexible elements: exact pixel spacing, final typography tokens, renderer-specific geometry, breakpoint mechanics, and minor asset crops, but only when they preserve the locked elements.
- Any material deviation must be named before implementation if predictable, or recorded during QA if discovered later.
- If a deviation changes the reading path, hierarchy, interaction meaning, source/caveat visibility, or visual role of generated imagery, return to the user for approval or regenerate the concept instead of silently adapting it.
- The final implementation should be traceable from concept element to code, asset, data field, or rendered layer.

The implementation may tune details only inside those constraints. It must not silently change the claim, comparison, data hierarchy, caveats, source context, visual hierarchy, layout proportions, interaction staging, or design process result.

### 7. Motion And Storyboard Pass

For animation, scroll, parallax, video, particles, flow, 3D, or camera movement:

- name the explanatory verb: reveal, move, accumulate, compare, transform, zoom, rotate, or highlight
- state what the first frame, key frames, and final frame prove
- define scene or progress states as data
- specify what one particle, moving mark, camera state, or transition represents and what it must not imply
- define reduced-motion behavior and a still-frame fallback
- ensure the main evidence is not hidden behind an intro or decorative loop

Use image generation for key-frame design when it helps place labels, annotations, substrates, or scene composition before code. User approval is required for key-frame concepts before animation implementation begins.

### 8. Implementation And Asset Discipline

Keep the final visualization editable, inspectable, and regenerable:

- begin implementation only after any required user design approval gate has passed
- implement data marks, labels, axes, source notes, caveats, and controls in code whenever practical
- use generated imagery as substrate, object marks, cutaway, texture, scene, or design reference, not as a substitute for data binding
- store final generated assets in deterministic project asset paths
- preserve prompt/version metadata when assets carry analytical meaning
- make the data-to-visual mapping explicit in code, template, report, or implementation notes

### 9. Semantic Fidelity QA

Compare the implementation against the user-approved concept and the evidence lock:

- visual fidelity: composition, hierarchy, spacing, color roles, label placement, imagery, responsive behavior, and motion states
- evidence fidelity: claim, comparison, denominator, scale, source, caveat, uncertainty, measured/estimated/schematic styling, and annotation meaning
- interaction fidelity: default visibility, hover/selection behavior, keyboard path, reduced-motion path, and mobile path
- export fidelity: static screenshot, PDF, slide, social crop, or report frame preserves the claim and caveat
- contract fidelity: every locked concept element is implemented, intentionally adapted within the contract, or recorded as an approved deviation

Record material mismatches and fix them, mark them as intentional deviations with a meaning-preserving reason, or return to the user for a revised contract. Do not ship a result that is merely "inspired by" the approved concept.

## Concept Prompt Requirements

Every concept prompt should include:

- the story takeaway and intended audience
- the artifact mode and delivery surface
- data layers that must remain editable after implementation
- approximate chart forms, labels, and annotation roles without asking for exact small text
- source/caveat placement needs
- mobile or output-size constraints
- touch, pinch, keyboard, visual viewport, spotty-connection, and device-capability constraints
- existing page or screenshot context, if applicable
- forbidden elements: copied publication identity, unsupported labels, misleading scale, decorative chart cards, ornamental motion, baked-in source notes, generic AI atmosphere, broad brush strokes, wispy ribbons, bokeh/orbs, cinematic wallpaper, and background visuals that do not carry evidence or orientation

## Output Expectations

When this workflow is used, state:

- whether concept generation is required and why
- the concept scope: page, existing-page integration, figure, embedded layer, asset, or key frame
- before approval: the generated large-screen and mobile portrait concept images, plus mobile landscape when needed, with concise bullets for the plan and any interactions, followed by an explicit approval or change-request question
- the user design approval status, approved concept references, and any requested iterations
- the semantic design contract summary
- the locked elements, flexible elements, and approved deviations that make the concept binding
- which data layers remain editable/data-bound
- the motion verb and reduced-motion/static fallback, if animation is used
- the semantic fidelity QA checks before completion
- the mobile fidelity QA checks before completion: portrait, optional landscape, settings return path, touch targets, keyboard-open viewport, stale/offline states, and capability fallbacks

## Red Flags

- A generated concept is treated as style inspiration only, with no evidence contract.
- A generated concept is approved, but the final result keeps only the vibe and not the layout, hierarchy, interaction staging, or data-layer promises.
- The concept looks polished but cannot explain the claim.
- Implementation begins before the user explicitly approves the generated design concept.
- Exact values, caveats, or source notes are baked into a raster image without need.
- The visualization is placed into an existing page without inspecting that page first.
- Motion is designed before its explanatory verb is named.
- The mobile or export version drops the caveat or changes the reading order.
- The mobile version is only the desktop DOM stacked vertically, with controls before the main visualization.
- Settings, filters, or an on-screen keyboard hide the main visualization without a quick return path.
- The concept uses AR, camera, motion, vibration, notifications, or geolocation without analytical purpose, user intent, permission fallback, and accessible alternative.
- Streaming or remote mobile data blanks the chart during poor connection instead of preserving a stale or partial state.
- A concept is implemented faithfully as pixels while changing the data meaning.
