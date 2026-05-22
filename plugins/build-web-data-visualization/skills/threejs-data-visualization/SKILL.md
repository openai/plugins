---
name: threejs-data-visualization
description: Render WebGL-accelerated data visualizations with Three.js, raw WebGL, deck.gl, luma.gl, PixiJS, Sigma.js, Plotly WebGL traces, ECharts GL, CesiumJS, Babylon.js, or related GPU libraries. Use when the visualization needs true spatial structure, dense 2D or 3D GPU rendering, particle or flow animation, volumetric views, or interactive exploration that adds real analytical value.
---

# Three.js and WebGL Data Visualization

## Overview

Use this skill when the user truly benefits from 3D, GPU-heavy 2D, shader-driven animation, or WebGL-accelerated interaction. Three.js is appropriate for volumetric data, 3D point clouds, spatial trajectories, surfaces, scientific or immersive scenes, and custom particle systems. WebGL or WebGL-backed libraries are also appropriate for dense 2D scatterplots, animated networks, flow maps, particle trails, GPU aggregation, or custom shader effects that exceed practical SVG/DOM limits and are not a good fit for Canvas2D.

Default assumption: use the simplest truthful renderer that meets the scale and interaction requirements. 3D is justified only when depth carries analytical meaning. WebGL is justified when GPU throughput, shader control, large mark counts, or animation quality matter enough to offset accessibility, export, debugging, bundle, and GPU-memory costs. Cosmetic 3D or decorative particles are regressions.

Mobile GPUs, touch gestures, battery, thermal limits, and permissions can change the renderer choice. Use `../../references/foundations/mobile-first-responsive-visualization.md` for mobile portrait/landscape contracts, AR/camera/motion/vibration decisions, visual viewport behavior, spotty connection handling, and touch-first controls.

## Choose WebGL When

- the data is inherently spatial, volumetric, trajectory-based, or surface-based
- depth, orbit, slicing, or perspective reveals structure unavailable in 2D
- an editorial story needs camera states to reveal a meaningful surface, volume, terrain, or multiaxis relationship
- GPU instancing, texture-backed data, or shader-based rendering materially improves scale
- dense 2D plots, networks, or maps need hundreds of thousands to millions of marks, continuous pan or zoom, or real-time filtering
- animated flow, trips, particles, or transitions must remain smooth without generating thousands of DOM or SVG elements
- the view needs GPU picking, custom blending, post-processing, or shader effects tied to data attributes
- the experience needs immersive or exploratory navigation
- AR or camera-backed spatial inspection adds analytical value and has a non-permission fallback

## Avoid WebGL When

- the same comparison is clearer in 2D
- labels and exact values dominate the task
- the chart will mostly be consumed as a static document
- a declarative grammar, D3/SVG, or Canvas2D can handle the mark count with less maintenance and better export/accessibility
- the required effect is mostly decoration, novelty, or attention capture without a specific analytical verb
- the page will show many small charts where WebGL context pressure and GPU memory would outweigh per-chart speed

## Library Selection

- Three.js: custom 3D scenes, point clouds, instancing, particles, shader materials, camera-led stories, and 3D analytical surfaces.
- deck.gl: high-volume geospatial and non-geospatial layers, GPU aggregation, picking, animated trips, arcs, paths, point clouds, and overlays on MapLibre, Mapbox, Google Maps, or ArcGIS.
- luma.gl: low-level WebGL2 or WebGPU-leaning GPU programming when deck.gl abstractions are too high-level but raw WebGL would be too much boilerplate.
- raw WebGL2: maximum control for custom shaders, data textures, transform feedback, framebuffers, or unusual render pipelines; reserve for teams comfortable owning GPU lifecycle and debugging.
- regl or TWGL: lighter low-level WebGL wrappers when custom shaders are needed without a full scene engine; regl is especially good for command-style, state-minimized rendering.
- PixiJS: GPU-accelerated 2D sprites, particles, texture atlases, labels-as-sprites, playful dashboards, and 2D editorial animation where a scene graph helps.
- Sigma.js: large interactive node-link graphs where WebGL rendering, graph layouts, hover states, and graph-specific affordances matter more than custom shader freedom.
- Plotly WebGL traces: fast scientific or product charts when a high-level declarative API is more important than custom rendering control.
- ECharts GL: configuration-driven 3D charts, globe views, and WebGL acceleration inside an ECharts product stack.
- MapLibre GL JS or Mapbox GL JS: vector-tile product maps, data-driven style layers, camera motion, heatmaps, and custom layers.
- CesiumJS: 3D globe, terrain, 3D Tiles, time-dynamic geospatial visualization, and high-precision WGS84 scenes.
- Babylon.js: full 3D engine features such as GPU particles, physics, rich materials, large-world rendering, and WebXR when the work is closer to an interactive simulation than a chart.

## Particle and Flow Effects

Use particle effects only when they make movement, accumulation, attention, or state more legible:

- flow particles along network edges, routes, pipes, links, or migration paths when direction and rate are the story
- trip trails or fading path segments when temporal progression matters
- pulsing, halo, shimmer, ember, or sparkle effects for selected, anomalous, high-risk, newly changed, or user-focused marks
- density particles, dot advection, or flow fields when a field is continuous and exact individual paths are not meaningful
- restrained fire, heat, glow, or hazard particles only when the metaphor matches the domain and does not trivialize serious subject matter

Do not use particles when they obscure totals, imply individual entities that are not in the data, overstate certainty, glamorize harm, or compete with labels and comparison tasks. Always provide a reduced-motion fallback and a static final or key frame.

## Default Architecture

1. Choose the renderer from data shape and interaction load before choosing visual style.
2. Prefer orthographic projection for chart-like 3D or 2.5D scenes.
3. Use perspective only when depth cues matter.
4. Keep data-to-scene transforms explicit and reversible.
5. Use GPU-friendly primitives:
   - `BufferGeometry`
   - instancing
   - points
   - sprites or billboards
   - texture atlases
   - typed arrays and binary attributes
   - shader materials when needed
6. Batch static marks, keep dynamic attributes narrow, and avoid re-uploading full buffers every frame.
7. Assess how many scenes may be visible at once, because GPU memory, context pressure, and overlay complexity change the recommendation.
8. Keep labels, legends, controls, and rich annotation in DOM or SVG overlays unless the scene truly demands in-canvas text.
9. For editorial stories, define named camera or animation states as part of the annotation plan: overview, focus, comparison, reveal, final.
10. Keep generated textures, basemaps, or illustrated backdrops separate from data geometry so they can be reviewed and swapped.
11. For custom shaders, define the data contract first: attributes, uniforms, textures, derived values, picking IDs, and fallbacks.
12. For particles, define emission source, path or field, speed, lifetime, color, opacity curve, decay, selection behavior, and reduced-motion state before coding.
13. For advanced scenes, complete `../../assets/templates/advanced-interactive-visualization-contract.md` before implementation. Name one primary scene owner, a true fallback path, coordinate frames, camera states, picking model, animation clock, interaction state machine, render-ready signal, and screenshot QA.
14. Never let a fallback or helper renderer duplicate the primary visual while WebGL is active. One renderer owns the focal scene; fallbacks appear only when the primary scene fails or is intentionally disabled.
15. For mobile, cap DPR or quality when needed, pause offscreen/inactive loops, lazy-load heavy assets with reserved dimensions, and define stale/offline rendering for streamed or tiled data.

## Interaction Rules

- Support reset view, focus target, and orientation cues.
- Keep camera behavior predictable.
- Use shortest-path rotation or named camera states when focusing spherical or cyclic data.
- Use brushing, filtering, aggregation, level of detail, or slicing when full-scene density becomes unreadable.
- Pair 3D navigation with 2D summaries where possible.
- Prefer GPU picking, spatial indexes, ID buffers, or screen-space nearest-mark picking for dense hit testing; avoid per-mark DOM overlays except for selected or focused marks.
- Respect reduced-motion by providing direct camera-state controls, paused particles, a stepped sequence, or a static key-frame sequence.
- Preserve browser interaction expectations. If the scene captures wheel, pinch, or drag, provide clear reset and alternate controls.
- On mobile, provide tap/focus selection, step-through or search for dense marks, explicit zoom buttons or two-finger gestures, and a portrait fallback when landscape is the richer inspection mode.
- Use WebXR, camera, device motion, vibration, notifications, or geolocation only when the capability has a named analytical purpose, a user-initiated permission moment, and an accessible fallback.

## Output Expectations

- Justify the WebGL choice against SVG, DOM, Canvas2D, and declarative options.
- Preserve orientation and scale cues.
- Provide screenshot or image export paths when the result must appear in reports.
- Keep labels, legends, and summaries readable in 2D overlays when exact reading matters.
- For animated WebGL, state the animation verb, frame budget, clock model, reduced-motion behavior, and static fallback.
- For particle effects, state what each particle represents, what it must not be interpreted as, and how opacity/lifetime/rate map to data.
- For glows, pulses, halos, thickness, blur, shimmer, or selection effects, state the exact data field or interaction state they encode. If the effect has no mapping, remove it.
- For editorial 3D or particle stories, state the first frame, final frame, camera or motion states, and 2D/static fallback.
- For new work, include a technical design section covering simultaneous scene count, GPU memory, context pressure, buffer update patterns, interaction costs, and maintenance tradeoffs versus Canvas2D and SVG/DOM alternatives.
- For mobile work, include portrait and optional landscape framing, touch/pinch/camera-control behavior, DPR/quality budget, battery/thermal assumptions, permission-gated capability fallbacks, and spotty-connection behavior.
- For globe, terrain, or map-like scenes, include coordinate-alignment checks for texture, basemap, markers, labels, hit testing, camera focus, and fallback geometry.

## References

- Shared theory:
  - `../../references/foundations/task-abstraction-and-chart-selection.md`
  - `../../references/foundations/art-directed-interactive-visual-stories.md`
  - `../../references/foundations/perception-color-and-encoding.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
- Skill references:
  - `./references/when-3d-is-justified.md`
  - `./references/scene-architecture-and-encodings.md`
  - `./references/gpu-scaling-and-interaction.md`
  - `./references/webgl-library-selection.md`
  - `./references/webgl-2d-animation-patterns.md`
  - `./references/particle-effects-and-flow.md`
  - `./references/scene-readiness-and-interaction-qa.md`
  - `./references/cutaway-terrain-and-domain-scenes.md`
- Templates:
  - `../../assets/templates/advanced-interactive-visualization-contract.md`

## Representative Prompts

- "Visualize trajectories in 3D with brushing and focus."
- "Render a dense point cloud with GPU instancing."
- "Build a volumetric or surface view with supporting 2D annotations."
- "Tell me whether this should stay 2D or move to Three.js."
- "Design a Three.js scene that still reads clearly in screenshots."
- "Build a WebGL scatterplot or network that can animate hundreds of thousands of marks."
- "Use particles to show flow between nodes without making the chart feel decorative."
- "Choose between deck.gl, Three.js, PixiJS, regl, raw WebGL, and Canvas2D for this visualization."
