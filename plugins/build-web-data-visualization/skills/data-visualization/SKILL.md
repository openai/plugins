---
name: data-visualization
description: Route web data visualization work. Use when the user needs chart choice, visual critique, dashboards, maps or geospatial views, Gantt timelines, UML/software diagrams, scrollytelling, reports or exports, testing, accessibility, browser implementation, or concept-first visual design.
---

# Web Data Visualization

## Overview

Use this skill as the implicit orchestrator for the plugin. Classify the task, choose the smallest useful specialist skill set, and route before doing deep chart, renderer, testing, accessibility, or export work. Specialist skills stay explicit-only unless this router hands off to them.

Default stance: the best visualization is the simplest truthful view that answers the user's question with the least decoding burden. Preserve evidence quality first: correct task abstraction, trustworthy data treatment, visible caveats, direct labels, accessible encodings, mobile viability, shareable state, and QA. Do not default to dashboards, 3D, animation, generated imagery, particles, or WebGL unless they carry analytical meaning.

Contextual imagery, atmospheric marks, and motion must be evidence-bearing. Do not use broad translucent brush strokes, wispy ribbons, bokeh/orbs, cinematic wallpaper, stock-photo haze, or decorative gradients as substitutes for data layers. When motion, flow, density, intensity, or spread appears, encode it with measured or clearly schematic contours, sampled fields, trajectories, particles with a defined unit or meaning, or annotated layers.

Mobile is a primary surface. Unless the user explicitly excludes it, treat large-screen and mobile portrait as sibling states. Add mobile landscape when a wide substrate, AR/camera/motion, two-handed interaction, or keyboard-heavy workflow needs it.

## Router Workflow

1. Classify the analytical job: comparison/ranking, time change, distribution/uncertainty, correlation, composition/flow, hierarchy/network, software/system structure, schedule, monitoring, geography, or export/reporting.
2. Classify the data shape: tabular, time series, multivariate, matrix, tree/graph, semantic diagram source, schedule/project plan, geospatial, stream, or generated/simulated story data.
3. Lock delivery constraints: static vs interactive, exploratory vs explanatory, browser/dashboard/report/PDF/slides, reuse level, scale, update rate, export, large-screen/mobile states, touch/keyboard/pinch, sensors, alerting, bandwidth, and persistence.
4. Define the reading path before the renderer: insight title, immediate evidence, on-demand detail, labels/keys/controls, caveats, mobile order, and what should stay visible when panels collapse.
5. Plan state explicitly: URL-backed filters, selections, ranges, zoom/map/camera, tabs, drill-down, saved-view ids, local/IndexedDB/remote persistence, invalid state, copy-link, refresh, and back-button behavior.
6. Choose whether a contextual substrate helps: map, field/court/track, floor plan, system schematic, terrain, object cutaway, or other domain surface. Use it only when it improves orientation or mark placement.
7. Route to the narrowest specialist skill. If the request spans several visual layers, read `../../references/foundations/embedded-visualization-self-use.md`, inventory the layers, assign owners, and use specialist passes for substantial layers.
8. For new implementation work, include a compact technical design before coding: instance count, data/interaction profile, renderer ownership, URL/persistence contract, mobile performance, page-level cost, maintenance tradeoffs, fallbacks, and QA.
9. For advanced visual design, use `../../references/foundations/meaning-preserving-visual-design-workflow.md` and `../../references/foundations/mobile-first-responsive-visualization.md`; generate large-screen and mobile concepts, pause for approval, and treat approved concepts as semantic contracts.

## Routing Matrix

- Strategy and critique: chart choice, hierarchy, narrative claim, visual critique, anti-patterns, layout reasoning.
- Declarative grammar: standard tabular charts that fit Vega-Lite, Vega, Observable Plot, or similar grammar.
- D3/SVG: bespoke SVG/DOM geometry, direct labels, axes, annotations, transitions, or crisp vector polish.
- Canvas2D: dense flat marks, frequent redraw, custom hit testing, sparkline tables, or repeated microcharts.
- Three.js/WebGL: GPU-scale marks, particles, flow, shader effects, true 3D, deck.gl, PixiJS, Sigma.js, CesiumJS, luma.gl, or raw WebGL when analytical value justifies it.
- Geospatial: maps, projections, basemaps, thematic layers, slippy/product maps, routes, zoom behavior, or cartographic interaction.
- Dashboards: monitoring, streams, coordinated views, alerting, stale/offline states, and operational workspaces.
- Statistical: distributions, intervals, uncertainty, missingness, aggregation, sampling, and analytical rigor.
- Gantt: project schedules, task spans, milestones, dependencies, baselines, critical path, resources, and PM tool imports/exports.
- Node-link layout: graph auto-layout, crossings, edge routing, overlap, stability, force/layered/tree/radial layouts.
- UML/software architecture: UML, C4, ERD, BPMN, sequence/class/activity/state diagrams, PlantUML, Mermaid, DOT, D2, Structurizr, DBML, XMI/UMLDI.
- Scrollytelling: scroll-driven state, sticky graphics, parallax, moviescrollers, Scrollama, ScrollTrigger, ScrollTimeline, key frames, reduced-motion scenes.
- React/Next.js: component ownership, hydration, client/server boundaries, dynamic loading, route/search-param state, bundle and export integration.
- TypeScript engineering: typed data contracts, reusable APIs, runtime boundaries, renderer adapters, URL codecs, saved-view schemas.
- Testing: unit/component/E2E, visual regression, mocks, dashboard QA, canvas/WebGL readiness, exports, and brittle-test avoidance.
- Accessibility: text alternatives, contrast, redundant encodings, keyboard/screen-reader paths, reduced motion, inclusive review.
- Reports/slides: PDFs, PowerPoint/Google Slides, document embedding, figure packaging, export assets, and regeneration.

When routing is unclear, read `./references/route-by-problem.md` or `./references/prompt-routing-examples.md`. When stack choice is unclear, read `./references/default-stack-selection.md`.

## Quality Gates

- The answer must name the analytical job, chart or artifact family, primary route, and fallback when reasonable alternatives exist.
- Explanatory work needs an insight title, takeaway, artifact mode, annotation plan, source/caveat placement, and mobile reading path.
- Prefer direct labels, embedded keys, small multiples, in-cell graphics, and annotation over detached legends, equal-weight dashboards, or hover-only discovery.
- Use a color-role ledger: neutral context, primary focal accent, optional comparison accent, and separate treatment for selected/focused/alert states. Check contrast, grayscale, and color-deficiency resilience.
- Treat accessibility, mobile, export, URL state, persistence, and QA as design inputs, not cleanup.
- Keep essential values visible without hover. On mobile, replace hover with tap/focus, enlarge hit regions, provide drag/pinch alternatives, and avoid control stacks that hide the main evidence.
- For live or remote data, prefer stale-but-visible views with last-updated, live/stale/offline/partial states, reconnect behavior, and low-bandwidth degradation.
- Prefer declarative grammars before D3, D3/SVG before Canvas when labels/axes dominate, Canvas before WebGL for simple dense flat marks, and WebGL/3D only when scale, picking, shaders, particles, flow, geospatial layers, or depth justify it.
- Motion, particles, generated imagery, domain substrates, and 3D must have a stated analytical purpose plus static/reduced-motion fallback.
- Use editorial hero and background substrates only when they improve orientation, scale, place, mechanism, or label-safe context. Quiet basemaps, terrain, thin cartographic linework, real/generated textures, or clear photographic crops are preferable to generic atmosphere.
- Include an art-direction QA pass for generic AI atmosphere: broad brush strokes, wispy ribbons, bokeh/orbs, one-hue drama, cinematic wallpaper, and background visuals that look polished but do not carry evidence or orientation.
- For sensitive geopolitical, conflict, disaster, displacement, or humanitarian work, use `../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md`; distinguish measured, estimated, disputed, dated, and schematic layers.
- For fictional or illustrative stories, use `../../references/foundations/fictional-data-story-simulation.md`; require enough deterministic simulated data to support the visual density.
- Treat visual references as principle studies. Transform the idea so the output cannot be mistaken for the reference layout, palette, type system, scene, or pacing.

## Response Contract

- For recommendations: give the primary route, fallback route, chart/artifact family, stack fit, immediate evidence, on-demand details, mobile path, URL/persistence state, accessibility notes, and QA checks.
- For implementation: route to the narrowest specialist skill, then state renderer ownership, coordinate/data encoding, interaction states, fallback/render-ready behavior, instance-count assumption, performance risks, and tests before editing.
- For concept-first visual design: use the shared design workflow, show the required concept set, ask for approval before implementation, then preserve approved concepts as semantic contracts.
- For composite deliverables: state the embedded visualization inventory, specialist owner for each meaningful layer, mini-brief, QA check, and delegated/local fresh-pass status.

## References

- Router references: `./references/route-by-problem.md`, `./references/default-stack-selection.md`, `./references/prompt-routing-examples.md`.
- Core foundations: `../../references/foundations/task-abstraction-and-chart-selection.md`, `../../references/foundations/perception-color-and-encoding.md`, `../../references/foundations/shareable-state-and-persistence.md`, `../../references/foundations/mobile-first-responsive-visualization.md`, `../../references/foundations/layout-hierarchy-and-self-explanatory-ux.md`, `../../references/foundations/implementation-design-and-tradeoffs.md`.
- Advanced workflows: `../../references/foundations/editorial-infographic-system.md`, `../../references/foundations/art-directed-interactive-visual-stories.md`, `../../references/foundations/meaning-preserving-visual-design-workflow.md`, `../../references/foundations/embedded-visualization-self-use.md`, `../../references/foundations/fictional-data-story-simulation.md`, `../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md`, `../../references/foundations/operational-visualization-workspaces.md`.
- Templates: `../../assets/templates/advanced-interactive-visualization-contract.md`, `../../assets/templates/visual-design-contract.md`, `../../assets/templates/chart-brief.md`, `../../assets/templates/visualization-test-plan.md`.
