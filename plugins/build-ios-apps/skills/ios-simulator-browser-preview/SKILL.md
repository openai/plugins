---
name: ios-simulator-browser-preview
description: Preview and control a booted iOS Simulator in the Codex in-app browser with serve-sim. Use when asked to stream or mirror an iOS Simulator into Browser, inspect simulator UI through browser-use tools, install or run serve-sim, expose a simulator preview URL, or pair simulator testing with a browser-visible surface.
---

# iOS Simulator Browser Preview

## Overview
Use `serve-sim` to expose a booted iOS Simulator in the Codex in-app browser. This skill complements `ios-debugger-agent`: use that skill to build, launch, and inspect the app itself, then use this one when the user wants the simulator visible and controllable in Browser.

## Requirements
- macOS with Xcode command line tools available through `xcrun simctl`
- Node.js 18+
- Prefer `npx --yes serve-sim` as the install-and-run path; a global install is not required.

## Default Workflow

### 1) Find the target simulator
- Call `mcp__xcodebuildmcp__list_sims` and select a simulator with state `Booted`.
- If there is exactly one booted simulator, let `serve-sim` auto-detect it.
- If there are multiple booted simulators, pass the exact simulator name to avoid attaching to the wrong device.
- If none are booted and the user also wants to run an app, follow `ios-debugger-agent` first. If they only asked for mirroring, ask them to boot a simulator.

### 2) Start the preview server
- Prefer the browser-preview mode:

```bash
npx --yes serve-sim
```

- With multiple booted simulators or a user-selected target:

```bash
npx --yes serve-sim "iPhone 17 Pro"
```

- Keep the process running while Browser is using the preview.
- Read the `Local:` URL from stdout, usually `http://localhost:3200`.

### 3) Open it in Browser
- Use the `browser` skill for the Codex in-app browser.
- Open the local preview URL from `serve-sim`, usually `http://localhost:3200`.
- Verify the page loaded before claiming success:
  - confirm the page title contains `Simulator`
  - take a screenshot or inspect the visible DOM when the user needs proof
- Prefer the browser preview URL, not the raw stream helper URL, when the user asks to "open the simulator in the browser."

## Controlling The Simulator
- Prefer accessibility snapshots from the preview server when deciding what to interact with:

```bash
curl -sN --max-time 2 http://localhost:3200/ax
```

- Use AX labels and frames to identify the real simulator target semantically, for example `Lire la suite`, `Tout accepter`, or `Tout refuser`, instead of guessing from pixels.
- Use AX for targeting and the simulator preview for visual confirmation. If AX is unavailable or incomplete, fall back to screenshots and visible inspection.
- When `serve-sim` exposes the right target in AX but there is no direct AX activation primitive, use the AX frame center to send a short tap through the control channel rather than eyeballing coordinates from the preview stream.
- Use Browser computer-use for the preview shell itself or as a visual fallback, not as the first choice for precise in-simulator controls; the simulator content is still a streamed surface.
- After each interaction, re-check AX or capture a fresh screenshot before continuing.

## Inspection APIs
Use the preview-server APIs when Browser needs more than pixels:

- `GET /ax` streams normalized accessibility snapshots for the visible simulator UI. Use this first for semantic UI inspection, target discovery, and post-action verification.
  - Snapshot shape: `screen` plus `elements[]`
  - Each element includes `id`, `path`, `label`, `value`, `role`, `type`, `enabled`, and `frame`
- `GET /api` returns the active preview state, including the selected device plus helper `url`, `streamUrl`, and `wsUrl`. Use it to confirm which simulator is attached.
- `GET /appstate` streams foreground-app changes such as `bundleId`, `pid`, and `isReactNative`. Use it to verify that the expected app actually came to the front.
- `GET /logs` streams simulator logs as SSE. Use it when the user needs runtime proof alongside visible behavior.
- `GET /devtools` lists inspectable Safari or `WKWebView` targets when present. Use it only for web content inside the simulator, not as a general native-view inspector.

Prefer the preview-server endpoints on `localhost:3200` for agent workflows. The lower-level helper also exposes raw endpoints on its stream port, but `/ax` on the preview server is already normalized for decision-making.

## Control APIs
After locating the target with `/ax`, prefer `serve-sim` control commands over pixel guessing:

```bash
npx --yes serve-sim gesture '{"type":"begin","x":0.5,"y":0.5}'
npx --yes serve-sim gesture '{"type":"end","x":0.5,"y":0.5}'
npx --yes serve-sim button home
npx --yes serve-sim rotate landscape_left
```

- Use `gesture` for taps, swipes, and other normalized-coordinate touch sequences.
- Use `button` for hardware-style controls when the shell action is clearer than a screen gesture.
- Use `rotate` when validating responsive behavior or reproducing orientation-sensitive bugs.
- Use `ca-debug` and `memory-warning` only when the task is specifically about rendering diagnostics or memory-pressure behavior.

## Compatibility Notes
- The core preview, control, `/ax`, `/api`, `/appstate`, and `/logs` flows work for both native apps and Expo or React Native apps because `serve-sim` operates at the simulator layer.
- `/ax` quality depends on the app's accessibility tree. If labels are missing, fall back to screenshots or the native simulator-debugging flow.
- Expo can additionally mount `serve-sim/middleware` inside Metro or another dev server for an embedded `/.sim` route. That is a convenience layer, not a requirement for simulator inspection.
- `/devtools` applies only when the simulator is showing inspectable web content such as Safari or a `WKWebView`.

## Detached Helper Mode
Use detached mode only when the user needs a stream helper for another dev server or middleware integration, not as the default browser-preview flow.

```bash
npx --yes serve-sim --detach --quiet
```

- This returns JSON for the helper stream, such as `url`, `streamUrl`, `wsUrl`, and `device`.
- Detached mode exposes the helper stream, usually on `127.0.0.1:3100`; it does not replace the preview UI on `localhost:3200`.
- For embedded dev-server integration, follow the upstream `serve-sim/middleware` instructions instead of inventing a proxy.

## Lifecycle & Recovery
- Inspect active helpers:

```bash
npx --yes serve-sim --list
```

- Stop helpers when finished:

```bash
npx --yes serve-sim --kill
```

- If `serve-sim` reports a stale helper for a device that is no longer booted, let it clean up the helper and continue.
- If the command fails with CoreSimulator permission/service errors from inside a restricted shell, rerun it in an environment that can access the local simulator service before concluding the tool is broken.

## When To Use What
- Need to build, launch, tap, type, or capture native simulator state: use `ios-debugger-agent`.
- Need the simulator visible inside Codex Browser or available to browser automation: use this skill.
- Need both: run the iOS debugger flow first, then open the browser preview.

## Verified Behavior
- Direct preview mode opens a browser UI on `http://localhost:3200`.
- The preview page is controllable in Browser and exposes visible controls such as Home, rotate, and tools.
- The preview server also exposes normalized simulator accessibility snapshots at `/ax`, which are better than raw pixel guessing for choosing in-simulator controls.
- `--detach --quiet` returns the stream helper JSON and is better suited to middleware or custom dev-server embedding than direct human preview.
