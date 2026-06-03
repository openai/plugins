---
name: "sentry-setup"
description: "Use when the user wants to install Sentry, update instrumentation, enable or tune SDK features, or fetch framework-specific setup guidance from skills.sentry.dev. This skill covers platform detection, routing to the right upstream Sentry skill, and applying or updating instrumentation safely."
---

# Sentry Setup

Use this skill for installation and source-code changes: adding Sentry to a project, updating instrumentation, upgrading SDK setup, or enabling features like Replay, Logs, Profiling, AI monitoring, Crons, alerts, and OpenTelemetry-related workflows.

If the user instead wants to inspect live Sentry data, route to `../sentry/SKILL.md`.

## Responsibilities

Use this skill when the user asks to:

- add Sentry to a project
- install `@sentry/...` or another Sentry SDK
- configure Sentry in Next.js, React, Node.js, Python, Go, Cloudflare, or another framework
- update `instrumentation.ts`, `global-error.tsx`, init files, DSNs, or SDK wiring
- enable or adjust Replay, Logs, Profiling, AI monitoring, Crons, alerts, metrics, or tracing
- upgrade an SDK or resolve deprecated Sentry APIs

Do not use this skill for Sentry issue, event, trace, or log investigation. That belongs in `../sentry/SKILL.md`.

## Required flow

Do not skip the routing steps.

1. Detect the project platform from repo files.
2. Tell the user what platform or framework was detected.
3. Recommend the matching upstream Sentry skill or router page.
4. Fetch the specific upstream skill with `curl -sL`.
5. Follow the fetched skill carefully instead of improvising from memory.
6. Only make code changes after the target framework and feature path are clear.

## Fetch rules

Use `curl -sL` because these skill files are long and structured:

```bash
curl -sL https://skills.sentry.dev/sdks
curl -sL https://skills.sentry.dev/workflows
curl -sL https://skills.sentry.dev/features
curl -sL https://skills.sentry.dev/<skill-name>/SKILL.md
```

Primary entry points:

- SDK routing: `https://skills.sentry.dev/sdks`
- Workflow routing: `https://skills.sentry.dev/workflows`
- Feature routing: `https://skills.sentry.dev/features`
- Full index: `https://skills.sentry.dev/`

## Platform detection

Detect the platform from project files before fetching a framework-specific skill:

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
- `wrangler.toml` or `wrangler.jsonc` -> Cloudflare
- `svelte.config.js` -> Svelte

Priority rules:

- Prefer Next.js over React or generic Node.js.
- Prefer NestJS over generic Node.js.
- Prefer Cloudflare over generic Node.js.
- Prefer React Native over React.
- Prefer framework-specific skills over language-only skills.

State the recommendation explicitly before proceeding, for example:

```text
I found a Next.js app, so the right upstream Sentry setup skill is sentry-nextjs-sdk.
I’m fetching that now and will follow its guidance for the instrumentation changes.
```

## SDK skills

Fetch the framework-specific skill that matches the detected platform:

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

## Feature and update routing

Use the framework SDK skill for initial installation, then route to feature or upgrade skills when the user’s ask is narrower:

- SDK upgrades or deprecated APIs: `https://skills.sentry.dev/sentry-sdk-upgrade/SKILL.md`
- AI monitoring: `https://skills.sentry.dev/sentry-setup-ai-monitoring/SKILL.md`
- Alerts: `https://skills.sentry.dev/sentry-create-alert/SKILL.md`
- OpenTelemetry Collector setup: `https://skills.sentry.dev/sentry-otel-exporter-setup/SKILL.md`

If the user is asking about fixing production issues or Sentry PR comments rather than instrumentation, use the workflows router:

- `https://skills.sentry.dev/workflows`

## Feature guidance

When the upstream skill leaves implementation choices open, use these defaults:

- Error monitoring: always include it
- Tracing: default on for server and client frameworks where the upstream skill recommends it
- Replay: recommend for user-facing browser apps
- Logs: recommend when the app already uses structured logging or needs log-to-trace correlation
- Profiling: recommend for performance-sensitive apps only when platform support is clear
- AI monitoring: recommend only when the app actually makes LLM calls
- Crons: recommend only when there are scheduled jobs or cron-like workflows in the codebase

Do not enable optional features blindly. Tie them to the actual app and user request.

## Next.js path

When the detected platform is Next.js:

1. Fetch `https://skills.sentry.dev/sentry-nextjs-sdk/SKILL.md`.
2. Follow its detection steps before editing files.
3. Prefer the official wizard when the user is open to it:

```bash
npx @sentry/wizard@latest -i nextjs
```

4. If the user wants manual changes, follow the current upstream guidance for:
   - `instrumentation-client.ts`
   - `sentry.server.config.ts`
   - `sentry.edge.config.ts`
   - `instrumentation.ts`
   - `app/global-error.tsx` or `pages/_error.tsx`
5. Merge with existing instrumentation files instead of overwriting them.

## Safety rules

- Do not guess SDK APIs when the upstream skill can be fetched.
- Do not overwrite an existing instrumentation file without reading and merging it.
- Do not invent DSNs, orgs, or project names.
- If multiple runtimes exist, make the runtime split explicit.
- Keep changes aligned with the project’s existing package manager and file naming conventions.

## Output expectations

- State the detected platform and the upstream skill you fetched.
- Summarize the exact instrumentation or feature changes you made or recommend.
- Call out any interactive step the user must run themselves, such as browser-driven wizards.
- If the request turns into live issue investigation instead of setup, switch to `../sentry/SKILL.md`.
