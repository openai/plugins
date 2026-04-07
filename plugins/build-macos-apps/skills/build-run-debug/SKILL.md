---
name: build-run-debug
description: Build, run, and debug local macOS apps and desktop executables using shell-first Xcode and Swift workflows. Use when asked to build a Mac app, launch it, diagnose compiler or linker failures, inspect startup problems, or debug desktop-only runtime issues.
---

# Build / Run / Debug

## Quick Start

Use this skill to set up one project-local `script/build_and_run.sh` entrypoint,
wire `.codex/environments/environment.toml` so the Codex app shows a Run button,
then use that script as the default build/run path.

Prefer shell-first workflows:

- `./script/build_and_run.sh` as the single kill + build + run entrypoint once it exists
- `xcodebuild` for Xcode workspaces or projects
- `swift build` plus raw executable launch inside that script for true SwiftPM command-line tools
- `swift build` plus project-local `.app` bundle staging and `/usr/bin/open -n` launch for SwiftPM AppKit/SwiftUI GUI apps
- optional script flags for `lldb`, `log stream`, telemetry verification, or post-launch process checks

Do not assume simulators, touch interaction, or mobile-specific tooling.

If an Xcode-aware MCP surface is already available and the user explicitly wants
it, use it only where it fits. Keep that usage narrow and honest: prefer it for
Xcode-oriented discovery, logging, or debugging support, and do not force
simulator-specific workflows onto pure macOS tasks.

## Workflow

1. Discover the project shape.
   - Check whether the workspace is already inside a git repo with `git rev-parse --is-inside-work-tree`.
   - If no git repo is present, run `git init` at the project/workspace root before building so Codex app git-backed features are available. Never run `git init` inside a nested subdirectory when the current workspace already belongs to a parent repo.
   - Look for `.xcworkspace`, `.xcodeproj`, and `Package.swift`.
   - If more than one candidate exists, explain the default choice and the ambiguity.

2. Resolve the runnable target and process name.
   - For Xcode, list schemes and prefer the app-producing scheme unless the user names another one.
   - For SwiftPM, identify executable products when possible.
   - Split SwiftPM launch handling by product type:
     - use raw executable launch only for true command-line tools,
     - use a generated project-local `.app` bundle for AppKit/SwiftUI GUI apps.
   - Determine the app/process name to kill before relaunching.

3. Create or update `script/build_and_run.sh`.
   - Make the script project-specific and executable.
   - It should always:
     1. stop the existing running app/process if present,
     2. build the macOS target,
     3. launch the freshly built app or executable.
   - Add optional flags for debugging/log inspection:
     - `--debug` to launch under `lldb` or attach the debugger
     - `--logs` to stream process logs after launch
     - `--telemetry` to stream unified logs filtered to the app subsystem/category
     - `--verify` to launch the app and confirm the process exists with `pgrep -x <AppName>`
   - Keep the default no-flag path simple: kill, build, run.
   - Prefer writing one script that owns this workflow instead of repeatedly asking the agent to manually run `swift build`, locate the artifact, then invoke an ad hoc run command.
   - For SwiftPM GUI apps, make the script build the product, create `dist/<AppName>.app`, copy the binary to `Contents/MacOS/<AppName>`, generate a minimal `Contents/Info.plist` with `CFBundlePackageType=APPL`, `CFBundleExecutable`, `CFBundleIdentifier`, `CFBundleName`, `LSMinimumSystemVersion`, and `NSPrincipalClass=NSApplication`, then launch with `/usr/bin/open -n <bundle>`.
   - For SwiftPM GUI `--logs` and `--telemetry`, launch the bundle with `/usr/bin/open -n` first, then stream unified logs with `/usr/bin/log stream --info ...`.
   - Do not recommend direct SwiftPM executable launch for AppKit/SwiftUI GUI apps.
   - Use `references/run-button-bootstrap.md` as the canonical source for the
     script shape and exact environment file format. Do not fork a second
     authoritative snippet in another skill or command.

4. Write `.codex/environments/environment.toml` at the project root once the script exists.
   - Use this exact placement: `.codex/environments/environment.toml`.
   - Use the exact action shape in `references/run-button-bootstrap.md`.
   - This file is what gives the user a Codex app Run button wired to the script.
   - If the project already has this file, update the `Run` action command to point at `./script/build_and_run.sh` instead of creating a duplicate action.

5. Build and run through the script.
   - Default to `./script/build_and_run.sh`.
   - Use `./script/build_and_run.sh --debug`, `--logs`, `--telemetry`, or `--verify` when the user asks for debugger/log/telemetry/process verification support.

6. Summarize failures correctly.
   - Classify the blocker as compiler, linker, signing, build settings, missing SDK/toolchain, script bug, or runtime launch.
   - Quote the smallest useful error snippet and explain what it means.

7. Debug the right way.
   - Use the script's `--logs` or `--telemetry` mode for config, entitlement, sandbox, and action-event verification.
   - For SwiftPM GUI apps, if the app bundle launches but its window still does not come forward, check whether the entrypoint needs `NSApp.setActivationPolicy(.regular)` and `NSApp.activate(ignoringOtherApps: true)`.
   - Use the script's `--debug` mode or direct `lldb` if symbolized crash debugging is needed.
   - If the user needs to instrument and verify specific window, sidebar, menu, or menu bar actions, switch to `telemetry`.
   - Keep evidence tight and user-facing.

8. Use Xcode-aware MCP tooling only when it helps.
   - If the user explicitly asks for XcodeBuildMCP and it is already available, prefer it over ad hoc setup.
   - Use the MCP for Xcode-aware discovery or debug/logging workflows when the available tool surface clearly matches the task.
   - Fall back to shell commands immediately when the MCP does not provide a clean macOS path.

## Preferred Commands

- Project discovery:
  - `find . -name '*.xcworkspace' -o -name '*.xcodeproj' -o -name 'Package.swift'`
- Scheme discovery:
  - `xcodebuild -list -workspace <workspace>`
  - `xcodebuild -list -project <project>`
- Build/run:
  - `./script/build_and_run.sh`
  - `./script/build_and_run.sh --debug`
  - `./script/build_and_run.sh --logs`
  - `./script/build_and_run.sh --telemetry`
  - `./script/build_and_run.sh --verify`

## References

- `references/run-button-bootstrap.md`: canonical `build_and_run.sh` and `.codex/environments/environment.toml` contract.

## Guardrails

- Prefer the narrowest command that proves or disproves the current theory.
- Do not leave the user with a one-off manual command chain once a stable `build_and_run.sh` script can own the workflow.
- Do not write `.codex/environments/environment.toml` before the run script exists, and do not point the Run action at a stale script path.
- Do not launch a SwiftUI/AppKit SwiftPM GUI app as a raw executable unless the user explicitly wants to diagnose that failure mode: it can produce no Dock icon, no foreground activation, and missing bundle identifier warnings. Keep raw executable launch only for true command-line tools.
- Do not claim UI state you cannot inspect directly.
- Do not describe mobile or simulator workflows as if they apply to macOS.
- If build output is huge, summarize the first real blocker and point to follow-up commands.

## Output Expectations

Provide:
- the detected project type
- the script path and Codex environment action you configured, if applicable
- the command you ran
- whether build and launch succeeded
- the top blocker if they failed
- the smallest sensible next action
