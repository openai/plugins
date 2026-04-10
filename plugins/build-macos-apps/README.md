# Build macOS Apps Plugin

This plugin packages macOS-first development workflows in `plugins/build-macos-apps`.

It currently includes these skills:

- `build-run-debug`
- `test-triage`
- `signing-entitlements`
- `swiftpm-macos`
- `packaging-notarization`
- `swiftui-patterns`
- `liquid-glass`
- `window-management`
- `appkit-interop`
- `view-refactor`
- `telemetry`

## What It Covers

- discovering local Xcode workspaces, projects, and Swift packages
- building and running macOS apps with shell-first desktop workflows
- creating one project-local `script/build_and_run.sh` entrypoint and wiring `.codex/environments/environment.toml` so the Codex app Run button works
- implementing native macOS SwiftUI scenes, menus, settings, toolbars, and multiwindow flows
- adopting modern macOS Liquid Glass and design-system guidance with standard SwiftUI structures, toolbars, search, controls, and custom glass surfaces
- tailoring SwiftUI windows with title/toolbar styling, material-backed container backgrounds, minimize/restoration behavior, default and ideal placement, borderless window style, and launch behavior
- bridging into AppKit for representables, responder-chain behavior, panels, and other desktop-only needs
- refactoring large macOS view files toward stable scene, selection, and command structure
- adding lightweight `Logger` / `os.Logger` instrumentation for windows, sidebars, menu commands, and menu bar actions
- reading and verifying runtime events with Console, `log stream`, and process logs
- triaging failing unit, integration, and UI-hosted macOS tests
- debugging launch failures, crashes, linker problems, and runtime regressions
- inspecting signing identities, entitlements, hardened runtime, and Gatekeeper issues
- preparing packaging and notarization workflows for distribution

## What It Does Not Cover

- iOS, watchOS, or tvOS simulator control
- desktop UI automation
- App Store Connect release management
- pixel-perfect visual design or design-system generation

## Plugin Structure

The plugin lives at:

- `plugins/build-macos-apps/`

with this shape:

- `.codex-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata and points Codex at the plugin contents

- `agents/`
  - plugin-level agent metadata
  - currently includes `agents/openai.yaml` for the OpenAI surface

- `commands/`
  - reusable workflow entrypoints for common macOS development tasks

- `skills/`
  - the actual skill payload
  - each skill keeps the normal skill structure (`SKILL.md`, optional
    `agents/`, `references/`, `assets/`, `scripts/`)

## Notes

This plugin is currently skills-first at the plugin level. It does not ship a
plugin-local `.mcp.json`, matching the public `plugins/build-ios-apps` shape.

The default posture is shell-first. Unlike the iOS build plugin, this plugin
does not assume simulator tooling or touch-driven UI inspection for its main
workflows. The core execution model leans on `xcodebuild`, `swift`, `open`,
`lldb`, `codesign`, `spctl`, `plutil`, and `log stream`, with a compact desktop
UI layer for native SwiftUI scene design, AppKit interop, and macOS-specific
refactoring.
