---
name: m365-enterprise-daily-brief
description: Build a scoped Microsoft 365 daily brief across Outlook, Teams, SharePoint, and Planner. Use when the user wants a practical readout of what changed today and what most likely needs attention next.
---

# Microsoft 365 Enterprise Daily Brief

Use this skill when the user wants a cross-surface daily brief rather than a single-product summary.

## Workflow

1. Require explicit scope when the user does not name workstreams, teams, mailboxes, or document areas.
2. Anchor relative dates like "today" and "tomorrow" to explicit local dates.
3. Gather only the surfaces that matter:
   - Outlook mail via `list_messages` or `search_messages`
   - Outlook calendar via `list_events`
   - Teams via `list_chats(unread_only=True)` and `list_recent_threads`
   - SharePoint via `search_sharepoint`
   - Planner via `list_planner_tasks`
4. Keep the brief focused on changes, blockers, asks, ownership changes, and tasks that likely change the user's plan.
5. If a surface is too broad or under-scoped, say that directly instead of pretending the brief is exhaustive.

## Output Conventions

- Group the brief by workstream or surface, whichever is easier to scan.
- Lead with what most likely needs action today.
- Add a short coverage note when the brief is intentionally scoped rather than exhaustive.
