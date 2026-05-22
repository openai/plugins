---
name: d3-data-visualization
description: Build custom data visualizations with D3. Use when the user needs SVG or DOM-based charts, rich annotation, domain-native contextual backgrounds, data joins, custom scales or interactions, scroll-driven SVG scene states, or precise control over browser visualization behavior.
---

# D3 Data Visualization

## Overview

Use this skill for custom browser visualizations where SVG or DOM semantics matter and a declarative grammar no longer fits cleanly. D3 is strongest when the chart needs bespoke scales, marks, layouts, transitions, zooming, brushing, annotations, or vector export.

Default assumption: use D3 for scales, layouts, geometry, labels, annotation layers, and behavior. Do not turn D3 into the entire application architecture if a framework already owns the surrounding UI.

## Choose D3 When

- the chart needs custom marks or nonstandard layouts
- SVG quality matters for export, print, or accessibility
- annotation and labeling are part of the design, not an afterthought
- the visualization needs custom vector background geometry such as a field, court, track, floor plan, schematic, or other meaningful contextual surface
- an editorial story needs data-bound generated cutouts, illustrated substrates, scrollytelling/parallax states, or animated annotation reveals in SVG
- the mark count is moderate enough for DOM or SVG
- the interaction model needs zoom, brush, drag, or coordinated views
- a UML-like, dependency, architecture, state, or flow diagram needs bespoke SVG annotation or product-specific composition after `../uml-and-software-architecture-visualization/SKILL.md` has defined the diagram semantics
- a declarative grammar would become harder to read than the resulting D3 code

## Avoid D3-First DOM Rendering When

- mark counts are so large that DOM throughput becomes the bottleneck
- animation is continuous and frame budgets are tight
- the task would be faster to solve with Canvas2D or WebGL

## Working Pattern

1. Build a clean data model first.
2. Separate:
   - parsing and normalization
   - scale construction
   - derived geometry
   - rendering
   - interaction state
3. Prefer stable keys in joins.
4. Use D3 for math and behavior, not for hiding weak state management.
5. Assess how many D3 instances may coexist on the page so DOM, layout, and event costs are evaluated at dashboard scale.
6. If using a contextual surface, keep source units and render scales explicit, draw the background as a separate layer, and adapt mark placement or layout forces to the domain geometry.
7. For art-directed stories, keep generated image, substrate, data-mark, label, and annotation layers separate so each can be reviewed and exported.
8. Keep annotations and interaction overlays explicit.
9. For SVG output, apply `./references/svg-polish-and-crispness.md` before calling the chart finished. Explicitly set font sizes, tick padding, gridline strokes, data stroke widths, icon sizes, label alignment, and zoom-stable stroke behavior.
10. For browser-facing work, use `../../references/foundations/mobile-first-responsive-visualization.md` so the D3 layout is recomputed for large-screen and mobile states rather than scaled down from one desktop SVG.

## Editorial Defaults

- Build an explicit label layer. Direct end labels, inline keys, or panel labels should be considered before a detached legend.
- Build an explicit annotation layer. Callouts should attach to data points, ranges, thresholds, or domain geometry rather than floating as decoration.
- Keep gridlines, axes, and reference marks quiet. Most ink should be data, labels, or annotation.
- Default SVG chart polish: 10-12 px axis ticks, 11-13.5 px direct labels, 0.5-1 px non-data strokes, 1.5-2.25 px normal data lines, 2.5-3 px focus lines, short 4-6 px ticks, and no heavy chart border unless it carries meaning.
- Use D3 axes as geometry generators, then style them. Prefer `.tickSizeOuter(0)`, 6-8 px tick padding, quiet gridlines, removed domains when redundant, and fewer ticks before rotated or tiny labels.
- Use `shape-rendering: crispEdges` for straight axes, gridlines, and rectangular cells; do not apply it globally to curves, symbols, circles, or diagonal marks.
- Use `vector-effect: non-scaling-stroke` for zoomable outlines, axes, annotation connectors, map borders, and icons that should keep screen-stable stroke weight.
- Use custom layout only when the story needs it; do not copy a publication's composition or visual identity.
- For narrow widths, provide either a simplified mark layout, small-multiple stack, or numbered annotation key below the chart.
- On mobile, make tap/focus the inspection path, enlarge hit areas beyond visible marks, provide drag alternatives, define pinch or zoom ownership, and keep the main chart visible when filters or settings open.
- Favor inspectable SVG for editorial charts that need export, accessibility, and precise labels. Move dense mark fields to Canvas only when the DOM count justifies it.
- For scrollytelling or parallax, use `../scrollytelling-and-parallax-data-visualization/SKILL.md` for the scroll narrative, then let D3 own scales, derived geometry, data joins, labels, and SVG transitions. Keep each scene valid as a still.
- For generated imagery, use D3/SVG for labels, anchors, masks, clipping, and data overlays rather than baking numbers into images.
- For motion, use transitions to reveal sequence, direction, accumulation, comparison, or mechanism. Respect reduced-motion with final-state rendering.
- For 3D-looking SVG, avoid perspective distortion unless it represents a real multiaxis surface; label axes and provide a flat fallback when needed.

## Core D3 Building Blocks

- `d3-array` for grouping, extent, ticks, and summaries
- `d3-scale` for position, color, and size mappings
- `d3-axis` for readable axes
- `d3-shape` for lines, areas, arcs, and symbol generation
- `d3-selection` and `d3-transition` for DOM behavior
- `d3-brush`, `d3-zoom`, and `d3-drag` for direct manipulation
- `d3-force`, `d3-hierarchy`, `d3-contour`, and other layouts only when their data structure fits

## Integration Rules

- In React or another UI framework, prefer framework-owned structure and D3-owned geometry, scales, and behaviors.
- For highly custom charts, a small imperative D3 island is fine if the boundary is clear.
- Keep responsive behavior tied to container measurements, not magic constants.
- Recompute labels, tick counts, annotation placement, collision rules, and plot height for mobile portrait and optional landscape sizes; do not only resize the outer `viewBox`.
- Prefer SVG for labels and annotations even in hybrid systems.
- Keep contextual background layers non-interactive unless they are part of selection, zoom, or hit testing.
- Move to Canvas or WebGL when DOM count or continuous redraw becomes the limiting factor.

## Output Expectations

- Explain why D3 is the right rendering layer.
- Keep chart structure semantic and inspectable.
- Provide export paths for SVG or PNG when needed.
- Pair interaction with obvious annotation and reset controls.
- For mobile, state the touch target policy, hover replacement, drag/pinch ownership, and how the on-screen keyboard or settings panels return the user to the chart.
- When drawing a contextual surface, state the source geometry and how data marks are positioned, constrained, or biased by it.
- For image-supported editorial work, state which assets are generated, which layers remain data-bound, and how labels anchor to the substrate.
- For animation, state the verb, scene states, duration budget, and reduced-motion fallback.
- For new work, include a technical design section covering simultaneous instance count, DOM and interaction cost, and maintenance tradeoffs versus declarative or Canvas-based alternatives.

## References

- Shared theory:
  - `../../references/foundations/editorial-infographic-system.md`
  - `../../references/foundations/art-directed-interactive-visual-stories.md`
  - `../../references/foundations/perception-color-and-encoding.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/domain-contextual-surfaces.md`
  - `../../references/foundations/storytelling-annotation-and-critique.md`
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
- Skill references:
  - `./references/d3-module-map.md`
  - `./references/d3-architecture-patterns.md`
  - `./references/d3-interaction-and-annotation.md`
  - `./references/d3-pitfalls-and-scale-limits.md`
  - `./references/svg-polish-and-crispness.md`
  - `../uml-and-software-architecture-visualization/SKILL.md`
  - `../scrollytelling-and-parallax-data-visualization/SKILL.md`

## Representative Prompts

- "Build a D3 slopegraph with direct labels."
- "Add zoom and brushing to this scatterplot."
- "Create a publication-quality SVG chart from this dataset."
- "Draw a domain-accurate soccer pitch behind a player network and bias node positions by role."
- "Refactor this D3 chart so React owns layout and D3 owns math."
- "Animate this D3 chart through scrollytelling scene states."
- "Tell me when this D3 chart should move to Canvas."
