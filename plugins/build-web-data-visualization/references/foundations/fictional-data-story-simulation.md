# Fictional Data Story Simulation

## Purpose

Use this reference when an editorial visualization, scrollytelling story, report, or demo uses invented, illustrative, or synthetic data. Fictional does not mean vague. A fictional story still needs a coherent data-generating world so the visuals have evidence, density, and discoverable structure.

The goal is to make simulated stories feel inspectable rather than ornamental. Every chart, map, particle layer, media overlay, and interaction should be backed by deterministic fields that can be regenerated and reviewed.

## Fictional Data Story Rule

- Define the simulated world before visual design.
- Preserve a fixed seed, named assumptions, and pure derivation functions.
- Label values clearly as fictional, simulated, illustrative, or synthetic.
- Generate enough dimensions to support several visual forms, not just headline KPIs.
- Keep the editorial claim explainable from the generated data. If the claim requires hand-written exceptions, improve the simulation.

## Minimum Data Richness Contract

Every ambitious fictional editorial or parallax story should include:

- Entity layer: ships, farms, stations, people, objects, routes, regions, machines, or other inspectable units.
- Temporal layer: hourly, daily, state-change, or event-sequence data.
- Spatial or physical layer: map, altitude, room, machine, route, body, terrain, cross-section, or other substrate.
- Event layer: storms, failures, thresholds, interventions, policy shifts, discoveries, milestones, or anomalies.
- Outcome layer: yield, risk, cost, delay, health, reliability, loss, gain, decision quality, or another consequence.
- Derived comparison layer: ranks, deltas, rates, bands, distributions, flows, uncertainty, or risk-adjusted outcomes.

## Embedded Visualization Self-Use Gate

Before composing the story, use `./embedded-visualization-self-use.md` to list each embedded visualization, write a mini-brief, and route it to a specialist skill:

- Chart choice, story framing, hierarchy, or critique: `../../skills/visualization-strategy-and-critique/SKILL.md`.
- Bespoke SVG marks, labels, annotations, and transitions: `../../skills/d3-data-visualization/SKILL.md`.
- Dense flat marks, swarms, heat strips, or repeated microcharts: `../../skills/canvas2d-data-visualization/SKILL.md`.
- Particles, flow, GPU-scale marks, WebGL scenes, or 3D: `../../skills/threejs-data-visualization/SKILL.md`.
- Maps, routes, spatial substrates, or geospatial layers: `../../skills/geospatial-and-cartographic-visualization/SKILL.md`.
- Distributions, intervals, missingness, or statistical comparisons: `../../skills/statistical-and-uncertainty-visualization/SKILL.md`.
- React, Next.js, or TypeScript integration: `../../skills/react-and-nextjs-data-visualization/SKILL.md` and `../../skills/typescript-data-visualization-engineering/SKILL.md`.
- Scroll-driven state, parallax, or media synchronization: `../../skills/scrollytelling-and-parallax-data-visualization/SKILL.md`.
- Final QA, visual regression, reduced-motion states, and generated-asset alignment: `../../skills/testing-data-visualizations/SKILL.md`, accessibility review, and human visual review.

Do not accept a generic embedded chart tile when a specialist skill would have improved the chart family, encoding, labels, interaction, fallback, accessibility, or QA plan. If delegation is available and the user has explicitly authorized it, substantial embedded visuals can use a fresh delegated specialist prompt; otherwise, load the relevant specialist skill locally before designing that layer.

## Simulation Design Pattern

1. Name the world, entities, units, and time span.
2. Declare the editorial claim and the data conditions that must make it true.
3. Generate base entities with stable roles and attributes.
4. Generate time-varying environment fields.
5. Generate event windows and thresholds.
6. Derive entity telemetry from environment, route, role, and event state.
7. Derive summaries, ranks, deltas, risk-adjusted metrics, and chart-specific datasets.
8. Add invariants that prove the story still holds after refactors.

## Good Visual Density

Rich fictional stories should trade paragraphs for inspectable evidence:

- Use direct labels, callouts, small multiples, swarms, heat strips, slopegraphs, route maps, cross-sections, flow diagrams, and sparklines.
- Let interactions reveal ship, object, route, station, or event details.
- Use generated imagery as substrate or object marks, while keeping numbers and labels editable.
- Use particles only when each particle has a stated meaning such as vapor flow, risk movement, recency, selection, or accumulation.
- Keep the default frame editorial. Exploration should reward curiosity, not be required to understand the main claim.

## Review Questions

- Could another engineer regenerate the same story from the seed and assumptions?
- Are there enough data fields to justify the visual variety?
- Does each embedded visualization have a named specialist owner, mini-brief, QA check, and delegated or local fresh-pass status?
- Are fictional values labeled honestly without weakening the narrative?
- Do the first frame, key frames, final frame, and reduced-motion state preserve the claim?
- Are interactions discovering data relationships rather than rescuing a sparse story?
