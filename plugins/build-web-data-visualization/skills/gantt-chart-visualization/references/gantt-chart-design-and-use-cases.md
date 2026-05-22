# Gantt Chart Design And Use Cases

## What Problem This Solves

This reference helps decide whether a Gantt chart is the right visualization and what the default reading path should be.

## When To Use It

Use this when the user asks about Gantt charts, timelines with task spans, roadmaps, project schedules, dependencies, critical path, baselines, resources, or schedule risk.

## Good Gantt Use Cases

- Project planning: phases, work breakdown structures, task spans, milestones, dependencies, and deadlines.
- Execution tracking: planned versus actual dates, percent complete, overdue work, and schedule variance.
- Dependency management: blockers, predecessors, successors, lag, lead time, and critical path.
- Resource planning: who or what is assigned over time, workload conflicts, and capacity limits.
- Portfolio and roadmap review: releases, cross-team initiatives, external commitments, and phase overlap.
- High-stakes operational planning: construction, manufacturing, migrations, audits, events, launches, cutovers, clinical or research workflows, and vendor coordination.

## What Good Looks Like

- The left side has a stable task grid with task name, owner/resource, status, progress, dates, and warning fields.
- The right side has a readable time axis with bars aligned to the same rows.
- Milestones are visually distinct from task spans.
- Dependencies are visible on demand or in a restrained default style that does not obscure bars.
- Today, deadlines, non-working time, and baselines are visible when they answer a real question.
- Grouping follows the user's planning hierarchy: WBS, phase, team, release, workstream, resource, location, or priority.
- Color has semantic meaning such as status, criticality, team, risk, or variance. Do not assign a rainbow of task colors unless categories are meaningful and few.
- The default view answers one dominant question: "what is planned," "what is slipping," "what is blocking," "who is overloaded," or "what changed from baseline."

## When Gantt Is A Poor Fit

- Kanban is better when the main job is state flow, WIP limits, handoffs, blocked cards, or throughput.
- A table is better when the user mostly needs exact values, filtering, sorting, and row lookup.
- A calendar is better for appointment-like booking, meetings, shifts, or events without dependency structure.
- A resource timeline is better for rooms, equipment, or staff booking where the resource is the primary axis.
- A milestone timeline is better for executive snapshots with few dates and little task detail.
- A dependency graph is better when dates are unreliable but blocker topology matters.
- A risk or uncertainty view is better when date distributions, confidence, or scenarios matter more than a single schedule.
- A burndown, cumulative flow diagram, or throughput chart is better for agile delivery health.

## Common Reading Tasks

- Find what starts, finishes, or is due this week.
- Compare planned date, baseline date, and actual date.
- Identify the critical path or driving dependencies.
- Find delayed tasks and downstream impact.
- Find tasks with no owner, no dates, impossible ranges, missing predecessors, or overallocated resources.
- Inspect one phase while preserving context of the whole schedule.
- Compare workloads by resource, team, or workstream.
- Export a stakeholder snapshot that still makes sense without interaction.

## Visual Encoding Defaults

- Task bar position: start and finish dates.
- Bar length: duration.
- Filled portion or adjacent label: progress, only when progress is reliable.
- Diamond or narrow marker: milestone.
- Thin secondary bar: baseline.
- Vertical line: today or selected date.
- Stroke, badge, or icon: risk, constraint, missed deadline, or manually scheduled task.
- Link lines: dependencies, preferably muted by default and emphasized on selection.
- Row indentation: hierarchy or WBS.
- Banding or subtle background: weekends, holidays, sprint windows, releases, or non-working periods when needed.

## Pitfalls

- Showing every dependency line at full opacity in a dense schedule.
- Treating issue-created and issue-closed dates as a planned Gantt schedule.
- Hiding task names, dates, or status behind hover.
- Using color only for owner when the decision is about risk or critical path.
- Letting parent rows look editable when they are computed rollups.
- Showing precise dates for estimates that are still rough or scenario-based.
- Mixing date-only exports and datetime APIs without a timezone policy.
- Calling a milestone-only roadmap a Gantt chart when there are no task spans.

## Source Links

- [Atlassian Gantt chart overview](https://www.atlassian.com/agile/project-management/gantt-chart)
- [monday.com Gantt chart view](https://support.monday.com/hc/en-us/articles/360015643840-The-Gantt-Chart-View-and-Widget)
- [Microsoft Project critical path](https://support.microsoft.com/en-us/office/show-the-critical-path-of-your-project-in-project-8dc6b030-e2d5-45d2-8e8e-89b30c3a1eac)
- [Smartsheet dependencies and critical path](https://help.smartsheet.com/articles/765727-enabling-dependencies-using-predecessors)
