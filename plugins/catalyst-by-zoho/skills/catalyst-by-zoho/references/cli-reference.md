# CLI Command Reference

Complete reference for the Catalyst CLI (`catalyst` / `zcatalyst`). For official docs see: https://docs.catalyst.zoho.com/en/cli/v1/cli-command-reference/

---

## Table of Contents
1. [Global Options](#global-options)
2. [Authentication & Identity](#authentication--identity)
3. [Token Management](#token-management)
4. [Project Management](#project-management)
5. [Initialization & Setup](#initialization--setup)
6. [Functions](#functions)
7. [Client](#client)
8. [Slate](#slate)
9. [AppSail Setup](#appsail-setup)
10. [Data Store](#data-store)
11. [API Gateway](#api-gateway)
12. [IAC (Infrastructure as Code)](#iac)
13. [Event & Signal Payload Generation](#event--signal-payload-generation)
14. [Configuration](#configuration)
15. [Code Library](#code-library)
16. [Local Development](#local-development)
17. [Deployment](#deployment)
18. [Other Commands](#other-commands)
19. [Safety Rules](#safety-rules)
20. [Troubleshooting](#troubleshooting)
21. [Resource-First Development Order](#resource-first-development-order)

---

## Global Options

These flags can be used with any command:

| Flag | Description |
|------|-------------|
| `-v`, `--version` | Print CLI version |
| `-p`, `--project` | Specify the project ID or name to target |
| `--org` | Specify the organization ID |
| `--token` | Use a Catalyst auth token instead of interactive login |
| `--dc` | Data center region: `us`, `eu`, `in`, `au`, `jp`, `sa`, `ca` |
| `--verbose` | Enable verbose/debug output for troubleshooting |
| `-h`, `--help` | Show help for a command |

---

## Authentication & Identity

### `catalyst login`
Authenticate with Zoho Catalyst. Opens a browser for OAuth by default.

```bash
catalyst login                  # Interactive browser-based login
catalyst login --no-localhost   # Use manual code entry (for remote/headless machines)
catalyst login --force          # Force re-login even if already authenticated
```

### `catalyst logout`
Log out of the current session, clearing stored credentials.

```bash
catalyst logout
```

### `catalyst whoami`
Display the currently logged-in user and associated org details.

```bash
catalyst whoami
```

---

## Token Management

### `catalyst token:generate`
Generate a new auth token for CI/CD or automation.

```bash
catalyst token:generate              # Generate a new token
catalyst token:generate --current    # Generate token for the current project context
```

### `catalyst token:list`
List all active tokens.

```bash
catalyst token:list
```

### `catalyst token:revoke`
Revoke an existing token.

```bash
catalyst token:revoke
```

---

## Project Management

### `catalyst project:list`
List all projects accessible in the current org.

```bash
catalyst project:list
```

### `catalyst project:use`
Set the active project context for subsequent commands.

```bash
catalyst project:use
```

### `catalyst project:reset`
Clear the current project context.

```bash
catalyst project:reset
```

---

## Initialization & Setup

### `catalyst init`
Initialize a Catalyst project in the current directory.

**IMPORTANT: ALWAYS use `--non-interactive` when running from an automated agent.**

```bash
catalyst init                                                    # Interactive mode
catalyst init --force --org <org_id> --project <project_id> --non-interactive  # Non-interactive (REQUIRED for agents)
```

| Flag | Description |
|------|-------------|
| `--force` | Overwrite existing project config |
| `--org` | Organization ID |
| `--project` | Project ID |
| `--non-interactive` | Skip all prompts (ALWAYS use this in automation) |

### `catalyst functions:setup`
Set up the functions directory structure in the current project.

```bash
catalyst functions:setup
```

### `catalyst functions:add`
Add a new function to the project. **This is fully interactive** — it prompts for function name, type (arrow keys), and stack (arrow keys). There are NO non-interactive flags (unlike `init`, `appsail:add`, and `slate:create` which all support flags).

```bash
catalyst functions:add    # ⚠️ ALWAYS interactive — no --name/--type/--stack flags exist
```

**Known limitation for AI agents:** This is the only setup command that cannot be automated. The user MUST run it interactively for the first function in a project.

**Agent workaround for subsequent functions:** Once the user has run `functions:add` at least once (so `catalyst.json` has a populated `functions` block), agents can add more functions by manually:
1. Creating the directory: `functions/<new_function_name>/`
2. Adding `functions/<new_function_name>/catalyst-config.json`:
   ```json
   {
     "deployment": {
       "name": "<new_function_name>",
       "type": "advancedio",
       "stack": "node20"
     },
     "execution": {
       "main": "index.js"
     }
   }
   ```
   Valid `type` values: `basicio`, `advancedio`, `event`, `cron`, `job`, `integration`, `browserlogic`
   Valid `stack` values: `node20`, `node18`, `node16`, `node14`, `java17`, `java11`, `java8`, `python39`
   (Prefer `node20` for new projects — `node14`/`node16` receive no upstream security patches)
3. Adding the function name to `catalyst.json` → `functions.targets` array:
   ```json
   {
     "functions": {
       "targets": ["existing_function", "new_function_name"],
       "ignore": [],
       "source": "functions"
     }
   }
   ```
4. Creating the entry point file (`index.js`, `main.py`, etc.) with the correct handler signature
5. Running `npm init -y && npm install zcatalyst-sdk-node` in the function directory (for Node.js)

**Important:** This workaround only works when `catalyst.json` already has a `functions` block from a prior `functions:add`. If no function has ever been registered, the user must run `functions:add` interactively first.

### `catalyst client:setup`
Set up the client (frontend) directory in the current project.

```bash
catalyst client:setup
```

### `catalyst appsail:add`
Add an AppSail service. **ALWAYS use flags to avoid interactive prompts.**

```bash
catalyst appsail:add --name <name> --stack <stack>
catalyst appsail:add --name <name> --stack <stack> --source <dir> --build <cmd> --platform <platform> --overwrite-config
```

| Flag | Description |
|------|-------------|
| `--name` | Service name (required) |
| `--stack` | Runtime stack, e.g. `node18`, `java17`, `python_3_9` (required) |
| `--source` | Source directory path |
| `--build` | Build command |
| `--platform` | Target platform |
| `--overwrite-config` | Overwrite existing config if present |

---

## Functions

### `catalyst functions:shell`
Open an interactive shell for testing functions locally.

```bash
catalyst functions:shell
```

### `catalyst functions:execute`
Execute a function locally.

```bash
catalyst functions:execute
```

### `catalyst functions:config`
View or modify function configuration.

```bash
catalyst functions:config              # View config
catalyst functions:config --memory     # View/set memory allocation
```

### `catalyst functions:delete`
Delete a function.

```bash
catalyst functions:delete --local      # Remove only from local project
catalyst functions:delete --remote     # Remove from remote (deployed) project
```

---

## Client

### `catalyst client:setup`
Initialize the client directory for the project.

```bash
catalyst client:setup
```

### `catalyst client:delete`
Delete the client component.

```bash
catalyst client:delete --local     # Remove only from local project
catalyst client:delete --remote    # Remove from remote (deployed) project
```

---

## Slate

Slate is Catalyst's frontend framework scaffolding system. **NEVER scaffold manually (no `npm create vite`, etc.).** Always use Slate commands. Additional libraries should be installed AFTER scaffolding.

### `catalyst slate:create`
Create a new Slate frontend project.

```bash
catalyst slate:create --name <name> --framework <framework>
catalyst slate:create --name <name> --framework <framework> --default
```

| Flag | Description |
|------|-------------|
| `--name` | Slate project name |
| `--framework` | Framework to use (see table below) |
| `--default` | Use default settings without prompts |

#### Framework Values

| Framework Value | Detection Keywords | Build Output Directory |
|----------------|-------------------|----------------------|
| `static` | Plain HTML/CSS/JS | `.` or `public/` |
| `angular` | Angular, @angular/core | `dist/<project-name>` |
| `astro` | Astro | `dist/` |
| `create-react-app` | CRA, create-react-app | `build/` |
| `nextjs` | Next.js, next | `out/` or `.next/` |
| `preact` | Preact | `dist/` |
| `react-vite` | React + Vite | `dist/` |
| `solidjs` | SolidJS, Solid | `dist/` |
| `svelte` | Svelte, SvelteKit | `dist/` or `build/` |
| `vue` | Vue.js, Vue 3 | `dist/` |
| `other` | Custom/unknown | Varies |

#### `dev_command` per Framework (in `cli-config.json`)

| Framework | Dev Command |
|-----------|------------|
| React + Vite | `npx vite --port $PORT` |
| Next.js | `npx next dev --port $PORT` |
| Angular | `npx ng serve --port $PORT` |
| Astro | `npx astro dev --port $PORT` |
| Vue | `npx vite --port $PORT` |
| SolidJS | `npx vite --port $PORT` |
| Preact | `npx vite --port $PORT` |
| Svelte | `npx vite --port $PORT` |
| Create React App | `npx react-scripts start` (PORT env var) |

### `catalyst slate:link`
Link an existing local directory as a Slate project.

```bash
catalyst slate:link
```

### `catalyst slate:unlink`
Unlink a Slate project from the Catalyst project.

```bash
catalyst slate:unlink
```

---

## AppSail Setup

AppSail is for deploying full application servers (Express, Spring Boot, Flask, etc.).

**ALWAYS use flags to avoid interactive prompts.**

```bash
# Node.js 18
catalyst appsail:add --name my-api --stack node18

# Java 17 WAR
catalyst appsail:add --name my-service --stack java17

# Python 3.9
catalyst appsail:add --name my-app --stack python_3_9

# With all options
catalyst appsail:add --name my-api --stack node18 --source ./server --build "npm run build" --platform linux --overwrite-config
```

---

## Data Store

### `catalyst ds:import`
Import data into the Data Store from a CSV file.

```bash
catalyst ds:import
```

### `catalyst ds:export`
Export Data Store tables to CSV.

```bash
catalyst ds:export
```

### `catalyst ds:status`
Check the status of a Data Store import/export operation.

```bash
catalyst ds:status
```

---

## API Gateway

### `catalyst apig:enable`
Enable the API Gateway for the current project.

```bash
catalyst apig:enable
```

### `catalyst apig:disable`
Disable the API Gateway.

```bash
catalyst apig:disable
```

### `catalyst apig:status`
Check API Gateway status.

```bash
catalyst apig:status
```

---

## IAC

Infrastructure as Code for managing project resources declaratively.

### `catalyst iac:pack`
Package the current project state into an IAC archive.

```bash
catalyst iac:pack
```

### `catalyst iac:import`
Import an IAC package into the project.

```bash
catalyst iac:import -n    # Import with a specific name
```

### `catalyst iac:export`
Export the project configuration as an IAC package.

```bash
catalyst iac:export                # Export development config
catalyst iac:export --production   # Export production config (CAUTION: targets live environment)
```

### `catalyst iac:status`
Check the status of an IAC operation.

```bash
catalyst iac:status
```

---

## Event & Signal Payload Generation

Generate sample payload files for testing event listeners, integrations, jobs, and signals.

### `catalyst event:generate`
Generate a sample event payload.

```bash
catalyst event:generate
```

### `catalyst event:generate:integ`
Generate a sample integration event payload.

```bash
catalyst event:generate:integ
```

### `catalyst event:generate:job`
Generate a sample job event payload.

```bash
catalyst event:generate:job
```

### `catalyst signals:generate`
Generate a sample signal payload.

```bash
catalyst signals:generate
```

---

## Configuration

Manage CLI configuration key-value pairs.

### `catalyst config:set`
Set a configuration value.

```bash
catalyst config:set <key> <value>
```

### `catalyst config:get`
Get a configuration value.

```bash
catalyst config:get <key>
```

### `catalyst config:delete`
Delete a configuration key.

```bash
catalyst config:delete <key>
```

### `catalyst config:list`
List all configuration values.

```bash
catalyst config:list
```

---

## Code Library

### `catalyst codelib:install`
Install a code library into the project.

```bash
catalyst codelib:install
```

---

## Local Development

### `catalyst serve`
Start the local development server. Serves functions, client, and AppSail locally.

**IMPORTANT: The `catalyst serve` port is dynamic. Never hardcode the port. Never use Vite's dev server directly -- always use `catalyst serve`.**

```bash
catalyst serve                          # Start with defaults
catalyst serve --http                   # Force HTTP (no HTTPS)
catalyst serve --debug                  # Enable debug mode
catalyst serve --proxy                  # Enable proxy mode
catalyst serve --only functions         # Serve only functions
catalyst serve --only client            # Serve only client
catalyst serve --except appsail         # Serve everything except AppSail
catalyst serve --no-watch               # Disable file watching/hot reload
catalyst serve --no-open                # Don't auto-open browser
```

| Flag | Description |
|------|-------------|
| `--http` | Use HTTP instead of HTTPS |
| `--debug` | Enable debug/verbose output |
| `--proxy` | Enable proxy mode for API calls |
| `--only <component>` | Serve only the specified component(s) |
| `--except <component>` | Serve everything except specified component(s) |
| `--no-watch` | Disable file watcher / hot reload |
| `--no-open` | Don't open the browser automatically |

---

## Deployment

### `catalyst deploy`
Deploy the project to Catalyst cloud.

```bash
catalyst deploy                         # Deploy everything
catalyst deploy --only functions        # Deploy only functions
catalyst deploy --only client           # Deploy only client
catalyst deploy --except appsail        # Deploy everything except AppSail
```

#### AppSail Deploy Options

```bash
catalyst deploy appsail
```

#### Slate Deploy Options

```bash
catalyst deploy slate -m "Deployment message"
catalyst deploy slate --production       # Deploy to production (CAUTION)
```

| Flag | Description |
|------|-------------|
| `--only <component>` | Deploy only the specified component |
| `--except <component>` | Deploy everything except specified component |
| `-m` | Deployment message (for Slate) |
| `--production` | Deploy to production environment (CAUTION) |

---

## Other Commands

### `catalyst pull`
Pull remote project resources to local.

```bash
catalyst pull
```

### `catalyst run-script`
Run a custom script defined in the project.

```bash
catalyst run-script
```

### `catalyst help`
Display help for any command.

```bash
catalyst help
catalyst help <command>
catalyst <command> --help
```

---

## Safety Rules

### Destructive Commands Reference

| Command | Risk Level | What It Does | Safeguard |
|---------|-----------|--------------|-----------|
| `functions:delete --remote` | HIGH | Deletes deployed function | Confirm project first |
| `client:delete --remote` | HIGH | Deletes deployed client | Confirm project first |
| `deploy --production` | HIGH | Pushes to production | Verify project and changes |
| `deploy slate --production` | HIGH | Pushes Slate to production | Verify project and changes |
| `iac:export --production` | MEDIUM | Exports production config | May expose secrets |
| `iac:import` | MEDIUM | Overwrites project resources | Verify package contents |
| `ds:import` | MEDIUM | Overwrites Data Store data | Verify CSV and table |
| `project:reset` | LOW | Clears project context | Re-run `project:use` |

### Critical Rules

- **`--production` flag warning**: Any command with `--production` targets the live production environment. Always double-check the project context before using this flag.
- **Always confirm project before mutating**: Run `catalyst whoami` and verify the project context before running any destructive or deployment command.

---

## Troubleshooting

### Common Issues

| Issue | Diagnosis | Solution |
|-------|-----------|---------|
| Login fails | Auth token expired or browser blocked | Run `catalyst login --force` or use `--no-localhost` for headless |
| Wrong project targeted | Stale `.catalystrc` or context | Run `catalyst whoami`, then `catalyst project:use` or `catalyst init` |
| Wrong data center | Mismatched `--dc` flag | Re-login with correct `--dc` (us/eu/in/au/jp/sa/ca) |
| Deploy fails | Missing config, build errors | Check `catalyst.json`, run `catalyst deploy --verbose` |
| Functions not found | Missing `catalyst-config.json` or wrong directory structure | Verify `functions/<name>/catalyst-config.json` exists |
| Port conflicts | Another process using the port | Stop other servers; `catalyst serve` assigns ports dynamically |
| Token expired | Stale auth token | Run `catalyst token:generate` or `catalyst login --force` |
| IAC status stuck | Long-running import/export | Run `catalyst iac:status` to check progress |
| DS import fails | Malformed CSV or schema mismatch | Verify CSV format matches table schema; run `catalyst ds:status` |

### Debugging

- **Enable verbose output**: Add `--verbose` to any command for detailed logs.
- **Get command help**: Run `catalyst help <command>` or `catalyst <command> --help`.

---

## Resource-First Development Order

Always follow this order when building a Catalyst project:

1. **Login**: `catalyst login`
2. **Init**: `catalyst init --force --org <org> --project <proj> --non-interactive`
3. **Create tables**: Set up Data Store tables (via console or IAC)
4. **Configure permissions**: Set table-level and row-level access
5. **Seed data**: Import initial data with `catalyst ds:import`
6. **Set up compute**: Add functions (`functions:add`), AppSail (`appsail:add`), or Slate (`slate:create`)
7. **Write code**: Implement business logic using the Catalyst SDK
8. **Serve locally**: `catalyst serve` (port is dynamic, never hardcode)
9. **Deploy**: `catalyst deploy`

---

External documentation: https://docs.catalyst.zoho.com/en/cli/v1/cli-command-reference/
