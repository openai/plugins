---
name: google-sheets-chart-builder
description: Design, create, and revise Google Sheets charts with better chart-spec recall and editing discipline. Use when the user wants to add a chart to a sheet, choose the right chart type for existing data, repair a broken chart, update a chart's data series, or reposition or resize a chart after creating it.
---

# Google Sheets Chart Builder

Use this skill when the chart itself is the task.

Read `./references/chart-recipes.md` before the first chart write. The point is to refresh chart request shapes and a few non-obvious API constraints before building or editing.

## Workflow

1. Ground the chart in the live sheet first: exact source tab, domain column, series columns, headers, and whether the data is contiguous.
2. Choose the simplest chart type that matches the table shape and user intent.
3. Draft one chart spec first, using a clean anchor position that will not collide with existing content.
4. If the chart needs revision, update the chart spec deliberately rather than trying to patch a tiny nested fragment from memory.
5. Treat chart content changes and chart position changes as separate operations.

## Output Conventions

- Name the source sheet and the exact domain and series ranges.
- State the chosen chart type and why it fits the data.
- For edits, state whether you are changing the chart spec, the chart position, or both.

## References

- For chart-type heuristics, request-shape reminders, and official Google Sheets docs links, read `./references/chart-recipes.md`.
