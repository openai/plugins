---
name: testing-data-visualizations
description: Test data visualizations and dashboards. Use when the user needs chart or diagram test strategy, screenshot or image diff testing, visual regression, mocked or synthetic chart data, component or unit tests, E2E dashboard QA, interactive UML-like diagram verification, scroll-driven story verification, export verification, or guidance on avoiding brittle over-testing.
---

# Testing Data Visualizations

## Overview

Use this skill when the main question is how to verify a visualization, not just how to render one. Testing charts means protecting analytical truth, interaction behavior, rendering stability, and product integration without turning every pixel into a brittle contract.

Default assumption: use the smallest test mix that catches wrong numbers, broken interactions, and obvious visual regressions. Favor deterministic fixtures and targeted image baselines over giant snapshot suites.

## Choose This Skill When

- the user asks how to test a chart, dashboard, or visualization component
- screenshot testing, image diffing, or visual regression is the main concern
- the user needs help deciding what to mock and where to mock it
- the question is about unit versus component versus E2E coverage
- a live dashboard, export flow, or embedded chart needs QA strategy
- the user wants help trimming a brittle or overgrown chart test suite

## Working Pattern

1. Identify the highest-risk failures:
   - wrong transforms, aggregation, binning, stacking, or sorting
   - wrong scale domain, legend mapping, or annotation placement
   - broken hover, focus, selection, brush, or cross-filter behavior
   - mobile layouts that put controls or prose before the main visualization, hide the chart behind settings, or fail to return to the chart after Apply, Cancel, Reset, or close
   - touch interactions with tiny hit targets, hover-only values, missing drag alternatives, scroll hijacking, or broken pinch/zoom ownership
   - on-screen keyboard and visual viewport regressions that cover the main evidence or the only critical action
   - operational workspace regressions where outline trees, filters, selected marks, central viewport, URL state, and inspectors fall out of sync
   - mobile capability regressions where AR, camera, motion, vibration, notification, or geolocation prompts appear too early, lack fallbacks, or become required without user approval
   - spotty-connection regressions where live visualizations blank out, lose stale indicators, mislabel partial data, or fail to reconnect gracefully
   - wheel-zoom, pinch, or drag interactions that also scroll the page or leak scroll chaining to the document
   - clipping, overlap, layout drift, or export mismatch
   - project changes or implementation code that began before the user approved a required generated design concept
   - Codex image-generated concepts whose implementation preserves only the vibe or pixels but loses the claim, source context, caveat, evidence hierarchy, layout contract, or interaction staging
   - generated asset crop, overlay alignment, or label-safe region regressions
   - Canvas or WebGL render readiness, context loss, blank frames, high-DPI scaling, and overlay alignment
   - WebGL fallback duplication where a fallback remains visible behind or above the primary scene
   - globe, map, terrain, or cutaway coordinate-frame regressions where markers, labels, textures, hit testing, and camera focus no longer align
   - interaction state-machine regressions where hover, selection, expansion, pause/resume, drag, wheel, reset, close, or idle behavior changes meaning
   - animated story states whose first frame, key frames, or final frame no longer communicate the claim
   - scrollytelling or parallax states that desynchronize text, data layers, media, trigger ranges, or reduced-motion fallbacks
   - composite reports, decks, or stories where embedded visual layers bypassed specialist mini-briefs and became generic chart cards
   - UML-like or software architecture diagrams with stale generated source, invalid relationships, broken import/export, layout overlap, lost source IDs, or round-trip drift
   - fictional or synthetic story simulations whose seeded data no longer supports the editorial claim, route ranking, event timing, or derived comparisons
   - stale, empty, partial, loading, or failure state regressions
2. Choose the lightest effective layer:
   - unit tests for pure data shaping and formatting logic
   - component tests for public chart contracts and interaction callbacks
   - visual regression for layout-sensitive and appearance-sensitive states
   - E2E tests for real user workflows, async data behavior, and export paths
3. Make rendering deterministic before asserting:
   - fixed viewport and container size
   - stable fonts, theme tokens, locale, and timezone
   - reduced or disabled animation
   - reduced-motion and final-state fixtures for animated stories
   - deterministic scroll position, viewport size, scene id, progress value, and media readiness for scrollytelling stories
   - deterministic WebGL camera, clock, particle seed, device pixel ratio, and quality settings
   - seeded or fixture-backed data
   - fixed generated asset fixtures or checked-in placeholders instead of live generation inside tests
   - approved large-screen and mobile concept screenshots or references plus a semantic design contract fixture, locked/flexible element fixture, concise concept-review bullet summary, and user approval record for concepted visualization work
   - deterministic desktop, mobile portrait, and optional mobile landscape viewport sizes
   - deterministic operational workspace fixtures for mode, selected entity, filters, outline scroll, inspector state, zoom or camera, and mobile panel state
   - visual viewport or keyboard-open fixture for input-heavy mobile views
   - mocked online, offline, delayed, stale, partial, and reconnect states for live/mobile data
   - mocked permission-denied and unsupported states for AR, camera, motion, vibration, notification, and geolocation paths when used
   - fixed fictional simulation seeds plus invariant checks for entity counts, event windows, value ranges, ranking outcomes, and summary consistency
   - explicit render-ready signals before capture
4. Mock at the boundary:
   - prefer mocked network responses, data loaders, or repository adapters
   - keep transform and render logic real whenever practical
   - maintain canonical, edge-case, and stress fixtures
5. Define the non-goals:
   - do not test third-party chart library internals
   - do not duplicate the same assertion at every layer
   - do not baseline volatile states unless the volatility is the feature
6. When the visualization is operational or live, include stale, delayed, empty, and degraded modes.

## Coverage Heuristics

- Unit tests are appropriate for scales, domains, bin boundaries, sort rules, label formatting, tooltip payload shaping, color assignment, selection reducers, and any logic that can fail without rendering.
- Component tests are appropriate for legends, axis labels that matter semantically, accessible names, empty and error states, callback payloads, interaction wiring, and conditional UI around the chart.
- Screenshot or image tests are appropriate for overlap, clipping, tick collisions, annotation placement, color regressions, dense mark readability, and regression-prone layout states.
- For art-directed editorial stories, screenshot tests are appropriate for first frame, selected key frames, final frame, generated-asset alignment, mobile crop behavior, and mobile portrait or landscape contract fidelity.
- For concept-first visualization work, pair visual regression with semantic fidelity checks against the shared design workflow: approved concept references, recorded review bullets, implementation-after-approval evidence, locked and flexible elements, approved deviations, title claim, required comparison, denominator, scale, caveat, source visibility, measured/estimated/schematic styling, and data-bound label preservation.
- For scrollytelling and parallax stories, cover enter, exit, reverse scroll, fast scroll, resize, reduced-motion, stacked mobile fallback, and static key frames.
- For fictional visual stories, add data invariant tests before visual regression: deterministic seed output, minimum richness layers, expected event timing, primary claim truth, and derived summary agreement.
- E2E tests are appropriate for cross-chart coordination, URL or filter state, live refresh behavior, drill-down, exports, downloads, and embedding or routing flows.
- For Canvas or WebGL charts, rely more on data-contract tests, interaction tests, render-ready markers, canvas-pixel sanity checks, context-loss coverage, and targeted visual baselines than on DOM snapshots.
- For advanced WebGL/geospatial/cutaway work, include desktop, mobile portrait, and optional mobile landscape screenshots, a no-WebGL fallback screenshot, a nonblank canvas-pixel or first-frame check, coordinate alignment spot checks, and live interaction smoke tests for drag, wheel, click, tap, hover, keyboard, reset, expand, close, and pinch as applicable.
- For mobile dashboards and live views, cover last-known-good rendering, stale/live/offline/partial badges, delayed events, reconnect, background/resume, lower-frequency degradation, notification opt-in, and vibration or alert fallbacks when used.
- For particle or flow animation, capture first frame, a representative key frame, final or paused state, and reduced-motion fallback rather than baselining every frame.
- For UML-like diagrams, test parser/model normalization, semantic diagnostics, layout fixtures, interaction states, export snapshots, and source round-tripping when the product promises it.

## Output Expectations

- Propose a layered test plan instead of a single-tool answer.
- Separate data correctness, visual stability, and workflow coverage.
- Explain where real data, mocked data, and synthetic fixtures each belong.
- Call out brittleness risks and how to keep the suite deterministic.
- When implementing tests, start with the narrowest high-value slice before scaling coverage.
- For visual stories, include a human review checklist in release notes when imagery, WebGL, particles, 3D, or animation materially affects interpretation.
- For concepted work, include the shared workflow evidence: approval status, approved concept references, concise review bullets, visual design contract, locked/flexible element record, mobile/landscape continuation record, material mismatches, fixes or approved deviations, and semantic fidelity QA results.
- For mobile-capable browser work, include screenshot or interaction checks for mobile portrait, mobile landscape when justified, main-visualization visibility, settings return path, touch targets, hover replacement, drag alternatives, keyboard-open viewport, spotty connection, and permission-denied fallbacks.
- For operational workspaces, include checks for command bars, outline/filter/detail panels, default selection, synchronized inspector state, pan/zoom/reset, empty-surface click versus drag, URL restore, and mobile command-panel behavior.
- For composite deliverables, include embedded visualization self-use review notes: each layer's specialist owner, mini-brief, QA check, and delegated or local fresh-pass status.
- For simulated stories, include data-richness and self-use-gate review notes: which specialist skill shaped each embedded visualization, which mini-brief it followed, and which invariants prove the fictional data still supports the story.

## References

- Shared theory:
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
  - `../../references/foundations/meaning-preserving-visual-design-workflow.md`
  - `../../references/foundations/embedded-visualization-self-use.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/operational-visualization-workspaces.md`
- Skill references:
  - `./references/test-level-selection.md`
  - `./references/unit-and-component-tests.md`
  - `./references/visual-regression-and-image-testing.md`
  - `./references/data-mocking-and-fixtures.md`
  - `./references/e2e-dashboard-and-export-strategies.md`
  - `./references/avoiding-brittle-over-testing.md`
- Useful templates:
  - `../../assets/templates/visualization-test-plan.md`
  - `../../assets/templates/visual-design-contract.md`
  - `../../assets/templates/advanced-interactive-visualization-contract.md`
  - `../../assets/templates/interactive-uml-test-plan.md`
  - `../../assets/templates/playwright-visual-regression-starter.ts`
- Adjacent skills:
  - `../scrollytelling-and-parallax-data-visualization/SKILL.md`
  - `../uml-and-software-architecture-visualization/SKILL.md`
  - `../react-and-nextjs-data-visualization/SKILL.md`
  - `../typescript-data-visualization-engineering/SKILL.md`
  - `../../references/foundations/fictional-data-story-simulation.md`
  - `../dashboards-and-real-time-visualization/SKILL.md`
  - `../accessibility-and-inclusive-visualization/SKILL.md`

## Representative Prompts

- "How should I test this React chart component?"
- "Set up screenshot testing for this dashboard without making it flaky."
- "What data should I mock for this D3 or Canvas visualization?"
- "Which parts of this chart deserve unit tests versus E2E tests?"
- "Help me design visual regression coverage for a live monitoring screen."
- "Review this visualization test suite and tell me what to delete."
- "Design tests for a parallax scrollytelling story without making screenshots flaky."
- "Design tests for an interactive UML, ERD, state machine, flow, dependency, or architecture diagram."
