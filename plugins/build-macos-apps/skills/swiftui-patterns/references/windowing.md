# Windowing

## Intent

Use this when choosing the top-level scene model for a native macOS app.

## Choose the scene type deliberately

- Use `WindowGroup(..., id:)` for the primary app window when it should appear at launch, especially in apps that also have a `MenuBarExtra`.
- Use `WindowGroup` for any scene that can have multiple independent instances.
- Use `Window` for singleton utility windows or focused secondary surfaces. In menu-bar-heavy apps, `Window(...)` is better for auxiliary/on-demand windows and may not present the main window automatically at launch.
- Use `Settings` for preferences. Do not bury settings inside the main content flow.
- Use `DocumentGroup` when the app is fundamentally document-driven.

## Example: main app plus utility window

```swift
@main
struct SampleApp: App {
  var body: some Scene {
    WindowGroup("Library", id: "library") {
      LibraryRootView()
    }

    Window("Inspector", id: "inspector") {
      InspectorRootView()
    }

    Settings {
      SettingsView()
    }
  }
}
```

## Opening windows

- Use `openWindow(id:)` when a command, toolbar item, or button should open another scene.
- Keep per-window state in the scene or `@SceneStorage`, not in a single global pile.

## Pitfalls

- Avoid modeling every feature as a pushed destination inside one window.
- Do not use only `Window(...)` for the main launch window in a menu-bar-plus-window app unless you have verified the launch behavior and intentionally want an on-demand auxiliary window.
- Avoid singleton state for window-specific selections or drafts.
- If you need lower-level titlebar, tabbing, or window lifecycle control, switch to `appkit-interop`.
