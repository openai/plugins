# Operational Visualization Workspaces

## Purpose

Use this reference for visualization surfaces where people repeatedly inspect, filter, navigate, and act on dense analytical state: architecture explorers, live dashboards, monitoring consoles, schema viewers, state-machine inspectors, network maps, map operations tools, and similar product workspaces.

Default assumption: the main visualization or evidence viewport is the work surface. Controls, outlines, inspectors, and status readouts should support it without forcing the user to dig through generic cards or scroll past settings before seeing the evidence.

## Workspace Shell

- Use a large-screen tri-pane shell when the task has many entities: left outline or controls, central visualization viewport, right inspector or analysis rail.
- Keep the central viewport dominant and intrinsically sized. For dense diagrams, maps, timelines, and canvases, prefer scrollable pan/zoom surfaces over shrinking text below legibility.
- Use one compact top command/status bar for mode, counts, live state, and global actions. Avoid a marketing-style hero on an operational surface.
- Keep secondary controls compact, collapsible, or panelized. Active filters, selections, caveats, source status, and reset paths stay visible outside closed panels.
- Provide a meaningful default selection or focused region when the full workspace would otherwise open as an undirected maze.
- Let empty-canvas clicks clear selection only when it is clear that a drag did not occur.

## Mobile Shell

- Mobile portrait needs a useful entry point, not a vertically stacked desktop rail.
- Use a compact command bar for mode, search, filters, outline, and details. Put deeper controls in drawers, bottom sheets, or side panels.
- Keep the visualization visible on first load or make it immediately reachable before long filters, prose, or inspectors.
- Keep a lightweight detail or inspector area available without replacing the visualization permanently.
- Close mobile panels after navigation or applied settings when the user's likely next step is reading the affected visualization.
- Offer mobile landscape when a wide graph, timeline, Gantt chart, schema, field/court, map, or 3D view materially improves tracing.

## Navigation And State

- Sync outline trees, search results, selected marks, and inspectors. Selecting in one surface should update the others.
- Use stable entity IDs, not visible labels, for selection, navigation, URL state, and test fixtures.
- Auto-scroll navigation outlines to the selected entity without stealing focus from active inputs.
- Separate hover preview from committed selection. Hover can emphasize neighborhoods; selection should drive inspector state, deep links, and stable highlights.
- Treat view mode, selected entity, filters, search, zoom or camera target, and active panel as candidates for URL state when users need shareable workspaces.
- Keep transient hover, drag-in-progress, and animation frame out of URL and persistence.

## Interaction Model

- Define pan, zoom, wheel, pinch, drag, keyboard, reset, escape, and clear-selection behavior before implementation.
- Use explicit `touch-action`, scroll containment, and alternate controls when the visualization captures gestures.
- Provide zoom controls and reset controls for dense viewports; do not rely on precision trackpads or hidden gestures only.
- Give small marks and diagram nodes enlarged hit regions or step-through/search alternatives on touch devices.
- For live or operational data, prefer stale-but-visible states over blank reconnects. Show live, stale, partial, offline, delayed, and last-updated status.

## Visual System

- Operational styling should be dense but calm: compact typography, restrained borders, stable dimensions, and strong contrast for selected or critical evidence.
- Use semantic color ledgers. Distinguish topology layer, relationship kind, selected state, hover preview, alert severity, stale state, disabled state, and decorative substrate.
- Avoid nested cards and repeated floating containers. Use rails, bands, dividers, tables, outlines, and viewport chrome instead.
- Keep labels and legends in editable text layers. If a generated or raster substrate is used, it must leave label-safe regions and never bake in factual values.
- Make the workspace readable as a screenshot: selected entity, active filters, source/caveat, and main claim or status should survive without hover.

## QA Checklist

- Large-screen shell keeps outline/controls, visualization, and inspector aligned without nested-card clutter.
- Mobile portrait opens with the main visualization visible or immediately reachable before long controls.
- Mobile command bar opens and closes outline, filters, and details without losing selection or scroll state.
- Search, filters, selected entity, outline, viewport highlight, and inspector stay synchronized.
- Dragging the viewport does not accidentally clear selection; deliberate empty-surface click can clear it.
- Pan/zoom/reset, touch, keyboard, and escape paths work and do not fight page scroll.
- Dense labels remain legible through scroll, pan, zoom, focus, or landscape fallback instead of being scaled away.
- URL/share state restores mode, filters, selected entity, and meaningful viewport or camera state.
- Live/stale/offline/partial states preserve last-known-good evidence and visible source status.
- Desktop, mobile portrait, and optional landscape screenshots preserve the same analytical state.
