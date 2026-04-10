---
name: "sentry"
description: "Guide for using the Sentry CLI to inspect issues, events, traces, spans, logs, dashboards, organizations, projects, and authenticated API data from Codex via `npx -y sentry@latest`. Also covers setting up Sentry SDKs by fetching expert setup guides from skills.sentry.dev."
---

# Sentry

This skill covers two capabilities:
1. Querying Sentry with the official CLI via `npx -y sentry@latest`
2. Setting up Sentry SDKs by fetching expert setup guides from the Sentry Skills Registry

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
- Prefer direct lookup by ID over list-then-filter when the identifier is already known.
- Let the CLI auto-detect org/project context when possible; add explicit `org/project` scoping when detection fails or resolves incorrectly.
- Never print or store auth tokens.
- Do not dump large raw JSON into the conversation context.

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

### Workflow patterns

#### Investigate an issue

```bash
npx -y sentry@latest issue list --query "is:unresolved" --limit 5
npx -y sentry@latest issue view @latest
npx -y sentry@latest issue explain @latest
npx -y sentry@latest issue plan @latest
```

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

#### Explore schema or raw API

```bash
npx -y sentry@latest schema
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

## Setting Up Sentry in a Project

When the user asks to set up Sentry, install Sentry, add monitoring, configure Sentry for a platform, or upgrade an SDK, fetch the appropriate skill from the Sentry Skills Registry.

### Required flow

Do not jump straight into installation steps.

1. Detect the platform from the project files.
2. Tell the user what platform was detected and which Sentry SDK skill matches it.
3. Confirm that recommendation before fetching the specific SDK skill.
4. Read the fetched SDK skill carefully and follow it instead of improvising.

### Fetch the Sentry skills

Use `curl -sL` to download the full skill markdown. Do not use summarizing fetch tools for these long skill files.

```bash
curl -sL https://skills.sentry.dev/sdks
curl -sL https://skills.sentry.dev/workflows
curl -sL https://skills.sentry.dev/features
curl -sL https://skills.sentry.dev/<skill-name>/SKILL.md
```

### Entry points

- Platform detection and SDK install: `https://skills.sentry.dev/sdks`
- Workflow skills: `https://skills.sentry.dev/workflows`
- Feature skills: `https://skills.sentry.dev/features`
- Full index: `https://skills.sentry.dev/`

### SDK skills by platform

- Android: `https://skills.sentry.dev/sentry-android-sdk/SKILL.md`
- Browser JavaScript: `https://skills.sentry.dev/sentry-browser-sdk/SKILL.md`
- Cloudflare Workers/Pages: `https://skills.sentry.dev/sentry-cloudflare-sdk/SKILL.md`
- Apple platforms: `https://skills.sentry.dev/sentry-cocoa-sdk/SKILL.md`
- .NET: `https://skills.sentry.dev/sentry-dotnet-sdk/SKILL.md`
- Elixir: `https://skills.sentry.dev/sentry-elixir-sdk/SKILL.md`
- Flutter / Dart: `https://skills.sentry.dev/sentry-flutter-sdk/SKILL.md`
- Go: `https://skills.sentry.dev/sentry-go-sdk/SKILL.md`
- NestJS: `https://skills.sentry.dev/sentry-nestjs-sdk/SKILL.md`
- Next.js: `https://skills.sentry.dev/sentry-nextjs-sdk/SKILL.md`
- Node.js / Bun / Deno: `https://skills.sentry.dev/sentry-node-sdk/SKILL.md`
- PHP: `https://skills.sentry.dev/sentry-php-sdk/SKILL.md`
- Python: `https://skills.sentry.dev/sentry-python-sdk/SKILL.md`
- React Native / Expo: `https://skills.sentry.dev/sentry-react-native-sdk/SKILL.md`
- React: `https://skills.sentry.dev/sentry-react-sdk/SKILL.md`
- Ruby: `https://skills.sentry.dev/sentry-ruby-sdk/SKILL.md`
- Svelte / SvelteKit: `https://skills.sentry.dev/sentry-svelte-sdk/SKILL.md`

### Workflow and feature skills

- Fix issues from Sentry: `https://skills.sentry.dev/sentry-fix-issues/SKILL.md`
- Resolve Sentry PR review comments: `https://skills.sentry.dev/sentry-code-review/SKILL.md`
- Review PRs for Seer bug predictions: `https://skills.sentry.dev/sentry-pr-code-review/SKILL.md`
- Upgrade Sentry JS SDK: `https://skills.sentry.dev/sentry-sdk-upgrade/SKILL.md`
- Create alerts: `https://skills.sentry.dev/sentry-create-alert/SKILL.md`
- OpenTelemetry Collector setup: `https://skills.sentry.dev/sentry-otel-exporter-setup/SKILL.md`
- AI agent monitoring: `https://skills.sentry.dev/sentry-setup-ai-monitoring/SKILL.md`

### Platform detection

When the user does not specify a platform, detect it from project files:

- `package.json` with `next` -> Next.js
- `package.json` with `@nestjs/core` -> NestJS
- `package.json` with `react-native` -> React Native
- `package.json` with `react` and no framework -> React
- `package.json` alone -> Node.js / Bun / Deno
- `build.gradle` with Android plugin -> Android
- `Podfile` or `*.xcodeproj` -> Apple platforms
- `pubspec.yaml` -> Flutter
- `requirements.txt` or `pyproject.toml` -> Python
- `go.mod` -> Go
- `Gemfile` -> Ruby
- `composer.json` -> PHP
- `mix.exs` -> Elixir
- `*.csproj` or `*.sln` -> .NET
- `wrangler.toml` -> Cloudflare
- `svelte.config.js` -> Svelte

Use these priority rules when multiple matches are possible:

- Prefer Next.js over React or generic Node.js.
- Prefer NestJS over generic Node.js.
- Prefer Cloudflare over generic Node.js.
- Prefer React Native over React.
- Prefer the framework-specific skill over the language-only skill when both match.

After detection, state the recommendation explicitly, for example:

```text
I found a Next.js app, so the right Sentry setup skill is sentry-nextjs-sdk.
If that matches your intent, I’ll fetch that skill and follow it.
```

Then fetch the matching SDK skill and follow it directly. If there is no clear match, fall back to Sentry docs.

## Output expectations

- Summarize findings instead of dumping raw payloads.
- Call out when no results are returned.
- Mention the concrete commands used when that helps the user reproduce or refine the search.
- Redact obvious secrets or PII if they appear in command output.
