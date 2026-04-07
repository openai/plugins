# Split Views and Inspectors

## Intent

Use this when the app benefits from a stable sidebar-detail layout, optional supplementary content, or an inspector panel.

## Core patterns

- Prefer explicit selection state over push-only navigation.
- Start with `NavigationSplitView` when the layout matches the system mental model.
- Use a manual split only when you need unusual sizing or an always-visible custom column.
- Use `inspector(isPresented:)` for lightweight detail controls that complement the main content.

## Example: sidebar + detail

```swift
struct LibraryRootView: View {
  @State private var selection: Item.ID?
  @State private var showInspector = false

  var body: some View {
    NavigationSplitView {
      SidebarList(selection: $selection)
    } detail: {
      DetailView(selection: selection)
        .inspector(isPresented: $showInspector) {
          InspectorView(selection: selection)
        }
    }
  }
}
```

## Pitfalls

- Avoid swapping the whole root layout with top-level conditionals when selection changes.
- Avoid hiding too much detail behind modal sheets when an inspector or secondary column would fit better.
- If the layout requires AppKit split view delegation or advanced window coordination, use `appkit-interop`.
