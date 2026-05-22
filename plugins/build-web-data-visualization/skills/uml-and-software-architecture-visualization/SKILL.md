---
name: uml-and-software-architecture-visualization
description: Design, critique, read, write, render, and implement UML and UML-like software diagrams. Use when the user mentions UML, sequence diagrams, class diagrams, activity diagrams, state machines, use case diagrams, component diagrams, deployment diagrams, object diagrams, package diagrams, profile diagrams, timing diagrams, communication diagrams, interaction overview diagrams, composite structure diagrams, ERDs, database schema diagrams, C4, BPMN, swimlanes, flowcharts, network diagrams, application architecture diagrams, software architecture diagrams, diagram-as-code, model-as-code, XMI, UMLDI, PlantUML, Mermaid, Graphviz DOT, D2, Structurizr, DBML, diagrams.net/draw.io, Kroki, or interactive diagram editors and explorers.
---

# UML and Software Architecture Visualization

## Overview

Use this skill when the visualization is about system structure, behavior, process, state, data models, dependencies, architecture, or interactions rather than numeric charting alone. The job is to choose the clearest notation, source format, renderer, and interaction model for the audience.

Default assumption: use formal UML when notation precision, methodology alignment, or model interchange matters. Use a UML-like diagram such as C4, ERD, BPMN, flowchart, swimlane, dependency graph, or architecture map when that communicates the user's actual question with less ceremony.

When the main challenge is automatic placement, crossing reduction, routing style, overlap removal, or layout stability rather than notation selection, route through `../node-link-and-diagram-layout/SKILL.md` before locking in a renderer.

For browser or app diagrams, use `../../references/foundations/mobile-first-responsive-visualization.md` so mobile portrait, optional landscape, touch, keyboard, search, and main-diagram visibility are planned before implementation.

For architecture consoles, schema explorers, state-machine inspectors, dependency maps, or other dense repeated-use diagram products, also use `../../references/foundations/operational-visualization-workspaces.md` so the shell, outline, inspector, command bar, mobile panels, URL state, and pan/zoom behavior are designed as part of the diagram.

## Core Workflow

1. Identify the modeling job:
   - static structure, runtime interaction, workflow, lifecycle state, deployment topology, dependency graph, database schema, architecture context, or implementation detail
2. Identify the audience:
   - business stakeholder, analyst, product owner, architect, developer, operator, auditor, or onboarding reader
3. Choose formal UML or a UML-like alternative:
   - formal UML for standard semantics, XMI, UMLDI, or tooling interchange
   - C4 for layered software architecture communication
   - ERD or DBML for relational schemas and data model documentation
   - BPMN or swimlane activity diagrams for business processes and handoffs
   - flowcharts or state machines for control flow and lifecycle logic
   - network or dependency diagrams for topology, coupling, and impact analysis
4. Select the diagram family and scope:
   - one primary question per diagram
   - one abstraction level per view unless the user explicitly needs a bridge diagram
   - source IDs, names, stereotypes, technologies, and relationship labels preserved when available
5. Choose the source or interchange format:
   - XMI/UMLDI for formal model exchange
   - PlantUML, Mermaid, DOT, D2, Structurizr DSL, DBML, or BPMN XML for source-backed documentation and CI
   - JSON graph models when building a product renderer or interactive editor
6. Choose the layout strategy when automatic arrangement matters:
   - route to `../node-link-and-diagram-layout/SKILL.md` for layered, tree, force, radial, planarization, routing, overlap, and stability decisions
   - preserve source order, port order, and grouping constraints when they are semantically meaningful
7. Choose the renderer or editor stack:
   - static image generation, documentation embed, notebook/script, web component, interactive explorer, or editable diagramming product
8. Define the normalized model contract before rendering:
   - nodes, edges, compartments, ports, lanes, groups, hierarchy, labels, metadata, source IDs, layout hints, and validation diagnostics
9. Plan export, accessibility, and tests:
   - SVG/PNG/PDF/HTML outputs, text alternatives, keyboard paths, deterministic layout fixtures, semantic validation, and visual regression where layout matters
10. For multi-view architecture explorers, choose a calm default reading state:
   - show one dense subdiagram at a time, especially for schemas and state machines
   - keep side panels as compact controls and outlines, not nested cards
   - render all relationships quietly by default, then emphasize hover and selection paths
   - use a synced navigation tree so users can jump among topology entities, tables, states, and transitions without hunting inside the canvas
   - prefer scrollable intrinsic canvases over shrinking node text below readable size
   - on mobile, show a focused default subdiagram or outline plus detail path instead of stacking every control above the diagram
   - use mobile landscape for wide schema, sequence, or dependency inspection when it improves legibility, while preserving a useful portrait entry point
   - use compact command bars, synchronized outlines, central scrollable canvases, and inspector rails instead of equal-weight cards

## Diagram Selection Defaults

- Sequence diagram: message order across actors, services, or objects.
- Communication diagram: collaboration topology when the object network matters as much as ordering.
- Activity diagram or swimlane: workflow, branching, parallel work, ownership, and handoffs.
- State machine: lifecycle rules, event-driven behavior, allowed transitions, and invalid states.
- Class or object diagram: code-level structure, interfaces, relationships, snapshots, and domain object shape.
- Component, package, deployment, or C4 diagram: architecture structure at the right abstraction level.
- Use case diagram: actor goals and system boundary, usually early requirements or stakeholder alignment.
- ERD, DBML, or database schema diagram: tables, relationships, keys, constraints, and schema ownership.
- BPMN: business process execution semantics, events, gateways, pools, tasks, and process interchange.
- Flowchart: lightweight control flow when UML activity or BPMN would be too formal.
- Network or dependency diagram: topology, coupling, blast radius, graph traversal, and modularity.

## Stack Defaults

- Documentation-first static diagrams: prefer PlantUML or Mermaid, with SVG export when labels must stay crisp.
- Formal UML exchange: use XMI plus UMLDI where diagram geometry must travel with model semantics; expect vendor-specific gaps.
- Architecture model-as-code: prefer Structurizr DSL for C4; use C4-PlantUML or Mermaid C4 when docs integration is more important than a reusable model.
- Database schema diagrams: prefer DBML, SQL-derived ERD tooling, Mermaid ER, or PlantUML IE/ER.
- Diagram source rendering: use Mermaid, PlantUML, D2, Graphviz DOT, Structurizr DSL, DBML, BPMN XML, or Kroki when text DSL rendering is needed.
- TypeScript or web rendering: use Mermaid for simple docs, React Flow for editable node-edge UIs, Cytoscape.js for graph analysis and larger networks, Sprotty for model-driven diagram tools, JointJS or GoJS for full-featured diagram editors, and ELK or Dagre for auto-layout.
- Bespoke SVG/D3: use only when the diagram needs custom annotation, visual polish, or product-specific composition that diagram DSLs cannot express cleanly.
- For dense topology, ERD, or state-machine explorers, route layout choice through `../node-link-and-diagram-layout/SKILL.md`, then prefer ELK or Dagre when adding a dependency is acceptable; if staying bespoke, implement an explicit layered layout, stable ranks, non-overlap spacing, routed edges, and focus-state filtering instead of relying on hand-placed nodes.

## Reference Guide

- Read `references/uml-diagram-types-and-selection.md` for formal UML diagram types, alternatives, and selection heuristics.
- Read `../node-link-and-diagram-layout/SKILL.md` when the main issue is node placement, crossing reduction, routing style, or overlap management.
- Read `references/formats-and-interchange.md` before reading, writing, converting, or round-tripping diagram formats.
- Read `references/typescript-web-rendering.md` for browser, TypeScript, React, and interactive renderer choices.
- Read `references/interactive-diagram-patterns.md` before designing interactive explorers or diagram editors.
- Read `references/quality-accessibility-export-testing.md` for semantic checks, accessibility, export, and QA.

## Output Expectations

- State the recommended diagram type and one fallback, with the reason tied to audience and modeling job.
- State whether the output is formal UML, UML-like, architecture model-as-code, graph visualization, or an editable diagram product.
- Identify the source format, renderer, export path, and any required conversion or validation.
- For generated diagrams, preserve source IDs and call out inferred relationships rather than presenting them as source truth.
- For interactive diagrams, define selection, pan/zoom, search, filtering, drill-down, editing, layout recalculation, keyboard access, export, and source round-tripping.
- For architecture views, keep abstraction levels consistent and label relationships with verbs or data/protocol semantics.
- For class and schema diagrams, control detail level so attributes, methods, constraints, and relationships do not overwhelm the primary question.
- For ERDs and database schemas, route foreign keys in dedicated gutters or ports; never let connectors run underneath table boxes or column text.
- Include a testing and accessibility plan when the diagram is part of a product surface or durable documentation workflow.
- For mobile diagrams, state portrait and optional landscape behavior, touch/pan/zoom ownership, search or step-through path, keyboard-open behavior, and how controls return users to the diagram.
- For explorer-style diagram products, state the workspace shell, navigation tree, default selection, inspector synchronization, URL state, pan/zoom/reset controls, and mobile command-panel behavior.

## Adjacent Skills

- Use `../visualization-strategy-and-critique/SKILL.md` when deciding whether a UML-like diagram is the right visual form.
- Use `../node-link-and-diagram-layout/SKILL.md` for graph-family classification, layout algorithms, routing, overlap removal, and stability.
- Use `../typescript-data-visualization-engineering/SKILL.md` for typed graph models, renderer contracts, and browser architecture.
- Use `../react-and-nextjs-data-visualization/SKILL.md` for React or Next.js integration.
- Use `../d3-data-visualization/SKILL.md` for bespoke SVG geometry, annotation, and polish.
- Use `../accessibility-and-inclusive-visualization/SKILL.md` for text alternatives, keyboard paths, contrast, and export accessibility.
- Use `../testing-data-visualizations/SKILL.md` for visual regression, interaction, and export test strategy.
- Use `../reports-pdfs-and-slide-automation/SKILL.md` for PDFs, decks, and document embedding.
- Use `../../references/foundations/mobile-first-responsive-visualization.md` for mobile diagram layout, touch, keyboard, and responsive QA.
- Use `../../references/foundations/operational-visualization-workspaces.md` for architecture consoles, schema explorers, state-machine inspectors, and repeated-use diagram workspaces.

## Representative Prompts

- "Choose the right UML or UML-like diagram for this system, process, or data model."
- "Read this XMI and summarize the class model."
- "Create a sequence diagram for OAuth login."
- "Make an interactive React dependency diagram."
- "Visualize my PostgreSQL schema."
- "Turn this PostgreSQL schema into an ERD or DBML diagram."
- "Which diagram should explain this checkout workflow?"
- "Compare Mermaid, PlantUML, Graphviz, D2, and Structurizr for this documentation site."
- "Make a state machine diagram and test invalid transitions."
- "Design a C4 model for this application architecture."
