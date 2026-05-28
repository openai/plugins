---
name: geospatial-and-cartographic-visualization
description: Design geospatial and cartographic visualizations. Use when the user needs help deciding whether to use a map, choosing projections or basemaps, building choropleths or symbol maps, or implementing thematic maps, slippy maps, or geospatial interactions with D3 geo, Leaflet, MapLibre, Mapbox GL JS, Google Maps, OpenLayers, deck.gl, ArcGIS Maps SDK, Azure Maps, HERE Maps, CesiumJS, or related tools.
---

# Geospatial and Cartographic Visualization

## Overview

Use this skill when place, projection, movement, or spatial adjacency matter analytically, or when the product surface genuinely needs a map interaction model. Do not use maps by reflex just because there is a latitude, longitude, or region name in the dataset.

Default assumption: use a map only when geography is part of the reasoning or when the product truly needs a map surface. If the task is comparison, ranking, or distribution across regions, a non-map view may be clearer. Distinguish analytical cartography from product-map UX early.

Mobile map users are common and often primary. Use `../../references/foundations/mobile-first-responsive-visualization.md` when choosing marker density, label strategy, portrait/landscape behavior, touch gestures, geolocation/camera/AR capability use, and spotty tile or data connections.

## Working Pattern

1. Decide whether the question is spatial or merely grouped by place.
2. Infer the user's map purpose before asking questions. Recommend a likely substrate and state assumptions, then ask only the missing high-impact questions that would change the map design.
3. Decide which map experience is needed:
   - thematic analytical map
   - slippy map for exploration or layered context
   - route, places, or product-map experience
   - terrain, imagery, or operational situational-awareness map
4. Choose the basemap or substrate intentionally:
   - road and city map for driving, routing, traffic, delivery, road safety, or weather-for-driving
   - topographic or terrain map for hiking, wildfire, flood, landslide, environmental risk, outdoor planning, or field work
   - neutral administrative boundary map for regional comparison when geography matters
   - imagery or raster substrate for satellite, remote sensing, damage, land use, agriculture, construction, or visual evidence
   - quiet neutral basemap for dense points or events unless roads, terrain, or boundaries are part of the reasoning
   - globe or 3D terrain only when depth, terrain, occlusion, or globe context changes the analysis
5. Choose the map family:
   - choropleth
   - symbol map
   - clustered symbol map
   - flow map
   - hex or tile summary
   - raster or density field
   - animated route or trip layer
   - terrain, risk, or damage texture fused to a physical substrate
6. If points overlap, choose the overlap strategy intentionally:
   - clustered summary symbols when dense points need a count or summary preview that can dissolve on zoom
   - displacement or spiderfying when the count is low and each individual point needs immediate visibility
   - exact-location anchor dots when large proportional, halo-style, or concentric point symbols must preserve the true coordinate at detailed zoom levels
7. Choose multiscale zoom behavior intentionally:
   - map-space geometry when the shape, area, or path itself is the thing being inspected
   - screen-stable symbols, labels, and callouts when they act as locators, badges, or UI-like annotations
   - screen-stable strokes for borders, outlines, and graticules unless changing thickness is itself meaningful
   - zoom-stepped sizing only when legibility or hierarchy genuinely improves by changing symbol or label size across scales
8. If dense visible points need one-at-a-time inspection, consider step-through selection with keyboard arrows or previous/next controls within the current extent or current layer.
9. For mobile maps, define the portrait and optional landscape experience before implementation:
   - fewer markers and shorter labels at narrow widths
   - mobile-only marker or label variants when needed
   - a key or detail sheet for labels that cannot fit
   - tap, step-through, search, and reset paths for dense points
   - two-finger zoom or explicit zoom controls when one-finger pan should preserve page scroll
   - stale tile/data, offline, low-bandwidth, and reconnect states
10. For scientific, live, disaster, terrain, climate, seismic, ocean, or other source-sensitive spatial work, create a source and method ledger before visual design or implementation. Include source URL/API, license or attribution, update cadence, units, coordinate reference, coverage gaps, rate limits, cache/fallback policy, and which layers are measured, inferred, schematic, or decorative.
11. Choose a projection, basemap style, and normalization strategy intentionally.
12. For globes or custom projections, audit coordinate alignment across basemap/texture, event markers, labels, hit testing, camera focus, and fallback geometry before coding. Record longitude origin, wrap policy, and at least a few known-place spot checks.
13. Choose the implementation stack:
   - D3 geo for custom projections, thematic cartography, and annotation-rich analytical maps
   - Leaflet for lightweight slippy maps, markers, layer controls, GeoJSON overlays, and familiar pan or zoom controls
   - MapLibre GL JS or Mapbox GL JS for vector-tile styling, data-driven styling, label-aware layer ordering, hillshade, heatmaps, tilt or rotation, and modern slippy-map experiences
   - Google Maps when managed road basemaps, routing, Places, geocoding, traffic context, or Google Maps Platform capabilities drive the product need
   - OpenLayers for GIS-heavy web maps, projections, WMS/WMTS/OGC services, vector and raster layers, and advanced layer control
   - deck.gl for high-volume layers, aggregation, trips, arcs, paths, particle-like flows, point clouds, hex or grid layers, and GPU-heavy geospatial interaction on top of MapLibre, Google Maps, Mapbox, or ArcGIS
   - ArcGIS Maps SDK for hosted GIS services, FeatureLayer workflows, renderers, clustering, binning, heatmaps, editing, and operational maps
   - Azure Maps or HERE Maps for enterprise routing, traffic, fleet, logistics, geocoding, provider data, and vendor-specific location services
   - CesiumJS for 3D globe, terrain, imagery layering, temporal scenes, and 3D Tiles
14. Keep legends, labels, uncertainty, and comparison needs explicit.
15. For editorial map stories, decide whether the map is a quiet stage for evidence, a moving flow field, a particle-guided route story, a risk surface, or a scrollytelling sequence.
16. For conflict, occupation, displacement, disaster, or humanitarian maps, use `../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md`. Require dated states, source and method notes, attribution, and visible distinctions between measured, estimated, and schematic geometry.
17. If the map owns wheel zoom or gesture panning, also own the browser behavior: prevent page scrolling or scroll chaining, keep reset and button controls visible, and verify the interaction with mouse wheel, trackpad, touch pan, and pinch.
18. Use AR, camera, geolocation, or motion only when they materially improve spatial reasoning or data collection, and always provide manual/non-permission fallbacks.

## Output Expectations

- Explain why a map is or is not justified.
- State the recommended basemap or substrate, required contextual layers, thematic data layers, and any unresolved questions before choosing the implementation stack.
- Call out projection, area, and normalization tradeoffs.
- For live/scientific spatial work, include the source and method ledger plus missing-data/fallback policy.
- For globes/custom projections, include coordinate-frame alignment checks and shortest-path focus behavior when selection moves the camera or globe.
- If large or overlapping point symbols are involved, call out whether the map needs clustered summaries, spiderfying or displacement, exact-location anchor dots, or a combination across zoom levels.
- For interactive maps, state which layers should zoom in map space and which should remain screen-stable.
- For mobile maps, state the portrait layout, whether landscape is justified, marker/label reduction rules, touch gesture ownership, geolocation/camera/AR usage if any, and stale/offline tile or data behavior.
- If users may inspect many nearby points in sequence, call out whether the map needs step-through selection controls in addition to direct clicking.
- Choose the stack based on interaction model, data scale, basemap needs, and annotation requirements.
- For editorial map stories, state the visual substrate, flow or risk layer, annotation plan, motion purpose, and static fallback.
- For animated flow or particle maps, state what each moving mark represents, whether emission rate encodes volume or only direction, and how the same claim appears in reduced-motion and static exports.
- For sensitive geopolitical or humanitarian maps, state the date or update cadence for each map state, the source hierarchy, the evidence status of each layer, and the ethical framing constraints.
- Call out any meaningful dependency on tile providers, commercial map platforms, or style infrastructure.

## References

- Shared theory:
  - `../../references/foundations/task-abstraction-and-chart-selection.md`
  - `../../references/foundations/perception-color-and-encoding.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/art-directed-interactive-visual-stories.md`
  - `../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md`
- Skill references:
  - `./references/map-or-not.md`
  - `./references/adaptive-basemaps-and-layer-stacks.md`
  - `./references/projections-and-normalization.md`
  - `./references/source-method-and-coordinate-ledger.md`
  - `./references/choropleths-symbols-and-flows.md`
  - `./references/point-overlap-strategies.md`
  - `./references/multiscale-symbols-and-zoom-behavior.md`
  - `./references/deckgl-d3-geo-stack-selection.md`
  - `./references/slippy-map-and-product-stack-selection.md`

## Representative Prompts

- "Should this be a map at all?"
- "What basemap and contextual layers should this map use?"
- "Choose the right geospatial visualization for this dataset."
- "Map weather conditions for driving."
- "Visualize wildfire risk near hiking trails."
- "Show flood exposure with terrain and rivers."
- "Help me build a choropleth without misleading normalization."
- "Should this map cluster nearby points, spiderfy them, or show exact-location anchor dots?"
- "How do I keep exact coordinates visible inside large proportional symbols?"
- "What should zoom with the map and what should stay the same size on screen?"
- "When should I use deck.gl instead of D3 geo?"
- "Should this product map use Leaflet, MapLibre, or Google Maps?"
- "Should this use Leaflet, MapLibre, Google Maps, OpenLayers, ArcGIS, deck.gl, or CesiumJS?"
- "Critique this map for cartographic and analytical mistakes."
