---
name: swiftui-patterns
description: Best practices and example-driven guidance for building native macOS SwiftUI scenes and components, including windows, commands, toolbars, settings, split views, inspectors, menu bar extras, and keyboard-driven workflows. Use when creating or refactoring macOS SwiftUI UI, choosing scene types, wiring menus or settings, or needing desktop-specific component patterns and examples.
---

# SwiftUI Patterns

## Quick Start

Choose a track based on your goal:

### Existing project

- Identify the feature or scene and the primary interaction model: document, editor, sidebar-detail, utility window, settings, or menu bar extra.
- Read the nearest existing scene or root view before inventing a new desktop structure.
- Choose the relevant reference from `references/components-index.md`.
- If SwiftUI cannot express the required platform behavior cleanly, use the `appkit-interop` skill rather than forcing a shaky workaround.

### New app scaffolding

- Choose the scene model first: `WindowGroup`, `Window`, `Settings`, `MenuBarExtra`, or `DocumentGroup`.
- If the app combines a normal main window and a `MenuBarExtra`, use `WindowGroup(..., id:)` for the primary window when it should appear at launch. Treat `Window(...)` as a better fit for auxiliary/on-demand singleton windows; in menu-bar-heavy apps, a `Window(...)` scene may not present the main window automatically at launch.
- Before creating the scaffold, check whether the workspace is already inside a git repo with `git rev-parse --is-inside-work-tree`. If not, run `git init` at the project root so Codex app git-backed features are available from the start. Do not initialize a nested repo inside an existing parent checkout.
- For a new app scaffold, also create one project-local `script/build_and_run.sh` and `.codex/environments/environment.toml` so the Codex app Run button works immediately. Use the exact bootstrap contract from `build-run-debug` and its `references/run-button-bootstrap.md` file rather than inventing a second variant here.
- Decide which state is app-wide, scene-scoped, or window-scoped before writing views.
- Use system-adaptive colors and materials by default (`Color.primary`, `Color.secondary`, semantic foreground styles, `.regularMaterial`, etc.) so the app follows Light/Dark mode automatically. Do not hardcode white or light backgrounds unless the user explicitly asks for a fixed theme, and do not reach for opaque `windowBackgroundColor` fills for root panes by default.
- Pick the references for the first feature surface you need: windowing, commands, split layouts, or settings.

## General Rules To Follow

- Design for pointer, keyboard, menus, and multiple windows.
- Keep scenes explicit. A separate settings window, utility window, or menu bar extra should be modeled as its own scene, not hidden inside one monolithic `ContentView`.
- Prefer system desktop affordances: `commands`, toolbars, sidebars, inspectors, contextual menus, and `searchable`.
- For menu bar apps, keep `MenuBarExtra` item titles and action labels short and scannable. Cap visible menu item text at 30 characters; if source content is longer, truncate or summarize it before rendering and open the full content in a dedicated window or detail surface.
- If a `MenuBarExtra` app should still behave like a regular Dock app with a visible main window/process, install an `NSApplicationDelegate` via `@NSApplicationDelegateAdaptor`, call `NSApp.setActivationPolicy(.regular)` during launch, and activate the app with `NSApp.activate(ignoringOtherApps: true)`. If the app is intentionally menu-bar-only, document that `.accessory` / no-Dock behavior is a deliberate product choice.
- Prefer system-adaptive colors, materials, and semantic foreground styles. Avoid fixed white/light backgrounds in scaffolding and examples unless the requested design explicitly calls for a custom non-adaptive theme.
- Do not paint `NavigationSplitView` sidebars or root window panes with opaque custom `Color(...)` or `Color(nsColor: .windowBackgroundColor)` fills by default. Prefer native macOS sidebar/window materials and system-provided backgrounds unless the user explicitly asks for a custom opaque surface. In sidebar-detail-inspector layouts, let the sidebar keep the standard source-list/material appearance and reserve custom backgrounds for detail or inspector content cards where needed.
- Use `@SceneStorage` for per-window ephemeral state and `@AppStorage` for durable user preferences.
- Keep selection state explicit and stable. macOS layouts often pivot around sidebar selection rather than push navigation.
- Prefer `NavigationSplitView` or a deliberate manual split layout over iOS-style stacked flows when the app benefits from always-visible structure.
- For `List(...).listStyle(.sidebar)` and `NavigationSplitView` sidebars, prefer flat native rows with standard system selection/highlight behavior. Keep rows visually lightweight and Mail-like: at most one leading icon, one strong title line, and one optional secondary detail line in `.secondary`. Avoid stacked metadata rows, repeated inline utility icons, or dense multi-column status text in the sidebar. Reserve card-style and metadata-heavy surfaces for detail or inspector panes unless the user explicitly asks for a highly custom sidebar treatment.
- Keep primary actions discoverable from both UI chrome and keyboard shortcuts when appropriate.
- Use SwiftUI-native scenes and views first. If you need low-level window, responder-chain, text system, or panel control, switch to `appkit-interop`.

## Recommended Sidebar Row Pattern

Prefer a native source-list row shape:

```swift
List(selection: $selection) {
  ForEach(items) { item in
    HStack(spacing: 10) {
      Image(systemName: item.systemImage)
        .foregroundStyle(.secondary)
        .frame(width: 16)

      VStack(alignment: .leading, spacing: 2) {
        Text(item.title)
          .lineLimit(1)

        if let detail = item.detail {
          Text(detail)
            .font(.caption)
            .foregroundStyle(.secondary)
            .lineLimit(1)
        }
      }
    }
    .tag(item.id)
  }
}
.listStyle(.sidebar)
```

This keeps selection, highlight, spacing, and scanability aligned with standard
macOS sidebars. Keep each row to one icon maximum and one or two text lines
maximum, with the second line reserved for a short detail label. Use richer card
treatments and denser metadata in the detail or inspector content, not in every
sidebar row.

## Recommended Split-View Background Pattern

Prefer letting the sidebar and split container use system backgrounds, while
applying custom surfaces only to detail cards or inspector sections:

```swift
NavigationSplitView {
  List(selection: $selection) {
    ForEach(items) { item in
      Label(item.title, systemImage: item.systemImage)
        .tag(item.id)
    }
  }
  .listStyle(.sidebar)
} detail: {
  ScrollView {
    VStack(alignment: .leading, spacing: 16) {
      DetailSummaryCard(item: selectedItem)
      DetailMetricsCard(item: selectedItem)
    }
    .padding()
  }
}
```

Avoid painting the sidebar and root split panes with opaque custom fills by
default:

```swift
NavigationSplitView {
  List(items) { item in
    SidebarCardRow(item: item)
  }
  .listStyle(.sidebar)
  .background(Color(nsColor: .windowBackgroundColor))
} detail: {
  DetailView(item: selectedItem)
    .background(Color(.white))
}
```

## State Ownership Summary

Use the narrowest state tool that matches the ownership model:

| Scenario | Preferred pattern |
| --- | --- |
| Local view or control state | `@State` |
| Child mutates parent-owned value state | `@Binding` |
| Root-owned reference model on macOS 14+ | `@State` with an `@Observable` type |
| Child reads or mutates an injected `@Observable` model | Pass it explicitly as a stored property |
| Window-scoped ephemeral selection or expansion state | `@SceneStorage` when practical, otherwise scene-owned `@State` |
| Shared user preference | `@AppStorage` |
| Shared app service or configuration | `@Environment(Type.self)` |
| Legacy reference model on older targets | `@StateObject` at the owner and `@ObservedObject` when injected |

Choose the ownership location first, then the wrapper. Do not turn simple desktop state into a view model by reflex.

## Cross-Cutting References

- `references/components-index.md`: entry point for scene and component guidance.
- `references/windowing.md`: choosing between `WindowGroup`, `Window`, `DocumentGroup`, and window-opening patterns.
- `references/settings.md`: dedicated settings scenes, `SettingsLink`, and preference layouts.
- `references/commands-menus.md`: command menus, keyboard shortcuts, focused values, and desktop action routing.
- `references/split-inspectors.md`: sidebars, split views, selection-driven layout, and inspectors.
- `references/menu-bar-extra.md`: menu bar extra structure and when it fits.

## Anti-Patterns

- One huge `ContentView` pretending the whole app is a single screen.
- Touch-first interaction models ported directly from iOS without desktop affordances.
- Hiding core actions behind gestures with no menu, toolbar, or keyboard path.
- Building a menu-bar-plus-window app around only a `Window(...)` scene and then expecting the main window to appear at launch. Use `WindowGroup(..., id:)` for the primary launch window and reserve `Window(...)` for auxiliary/on-demand windows.
- Rendering full unbounded document titles, prompts, or message text directly inside a menu bar extra. Menu item labels should stay at or below 30 characters, with longer content moved into a dedicated window or detail view.
- Treating settings as another navigation destination in the main content window.
- Hardcoding `.background(.white)`, `Color.white`, or a fixed light palette in a brand-new scaffold without an explicit design requirement.
- Wrapping each sidebar item in large rounded custom cards inside a `.sidebar` list, which fights native source-list density, alignment, and selection behavior unless the user explicitly asked for a bespoke visual sidebar.
- Building sidebar rows with multiple repeated icons, three or more text lines, or a dense strip of inline metadata counters/timestamps/models. Keep the sidebar row to one icon and one or two text lines, then move richer metadata into the detail pane.
- Painting `NavigationSplitView` sidebars or root window panes with opaque custom color fills by default, instead of letting the sidebar use native source-list/material appearance and reserving custom backgrounds for actual content cards.
- Using push navigation for layouts that want stable sidebar selection and detail panes.
- Reaching for AppKit before the SwiftUI scene and command APIs have been used properly.

## Workflow For A New macOS Scene Or View

1. Define the scene type and ownership model before writing child views.
2. Decide which actions live in content, toolbars, commands, inspectors, or settings.
3. Sketch the selection model and layout: sidebar-detail, editor-inspector, document window, or utility window.
4. Build with small, focused subviews and explicit inputs rather than giant computed fragments.
5. Add keyboard shortcuts and menu or toolbar exposure for actions that matter on desktop.
6. Validate the flow with a build and a quick usability pass: multiwindow assumptions, settings entry points, and selection stability.

## Component References

Use `references/components-index.md` as the entry point. Each component reference should include:
- intent and best-fit scenarios
- minimal usage pattern with desktop conventions
- pitfalls and discoverability notes
- when to fall back to `appkit-interop`
