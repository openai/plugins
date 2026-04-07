# Windows and Panels

## Intent

Use this when SwiftUI scenes are not enough for the required macOS window or panel behavior.

## Common cases

- Accessing the backing `NSWindow`
- Configuring titlebar or toolbar behavior
- Presenting `NSOpenPanel` or `NSSavePanel`
- Managing utility panels or floating windows

## Core patterns

- Prefer SwiftUI `Window`, `WindowGroup`, and `openWindow` first.
- Use AppKit only for window features SwiftUI does not expose cleanly.
- Keep file open/save panels behind a small service or helper instead of scattering panel setup throughout the view tree.

## Example: open panel

```swift
@MainActor
func chooseFile() -> URL? {
  let panel = NSOpenPanel()
  panel.canChooseFiles = true
  panel.canChooseDirectories = false
  panel.allowsMultipleSelection = false
  return panel.runModal() == .OK ? panel.url : nil
}
```

## Pitfalls

- Do not let random views own long-lived `NSWindow` references.
- Keep floating panels and utility windows consistent with the scene model.
- If the behavior is really just settings or a secondary scene, go back to `swiftui-patterns`.
