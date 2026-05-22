# Gantt Data Contracts And Integrations

## What Problem This Solves

This reference defines the normalized model and integration boundaries for Gantt chart data.

## When To Use It

Use this when building a reusable Gantt component, adapter, API, fixture, or sync workflow.

## Canonical Normalized Model

Use explicit objects instead of passing raw source rows into render code.

```ts
type GanttTask = {
  id: string;
  sourceId: string;
  sourceSystem: string;
  name: string;
  parentId?: string;
  wbsCode?: string;
  type: "task" | "milestone" | "summary" | "external" | "placeholder";
  start?: string;
  end?: string;
  duration?: number;
  durationUnit?: "minutes" | "hours" | "days" | "weeks";
  progress?: number;
  status?: string;
  ownerIds?: string[];
  resourceIds?: string[];
  calendarId?: string;
  deadline?: string;
  baselineStart?: string;
  baselineEnd?: string;
  actualStart?: string;
  actualEnd?: string;
  constraintType?: string;
  constraintDate?: string;
  isCritical?: boolean;
  slack?: number;
  riskLevel?: string;
  url?: string;
  provenance: Record<string, string>;
  diagnostics?: string[];
};
```

```ts
type GanttDependency = {
  id: string;
  sourceId?: string;
  predecessorId: string;
  successorId: string;
  type: "FS" | "SS" | "FF" | "SF";
  lag?: number;
  lagUnit?: "minutes" | "hours" | "days" | "weeks";
  isCritical?: boolean;
  isInferred?: boolean;
  provenance: Record<string, string>;
  diagnostics?: string[];
};
```

Also model:

- `GanttResource`: person, team, role, equipment, room, vendor, or capacity pool.
- `GanttCalendar`: working days, working hours, exceptions, holidays, timezone, and source calendar.
- `GanttBaseline`: named baseline with date, source, and optional per-task baseline values.
- `GanttViewState`: visible time range, zoom level, expanded groups, filters, sort, selection, toggles, and source snapshot version.
- `GanttDiagnostics`: adapter-level warnings, dropped rows, invalid links, inferred fields, timezone policy, and export limits.

## Provenance Rules

- Every mapped field should know where it came from: source field ID, display name, API path, file column, or derived rule.
- Preserve source URLs and IDs so selections can deep-link back to the system of record.
- Mark inferred fields explicitly. Examples: deriving a milestone from equal start/end dates, deriving end from start plus duration, or treating a custom "Target end" field as finish.
- Keep date parsing assumptions visible: locale, timezone, date-only handling, inclusive/exclusive finish policy, and business calendar.
- Keep source filters and view constraints visible when importing a view export.

## Adapter Boundaries

- Source adapter: fetches or reads raw data, discovers schema, maps fields, validates references, and emits normalized data plus diagnostics.
- Schedule engine or service: computes rollups, critical path, calendar-aware duration, dependency shifts, and resource allocation when the product owns scheduling behavior.
- Renderer: draws normalized tasks, links, resources, calendars, and warnings. It should not know Jira field IDs or Project XML element names.
- Sync layer: persists edits back to the source system only after validation and user confirmation.

## Import Contracts

- Accept incomplete schedules and report what cannot be rendered.
- Keep unscheduled tasks in the grid with a clear "no schedule dates" state.
- Treat parent date rollups as computed unless explicitly editable.
- Treat missing dependency targets as diagnostics, not silent drops.
- Include source snapshot metadata: exported at, imported at, source query, view name, project ID, user, timezone, and permission scope when available.
- For CSV and spreadsheets, require a column mapping screen or documented mapping table.

## Edit And Sync Contracts

- Editing a date should say whether it changes only the local view, the normalized schedule, or the source system.
- Commit drag and resize edits on pointer up, not during every pointer move.
- Validate permissions before exposing edit handles.
- Return clear validation results: accepted, accepted with downstream shifts, rejected, pending sync, or source conflict.
- Log dependency changes with predecessor, successor, type, lag, and reason.
- Preserve source-system optimistic concurrency tokens or version fields when available.
- Provide rollback, undo, or "discard local changes" for sync failures.

## Integration Patterns

- Read-only reporting: source adapter plus normalized snapshot plus deterministic export.
- Embedded product widget: normalized API plus persisted view state and deep links.
- Editable project planner: scheduling engine, transactional edits, audit trail, and source sync.
- Portfolio rollup: multiple source adapters normalize into shared tasks/resources, but keep source-specific semantics and confidence visible.
- Hybrid source of truth: one system owns tasks, another owns resources, another owns calendar exceptions. Make ownership explicit.

## Common Mistakes

- Using row index as task ID.
- Merging multiple source systems without preserving source namespace.
- Treating parent rows, epics, issues, and activities as the same type without hierarchy metadata.
- Letting render logic parse dates, dependency strings, or source API payloads.
- Silently making all dependencies finish-to-start.
- Writing edits back to source systems without preserving custom fields, calendars, and permissions.
- Ignoring inclusive finish dates in day-based exports.

## Source Links

- [Microsoft Project XML Project element structure](https://learn.microsoft.com/en-us/office-project/xml-data-interchange/project-elements-and-xml-structure)
- [Jira issue fields API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/)
- [Jira issue links API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-links/)
- [GitHub GraphQL ProjectV2 objects](https://docs.github.com/en/graphql/reference/objects)
- [Smartsheet predecessor schema](https://developers.smartsheet.com/api/smartsheet/openapi/schemas/predecessor)
- [Azure DevOps Analytics data model](https://learn.microsoft.com/en-us/azure/devops/report/extend-analytics/data-model-analytics-service)
