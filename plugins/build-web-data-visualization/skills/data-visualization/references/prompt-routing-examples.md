# Prompt Routing Examples

## What Problem This Solves

This reference gives concrete examples of how broad user requests should be routed.

## When to Use It

Use this when a prompt spans multiple domains or feels underspecified.

## Key Takeaways

- "What chart should I use?" routes to strategy.
- "Build a Gantt chart", "show a project schedule", "show critical path", "import MS Project XML", or "read a Jira Advanced Roadmaps CSV" routes to the Gantt chart skill first.
- "Should this be a Gantt chart, Kanban board, calendar, milestone timeline, dependency graph, or resource timeline?" routes to the Gantt chart skill and strategy.
- "How do I auto-arrange these connected boxes and lines?" routes to the node-link and diagram layout skill first.
- "What layout algorithm should I use for a network diagram, state machine, database schema, or decision tree?" routes to the node-link and diagram layout skill first, then to UML, TypeScript, React, D3, or testing as needed.
- "Create a sequence diagram", "read this XMI", "make an ERD from my database", "design a C4 architecture diagram", "write PlantUML", "render Mermaid", or "build an interactive dependency diagram" routes to the UML and software architecture visualization skill first.
- "Should this checkout workflow be a sequence diagram, activity diagram, swimlane, state machine, BPMN diagram, or flowchart?" routes to the UML skill and strategy.
- "How should this dashboard or chart be laid out so it is obvious without extra copy?" routes to strategy, then to dashboards or implementation as needed.
- "Generate a desktop and mobile design for this visualization" routes to the meaning-preserving visual design workflow and mobile-first responsive reference before implementation.
- "Make this chart work well on phones" routes to mobile-first responsive guidance, then strategy, implementation, and testing as needed.
- "Should this use AR, camera, vibration, motion, geolocation, or notifications?" routes to mobile-first responsive guidance first, then WebGL/geospatial/dashboard/accessibility depending on the capability.
- "Handle spotty mobile connections for this live chart" routes to dashboard streaming guidance, mobile-first responsive guidance, and testing.
- "Write a Vega-Lite or Plot spec" routes to grammar.
- "Make this performant at 500k points" routes to Canvas or WebGL depending on update rate, interaction load, and whether GPU picking, shader effects, or particles are needed.
- "Render sparklines for every row in this table" routes to Canvas, with strategy guidance for scale choices if needed.
- "Make these dense Canvas marks clickable or draggable" routes to Canvas interaction guidance.
- "Make a WebGL scatterplot with lasso selection and smooth zoom" routes to the Three.js/WebGL skill, then TypeScript or React integration if needed.
- "Should this be raw WebGL, Three.js, deck.gl, PixiJS, or Canvas?" routes to the Three.js/WebGL library-selection reference after the analytical task is clarified.
- "Show data flowing between nodes with particles" routes to strategy first if the analytical goal is unclear, then to the Three.js/WebGL particle and flow guidance.
- "Call out important marks with sparkles, fire, glow, or pulses" routes to strategy and accessibility first, then to the Three.js/WebGL particle guidance only if the effect has a clear data meaning and fallback.
- "Make a parallax scrolling timeline with maps and video" routes to scrollytelling first, then geospatial, React, D3, video, or WebGL depending on the visual layer.
- "Use Scrollama for a data story" routes to scrollytelling first, then React or TypeScript integration if the implementation surface matters.
- "Should this be scrollytelling or a stepper?" routes to strategy and scrollytelling.
- "Make this scroll-driven visualization accessible and performant" routes to scrollytelling, then accessibility and testing.
- "Build a slippy map with markers, layers, and familiar map controls" routes to geospatial first, then to React or TypeScript if needed.
- "Animate people, vehicles, or packets moving between cities" routes to geospatial first, then WebGL particle/flow guidance for motion semantics and reduced-motion/static fallback.
- "How should I handle overlapping points on this map?" routes to geospatial first.
- "What should zoom with this map and what should stay screen-stable?" routes to geospatial first.
- "Turn this into a report or deck" routes to reports and automation.
- "Make this accessible" routes to accessibility even if the chart is otherwise library-specific.
- "Read GitHub Projects GraphQL fields, Smartsheet predecessors, monday.com timeline columns, Asana JSON, ClickUp task dates, or Azure DevOps iterations for a schedule view" routes to Gantt API/export ingestion before TypeScript or renderer work.

## Common Mistakes

- Treating the first named library as the real problem.
- Sending a Gantt prompt straight to D3, Canvas, React, or a generic charting library before deciding whether the source is a true schedule, task tracker, roadmap snapshot, resource calendar, or static export.
- Sending UML-like diagram prompts straight to a renderer before choosing formal UML, C4, ERD, BPMN, flowchart, swimlane, state machine, dependency graph, or another notation.
- Sending auto-layout questions straight to a renderer without first classifying the graph as a tree, layered digraph, undirected network, port-constrained block diagram, or something else.
- Ignoring document and export constraints during routing.
- Treating particles or WebGL as a chart type instead of a renderer/effect choice that must serve a concrete analytical job.
- Treating parallax as an automatic upgrade instead of asking whether scroll-driven motion carries evidence.
- Sending all WebGL prompts to Three.js when deck.gl, PixiJS, Sigma.js, Plotly WebGL traces, ECharts GL, MapLibre, CesiumJS, Canvas2D, or raw WebGL may be a better fit.
- Treating mobile as CSS-only resizing after the concept, reading path, touch model, and stale-data behavior are already fixed.

## Adjacent Skills

- `../SKILL.md`

## Source Links

- [From Data to Viz](https://www.data-to-viz.com/)
- [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1/About-UML)
- [PlantUML](https://plantuml.com/)
- [Mermaid syntax reference](https://mermaid.js.org/intro/syntax-reference)
- [FT Visual Vocabulary](https://github.com/ft-interactive/visual-vocabulary)
- [Mike Bostock: How To Scroll](https://bost.ocks.org/mike/scroll/)
- [MDN: WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API)
- [deck.gl Introduction](https://deck.gl/docs)
- [Microsoft Project XML Data Interchange Schema](https://learn.microsoft.com/en-us/office-project/xml-data-interchange/project-xml-data-interchange-schema-reference)
- [Oracle P6 import/export formats](https://docs.oracle.com/cd/F25600_01/English/admin/p6_pro_importing_exporting/import_export_file_formats.htm)
- [Smartsheet predecessor schema](https://developers.smartsheet.com/api/smartsheet/openapi/schemas/predecessor)
