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

## Example: native sidebar row

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

Keep each row to one icon and one or two text lines. Put richer metadata in the
detail or inspector content instead of every sidebar row.

## Example: split-view backgrounds

Let the sidebar and split container keep system backgrounds while detail content
owns custom surfaces:

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

Avoid opaque sidebar and root split-pane fills by default:

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

## Pitfalls

- Avoid swapping the whole root layout with top-level conditionals when selection changes.
- Avoid hiding too much detail behind modal sheets when an inspector or secondary column would fit better.
- If the layout requires AppKit split view delegation or advanced window coordination, use `appkit-interop`.
