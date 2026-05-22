# Domain Contextual Surfaces

## What Problem This Solves

Some visualizations become easier to understand, more memorable, and more useful when the marks live on a domain-native surface instead of a neutral plotting area. A soccer pass network on a pitch, a basketball shot chart on a court, vehicle telemetry on a race circuit, hospital movement on a floor plan, or sensor readings on an equipment schematic can reduce decoding because the viewer already knows the space.

Use this as analytical scaffolding, not decoration. The background should carry domain meaning, constrain layout, or explain position.

## When to Use It

Use a contextual surface when at least one is true:

- Real-world position, zones, lanes, sequence, adjacency, or orientation matters.
- The audience knows the domain and will read the surface faster than abstract axes.
- The background supplies useful anchors such as goals, center lines, turn numbers, rooms, machine components, route segments, or regulation zones.
- Marks should be positioned or biased by domain roles, such as defenders on the defensive side, midfielders near midfield, and forwards in attacking areas.
- A plain chart would require extra prose to explain where things happen.
- The subject is an object, room, vehicle, machine, terrain, route, or cutaway that can become the coordinate system for labels and data marks.

Avoid it when the surface is only thematic wallpaper, makes values harder to compare, hides uncertainty, or implies spatial precision the data does not have.

## Research and Source Guidance

- For regulated or standardized spaces, verify dimensions and markings against authoritative sources before drawing: sports laws, engineering specs, facility plans, GTFS or GIS data, equipment manuals, or domain documentation.
- Preserve units in code when possible, then map them into the render coordinate system with explicit scales.
- For proprietary or approximate spaces, label the geometry as schematic rather than exact.
- If rules, dimensions, or current standards could have changed, look them up before implementing.

## Design Rules

- Draw the surface with subdued contrast so data marks remain dominant.
- Keep semantic landmarks visible: boundaries, midlines, zones, goals, key areas, rooms, track turns, or component outlines.
- Use the same coordinate contract for background and marks.
- Let domain geometry influence layout when appropriate: force anchors, collision constraints, clipping, lanes, zones, or snapping.
- Keep labels readable on top of the surface with halos, contrast-aware color, or reserved label bands.
- Make interaction respect the surface: zoom, pan, hit testing, hover targets, and reset states should keep the domain context understandable.
- Provide an accessible text description that names the contextual surface and the meaning of the overlaid marks.
- If the surface is generated, keep values, labels, source notes, and uncertainty in editable overlays. Review the generated asset for factual plausibility and label-safe regions.

## Implementation Patterns

- SVG or D3: good for moderate mark counts, crisp vector backgrounds, official line work, labels, and export.
- Canvas: good when the contextual surface is mostly static and the mark layer is dense or frequently redrawn; use layered canvases or Canvas plus SVG/HTML overlays.
- WebGL or Three.js: use only when spatial depth, camera movement, dense GPU marks, particle/flow motion, or shader effects add real analytical value.
- Declarative chart grammars: use for simple layered marks when the background can be expressed cleanly; move to D3 or Canvas when custom geometry dominates the work.

## Examples

- Soccer influence network: draw the pitch from field dimensions, center circle, halfway line, penalty and goal areas, penalty spots, and corner arcs; bias node anchors by player role and side of play.
- Basketball shot chart: draw the court with hoop, lane, restricted area, three-point arcs, and corner threes; encode shot quality or outcome above the court.
- Motorsports telemetry: draw the circuit path, turn labels, sectors, pit lane, and start-finish line; place speed, braking, or tire marks along distance.
- Building occupancy or hospital movement: use a floor plan or simplified schematic; aggregate or jitter points inside rooms and corridors to avoid false precision.
- Supply chain or machine telemetry: use a schematic when component location and flow direction explain alerts better than a generic node-link diagram.
- Household inventory: use a room or object cutaway as the substrate, then anchor import shares, material origin, risk, or cost labels to visible objects.
- Technical adaptation: use an exploded schematic when additions, removals, protections, or flow paths explain change over time.

## Common Mistakes

- Using a beautiful background that competes with the data.
- Letting decorative imagery imply exact positions when the dataset only supports categories or approximate zones.
- Hard-coding pixel geometry without preserving source units or scale.
- Placing labels or controls where the background texture makes them unreadable.
- Baking data labels into a generated image so they cannot be edited, localized, tested, or updated.
- Forgetting that the contextual surface also needs testing at mobile sizes, export sizes, and high-density states.
