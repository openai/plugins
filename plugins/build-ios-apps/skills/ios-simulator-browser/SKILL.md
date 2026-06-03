---
name: ios-simulator-browser
description: Mirror an iOS Simulator into the Codex in-app browser and render SwiftUI previews from importable Swift packages in that simulator with hot reload. Use when a user wants to watch or interact with an iOS app in the browser, see a SwiftUI preview outside Xcode Canvas, iterate live on a preview, or capture browser-visible simulator proof.
---

# iOS Simulator Browser

## Browser Workflow

1. Obtain an explicit Simulator UDID from the existing iOS build/run workflow or from `xcrun simctl list devices available`.
2. Start `serve-sim` in a long-running terminal pinned to that simulator. Clean up any tracked stale helper for this simulator before starting, and install a trap so the helper is cleaned up when this terminal exits:

   ```bash
   SIM="<simulator-udid>"
   cleanup_serve_sim() {
     npx --yes serve-sim@latest --kill "$SIM" >/dev/null 2>&1 || true
   }
   trap cleanup_serve_sim EXIT INT TERM HUP
   cleanup_serve_sim
   npx --yes serve-sim@latest "$SIM"
   ```

3. Open the exact local preview URL printed by `serve-sim` in the Codex in-app browser.
4. Verify that a real frame is rendering before reporting success. A loaded page alone is not proof that the simulator stream is healthy.

- Keep the terminal alive while the browser mirror is in use. When finished, stop the terminal and wait for it to exit so the trap runs.
- If the terminal disappeared or did not exit cleanly, run `npx --yes serve-sim@latest --kill "$SIM"` before starting another mirror for that simulator.
- Never run an unscoped `serve-sim --kill`; another thread may own a different simulator mirror.

## SwiftUI Preview Workflow

Use the bundled launcher when the requested previews live in an importable Swift package. Point it at the package manifest and select the target whose previews should be displayed. It generates a disposable host project outside the user's source tree, installs and launches that host in Simulator, and watches the package for edits.

```bash
node <skill-root>/scripts/swiftui-preview-browser.mjs \
  /absolute/path/to/Package.swift \
  --package-target "<target>" \
  --device "<simulator-udid>"
```

- Watch mode is enabled by default. On a Swift package source edit, the launcher rebuilds a generated dylib and hot-swaps it into the running host without relaunching the app.
- The generated host shows every preview variant discovered in the selected Swift Package target with in-simulator page controls. To show a subset instead, pass `--preview-filter <regex[, ...]>`; it matches display names and code identifiers such as `StatusRowView_Previews`.
- Once the launcher prints the selected Simulator UDID, start `serve-sim` for that same UDID and open its printed URL in the in-app browser.

## Support Boundary

- Support Swift Package-backed `PreviewProvider` and `#Preview` declarations through the generated host.
- Do not edit the user's `.xcodeproj`, `.xcworkspace`, `Package.swift`, schemes, or build settings to force preview support.

## Proof

For browser or preview QA, capture a browser screenshot showing the simulator frame. For hot reload QA, also report the launcher's `hot reloaded package preview ... in pid ...` output and show the changed frame after editing.
