---
name: visualization-strategy-and-critique
description: Choose, lay out, critique, and explain data visualizations. Use when the user asks what visualization fits a dataset or goal, how a chart, dashboard, operational workspace, UML-like diagram, or software architecture diagram should be composed or interacted with, asks for visual page design, a layout mockup, generated large-screen and mobile concept images, or to be shown what a visualization could look like, when domain-native contextual surfaces or graphical backgrounds may help, when scrollytelling or parallax might be appropriate, wants a critique of an existing visualization, or needs guidance grounded in trusted visualization theory and practice. For advanced visual design or page-layout prompts where composition affects understanding, Codex must generate and show both large-screen and mobile portrait image concepts before implementation or text-only design handoff, plus mobile landscape when needed.
---

# Visualization Strategy and Critique

## Overview

Use this skill when the hardest problem is not rendering marks. The hardest problem is deciding what evidence to show, what comparisons matter, what the audience must understand, how the surface should be composed, and which visual form makes that reasoning easiest.

Treat Tufte, Bertin, Cleveland and McGill, Tukey, Munzner, Few, Cairo, Ware, Shneiderman, Cole Nussbaumer Knaflic, Amanda Cox, Mike Bostock, and Jen Christiansen as working lenses. Use them to make decisions, not to decorate explanations.

Default assumption: the best interface is largely self-explanatory. If the user would need a paragraph or hover-only behavior to grasp the main comparison, simplify the layout, labeling, or default state before adding more prose.

Mobile and large screens are sibling strategy targets. Unless the user explicitly excludes one, choose a reading path and concept direction for both before treating responsive behavior as an implementation detail.

## Default Procedure

1. Define the question, decision, or claim the view must support.
2. Identify the audience and the stakes.
3. Classify the data and the required comparisons.
4. Write the insight title as a testable claim before sketching.
5. Choose the simplest visual form that makes the key comparison easiest to read.
6. For project schedules, roadmaps with task spans, milestones, dependencies, critical path, baselines, or resource plans, use `../gantt-chart-visualization/SKILL.md` before choosing a renderer. Treat MS Project, Primavera, Jira, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, Azure DevOps, CSV, TSV, XLSX, and JSON inputs as source-ingestion problems before chart-design problems.
7. For system structure, workflow, state, dependency, schema, code, or software architecture explanation, use `../uml-and-software-architecture-visualization/SKILL.md` before choosing formal UML, C4, ERD, BPMN, flowchart, swimlane, state machine, network, architecture map, or an interactive diagram renderer.
8. For editorial work, choose the artifact mode before the renderer: data-first chart, generated object marks, illustrated substrate, cartographic flow field, WebGL-accelerated 2D, particle or flow animation, 3D surface, or scrollytelling/parallax sequence.
9. Decide whether a meaningful domain surface should shape the view: field, court, track, floor plan, schematic, route, room, object, terrain, or other graphical context that helps explain position, roles, zones, mechanism, or flow.
10. For editorial infographics, report/deck figures, visual articles, composite layouts, animation, generated imagery, scrollytelling, parallax, or visualization placement inside an existing page, use `../../references/foundations/meaning-preserving-visual-design-workflow.md` and `../../references/foundations/mobile-first-responsive-visualization.md` when composition materially affects understanding. Apply those shared references for required concept generation, large-screen/mobile variants, approval or iteration, semantic design contracts, and implementation deferral.
11. For fictional, synthetic, or illustrative stories, use `../../references/foundations/fictional-data-story-simulation.md` before sketching. Require entity, temporal, spatial or physical, event, outcome, and derived comparison layers.
12. For reports, stories, parallax, editorials, visual articles, or decks with embedded visualizations, use `../../references/foundations/embedded-visualization-self-use.md` before composition. Inventory each visual layer, name the primary specialist owner, write a mini-brief for job, data shape, encoding, interaction, fallback, accessibility, QA, and fresh-pass status, and use authorized delegation or an explicit local specialist pass for substantial layers.
13. Keep labels and keys in the view or immediately beside it so decoding does not require hunting across the page.
14. If using visual references, extract the principle and state the original transformation for this dataset. Do not clone a publication layout, type style, palette, scene, or interaction cadence.
15. Decide what must be visible by default versus revealed interactively.
16. Compose a clear reading order: one focal view, subordinate context, and controls placed near the evidence they affect. On mobile, the main visualization must appear before or alongside settings, and settings must return the user to the affected view after Apply, Cancel, Reset, or close.
17. For operational consoles, architecture explorers, live dashboards, schema/state-machine inspectors, or repeated analytical workspaces, use `../../references/foundations/operational-visualization-workspaces.md` before sketching the shell. Decide the main viewport, outline/control rail, inspector, command/status bar, mobile panel model, default selection, and URL state together.
18. For new implementation work, turn the chart recommendation into a concise technical design that covers simultaneous instance count, renderer fit, performance, and maintenance tradeoffs.
19. For advanced WebGL, 3D, globe, geospatial, terrain, cutaway, particle, scrollytelling, or multi-layer interactive work, use `../../assets/templates/advanced-interactive-visualization-contract.md` after concept approval and before implementation. Require renderer ownership, coordinate-frame checks, mark semantics, interaction states, fallback/render-ready behavior, and QA.
20. Add annotation, narrative, imagery, motion, or small multiples only when they reduce interpretation cost.

## Editorial Infographic Mode

Use `../../references/foundations/editorial-infographic-system.md` when the user asks for an infographic, article visual, publication-quality chart, visual story, executive figure, or non-dashboard explanation.

- Start from the story sentence: what should the reader understand after 10 seconds?
- Replace topic titles with claim titles.
- Design custom composition around the evidence instead of applying a generic chart template.
- Use `../../references/foundations/meaning-preserving-visual-design-workflow.md` and `../../references/foundations/mobile-first-responsive-visualization.md` for concept generation, large-screen/mobile variants, approval gates, semantic contracts, mobile reading paths, touch/keyboard behavior, spotty-connection plans, and capability audits.
- Use annotations to explain turning points, mechanisms, caveats, and consequences.
- Prefer direct labels, small multiples, and focused panels over legends and equal-weight dashboards.
- Use restrained color: neutral context plus one or two intentional accents.
- Include a mobile/narrow version or adaptation rule whenever the output is for web.

Use `../../references/foundations/art-directed-interactive-visual-stories.md` when the user asks for a visually stunning interactive, animation, image generation, WebGL, particles, 3D, illustrated explanation, map-flow story, cutaway, object-based infographic, or anything inspired by major publication visual storytelling.

- Decide what the visual artifact is, not just what chart type it is.
- Treat references as principle studies. Write what was learned, then transform it into a story-specific composition that would not be mistaken for the reference.
- If the answer is imagery or illustration, state what the asset explains and which data layers stay editable.
- If the answer is animation, name the animation verb and provide a reduced-motion fallback.
- If the answer is particles or flow animation, state what one particle represents, what it must not imply, and how the static fallback preserves the claim.
- If the answer is 3D, state which data dimensions justify depth and what the static fallback is.
- If the answer is scrollytelling or parallax, use `../scrollytelling-and-parallax-data-visualization/SKILL.md`, outline the scenes, state what each reveal adds, and decide whether a stepper, small multiples, or static frames would be clearer.
- Add a human visual-review pass: would an editor keep the image, motion, labels, and pacing after novelty fades?

Use `../../references/foundations/fictional-data-story-simulation.md` when the story is invented or simulated.

- Build the simulated-world contract before choosing charts, imagery, animation, or interaction.
- Make sure the data can support multiple visual forms: temporal, spatial or physical, event, outcome, and derived comparison views.
- Label values as fictional or simulated and preserve the seed/regeneration path.
- Treat sparse fictional data as a design blocker, not a copywriting problem.

Use `../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md` when the story involves conflict, occupation, territorial control, civilian harm, displacement, disaster, sanctions, migration, or humanitarian need.

- Build a source and method ledger before sketching the layout.
- Distinguish measured, estimated, and schematic evidence layers in data, labels, and visual styling.
- Keep dates, source notes, attribution, and caveats close to the map states or human-impact values they support.
- Use humane, precise language and avoid decorative violence, team-color framing, or false precision.
- Require a static screenshot or export path that preserves the claim without hover, autoplay, or tactical-map interaction.

## Layout and Interaction Defaults

- Make one question dominant on the surface instead of giving equal emphasis to every chart, card, and control.
- Put legends, filters, toggles, and summaries next to the evidence they affect.
- Use direct labels, embedded keys, and short framing text before resorting to explanatory sidebars or long captions.
- Use domain-native backgrounds only when they add meaning or orientation. If used, keep them visually subordinate and let them inform mark placement, zones, or interaction.
- Use generated images only when they add meaning or orientation. Keep numerical labels and source notes in editable data-bound layers wherever possible, and enforce approved concepts through the shared semantic design contract.
- Use motion as staged explanation, not ambient decoration.
- Use scrollytelling when a linear author-led path helps readers understand staged change. Use a stepper when discrete states, replay, direct access, or known length matter more than scrolling.
- Use WebGL only when scale, interaction, particles, flow, shader effects, or true 3D make the renderer meaningfully better than SVG/DOM or Canvas2D.
- For operational workspaces, keep the main evidence viewport dominant. Use compact rails, command bars, navigation trees, drawers, synchronized inspectors, and active-state summaries instead of stacked card grids.
- Use particles only for flow, direction, accumulation, recency, focus, anomaly, risk, or state. Avoid particles as texture.
- Use hover for preview and selection for commitment; keep essential values and categories visible without pointer precision.
- Use touch-first mobile paths: tap or focus for inspection, step-through controls for dense targets, drag alternatives, explicit pinch/zoom ownership, and no hover-only evidence.
- Add reset paths and obvious escape hatches whenever interaction changes the analytical state.
- For ambitious interactive scenes, define the interaction state machine before coding: default, hover/preview, selected/committed, expanded/detail, paused/idle, loading, fallback, and error states as relevant.

## Chart Selection Heuristics

- Use bars, dots, and tables with in-cell graphics, including sparklines, for precise comparisons across categories.
- Use lines, horizon-like summaries, or small multiples for time and repeated temporal comparison.
- Use Gantt charts for planned schedules where task spans, milestones, dependencies, baselines, critical path, or resources are the main evidence. Prefer milestone timelines, Kanban boards, tables, dependency graphs, calendars, resource timelines, or uncertainty views when those better match the decision.
- Use UML, C4, ERD, BPMN, flowcharts, swimlanes, state machines, sequence diagrams, or dependency diagrams when system relationships, behavior, process, or architecture are the evidence.
- Use scatterplots, density views, and faceted alternatives for relationships and multivariate structure.
- Use histograms, box plots, violin plots, and interval-aware charts for distributions and uncertainty.
- Use maps only when geography is analytically meaningful.
- Use networks, trees, sankeys, or alluvial forms only when structure or flow is the story and simpler alternatives fail.
- Use 3D only when depth or volume is intrinsic to the data.
- Use WebGL-accelerated 2D when density, zoom/pan, GPU picking, particles, shader effects, or smooth animation materially improve analysis.

## Critique Checklist

1. Does the title state a question, claim, or purpose?
2. Is the key comparison assigned the strongest visual encoding?
3. Are scales, baselines, and units trustworthy?
4. Are aggregation, smoothing, uncertainty, and missingness disclosed?
5. Is color semantic or merely decorative?
6. Is the reading order obvious without reading a block of explanatory prose?
7. Can the viewer decode series or symbol meaning without chasing a detached legend?
8. Would direct labels, embedded keys, or small multiples outperform the current composition?
9. Is any interaction hiding something that should be visible immediately?
10. Does the visualization help the viewer decide what matters next?
11. Would the figure still make sense as a static screenshot without hover?
12. Does the mobile reading order preserve the same claim?
13. Does the mobile default view keep the main visualization visible rather than stacking controls first?
14. Are touch, pinch, on-screen keyboard, spotty connection, and permission-gated capability paths accounted for?
15. For operational workspaces, do the outline, filters, visualization, selected state, and inspector stay synchronized across desktop and mobile?
16. Does imagery, illustration, WebGL, particles, 3D, or animation carry analytical meaning?
17. Would the composition still work as a still screenshot?
18. Does the result look edited by a human rather than assembled from equal-weight chart boxes?
19. If generated concepts were used, did the user approve the large-screen and mobile concept set before project changes or implementation code began, and does the implementation preserve the approved semantic design contract, locked elements, and visual composition?
20. For sensitive stories, can a reader tell what is measured, estimated, schematic, disputed, or dated?
21. For composite deliverables, did each embedded chart, map, table-graphic, swarm, distribution, flow layer, particle layer, media overlay, or key get a specialist mini-brief and visible specialist guidance before integration?
22. For advanced interactive work, are renderer ownership, coordinate alignment, visual-effect meanings, picking, fallback rendering, and interaction states documented before implementation?

## Anti-Patterns

- 3D bars, tilted pies, and perspective distortion
- dual axes without extremely careful explanation
- rainbow ramps for ordered magnitude
- dashboards made of equally weighted KPI tiles
- decorative gradients, shadows, and animation that compete with the data
- particle effects, glows, fire, sparkles, or ambient motion that attract attention without explaining evidence
- generated backgrounds with ordinary charts pasted on top
- decorative parallax, scrolljacking, or scroll-scrubbed effects that make the reader fight the browser
- chart galleries masquerading as editorial stories
- contextual backgrounds used as wallpaper without changing interpretation, layout, or orientation
- map-first thinking for non-spatial questions
- interaction used to compensate for a weak default view
- explanatory paragraphs embedded in the chart chrome because the layout is doing too little work
- tooltips used as the primary key or as the only place important values appear

## What Good Looks Like

- The chart answers a concrete question.
- The dominant comparison is visually obvious.
- Supporting context is present but subordinate.
- Any contextual surface is accurate enough for the claim and helps the viewer understand where, how, or why the data occurs.
- Labels and keys stay with the evidence instead of living in a distant legend block.
- Annotation adds meaning, not clutter.
- The layout tells the viewer where to look first and what controls matter.
- The figure survives export, grayscale, resizing, and partial reproduction.
- The implementation approach still looks reasonable when the view is repeated across the actual product surface.

## References

- Shared theory:
  - `../../references/foundations/editorial-infographic-system.md`
  - `../../references/foundations/art-directed-interactive-visual-stories.md`
  - `../../references/foundations/meaning-preserving-visual-design-workflow.md`
  - `../../references/foundations/embedded-visualization-self-use.md`
  - `../../references/foundations/fictional-data-story-simulation.md`
  - `../../references/foundations/sensitive-geopolitical-and-humanitarian-stories.md`
  - `../../references/foundations/theory-and-principles.md`
  - `../../references/foundations/task-abstraction-and-chart-selection.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/operational-visualization-workspaces.md`
  - `../../references/foundations/domain-contextual-surfaces.md`
  - `../../references/foundations/storytelling-annotation-and-critique.md`
  - `../../references/foundations/layout-hierarchy-and-self-explanatory-ux.md`
  - `../../references/foundations/interaction-models-and-progressive-disclosure.md`
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
- Templates:
  - `../../assets/templates/advanced-interactive-visualization-contract.md`
- Skill references:
  - `../gantt-chart-visualization/SKILL.md`
  - `../uml-and-software-architecture-visualization/SKILL.md`
  - `../scrollytelling-and-parallax-data-visualization/SKILL.md`
  - `./references/decision-framing.md`
  - `./references/chart-selection-patterns.md`
  - `./references/critique-lenses.md`
  - `./references/tufte-munzner-cairo-synthesis.md`

## Representative Prompts

- "What visualization should I use for this product analytics question?"
- "Help me visually design this visualization page and generate large-screen and mobile concept images."
- "Critique this chart and tell me the biggest reasoning failures."
- "Should this be a heatmap, dot plot, or small-multiple line chart?"
- "Would this visualization be clearer on a field, court, track, floor plan, or schematic background?"
- "Should this table use sparklines, bars, or standalone charts?"
- "Should this project schedule be a Gantt chart, roadmap, Kanban board, calendar, resource timeline, or dependency graph?"
- "How should I visualize MS Project, Primavera, Jira, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, or Azure DevOps planning data?"
- "Should this system explanation be a UML diagram, C4 view, ERD, BPMN workflow, flowchart, swimlane, state machine, sequence diagram, or dependency graph?"
- "I need a narrative figure for an executive audience, not a dashboard."
- "Should this be a scrollytelling story, parallax timeline, stepper, or small multiples?"
- "Explain why this visualization feels misleading even though the numbers are correct."
