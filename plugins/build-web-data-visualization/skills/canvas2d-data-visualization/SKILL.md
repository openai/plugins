---
name: canvas2d-data-visualization
description: Render data visualizations with Canvas2D. Use when the visualization needs high mark counts, fast redraws, immediate-mode rendering, custom hit testing, or a hybrid Canvas plus SVG or HTML architecture.
---

# Canvas2D Data Visualization

## Overview

Use this skill when raster rendering is the practical choice. Canvas2D is strong for dense scatterplots, sparkline walls, heatmaps, streaming traces, tiled timelines, draggable analytical workspaces, and other views where SVG or DOM overhead becomes the limiting factor.

Default assumption: keep a retained scene model in application state even if the actual drawing is immediate-mode Canvas.
Any visualization or interaction that can be built in SVG can usually be built in Canvas2D too, but the retained geometry, hit testing, focus model, and accessibility layer become the application's responsibility. Choose Canvas for performance or rendering control; keep SVG/HTML when native DOM semantics, text, accessibility, or exportability matter more than redraw speed.
Canvas2D can also be simpler or faster than WebGL for flat immediate-mode workloads because it avoids shader setup, buffer uploads, GPU context pressure, and custom WebGL lifecycle code. Move from Canvas2D to WebGL when GPU picking, shader effects, particle count, custom blending, smooth animation, true 3D, or high-volume geospatial layers justify that extra complexity.

For browser-facing Canvas work, use `../../references/foundations/mobile-first-responsive-visualization.md` so backing-store size, hit testing, touch gestures, keyboard overlays, spotty connection states, and mobile performance budgets are part of the design contract.

## Choose Canvas2D When

- the chart needs tens of thousands to millions of marks
- panning or zooming must feel fluid
- the view updates continuously
- the page needs many repeated microcharts such as sparklines in tables or KPI grids
- many chart instances are visible at once and SVG node count would dominate layout, style, and memory cost
- marks need custom clickable, hoverable, brushable, or draggable behavior over dense geometry
- you can tolerate raster output or provide separate export paths
- the chart benefits from layered drawing control, including static contextual backgrounds behind dense marks

Prefer SVG, HTML, or a declarative grammar when the chart is small, static, text-heavy, annotation-heavy, primarily accessibility-driven, or needs straightforward copy/paste/editable-vector export.
Prefer WebGL or the Three.js/WebGL skill when the chart needs GPU-scale particles, custom shaders, instancing, very large graph or point layers, 3D, or map overlays that Canvas2D would struggle to animate or pick interactively.

## Core Practices

1. Scale the backing store for browser zoom and high-DPI output:
   - set CSS `style.width` and `style.height` in CSS pixels
   - set the `canvas.width` and `canvas.height` attributes to `cssSize * pixelRatio`
   - use `globalThis.devicePixelRatio || 1` as the page-zoom-aware ratio
   - consider `visualViewport.scale` only when deliberately redrawing for pinch-zoom crispness
   - reset the context with `ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0)` so drawing code can stay in CSS pixels
2. Keep world-to-screen transforms explicit.
3. Use layered canvases for:
   - static background, including any field, court, floor plan, schematic, or other contextual surface
   - primary marks
   - highlight or hover state
   - interaction overlays
4. Avoid full redraws when partial invalidation is possible.
5. Build deterministic hit testing:
   - spatial index
   - color picking buffer
   - nearest-point search
   - `Path2D` geometry replay against candidate subsets with `isPointInPath()` and `isPointInStroke()`
   - analytic tests for simple shapes such as points, line segments, rectangles, intervals, and bands
6. Assess how many Canvas instances may be visible at once, because backing-store size and redraw cost multiply quickly at dashboard scale.
7. Treat pointer interaction as a first-class subsystem:
   - normalize `PointerEvent.clientX/clientY` through `getBoundingClientRect()`
   - invert the current pan/zoom transform before mapping to data coordinates
   - use `setPointerCapture()` for drags so movement continues outside the canvas
   - clean up drag state on `pointerup`, `pointercancel`, and `lostpointercapture`
   - use `touch-action` deliberately for touch and pen surfaces
   - provide non-drag alternatives and enlarged invisible hit regions for small marks on coarse pointers
   - keep keyboard and screen-reader affordances in HTML when Canvas marks are semantically important
8. For mobile, define whether one-finger drag pans the chart or scrolls the page, whether pinch zoom is chart-owned or browser-owned, and how reset or explicit zoom controls work.

## Hybrid Architecture

- Canvas for bulk marks
- SVG or HTML for axes, labels, legends, rich tooltips, menus, form controls, keyboard focus, and annotations
- shared scales and transforms across both layers

This is usually better than forcing all responsibilities into Canvas. Use absolutely positioned HTML overlays for elements that need native layout, selection, input, focus rings, links, or accessible semantics; keep them synchronized by deriving every overlay position from the same world-to-screen transform used by the Canvas renderer.
For sparklines and other microcharts, nearby row labels, headers, and inline values usually work better than a shared detached legend.

## Performance Defaults

- batch draw calls
- precompute style groups
- use typed arrays for geometry-heavy views
- cull off-screen marks
- decimate or aggregate when the viewport cannot resolve individual points
- use `OffscreenCanvas` and workers when main-thread contention is significant
- keep text and annotations in HTML or SVG unless Canvas text is genuinely required
- prefer one shared Canvas layer or virtualization for large sparkline tables instead of hundreds of independent backing stores when memory becomes visible
- compute backing-store memory as `width * height * pixelRatio^2 * 4 * layerCount * instanceCount`
- cap pixel ratio or quality on mobile when memory, battery, or thermal pressure would outweigh crispness
- keep stale/offline/partial-data overlays in HTML or a light Canvas layer instead of blanking the chart during network recovery
- use `getContext("2d", { willReadFrequently: true })` only for canvases that repeatedly call `getImageData()`, such as color-picking buffers

## Output Expectations

- Explain why Canvas is better than SVG for the workload.
- If SVG could also work, name the interaction, accessibility, and maintenance costs Canvas introduces and why the performance tradeoff is still worth it.
- Keep labels and accessibility strategy explicit.
- For sparkline-heavy views, explain how the surrounding table or card context carries meaning without forcing legend lookup.
- For clickable or draggable Canvas views, specify the hit-testing strategy and how pointer coordinates map to data coordinates.
- For mobile Canvas views, specify touch target policy, pointer capture, drag alternatives, pinch/zoom ownership, visual viewport or keyboard behavior, DPR cap, and low-bandwidth/stale-data behavior when relevant.
- For color-picking buffers, specify id encoding, alpha and antialiasing assumptions, `getImageData()` readback cost, and when the buffer invalidates.
- For zoomable or resizable Canvas views, specify how CSS size, backing-store attributes, `devicePixelRatio`, and redraw invalidation are handled.
- For HTML overlays, specify which layer owns pointer events, focus, tooltip positioning, and accessibility semantics.
- If a contextual surface is part of the design, document its source geometry and keep overlays, labels, and hit testing aligned to the same coordinate transform.
- Preserve a path to exported assets, usually via PNG plus optional vector companion views.
- For new work, include a technical design section covering simultaneous instance count, memory and redraw cost per instance, and maintenance tradeoffs of the hybrid architecture.

## References

- Shared theory:
  - `../../references/foundations/perception-color-and-encoding.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/domain-contextual-surfaces.md`
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
- Skill references:
  - `./references/rendering-architecture.md`
  - `./references/high-density-interaction.md`
  - `./references/performance-playbook.md`
  - `./references/sparklines-and-microcharts.md`

## Representative Prompts

- "Render a million-point scatterplot in the browser."
- "Build a fast Canvas timeline with brushing and zoom."
- "Move this SVG heatmap to Canvas without losing labels."
- "Render sparklines for every row in a data table."
- "Design hit testing for a dense Canvas chart."
- "Explain how to split this visualization across multiple Canvas layers."
- "Make these Canvas marks clickable and draggable."
- "Fix this blurry Canvas chart when the browser is zoomed."
