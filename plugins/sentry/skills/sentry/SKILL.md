---
name: "sentry"
description: "Use when the user wants to inspect Sentry data from Codex with the official CLI: issues, events, traces, spans, logs, dashboards, orgs, projects, schema, or authenticated API access. This skill is for investigation and querying, not SDK installation or instrumentation changes."
---

# Sentry CLI

Use this skill for read and investigate workflows inside Sentry. If the user wants to install Sentry, update instrumentation, turn on new SDK features, or fetch guidance from `skills.sentry.dev`, route to `../sentry-setup/SKILL.md` immediately.

## Querying Sentry Data

Use the Sentry CLI as the primary interface. In Codex, the zero-install path is:

```bash
npx -y sentry@latest ...
```

### Core rules

- Prefer CLI commands over raw API calls.
- Use `--json` for structured output when you need to parse results.
- Use `--fields` to keep JSON payloads small.
- Use `--limit` aggressively.
- Prefer `--period` for time filters.
- Prefer direct lookup by ID over list-then-filter when the identifier is already known.
- Let the CLI auto-detect org/project context when possible; add explicit `org/project` scoping when detection fails or resolves incorrectly.
- Never print or store auth tokens.
- Do not dump large raw JSON into the conversation context.
- Prefer noun-first commands exactly as the CLI exposes them: `issue list`, `trace view`, `event list`, `schema`, `api`.

### Use this skill for

- Investigating recent errors or unresolved issues
- Reading issue details, events, traces, spans, logs, dashboards, orgs, or projects
- Asking Sentry for Seer explanations or plans on an issue
- Exploring the Sentry API surface with `schema`
- Using authenticated raw API access when the dedicated command family is not enough

### Do not use this skill for

- Installing Sentry into an app
- Adding or updating `instrumentation.ts`, `global-error.tsx`, SDK init files, or DSNs
- Turning on features like Replay, Profiling, Logs, AI monitoring, or Crons in source code
- SDK upgrades or instrumentation migrations

For those tasks, switch to `../sentry-setup/SKILL.md`.

### Authentication

- Prefer CLI-native auth with:

```bash
npx -y sentry@latest auth login
```

- To verify auth status:

```bash
npx -y sentry@latest auth status --json
```

- Token-based auth is allowed when interactive login is not appropriate, but do not ask the user to paste tokens into chat.
- If the user is not authenticated, tell them to run `npx -y sentry@latest auth login` locally and confirm when ready.

### Fast validation

Before relying on a command family for the first time in a session, it is reasonable to confirm the CLI surface:

```bash
npx -y sentry@latest --help
npx -y sentry@latest auth --help
npx -y sentry@latest issue --help
npx -y sentry@latest trace --help
```

### Common commands

```bash
npx -y sentry@latest issue list --limit 5
npx -y sentry@latest issue view PROJ-123
npx -y sentry@latest issue explain PROJ-123
npx -y sentry@latest issue plan PROJ-123
npx -y sentry@latest event list PROJ-123 --limit 10
npx -y sentry@latest event view my-org/my-project/<event-id>
npx -y sentry@latest trace list --limit 5
npx -y sentry@latest trace view my-org/my-project/<trace-id>
npx -y sentry@latest trace logs my-org/<trace-id>
npx -y sentry@latest span list my-org/my-project/<trace-id>
npx -y sentry@latest log list --limit 20
npx -y sentry@latest dashboard list
npx -y sentry@latest org list
npx -y sentry@latest project list
npx -y sentry@latest schema issues
npx -y sentry@latest api /api/0/organizations/my-org/
```

### When to use `schema` vs `api`

- Use `schema` first when you need to discover the shape of an endpoint or confirm the supported path.
- Use `api` only after checking whether a dedicated command family already exists.
- Prefer `issue`, `event`, `trace`, `span`, `log`, `dashboard`, `org`, and `project` over `api`.

Examples:

```bash
npx -y sentry@latest schema "GET /api/0/organizations/{organization_id_or_slug}/issues/"
npx -y sentry@latest api /api/0/organizations/my-org/projects/ --json
```

### Large JSON handling

Sentry JSON can be very large. Do not paste raw `--json` output into context.

Use a temp file, then inspect it with `jq`:

```bash
npx -y sentry@latest trace view my-org/my-project/<trace-id> --json > /tmp/sentry-trace.json
jq '.spans[] | {op, description, duration}' /tmp/sentry-trace.json
```

```bash
npx -y sentry@latest issue list --json --fields shortId,title,status,count --limit 10 > /tmp/sentry-issues.json
jq '.[] | {shortId, title, status, count}' /tmp/sentry-issues.json
```

Guidance:
- Default to temp files for `--json` output.
- Extract only the fields needed for the current question.
- Prefer `--fields` plus `jq` over wide tables or full payloads.
- Use `--period` for time filters instead of inventing custom date logic.
- If a single trace or issue dump is large, summarize the subset you actually inspected instead of presenting the whole file.

### Workflow patterns

#### Investigate an issue

```bash
npx -y sentry@latest issue list --query "is:unresolved" --limit 5
npx -y sentry@latest issue view @latest
npx -y sentry@latest issue explain @latest
npx -y sentry@latest issue plan @latest
```

If the user already gave an issue short ID, skip the list step and go straight to `issue view`, `issue events`, `issue explain`, or `issue plan`.

#### Explore traces and performance

```bash
npx -y sentry@latest trace list --limit 5
npx -y sentry@latest trace view my-org/my-project/<trace-id>
npx -y sentry@latest span list my-org/my-project/<trace-id>
npx -y sentry@latest trace logs my-org/<trace-id>
```

#### Inspect logs

```bash
npx -y sentry@latest log list --limit 20
npx -y sentry@latest log list --query "severity:error" --limit 20
```

#### Inspect events

```bash
npx -y sentry@latest event list PROJ-123 --limit 20
npx -y sentry@latest event view my-org/my-project/<event-id>
```

#### Explore schema or raw API

```bash
npx -y sentry@latest schema
npx -y sentry@latest schema issues
npx -y sentry@latest schema "GET /api/0/organizations/{organization_id_or_slug}/issues/"
npx -y sentry@latest api /api/0/organizations/my-org/projects/
```

### Command families to prefer

- `auth`: login, status, identity
- `issue`: list, events, view, explain, plan
- `event`: list, view
- `trace`: list, view, logs
- `span`: list, view
- `log`: list, view
- `dashboard`: list, view
- `org`: list, view
- `project`: list, view
- `schema`: explore supported API surfaces
- `api`: authenticated fallback for endpoints not covered by higher-level commands

## Output expectations

- Summarize findings instead of dumping raw payloads.
- Call out when no results are returned.
- Mention the concrete commands used when that helps the user reproduce or refine the search.
- Redact obvious secrets or PII if they appear in command output.
- If the user actually wants installation or instrumentation work, say that you are switching to `../sentry-setup/SKILL.md`.
