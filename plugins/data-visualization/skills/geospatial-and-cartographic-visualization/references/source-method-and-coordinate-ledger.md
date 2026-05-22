# Source, Method, and Coordinate Ledger

## What Problem This Solves

Spatial visualizations can look credible while mixing incompatible sources, coordinate frames, units, or update cadences. This ledger makes live scientific and geospatial work explicit before design or implementation.

## Source Ledger

For each layer, record:

- source name, URL/API, license, attribution, and update cadence
- fields used, units, coordinate reference, and time zone/date policy
- coverage area, known gaps, precision, and latency
- request limits, batching limits, CORS/cache boundary, and failure modes
- fallback source or seeded fixture
- whether the layer is measured, inferred, estimated, simulated, schematic, or decorative

## Coordinate Ledger

For each rendered layer, record:

- input coordinate frame and unit
- projection or transform owner
- longitude origin and antimeridian/wrap policy
- vertical/depth/elevation convention and exaggeration policy
- alignment spot checks against known places
- how the same transform is shared by marks, labels, hit testing, camera focus, and fallback

## Label And Multiscale Policy

- Separate country, ocean/sea/lake/river, major city, regional city, and town labels by scale tier.
- Keep labels screen-stable when they behave like UI callouts; keep them map-space when location shape matters.
- Use collision suppression or priority rules before adding more labels.
- Reveal more labels only when zoom or focus makes them useful.

## Common Mistakes

- Choosing a public API after the visual design already assumes impossible data.
- Mixing a texture's longitude origin with marker coordinates from a different convention.
- Treating a terrain API without bathymetry as proof that water is absent.
- Using decorative place labels that do not share the same projection as the data marks.
