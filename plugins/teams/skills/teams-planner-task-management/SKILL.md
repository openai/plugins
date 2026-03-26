---
name: teams-planner-task-management
description: Review and manage Microsoft Teams Planner tasks. Use when the user wants to inspect plans or buckets, create tasks from follow-ups, update task fields, or safely delete a Planner task.
---

# Teams Planner Task Management

Use this skill to manage Planner tasks that live inside Teams. It is the Teams-native workflow for turning chat or meeting follow-ups into trackable tasks.

## Start Here

- If the user asks about "my tasks," start with `list_planner_tasks`.
- If the user names a plan or bucket but not the exact ID, resolve it first with `list_planner_plans` and `list_planner_buckets`.
- If the user names assignees for a new task, resolve people to exact user IDs before assignment.

## Workflow

1. Choose the correct task path:
   - review tasks: `list_planner_tasks`
   - inspect plan or bucket structure: `list_planner_plans`, `list_planner_buckets`
   - inspect one task: `fetch_planner_task`
   - create tasks from follow-ups: `create_planner_task`
   - move or update a task: `update_planner_task`
   - delete a task: `delete_planner_task`
2. For follow-up extraction from Teams meetings or chats, summarize the action items first, then turn each confirmed follow-up into a Planner task.
3. When creating tasks, keep titles short and action-oriented. Add assignees, due dates, start dates, priority, or completion percentage only when the user provided or clearly implied them.
4. When updating tasks, fetch the current task first if you need to restate the current state before changing it.
5. Delete a Planner task when the user clearly asked for that action and the target task is resolved.

## Safety

- Do not delete a task on implied intent.
- If a task, plan, or bucket is ambiguous, resolve the exact target before updating or deleting it.
- If follow-ups from a Teams summary are incomplete, return the proposed task list first instead of creating partial tasks silently.

## Output Conventions

- For task reviews, group tasks by plan, bucket, priority, or completion state, whichever makes the answer easiest to scan.
- For task creation proposals, show the task title, assignee, due date, and target bucket before creating anything when the user asked for proposals rather than direct creation.
- For destructive requests, restate the target task before deleting it.

## Example Requests

- "Show me my Planner tasks in Teams."
- "Turn these meeting follow-ups into Planner tasks in the launch board."
- "Move this Planner task to the blocked bucket and push the due date to Friday."
- "Delete this Planner task."
