# base44 link

Links an existing local Base44 project to a Base44 app in the cloud. Use this when you have a `base44/config.jsonc` but haven't connected it to a Base44 app yet.

## Critical: When to Use Link vs Create

| Scenario | Command |
|----------|---------|
| Starting fresh, no `base44/` folder | `npx base44 create` |
| Have `base44/config.jsonc` but no `.app.jsonc` | `npx base44 link` |
| Project already linked (has `.app.jsonc`) | Already done, use `deploy` |

## Syntax

```bash
npx base44 link [options]
```

## Options

| Option | Description | Required |
|--------|-------------|----------|
| `-c, --create` | Create a new project (skip selection prompt) | No |
| `-n, --name <name>` | Project name (required when `--create` is used) | With `--create` |
| `-d, --description <description>` | Project description | No |
| `-p, --projectId <id>` | Project ID to link to an existing project (skip selection prompt) | No |

## Non-Interactive Mode

For CI/CD or agent use:

**Create a new project:**
```bash
npx base44 link --create --name my-app
```

**Link to an existing project:**
```bash
npx base44 link --projectId <project-id>
```

WRONG: `npx base44 link --create` (missing --name)
WRONG: `npx base44 link --create --projectId <id>` (cannot use both)
RIGHT: `npx base44 link --create --name my-app`
RIGHT: `npx base44 link --projectId <id>`

## Examples

```bash
# Interactive mode - prompts for project details
npx base44 link

# Non-interactive - create and link in one step
npx base44 link --create --name my-app

# With description
npx base44 link --create --name my-app --description "My awesome app"

# Link to a specific existing project by ID
npx base44 link --projectId abc123
```

## What It Does

1. Finds the `base44/config.jsonc` in the current directory (or parent directories)
2. Verifies no `.app.jsonc` exists (project not already linked)
3. Either:
   - Creates a new Base44 app in the cloud (with `--create`), OR
   - Links to an existing project (with `--projectId` or interactive selection)
4. Writes the app ID to `base44/.app.jsonc`

## Requirements

- Must have `base44/config.jsonc` in the project
- Must NOT have `base44/.app.jsonc` (use `deploy` if already linked)
- Must be authenticated (run `npx base44 login` first)

## Notes

- After linking, you can deploy resources with `npx base44 deploy`
- The `.app.jsonc` file should be git-ignored (contains your app ID)
