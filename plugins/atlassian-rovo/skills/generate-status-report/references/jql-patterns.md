# JQL Query Patterns

Common JQL patterns for status report generation.

## Basic Project Queries

**All open issues in a project:**
```jql
project = "PROJECT_KEY" AND status != Done
```

**Open issues by status:**
```jql
project = "PROJECT_KEY" AND status IN ("To Do", "In Progress", "In Review")
```

## Priority-Based Queries

**High priority open issues:**
```jql
project = "PROJECT_KEY" AND status != Done AND priority IN ("Highest", "High")
```

**Blocked issues:**
```jql
project = "PROJECT_KEY" AND status = Blocked
```

## Time-Based Queries

**Updated in last week:**
```jql
project = "PROJECT_KEY" AND updated >= -7d
```

**Completed in reporting period:**
```jql
project = "PROJECT_KEY" AND status = Done AND resolved >= -7d
```

**Created this sprint:**
```jql
project = "PROJECT_KEY" AND created >= -14d
```

## Assignee Queries

**Unassigned issues:**
```jql
project = "PROJECT_KEY" AND assignee is EMPTY AND status != Done
```

**Issues by team member:**
```jql
project = "PROJECT_KEY" AND assignee = "user@example.com" AND status != Done
```

## Combined Queries for Reports

**Current sprint overview:**
```jql
project = "PROJECT_KEY" AND status IN ("To Do", "In Progress", "In Review", "Done") AND updated >= -7d ORDER BY priority DESC, updated DESC
```

**Risk items (high priority blocked or overdue):**
```jql
project = "PROJECT_KEY" AND (status = Blocked OR (duedate < now() AND status != Done)) AND priority IN ("Highest", "High") ORDER BY priority DESC
```

## Epic and Component Queries

**Issues by epic:**
```jql
parent = "EPIC_KEY" AND status != Done
```

Note: Older Jira instances may use `"Epic Link" = "EPIC_KEY"` instead of `parent`.

**Issues by component:**
```jql
project = "PROJECT_KEY" AND component = "ComponentName" AND status != Done
```
