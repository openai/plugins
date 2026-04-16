---
name: render-migrate-from-heroku
description: "Migrate from Heroku to Render by reading local project files and generating equivalent Render services. Triggers: any mention of migrating from Heroku, moving off Heroku, Heroku to Render migration, or switching from Heroku. Reads Procfile, dependency files, and app config from the local repo. Optionally uses Heroku MCP to enrich with live config vars, add-on details, and dyno sizes. Uses Render MCP or Blueprint YAML to create services."
license: MIT
compatibility: Render MCP server recommended for direct creation and automated verification; not required for the Blueprint path. Heroku MCP server is optional (enhances config var and add-on discovery).
metadata:
  author: Render
  version: "1.5.0"
  category: migration
---

# Heroku to Render Migration

Migrate from Heroku to Render by reading local project files first, then optionally enriching with live Heroku data via MCP.

## Prerequisites Check

Before starting, verify what's available:

1. **Local project files** (required) — confirm the current directory contains a Heroku app (look for `Procfile`, `app.json`, `package.json`, `requirements.txt`, `Gemfile`, `go.mod`, or similar)
2. **Render MCP** (recommended) — check if `list_services` tool is available. Required for MCP Direct Creation (Step 3B) and automated verification (Step 6). Not required for the Blueprint path — the Render CLI and Dashboard handle generation, validation, and deployment.
3. **Heroku MCP** (optional) — check if `list_apps` tool is available

If Render MCP is missing and the user needs it, guide them through setup using the [MCP setup guide](references/mcp-setup.md). If Heroku MCP is missing, note that config var values and add-on plan details will need to be provided manually.

## Migration Workflow

Execute steps in order. Present findings to the user and get confirmation before creating any resources.

### Step 1: Inventory Heroku App

Gather app details from local files first, then supplement with Heroku MCP if available.

#### 1a. Read local project files (always)

Read these files from the repo to determine runtime, commands, and dependencies:

| File                                              | What it tells you                                                      |
| ------------------------------------------------- | ---------------------------------------------------------------------- |
| `Procfile`                                        | Process types and start commands (`web`, `worker`, `clock`, `release`) |
| `package.json`                                    | Node.js runtime, build scripts, framework deps (Next.js, React, etc.)  |
| `requirements.txt` / `Pipfile` / `pyproject.toml` | Python runtime, dependencies (Django, Flask, etc.)                     |
| `Gemfile`                                         | Ruby runtime, dependencies (Rails, Sidekiq, etc.)                      |
| `go.mod`                                          | Go runtime                                                             |
| `Cargo.toml`                                      | Rust runtime                                                           |
| `app.json`                                        | Declared add-ons, env var descriptions, buildpacks                     |
| `runtime.txt`                                     | Pinned runtime version                                                 |
| `static.json`                                     | Static site indicator                                                  |
| `yarn.lock` / `pnpm-lock.yaml`                    | Package manager (affects build command)                                |

From these files, determine:

- **Runtime** — from dependency files (see the [buildpack mapping](references/buildpack-mapping.md))
- **Runtime version** — from `runtime.txt`, `.node-version`, or `engines` in `package.json`. If pinned, carry it over as an env var (e.g., `PYTHON_VERSION`, `NODE_VERSION`). If not pinned, do not specify a version — never assume or state what Render's default version is.
- **Build command** — from package manager and framework (see the [buildpack mapping](references/buildpack-mapping.md))
- **Start commands** — from `Procfile` entries
- **Process types** — from `Procfile` (web, worker, clock, release)
- **Add-ons needed** — from `app.json` `addons` field, or infer from dependency files (e.g., `pg` in `package.json` suggests Postgres, `redis` suggests Key Value)
- **Static site?** — from `static.json`, SPA framework deps, or static buildpack in `app.json`

#### 1b. Enrich with Heroku MCP (if available)

If the Heroku MCP server is connected, call these tools to fill in details that aren't in the repo. The **dyno size** and **add-on plan slug** are critical — they determine which Render plans to use.

1. `list_apps` — let user select which app to migrate (confirms app name)
2. `get_app_info` — capture: region, stack, buildpacks, **config var names**
3. `list_addons` — capture the **exact add-on plan slug** (e.g., `heroku-postgresql:essential-2`, `heroku-redis:premium-0`). The part after the colon maps to a specific Render plan in the [service mapping](references/service-mapping.md).
4. `ps_list` — capture the **exact dyno size** for each process type (e.g., `Standard-2X`, `Performance-M`). Each dyno size maps to a specific Render plan in the [service mapping](references/service-mapping.md).
5. `pg_info` (if Postgres exists) — capture **Data Size** (actual usage) and the plan's disk allocation. The plan's disk size determines the `diskSizeGB` value in the Blueprint (see the [service mapping](references/service-mapping.md)).

If Heroku MCP is **not** available, ask the user to provide:

- Dyno sizes (or run `heroku ps:type -a <app>` and paste output)
- Add-on plans (or run `heroku addons -a <app>` and paste output)
- Database info (or run `heroku pg:info -a <app>` and paste output — captures plan name, data size, and disk allocation)
- App region (`us` or `eu`)
- Config var names (or run `heroku config -a <app> --shell` and paste output)

If the user cannot provide dyno sizes or add-on plans, use the fallback defaults from the [service mapping](references/service-mapping.md): `starter` for compute, `basic-1gb` for Postgres, `starter` for Key Value.

#### Present summary

```
App: [name] | Region: [region] | Runtime: [node/python/ruby/etc]
Source: [local files | local files + Heroku MCP]
Build command: [inferred from buildpack/deps]
Processes:
  web: [command from Procfile] → Render web service ([mapped-plan])
  worker: [command] → Render background worker ([mapped-plan], Blueprint only)
  clock: [command] → Render cron job ([mapped-plan])
  release: [command] → Append to build command
Add-ons:
  Heroku Postgres ([plan-slug], [disk-size]) → Render Postgres ([mapped-plan], diskSizeGB: [size])
  Heroku Redis ([plan-slug]) → Render Key Value ([mapped-plan])
Config vars: 14 total (list names, not values)
```

### Step 2: Pre-Flight Check

Before creating anything, run through the [pre-flight checklist](references/preflight-checklist.md) to validate the migration plan. Key checks:

- Runtime supported (or needs Dockerfile)
- Worker dynos, release phase, static site detection
- Third-party add-ons without Render equivalents
- Git remote exists and is HTTPS format
- Database size (large DBs need assisted migration)

Look up each Heroku dyno size and add-on plan in the [service mapping](references/service-mapping.md) to determine correct Render plans and cost estimates. Present the migration plan table from the [pre-flight checklist](references/preflight-checklist.md) and wait for user confirmation before creating any resources.

### Determine Creation Method

After the user approves the pre-flight plan, apply this decision rule. **Default to Blueprint** — only use MCP Direct Creation when every condition below is met.

**Use Blueprint** (the default) when ANY are true:

- Multiple process types (web + worker, web + cron, etc.)
- Databases or Key Value stores needed
- Background workers in the Procfile
- User prefers Infrastructure-as-Code configuration

**Fall back to MCP Direct Creation** ONLY when ALL are true:

- Single web or static site service (one process type)
- No background workers or cron jobs
- No databases or Key Value stores

If unsure, use Blueprint. Most Heroku apps have at least a database, so Blueprint applies to the vast majority of migrations.

### Step 3A: Generate Blueprint (Multi-Service)

This step has three mandatory sub-steps. Complete all three in order.

#### 3A-i. Write render.yaml

Generate a `render.yaml` file and write it to the repo root. See the [Blueprint example](references/blueprint-example.md) for a complete example, the [Blueprint docs](https://render.com/docs/blueprint-spec#projects-and-environments) for usage guidance, and the [Blueprint YAML JSON schema](https://render.com/schema/render.yaml.json) for the full field reference.

**IMPORTANT: Always use the `projects`/`environments` pattern.** The YAML must start with a `projects:` key — never use flat top-level `services:` or `databases:` keys. This groups all migrated resources into a single Render project.

**Set the `plan:` field for each service and database using the mapped Render plan from the [service mapping](references/service-mapping.md).** Look up the Heroku dyno size (from `ps_list`) and add-on plan slug (from `list_addons`) to find the correct Render plan. If the Heroku plan is unknown, use the fallback defaults: `starter` for compute, `basic-1gb` for Postgres, `starter` for Key Value.

Generate the YAML following the full template, rules, and patterns in the [Blueprint example](references/blueprint-example.md). Critical rules:

- Always use the `projects:`/`environments:` pattern — never flat top-level `services:`
- Set every `plan:` field using the [service mapping](references/service-mapping.md)
- Set `diskSizeGB` on databases from the Heroku disk allocation
- Use `fromDatabase` for `DATABASE_URL` and `fromService` for `REDIS_URL` — never hardcode connection strings
- Mark secrets with `sync: false`

#### 3A-ii. Validate the Blueprint

This step is mandatory. First, check if the Render CLI is installed:

```bash
render --version
```

If not installed, offer to install it:

- macOS: `brew install render`
- Linux/macOS: `curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh | sh`

Once the CLI is available, run the validation command and show the output to the user:

```bash
render blueprints validate render.yaml
```

If validation fails, fix the errors in the YAML and re-validate. Repeat until validation passes. **Do not proceed to the next step until the Blueprint validates successfully.**

#### 3A-iii. Provide the deploy URL

After validation passes:

1. Instruct user to commit and push: `git add render.yaml && git commit -m "Add Render migration Blueprint" && git push`
2. Get the repo URL by running `git remote get-url origin`. If the URL is SSH format (e.g., `git@github.com:user/repo.git`), convert it to HTTPS (`https://github.com/user/repo`). Then construct the deeplink: `https://dashboard.render.com/blueprint/new?repo=<HTTPS_REPO_URL>`
3. Present the **actual working deeplink** to the user — never show a placeholder URL. Guide user to open it, fill in `sync: false` secrets, and click **Apply**

**Do not skip the deploy URL.** The user needs this link to apply the Blueprint on Render.

### Step 3B: MCP Direct Creation (Single-Service)

Before creating resources via MCP, verify the active workspace:

```
get_selected_workspace()
```

If the workspace is wrong, list available workspaces with `list_workspaces()` and ask the user to select the correct one. Resources will be created in whichever workspace is active.

For single-service migrations without databases, create via MCP tools:

1. **Web service** — `create_web_service` with:
   - `runtime`: from the [buildpack mapping](references/buildpack-mapping.md)
   - `buildCommand`: from the [buildpack mapping](references/buildpack-mapping.md)
   - `startCommand`: from Procfile `web:` entry
   - `repo`: user-provided GitHub/GitLab URL
   - `region`: mapped from Heroku region
   - `plan`: mapped from Heroku dyno size using the [service mapping](references/service-mapping.md) (fallback: `starter`)
2. **Static site** — `create_static_site` if detected (instead of web service)

Present the creation result (service URL, ID) when complete.

### Step 4: Migrate Environment Variables

#### Gather config vars

Use the first available source:

1. **Heroku MCP** (preferred) — config vars from `get_app_info` results (Step 1b)
2. **User-provided** — ask the user to paste output of `heroku config -a <app> --shell`
3. **`app.json`** — var names and descriptions (no values, but useful for `sync: false` entries)

#### Filter and categorize

Remove auto-generated and Heroku-specific vars (see the full filter list in the [service mapping](references/service-mapping.md)):

- `DATABASE_URL`, `REDIS_URL`, `REDIS_TLS_URL` (Render generates these)
- `HEROKU_*` vars (e.g., `HEROKU_APP_NAME`, `HEROKU_SLUG_COMMIT`)
- Add-on connection strings (`PAPERTRAIL_*`, `SENDGRID_*`, etc.)

Present filtered list to user — **do not write without confirmation**.

#### Apply vars

**Blueprint path (Step 3A):** Env vars are already embedded in the `render.yaml` on each service (non-secret values inline, secrets marked `sync: false` for the user to fill in during Blueprint apply). No separate MCP call is needed — skip to Step 5.

**MCP path (Step 3B):** Call Render `update_environment_variables` with confirmed vars (supports bulk set, merges by default).

### Step 5: Data Migration

Follow the [data migration guide](references/data-migration.md) to migrate Postgres and Redis data. The guide covers sub-steps 5a through 5e in detail. Summary of the flow:

1. **Pre-migration checks** — confirm Render resources are provisioned via `list_postgres_instances()` and `list_key_value()`, check source DB size, verify Render CLI (`render --version`), `pg_dump`, and `pg_restore` are installed
2. **Gather connection strings** — Heroku Postgres via `pg_credentials` (MCP) or user CLI paste. For Key Value, construct a Dashboard deeplink from the ID.
3. **Postgres migration** — two approaches based on size: **under 2 GB** uses `render psql` (no Render connection string needed); **2-50 GB** uses `pg_dump -Fc` + `pg_restore` with external connection string from Dashboard (faster, compressed, parallel restore).
4. **Key Value / Redis** — usually skip (ephemeral cache). If persistent data, use `redis-cli` dump/restore with Dashboard-provided Render URL.
5. **Data validation** — verify schema and row counts via `query_render_postgres`, compare against Heroku source if MCP is available.

### Step 6: Verify Migration

After user confirms database migration is complete, run through each check in order. Stop at the first failure, fix it, and redeploy before continuing.

#### 1. Confirm deploy status

```
list_deploys(serviceId: "<service-id>", limit: 1)
```

Expect `status: "live"`. If status is `failed`, inspect build and runtime logs immediately.

#### 2. Verify service health

Hit the health endpoint (or `/`) and confirm a 200 response. If there is no health endpoint, verify the app binds to `0.0.0.0:$PORT` (not `localhost`).

#### 3. Scan error logs

```
list_logs(resource: ["<service-id>"], level: ["error"], limit: 50)
```

Look for clear failure signatures: missing env vars, connection refused, module not found, port binding errors.

#### 4. Verify env vars and port binding

Confirm all required env vars are set — especially secrets marked `sync: false` during Blueprint apply. Ensure the app binds to `0.0.0.0:$PORT`.

#### 5. Check resource metrics

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_request_count", "cpu_usage", "memory_usage"]
)
```

Verify CPU and memory are within expected ranges for the selected plan.

#### 6. Confirm database connectivity

```
query_render_postgres(postgresId: "<postgres-id>", sql: "SELECT count(*) FROM <key_table>")
```

Run a read-only query on a key table to confirm data was restored correctly. Compare row counts against the Heroku source if possible.

Present a health summary after all checks pass.

### Step 7: DNS Cutover (Manual)

Instruct user to:

1. Add CNAME pointing domain to `[service-name].onrender.com`
2. Remove/update old Heroku DNS entries
3. Wait for propagation

## Rollback Plan

If the migration fails at any point:

- **Services created but not working**: Services can be deleted from the Render dashboard (MCP server intentionally does not support deletion). Heroku app is untouched until maintenance mode is enabled.
- **Env vars wrong**: Call `update_environment_variables` with `replace: true` to overwrite, or fix individual vars.
- **Database migration failed**: Render Postgres can be deleted and recreated. Heroku database is read-only during dump (no data loss). If `maintenance_off` is called on Heroku, the original app is fully operational again.
- **DNS already changed**: Revert CNAME to Heroku and disable maintenance mode on Heroku.

Key principle: **Heroku stays fully functional until the user explicitly cuts over DNS.** The migration is additive until that final step.

## Error Handling

- Service creation fails: show error, suggest fixes (invalid plan, bad repo URL)
- Env var migration partially fails: show which succeeded/failed
- Heroku auth errors: instruct `heroku login` or check `HEROKU_API_KEY`
- Render auth errors: check Render API key in MCP config
