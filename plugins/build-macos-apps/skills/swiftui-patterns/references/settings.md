# Settings

## Intent

Use this when building a native macOS settings window with SwiftUI.

## Core patterns

- Declare a dedicated `Settings` scene in the app.
- Keep settings content in a separate root view.
- Use `@AppStorage` for user preferences that should persist.
- Prefer tabs, sections, or a split settings layout over deep push navigation.
- Use `SettingsLink` or `OpenSettingsAction` for in-app entry points.

## Example

```swift
@main
struct SampleApp: App {
  var body: some Scene {
    WindowGroup {
      ContentView()
    }

    Settings {
      SettingsView()
    }
  }
}

struct SettingsView: View {
  @AppStorage("showSidebarIcons") private var showSidebarIcons = true

  var body: some View {
    TabView {
      Form {
        Toggle("Show Sidebar Icons", isOn: $showSidebarIcons)
      }
      .tabItem { Label("General", systemImage: "gearshape") }
    }
    .frame(width: 460, height: 260)
    .scenePadding()
  }
}
```

## Pitfalls

- Do not reuse an iOS full-screen settings screen unless the app really is a direct Catalyst-style port.
- Keep settings rows simple and accessible.
- If settings require custom panels, responders, or first-responder integration, use `appkit-interop`.
