---
name: codex-expo-run-actions
description: Wire Expo projects into the Codex app with project-local run scripts and .codex/environments/environment.toml actions. Use when the user wants the Codex app Run button, build/run actions, action buttons, or a stable Expo start/run workflow from Codex.
version: 1.0.0
license: MIT
---

# Codex Run Actions for Expo

Use this skill to connect an Expo project to the Codex app action bar.

The goal is one project-local script plus `.codex/environments/environment.toml`,
so the user can press `Run` in the Codex app and see the Expo CLI / Metro logs in
an action terminal.

## Workflow

1. Confirm the current workspace is an Expo app.
   - Look for `package.json`.
   - Look for `app.json`, `app.config.js`, `app.config.ts`, or `expo` in `package.json`.
   - Do not wire the Codex action at a monorepo root if the Expo app is in a child package.

2. Discover the package runner.
   - Prefer the package manager declared in `packageManager`.
   - Otherwise infer from lockfiles.
   - The generated run script should still have a safe fallback to `npx expo`.

3. Create or update `script/build_and_run.sh`.
   - Use the reference file for the script shape.
   - Default no-argument mode starts the Expo dev server: `expo start`.
   - Keep the dev server in the foreground so the Codex action terminal owns logs and Ctrl-C behavior.
   - Support optional modes for direct buttons:
     - `--ios` starts Expo and opens iOS simulator.
     - `--android` starts Expo and opens Android.
     - `--web` starts Expo for web.
     - `--dev-client` starts in dev-client mode.
     - `--tunnel` starts a tunnel.
     - `--export-web` exports web.

4. Write `.codex/environments/environment.toml`.
   - Always add or update one primary action named `Run`.
   - Wire `Run` to `./script/build_and_run.sh`.
   - Add direct `Run iOS`, `Run Android`, `Run Web`, or `Run Dev Client`
     actions only when the user asks for those buttons or the project clearly needs them.
   - If the environment file already exists, update the existing matching action instead of duplicating it.

5. Use the action script as the default local run path.
   - After wiring, run `./script/build_and_run.sh --help` or a short non-server mode if you need to sanity-check syntax.
   - Do not start a long-lived Metro server during a setup-only task unless the user asked you to run the app.

## References

- `references/expo-run-button-bootstrap.md`: canonical Expo `script/build_and_run.sh` and Codex environment action examples.

## Guardrails

- Try Expo Go / `expo start` first; do not default the Codex Run button to `expo run:ios`, `expo run:android`, prebuild, or EAS Build.
- Do not wire cloud actions such as `eas build`, `eas submit`, or store deployment into Codex buttons unless the user explicitly asks and accepts the auth / time / cost tradeoff.
- Do not create a nested git repo.
- Do not put secrets in `.codex/environments/environment.toml` or in the run script.
- Do not background Metro from the run script; the action terminal should show the active server logs.
- Do not hard-code npm if the project uses pnpm, yarn, or bun.

## Output Expectations

When setup changes are made, summarize:

- the Expo app root you wired
- the run script path
- the Codex environment file path
- the actions added or updated
- how to launch the same path from shell
