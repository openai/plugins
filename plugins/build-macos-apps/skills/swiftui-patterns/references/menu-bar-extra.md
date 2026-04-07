# Menu Bar Extra

## Intent

Use this when the app primarily lives in the macOS menu bar instead of a traditional always-open window.

## Core patterns

- Use `MenuBarExtra` for lightweight utilities, status indicators, and quick actions.
- If the app also has a primary main window that should appear at launch, define that scene with `WindowGroup(..., id:)` and use `Window(...)` only for auxiliary/on-demand windows.
- If the menu bar app should still show in the Dock and activate like a normal app, install an app delegate with `@NSApplicationDelegateAdaptor`, call `NSApp.setActivationPolicy(.regular)` during launch, and then `NSApp.activate(ignoringOtherApps: true)`.
- If the app is intentionally menu-bar-only, explicitly document that `.accessory` / no-Dock behavior is expected product behavior rather than a launch bug.
- Keep the menu content concise and action-oriented.
- Keep each visible menu item label to 30 characters or fewer. If the backing content can be longer than that, derive a short display title and open the full text in a separate window or detail pane.
- If the app has deeper workflows, open a dedicated window from the menu bar extra rather than cramming everything into the menu.

## Example

```swift
import AppKit

private func shortMenuTitle(_ title: String) -> String {
  if title.count <= 30 {
    return title
  }
  return String(title.prefix(27)) + "..."
}

final class AppDelegate: NSObject, NSApplicationDelegate {
  func applicationDidFinishLaunching(_ notification: Notification) {
    NSApp.setActivationPolicy(.regular)
    NSApp.activate(ignoringOtherApps: true)
  }
}

@main
struct SampleApp: App {
  @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate

  var body: some Scene {
    WindowGroup("Sample", id: "main") {
      ContentView()
    }

    MenuBarExtra("Sample", systemImage: "bolt.circle") {
      Button(shortMenuTitle("Open Dashboard")) { /* open window */ }
      Divider()
      Button("Quit") {
        NSApplication.shared.terminate(nil)
      }
    }
  }
}
```

## Pitfalls

- Do not rely on a `Window(...)` scene alone for the main launch window in a menu-bar-plus-window app when the product expects a regular window at startup.
- Do not silently ship a no-Dock menu-bar-only app if the user expects a normal app process. Either install the app delegate and switch to `.regular`, or clearly document that `.accessory` behavior is intentional.
- Do not turn the menu bar extra into a tiny, overloaded substitute for a full app window.
- Do not render raw unbounded titles or message bodies as menu items. Long labels quickly blow out the menu width and should be capped to 30 characters with a short display title.
- If the extra needs advanced status item customization or AppKit menu control, use `appkit-interop`.
