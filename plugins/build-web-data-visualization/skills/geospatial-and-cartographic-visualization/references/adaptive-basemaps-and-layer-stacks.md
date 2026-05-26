# Adaptive Basemaps and Layer Stacks

## What Problem This Solves

This reference helps choose the map substrate, contextual layers, thematic layers, and implementation stack from the user's actual map purpose. A good geo visualization should not start with "Leaflet or Google Maps?" It should start with what the viewer needs to reason about: roads, terrain, water, boundaries, imagery, density, movement, or exact locations.

Default behavior: infer the likely map purpose from the request, recommend a substrate and layer stack, state assumptions, and ask only the missing high-impact questions. Do not run a blanket map questionnaire when the request already gives enough intent.

## When to Use It

Use this whenever a geospatial request needs an interactive map, basemap choice, map-library choice, or layered contextual surface. It is especially useful when the user asks for roads, cities, routes, weather, hiking, wildfire, flood, terrain, satellite imagery, dense GPS points, operational maps, or map-library recommendations.

## Key Takeaways

- Choose the basemap or substrate before choosing the library.
- Treat roads, cities, terrain, rivers, elevation, imagery, parcels, and administrative boundaries as analytical context, not decoration.
- Use the prompt to infer the likely substrate, then ask only for missing context that would change the map design.
- Name the contextual layers separately from the thematic data layers.
- Pick the implementation stack after the substrate, data scale, interaction model, provider dependencies, and layer needs are clear.

## Infer Then Ask

1. Infer the user's map purpose from domain words, verbs, and decisions the viewer must make.
2. Recommend the best substrate and contextual layers.
3. Recommend thematic layers and encodings.
4. Ask only the questions whose answers would materially change the substrate, layers, or stack.
5. Then choose the implementation stack.

When the prompt is underspecified, ask one to three focused questions. Prefer questions like "Should viewers see route context and road hierarchy?" over broad questions like "What kind of map do you want?"

## Purpose to Substrate Defaults

- Driving, routing, delivery, traffic, road safety, emergency access, or weather-for-driving:
  - Use a road and city basemap.
  - Include route corridors, road hierarchy, city labels, traffic, incidents, closures, weather hazards, and time or direction where relevant.
  - Prefer Google Maps, HERE Maps, Azure Maps, ArcGIS, Mapbox GL JS, or MapLibre depending on routing, traffic, provider, and styling needs.
- Hiking, outdoor planning, wildfire, flood, landslide, environmental risk, watershed, or field work:
  - Use a topographic or terrain substrate.
  - Include elevation, hillshade or contours, rivers, lakes, land cover, trails, roads or access routes, boundaries, perimeters, and incident layers.
  - Prefer MapLibre, Mapbox GL JS, ArcGIS, OpenLayers, CesiumJS, or deck.gl depending on terrain, raster, service, and density needs.
- Regional comparison by county, state, country, district, or neighborhood:
  - Use a neutral administrative boundary map only if geography, adjacency, or local recognition matters.
  - Consider a sorted table, dot plot, bar chart, or small multiples when the main task is ranking or precise comparison.
  - Use choropleths only for rates, ratios, shares, or normalized values, not raw counts.
- Satellite, remote sensing, land use, agriculture, construction, damage, or change detection:
  - Use imagery or raster evidence as the substrate when visual inspection matters.
  - Keep analytical overlays transparent and label-safe so the imagery remains readable.
  - Prefer MapLibre, Mapbox GL JS, OpenLayers, ArcGIS, Azure Maps, Google Maps, or CesiumJS depending on imagery source, tiling, and 3D needs.
- Conflict, occupation, displacement, civilian harm, disaster response, or humanitarian need:
  - Use a subdued boundary, terrain, imagery, or city-label substrate according to what the evidence requires.
  - Include dated map states, source hierarchy, evidence status, and caveats near the thematic layer.
  - Prefer D3 geo for static or editorial map frames, MapLibre/OpenLayers/ArcGIS for layered evidence and imagery, or deck.gl only when volume or animation genuinely aids analysis.
- Dense points, events, sensors, vehicles, GPS traces, or check-ins:
  - Use a quiet neutral basemap unless terrain, roads, or boundaries are part of the reasoning.
  - Choose clustering, binning, heatmaps, hex layers, or sampled traces before drawing raw markers.
  - Prefer deck.gl for high-volume GPU overlays, ArcGIS for feature reduction and hosted layers, or MapLibre/Mapbox/OpenLayers for vector-tile and cluster workflows.
- Globe, 3D terrain, volumetric context, 3D Tiles, buildings, or line-of-sight:
  - Use 3D only when depth, terrain, occlusion, or globe-scale context changes the analysis.
  - Prefer CesiumJS for globe, terrain, imagery, and 3D Tiles; use deck.gl or Three.js only when custom GPU layers or bespoke 3D rendering are justified.

## Questions to Ask When Missing

Ask these only when the answer would change the recommendation:

- Should viewers see roads, cities, transit, or route context?
- Should viewers see terrain, mountains, rivers, elevation, slope, or land cover?
- Is satellite or aerial imagery evidence needed, or would it distract from the data?
- Are administrative boundaries, neighborhoods, parcels, service areas, or custom regions important?
- Is the map for navigation, situational awareness, comparison, storytelling, or open-ended exploration?
- Do users need exact individual locations, aggregate density, or both?
- Is this static or editorial, interactive exploratory, operational, or real-time?

## Layer Stack Pattern

- Basemap or substrate: the contextual surface, such as road map, neutral light map, topographic map, imagery, terrain, or globe.
- Contextual layers: roads, labels, trails, rivers, contours, boundaries, land cover, parcels, transit, traffic, buildings, or weather context.
- Thematic layers: choropleth fills, proportional symbols, clusters, heatmaps, bins, routes, flows, rasters, uncertainty bands, event markers, or annotations.
- Interaction layers: hover/click targets, selection states, popups, tooltips, filters, layer toggles, legends, and keyboard or step-through controls.
- Operational layers: live updates, time sliders, alert states, stale-data indicators, and fallback static views where needed.

Use the source -> layer -> style -> interaction model whenever the library supports it. Keep one source feeding multiple layers when the same data needs fill, outline, vertex handles, labels, or hit targets.

## Purpose-Driven Library Recommendations

- Leaflet: simple slippy maps, raster tiles, markers, layer controls, GeoJSON overlays, popups, and small-to-medium datasets.
- MapLibre GL JS: open-source vector tiles, data-driven styling, label-aware layer ordering, hillshade, heatmaps, terrain-style context, and modern web map styling without a commercial map runtime.
- Mapbox GL JS: Mapbox-hosted styles, Studio workflows, vector tiles, polished 3D basemap features, and commercial Mapbox platform integration.
- Google Maps Platform: familiar managed road maps, Places, geocoding, routes, traffic context, street context, and product maps where Google coverage and services are the reason to use the platform.
- OpenLayers: GIS-heavy web maps, projections, WMS/WMTS/OGC services, vector and raster layers, custom controls, and standards-oriented enterprise maps.
- deck.gl: high-volume analytical overlays, GPU aggregation, arcs, trips, hexagons, grids, heatmaps, point clouds, and overlays on MapLibre, Google Maps, Mapbox, or ArcGIS.
- ArcGIS Maps SDK for JavaScript: hosted GIS services, FeatureLayer workflows, renderers, clustering, binning, heatmaps, editing, operational layers, and enterprise ArcGIS environments.
- Azure Maps or HERE Maps: enterprise routing, traffic, fleet, logistics, geocoding, provider data, and vendor-specific location services.
- CesiumJS: 3D globe, terrain, imagery layering, 3D Tiles, temporal geospatial scenes, and camera paths where 3D is analytically meaningful.
- D3 geo: custom projections, static or editorial thematic maps, bespoke annotations, and non-slippy analytical cartography.

## Output Pattern

When answering a map-design or map-stack request, include:

- Map justification: whether a map is needed at all.
- Recommended substrate: road, topo, imagery, neutral, boundary, terrain, or globe.
- Required contextual layers: roads, cities, rivers, trails, contours, boundaries, labels, parcels, or other context.
- Thematic layers: the data overlays and visual encodings.
- Interaction model: static, exploratory, operational, real-time, scrollytelling, or route-centric.
- Stack recommendation: library or platform choice with provider dependencies.
- Unresolved questions: only the missing high-impact questions.

## Common Mistakes

- Choosing a library before deciding whether the viewer needs roads, terrain, imagery, boundaries, or a neutral substrate.
- Using a satellite basemap because it looks rich when it makes symbols and labels harder to read.
- Showing roads for wilderness, wildfire, flood, or slope analysis without also showing terrain, hydrography, and access context.
- Showing topography for delivery, traffic, or route risk when road hierarchy and city labels are the real context.
- Drawing raw markers for dense events when aggregation, clustering, or binning is needed.
- Treating the basemap as decoration instead of part of the analytical contract.
- Showing sensitive geopolitical or humanitarian layers as exact, timeless, or source-free when the evidence is dated, estimated, disputed, or schematic.

## Adjacent Skills

- `../SKILL.md`
- `./map-or-not.md`
- `./choropleths-symbols-and-flows.md`
- `./point-overlap-strategies.md`
- `./multiscale-symbols-and-zoom-behavior.md`
- `./slippy-map-and-product-stack-selection.md`
- `../../../references/foundations/domain-contextual-surfaces.md`
- `../../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md`

## Source Links

- [Leaflet Documentation](https://leafletjs.com/reference.html)
- [Leaflet GeoJSON Tutorial](https://leafletjs.com/examples/geojson/)
- [Leaflet Layers Control Tutorial](https://leafletjs.com/examples/layers-control/)
- [MapLibre GL JS Examples](https://maplibre.org/maplibre-gl-js/docs/examples/)
- [MapLibre Style Spec: Sources](https://maplibre.org/maplibre-style-spec/sources/)
- [MapLibre Style Spec: Layers](https://maplibre.org/maplibre-style-spec/layers/)
- [Google Maps JavaScript API: Layers](https://developers.google.com/maps/documentation/javascript/layers)
- [Google Maps JavaScript API: Data Layer](https://developers.google.com/maps/documentation/javascript/datalayer)
- [Google Maps JavaScript API: deck.gl Overlay View](https://developers.google.com/maps/documentation/javascript/deckgl-overlay-view)
- [deck.gl Documentation](https://deck.gl/docs)
- [OpenLayers Examples](https://openlayers.org/en/latest/examples/)
- [ArcGIS Maps SDK for JavaScript: Layers](https://developers.arcgis.com/javascript/latest/layers/)
- [ArcGIS Maps SDK for JavaScript: Visualization](https://developers.arcgis.com/javascript/latest/visualization/)
- [Azure Maps Web SDK: Create a data source](https://learn.microsoft.com/en-us/azure/azure-maps/create-data-source-web-sdk)
- [HERE Maps API for JavaScript](https://docs.here.com/maps-api-for-js/docs/introduction-maps-api-for-javascript)
- [CesiumJS Imagery Layers](https://cesium.com/learn/cesiumjs-learn/cesiumjs-imagery/)
- [Axis Maps: Choropleth Maps](https://www.axismaps.com/guide/choropleth)
- [Axis Maps: Proportional Symbols](https://www.axismaps.com/guide/proportional-symbols)
- [Datawrapper: What to consider when creating choropleth maps](https://www.datawrapper.de/academy/what-to-consider-when-creating-choropleth-maps)
- [ColorBrewer](https://colorbrewer2.org/)
