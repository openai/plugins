---
name: data-visualization
description: Route web data visualization work. Use when the user needs chart choice, visual critique, dashboards, maps or geospatial views, Gantt timelines, UML/software diagrams, scrollytelling, reports or exports, testing, accessibility, browser implementation, or concept-first visual design.
---

# Web Data Visualization

## Overview

Use this skill as the orchestrator and umbrella entrypoint for visualization work. Its job is to classify the analytical task, delivery medium, layout hierarchy, interaction needs, and scale constraints before choosing a chart family, grammar, renderer, or narrower specialist skill.

Default assumption: the best visualization is the simplest truthful view that answers the user's question with the least decoding burden. Prefer self-explanatory layouts, labels, and defaults over explanatory UI prose. For explanatory or editorial work, lead with a concrete takeaway, artifact mode, annotation plan, and custom composition before choosing a renderer. Do not default to 3D, animation, generated imagery, or dashboards unless the problem genuinely requires them.

Mobile is a primary surface. Unless the user explicitly scopes the work away from mobile or large screens, accommodate both. For concept-first design, produce paired large-screen and mobile portrait concepts; add mobile landscape when a wide handheld orientation, camera/AR, two-handed interaction, keyboard pressure, or a wide substrate matters.

## Orchestrator Role

This is the only skill in this plugin intended for implicit invocation from broad user requests. Use it to identify the task, choose the smallest useful specialist skill set, and route immediately when the request is primarily about a specific medium, renderer, workflow, or QA concern. Specialist skills are available for explicit invocation or for handoff from this orchestrator.

## Core Workflow

1. Identify the analytical job:
   - comparison or ranking
   - trend or change over time
   - distribution or uncertainty
   - correlation or multivariate structure
   - composition or flow
   - hierarchy, network, topology, or node-link auto-layout
   - system structure, process, behavior, state, dependency, schema, or software architecture
   - project schedule, roadmap, dependency, milestone, baseline, or resource plan
   - monitoring, alerting, or operational review
   - geography or spatial reasoning
2. Classify the data shape:
   - tabular
   - time series
   - multivariate table
   - matrix
   - tree or graph
   - semantic model or diagram source
   - schedule or project plan
   - geospatial
   - stream
3. Lock delivery constraints:
   - static or interactive
   - exploratory or explanatory
   - browser, dashboard, report, PDF, or slide deck
   - one-off analysis or reusable product component
   - scale, update rate, and export requirements
   - large-screen, mobile portrait, and whether mobile landscape is required
   - touch, pinch, keyboard, on-screen keyboard, sensor, alerting, and spotty-connection constraints
4. Decide the default reading path:
   - the one-sentence takeaway the figure must prove
   - what must be visible immediately
   - what can be revealed on hover, selection, or drill-down
   - where labels, keys, controls, and summaries should live
   - how the view stays understandable without instructional filler text
   - how the mobile view keeps the main visualization visible or quickly restores it after settings changes
5. Plan shareability and persistence before choosing interaction details:
   - which filters, selections, time ranges, comparison groups, zoom/map/camera state, active tabs, drill-down path, or saved-view ids belong in the URL
   - which user-specific preferences, drafts, cached slices, annotations, or long custom configs belong in localStorage, IndexedDB, or remote storage
   - how incoming URL state overrides local persistence, how invalid or stale state is normalized, and what copy-link or saved-view affordance is needed
   - which configuration, drill-down, or details areas should be collapsed by default or made collapsible so the main evidence remains visible
6. Consider whether a domain-native contextual surface would reduce decoding cost or make the view more compelling:
   - field, court, rink, track, circuit, floor plan, instrument panel, timeline artifact, map-like plan, schematic, or other meaningful backdrop
   - official dimensions, coordinate systems, zones, paths, or landmarks that should shape mark placement
   - whether marks, labels, forces, collision, or interaction must adapt to the background instead of floating on a neutral plot
7. For editorial or interactive visual stories, choose the artifact mode before the chart library:
   - data-first chart
   - generated object marks or cutouts
   - illustrated substrate or technical diagram
   - cartographic flow field or risk surface
   - WebGL-accelerated 2D, particle, 3D, or camera-led surface
   - scrollytelling or parallax sequence with staged states
   - whether image generation is needed for objects, cutaways, textures, or contextual scenes
8. For editorial infographics, reports, decks, visual articles, scrollytelling, parallax, generated imagery, animation, composite layouts, or visualization placement inside existing pages, use `../../references/foundations/meaning-preserving-visual-design-workflow.md` and `../../references/foundations/mobile-first-responsive-visualization.md` when visual composition materially affects understanding. Apply those shared references for Codex image concept generation, large-screen/mobile concept sets, approval gates, semantic design contracts, and implementation deferral instead of restating that workflow here.
9. For reports, decks, editorials, scrollytelling, parallax, visual articles, or other composite deliverables with embedded visual layers, use `../../references/foundations/embedded-visualization-self-use.md` before composition. Inventory each chart, map, table-graphic, swarm, distribution, flow layer, particle layer, media overlay, key, inset, or fallback; assign a primary specialist skill owner; write a mini-brief covering job, data shape, encoding, interaction, fallback, accessibility, QA, and fresh-pass status; then use an authorized delegated or explicit local specialist pass for substantial layers.
10. For fictional, invented, synthetic, or illustrative editorial stories, use `../../references/foundations/fictional-data-story-simulation.md` before visual design. Require a coherent simulated world, deterministic seed, minimum data richness contract, and embedded visualization self-use gate.
11. For sensitive geopolitical, conflict, disaster, displacement, or humanitarian stories, create a source and method ledger before composition. Distinguish measured, estimated, and schematic layers in both data structures and visual styling.
12. When references or screenshots are provided, treat them as inspiration audits: extract the principle, state the original transformation, and avoid cloning any layout, scene, palette, type system, or interaction cadence.
13. For new implementation work, include a concise technical design assessment before committing to a stack or renderer:
   - how many visualization instances may appear at once
   - the per-instance data and interaction profile
   - the URL, persistence, and saved-view contract for shareable analysis state
   - the large-screen and mobile rendering budgets, including battery, DPR, and bandwidth assumptions where relevant
   - performance implications at page level, not just for one demo instance
   - maintenance and reuse implications
14. For advanced WebGL, 3D, geospatial, cutaway, particle, scrollytelling, or multi-layer interactive work, fill the relevant parts of `../../assets/templates/advanced-interactive-visualization-contract.md` after concept approval and before implementation. The contract must name renderer ownership, coordinate frames, visual encodings, interaction states, URL/persistence state, fallback/render-ready behavior, domain-scene assumptions, and QA checks.
15. Route immediately to the narrowest specialist skill.

## Routing Rules

1. Use `../visualization-strategy-and-critique/SKILL.md` for chart choice, critique, design reasoning, narrative framing, or anti-pattern review.
2. Use `../gantt-chart-visualization/SKILL.md` for Gantt charts, project schedules, roadmap task spans, milestones, dependencies, predecessors, critical path, baselines, WBS, resource plans, capacity timelines, and project-management imports or exports from MS Project, Primavera P6, Jira Advanced Roadmaps, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, Azure DevOps, CSV, TSV, XLSX, or JSON.
3. Use `../node-link-and-diagram-layout/SKILL.md` when the primary problem is how to auto-arrange connected nodes, reduce crossings, route edges, avoid overlap, preserve layout stability, or choose graph-layout algorithms for node-link diagrams, network diagrams, dependency graphs, state machines, database schemas, decision trees, or other line-connected nodes.
4. Use `../uml-and-software-architecture-visualization/SKILL.md` for UML, UML-like diagrams, software architecture diagrams, sequence/class/activity/state/use-case/component/deployment diagrams, ERDs, C4, BPMN, swimlanes, flowcharts, database schema diagrams, PlantUML, Mermaid, Graphviz DOT, D2, Structurizr, DBML, XMI/UMLDI, or interactive diagram editors and explorers when notation, source format, or modeling scope is the main question.
5. Use `../scrollytelling-and-parallax-data-visualization/SKILL.md` for parallax scrolling, scrollytelling, scroll-driven timelines, sticky graphics, Scrollama, ScrollTrigger, ScrollTimeline, view timelines, moviescrollers, or scroll-scrubbed data stories.
6. Use `../grammar-of-graphics-and-declarative-visualization/SKILL.md` as the default path for tabular charts that can be expressed declaratively.
7. Use `../d3-data-visualization/SKILL.md` for bespoke SVG or DOM visualization, custom interaction, or annotation-rich vector work.
8. Use `../canvas2d-data-visualization/SKILL.md` for dense 2D rendering, immediate-mode drawing, large mark counts, or repeated microcharts such as sparkline tables and walls when Canvas2D meets the interaction and animation needs with less complexity than WebGL.
9. Use `../threejs-data-visualization/SKILL.md` for true 3D, WebGL-accelerated 2D, raw WebGL, deck.gl, luma.gl, PixiJS, Sigma.js, Plotly WebGL traces, ECharts GL, CesiumJS, Babylon.js, particle effects, flow animations, GPU-scale marks, or shader-driven scenes that create real analytical value.
10. Use `../react-and-nextjs-data-visualization/SKILL.md` when the main problem is integrating charts into React or Next.js applications.
11. Use `../typescript-data-visualization-engineering/SKILL.md` for broader TypeScript browser architecture, typing, component APIs, and runtime boundaries beyond React or Next specifics.
12. Use `../testing-data-visualizations/SKILL.md` when the main problem is test strategy, visual regression, screenshot or image diff workflows, data mocking, dashboard QA, or deciding what not to test.
13. Use `../dashboards-and-real-time-visualization/SKILL.md` for monitoring, streaming, coordinated views, and operational dashboards.
14. Use `../statistical-and-uncertainty-visualization/SKILL.md` for distribution, interval, missingness, and analytical rigor questions.
15. Use `../accessibility-and-inclusive-visualization/SKILL.md` for accessible chart design, text alternatives, and review workflows.
16. Use `../geospatial-and-cartographic-visualization/SKILL.md` for maps, projections, cartography, and geospatial interaction.
17. Use `../reports-pdfs-and-slide-automation/SKILL.md` for reports, PDFs, slide decks, figure packaging, and document embedding.

## Defaults

- For publication-style, article, infographic, or executive explanatory work, use `../../references/foundations/editorial-infographic-system.md` before implementation.
- For browser, app, dashboard, article, or embedded visualization work, use `../../references/foundations/mobile-first-responsive-visualization.md` unless the user explicitly excludes mobile or large screens. Mobile and large-screen experiences are sibling states. Do not let a desktop left rail, prose column, filter builder, or settings stack appear before the main visualization on mobile just because of DOM order.
- For dense product workspaces, consoles, architecture explorers, live dashboards, schema/state-machine inspectors, map operations tools, or repeated analytical workflows, use `../../references/foundations/operational-visualization-workspaces.md`. Treat the main visualization as the work surface; put outlines, controls, filters, and inspectors in compact rails, command bars, drawers, or panels that stay synchronized with the selected evidence.
- For art-directed, animated, generated-image, scrollytelling, parallax, WebGL, 3D, particle, map-flow, or illustrated visual stories, also use `../../references/foundations/art-directed-interactive-visual-stories.md`.
- For advanced explanatory or composite surfaces where layout, imagery, animation, or page integration affects interpretation, use `../../references/foundations/meaning-preserving-visual-design-workflow.md` and `../../references/foundations/mobile-first-responsive-visualization.md` for concept generation, required approval, mobile variants, semantic design contracts, and concept-to-result QA.
- For ambitious interactive scenes, especially WebGL, 3D, globes, maps, cutaways, terrain, particles, and drill-down inspectors, use `../../assets/templates/advanced-interactive-visualization-contract.md` before coding so renderer ownership, coordinate alignment, mark semantics, interaction state, and fallback QA are explicit.
- For scroll-driven visual stories, also use `../scrollytelling-and-parallax-data-visualization/SKILL.md` before choosing Scrollama, ScrollTrigger, Motion, D3, Canvas, WebGL, video, or CSS scroll timelines.
- For fictional or illustrative visual stories, require a deterministic simulation with entity, temporal, spatial or physical, event, outcome, and derived comparison layers before building charts, imagery, animation, or parallax.
- For reports, stories, parallax, editorials, visual articles, or decks that embed multiple visualizations, inventory each embedded visual layer, write a mini-brief, and route it through the plugin's relevant specialist skill instead of treating it as page decoration. Use fresh delegated specialist work only when the runtime supports it and the user has explicitly authorized delegation; otherwise do the same pass locally by loading the specialist skill before designing that layer.
- For conflict, occupation, displacement, civilian harm, disaster, or humanitarian work, also use `../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md`.
- Use visual references as principle studies only. If a draft can be mistaken for the reference, change the composition, substrate, pacing, and styling until it is story-specific.
- Require every explanatory chart to have an insight title, not just a topic title.
- Prefer annotation-driven explanation over dashboards, KPI tiles, generic chart inventories, or hover-only discovery.
- Prefer a composed visual scene, substrate, or staged sequence over a grid of bordered chart tiles when the user asks for an editorial infographic.
- Prefer generated imagery only when it carries scale, place, mechanism, motion, or stakes. Keep labels and data layers editable whenever possible.
- Prefer animation only when it has an explanatory verb and a reduced-motion fallback.
- Prefer native scrolling, sticky positioning, and reversible scroll progress for scrollytelling. Avoid scrolljacking and decorative parallax.
- Prefer declarative grammars before bespoke rendering when the chart can be expressed cleanly.
- Prefer 2D over 3D unless depth is intrinsic to the data.
- Prefer Canvas2D over WebGL for simple dense flat marks when Canvas2D satisfies frame budget, hit testing, and maintenance needs. Prefer WebGL when mark count, GPU picking, shader effects, blending, particle count, 3D structure, geospatial layers, or continuous animation make SVG/DOM or Canvas2D impractical.
- Prefer particle effects only when they explain flow, direction, accumulation, recency, focus, anomaly, risk, or state. If one particle's meaning cannot be stated clearly, use a static mark, arrow, label, width, color, or annotation instead.
- Prefer direct labels, embedded or chart-adjacent keys, small multiples, and annotated evidence over detached legends and decorative chrome.
- Use color sparingly: one primary accent and one secondary accent unless the data semantics require more.
- Prefer meaningful domain context when it helps users orient quickly: a soccer pitch for player networks, a court for shot charts, a race circuit for telemetry, a floor plan for movement, or an instrument schematic for sensor data. Treat these as analytical scaffolds, not decoration.
- Prefer self-explanatory surfaces over explanatory copy. If a paragraph is teaching the viewer how to read the chart, improve the composition or labeling first.
- Prefer hover for preview and selection or drill-down for commitment. Do not hide essential values or labels behind hover alone.
- Prefer touch-first interaction on mobile: tap or focus replaces hover, drag has button or stepper alternatives, dense marks have enlarged hit regions or step-through controls, and pinch/wheel ownership is explicitly documented instead of fighting browser scroll.
- Prefer mobile capability audits for AR, camera, motion/orientation, vibration, notifications, and geolocation. Use them only when they add analytical value, ask permission after user intent is clear, and provide non-permission fallbacks.
- Prefer stale-but-visible live views over blank loading states on mobile networks. For streaming or remote data, show last updated time, live/stale/offline/partial status, reconnect behavior, and lower-bandwidth degradation rules.
- Prefer small multiples when repeated panels clarify comparison better than stacking, color, or interaction.
- Prefer tables with in-cell graphics, including sparklines, when row-wise lookup and compact trend comparison matter more than full standalone charts.
- Prefer source-backed UML, C4, ERD, BPMN, flowchart, state machine, and software architecture diagrams when the work is system documentation, process explanation, code/schema reverse engineering, or interactive diagramming. Route through the UML specialist before choosing Mermaid, PlantUML, Graphviz, D2, Structurizr, React Flow, Cytoscape.js, Sprotty, JointJS, GoJS, or a bespoke SVG renderer.
- Prefer explicit graph-layout routing for line-connected node diagrams before arguing about libraries. For auto-arrangement questions, route through `../node-link-and-diagram-layout/SKILL.md` before choosing ELK, Graphviz, Dagre, Cytoscape.js, React Flow, D3, Canvas, or WebGL.
- Prefer Gantt charts when planned time spans, milestones, dependencies, baselines, critical path, or resource scheduling are the main evidence. Route project-management API or export ingestion through the Gantt skill before choosing a renderer. Prefer Kanban, calendars, milestone timelines, dependency graphs, tables, or uncertainty views when those better match the task.
- Prefer explicit SVG polish defaults when SVG owns chart text, axes, icons, strokes, or labels. For bespoke SVG/D3 work, route through `../d3-data-visualization/references/svg-polish-and-crispness.md` so tick labels, direct labels, icons, gridlines, data strokes, outlines, and zoom behavior have concrete professional defaults.
- Prefer accessible defaults and exportable assets early, not as cleanup work.
- Prefer URL-addressable visualization state for meaningful filters, selections, ranges, zoom, map/camera targets, comparisons, tabs, and drill-down paths. Omit defaults, validate incoming state, avoid secrets or raw data in URLs, and keep copy-link/share actions obvious.
- Prefer persistence as a complement to URL state: localStorage for small personal preferences, IndexedDB for larger drafts/cached view specs, and remote storage for named shared views, permissions, cross-device continuity, or audit history. Incoming URL state should win over stale local state.
- Prefer collapsible configuration, filter-builder, drill-down, and inspector areas when they are not the main evidence. Keep active filters, selections, and caveats visible even when the controls are collapsed.
- Prefer a color-role ledger over ad hoc palettes: neutral context, one primary focal accent, optional secondary or comparison accent, and separate visual treatment for selection/focus/alerts so a single hue does not carry unrelated meanings.
- Prefer contrast hierarchy to decoration: make the most important data and annotation highest contrast, keep gridlines, basemaps, inactive series, and secondary context visibly quieter, and test the result in grayscale and color-deficiency scenarios.
- Prefer interaction contracts that do not fight the browser. If a visualization takes over wheel, pinch, or drag behavior, explicitly prevent page scroll or scroll chaining and provide an alternate control path.
- Prefer explicit uncertainty, missingness, and aggregation disclosure when conclusions depend on them.
- Prefer stack choices that survive repeated page-level instances, not just a single impressive prototype.

## Output Expectations

- Return one primary path and one fallback when multiple reasonable options exist.
- State the chart family, stack choice, and why it fits the task, audience, and medium.
- For explanatory work, state the takeaway, insight title, artifact mode, annotation plan, and mobile reading path.
- For mobile-capable browser work, state the mobile portrait plan, whether mobile landscape is needed, how the main visualization stays visible around controls and keyboard input, and how touch, pinch, alerting, sensors, and spotty connections are handled.
- For operational workspaces, state the large-screen shell, mobile command or panel model, default selection or focus region, outline/search/filter/inspector synchronization, pan/zoom/clear-selection behavior, and which state belongs in the URL.
- For art-directed work, state the image-generation or illustration plan, motion purpose, still-frame fallback, and human visual-review criteria.
- For concepted visual-design work, follow the shared design workflow references for concept images, approval status, approved references, locked and flexible elements, mobile/landscape continuation, approved deviations, and concept-to-result fidelity QA.
- For scrollytelling or parallax work, state the technique, scene contract, scroll trigger/progress model, reduced-motion fallback, mobile path, and static key frames.
- For reports, stories, decks, and other composite deliverables, state the embedded visualization inventory, each layer's specialist owner, mini-brief, QA check, and whether it used delegated fresh context, a local fresh specialist pass, or a documented lightweight exception.
- For fictional stories, state the simulated-world contract, seed or regeneration path, data richness layers, and the specialist mini-brief for each embedded visualization.
- For sensitive geopolitical or humanitarian work, state the source ledger, evidence status for each layer, dated map or event states, humane language rules, and static fallback.
- State what should be visible immediately versus revealed on demand.
- For new work, always include a technical design section that covers instance-count assumptions, performance implications, and maintenance tradeoffs.
- For advanced interactive work, also state the renderer ownership boundary, coordinate-frame alignment plan, data-to-visual encoding ledger, interaction state machine, fallback/render-ready plan, and QA checks.
- State which visualization settings are encoded in the URL, which are persisted locally or remotely, and how links, saved views, invalid state, and refresh/back-button behavior work.
- State which configuration, detail, and drill-down areas are collapsed by default or closable, and what remains visible when they are closed.
- If the number of simultaneous instances is unknown, make a reasonable assumption and label it clearly.
- If UX copy is doing analytical work, replace it with better layout, labels, defaults, or interaction design.
- State whether a contextual surface is useful, what source or geometry should define it, and how marks will accommodate it.
- When critiquing visuals, separate semantic problems from rendering or product-integration problems.
- When implementation is requested, route to the narrowest follow-on skill immediately.

## References

- Shared theory:
  - `../../references/foundations/editorial-infographic-system.md`
  - `../../references/foundations/art-directed-interactive-visual-stories.md`
  - `../../references/foundations/meaning-preserving-visual-design-workflow.md`
  - `../../references/foundations/embedded-visualization-self-use.md`
  - `../../references/foundations/fictional-data-story-simulation.md`
  - `../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md`
  - `../../references/foundations/theory-and-principles.md`
  - `../../references/foundations/task-abstraction-and-chart-selection.md`
  - `../../references/foundations/perception-color-and-encoding.md`
  - `../../references/foundations/shareable-state-and-persistence.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/operational-visualization-workspaces.md`
  - `../../references/foundations/domain-contextual-surfaces.md`
  - `../../references/foundations/layout-hierarchy-and-self-explanatory-ux.md`
  - `../../references/foundations/interaction-models-and-progressive-disclosure.md`
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
- Templates:
  - `../../assets/templates/advanced-interactive-visualization-contract.md`
- SVG polish:
  - `../d3-data-visualization/references/svg-polish-and-crispness.md`
- Source index:
  - `../../references/source-index/theory-books-and-papers.md`
  - `../../references/source-index/official-implementation-docs.md`
  - `../../references/source-index/practitioner-guides.md`
- Skill references:
  - `./references/route-by-problem.md`
  - `./references/default-stack-selection.md`
  - `./references/prompt-routing-examples.md`
  - `../gantt-chart-visualization/SKILL.md`
  - `../node-link-and-diagram-layout/SKILL.md`
  - `../uml-and-software-architecture-visualization/SKILL.md`
  - `../scrollytelling-and-parallax-data-visualization/SKILL.md`

## Representative Prompts

- "Choose the best visualization stack for this dataset and audience."
- "Help me visually design this advanced visualization page and generate large-screen and mobile concepts before implementation."
- "Should this be Vega-Lite, D3, Canvas, WebGL, deck.gl, PixiJS, or Three.js?"
- "Use WebGL particles to show flow between nodes, but only if it improves the analysis."
- "Make a parallax scrolling timeline with maps and video."
- "Should this data story be scrollytelling, a stepper, small multiples, or static charts?"
- "How should I integrate this visualization into a React or Next.js app?"
- "Make this dashboard URL-driven so I can share the current filters, range, selection, and drill-down."
- "Persist these visualization settings so users can come back to the same configured view."
- "Design a test plan for this chart, including mocks and visual regression."
- "Critique this dashboard and tell me what to fix first."
- "I need a browser chart that can scale to hundreds of thousands of points."
- "Should this be a table with sparklines or a full chart?"
- "Turn this MS Project, Jira, GitHub Projects, Primavera, Smartsheet, monday.com, Asana, ClickUp, or Azure DevOps schedule into a useful Gantt chart."
- "Should this roadmap be a Gantt chart, milestone timeline, Kanban board, calendar, dependency graph, or resource timeline?"
- "How should I auto-arrange this dependency graph, schema, state machine, or other node-link diagram?"
- "Choose the right UML or UML-like diagram for this system, process, database schema, or software architecture."
- "Read or write PlantUML, Mermaid, Graphviz DOT, D2, Structurizr DSL, DBML, BPMN, or UML XMI."
- "Make this sports or movement visualization use a domain-accurate background, like a pitch, court, track, or floor plan."
- "Turn these visuals into an accessible PDF report and a slide deck."
