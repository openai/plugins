# Quality, Accessibility, Export, and Testing

## Purpose

Use this reference to review UML and UML-like diagrams before they become durable docs, images, reports, slide assets, or interactive product surfaces.

## Semantic Checks

- Diagram type matches the modeling job and audience.
- Scope and abstraction level are explicit.
- Nodes have stable source IDs or traceable source references when generated.
- Relationships are labeled and direction is clear.
- Inferred relationships are marked as inferred.
- Cardinality, guards, events, protocols, ownership, or data names are included when they matter.
- The diagram avoids mixing code, deployment, business process, and database semantics in one undifferentiated view.
- The diagram has a source/date/generator note when it is exported or generated.

## Layout Checks

- Reading order is obvious.
- Main actors, systems, states, or tables are visible without panning in the default view.
- If the default view cannot show the whole model legibly, the viewport still starts on the most important region and the canvas supports obvious scrolling or navigation.
- Edge crossings and long diagonal connectors are controlled.
- Topology diagrams use layered layout, routed edges, or explicit filtering before they become a dense web of overlapping links.
- ERD connectors attach to ports or table sides and travel through gutters; no connector runs beneath table cards or column text.
- Labels do not overlap nodes, edges, ports, or lane headers.
- Selected or searched transition labels never render underneath state nodes.
- Groups, lanes, schemas, packages, or deployment zones are visually subordinate to the content.
- Dense schema and state-machine collections are split into focused single-diagram views with a selector when side-by-side comparison is not the goal.
- The diagram is still readable in grayscale and at intended export size.
- Huge generated diagrams are split, filtered, or summarized.

## Stale-Diagram Risk

- Prefer generated or source-backed diagrams for code, schema, and dependency views.
- Use hand-curated diagrams for concepts, architecture decisions, and explanation.
- Include regeneration commands or source paths for generated assets.
- In code-level diagrams, favor public API or selected collaborators over exhaustive internals.
- For architecture docs, schedule review checkpoints or tie diagrams to architecture decision records.

## Accessibility

- Provide a text summary of the diagram's purpose and key conclusion.
- For complex diagrams, provide an outline or table of nodes and relationships.
- For multi-view architecture explorers, provide a synced navigation tree or structured outline that can reach systems, tables, states, and transitions without pointer panning.
- Do not rely on color alone for relationship type, state, or ownership.
- Ensure contrast for text, strokes, selected states, and annotations.
- Keep essential values and labels visible without hover.
- Hover may preview adjacency, but the same path or selection must be reachable with keyboard focus or click.
- Provide keyboard paths for interactive selection, search, reset, and export.
- Respect reduced-motion settings for animated layout, transitions, and guided reveals.
- For SVG exports, preserve text where possible; for PNG exports, include alt text or a long description beside the asset.

## Export Rules

- Use SVG for documentation, web, and print when vector fidelity and searchable text matter.
- Use PNG when office tools or slide workflows render SVG inconsistently.
- Use PDF for print workflows and reports when the pipeline preserves quality.
- Use HTML when interactivity must travel.
- Export source DSL beside rendered assets where possible.
- For interactive diagrams, export static default, selected, filtered, and key drill-down states when those states carry meaning.
- Include fonts, theme tokens, dimensions, and source notes in the export workflow.

## Testing

- Unit tests: source parsing, model normalization, relationship inference, validation diagnostics, sort/group rules, and DSL generation.
- Component tests: visible labels, empty/error states, details panel payloads, callback behavior, keyboard affordances, and export buttons.
- Visual regression: layout-sensitive states, label overlap, dense graphs, selected/filter states, and exported SVG/PNG snapshots.
- E2E tests: import, search, filter, select, drill-down, edit, undo/redo, save, export, and round-trip where supported.
- Accessibility checks: keyboard-only path, focus order, contrast, reduced motion, and text alternatives.
- Performance checks: large graph parse/layout/render budget, offscreen pausing, worker behavior, and memory cleanup.

## Acceptance Criteria

- A reader can explain the main point without a tutorial paragraph.
- A maintainer can find the source of the diagram.
- A reviewer can tell what is explicit source truth versus generated inference.
- The diagram survives the target export medium.
- Interactive diagrams work without pointer-only or hover-only access to essential information.
- Tests cover semantic correctness and the highest-risk visual or interaction states without freezing every pixel.
