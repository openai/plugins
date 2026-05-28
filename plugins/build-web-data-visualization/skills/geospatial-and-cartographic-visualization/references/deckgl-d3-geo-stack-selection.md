# deck.gl and D3 Geo Stack Selection

## What Problem This Solves

This reference helps decide between D3 geo and GPU-oriented analytical geospatial stacks.

## When to Use It

Use this when implementing geospatial visualization on the web.

## Key Takeaways

- D3 geo is strong for SVG-centric maps, projections, thematic cartography, and annotation-rich analytical composition.
- deck.gl is strong for high-volume points, layers, aggregation, animation, trips, arcs, paths, point clouds, particle-like flows, and GPU-heavy geospatial interaction.
- The right choice depends on scale, interaction model, basemap expectations, and annotation needs.
- MapLibre or Mapbox should own vector-tile product maps; deck.gl should own analytical GPU overlays when its layer model fits.
- CesiumJS should own globe, terrain, 3D Tiles, and time-dynamic WGS84 scenes before forcing Three.js into geospatial precision work.
- Particle flow on maps should be treated as motion evidence or focus guidance, not decoration. Static arrows, width, color, and labels should preserve the claim.

## Common Mistakes

- Using deck.gl when the real problem is a small annotated thematic map.
- Using SVG maps for millions of points.
- Treating either option as a general-purpose product-map framework when Leaflet, MapLibre, or Google Maps is the better fit.
- Using animated trips or particles for sensitive human movement without caveats, static fallback, and humane restraint.

## Adjacent Skills

- `../SKILL.md`
- `../../d3-data-visualization/SKILL.md`
- `./slippy-map-and-product-stack-selection.md`

## Source Links

- [D3 geo projections](https://d3js.org/d3-geo/projection)
- [deck.gl docs](https://deck.gl/docs)
- [deck.gl TripsLayer](https://deck.gl/docs/api-reference/geo-layers/trips-layer)
- [deck.gl ArcLayer](https://deck.gl/docs/api-reference/layers/arc-layer)
- [deck.gl Aggregation Layers](https://deck.gl/docs/api-reference/aggregation-layers/overview)
- [MapLibre GL JS](https://maplibre.org/projects/gl-js/)
- [CesiumJS](https://cesium.com/platform/cesiumjs/)
