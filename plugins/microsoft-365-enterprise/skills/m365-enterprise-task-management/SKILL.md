---
name: m365-enterprise-task-management
description: Review and manage shared Microsoft Planner tasks in enterprise workflows. Use when the user wants to inspect tasks, create tasks from follow-ups, update task fields, or safely delete a Planner task from one Microsoft 365 workflow context.
---

# Microsoft 365 Enterprise Task Management

Use this skill for shared Microsoft Planner workflows on the enterprise connector.

## Workflow

1. Use `list_planner_tasks` for "my tasks" style requests.
2. Use `list_planner_plans` and `list_planner_buckets` when the user names a plan or bucket informally and you need exact IDs.
3. Use `fetch_planner_task` before updating or deleting when the exact current state matters.
4. Use `create_planner_task` for confirmed follow-ups from email, meetings, Teams threads, or document reviews.
5. Use `update_planner_task` to move, reprioritize, reassign, or update dates on an existing task.
6. Use `delete_planner_task` only with clear destructive intent.

## Output Conventions

- Keep task reviews grouped by plan, bucket, priority, or completion state.
- For proposed task creation, show the title, assignee, due date, and bucket before writing when the user asked for proposals rather than direct creation.
- Restate the exact task before any destructive delete.
