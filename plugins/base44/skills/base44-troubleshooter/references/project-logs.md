# base44 logs

Fetch function logs for this app.

## Syntax

```bash
npx base44 logs [options]
```

## Options

| Option | Description | Required |
|--------|-------------|----------|
| `--function <names>` | Filter by function name(s), comma-separated. If omitted, fetches logs for all project functions | No |
| `--since <datetime>` | Show logs from this time (ISO format) | No |
| `--until <datetime>` | Show logs until this time (ISO format) | No |
| `--level <level>` | Filter by log level: `log`, `info`, `warn`, `error`, `debug` | No |
| `-n, --limit <n>` | Number of results to return (1-1000, default: 50) | No |
| `--order <order>` | Sort order: `asc` or `desc` (default: `desc`) | No |

## Examples

```bash
# Fetch logs for all project functions (last 50 entries)
npx base44 logs

# Fetch only errors
npx base44 logs --level error

# Fetch logs for a specific function
npx base44 logs --function my-function

# Fetch logs for multiple functions
npx base44 logs --function send-email,process-payment

# Fetch logs since a specific time
npx base44 logs --since 2024-01-15T10:00:00

# Fetch logs within a time range
npx base44 logs --since 2024-01-15T10:00:00 --until 2024-01-15T12:00:00

# Fetch last 100 log entries in ascending order
npx base44 logs -n 100 --order asc

# Last 10 errors for a specific function
npx base44 logs --function myFunction --level error --limit 10
```

## Notes

- **Authentication required.** You must be logged in before fetching logs.
- **Project context required.** Must be run from the project directory (where `base44/.app.jsonc` exists).
- When multiple functions are specified, logs are merged and sorted by timestamp.
- If `--function` is omitted, logs are fetched for **all functions** defined in `base44/config.jsonc`.
- The `--limit` applies after merging logs from all specified functions.
- The `--since` and `--until` values are normalized to UTC if no timezone is provided (appends `Z`).
