---
name: mixpanel-auth
description: "Manage Mixpanel Headless authentication: check session state, list/add/use accounts, run OAuth login, switch projects/workspaces, manage targets, and check bridge credentials."
---

# Mixpanel Authentication Management

You manage Mixpanel credentials by shelling out to `auth_manager.py`. Every
subcommand emits exactly one JSON object to stdout — parse it and present the
result conversationally.

Before running bundled scripts, set `PLUGIN_ROOT` to the absolute path of the installed
`mixpanel-headless` plugin directory.

**Script path:** `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py`

**Schema:** Every response has `schema_version: 1` and a discriminated `state`
of `ok` | `needs_account` | `needs_project` | `error`. Errors emit JSON to
stdout (exit 0) so you can `json.loads` unconditionally — no try/except needed.

## Security Rules (NON-NEGOTIABLE)

- **NEVER ask for secrets (passwords, API secrets) in conversation** — they would be visible in history
- **NEVER pass secrets as CLI arguments** — visible in process list
- For account creation, guide the user to run `mp account add <name> --type service_account -u <username> -p <project_id> -r <region>` themselves — this prompts for the secret with hidden input

## Routing

Parse `$ARGUMENTS` and route to the appropriate subcommand. With no
arguments, run `session`.

### "login"

For first-time setup, the frictionless one-shot path is `mp login`. It
runs the right auth flow for the environment, derives the account name
from `/me`, and pins a default project. Tell the user to run:

```bash
mp login
```

Region behavior is auth-type-specific:
- `service_account` and `oauth_token` paths: probes `us → eu → in` and
  uses the first 200.
- `oauth_browser` path (the bare-`mp login` default): commits to `us`
  unless the user passes `--region eu` or `--region in`.

Optional flags they may want:
- `--name NAME` — override the derived account name
- `--region us|eu|in` — set the region explicitly (required for EU / India browser users)
- `--project ID` — skip the project picker
- `--service-account` — force the SA path (requires `MP_USERNAME` + `MP_SECRET` in env)
- `--token-env VAR` — force the static-bearer path (reads token from `$VAR`)
- `--no-browser` — print the authorization URL instead of launching a browser

After the user confirms they ran it, verify with `account test`:
`python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py account test`

### No arguments or "session"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py session`

Switch on `state`:
- **`ok`** — show one line: "Active: `account.name` → project `project.id`"
  (add workspace `workspace.id` if non-null). Mention that
  the account-list and project-list workflows in this skill exist if the user wants to switch.
- **`needs_account`** — no account configured. Show the first
  `next[0].command` as the recommended onboarding step (the frictionless
  `mp login` orchestrator); list the alternatives in `next[1]` (explicit
  account add) and `next[2]` (`MP_OAUTH_TOKEN` env triple — best for
  non-interactive contexts like CI or agents).
- **`needs_project`** — account configured but no project pinned. Tell the
  user to run `mp project list` then `mp project use <id>`.
- **`error`** — show `error.message`. If `error.actionable` is true, the
  message names a concrete next command.

### "account list"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py account list`

Present `items` as a clean table: `name`, `type`, `region`, `is_active`.
Mark the active account with a star. If `referenced_by_targets` is non-empty
for any account, mention it ("`team` is referenced by targets: `ecom`").

If `items` is empty, show the `next` onboarding hints (same as `needs_account`).

### "account add"

This is a guided wizard. Do NOT run any script that handles secrets.

1. Ask for the **account name** (e.g., "personal", "team", "ci")
2. Ask for the **type** — `oauth_browser` (recommended for laptops),
   `service_account` (long-lived), or `oauth_token` (CI/agents)
3. Ask for the **region** (us, eu, or in — default us)
4. For `service_account`: ask for username and project ID (numeric).
   For `oauth_token`: ask for project ID and the env-var name holding the bearer.
   For `oauth_browser`: project ID is OPTIONAL — `mp account login` will
   backfill it after the PKCE flow.
5. Then instruct the user to run the appropriate command. For service accounts:

```bash
Now run this command — it will prompt for your service account secret with hidden input:

mp account add <NAME> --type service_account --username <USERNAME> --project <PROJECT_ID> --region <REGION>
```

For OAuth browser, prefer the one-shot `mp login` (covered by the "login"
branch above):

```bash
mp login --name <NAME> --region <REGION>
```

For full control over registration before the PKCE flow, the explicit
two-step is still available:

```bash
mp account add <NAME> --type oauth_browser --region <REGION>
mp account login <NAME>      # opens browser for PKCE flow
```

Replace placeholders with the values collected above.

6. After the user confirms they ran it, verify with `account test`:
   `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py account test <NAME>`
7. Report success or failure based on the `result.ok` field.

### "account use" or "account use <name>"

If a name is provided:
- Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py account use <name>`

If no name:
- First run `account list` to show available accounts
- Ask which to switch to
- Then run `account use` with the chosen name

On `state: ok`, show one line: "Switched to `active.account` (project `active.project`)".
On `state: error`, show `error.message`.

### "account login" or "account login <name>"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py account login <name>`

Tell the user a browser window will open for Mixpanel authentication.
Wait for the JSON response.

On `state: ok`: "OAuth login successful! `logged_in_as.user.email`, token
valid until `logged_in_as.expires_at`."
On `state: error`: Show `error.message` and suggest retrying.

### "account test" or "account test <name>"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py account test [name]`

The subcommand never raises — `state` is always `ok`. Read `result.ok` to
determine whether the credentials worked:
- `result.ok: true` → "Connected as `result.user.email` ·
  `result.accessible_project_count` accessible projects."
- `result.ok: false` → "Test failed: `result.error`."

### "project list"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py project list`

Present `items` as a table: organization, project name, project ID. Mark the
active project (`is_active: true`) with a star. Suggest the project-use workflow
in this skill to switch.

### "project use <id>"

If no ID: run `project list` first, then ask which to switch to.

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py project use <PROJECT_ID>`

On `state: ok`: "Switched to project `active.project`."
On `state: error`: Show `error.message`.

### "workspace list"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py workspace list`

Present `items` as a table: workspace ID, name, `is_default`. Mark the
active workspace with a star. Mention the parent project from
`project.name` (`project.id`).

### "workspace use <id>"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py workspace use <WORKSPACE_ID>`

On `state: ok`: "Pinned workspace `active.workspace`."

### "target list"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py target list`

Targets are saved (account, project, workspace?) triples — named cursor
positions. Present as a table: name, account, project, workspace.

### "target add"

Guided wizard — collect target name, account name, project ID, optional
workspace ID. Then either invoke the auth_manager directly:

```
python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py target add <NAME> --account <ACCT> --project <PROJ> [--workspace <WS>]
```

Or guide the user to `mp target add <NAME> --account <ACCT> --project <PROJ> [--workspace <WS>]`.

### "target use <name>"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py target use <name>`

Applies all three axes (`account` / `project` / `workspace`) to `[active]`
in a single atomic config write.

### "bridge status"

Run: `python3 $PLUGIN_ROOT/skills/mixpanelyst/scripts/auth_manager.py bridge status`

Parse the JSON:
- If `bridge` is null → "No bridge file found. To create one, run
  `mp account export-bridge --to <path>` on your host machine."
- If `bridge` is non-null → show `bridge.path`, `bridge.account.name`
  (`bridge.account.type`), pinned `bridge.project` / `bridge.workspace` if set,
  and any custom `bridge.headers`.

## Bearer-token env vars (`MP_OAUTH_TOKEN`)

For non-interactive contexts (CI, agents, ephemeral environments) where the
PKCE browser flow isn't viable, set:

```
export MP_OAUTH_TOKEN=<bearer-token>
export MP_PROJECT_ID=<project-id>
export MP_REGION=<us|eu|in>
```

The library builds an `Authorization: Bearer <token>` header for every
Mixpanel endpoint. The full service-account env-var set (`MP_USERNAME` +
`MP_SECRET` + `MP_PROJECT_ID` + `MP_REGION`) takes precedence when both
sets are complete, so this is safe to add to a shell that already exports
the service-account vars.

## Presentation Style

- Be concise — show status in 1–2 lines, not a wall of JSON
- Use tables for lists of accounts, projects, workspaces, targets
- Always suggest a next action when something is missing
- On errors, show `error.message` verbatim — it names the fix
