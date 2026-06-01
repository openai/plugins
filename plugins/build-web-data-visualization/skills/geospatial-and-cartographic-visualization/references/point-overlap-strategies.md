# Point Overlap Strategies

## What Problem This Solves

This reference helps choose how to handle nearby or overlapping points once a point map is already justified.

## When to Use It

Use this when individual point symbols collide, stack, or become unreadable at the current scale.

## Key Takeaways

- Use clustered summary symbols when the map needs a quick preview of dense point areas and exact per-point inspection can wait until zoom or click.
- Prefer marker clustering, screen-space clustering, or feature-reduction clustering when the goal is to reduce clutter and show approximate density at a glance.
- Use a representative cluster symbol when one member should stand in for the group, such as the largest event plus the total count of nearby events.
- Use displacement or spiderfying when overlap counts are small and users need to see each individual point immediately rather than an aggregate preview.
- Use an exact-location anchor dot when large proportional, halo-style, or concentric symbols make it hard to see the true coordinate after clusters dissolve.
- Treat the anchor dot as a symbol-design pattern, not as a replacement for clustering or displacement. It usually complements one of those strategies across zoom levels.
- Keep the anchor dot above the decorative rings or halos, and prefer draw order that keeps smaller symbols above larger ones so detailed locations remain visible.
- Let clustered summaries dissolve as users zoom in; do not keep clusters active longer than necessary at detailed scales.
- When users need to inspect many visible nearby points one at a time, add step-through selection with left or right keys or previous and next controls within the current extent instead of requiring repeated precision clicks.

## Naming Guidance

- `marker clustering`, `screen-space clustering`, and `feature-reduction clustering` are the standard names for grouping nearby points into a count or summary symbol that breaks apart on zoom.
- `spiderfying` is the common interactive name for expanding a small overlapping set from one cluster center so each point can be clicked.
- `displacement` is the cartographic generalization term for moving symbols apart while trying to preserve the local pattern.
- `exact-location anchor dot` is the plugin's descriptive term for a layered point symbol whose tiny center mark stays visible above large rings or halos to preserve locational certainty.

## Common Mistakes

- Fan-spreading dozens of points when a clustered summary would communicate the situation more cleanly.
- Clustering points that users must compare individually right away.
- Treating cluster counts or summary symbols as analytical statistics instead of visual simplifications.
- Failing to define what the representative symbol means when using a strongest, largest, or predominant member to stand in for a cluster.
- Using large proportional or halo symbols without a visible center mark, leaving users unsure of the exact coordinate.
- Forgetting draw order, which can let large marks bury smaller nearby locations even after clustering is disabled.
- Making users repeatedly re-click dense point symbols when a sequential browsing control would better support comparison.

## Adjacent Skills

- `../SKILL.md`
- `./choropleths-symbols-and-flows.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`

## Source Links

- [ArcGIS Maps SDK for JavaScript: Clustering](https://developers.arcgis.com/javascript/latest/visualization/high-density-data/clustering/)
- [ArcGIS Maps SDK for JavaScript: FeatureReductionCluster](https://developers.arcgis.com/javascript/latest/references/core/layers/support/FeatureReductionCluster/)
- [Mapbox GL JS: Create and style clusters](https://docs.mapbox.com/mapbox-gl-js/example/cluster/)
- [Leaflet.markercluster](https://leaflet.github.io/Leaflet.markercluster/)
- [ArcGIS Pro: Proportional symbols](https://pro.arcgis.com/en/pro-app/latest/help/mapping/layer-properties/proportional-symbology.htm)
- [ArcGIS Pro: Point symbols](https://pro.arcgis.com/en/pro-app/latest/help/mapping/layer-properties/point-symbols.htm)
- [ArcGIS Pro: Marker symbol layers](https://pro.arcgis.com/en/pro-app/latest/help/mapping/layer-properties/marker-symbol-layers.htm)
- [ArcGIS Pro: Position and place marker symbol layers](https://pro.arcgis.com/en/pro-app/3.5/help/mapping/layer-properties/position-and-place-marker-symbol-layers.htm)
- [ArcGIS Pro: Disperse Markers](https://pro.arcgis.com/en/pro-app/latest/tool-reference/cartography/disperse-markers.htm)
- [Liu et al. 2019: Real-Time Displacement of Point Symbols Based on Spatial Distribution Characteristics](https://www.mdpi.com/2220-9964/8/10/426)
