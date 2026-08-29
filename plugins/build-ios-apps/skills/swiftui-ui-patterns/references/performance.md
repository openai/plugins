# Performance guardrails

## Intent

Use these rules when a SwiftUI screen is large, scroll-heavy, frequently updated, or at risk of unnecessary recomputation. This page is a build-time guardrail, not a substitute for a full audit; when the task is specifically about performance, use the `swiftui-performance-audit` skill and its deeper review guide.

## Core rules

- Give `ForEach` and list content stable identity. Do not use unstable indices as identity when the collection can reorder or mutate.
- Keep one stable root view per `ForEach` element; filter before iterating instead of making rows appear and disappear at the root.
- In lazy containers, keep row-lifetime `@State` on the stable root view returned from `ForEach`; nested child state can be recreated when offscreen content is rebuilt.
- Keep expensive filtering, sorting, and formatting out of `body`; precompute or move it into a model/helper when it is not trivial.
- Narrow observation scope so only the views that read changing state need to update.
- Use lazy containers for large repeated content when standard stacks load too many children; prefer standard stacks for small content or when profiling does not show a lazy benefit.
- Avoid swapping entire top-level view trees for small state changes; keep a stable root view and vary localized sections or modifiers.
- Prefer value-based modifiers over `.if`-style helpers when a condition changes only styling or behavior.
- Avoid `AnyView`, stored builder closures, and manual `Binding(get:set:)` in hot paths when concrete views, stored child views, or key-path bindings would do.
- Keep `GeometryReader`, preference chains, and high-volume environment writes tightly scoped so one hot signal does not wake an unrelated subtree.
- Use `@State` only for view-owned state, not as an ad hoc cache for arbitrary expensive computation.
- Scope animation to the smallest view that owns the visual change; prefer scoped `.animation(...) { content in ... }` modifiers when available over broad animation modifiers on large containers.

## Example: stable identity

```swift
ForEach(items) { item in
  Row(item: item)
}
```

Prefer that over index-based identity when the collection can change order:

```swift
ForEach(Array(items.enumerated()), id: \.offset) { _, item in
  Row(item: item)
}
```

## Example: move expensive work out of body

```swift
struct FeedView: View {
  let items: [FeedItem]

  private var sortedItems: [FeedItem] {
    items.sorted(using: KeyPathComparator(\.createdAt, order: .reverse))
  }

  var body: some View {
    List(sortedItems) { item in
      FeedRow(item: item)
    }
  }
}
```

If the work is more expensive than a small derived property, move it into a model, store, or helper that updates less often.

## When to investigate further

- Janky scrolling in long feeds or grids
- Typing lag from search or form validation
- Overly broad view updates when one small piece of state changes
- Large screens with many conditionals or repeated formatting work

## Pitfalls

- Recomputing heavy transforms every render
- Observing a large object from many descendants when only one field matters
- Building custom scroll containers when `List`, `LazyVStack`, or `LazyHGrid` would already solve the problem
- Using `.id(...)` as a force-refresh mechanism instead of a real identity boundary
- Reaching for `.equatable()` before composition and dependency scope have been fixed
- Publishing broad preference payloads or geometry changes on every tiny layout update
- Animating an entire container when only a small row, control, or transition changes
