# Rendering Architecture

## What Problem This Solves

This reference covers how to structure a Canvas-based visualization so it stays maintainable and interactive.

## When to Use It

Use this when designing a Canvas chart from scratch or migrating from SVG to Canvas.

## Key Takeaways

- Keep scene state separate from drawing code.
- Use multiple layers for static marks, active marks, and interaction overlays.
- Share scales and transforms across Canvas and any DOM or SVG companion layers.
- Size Canvas in two coordinate systems: CSS pixels for layout and backing-store pixels for raster sharpness.
- Use retained geometry even though Canvas itself is immediate-mode.
- Prefer HTML overlays for native controls, rich labels, menus, keyboard focus, and accessible text.
- Redraw from state after every resize, DPR change, zoom transform, or data mutation.
- Treat Canvas accessibility as a companion DOM problem, not as an afterthought.

## Architecture Pattern

Use a retained scene model:

- data records and stable ids
- scales and world-to-screen transforms
- draw commands or mark descriptors
- optional cached `Path2D` objects for moderate-size geometry
- spatial index, picking buffer, or analytic hit-test data
- invalidation state for static, marks, hover, and overlay layers

Canvas should be the renderer, not the source of truth. A hover state, selected ids, dragged id, brush extent, pan/zoom transform, and filtered data should all live outside the drawing context so the chart can redraw deterministically.

## CSS Size, Backing Store, and Browser Zoom

Canvas has layout dimensions and bitmap dimensions. Keep them synchronized:

```ts
type CanvasSize = {
  cssWidth: number;
  cssHeight: number;
  pixelRatio: number;
};

function resizeCanvas(
  canvas: HTMLCanvasElement,
  ctx: CanvasRenderingContext2D,
  cssWidth: number,
  cssHeight: number,
  maxPixelRatio = 3,
): CanvasSize {
  const pixelRatio = Math.max(
    1,
    Math.min(maxPixelRatio, globalThis.devicePixelRatio || 1),
  );
  const width = Math.max(1, Math.round(cssWidth));
  const height = Math.max(1, Math.round(cssHeight));
  const bitmapWidth = Math.max(1, Math.round(width * pixelRatio));
  const bitmapHeight = Math.max(1, Math.round(height * pixelRatio));

  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;

  if (canvas.width !== bitmapWidth || canvas.height !== bitmapHeight) {
    canvas.width = bitmapWidth;
    canvas.height = bitmapHeight;
  }

  ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);

  return { cssWidth: width, cssHeight: height, pixelRatio };
}
```

Use `globalThis.devicePixelRatio` for page zoom and high-DPI screens. Page zoom changes `devicePixelRatio`; pinch zoom is represented by `visualViewport.scale` and should only be multiplied into the backing store when the product intentionally redraws for pinch-zoom sharpness. Always clamp the pixel ratio for very large dashboards because memory grows with `pixelRatio^2`.

Watch size and ratio changes with a combination of `ResizeObserver`, `window.resize`, and a recreated resolution media query:

```ts
let stopWatchingDpr: (() => void) | undefined;

function watchDevicePixelRatio(onChange: () => void) {
  stopWatchingDpr?.();

  const query = matchMedia(`(resolution: ${globalThis.devicePixelRatio}dppx)`);
  query.addEventListener("change", onChange, { once: true });
  stopWatchingDpr = () => query.removeEventListener("change", onChange);
}
```

When the ratio or CSS size changes, resize every Canvas layer, reset each context transform, rebuild cached screen-space geometry if needed, and redraw.

If a parent stage is CSS-transformed with rotation, skew, or non-uniform scaling, `clientX - rect.left` is not enough. Keep the CSS transform matrix or use `DOMMatrix` to invert the full screen-to-stage transform before hit testing.

## Layering

Use a relatively positioned stage with stacked canvases and optional HTML/SVG overlays:

- background Canvas: slow-changing contextual surfaces, grid bands, heatmap tiles, static map geometry
- marks Canvas: primary data marks
- interaction Canvas: hover, selection, brush handles, drag preview
- HTML/SVG overlay: axes, labels, tooltips, popovers, editable controls, focusable affordances

Set passive overlay labels to `pointer-events: none`. For controls that need clicks or focus, set `pointer-events: auto`, ensure they sit above the Canvas, and decide whether they should stop propagation or route interactions back into the Canvas controller.

## HTML Overlay Quirks

- Derive overlay positions from the same transform as Canvas marks; never duplicate scale math in separate components.
- Keep the stage as the common coordinate parent so `translate(x, y)` positions align with Canvas CSS pixels.
- Reposition overlays after pan, zoom, scroll, resize, DPR changes, data updates, and font loading.
- Avoid overlaying thousands of DOM nodes; use overlays for selected, focused, edited, or annotated marks rather than every mark.
- When an overlay intercepts pointer events, maintain a clear ownership rule so dragging does not unexpectedly switch between Canvas and HTML.
- Preserve accessibility in the overlay: real buttons, links, inputs, table cells, `aria-live` updates, and keyboard focus usually belong in HTML.

## Accessibility and Focus

Canvas pixels do not create a semantic tree. For meaningful data marks, provide one of these companion structures:

- an adjacent data table or selected-detail panel for the data behind the view
- focusable HTML controls or anchors for selected, edited, or navigable marks
- fallback content inside the `<canvas>` element for basic unavailable-canvas messaging
- `aria-live` status updates for hover, brush, and selection changes that matter
- keyboard paths for selection, pan, zoom, brushing, and reset actions

Use `CanvasRenderingContext2D.drawFocusIfNeeded()` only when a Canvas-drawn affordance is backed by a real focused element. For most visualization work, HTML focus rings and overlays are easier to maintain and test than drawing focus entirely in Canvas.

## Common Mistakes

- Treating immediate-mode drawing as a reason to skip scene modeling.
- Pushing every responsibility, including labels and accessibility, into Canvas.
- Setting only `canvas.width` and `canvas.height` without matching CSS size, or setting only CSS size and accepting a blurry backing store.
- Calling `ctx.scale()` repeatedly after every resize instead of resetting with `ctx.setTransform()`.
- Letting Canvas and HTML overlays use separate transforms that drift after zooming or resizing.
- Creating one Canvas per row or mark without calculating aggregate backing-store memory.
- Drawing interactive controls in Canvas without a matching keyboard and screen-reader model.

## Adjacent Skills

- `../SKILL.md`
- `../../typescript-data-visualization-engineering/SKILL.md`
- `../../accessibility-and-inclusive-visualization/SKILL.md`

## Source Links

- [MDN: Window.devicePixelRatio](https://developer.mozilla.org/en-US/docs/Web/API/Window/devicePixelRatio)
- [MDN: VisualViewport.scale](https://developer.mozilla.org/en-US/docs/Web/API/VisualViewport/scale)
- [MDN: Optimizing canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas)
- [MDN: CanvasRenderingContext2D.drawFocusIfNeeded](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawFocusIfNeeded)
- [D3 API](https://d3js.org/api)
