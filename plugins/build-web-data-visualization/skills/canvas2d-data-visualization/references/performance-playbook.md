# Performance Playbook

## What Problem This Solves

This reference gives the first optimizations to reach for in Canvas-heavy charts.

## When to Use It

Use this when performance complaints start or when planning a dense view that must feel fluid.

## Key Takeaways

- Reduce work before micro-optimizing.
- Batch draw calls, precompute style groups, cull off-screen geometry, and decimate where display resolution cannot show every sample.
- Move expensive work off the main thread when the architecture supports it.
- Canvas is a strong default for frequently updating visualizations and pages with many repeated chart instances.
- Backing-store memory grows with CSS size, pixel ratio, layer count, and instance count.
- Layer static, frequently changing, and interaction-only graphics so a hover or drag does not force a full redraw.
- Readback-heavy canvases, especially picking buffers, need a different context strategy from draw-only canvases.

## First Decision: Reduce Work

Before tuning draw calls, reduce what must be drawn:

- aggregate, bin, tile, or decimate data that cannot be resolved at the current zoom level
- cull marks outside the viewport
- draw only dirty layers or dirty regions
- cache static surfaces and repeating glyphs in an offscreen canvas
- virtualize rows, panes, or chart instances that are outside the viewport
- reduce pointer-move work with throttling to `requestAnimationFrame`

Canvas can draw more marks than SVG, but it is not exempt from data reduction. A million points drawn on every pointer move is still the wrong interaction model.

## Frequent Updates

Prefer Canvas when data changes many times per second, when charts animate continuously, or when a dashboard streams values into many traces. Use:

- a fixed render loop driven by `requestAnimationFrame`
- immutable or versioned data buffers so draw code can cheaply decide what changed
- ring buffers for streaming traces
- precomputed screen-space coordinates when scales and viewport are stable
- a separate hover/selection layer so interaction does not invalidate the data layer
- `OffscreenCanvas` or workers when data preparation or rendering competes with input responsiveness

For live dashboards, define a degradation policy before implementation: drop frames, reduce sample rate, aggregate older samples, pause offscreen charts, or switch to summary marks under load.

## Many Instances on One Page

Canvas is especially useful for sparkline tables, KPI grids, small multiples, dense timelines, and monitoring boards. The risk is backing-store multiplication:

```txt
bytes = cssWidth * cssHeight * pixelRatio^2 * 4 * layerCount * instanceCount
```

Example: 400 charts at 160 x 40 CSS pixels with DPR 2 and one layer cost about 39 MB before extra buffers, labels, framework overhead, or browser allocation details. Add three layers and the cost triples.

Use one of these patterns:

- a single shared Canvas covering a virtualized table or grid
- pooled Canvas elements reused by visible rows
- static sparkline bitmaps generated into an offscreen cache
- one Canvas per card only when instance count stays small and resize behavior is simple
- HTML text for values and labels, Canvas only for the tiny trace

## Draw-Call Practices

- Sort or group marks by fill, stroke, alpha, composite mode, and line width to reduce context state changes.
- Prefer one polyline for a trace over many separate line segments.
- Use typed arrays for geometry-heavy views and avoid allocating objects in the render loop.
- Avoid expensive text measurement in every frame; cache label metrics or move labels to HTML/SVG.
- Avoid shadows and filters on dense marks; pre-render glow or halo effects if needed.
- Use integer-aligned coordinates for image blits and crisp one-pixel rules when appropriate.
- Disable alpha with `getContext("2d", { alpha: false })` when the canvas is opaque.
- Use `{ willReadFrequently: true }` for contexts that repeatedly call `getImageData()`, not for normal draw-only canvases.
- Consider `{ desynchronized: true }` only for latency-sensitive views where the browser tradeoff is acceptable.

## Redraw and Invalidation

- Redraw the full scene when the viewport transform, scale domain, or data filter changes.
- Redraw only the interaction layer for hover, selection outline, brush preview, and drag preview.
- Rebuild picking buffers when mark positions, z-order, hit geometry, or viewport transforms change.
- Rebuild cached `Path2D` geometry when the path is screen-space and the viewport changes.
- Use `clearRect()` for straightforward full-layer clears; benchmark alternatives only after profiling.

## OffscreenCanvas and Workers

Use `OffscreenCanvas` when expensive rendering or pre-rendering can happen away from the main DOM thread. It helps with:

- static tile generation
- expensive heatmap or density rasterization
- sprite or glyph atlas generation
- frame production for a visible bitmap-renderer canvas
- rendering in a worker when browser support and application architecture allow it

Keep pointer handling, DOM overlays, focus, and layout measurement on the main thread. Worker rendering still needs a clear message protocol for size, pixel ratio, data versions, and invalidation.

`OffscreenCanvasRenderingContext2D` is similar to regular Canvas2D, but it does not support UI-specific features such as `drawFocusIfNeeded()`. Keep accessibility and focus proxies in the main DOM layer.

## Common Mistakes

- Chasing micro-optimizations before reducing data or redraw scope.
- Ignoring device pixel ratio and text measurement costs.
- Assuming one Canvas per chart is always cheaper than SVG without calculating total memory.
- Recomputing scales, paths, spatial indexes, and text metrics inside every animation frame.
- Redrawing labels, axes, and static backgrounds during hover.
- Letting every visible sparkline own its own animation loop.
- Setting `willReadFrequently` on every Canvas instead of only readback-heavy buffers.

## Adjacent Skills

- `../SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`

## Source Links

- [MDN: Optimizing canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas)
- [MDN: OffscreenCanvas](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas)
- [MDN: OffscreenCanvasRenderingContext2D](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvasRenderingContext2D)
- [MDN: HTMLCanvasElement.getContext](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/getContext)
- [MDN: Window.devicePixelRatio](https://developer.mozilla.org/en-US/docs/Web/API/Window/devicePixelRatio)
- [deck.gl docs](https://deck.gl/docs)
