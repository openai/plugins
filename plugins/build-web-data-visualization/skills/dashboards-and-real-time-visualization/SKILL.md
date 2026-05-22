---
name: dashboards-and-real-time-visualization
description: Design dashboards and live visualization systems. Use when the user needs monitoring views, streaming charts, coordinated interactions, downsampling, or performance-aware operational visualization.
---

# Dashboards and Real-Time Visualization

## Overview

Use this skill when the visualization is a system, not a screenshot. That means update cadence, latency, interaction design, observability, and rendering budgets matter as much as chart choice.

If the main request is about how to test a live dashboard, freeze streams, mock refresh behavior, or cover alerting and stale states end to end, route first to `../testing-data-visualizations/SKILL.md`.

Mobile operational use is default unless explicitly excluded. Use `../../references/foundations/mobile-first-responsive-visualization.md` to plan the mobile portrait dashboard, optional landscape mode, touch interaction, on-screen keyboard behavior, spotty connection handling, and alerting or vibration strategy.

This skill covers three tightly related problems:

- real-time streaming and refresh behavior
- layout hierarchy and scan-first dashboard composition
- interaction patterns and coordinated views
- performance and scale

## Default Questions

1. What is the update model?
   - append-only stream
   - periodic polling
   - event bursts
   - full snapshot replacement
2. What latency matters?
   - sub-second monitoring
   - near-real-time operational review
   - asynchronous reporting
3. What must the user do?
   - notice anomalies
   - compare current versus historical
   - inspect causes
   - filter and drill down
4. What are the hard limits?
   - frame budget
   - memory budget
   - network budget
   - exportability
   - mobile bandwidth, battery, and thermal budget
5. How many visualization instances can be visible at once?
   - single focal chart
   - a few coordinated panels
   - many repeated tiles or sparklines
6. What mobile state must work under interruption?
   - spotty or offline connection
   - app backgrounding or tab visibility changes
   - one-handed use
   - alert acknowledgment
   - on-screen keyboard for filters or notes

## Real-Time Design Rules

- Show time windows clearly.
- Distinguish live data from historical context.
- Handle missing, late, and out-of-order events explicitly.
- Keep the last known good visualization visible during reconnects, with stale, delayed, partial, offline, and error states distinct from normal live data.
- Show last updated time and update cadence near the evidence.
- Use aggregation, downsampling, or rollups before raw point dumping.
- Provide alert thresholds, annotations, and state transitions, not just moving lines.
- Use vibration, system notifications, or push-style alerts only for user-requested and meaningful state changes; always provide an in-app visual and accessible alert path.
- Keep the most important metric stable in position and encoding.
- Keep keys with their charts: direct labels or chart-adjacent keys beat a shared legend parked elsewhere on the screen.
- Use sparklines and other microcharts when compact trend context helps scanning, but rely on nearby labels and values to carry meaning.
- Design dashboards around situation awareness, not around maximum tile count.
- Prefer self-explanatory panels and concise labels over instructional paragraphs scattered across the UI.

## Layout and Scanning Defaults

- Give the screen a clear focal path: current state first, then supporting context, then controls and secondary diagnostics.
- Avoid grids where every tile has equal visual weight unless the user truly needs uniform scanning across peers.
- Keep filters and toggles near the views they change instead of collecting everything in a distant control rail.
- Reserve callouts and narrative copy for anomalies, caveats, or actions. The normal state should be legible without tutorial text.
- Collapse or defer low-value controls so the live state stays visually dominant.
- On mobile, do not stack the filter rail or diagnostic controls before the live state. Use bottom sheets, drawers, tabs, or inline controls that return the user to the affected visualization after Apply, Cancel, Reset, or close.
- Use mobile landscape for monitoring views when a wide timeline, map, field, route, dense table, or multi-series trace is meaningfully clearer in a handheld wide orientation, but still provide a portrait summary.

## Interaction Patterns

- overview first, filter or focus, then details on demand
- overview plus detail
- focus plus context
- brush and link
- hover for preview, click for commitment
- tap/focus for preview, tap again or explicit action for commitment on touch devices
- drill-down and drill-through
- persistent selections that survive updates
- explicit reset and undo paths

Interactivity should reduce cognitive load, not hide essential context behind constant mouse movement.

For mobile dashboards, add step-through controls, search, or nearest-item selection for dense marks; do not rely on hover, pixel-perfect taps, or one-finger chart panning that traps page scroll.

## Performance Defaults

1. Budget for 16 ms frames only when truly needed.
2. Reduce work before optimizing code:
   - fewer marks
   - smarter aggregation
   - smaller repaint regions
   - lower-frequency updates where appropriate
3. Choose the renderer intentionally:
   - SVG for semantics and annotation
   - Canvas2D for dense 2D raster workloads
   - WebGL, deck.gl, PixiJS, Sigma.js, or Three.js for GPU-scale marks, maps, particles, graph rendering, or true 3D
4. Use ring buffers, viewport culling, and multi-resolution summaries for long-running live views.
5. Separate interaction state from render state so updates remain predictable.
6. Use particles or glow in dashboards only for active flow, alert state, focus, or recency. Avoid ambient motion that competes with monitoring.

## Output Expectations

- Describe the update model and failure modes.
- Describe mobile reconnect, stale-data, offline/partial-data, and low-bandwidth behavior.
- Explain what a user should understand at first scan before touching any controls.
- Explain what the mobile user sees first and how the main visualization remains visible around controls and keyboard input.
- Define the interaction contract before building widgets.
- State how the system degrades when data rate or mark count rises.
- Include a technical design section for new work covering simultaneous chart count, per-instance and page-level budgets, and maintenance implications of the chosen rendering strategy.
- Keep accessibility and export strategy visible.

## References

- Shared theory:
  - `../../references/foundations/storytelling-annotation-and-critique.md`
  - `../../references/foundations/layout-hierarchy-and-self-explanatory-ux.md`
  - `../../references/foundations/interaction-models-and-progressive-disclosure.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
- Skill references:
  - `./references/monitoring-vs-analysis.md`
  - `./references/streaming-data-pipelines.md`
  - `./references/interaction-patterns.md`
  - `./references/performance-and-degradation.md`
  - `../testing-data-visualizations/SKILL.md`

## Representative Prompts

- "Build a real-time operations dashboard from a WebSocket feed."
- "Keep this live chart smooth with 100 updates per second."
- "Design brushing, cross-filtering, and annotations for this monitoring UI."
- "Tell me if this should be a dashboard or a report."
- "Critique this monitoring screen using operational dashboard principles."
