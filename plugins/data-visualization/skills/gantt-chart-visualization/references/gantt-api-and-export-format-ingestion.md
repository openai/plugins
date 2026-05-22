# Gantt API And Export Format Ingestion

## What Problem This Solves

This reference helps agents read common project-management APIs and exports before mapping them into a Gantt chart.

## When To Use It

Use this before turning MS Project, Primavera, Jira, GitHub Projects, Smartsheet, monday.com, Asana, ClickUp, Azure DevOps, CSV, TSV, XLSX, JSON, PDF, SVG, PNG, or screenshot data into a schedule visualization.

## Source Classification

Classify the source before mapping fields:

- True schedule engine: supports activities/tasks, calendars, dependencies, constraints, resources, baselines, and scheduling rules.
- Task tracker: tracks work items with status, owner, dates, labels, comments, and maybe custom fields.
- Roadmap view: timeline-oriented snapshot, often filtered and less complete than the source system.
- Resource calendar: resource-first booking or availability schedule.
- Static export: CSV, TSV, XLSX, JSON, or printed report generated from one view.
- Visual artifact: PDF, PNG, SVG, screenshot, or slide image. Treat as visual evidence, not reliable structured schedule data.

## Ingestion Workflow

1. Identify source system, export format, export date, permissions, visible filters, timezone, locale, and whether the data is complete or view-limited.
2. Discover schema before mapping:
   - native fields
   - custom fields
   - date-only versus datetime values
   - dependency and hierarchy semantics
   - enum values for status, priority, issue type, and progress
   - resource, team, and calendar fields
3. Preserve source IDs:
   - source system, project ID, task/activity/issue key, row ID, link ID, version, URL, and export filename where available
4. Map conservatively:
   - trusted fields stay trusted
   - custom or inferred fields get confidence notes
   - missing dates stay missing unless the user asks for inference
5. Validate before rendering:
   - invalid date ranges
   - missing dependency targets
   - dependency cycles
   - parent/child date mismatches
   - zero-duration milestones versus malformed tasks
   - timezone boundary shifts
   - duplicate IDs
   - source filters that hide dependencies or children
6. Separate adapters from rendering:
   - one source adapter produces normalized data and diagnostics
   - render code consumes normalized tasks, links, resources, calendars, baselines, and warnings

## Microsoft Project

- Prefer Project XML for rich interchange when available.
- Treat MPP as a proprietary application file that usually needs Microsoft Project or a specialized library to read safely.
- Treat CSV exports as field-table snapshots, not complete projects. They may omit calendars, dependency metadata, resources, baselines, and custom field context depending on the exported table.
- Treat PDF and XPS as view-only artifacts.
- Project XML can include project-level settings, calendars, tasks, resources, assignments, outline codes, WBS masks, extended attributes, and timephased data. Map those into normalized tasks, resources, calendars, and baselines where needed.
- Watch for manually scheduled tasks, constraints, parent rollups, inactive tasks, elapsed durations, calendar-specific working time, and local date display versus stored datetime.

## Primavera P6

- Read P6 XML or XER as schedule-engine exports when available.
- P6 exports can carry activities, activity relationships, resources, roles, calendars, codes, baselines, and scenarios depending on product and export settings.
- XER is proprietary and common in P6 workflows. Document parser assumptions and product/version support.
- P6 XML is often better for richer interchange and baseline/scenario handling, depending on source product.
- Validate relationship type, lag, driving relationship, critical flag, baseline membership, activity type, percent complete type, and calendar assignment.
- Do not assume a P6 file includes all enterprise dictionaries; exports often include only objects assigned to exported projects or activities.

## Jira And Jira Advanced Roadmaps

- Use Jira REST/JQL to fetch issues and discover fields before assuming date mappings.
- Jira issue links are relationship records, not always schedule dependencies. Map "blocks" or "is blocked by" as dependency candidates only after checking link-type semantics.
- Advanced Roadmaps timelines may expose target start, target end, releases, teams, dependencies, and hierarchy through visible fields or exported CSV.
- Treat Advanced Roadmaps CSV as a filtered timeline-view snapshot. Only the visible plan data may be present.
- Custom fields are common. Discover field IDs, names, contexts, and types; preserve the source field ID in provenance.
- Do not infer planned task spans from created, updated, resolved, or status-transition timestamps unless the user asks for actual lifecycle analysis.
- Changelogs are useful for actual workflow timelines, not planned schedule bars by default.

## GitHub Projects

- Use GitHub Projects v2 GraphQL data when structured access is available.
- Projects v2 field values can include date, iteration, milestone, number, text, single-select, labels, reviewers, users, repositories, issues, and pull requests.
- TSV export is a view snapshot. It is useful for reporting but may reflect only visible fields in the exported view.
- GitHub milestones are due-date markers with open/closed issue counts; they are not full task spans.
- GitHub issues and pull requests do not have native start/end schedule fields unless represented by Projects custom fields, labels, milestones, or external integrations.
- Preserve project item ID, content node ID, issue or PR URL, repository, field ID, field name, and view/export context.

## Smartsheet

- Sheets can use Start Date, End Date, Duration, Predecessors, and Percent Complete columns when dependencies are enabled.
- Predecessors can carry dependency type, lag, row ID, row number, invalid state, and critical-path information through API object values.
- Parent rows often roll up dates and progress from children; do not treat them like directly scheduled activities unless the source says so.
- Smartsheet row IDs are stable source IDs; row numbers can change.
- Check whether formulas are disabled or overwritten in dependency-managed columns.

## monday.com

- Gantt and timeline views are built from board columns such as Timeline or Date, People, Status, and Dependency.
- Board exports to Excel are table exports; views may not export exactly as interactive Gantt state.
- monday dependency settings can include flexible, strict, or no-action behavior and dependency types. Preserve that behavior if building an editable schedule.
- Timeline and Date columns may be sufficient for display, but not for a true scheduling engine unless dependency and rescheduling semantics are available.

## Asana

- Asana projects can be exported as JSON or CSV, and tasks can be imported from CSV.
- Dependencies are represented as tasks blocking or blocked by other tasks.
- Due dates and custom fields are common; start dates may depend on plan tier, project setup, or field configuration.
- Preserve task GIDs, project/portfolio GIDs, custom field GIDs, section, assignee, completed state, dependencies, and export context.

## ClickUp

- ClickUp tasks can include start date, due date, assignees, status, priority, time estimates, points, parent/subtask relationships, tags, custom fields, and dependencies.
- API dates may be Unix epoch milliseconds or strings depending on endpoint. Normalize with an explicit timezone policy.
- Date-only values may use local-time defaults. Do not let midnight or early-morning defaults shift the visual day unexpectedly.
- Rescheduling dependencies depend on required date fields and workspace settings.

## Azure DevOps

- Iterations provide start and finish dates for sprint or timebox views.
- Work items can be grouped by iteration and area paths; Analytics OData snapshots are better for trends and lifecycle history than planned Gantt bars.
- Planned schedule fields are often custom or process-specific. Discover fields before mapping.
- Do not treat iteration membership alone as task start/end unless the user wants an iteration-level roadmap.

## CSV, TSV, XLSX, JSON

- Require explicit column mapping for task ID, name, parent, start, finish, duration, progress, owner/resource, status, dependency IDs, milestone flag, baseline dates, and source URL.
- Detect delimiter, encoding, header rows, locale, date format, decimal format, and timezone.
- Preserve unmapped columns as metadata when useful.
- Attach confidence notes to inferred columns such as "Start", "Target start", "Begin", "Due", "Finish", "ETA", or custom labels.
- Validate that dependency references point to stable IDs, not row numbers that can change after sorting.

## PDF, PNG, SVG, Screenshots, Slides

- Treat as visual artifacts only.
- Use them to critique layout, recover labels manually, or guide a redesign.
- Do not claim reliable structured schedule data unless there is an accompanying source table or OCR workflow with human validation.
- When recreating a Gantt from an image, label the result as reconstructed and carry uncertainty notes.

## Source Links

- [Microsoft Project XML Data Interchange Schema](https://learn.microsoft.com/en-us/office-project/xml-data-interchange/project-xml-data-interchange-schema-reference)
- [Microsoft Project supported file formats](https://support.microsoft.com/en-gb/office/file-formats-supported-by-project-desktop-face808f-77ab-4fce-9353-14144ba1b9ae)
- [Microsoft Graph Planner overview](https://learn.microsoft.com/en-us/graph/planner-concept-overview)
- [Jira issue linking model](https://developer.atlassian.com/cloud/jira/platform/issue-linking-model/)
- [Jira issue search API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/)
- [Jira Advanced Roadmaps CSV export](https://support.atlassian.com/jira-software-cloud/docs/export-advanced-roadmaps-plan-data-as-csv/)
- [GitHub Projects data export](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-your-project/exporting-your-projects-data)
- [GitHub GraphQL ProjectV2 objects](https://docs.github.com/en/graphql/reference/objects)
- [Oracle P6 import/export formats](https://docs.oracle.com/cd/F25600_01/English/admin/p6_pro_importing_exporting/import_export_file_formats.htm)
- [Oracle Primavera Cloud activity relationship API](https://docs.oracle.com/en/industries/construction-engineering/primavera-cloud/rest-api/api-activity-relationship.html)
- [Smartsheet predecessor schema](https://developers.smartsheet.com/api/smartsheet/openapi/schemas/predecessor)
- [Asana project import/export](https://help.asana.com/s/article/project-importing-and-exporting)
- [Asana task dependencies](https://help.asana.com/s/article/task-dependencies)
- [monday.com Gantt chart view](https://support.monday.com/hc/en-us/articles/360015643840-The-Gantt-Chart-View-and-Widget)
- [monday.com dependencies](https://support.monday.com/hc/en-us/articles/360007402599-Dependencies-on-monday-com)
- [ClickUp task API](https://developer.clickup.com/docs/tasks)
- [ClickUp date formatting](https://developer.clickup.com/docs/general-time)
- [ClickUp rescheduling dependencies](https://help.clickup.com/hc/en-us/articles/6304547785367-Rescheduling-dependencies)
- [Azure DevOps iterations API](https://learn.microsoft.com/en-us/rest/api/azure/devops/work/iterations/get)
