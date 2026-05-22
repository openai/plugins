# Chart Selection Patterns

## What Problem This Solves

This reference maps recurring analytical tasks to reliable chart families.

## When to Use It

Use this when the user is deciding between bars, dots, lines, heatmaps, small multiples, tables, maps, or more complex structures.

## Key Takeaways

- Use bars and dots for precise category comparison.
- Use lines and small multiples for time-based comparison.
- Use tables with embedded cues such as bars, dots, and sparklines when exact values or compact row-wise trend comparison matter.
- Use Gantt charts when the task is project scheduling: planned start/end spans, milestones, dependencies, predecessors, critical path, baselines, WBS, or resource allocation over time.
- Use milestone timelines instead of Gantt charts when the data has only key dates and no meaningful task spans.
- Use Kanban, tables, calendars, dependency graphs, resource timelines, or uncertainty views when workflow state, lookup, booking, topology, capacity, or risk distributions matter more than planned schedule bars.
- Use UML, C4, ERD, BPMN, flowcharts, swimlanes, state machines, sequence diagrams, or dependency diagrams when the evidence is system structure, process, state, interaction, database schema, code shape, or architecture.
- Use scatterplots and density views for relationships.
- Use maps only when location is part of the reasoning.

## Common Mistakes

- Using pies for precise comparison.
- Choosing a map when a sorted bar chart would be clearer.
- Choosing a network when grouped tables or matrices would explain more.
- Choosing a Gantt chart for issue status or task ownership when dates and dependencies are not the main evidence.
- Choosing a class diagram for architecture communication when a C4 container/component view or dependency graph would be clearer.
- Choosing a generic flowchart when BPMN semantics, swimlane ownership, or state-machine transition validity is the main point.
- Treating created/closed timestamps as planned schedule dates without saying the view is an actual lifecycle timeline.
- Pulling the key away from the chart so the viewer has to bounce between evidence and legend.

## Adjacent Skills

- `../SKILL.md`
- `../../gantt-chart-visualization/SKILL.md`
- `../../uml-and-software-architecture-visualization/SKILL.md`
- `../../geospatial-and-cartographic-visualization/SKILL.md`

## Source Links

- [From Data to Viz](https://www.data-to-viz.com/)
- [FT Visual Vocabulary](https://github.com/ft-interactive/visual-vocabulary)
- [Datawrapper Academy](https://academy.datawrapper.de/)
- [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1/About-UML)
- [C4 model diagrams](https://c4model.com/diagrams)
- [Atlassian Gantt chart overview](https://www.atlassian.com/agile/project-management/gantt-chart)
