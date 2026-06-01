# WebGL 2D and Animation Patterns

## What Problem This Solves

This reference helps design 2D and 2.5D WebGL data visualizations that are fast, legible, and analytically honest.

## When to Use It

Use this when building dense scatterplots, embedding maps, networks, animated path systems, sprite fields, simulations, high-frequency dashboards, or particle-enhanced 2D visualizations.

## Core Patterns

- Dense scatterplot: use WebGL points, instanced quads, or library-specific scatter layers; keep axes and labels in SVG/HTML.
- Embedding map: use tiled or level-of-detail points, GPU picking, lasso selection, and semantic zoom labels.
- Dense network: use WebGL for nodes and edges, CPU or worker layout, level-of-detail edge rendering, and selected-neighborhood overlays.
- Flow map: use deck.gl `ArcLayer`, `LineLayer`, `PathLayer`, `TripsLayer`, or custom shader trails; normalize flow rates and provide static arrow or width encodings.
- Particle advection: use particles to reveal direction and flow field shape, not exact counts; pair with legend, density field, or aggregated totals.
- Streaming traces: use ring buffers or texture-backed history; decimate, aggregate, or window old data.
- Animated transitions: animate between meaningful states with interpolation, not arbitrary motion; expose final-state fallback.
- Focus effects: use halos, pulses, glows, or short-lived sparkles only for selected, changed, anomalous, or guided-narrative marks.

## Animation Rules

- Name the verb before coding: reveal, flow, accumulate, compare, transition, pulse, highlight, decay, orbit, slice, or scrub.
- Keep the first frame useful. Do not make users wait for the chart to become readable.
- Keep motion tied to data values or user state. Avoid ambient movement in analytical dashboards.
- Prefer `requestAnimationFrame` only when a frame actually changes, except intentionally continuous scenes.
- Use a single scene clock per visualization and pause it when hidden.
- Use uniforms for time, phase, selection, and thresholds when possible.
- Use reduced-motion to show final state, paused particles, key frames, or step controls.
- Provide pause/scrub controls when animation encodes time.

## Data Mapping for Motion

- Speed can encode rate, but only when users can compare it reliably; often width, color, or labels should carry quantitative value while speed conveys direction.
- Emission rate can encode volume, but cap it and document whether each particle is an individual item, a sample, or a visual carrier.
- Trail length can encode recency or persistence; it should not imply cumulative totals unless designed that way.
- Opacity decay can encode age, uncertainty, or fading focus; do not mix those meanings in one chart.
- Jitter can prevent overlap, but disclose when positions are schematic or randomized.
- Additive blending can make density feel vivid, but it can saturate quickly and hide high-value differences.

## WebGL vs Canvas2D for 2D

- Prefer Canvas2D when the marks are simple, the scene is flat, the animation is moderate, and custom hit testing is manageable.
- Prefer WebGL when mark count, pan/zoom smoothness, blending, particle count, shader logic, GPU picking, or per-point transitions are the bottleneck.
- Prefer SVG/HTML overlays for labels, axes, annotations, legends, tooltips, menus, and focusable controls even when marks are WebGL.
- Measure the real workload. WebGL has setup, buffer upload, context, shader, texture, and memory costs that can make it worse for small or simple charts.

## Implementation Checklist

- Define coordinate transforms in one place and share them with overlays and hit testing.
- Use typed arrays and stable schemas for positions, colors, sizes, timestamps, IDs, and selection state.
- Separate static buffers from dynamic buffers.
- Keep per-frame CPU work minimal: update uniforms, small buffers, or texture regions.
- Use workers for layout, aggregation, simulation, or preprocessing when CPU work threatens interaction.
- Rebuild GPU buffers only when the data version changes.
- Clamp device pixel ratio for heavy scenes.
- Use offscreen or virtualized rendering for non-visible scenes only when it reduces total work.
- Provide deterministic visual states for testing, screenshots, and reports.

## Common Mistakes

- Letting motion carry the only evidence.
- Using particles to make a static relationship feel more important than it is.
- Overdrawing millions of translucent marks without aggregation or density design.
- Putting every label into the WebGL layer and losing accessible text.
- Creating independent animation loops for every chart instance.
- Ignoring static export, screenshot reproducibility, and reduced-motion requirements.

## Adjacent Skills

- `../SKILL.md`
- `../../canvas2d-data-visualization/SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`
- `../../testing-data-visualizations/SKILL.md`

## Source Links

- [deck.gl Animations and Transitions](https://deck.gl/docs/developer-guide/animations-and-transitions)
- [deck.gl TripsLayer](https://deck.gl/docs/api-reference/geo-layers/trips-layer)
- [deck.gl ArcLayer](https://deck.gl/docs/api-reference/layers/arc-layer)
- [deck.gl PathLayer](https://deck.gl/docs/api-reference/layers/path-layer)
- [deck.gl PostProcessEffect](https://deck.gl/docs/api-reference/core/post-process-effect)
- [PixiJS ParticleContainer](https://pixijs.com/8.x/guides/components/scene-objects/particle-container)
- [Plotly JavaScript](https://plotly.com/javascript/)
- [Apache ECharts Animation Transition](https://echarts.apache.org/handbook/en/how-to/animation/transition/)
- [regl-scatterplot](https://github.com/flekschas/regl-scatterplot)
