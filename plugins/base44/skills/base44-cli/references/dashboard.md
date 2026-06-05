# base44 dashboard open

Opens the Base44 app dashboard in your default web browser.

## Syntax

```bash
npx base44 dashboard open
```

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

1. Reads the project's app ID from `base44/.app.jsonc`
2. Opens the dashboard URL in your default browser
3. Displays the dashboard URL in the terminal

## Example

```bash
# Open dashboard for current project
npx base44 dashboard open
```

## Output

```bash
$ npx base44 dashboard open

Dashboard opened at https://base44.cloud/apps/your-app-id
```

## Requirements

- Must be run from a linked Base44 project directory (contains `base44/.app.jsonc`)
- Must be authenticated (run `npx base44 login` first)

## Notes

- The dashboard provides a web interface to manage your app's entities, functions, agents, users, and settings
- If you're not in a project directory, the command will fail with an error
- The command will not open a browser in CI environments (when `process.env.CI` is set)
