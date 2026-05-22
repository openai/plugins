# TypeScript Web Rendering

## Purpose

Use this reference when implementing UML or UML-like diagrams in TypeScript, JavaScript, React, Next.js, documentation sites, or browser products.

## Static and Docs Rendering

- Mermaid: best default for Markdown-friendly docs, quick sequence/class/state/ER/flow/C4/architecture diagrams, and web embeds. Use Mermaid API or CLI when diagrams must render inside a site or build pipeline.
- PlantUML: use when formal UML coverage is stronger than Mermaid or existing docs are PlantUML-based. Render via CLI, local server, or Kroki. In browser-only settings, verify rendering support and security boundaries.
- Graphviz/WASM or Viz.js: use for DOT dependency graphs, package maps, and generated layouts where local Graphviz is unavailable.
- D2: use for polished declarative software diagrams, UML classes, architecture diagrams, tables, and themed documentation diagrams.
- Structurizr DSL: use when C4 views should come from one architecture model. Embed generated views or integrate Structurizr tooling rather than recreating the model in ad hoc chart code.
- Kroki: use as a unified rendering layer when the deployment can host or call a trusted diagram rendering service.

## Interactive Renderer Selection

- React Flow: use for editable or semi-editable node-edge product UIs, custom React node components, handles/ports, flow builders, state machines, pipelines, and application dependency explorers.
- Cytoscape.js: use for larger graphs, graph analysis, compound nodes, network exploration, layout plugins, shortest paths, centrality, impact analysis, and graph-theory APIs.
- Sprotty: use for model-driven diagram tools, language-server-backed diagrams, Eclipse/Theia/VS Code style integration, remote model semantics, and SVG rendering with command/action architecture.
- JointJS: use for interactive SVG diagramming, visual no-code/low-code surfaces, UML/ERD/FSA-like shapes, custom elements, and graph/paper architecture.
- GoJS: use for full-featured commercial diagramming applications, editors, statecharts, org charts, industrial diagrams, and complex interaction behavior.
- D3/SVG: use for custom explanatory diagrams when the visual design, annotation, or layout is too specific for a diagram framework.
- Canvas/WebGL: use only when graph scale or animation makes SVG impractical; pair with accessible HTML overlays or summaries.

## Layout Engines

- ELK: use for layered, orthogonal, compound, port-aware, and complex block diagrams. Best when edge routing and nested structure matter.
- Dagre: use for simpler directed acyclic graph layout in the browser. Good for flow charts, dependency chains, and React Flow auto-layout.
- Graphviz DOT: use for server-side or build-time static layouts.
- Force layouts: use for exploratory networks only when spatial clusters reveal structure; avoid for process order or architecture hierarchy.
- Manual layout: allow when humans need curated explanatory views, but store coordinates as layout hints separate from the semantic model.
- Bespoke layered layout: acceptable for small custom explorers when dependencies are fixed, but still implement ranks, non-overlap spacing, deterministic ordering, and routed edge lanes instead of plotting raw coordinates.
- ERD layout: place root/parent tables and dependent tables in separate columns or ranks, route foreign keys through gutters, and draw connectors above/between table boxes rather than underneath table contents.
- State-machine layout: show one state machine at a time unless the task is comparison; use a selector or tabs when multiple machines exist.
- If labels become unreadable at responsive width, keep the renderer at a fixed intrinsic SVG or canvas size and put it inside a scrollable viewport rather than scaling everything down.
- For UML-like explorers with only a few top-level modes, use a lightweight segmented control for the mode itself, but use a dropdown or command-style picker for long schema or state-machine lists so controls do not scroll off-screen.

## Type Contracts

Define renderer-neutral types before choosing a widget:

- `DiagramModel`: id, title, type, scope, source, generatedAt, nodes, edges, groups, lanes, annotations, diagnostics.
- `DiagramNode`: id, label, kind, stereotype, compartment data, parent/group, ports, sourceRef, metadata, layoutHint.
- `DiagramEdge`: id, source, target, kind, label, direction, cardinality, protocol/data, sourceRef, metadata, layoutHint.
- `DiagramState`: selected IDs, focused ID, expanded groups, filters, search query, viewport, layout mode, edit mode.

Use adapter functions to transform the renderer-neutral model into React Flow nodes/edges, Cytoscape elements, Sprotty model elements, JointJS cells, GoJS node/link data, Mermaid source, PlantUML source, DOT, or D2.

## Browser Integration Rules

- Keep parsing, validation, layout, and rendering separable.
- Use web workers for large graph layout or expensive parsing.
- Preserve a source view or export source when diagrams are generated from text DSLs.
- Lazy-load heavy renderers on routes that need them.
- Reserve dimensions before rendering to avoid layout shift.
- Provide deterministic layout seeds or fixture coordinates for tests.
- Avoid making the renderer state the only source of truth; keep semantic model state in app-owned data.
- Model hover selection separately from committed selection so exploratory previews are less visually dominant than clicked impact paths.
- Keep filter state outside the renderer and pass derived visible/highlight sets into SVG, Canvas, or diagram-library adapters.
- Keep navigation state outside the renderer too: a synced tree or outline should be able to open the correct view, schema, state machine, or selected entity without reverse-engineering DOM geometry.
- For state machines and ERDs, render connector labels in a late overlay layer or HTML annotation layer so selected labels always sit above nodes and tables.

## Source Anchors

- Mermaid: https://mermaid.js.org/intro/syntax-reference
- PlantUML: https://plantuml.com/
- Graphviz DOT: https://graphviz.org/doc/info/lang.html
- D2: https://d2lang.com/
- Structurizr DSL: https://docs.structurizr.com/dsl
- Kroki: https://docs.kroki.io/kroki/
- React Flow: https://reactflow.dev/learn/concepts/terms-and-definitions
- Cytoscape.js: https://js.cytoscape.org/
- Sprotty: https://sprotty.org/docs/introduction/
- JointJS: https://docs.jointjs.com/
- GoJS: https://go.js.org/
- Eclipse ELK: https://eclipse.dev/elk/documentation.html
- Dagre: https://github.com/dagrejs/dagre
