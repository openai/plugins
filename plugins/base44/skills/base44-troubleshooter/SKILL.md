---
name: base44-troubleshooter
description: Troubleshoot production issues using backend function logs. Use when investigating app errors, debugging function calls, or diagnosing production problems in Base44 apps.
---

# Troubleshoot Production Issues

## Prerequisites

Verify authentication before fetching logs:

```bash
npx base44 whoami
```

If not authenticated or token expired, instruct user to run `npx base44 login`.

Must be run from the project directory (where `base44/.app.jsonc` exists):

```bash
cat base44/.app.jsonc
```

## Available Commands

| Command | Description | Reference |
|---------|-------------|-----------|
| `base44 logs` | Fetch function logs for this app | [project-logs.md](references/project-logs.md) |

## Troubleshooting Flow

### 1. Check Recent Errors

Start by pulling the latest errors across all functions:

```bash
npx base44 logs --level error
```

### 2. Drill Into a Specific Function

If you know which function is failing:

```bash
npx base44 logs --function <function_name> --level error
```

### 3. Inspect a Time Range

Correlate with user-reported issue timestamps:

```bash
npx base44 logs --function <function_name> --since <start_time> --until <end_time>
```

### 4. Analyze the Logs

- Look for stack traces and error messages in the output
- Check timestamps to correlate with user-reported issues
- Use `--limit` to fetch more entries if the default 50 isn't enough
