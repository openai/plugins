# Gantt Interaction Patterns

## What Problem This Solves

This reference defines useful Gantt interactions without turning the chart into a maze of hidden states.

## When To Use It

Use this for interactive, editable, exploratory, dashboard, or product Gantt surfaces.

## Layout Contract

- Use a frozen task grid on the left and a horizontally scrollable timeline on the right.
- Keep row heights stable so bars, labels, dependency anchors, focus rings, and hover states cannot shift the layout.
- Keep time-axis controls near the timeline: day/week/month/quarter/year, today, fit, and date range.
- Place row filters, grouping, and search near the task grid.
- Keep selection details in a side panel, drawer, or row expansion so hover is only preview.
- Preserve vertical row alignment between grid and timeline during virtualization.

## Navigation

- Horizontal pan by scrollbar, trackpad, drag handle, or timeline minimap. Do not trap page scrolling without a clear control.
- Zoom by explicit controls first. Wheel or pinch zoom should be opt-in and reversible.
- Provide `today`, `fit project`, `selected task`, and `reset filters` controls.
- Support expand/collapse for hierarchy and group rows.
- Preserve selection and scroll position when filters or zoom levels change where possible.

## Inspection

- Hover can preview start, finish, duration, owner, status, progress, and key dependencies.
- Click or keyboard selection commits the task and exposes details, source links, comments, audit trail, and dependency impact.
- Dependency inspection should highlight predecessor and successor chains without lighting up the entire graph.
- Critical path, baselines, non-working time, and dependencies should be toggles when they make the default view too dense.

## Editing

- Drag to move a task only when the user has permission and the scheduling engine can validate the change.
- Resize start or finish only when date changes are allowed and duration rules are clear.
- Dependency editing must show valid drop targets, dependency type, lag, and cycle prevention.
- Batch edits need preview and undo because schedule changes can shift many tasks.
- Parent rows should not be directly edited when they are rollups from child tasks.
- Manual scheduling, fixed dates, constraints, calendars, and locked tasks need visible affordances before a drag starts.

## Validation And Conflict Behavior

- Block or warn on dependency cycles, missing targets, invalid ranges, and impossible calendar dates.
- Explain when a move shifts downstream tasks, violates a deadline, or changes the critical path.
- Show source-system sync failures separately from visual validation failures.
- For optimistic updates, keep a pending state and a rollback path.
- For collaborative editing, handle stale schedule versions and conflicts explicitly.

## Common Controls

- Search by task name, ID, assignee, owner, milestone, source key, or WBS.
- Filter by owner, team, phase, status, risk, critical path, date range, dependency problem, and unscheduled tasks.
- Sort by WBS, start date, finish date, owner, status, slack, variance, or priority.
- Group by phase, workstream, team, resource, release, location, or source system.
- Toggle dependencies, baselines, critical path, labels, non-working time, completed tasks, and resource workload.
- Export current view, selected range, full schedule, PDF/image snapshot, CSV/TSV data, or source-system handoff file when supported.

## Mobile And Narrow Layout

- Do not squeeze an enterprise Gantt into an unreadable miniature.
- Prefer a list of phases or tasks with compact inline bars and a detail view.
- Use a milestone summary or selected-time-window view for stakeholder reading.
- Keep date labels and owner/status visible without hover.
- Use horizontal timeline scroll only when the target users actually need schedule editing on narrow screens.

## Common Mistakes

- Making every dependency line visible all the time.
- Making hover the only way to read dates or blockers.
- Allowing drag edits before defining scheduling rules and undo.
- Using custom wheel behavior that fights browser scroll.
- Showing dense labels inside bars that clip at small durations.
- Updating source data on every pointer move instead of on commit.
- Hiding permissions, locks, and calculated rollups until after edit failure.

## Source Links

- [DHTMLX Gantt docs](https://docs.dhtmlx.com/gantt/)
- [Bryntum Gantt features](https://bryntum.com/products/gantt/features/)
- [Highcharts Gantt docs](https://www.highcharts.com/docs/gantt/getting-started-gantt)
- [Frappe Gantt docs](https://frappe.io/gantt)
- [FullCalendar resource timeline](https://fullcalendar.io/docs/timeline-view)
