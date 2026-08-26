# Box CLI

## Table of Contents

- When to use CLI-first mode
- Safe auth checks
- Authentication paths
- Common verification commands
- Actor controls
- Guardrails

## When to use the CLI

Tool selection between MCP and CLI is handled in the main skill workflow — see the tool selection table in `SKILL.md`. The CLI is particularly strong for:

- **Full API coverage** — if a Box MCP tool isn't available for the task, the CLI can likely handle it.
- **Compact, controllable output** — `--fields` and `--json` flags let you request exactly the data you need.
- **Local verification and smoke tests** — quick inspection without changing application code.
- **Actor testing** — verify behavior as the current CLI actor or impersonate with `--as-user`.
- **Debugging** — reproduce failures with exact actor, object ID, and endpoint.

The CLI should be run strictly one command at a time (concurrent CLI invocations cause auth conflicts).

Use direct REST calls instead when:

- MCP remains unavailable after setup attempts
- Box CLI is not installed, cannot be authenticated, or is not an option for the user
- The user explicitly confirms they want REST fallback

For REST fallback request patterns and auth guidance, read `references/rest-calls.md`.

## Safe auth checks

Use these commands to confirm CLI availability and auth without printing secrets:

```bash
command -v box
box --version
box users:get me --json
```

Do not use `box configure:environments:get --current` as a routine check because it can print sensitive environment details.

## Authentication paths

These commands are interactive — they open a browser or prompt for input. Tell the user to run them in their own terminal rather than executing them as the agent.

- Fastest OAuth flow with the official Box CLI app:
  - `box login -d`
- OAuth with your own Box app:
  - `box login --platform-app`
- Add an environment from an app config file:
  - `box configure:environments:add PATH`

Never ask the user to paste credentials, tokens, or secrets into the conversation. If credentials are needed, guide the user to set them as environment variables or in the appropriate config file.

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
