# /build-and-run-macos-app

Create or update the project-local macOS `build_and_run.sh` script, wire the
Codex app Run button, then use that script as the default build/run entrypoint.

## Arguments

- `scheme`: Xcode scheme name (optional)
- `workspace`: path to `.xcworkspace` (optional)
- `project`: path to `.xcodeproj` (optional)
- `product`: SwiftPM executable product name (optional)
- `mode`: `run`, `debug`, `logs`, `telemetry`, or `verify` (optional, default: `run`)
- `app_name`: process/app name to stop before relaunching (optional)

## Workflow

1. Detect whether the repo uses an Xcode workspace, Xcode project, or SwiftPM package.
2. If the workspace is not inside git yet, run `git init` at the project root so Codex app git-backed features unlock.
3. Create or update `script/build_and_run.sh` so it always stops the current app, builds the macOS target, and launches the fresh result.
4. For SwiftPM, keep raw executable launch only for true CLI tools; for AppKit/SwiftUI GUI apps, create a project-local `.app` bundle and launch it with `/usr/bin/open -n`.
5. Support optional script flags for `--debug`, `--logs`, `--telemetry`, and `--verify`.
6. Follow the canonical bootstrap contract in `../skills/build-run-debug/references/run-button-bootstrap.md` for the exact script shape and `.codex/environments/environment.toml` format.
7. Run the script in the requested mode and summarize any build, script, or launch failure.

## Guardrails

- Do not initialize a nested git repo inside an existing parent checkout.
- Do not leave stale `Run` actions pointing at old script paths.
- Keep the no-flag script path simple: kill, build, run.
- Use `--debug`, `--logs`, `--telemetry`, or `--verify` only when the user asks for those modes.
