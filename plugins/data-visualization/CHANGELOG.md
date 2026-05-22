# Changelog

## 0.1.19 Build Web Data Visualization

- Renamed the plugin manifest, user-facing metadata, and icon accessibility labels to `Build Web Data Visualization`.

## 0.1.18 Web Data Visualization Plugin

- Renamed the plugin manifest and user-facing metadata to `Web Data Visualization Plugin`.
- Removed the former language-specific visualization skill, starter templates, and reference pages.
- Removed non-web routing, keywords, source-index links, and adjacent-skill references from the remaining web-focused visualization guidance.

## 0.1.17 OpenAI-Style Manifest And Operational Workspaces

- Updated the plugin manifest to remove TODO metadata, keep `Ben Lesh` as author and developer, use a human-facing display name, add OpenAI-style policy URLs, add real icon assets, and trim keywords to high-signal discovery terms.
- Added an `operational-visualization-workspaces` foundation reference for console-style visualization products, including tri-pane desktop shells, mobile command bars, synchronized outlines, central viewports, inspectors, default selections, pan/zoom rules, URL state, and live/stale operational states.
- Updated umbrella, strategy, React/Next.js, UML/software architecture, node-link layout, and testing skills so dense dashboards, architecture explorers, schema/state-machine inspectors, maps, and graph workspaces route through the new operational-workspace guidance.
- Expanded visual design, advanced interactive, and test-plan templates with command/status bars, outline/filter/detail panels, central viewport behavior, inspector synchronization, default focus, empty-surface click versus drag, and mobile command-panel QA.

## 0.1.16 Mobile-First Responsive Visualization

- Added a shared `mobile-first-responsive-visualization` foundation reference that makes mobile portrait and large-screen delivery default sibling surfaces, with mobile landscape required when the evidence, substrate, keyboard pressure, or device capabilities need it.
- Updated concept-first design guidance so advanced visual/page-layout work generates and reviews a large-screen concept image plus a mobile portrait concept image by default, and a mobile landscape concept image when justified.
- Strengthened mobile contracts around keeping the main visualization visible, returning to the chart after settings changes, touch/pinch/drag/keyboard behavior, on-screen keyboard real estate, hover replacements, and enlarged hit areas.
- Added mobile capability audit guidance for AR/WebXR, camera, motion/orientation, vibration, notifications, and geolocation, including analytical-purpose, permission-timing, privacy, battery/data, and fallback requirements.
- Added spotty-connection guidance for streaming or remote data: last-known-good state, stale/live/offline/partial indicators, reconnect behavior, low-bandwidth degradation, and mobile dashboard alerting.
- Updated umbrella, strategy, React/Next.js, TypeScript, dashboard, map, D3, Canvas, WebGL, scrollytelling, accessibility, testing, contracts, briefs, review checklists, source indexes, plugin metadata, and README guidance to treat mobile data visualization as a first-class design and QA surface.

## 0.1.15 Shareable State, Persistence, And Contrast Defaults

- Added a shared `shareable-state-and-persistence` foundation reference that makes URL-driven visualization state the default for meaningful filters, selections, ranges, zoom/camera state, tabs, drill-down paths, and saved-view ids.
- Added persistence guidance for localStorage, IndexedDB, and remote saved views, including precedence rules where incoming URL state overrides private persisted state.
- Strengthened color guidance around semantic color-role ledgers, contrast hierarchy, WCAG 2.2 text and non-text contrast checks, redundant encoding, and avoiding overloaded hue meanings.
- Updated progressive disclosure guidance so configuration, filter-builder, inspector, and drill-down areas are collapsed or closable when secondary, while active filters, selections, caveats, and source context remain visible.
- Updated React, TypeScript, accessibility, implementation, visual-contract, advanced-interactive-contract, testing, chart-brief, and human-review guidance to include share links, saved views, persistence, contrast review, and collapsed-control QA.
- Updated plugin metadata and source indexes with URL, storage, disclosure, and WCAG 2.2 references.

## 0.1.14 Advanced Interactive Visualization Contract

- Added an advanced interactive visualization contract for WebGL, 3D, geospatial, cutaway, particle, and multi-layer visualizations.
- Strengthened Three.js and geospatial guidance around renderer ownership, coordinate alignment, mark semantics, dense picking, camera focus, fallbacks, source ledgers, and interaction state machines.
- Added Earthquake-derived QA guidance for nonblank WebGL rendering, fallback screenshots, coordinate spot checks, and live interaction smoke tests.
- Added static tests for bundled Playwright starter templates.
- Trimmed manifest default prompts to the three prompts Codex can surface and shortened manifest-facing summary copy.

## 0.1.13 Mandatory Visual Concept Trigger

- Strengthened the umbrella and strategy skill frontmatter so visual page-design, layout mockup, and generated concept-image prompts are discoverable before the skill body loads.
- Made Codex image generation mandatory, not optional, when advanced visualization/page-layout composition affects understanding and the user asks to see a design direction, mockup, concept, key frame, or visual treatment.
- Added explicit mandatory trigger language to the meaning-preserving visual design workflow and art-directed visual-story guidance, including a fallback instruction for runtimes without image generation.
- Updated plugin metadata, keywords, and default prompts to advertise the visual-design concept path.

## 0.1.12 Binding Concept Contract Fidelity

- Strengthened approved Codex image-generated visualization concepts from "design direction" into binding semantic design contracts.
- Added locked versus flexible concept-element guidance so implementation preserves the approved layout, hierarchy, label-safe regions, interaction staging, data-bound layers, and mobile/export continuation.
- Required material deviations from approved concepts to be named, approved, or recorded as meaning-preserving instead of silently reinterpreting the concept.
- Added contract-fidelity QA and concept-to-result traceability requirements across umbrella, strategy, React/Next.js, TypeScript, scrollytelling, reports/decks, testing, accessibility, and template guidance.
- Updated plugin metadata, keywords, and starter prompts to advertise contract-bound image concept workflows.

## 0.1.11 User Approval Gate For Generated Concepts

- Added an explicit user design approval gate to the meaning-preserving visual design workflow: after Codex generates a design concept image or key-frame set, the plugin must show it to the user and wait for approval or requested iteration before implementation continues.
- Tightened the gate into an iterative user-review loop: generate the concept image, describe the plan and interactions in concise bullets, ask for approval or specific changes, revise or regenerate from feedback, and repeat until the user agrees on the design.
- Clarified that project changes, renderer-specific implementation work, asset finalization, and code generation must not begin while concept approval is pending.
- Updated semantic design contracts to record approval status, approval scope, approved concept references, review notes, and requested changes.
- Updated umbrella, strategy, scrollytelling, report/deck automation, React/Next.js, TypeScript, testing, and accessibility guidance so concepted visualization work treats user approval as a workflow gate, not an optional review.
- Expanded editorial, storyboard, generated-asset, test-plan, and human-review templates with approval status and iteration fields.
- Updated plugin metadata, keywords, and starter prompts to advertise user-approved concept workflows.

## 0.1.10 Meaning-Preserving Visual Design Workflow

- Added a `meaning-preserving-visual-design-workflow` foundation reference for Codex image-generated visualization concepts, existing-page integration concepts, per-layer concepts, generated assets, and animation key-frame concepts.
- Defined evidence-gated concepting so routine charts stay lightweight while editorial infographics, reports, decks, visual articles, scrollytelling, parallax, composite layouts, generated imagery, animation, and page placement can use concept-first design when composition affects understanding.
- Introduced semantic design contracts: accepted concepts must preserve the claim, evidence hierarchy, labels, caveats, source context, animation purpose, data-bound layers, and layout intent instead of acting as moodboards.
- Added a `visual-design-contract` template and expanded editorial briefs, interactive storyboards, image-generation asset briefs, visualization test plans, and human visual review checklists with concept scope, accepted concept references, editable data layers, semantic fidelity QA, and existing-page context intake.
- Updated umbrella, strategy, scrollytelling, report/deck automation, React/Next.js, TypeScript, testing, and accessibility skills so advanced visualization work invokes the new workflow and validates both visual fidelity and evidence fidelity.

## 0.1.9 Node-Link and Diagram Layout

- Added a dedicated `node-link-and-diagram-layout` skill for automatic layout of connected-node diagrams, including network diagrams, dependency graphs, decision trees, database schema diagrams, ERDs, state machines, and other line-connected node views.
- Added focused references for algorithm selection, layered versus tree versus force versus radial layout families, orthogonal routing, overlap removal, planarization, layout stability, and readability QA.
- Updated umbrella routing so auto-arrangement prompts route to the new layout specialist before renderer-specific work.
- Updated the UML and software architecture skill so notation selection and source-format work stay there, while layout-specific questions explicitly route through the new cross-cutting layout skill.
- Added graph-drawing research and official implementation links for Sugiyama-style layered layout, Graphviz engines, ELK layered and routing options, tidy tree layouts, force and stress methods, overlap removal, planarization, and graph-layout aesthetics.
- Updated plugin metadata, keywords, and prompts so graph-layout and auto-layout work is discoverable alongside UML, Gantt, scrollytelling, and general visualization tasks.

## 0.1.8 UML and Software Architecture Visualization

- Added a dedicated `uml-and-software-architecture-visualization` skill for formal UML, UML-like diagrams, software architecture diagrams, ERDs, database schema diagrams, C4, BPMN, swimlanes, flowcharts, state machines, network diagrams, diagram-as-code formats, and interactive diagram editors or explorers.
- Added focused UML references for diagram selection, formats and interchange, TypeScript/web rendering, interactive diagram patterns, and quality/accessibility/export/testing.
- Added UML diagram brief and interactive UML test-plan templates.
- Updated umbrella routing, strategy heuristics, prompt routing examples, chart-selection guidance, stack-selection defaults, adjacent implementation skills, source indexes, and plugin metadata so UML and software architecture prompts route to the new specialist before renderer-specific work.
- Added conservative source-backed guidance for XMI/UMLDI, PlantUML, Mermaid, Graphviz DOT, D2, Structurizr DSL, DBML, BPMN XML, and interactive React/TypeScript diagram products.
- Added interactive architecture explorer refinements for calm side rails, focused single-schema and single-state-machine views, layered topology layout, hover versus selection emphasis, and ERD connector routing through gutters instead of under table bodies.
- Added generic explorer guidance for synced navigation trees, full-width filter controls in narrow rails, scrollable intrinsic canvases when labels would otherwise become unreadable, and state-transition labels rendered above nodes only when focused.
- Added explicit layout QA checks for cumulative schema auto-placement, subdued zone separators instead of competing region cards, and selected/search label overlays that never disappear behind state nodes.

## 0.1.7 Gantt Chart Guidance Upgrade

- Added a dedicated `gantt-chart-visualization` skill for Gantt charts, project schedules, roadmaps with task spans, milestones, dependencies, predecessors, critical path, baselines, WBS, resource plans, capacity timelines, and schedule import/export work.
- Added focused Gantt references for chart-fit decisions, interaction patterns, API and export-format ingestion, normalized data contracts, performance and rendering, accessibility, export, and testing.
- Added source-reading guidance for MS Project XML/CSV/PDF/XPS, Primavera P6 XML/XER, Jira and Advanced Roadmaps, GitHub Projects GraphQL/TSV, Smartsheet predecessors, monday.com timeline/dependency columns, Asana JSON/CSV, ClickUp task dates, Azure DevOps iterations, and generic CSV/TSV/XLSX/JSON.
- Updated umbrella routing, strategy heuristics, prompt-routing examples, chart-selection guidance, stack-selection defaults, plugin metadata, and source indexes so Gantt and project-management schedule prompts route to the new specialist skill before renderer-specific work.
- Added conservative mapping rules: preserve source IDs and provenance, validate dependency cycles and missing targets, distinguish planned schedules from actual lifecycle timelines, and avoid inferring schedule dates from issue timestamps unless requested.

## 0.1.6 Embedded Visualization Self-Use

- Added an `embedded-visualization-self-use` foundation reference for reports, decks, editorial stories, scrollytelling pages, visual articles, and composite infographics.
- Upgraded the umbrella workflow so meaningful embedded visual layers must be inventoried, assigned a specialist owner, mini-briefed, QA checked, and handled with authorized delegated fresh context or an explicit local specialist pass.
- Updated report, scrollytelling, strategy, testing, fictional-story, art-directed-story, storyboard, rubric, and human-review guidance so embedded visuals are not treated as generic cards or layout decoration.
- Added guarded delegation rules: use fresh agents only when the runtime supports them and the user has explicitly authorized delegation; otherwise load the relevant specialist skill locally and record that fresh-pass status.
- Updated plugin metadata and prompts to advertise mini-brief-based embedded visualization review.

## 0.1.5 SVG Polish Defaults

- Added a `svg-polish-and-crispness` D3 reference with concrete professional defaults for SVG chart typography, axis ticks, tick padding, gridlines, data strokes, outlines, icon sizing, crisp rendering, zoom-stable strokes, responsive checks, and export review.
- Updated D3 guidance to require explicit SVG polish before shipping custom vector visualizations, including D3 axis styling, `shape-rendering` usage, and `vector-effect` guidance.
- Updated umbrella and editorial infographic defaults so SVG-based charts recommend specific text sizes, line weights, icon sizes, and responsive review checks instead of vague "clean up the chart" advice.
- Added SVG polish checks to the human visual review checklist.
- Added official implementation sources for D3 axes, SVG rendering attributes, WCAG contrast, and Material icon sizing.

## 0.1.4 Fictional Story Data Richness Upgrade

- Added a `fictional-data-story-simulation` foundation reference for invented, illustrative, and synthetic data stories.
- Added a minimum data richness contract for fictional editorial and parallax work: entity, temporal, spatial or physical, event, outcome, and derived comparison layers.
- Added an embedded visualization self-use gate requiring reports, stories, parallax, editorials, and decks to route each embedded visual layer through the relevant plugin specialist skill.
- Updated umbrella routing, strategy, scrollytelling, TypeScript, testing, art-directed, storyboard, and rubric guidance so sparse fictional data is treated as a design blocker rather than a copywriting problem.
- Expanded the Cloud Orchard demo into a deterministic 21-day, 72-ship fictional simulation with hourly telemetry, weather fields, events, route segments, altitude shelves, districts, depots, derived summaries, and data invariants.
- Upgraded the Cloud Orchard story with denser scene-specific visualizations: moisture profile heat strips, route comparison scatter, altitude/yield swarm, storm heatmap, recovery flow, risk/yield scatter, service log, and interactive atlas tabs.
- Expanded Cloud Orchard image and video prompts into a reusable asset bible for consistent sky harvest ships, cloud shelves, Threadfall storm media, atlas substrates, cutouts, and optional frame sequences.

## 0.1.3 Parallax Scrollytelling Upgrade

- Added a dedicated `scrollytelling-and-parallax-data-visualization` skill for parallax scrolling, sticky graphics, scroll-driven timelines, Scrollama, ScrollTrigger, ScrollTimeline, view timelines, moviescrollers, rich-media timelines, and scroll-scrubbed data stories.
- Added focused references for scrollytelling story patterns, scene contracts, implementation architecture, performance, accessibility, reduced-motion behavior, testing, and human review.
- Updated umbrella routing, strategy, React/Next.js, TypeScript, D3, accessibility, and testing guidance so scroll-driven stories route through a scene-contract and browser-behavior pass before renderer-specific implementation.
- Added source-index links for narrative visualization theory, scrollytelling vocabulary, Bostock and The Pudding practitioner guidance, platform APIs, animation performance, passive event listeners, lazy loading, and WCAG motion accessibility.
- Updated plugin metadata, keywords, and default prompts so parallax and scrollytelling data visualization work is discoverable.

## 0.1.2 WebGL Visualization Upgrade

- Expanded the Three.js skill into a broader WebGL visualization capability covering Three.js, raw WebGL2, deck.gl, luma.gl, regl, TWGL, PixiJS, Sigma.js, Plotly WebGL traces, ECharts GL, MapLibre, CesiumJS, and Babylon.js.
- Added decision guidance for when to choose SVG/DOM, Canvas2D, WebGL 2D, 3D, geospatial GPU layers, and low-level shader stacks.
- Added particle-effect and flow-animation guidance for networks, routes, trips, field advection, focus cues, sparkles, glow, fire, halos, and reduced-motion/static fallbacks.
- Updated routing, TypeScript library selection, geospatial stack selection, plugin metadata, and official source links so WebGL work routes to the right specialist path.
- Added WebGL references for library selection, 2D animation patterns, GPU scaling, scene architecture, and particle or flow effects.

## 0.1.1 Ukraine Infographic Lessons

- Added a sensitive geopolitical and humanitarian story reference for conflict, occupation, displacement, civilian harm, disaster, migration, and humanitarian visualizations.
- Added source-and-method ledger guidance that distinguishes measured, estimated, and schematic evidence layers before composition.
- Updated routing, strategy, geospatial, editorial, art-directed, brief, storyboard, human-review, and rubric guidance with lessons from the Ukraine war infographic: dated map states, visible source hierarchy, humane framing, restrained map interaction, and static screenshot accountability.

## 0.1.0 Editorial Infographic Upgrade

- Added an editorial infographic design system grounded in truthful, functional, story-driven visualization practice.
- Added an art-directed interactive visual-story layer for animation, generated imagery, illustrated substrates, 3D surfaces, cartographic flow fields, object marks, scrollytelling, and human visual review.
- Added strict defaults for insight titles, direct labels, annotation-driven explanation, restrained color, small multiples, mobile reading paths, and originality guardrails.
- Added strict rules that imagery must carry scale, place, mechanism, motion, or stakes; animation must have an explanatory verb; and reduced-motion/static fallbacks must preserve the claim.
- Tightened the originality guardrail: screenshots and publication examples must be treated as principle studies, with a documented original transformation and similarity check before rendering.
- Updated routing, strategy, D3, React/Next.js, TypeScript, and report automation skills to prefer explanatory editorial composition when the task calls for it.
- Updated accessibility guidance for generated imagery, complex scene descriptions, animation, reduced-motion behavior, and static export paths.
- Added chart brief, critique, accessibility, test-plan, editorial brief, interactive storyboard, image-generation asset brief, human review, example pattern, and evaluation rubric templates.
- Added source-index references for Cairo, Cox, Bostock/D3, Knaflic, Tufte, Christiansen, Columbia data visualization coursework, Datawrapper practitioner guidance, and the requested 2025 visual-stories page.
- Added a Next.js `/editorial` demo route with an original Ukraine war timeline using sourced territorial-control data, schematic map states, a drone-technology system diagram, human-impact visuals, source notes, and an editorial evaluation meter.
- Added shared TypeScript editorial rendering tokens and rubric helpers in the demo app.
- Updated demo navigation, metadata, palette, and selected demo titles toward calmer editorial hierarchy.
