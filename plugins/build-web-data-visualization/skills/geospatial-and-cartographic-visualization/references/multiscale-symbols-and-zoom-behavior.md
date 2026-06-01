# Multiscale Symbols and Zoom Behavior

## What Problem This Solves

This reference helps decide which map layers should visually scale with zoom and which should remain a stable size on screen.

## When to Use It

Use this when an interactive map feels harder to read as users zoom, especially when symbols, labels, or border lines get too large or too small relative to the task.

## Key Takeaways

- Let map-space geometry zoom when the viewer is inspecting the shape itself: coastlines, polygons, linework, raster surfaces, density fields, buffers, and paths that represent real spatial extent.
- Keep locator-style symbols screen-stable when they act as markers, badges, or summaries rather than real-world footprints. City dots, station badges, event pins, cluster badges, and many proportional-symbol overlays usually fit this category in interactive maps.
- Keep labels and callouts screen-stable by default in interactive maps. If they change size, do it in deliberate zoom steps rather than letting them continuously balloon with every zoom gesture.
- Keep boundary, outline, and graticule strokes screen-stable unless line width itself encodes something meaningful. In SVG implementations, `vector-effect="non-scaling-stroke"` is the usual tool for this behavior.
- Use map-scaled symbols only when the symbol is meant to represent physical extent in the world, such as an uncertainty radius, an impact zone, a service area, a measured footprint, or a buffer whose size should be interpreted spatially.
- Use zoom-stepped sizing, filtering, or layer visibility when the map needs a different visual hierarchy at overview versus detail scales. Do not let every layer respond to zoom in the same way.

## Practical Default

- Zoom the geography and the real spatial extents.
- Keep locator symbols, labels, badges, and UI-like annotations stable on screen.
- Keep strokes stable unless changing stroke width is semantically important.
- Add or remove detail by changing visibility, clustering, or label density before changing every symbol's size.

## Common Mistakes

- Letting temperature badges, earthquake markers, or other locator symbols grow so much during zoom that they hide the very geography the user is trying to inspect.
- Scaling border strokes with the map until outlines dominate the view.
- Treating quantity-encoded symbols as if they must also express world-space size, even when they are only comparative markers.
- Using one global zoom rule for all layers instead of separating geometry, symbols, labels, and annotations.

## Adjacent Skills

- `../SKILL.md`
- `./point-overlap-strategies.md`
- `./choropleths-symbols-and-flows.md`

## Source Links

- [ArcGIS Pro: Map reference scales](https://pro.arcgis.com/en/pro-app/latest/help/mapping/properties/map-reference-scales.htm)
- [ArcGIS Pro: Symbol units and size](https://pro.arcgis.com/en/pro-app/latest/help/mapping/layer-properties/units-and-symbol-size.htm)
- [MDN: vector-effect](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/vector-effect)
- [MDN: SVG vector-effect attribute](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/vector-effect)
