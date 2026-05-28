---
name: typescript-data-visualization-engineering
description: Build typed data visualizations in TypeScript. Use when the user wants TypeScript visualization code, typed data models, browser visualization components, UML-like diagram models, interactive graph or architecture diagram contracts, scroll-driven scene contracts, library selection guidance, or a maintainable visualization architecture beyond React- or Next-specific concerns.
---

# TypeScript Data Visualization Engineering

## Overview

Use this skill when the visualization must live in a TypeScript application. The focus is not just chart rendering. The focus is reliable data contracts, clear component boundaries, maintainable integration architecture, and a renderer that fits the product surface.

If the request is specifically about React components, client or server boundaries, hydration, dynamic loading, or Next.js delivery constraints, route first to `../react-and-nextjs-data-visualization/SKILL.md`.

If the request is primarily about test strategy, mocks, screenshot coverage, or deciding which chart logic deserves unit tests, route first to `../testing-data-visualizations/SKILL.md`.

## Renderer and Library Selection

- D3: custom chart math, behaviors, and bespoke SVG or hybrid views.
- Observable Plot or Vega-Lite wrappers: fast, declarative 2D charts.
- Visx, Recharts, ECharts, or Chart.js: product-oriented chart layers when their abstraction fits.
- Canvas2D adapters: dense flat views, immediate-mode rendering, and custom hit testing where Canvas is simpler than WebGL.
- WebGL adapters: dense GPU-scale 2D, particles, flow animation, custom shaders, GPU picking, or true 3D.
- Three.js: spatial, volumetric, instanced, particle, or camera-led 3D scenes.
- deck.gl, PixiJS, Sigma.js, Plotly WebGL traces, ECharts GL, MapLibre, CesiumJS, luma.gl, regl, TWGL, or raw WebGL2 when their renderer model matches the data shape.
- Scrollama, CSS ScrollTimeline/ViewTimeline, Motion `useScroll`, or GSAP ScrollTrigger when a scroll-driven scene controller is needed.
- Image generation pipeline: produced assets, transparent cutouts, textures, and scene backgrounds that remain separate from data-bound overlays.
- Mermaid, PlantUML/Kroki, Graphviz/WASM, D2, Structurizr, React Flow, Cytoscape.js, Sprotty, JointJS, GoJS, ELK, or Dagre when the surface is UML, ERD, C4, flow, state, schema, dependency, architecture, or interactive diagramming.

## TypeScript Rules

1. Define the data schema before rendering.
2. Validate external data at the boundary.
3. Keep derived chart geometry in typed functions.
4. Separate:
   - data loading
   - transformation
   - scale creation
   - rendering
   - interaction state
5. Model selections, filters, tooltip payloads, URL state, persisted preferences, and saved-view payloads as explicit types.
6. Define a canonical view-state codec for shareable state: parse, validate, normalize defaults, serialize in stable order, and migrate or reject stale schema versions.
7. Keep ephemeral interaction state separate from durable state. Hover, drag-in-progress, animation frame, and pointer position should not leak into saved URLs or persisted workspaces.
8. For new work, assess the intended number of simultaneous visualization instances so the architecture reflects page-level costs instead of single-instance demos.
9. For editorial systems, model reusable design tokens, annotation specs, label placement rules, artifact modes, motion states, asset manifests, color-role ledgers, and rubric checks as typed data instead of ad hoc strings inside render code.
10. For fictional, synthetic, or illustrative stories, model the data-generating world explicitly. Include seed, assumptions, entities, temporal records, spatial or physical substrate, event windows, outcomes, derived comparisons, and invariants. Use `../../references/foundations/fictional-data-story-simulation.md`.
11. For concepted editorial, report, deck, generated-image, animation, scrollytelling, or existing-page integration work, use `../../references/foundations/meaning-preserving-visual-design-workflow.md` and `../../references/foundations/mobile-first-responsive-visualization.md`. Apply the shared workflow for concept images, large-screen/mobile variants, approval or iteration, and typed semantic design contracts for evidence locks, responsive states, generated assets, fallbacks, and approved deviations.
12. For scrollytelling or parallax, use `../scrollytelling-and-parallax-data-visualization/SKILL.md` and define a typed scene contract:
   - visible data layers
   - generated or illustrated assets
   - media assets
   - camera or transform state
   - annotation state
   - trigger or progress range
   - interaction state
   - static key frame
   - reduced-motion fallback
13. For generated imagery, keep asset metadata explicit: prompt version, source, dimensions, focal crop, label-safe regions, alt text, continuity group, and data fields that bind to it.
14. For UML-like or software architecture diagrams, use `../uml-and-software-architecture-visualization/SKILL.md` first and keep a renderer-neutral diagram model separate from Mermaid, PlantUML, React Flow, Cytoscape.js, Sprotty, JointJS, GoJS, DOT, D2, or Structurizr adapters.

## React Guidance

- Prefer React-owned structure and D3-owned math when both are in play.
- Keep expensive transforms out of repeated render paths.
- Use clear component boundaries between chart container, render layer, and controls.
- Plan export paths if the chart must appear in reports or documents.
- Treat specs, scales, derived marks, and tooltip payloads as explicit typed interfaces.
- Treat URL codecs, saved-view payloads, storage keys, schema versions, and invalid-state fallbacks as part of the visualization API.
- Treat editorial elements as first-class props: insight title, subtitle, artifact mode, source, notes, annotations, direct labels, motion states, image assets, large-screen layout, mobile portrait layout, optional mobile landscape layout, and mobile fallback.
- Model mobile interaction and resilience explicitly: pointer mode, touch target/hit-area policy, hover replacement, pinch/drag ownership, visual viewport or keyboard state, stale/offline/partial data state, permission-gated capability availability, and reduced-motion/low-power mode.
- For embedded visual stories, make specialist skill ownership explicit in data contracts or implementation notes so maps, swarms, distributions, flow layers, and export fallbacks are not treated as generic components.

## Output Expectations

- Pick libraries that fit the app architecture, not generic popularity.
- Keep types useful at runtime boundaries.
- Call out whether the chart is DOM, Canvas, WebGL, or hybrid.
- For WebGL, call out whether the implementation is Three.js, deck.gl, PixiJS, Sigma.js, Plotly/ECharts GL, MapLibre/Cesium, luma.gl/regl/TWGL, raw WebGL, or a hybrid overlay.
- For particles or flow animation, state what each particle represents, the clock model, reduced-motion behavior, and static fallback.
- For art-directed stories, call out whether imagery is generated or hand-authored, which layers remain data-bound, and how still-frame and reduced-motion fallbacks are represented.
- For concepted stories or figures, use the shared design workflow for concept images, approval status, binding semantic design contract type, approved references, locked and flexible elements, data-bound layer contracts, generated asset metadata, mobile/landscape continuation, approved deviations, and semantic fidelity checks.
- For scroll-driven stories, call out the scene contract, controller, native-scroll behavior, static frames, reduced-motion path, and mobile fallback.
- For interactive tools, call out the URL view-state contract, persisted-state tiers, precedence rules, copy-link behavior, back/forward behavior, and collapsed-control state.
- For mobile-capable tools, call out the mobile portrait and optional landscape contracts, main-visualization visibility rule, touch/pinch/keyboard behavior, spotty-connection handling, and justified AR/camera/motion/vibration/notification capabilities.
- For fictional stories, call out the simulation seed, regeneration path, data richness layers, invariants, and derived datasets that support each embedded visualization.
- Include a technical design section for new work covering instance-count assumptions, performance implications, and maintenance tradeoffs of the chosen contracts and renderer.

## References

- Shared theory:
  - `../../references/foundations/editorial-infographic-system.md`
  - `../../references/foundations/art-directed-interactive-visual-stories.md`
  - `../../references/foundations/meaning-preserving-visual-design-workflow.md`
  - `../../references/foundations/fictional-data-story-simulation.md`
  - `../../references/foundations/task-abstraction-and-chart-selection.md`
  - `../../references/foundations/perception-color-and-encoding.md`
  - `../../references/foundations/shareable-state-and-persistence.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
- Skill references:
  - `../react-and-nextjs-data-visualization/SKILL.md`
  - `../uml-and-software-architecture-visualization/SKILL.md`
  - `../scrollytelling-and-parallax-data-visualization/SKILL.md`
  - `../testing-data-visualizations/SKILL.md`
  - `./references/library-selection-for-builders.md`
  - `./references/react-and-framework-boundaries.md`
  - `./references/types-and-data-contracts.md`
  - `./references/export-and-product-integration.md`

## Representative Prompts

- "Build a typed React charting system."
- "Design the TypeScript chart contracts behind a React or Next.js visualization surface."
- "Design the typed scene contract for a scrollytelling or parallax data story."
- "Choose a TypeScript visualization library for this product."
- "Convert this D3 prototype into maintainable TypeScript."
- "Embed Vega-Lite or Observable Plot in a React app without losing control."
- "Design the types for selections, tooltips, and chart data contracts."
- "Design typed contracts for an interactive UML, ERD, architecture, state machine, or dependency diagram."
