# Slippy Map and Product Stack Selection

## What Problem This Solves

This reference helps choose among product-map stacks when the real requirement is an interactive map surface with pan, zoom, markers, tiles, routes, or place context rather than a purely analytical thematic map.

## When to Use It

Use this when a request sounds like a product map, locator map, route map, store finder, field-operations map, or map-heavy app surface. Use `./adaptive-basemaps-and-layer-stacks.md` first when the real decision is whether the map needs roads, cities, terrain, imagery, boundaries, live operations, or a neutral substrate.

## Key Takeaways

- Leaflet is a strong default for lightweight slippy maps, markers, GeoJSON overlays, layer controls, and familiar map controls with a broad plugin ecosystem.
- MapLibre GL JS is strong for open-source vector-tile maps, data-driven styling, label-aware layer ordering, hillshade, heatmaps, tilt or rotation, and richer modern slippy-map experiences.
- Mapbox GL JS is strong when the product benefits from Mapbox-hosted basemaps, Studio styling, polished 3D basemap features, or commercial Mapbox platform integration.
- Google Maps is strong when the product needs managed road basemaps, Places, routing, geocoding, traffic context, or tighter Google Maps Platform integration.
- OpenLayers is strong for GIS-heavy web maps, projections, WMS/WMTS/OGC services, vector and raster layers, and advanced layer control.
- ArcGIS Maps SDK is strong for hosted GIS services, FeatureLayer workflows, renderers, clustering, binning, heatmaps, editing, and operational maps.
- Azure Maps and HERE Maps are strong for enterprise routing, traffic, fleet, logistics, geocoding, and provider-specific location services.
- CesiumJS is strong for 3D globe, terrain, imagery layering, temporal scenes, and 3D Tiles.
- deck.gl can layer on top of MapLibre, Google Maps, Mapbox, or ArcGIS when product maps also need high-volume analytical overlays.
- D3 geo is usually the wrong primary framework for a general slippy map, but it remains excellent for custom projections and thematic cartography.

## Common Mistakes

- Forcing D3 geo to own pan, zoom, tiles, markers, and controls for a standard product map.
- Choosing Google Maps for a thematic analytical map that mainly needs custom cartography and annotation.
- Choosing Leaflet for extremely heavy vector-tile or GPU-driven scenes that fit MapLibre or deck.gl better.
- Choosing a library before deciding whether the viewer needs roads, cities, terrain, imagery, boundaries, or a quiet neutral basemap.

## Adjacent Skills

- `../SKILL.md`
- `./adaptive-basemaps-and-layer-stacks.md`
- `./deckgl-d3-geo-stack-selection.md`
- `../../react-and-nextjs-data-visualization/SKILL.md`

## Source Links

- [Leaflet Documentation](https://leafletjs.com/reference.html)
- [Leaflet Choropleth Example](https://leafletjs.com/examples/choropleth/)
- [MapLibre GL JS](https://maplibre.org/projects/gl-js/)
- [Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
- [OpenLayers](https://openlayers.org/)
- [ArcGIS Maps SDK for JavaScript](https://developers.arcgis.com/javascript/)
- [Azure Maps Documentation](https://learn.microsoft.com/en-us/azure/azure-maps/)
- [HERE Maps API for JavaScript](https://docs.here.com/maps-api-for-js/docs/introduction-maps-api-for-javascript)
- [CesiumJS](https://cesium.com/platform/cesiumjs/)
- [deck.gl docs](https://deck.gl/docs)
