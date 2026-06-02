# Particle Effects and Flow

## What Problem This Solves

This reference turns particle effects from decoration into disciplined data-visualization encodings for flow, motion, focus, and state.

## When to Use It

Use this when a visualization may include particles, sparkles, fire, smoke, glowing trails, pulses, animated network flow, trip traces, migration or movement paths, density advection, or attention effects.

## First Question

Ask: what does one particle mean?

- entity: one particle is one observed person, vehicle, packet, event, or transaction
- sample: one particle represents a sampled subset of many items
- carrier: particles are visual carriers showing direction, velocity, or pathway shape, not count
- focus cue: particles mark selection, anomaly, change, risk, or guided attention
- texture: particles are only atmospheric decoration

Use entity, sample, carrier, or focus cue. Avoid texture in analytical work.

## Legitimate Uses

- Directed flow: particles move along edges, routes, rivers, pipes, or paths to show direction and sequence.
- Volume plus direction: particle emission rate or trail density supports width, color, or labels that carry the quantitative value.
- Time progression: fading trails show recent movement, trip histories, or temporal windows.
- Field behavior: particles advect through a vector field to reveal swirl, convergence, divergence, or prevailing direction.
- Anomaly or selection: a short pulse, halo, shimmer, or sparkle calls attention to one mark without changing its value encoding.
- Hazard or heat: glow, ember, fire, or smoke metaphors show heat, active risk, outages, or alarms only when the domain supports the metaphor.
- Onboarding or narrative reveal: particles briefly trace the path users should inspect, then settle into a static readable state.

## Avoid Particles When

- they imply individual entities from aggregate or uncertain data
- they make serious human harm feel spectacular or game-like
- they obscure labels, totals, uncertainty, or source caveats
- they encode quantitative differences with speed alone
- they add continuous motion to an operational dashboard that users need to monitor calmly
- reduced-motion users would lose the main claim
- a static arrow, width, color ramp, small multiple, or annotation would communicate more clearly

## Design Parameters

- Emission source: node, edge, route, surface, selected mark, threshold crossing, or story cue.
- Path: straight line, arc, polyline, spline, geodesic, force-directed edge, vector field, or screen-space trail.
- Rate: constant, value-scaled, thresholded, sampled, or event-driven.
- Speed: domain-time based, normalized for legibility, or constant carrier speed.
- Lifetime: route length, recency window, pulse duration, or decay curve.
- Size: usually stable or lightly value-scaled; avoid size flicker.
- Color: semantic state first, magnitude second; keep glow colors in the same semantic family.
- Opacity: age, uncertainty, density, or focus. Do not reuse opacity for multiple meanings.
- Blending: normal for readability, additive for glow and density with careful clamping.
- Interaction: particles usually should not be individually hoverable unless they are actual data entities.
- Fallback: static arrows, dashed paths, flow widths, highlighted outlines, final frame, or stepped key frames.

## Implementation Patterns

- Three.js particles: use `Points` and `PointsMaterial` for simple point clouds; use instanced quads or custom `ShaderMaterial` for textured sprites, variable size, glow, or per-particle lifetime.
- deck.gl flows: use `TripsLayer` for timestamped paths, `ArcLayer` for origin-destination links, `LineLayer` or `PathLayer` for static paths, and custom layers for shader-level particle movement.
- PixiJS particles: use `ParticleContainer` for high-volume 2D sprites when texture atlases and simple properties are enough.
- Sigma.js graph effects: use graph-specific highlighting and custom layers for network focus before building a bespoke edge-particle renderer.
- raw WebGL/regl/luma.gl: use ping-pong buffers, transform feedback, data textures, or shader time uniforms for high-count particle simulation.
- ECharts effects: use built-in transitions, `effectScatter`, keyframe animations, or ECharts GL when staying inside an ECharts stack.

## Flow Map Guidance

- Use static width, color, and labels for quantities; use particles to show direction, timing, or activity.
- For origin-destination maps, decide whether arcs are geographical paths, schematic links, or great-circle connections.
- For migration, evacuation, aid, or conflict-related movement, be especially careful: particles can dehumanize or aestheticize harm. Prefer restrained traces, clear caveats, and static fallback.
- For network flow, avoid sending particles down every edge at once. Filter, bundle, aggregate, or show focus neighborhoods.
- For city-to-city movement, sample particles so density does not hide geography or imply false precision.
- For data pipelines or system diagrams, particles can represent packets or events if the unit is explicit and count/rate is labeled elsewhere.

## Attention Effects

- Pulse: best for selected, newly changed, or alerting marks. Keep it brief and low amplitude.
- Halo: best for focus state while preserving underlying mark color and size.
- Sparkle: best for discovery, achievements, or positive highlights; use sparingly in serious analytical contexts.
- Fire or ember: best for heat, overload, urgent risk, or combustion-like domain metaphors; avoid for human tragedy.
- Glow trail: best for recency, active route, or current selection.
- Shockwave/ripple: best for origin events, spread, or radius of influence when distance from source matters.

## Validation Questions

- Can a viewer explain what the particles mean after looking at the legend or annotation?
- Would a static screenshot still support the claim?
- Does reduced-motion preserve the evidence?
- Does the effect preserve uncertainty and aggregation caveats?
- Does the effect help the primary audience make a better decision?
- Does the effect stay legible on mobile and low-power GPUs?

## Common Mistakes

- Equating more particles with more truth.
- Letting dense glows saturate into an unreadable blob.
- Mapping both count and speed to the same particles without labels.
- Animating all flows continuously when the story only needs selected route playback.
- Using fire, sparks, or explosions as generic "important" styling.
- Forgetting to pause animations in hidden tabs, modals, and non-visible routes.

## Adjacent Skills

- `../SKILL.md`
- `../../geospatial-and-cartographic-visualization/SKILL.md`
- `../../visualization-strategy-and-critique/SKILL.md`
- `../../accessibility-and-inclusive-visualization/SKILL.md`

## Source Links

- [Three.js Points](https://threejs.org/docs/pages/Points.html)
- [Three.js PointsMaterial](https://threejs.org/docs/pages/PointsMaterial.html)
- [Three.js ShaderMaterial](https://threejs.org/docs/pages/ShaderMaterial.html)
- [deck.gl TripsLayer](https://deck.gl/docs/api-reference/geo-layers/trips-layer)
- [deck.gl ArcLayer](https://deck.gl/docs/api-reference/layers/arc-layer)
- [deck.gl Animations and Transitions](https://deck.gl/docs/developer-guide/animations-and-transitions)
- [PixiJS ParticleContainer](https://pixijs.com/8.x/guides/components/scene-objects/particle-container)
- [Babylon.js Specifications](https://www.babylonjs.com/specifications/)
- [Apache ECharts Animation Transition](https://echarts.apache.org/handbook/en/how-to/animation/transition/)
