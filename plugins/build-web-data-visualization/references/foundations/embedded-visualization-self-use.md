# Embedded Visualization Self-Use

## Purpose

Use this reference when a report, deck, PDF, editorial story, scrollytelling page, parallax sequence, visual article, or multi-panel infographic contains meaningful embedded visualizations. The surrounding story can make charts feel like layout pieces. This gate prevents that by giving each visual layer its own specialist pass before final composition.

The goal is not ceremony. The goal is to make embedded charts, maps, swarms, tables, flow layers, particle fields, overlays, insets, and keys visibly better because the relevant visualization skill shaped the encoding, interaction, fallback, accessibility, and QA plan.

## When This Gate Applies

Use the gate for composite deliverables:

- reports, decks, PDFs, and article layouts with multiple figures
- scrollytelling or parallax stories with staged chart, map, media, or animation states
- editorial infographics with small multiples, inset charts, table-graphics, or contextual substrates
- fictional or illustrative stories after the simulation richness contract is complete
- visual stories that mix maps, distributions, flows, particles, generated imagery, or export fallbacks

Keep simple one-chart requests lightweight. A single straightforward chart still needs good strategy, accessibility, and testing judgment, but it does not need a full embedded-layer inventory unless it is part of a larger composed deliverable.

## Inventory First

Before implementation or document layout, list every evidence-bearing visual layer:

- chart, map, table-graphic, sparkline table, microchart, or small multiple
- swarm, distribution, interval, uncertainty, missingness, or statistical layer
- flow, route, network, particle, density, or WebGL layer
- contextual substrate, generated-image overlay, inset, visual key, or annotation graphic
- static fallback, export frame, reduced-motion frame, or document-only figure

Do not implement story or report visuals as generic cards unless the specialist pass confirms that a simple card or plain table is the right treatment.

## Mini-Brief Contract

Write a short, self-contained mini-brief for each layer before composing the page or document.

| Field | What To Capture |
| --- | --- |
| Visual layer | The layer name and where it appears in the story, page, slide, or scene. |
| Story job | The claim, comparison, lookup, or transition this layer must support. |
| Data shape | Grain, fields, units, time span, geography, volume, uncertainty, and missingness. |
| Primary specialist owner | The one skill responsible for the visual reasoning. |
| Supporting specialist skills | Integration, export, accessibility, testing, or renderer skills that also matter. |
| Encoding and layout | Chart family, marks, scales, labels, keys, annotation, and shared color semantics. |
| Interaction or fallback | Hover, selection, scroll state, reduced-motion state, static export, and mobile adaptation. |
| Accessibility | Alt text or long description, keyboard path, contrast, color redundancy, and tabular equivalent when needed. |
| QA check | The concrete test, screenshot, data invariant, export review, or human visual review that proves it worked. |
| Fresh-pass status | Delegated fresh agent, local fresh specialist pass, or not needed with reason. |

The mini-brief should be short enough to fit in a storyboard row, but complete enough that another agent or engineer could design the visual layer without inheriting unrelated story context.

## Specialist Routing Map

- Use `../../skills/visualization-strategy-and-critique/SKILL.md` for chart choice, hierarchy, narrative claim, critique, and whether the layer should exist.
- Use `../../skills/d3-data-visualization/SKILL.md` for bespoke SVG marks, labels, annotation, axes, transitions, and crisp vector polish.
- Use `../../skills/canvas2d-data-visualization/SKILL.md` for dense flat marks, swarm-like point clouds, heat strips, repeated microcharts, fast redraws, and custom hit testing.
- Use `../../skills/threejs-data-visualization/SKILL.md` for WebGL, particles, GPU-scale marks, 3D, camera-led surfaces, shader effects, and flow animation.
- Use `../../skills/geospatial-and-cartographic-visualization/SKILL.md` for maps, projections, basemaps, routes, symbol maps, choropleths, slippy maps, and cartographic interactions.
- Use `../../skills/statistical-and-uncertainty-visualization/SKILL.md` for distributions, intervals, confidence, sampling, missingness, outliers, and statistically honest comparison.
- Use `../../skills/react-and-nextjs-data-visualization/SKILL.md` for React or Next.js boundaries, hydration, dynamic imports, component integration, and route-level performance.
- Use `../../skills/typescript-data-visualization-engineering/SKILL.md` for typed data contracts, reusable chart APIs, scene state models, and browser architecture.
- Use `../../skills/scrollytelling-and-parallax-data-visualization/SKILL.md` for scroll-triggered scene states, sticky graphics, media synchronization, reduced-motion scenes, and scroll QA.
- Use `../../skills/accessibility-and-inclusive-visualization/SKILL.md` for text alternatives, contrast, keyboard support, reduced motion, inclusive palettes, and assistive review.
- Use `../../skills/testing-data-visualizations/SKILL.md` for data invariants, component tests, screenshot tests, E2E paths, export checks, and visual regression.
- Use `../../skills/reports-pdfs-and-slide-automation/SKILL.md` for figure packaging, PDF, slides, document composition, asset regeneration, and static figure sequences.

Layered visuals can have one primary owner and several supporting owners. The primary owner protects the visual reasoning. The parent story or report owner protects integration, editorial hierarchy, and consistency.

## Fresh Context And Guarded Delegation

Use a fresh delegated worker or explorer for substantial embedded visualizations only when:

- the runtime supports subagents or fresh agents
- the user has explicitly authorized delegation, parallel agents, or subagent work
- the visual layer is high risk, complex, or likely to suffer from surrounding-story context bleed

Good delegation candidates include dense maps, custom D3 annotations, Canvas or WebGL swarms, statistical uncertainty panels, generated-image overlays with data labels, export-critical figure sets, and any visual layer where a generic card would be a serious loss.

The delegated prompt should include only:

- the mini-brief for the visual layer
- the relevant data contract or small sample
- the target medium and constraints
- acceptance criteria and QA expectations
- the integration boundary or file ownership, when code changes are involved

Do not send the whole story draft unless the layer genuinely needs it. Fresh context is useful because it keeps the specialist from accepting weak encodings, inherited copy, or decorative layout assumptions from the parent deliverable.

The parent story, report, or deck agent remains responsible for:

- integrating the specialist output
- preserving shared encodings and terminology
- aligning typography, color, source notes, and caveats
- checking mobile order, static fallbacks, and export behavior
- performing final editorial and accessibility QA

If delegation is unavailable or not authorized, do the same pass locally: explicitly load the relevant specialist skill before designing that layer, then record the local fresh-pass status in the mini-brief.

## Consistency Across Layers

Composite deliverables need local excellence and global coherence.

- Reuse color semantics, units, baselines, denominators, date formats, and source-note style across layers.
- Keep one meaning per encoding. Do not let red mean risk in one layer and category in another unless the legend and context make that unavoidable.
- Use shared entities, names, geographies, thresholds, and event windows across charts and tables.
- Keep accessibility language consistent: chart type, main takeaway, caveat, and interaction or fallback.
- Ensure every static export, screenshot, slide, or PDF frame preserves the same claim as the interactive version.
- Let simple tables stay simple when lookup is the job, but enrich tables with in-cell graphics when compact comparison matters.

## Review Questions

- Did every meaningful embedded visual layer get inventoried before composition?
- Does each layer have a primary specialist owner and a short mini-brief?
- Did high-risk layers use authorized delegation or an explicit local fresh specialist pass?
- Are generic chart tiles or cards used only where they are the right analytical treatment?
- Are shared encodings, source notes, caveats, and accessibility summaries consistent across layers?
- Does the final story, report, deck, or PDF show visible evidence of specialist guidance in each embedded visualization?
