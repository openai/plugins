# Box CLI

## Table of Contents

- When to use CLI-first mode
- Safe auth checks
- Authentication paths
- Common verification commands
- Actor controls
- Guardrails

## When to use CLI-first mode

Use Box CLI first when:

- Codex needs a quick local smoke test without changing application code
- The operator already has a working Box CLI environment
- You want to verify behavior as the current CLI actor or with `--as-user`

Use `scripts/box_rest.py` instead when:

- The repository already uses token-based REST verification
- The task requires a raw bearer token from the surrounding platform
- Box CLI is not installed or not authenticated

## Safe auth checks

Use these commands to confirm CLI availability and auth without printing secrets:

```bash
command -v box
box --version
box users:get me --json
```

Prefer the bundled wrapper:

```bash
python3 scripts/box_cli_smoke.py check-auth
```

Do not use `box configure:environments:get --current` as a routine check because it can print sensitive environment details.

## Authentication paths

- Fastest OAuth flow with the official Box CLI app:
  - `box login -d`
- OAuth with your own Box app:
  - `box login --platform-app`
- Add an environment from an app config file:
  - `box configure:environments:add PATH`

After login or environment setup, re-run `box users:get me --json` to confirm the CLI can make authenticated calls.

## Common verification commands

Read-only checks:

```bash
box users:get me --json
box folders:get 0 --json --fields id,name,item_collection
box folders:items 0 --json --max-items 20
box search "invoice" --json --limit 10
```

Write checks:

```bash
box folders:create 0 "codex-smoke-test" --json
box files:upload ./artifact.pdf --parent-id 0 --json
box shared-links:create 12345 file --access company --json
```

Wrapper equivalents:

```bash
python3 scripts/box_cli_smoke.py get-folder 0 --fields id name item_collection
python3 scripts/box_cli_smoke.py list-folder-items 0 --max-items 20
python3 scripts/box_cli_smoke.py search "invoice" --limit 10
python3 scripts/box_cli_smoke.py create-folder 0 "codex-smoke-test"
```

## Actor controls

- Use `--as-user <id>` to verify behavior as a different allowed Box user.
- Use `-t <token>` only when the task explicitly requires a direct bearer token instead of the current CLI environment.
- Always report which actor was used for the verification command.

## Guardrails

- Do not paste or echo client secrets, private keys, or raw access tokens into the conversation.
- Prefer read commands before write commands.
- For shared links and collaborations, confirm scope and audience before creating or widening access.
- After any write, follow up with a read command against the same object and actor.

## Official docs

- CLI overview:
  - https://developer.box.com/guides/cli
- CLI OAuth quick start:
  - https://developer.box.com/guides/cli/quick-start
- CLI options and `--as-user`:
  - https://developer.box.com/guides/cli/quick-start/options-and-bulk-commands/
