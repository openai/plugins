# Route by Problem

## What Problem This Solves

This reference helps the umbrella skill decide which specialist skill should own the work.

## When to Use It

Use this at the start of broad requests or whenever a user mixes chart choice, implementation, testing, accessibility, and export concerns.

## Key Takeaways

- Route chart choice, critique, and narrative issues to strategy first.
- Route mobile-first responsive concerns, paired large-screen/mobile concept sets, touch/pinch/keyboard behavior, spotty connections, and device capability audits through `../../../references/foundations/mobile-first-responsive-visualization.md` before treating them as CSS-only cleanup.
- Route Gantt charts, project schedules, roadmap task spans, milestones, dependencies, predecessors, critical path, baselines, WBS, resource plans, capacity timelines, and project-management imports or exports to the Gantt chart skill before choosing a renderer.
- Route MS Project, Primavera P6, Jira Advanced Roadmaps, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, Azure DevOps, CSV, TSV, XLSX, or JSON schedule ingestion through the Gantt skill's API and export-format guidance before mapping fields.
- Route graph-layout and auto-arrangement questions for connected nodes to the node-link and diagram layout skill before debating Graphviz, ELK, Dagre, React Flow, Cytoscape.js, D3, Canvas, or WebGL.
- Route UML, UML-like diagrams, sequence/class/activity/state/use-case/component/deployment diagrams, ERDs, database schema diagrams, C4, BPMN, swimlanes, flowcharts, software architecture diagrams, PlantUML, Mermaid, Graphviz DOT, D2, Structurizr, DBML, XMI/UMLDI, and interactive diagram editors through the UML and software architecture visualization skill before choosing a renderer.
- Route parallax scrolling, scrollytelling, scroll-driven timelines, sticky graphics, moviescrollers, Scrollama, ScrollTrigger, ScrollTimeline, and view timeline prompts to the scrollytelling and parallax skill before choosing a renderer.
- Route layout hierarchy, self-explanatory labeling, and interaction-contract questions to strategy first.
- Route standard tabular chart implementation to declarative grammars first.
- Route dense flat rendering, frequent redraws, Canvas-specific hit testing, and repeated microcharts such as sparkline tables to Canvas when Canvas2D can satisfy the frame budget and interaction model.
- Route true 3D, WebGL-accelerated 2D, raw WebGL, deck.gl, luma.gl, PixiJS, Sigma.js, particle effects, animated flows, and GPU-scale shader work to the Three.js/WebGL skill.
- Route high-volume geospatial flows, trips, point clouds, arcs, and GPU map overlays to geospatial first, then the Three.js/WebGL skill when renderer details or custom particles matter.
- Route map fly-throughs, pan/zoom story maps, and route-centric scrollytelling to geospatial first for map reasoning, then scrollytelling for scene pacing and browser behavior.
- Route operational screens to dashboards, with Canvas2D or WebGL as renderer choices only after the monitoring task and degradation model are clear.
- Route maps, uncertainty, accessibility, testing, and document export to their dedicated skills instead of burying them as side notes.
- Route slippy or product-map requests to geospatial even when the user leads with React, D3, or dashboard language.
- Route fictional, invented, illustrative, or synthetic editorial stories through `../../../references/foundations/fictional-data-story-simulation.md` before art direction or implementation.
- Route embedded visualizations inside reports, stories, parallax, editorials, visual articles, and decks through `../../../references/foundations/embedded-visualization-self-use.md`: inventory the layers, assign specialist owners, write mini-briefs, and use authorized delegation or local fresh specialist passes for substantial layers.

## Common Mistakes

- Sending a chart-choice problem straight into library-specific implementation.
- Solving a layout or interaction problem with more copy instead of fixing the default view.
- Treating accessibility, testing, or export as post-processing.
- Treating task trackers, roadmap snapshots, resource calendars, and true schedule-engine exports as interchangeable.
- Inferring planned Gantt bars from issue created/closed timestamps when the user did not ask for actual lifecycle analysis.
- Treating UML, C4, ERD, BPMN, flow, and dependency diagrams as interchangeable boxes-and-lines output instead of choosing notation by modeling job and audience.
- Treating all connected-node diagrams as the same layout problem instead of distinguishing trees, DAGs, undirected networks, port-constrained block diagrams, and nearly planar graphs.
- Sending an interactive diagram request straight to React Flow, Cytoscape.js, Sprotty, JointJS, GoJS, D3, or Graphviz before defining the semantic model and source format.
- Sending a state machine, ERD, or dependency graph straight to force layout just because it is a graph.
- Routing a sparkline wall or dense interactive canvas to SVG just because the prototype has only a few marks.
- Routing a WebGL request straight to Three.js when deck.gl, PixiJS, Sigma.js, Plotly WebGL traces, ECharts GL, MapLibre, CesiumJS, or Canvas2D better match the data shape.
- Adding particle animation before deciding what the particles represent and what static or reduced-motion fallback preserves the claim.
- Treating decorative parallax as a visualization type instead of checking whether staged scroll reveals evidence.
- Sending scrollytelling straight to React, D3, or GSAP before defining the scene contract and reduced-motion/static fallback.
- Trying to make fictional stories feel rich with prose or imagery before generating enough simulated data dimensions to support charts, maps, interaction, and visual density.
- Naming a specialist owner for an embedded visual without actually using the relevant specialist guidance, mini-brief, QA check, or fresh-pass status.
- Letting desktop DOM order define mobile reading order, especially when controls or prose appear before the main visualization.

## Adjacent Skills

- `../SKILL.md`
- `../../gantt-chart-visualization/SKILL.md`
- `../../node-link-and-diagram-layout/SKILL.md`
- `../../uml-and-software-architecture-visualization/SKILL.md`
- `../../visualization-strategy-and-critique/SKILL.md`
- `../../scrollytelling-and-parallax-data-visualization/SKILL.md`
- `../../grammar-of-graphics-and-declarative-visualization/SKILL.md`
- `../../threejs-data-visualization/SKILL.md`
- `../../testing-data-visualizations/SKILL.md`
- `../../../references/foundations/mobile-first-responsive-visualization.md`

## Source Links

- [Visualization Analysis and Design](https://mitpressbookstore.mit.edu/book/9781466508910)
- [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1/About-UML)
- [PlantUML](https://plantuml.com/)
- [Mermaid syntax reference](https://mermaid.js.org/intro/syntax-reference)
- [From Data to Viz](https://www.data-to-viz.com/)
- [Mike Bostock: How To Scroll](https://bost.ocks.org/mike/scroll/)
- [Scrollama](https://github.com/russellsamora/scrollama)
- [MDN: WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API)
- [deck.gl Introduction](https://deck.gl/docs)
- [Microsoft Project XML Data Interchange Schema](https://learn.microsoft.com/en-us/office-project/xml-data-interchange/project-xml-data-interchange-schema-reference)
- [Jira issue linking model](https://developer.atlassian.com/cloud/jira/platform/issue-linking-model/)
- [GitHub Projects data export](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-your-project/exporting-your-projects-data)
