---
name: microsoft-365-enterprise
description: Route Microsoft 365 workflows across Outlook, Teams, SharePoint, and Planner. Use when the user needs one workflow that spans communication, meetings, files, or shared task tracking without switching Microsoft connectors.
---

# Microsoft 365 Enterprise

## Overview

Use this skill to route cross-surface Microsoft 365 workflows. This connector combines unified Outlook, Teams, SharePoint, and shared Microsoft Planner in one tool context.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Build a scoped daily brief across Microsoft surfaces | [../m365-enterprise-daily-brief/SKILL.md](../m365-enterprise-daily-brief/SKILL.md) |
| Build one meeting or workstream follow-up across Outlook, Teams, docs, and tasks | [../m365-enterprise-meeting-followup/SKILL.md](../m365-enterprise-meeting-followup/SKILL.md) |
| Review and manage shared Microsoft Planner tasks | [../m365-enterprise-task-management/SKILL.md](../m365-enterprise-task-management/SKILL.md) |
| Decide whether a follow-up belongs in Outlook or Teams and draft it correctly | [../m365-enterprise-communications/SKILL.md](../m365-enterprise-communications/SKILL.md) |

## Connector Rules

- Generic `search` is intentionally unavailable on this connector. Use:
  - `search_teams` for Teams messages
  - `search_sharepoint` for SharePoint or OneDrive files
- Generic `fetch` is intentionally unavailable on this connector. Use:
  - `fetch_teams` for Teams paths
  - `fetch_sharepoint` for SharePoint files
- Planner here is shared Microsoft task infrastructure, not a Teams-only feature.

## Routing

- Use this plugin when the job clearly crosses Microsoft surfaces.
- If the request is deeply specialist and single-surface, prefer the matching specialist plugin:
  - Outlook Email
  - Outlook Calendar
  - Teams
  - SharePoint
- Keep this plugin focused on orchestration, cross-surface synthesis, and shared task follow-through.

## Example Requests

- "Give me a Microsoft 365 brief for what changed today across mail, calendar, Teams, docs, and tasks."
- "Pull together the event, the mail thread, the Teams follow-ups, and the docs for this workstream."
- "Figure out whether this follow-up should go in email or Teams, then draft it."
