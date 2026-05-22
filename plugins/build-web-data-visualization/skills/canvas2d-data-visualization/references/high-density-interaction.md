# High-Density Interaction

## What Problem This Solves

This reference covers interaction strategies for dense Canvas charts where naive hit testing is too expensive.

## When to Use It

Use this when a chart has many marks and still needs hover, click, selection, brushing, lassoing, dragging, direct manipulation, or editable graphical handles.

## Key Takeaways

- Spatial indexes, nearest-point search, and color-picking buffers are practical interaction strategies.
- The chart should degrade gracefully under density rather than pretending every point is equally readable.
- HTML or SVG overlays are often the best place for labels and tooltips.
- `Path2D` plus `CanvasRenderingContext2D.isPointInPath()` and `isPointInStroke()` is useful for moderate candidate sets and irregular geometry.
- Pointer events and pointer capture are the default input model for dragging in Canvas spaces.
- Canvas interactions need a retained scene model because the browser cannot tell you which drawn mark was clicked.
- Color-picking buffers are powerful, but `getImageData()` readback and antialiasing details must be designed deliberately.

## Coordinate Normalization

Convert pointer events to the coordinate space used by the renderer before hit testing:

```ts
type Point = { x: number; y: number };

function eventToCanvasCssPoint(
  event: PointerEvent,
  canvas: HTMLCanvasElement,
): Point {
  const rect = canvas.getBoundingClientRect();
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
}
```

If drawing code uses CSS-pixel coordinates after `ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0)`, the point above is ready for screen-space hit testing. If drawing code uses raw backing-store pixels, multiply by `canvas.width / rect.width` and `canvas.height / rect.height`.

For panned or zoomed charts, maintain an explicit `DOMMatrix` or equivalent transform. Hit testing usually needs both:

- screen-space coordinates for `Path2D`, label, and handle tests
- data/world coordinates from the inverse transform for selections, brush extents, and dragging data objects

If the stage itself is transformed with CSS beyond simple translation, invert that CSS transform too. `getBoundingClientRect()` gives the bounding box, not a full inverse transform for rotated or skewed coordinate systems.

## Hit-Testing Strategies

Pick the least expensive strategy that preserves the user's intent:

- Analytic tests: circles, rectangles, bands, line segments, bars, and handles. This is fastest and easiest to test.
- Nearest-point search: use a spatial index and a pixel-radius threshold for dense scatterplots and traces.
- Spatial index plus geometry replay: query candidates first, then replay each candidate's `Path2D` with `isPointInPath()` or `isPointInStroke()`.
- Color picking: render stable mark ids into an offscreen picking buffer, then read the pixel under the pointer. This is useful for many irregular or overlapping shapes, but it needs careful redraw synchronization and color/id mapping.
- Interaction proxy geometry: use larger invisible hit areas than the visible marks, especially for thin lines, small points, mobile touch, and draggable handles.

Do not replay every shape on every pointer move for high-density views. First reduce candidates by screen bounds, tile, quadtree, interval index, row index, or color picking.

## Path2D Hit Testing

Use `Path2D` when a mark has complex or reusable geometry:

```ts
type HitCandidate = {
  id: string;
  path: Path2D;
  lineWidth?: number;
  fillRule?: CanvasFillRule;
};

function hitTestPath(
  ctx: CanvasRenderingContext2D,
  point: Point,
  candidates: HitCandidate[],
): string | undefined {
  ctx.save();
  try {
    for (let index = candidates.length - 1; index >= 0; index -= 1) {
      const candidate = candidates[index];
      ctx.lineWidth = Math.max(candidate.lineWidth ?? 1, 8);

      if (
        ctx.isPointInPath(candidate.path, point.x, point.y, candidate.fillRule) ||
        ctx.isPointInStroke(candidate.path, point.x, point.y)
      ) {
        return candidate.id;
      }
    }
  } finally {
    ctx.restore();
  }

  return undefined;
}
```

Set stroke style state that affects the tested stroke, especially `lineWidth`, line caps, joins, and dashes. Use `save()` and `restore()` or a dedicated hit-test context so inflated hit widths do not leak into visible drawing. Iterate in visual z-order from topmost to backmost when marks overlap.

For transformed paths, keep drawing and hit testing in the same coordinate convention. If draw commands are written in CSS pixels with the DPR transform active, use CSS-pixel pointer coordinates and keep that transform active during the test. If paths are stored in world or data coordinates, either apply the same world-to-screen transform before calling `isPointInPath()`/`isPointInStroke()` or invert the pointer point into the path's local coordinate system first.

## Color-Picking Buffers

Color picking is useful when geometry is too complex or numerous for path replay:

- draw each pickable mark into an offscreen Canvas using a unique opaque RGB id color
- disable antialias-sensitive ambiguity where possible by using filled proxy geometry or inflated hit regions
- keep a `color -> mark id` map and reserve transparent or black for "no hit"
- call `getImageData(x, y, 1, 1)` only after normalizing pointer coordinates into the picking buffer's pixel space
- create the picking context with `{ willReadFrequently: true }` if readback is genuinely frequent
- invalidate and redraw the picking buffer when data, viewport transform, z-order, hit geometry, or pixel ratio changes

Do not use visual colors for picking ids. Gradients, alpha, shadows, filters, antialiasing, color spaces, and compositing can produce colors that do not map cleanly back to a mark id.

## Clickable Marks

- Keep a stable id for every interactive mark.
- On `pointermove`, hit test a candidate subset, update hover state, cursor, and any hover layer.
- On `pointerdown`, hit test again and decide whether the gesture is click, drag, brush, lasso, pan, or range selection.
- On `click` or `pointerup`, confirm the pointer did not move beyond the click threshold before committing selection.
- Expose selected or focused state through HTML text, tables, controls, or an accessible side panel when the mark represents meaningful data.

## Draggable Graphics

Use pointer capture so drags continue even after the pointer leaves the Canvas:

```ts
let drag:
  | { id: string; start: Point; origin: Point; pointerId: number }
  | undefined;

canvas.addEventListener("pointerdown", (event) => {
  const point = eventToCanvasCssPoint(event, canvas);
  const id = hitTest(point);

  if (!id) return;

  canvas.setPointerCapture(event.pointerId);
  drag = {
    id,
    start: point,
    origin: getMarkPosition(id),
    pointerId: event.pointerId,
  };
});

canvas.addEventListener("pointermove", (event) => {
  if (!drag || event.pointerId !== drag.pointerId) return;

  const point = eventToCanvasCssPoint(event, canvas);
  updateMarkPosition(drag.id, {
    x: drag.origin.x + point.x - drag.start.x,
    y: drag.origin.y + point.y - drag.start.y,
  });
  invalidateInteractionLayer();
});

canvas.addEventListener("pointerup", (event) => {
  if (!drag || event.pointerId !== drag.pointerId) return;

  if (canvas.hasPointerCapture(event.pointerId)) {
    canvas.releasePointerCapture(event.pointerId);
  }
  commitDrag(drag.id);
  drag = undefined;
});

canvas.addEventListener("pointercancel", () => {
  drag = undefined;
});

canvas.addEventListener("lostpointercapture", () => {
  drag = undefined;
});
```

Set `touch-action: none` on the Canvas when direct manipulation should suppress browser panning and zooming. Use narrower values such as `pan-x` or `pan-y` when the chart should still allow native scrolling in one direction.

For drawing-like interactions where pointer precision matters, `PointerEvent.getCoalescedEvents()` can recover intermediate positions from a coalesced `pointermove`. Treat it as an enhancement because support is not universal.

## Brushing, Lassoing, and Editing

- Draw transient brush or lasso geometry on an interaction layer, not the marks layer.
- Convert the final screen-space gesture to data/world space before filtering data.
- Snap handles to data or scale constraints after pointer movement, not during every raw event, unless the product needs grid snapping.
- Keep resize handles and draggable control points larger than their visible glyphs.
- Use keyboard-editable HTML controls for exact values when drag precision is insufficient.

## HTML and SVG Overlays

Use overlays when an interaction wants browser-native behavior:

- tooltips with links, formatted text, copyable values, or focusable controls
- context menus, popovers, dropdowns, and editable fields
- selected-mark detail panels anchored to Canvas coordinates
- accessible tables or lists that mirror selected Canvas data
- brush or drag handles that need visible focus rings and keyboard support

Overlay positioning should be derived from the same transform as Canvas drawing. Passive labels can use `pointer-events: none`; interactive overlays need explicit ownership for pointer events so Canvas drags and overlay clicks do not compete.

## Common Mistakes

- Replaying all geometry on every pointer move.
- Acting as if a million-point plot can support the same interaction as a 500-point SVG chart.
- Using `event.offsetX`/`offsetY` blindly when CSS transforms, borders, nested layers, or HiDPI scaling are involved.
- Forgetting to inflate hit areas for strokes, small points, and touch targets.
- Starting a drag without pointer capture, causing the gesture to break when the pointer leaves the Canvas.
- Forgetting `pointercancel` and `lostpointercapture`, leaving stale drag state after interruption.
- Letting hover redraw the whole scene when a small interaction layer would be enough.
- Using visual paint colors as color-picking ids.

## Adjacent Skills

- `../SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`

## Source Links

- [MDN: CanvasRenderingContext2D.isPointInPath](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/isPointInPath)
- [MDN: CanvasRenderingContext2D.isPointInStroke](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/isPointInStroke)
- [MDN: Path2D](https://developer.mozilla.org/en-US/docs/Web/API/Path2D)
- [MDN: Pointer events](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events)
- [MDN: Element.setPointerCapture](https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture)
- [MDN: PointerEvent.getCoalescedEvents](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent/getCoalescedEvents)
- [MDN: HTMLCanvasElement.getContext](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/getContext)
- [deck.gl docs](https://deck.gl/docs)
