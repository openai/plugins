# /setup-codex-run-actions

Wire the current Expo project into the Codex app action bar.

## Arguments

- `root`: Expo app root, if not the current directory (optional)
- `actions`: comma-separated extra buttons such as `ios,android,web,dev-client,doctor,export-web` (optional)
- `run`: whether to start the Expo dev server after setup (optional, default: false)

## Workflow

1. Use the `codex-expo-run-actions` skill.
2. Confirm the target root is an Expo app before editing.
3. Create or update `script/build_and_run.sh` using the skill reference.
4. Create or update `.codex/environments/environment.toml`.
5. Always wire one primary `Run` action to `./script/build_and_run.sh`.
6. Add optional actions only when requested.
7. Validate with `bash -n ./script/build_and_run.sh` and `./script/build_and_run.sh --help`.
8. Start the dev server only when `run=true` or the user explicitly asks.

## Output

Report the script path, environment file path, action names, and validation command results.
