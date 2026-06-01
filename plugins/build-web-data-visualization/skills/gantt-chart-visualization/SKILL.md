---
name: gantt-chart-visualization
description: Design, critique, route, and implement Gantt charts and schedule visualizations. Use when the user mentions Gantt charts, project schedules, roadmaps with task spans, milestones, dependencies, predecessors, critical path, baselines, WBS, resource plans, capacity timelines, MS Project, Primavera P6, Jira Advanced Roadmaps, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, Azure DevOps iterations, or importing/exporting project-management data for a timeline chart.
---

# Gantt Chart Visualization

## Overview

Use this skill when work is organized around time spans, milestones, dependencies, resources, or schedule risk. A Gantt chart is a product surface as much as a chart: it usually combines a task grid, a calendar axis, bars, milestones, dependency links, editing rules, and integration with a project-management source of truth.

Default assumption: recommend a Gantt chart only when the schedule itself is the evidence. If the user mainly needs flow state, task ownership, ranking, issue status, or calendar booking, consider Kanban, tables, milestone timelines, dependency graphs, resource timelines, or uncertainty views first.

Gantt charts are wide by nature. Use `../../references/foundations/mobile-first-responsive-visualization.md` so mobile portrait gets a usable summary or focused slice, and mobile landscape is considered when horizontal schedule inspection matters.

## Core Workflow

1. Classify the scheduling question:
   - planned schedule, actual lifecycle timeline, roadmap, resource plan, capacity view, baseline variance, critical-path review, or stakeholder snapshot
   - whether the user needs read-only explanation, exploratory analysis, or editable project planning
2. Inspect the source before designing:
   - true schedule engine, task tracker, roadmap view, resource calendar, static export, or visual artifact
   - native fields, custom fields, date-only versus datetime values, timezone policy, hierarchy, dependency semantics, calendars, and permissions
   - provenance for every mapped field and any inferred value
3. Normalize into a Gantt model:
   - tasks, hierarchy or WBS, start, end, duration, progress, status, assignee or resource, milestones, dependencies, baselines, calendars, constraints, estimates, actuals, source IDs, and source confidence
4. Decide whether Gantt is the right surface:
   - use Gantt when time spans and dependency or resource reasoning drive the decision
   - use a milestone timeline for executive summaries with few dates
   - use Kanban for workflow state and throughput
   - use a table when lookup and exact fields dominate
   - use a dependency graph when structure matters more than dates
   - use a calendar or resource timeline for booking without project dependencies
   - use uncertainty views when date risk is probabilistic or estimates are still unstable
5. Design the default view:
   - frozen task grid plus calendar axis
   - today marker, visible scale, weekends or non-working time when meaningful
   - clear bars, milestones, dependency links, baselines, progress, and critical-path or risk styling
   - row grouping, hierarchy, and direct labels that work without hover
   - mobile portrait summary or focused default that does not shrink every row into illegibility
   - mobile landscape behavior when wide timeline reading, dependency tracing, or editing is important
6. Define the interaction contract:
   - zoom and pan, row virtualization, expand/collapse, search, filter, sort, hover preview, committed selection, keyboard navigation, drag/resize, dependency editing, undo/redo, export, and deep links
   - touch targets, drag alternatives, keyboard-open search/filter behavior, and settings-return behavior on mobile
7. Choose the renderer and library against real scale:
   - rows, visible time range, dependency count, editability, instance count, export requirements, and source-system sync needs
8. Plan testing and release gates:
   - data adapter tests, date/time fixtures, dependency graph validation, visual states, accessibility, export, and E2E scheduling workflows

## When To Use Gantt

- Project schedules with tasks that have start and finish dates.
- Work breakdown structures, phases, releases, epics, construction schedules, manufacturing plans, implementation plans, launch plans, and migration cutovers.
- Dependency chains where slippage affects downstream work.
- Critical-path, float, baseline, deadline, or variance analysis.
- Resource allocation, capacity planning, or workload conflicts over time.
- Cross-team roadmaps when the question is "what happens when" rather than "what status is this in."
- Schedule imports from MS Project, Primavera P6, Jira Advanced Roadmaps, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, Azure DevOps, or CSV/XLSX exports.

## When Not To Use Gantt

- Small or highly fluid work where a simple list, table, or Kanban board is clearer.
- Issue queues where status, priority, owner, or SLA matters more than planned span.
- Executive summaries with only releases or launch dates; use a milestone timeline or roadmap.
- Booking, appointments, or shift planning without task dependencies; use a calendar or resource timeline.
- Pure dependency reasoning without reliable dates; use a graph or matrix.
- Probabilistic schedules or early estimates where uncertainty is the main story; use interval, scenario, or risk views.
- Actual lifecycle analysis based only on created, started, and closed timestamps unless the user explicitly asks for actual flow history instead of a planned schedule.

## Stack Selection

- Enterprise editable schedule: use Bryntum Gantt, DHTMLX Gantt, Kendo UI Gantt, Syncfusion Gantt, or a comparable scheduling component when dependency editing, calendars, baselines, critical path, resource views, undo, import/export, and scheduling rules are product requirements.
- Lightweight display or reporting: use Highcharts Gantt, Frappe Gantt, Plotly timelines, Observable Plot, or similar when the view is mostly read-only and the schedule semantics are already computed.
- Resource booking or team availability: use FullCalendar resource timeline or a scheduler-style component when resources and calendar slots matter more than WBS scheduling.
- Small editorial schedule: use D3/SVG or a declarative grammar when labels, annotation, vector export, and precise composition matter.
- Large dense product surface: use a virtualized hybrid layout with HTML for grid text, SVG or Canvas for bars and dependency links, and Canvas for dense bar/link layers when DOM cost dominates.
- Avoid raw WebGL unless mark count, continuous pan/zoom, GPU picking, or custom shader effects make Canvas and DOM impractical.

## Reference Guide

- Read `references/gantt-chart-design-and-use-cases.md` for chart-fit decisions, use cases, and alternatives.
- Read `references/gantt-interaction-patterns.md` for interactive product behavior and editing contracts.
- Read `references/gantt-api-and-export-format-ingestion.md` before mapping MS Project, Primavera, Jira, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, Azure DevOps, CSV, TSV, XLSX, JSON, PDF, or image exports.
- Read `references/gantt-data-contracts-and-integrations.md` when defining adapters, normalized schemas, source provenance, sync, or product API contracts.
- Read `references/gantt-performance-and-rendering.md` before choosing SVG, Canvas, hybrid rendering, virtualization, or enterprise libraries for large schedules.
- Read `references/gantt-accessibility-export-and-testing.md` for keyboard navigation, screen-reader fallbacks, export, fixtures, and release gates.

## Output Expectations

- State whether Gantt is the primary recommendation or name the better alternative.
- State whether the source is planned schedule data, actual lifecycle data, a roadmap snapshot, a resource calendar, or a static visual artifact.
- Identify which fields are trusted, mapped, inferred, or missing.
- Include the canonical schedule model, minimum interactions, stack choice, performance assumptions, accessibility plan, and export path.
- For external sources, preserve source IDs and call out ambiguous custom fields instead of silently treating them as schedule truth.
- For editable schedules, call out validation and conflict behavior for drag, resize, dependency changes, calendars, baselines, and sync failures.
- For mobile, call out portrait summary or focused slice, landscape support if needed, touch/editing alternatives, keyboard behavior, and offline/stale sync behavior for remote schedules.

## Shared References

- `../../references/foundations/mobile-first-responsive-visualization.md`

## Representative Prompts

- "Should this project data be a Gantt chart, roadmap, Kanban board, or calendar?"
- "Design an interactive Gantt chart for 10,000 construction activities."
- "Map this MS Project XML export into a web Gantt data model."
- "Read a Jira Advanced Roadmaps CSV and decide what fields are safe to show in a timeline."
- "Turn GitHub Projects fields into a release roadmap without inventing dates."
- "Show critical path, dependencies, and baseline variance for this schedule."
- "Choose between DHTMLX, Bryntum, Highcharts Gantt, Frappe Gantt, FullCalendar, D3, and Canvas."
- "Test a Gantt chart with dependency cycles, missing predecessors, timezone edges, and export snapshots."
