# Interactive Diagram Patterns

## Purpose

Use this reference before designing UML-like explorers, architecture maps, flow builders, dependency graphs, schema browsers, and diagram editors. Interactive diagrams are product surfaces, not just pictures with pan and zoom.

## Interaction Modes

- Read-only explorer: pan, zoom, search, filter, selection, details panel, permalink, export.
- Guided explanation: curated steps, highlights, annotations, drill-down, static fallback.
- Review surface: compare versions, flag issues, link source files, comments, export snapshots.
- Editable diagram: create/delete nodes and edges, drag, resize, connect ports, edit labels, undo/redo, validation, save, import/export.
- Model-driven editor: diagram edits change a semantic model; backend validation and source round-tripping are first-class.

## Core Controls

- Pan and zoom with reset, fit-to-view, and keyboard alternatives.
- Search by label, kind, source ID, table, class, service, package, or technology.
- Filter by type, owner, domain, layer, status, source, criticality, or relationship kind.
- Selection opens details without hiding the main diagram.
- Multi-select supports comparison, group operations, and impact analysis when useful.
- Use compact dropdown, segmented, or tab controls for dense view switching; avoid showing every schema, state machine, or subgraph at once unless comparison is the task.
- Expand/collapse groups, packages, lanes, schemas, bounded contexts, and deployment zones.
- Drill-down preserves breadcrumb context and a route back to the parent view.
- Minimap helps only when the graph is larger than the viewport; skip it for small diagrams.
- Layout recalculation should be explicit when it may move user-curated positions.

## Editing Patterns

- Separate semantic edits from cosmetic layout edits.
- Validate before save, and show diagnostics near the affected node or edge.
- Support undo/redo for create, delete, move, label edit, connection edit, group edit, and layout changes.
- Treat ports/handles as typed connection points, not generic dots, when relationship validity matters.
- For state machines, validate unreachable states, missing initial/final states, duplicate transitions, and invalid event guards.
- For ERDs, validate missing keys, orphan foreign keys, circular dependencies where relevant, and cardinality.
- For architecture diagrams, validate mixed abstraction levels, unlabeled relationships, missing external systems, and unresolved dependencies.

## Layout and Navigation

- Use stable layout for review and documentation; avoid surprise movement after minor edits.
- Offer auto-layout for generated diagrams, but keep manual positions when users curate an explanatory view.
- Preserve collapsed group bounds and lane order across sessions.
- Use orthogonal routing for architecture, deployment, schema, and flow diagrams when it improves traceability.
- Use edge bundling or filtering before relying on dense hairball layouts.
- Show relationship direction clearly and keep edge labels close to the edge segment they describe.
- For architecture topology, prefer layered ranks by abstraction or deployment zone, then order nodes within each rank by dependency barycenter or stable source order; increase canvas size before accepting edge crossings.
- Do not solve dense topology by shrinking text until it is unreadable. Prefer a larger intrinsic canvas inside a scroll container, then keep the default viewport calm and legible.
- For dense architecture zones, favor separators, headings, and whitespace over large floating rounded region cards that compete with the actual nodes.
- Keep non-selected topology edges quiet by default, use hover for a medium-emphasis preview, and use selection for the strongest path highlight. Clear selection when users click empty canvas or surrounding chrome.
- For ERD/schema views, route foreign keys through gutters outside table bodies, attach to table-side ports, and reserve enough horizontal space that connectors do not run below or through column lists.
- Schema auto-layout must use cumulative measured heights, not per-item nominal heights, or stacked tables and connectors will drift into overlap.
- For multiple schemas or state machines, provide a single focused diagram with a selector. Show summaries or outlines in the side rail instead of rendering all diagrams in a grid.
- For state machines, treat transition labels as a focus layer rather than a permanent wallpaper. Show all edges, but render label chips for hover, search, or selection above the node layer so text never disappears behind states.
- Pair the visual diagram with a synced navigation tree or outline. Clicking the tree should move to the right view and item, and clicking the diagram should update the tree highlight.

## Density and Panel Design

- Treat side panels as rails: search, filters, outline, and selection details should be concise and mostly unboxed.
- Avoid cards inside cards in diagram workspaces. Use separators, whitespace, muted labels, and compact rows for grouping.
- Prefer checkbox dropdowns or popovers for multi-select filters such as layer, owner, relationship kind, criticality, and source.
- Give each filter its own full-width row when the rail is narrow; do not compress several multi-select controls into one wrapped strip.
- Reserve visible boxes for the actual diagram artifacts: nodes, tables, states, modals, or repeated item rows that need a hit target.

## Collaboration and Round-Tripping

- Store semantic model data separately from renderer-specific coordinates.
- Include version, generator, source files, schema version, and source IDs.
- When importing text DSLs, retain the original source or format loss warnings.
- When exporting text DSLs, disclose unsupported renderer-only properties.
- For collaborative editing, define ownership of conflicts: source file wins, diagram model wins, or manual resolution.
- Use comments or review markers as metadata, not as diagram node labels.

## Accessibility Patterns

- Provide a structured text summary of nodes, edges, groups, and selected paths.
- Make search, selection, details, export, and reset keyboard-accessible.
- Do not require precise dragging for core understanding.
- Offer table or outline views for dense graphs.
- Keep selected/focused states visible without color alone.
- Provide reduced-motion behavior for animated layout changes and guided reveals.

## Testing Patterns

- Test semantic reducers and validation separately from rendering.
- Test keyboard navigation, selection, filtering, search, drill-down, and export.
- Use deterministic layout fixtures for screenshot tests.
- Capture empty, loading, error, dense, selected, filtered, collapsed, and export states.
- Include import/export round-trip tests when source-backed editing is promised.
