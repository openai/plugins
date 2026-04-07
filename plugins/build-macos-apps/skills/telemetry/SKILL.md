---
name: telemetry
description: Add lightweight runtime telemetry and debug instrumentation to macOS apps, then verify those events after building and running. Use when wiring `Logger` / `os.Logger`, adding log points for window/sidebar/menu-bar actions, reading runtime logs from Console or `log stream`, or confirming that expected events fire after a local run.
---

# Telemetry

## Quick Start

Use this skill to add lightweight app instrumentation that helps debug behavior
without turning the codebase into a logging landfill. Prefer Apple's unified
logging APIs and verify the events after a build/run loop.

## Core Guidelines

- Prefer `Logger` from the `OSLog` framework for structured app logs.
- Give each feature a clear subsystem/category pair so runtime filtering stays easy.
- Log meaningful user and app lifecycle events: window opening, sidebar selection changes, menu commands, menu bar extra actions, sync/load milestones, and unexpected fallback paths.
- Keep info logs concise and stable. Use debug logs for noisy state details.
- Do not log secrets, auth tokens, personal data, or raw document contents.
- Add signposts only when measuring timing or performance spans; do not overinstrument by default.

## Minimal Logger Pattern

```swift
import OSLog

private let logger = Logger(
  subsystem: Bundle.main.bundleIdentifier ?? "SampleApp",
  category: "Sidebar"
)

@MainActor
func selectItem(_ item: SidebarItem) {
  logger.info("Selected sidebar item: \(item.id, privacy: .public)")
  selection = item.id
}
```

Use feature-specific categories like `Windowing`, `Commands`, `MenuBar`, `Sidebar`,
`Sync`, or `Import` so logs can be filtered quickly.

## Workflow

1. Identify the behavior that needs observability.
   - Window open/close
   - Sidebar or inspector selection changes
   - Menu or keyboard command actions
   - Menu bar extra actions
   - Background load/sync/import events
   - Error and recovery paths

2. Add the smallest useful instrumentation.
   - Create one `Logger` per feature area or type.
   - Log action boundaries and key state transitions.
   - Prefer one high-signal line per user action over noisy value dumps.

3. Build and run the app.
   - Use `build-run-debug` for the build/run loop.
   - If `script/build_and_run.sh` exists, prefer `./script/build_and_run.sh --telemetry` for live telemetry checks or `./script/build_and_run.sh --logs` for broader process logs.
   - Exercise the UI or command path that should emit telemetry.

4. Read runtime logs and verify the event fired.
   - Use Console.app with a process/subsystem filter when that is the fastest manual check.
   - Use `log stream --style compact --predicate 'process == "AppName"'` for live terminal verification.
   - Prefer tighter predicates when you know the subsystem/category:
     `log stream --style compact --predicate 'subsystem == "com.example.app" && category == "Sidebar"'`

5. Tighten or remove instrumentation.
   - If the event fires, keep only the logs that remain useful for future debugging.
   - If it does not fire, move the log closer to the suspected control path and rerun.

## Verification Checklist

- The app builds after telemetry changes.
- The relevant action emits exactly one clear log line or a small bounded sequence.
- The log can be filtered by process, subsystem, or category.
- No sensitive payloads are written to unified logs.
- Noisy temporary debug logs are removed or demoted before finishing.

## Guardrails

- Do not use `print` as the primary app telemetry mechanism for macOS app code.
- Do not leave a dense trail of permanent debug logs around every state mutation.
- Do not claim an event is wired correctly until you have a concrete verification path through Console, `log stream`, or captured process output.
- If the debugging task is mostly about crash/backtrace analysis rather than action telemetry, switch to `build-run-debug`.
