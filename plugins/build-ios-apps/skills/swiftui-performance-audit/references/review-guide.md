# SwiftUI performance review guide

Use this as the deep reference when auditing SwiftUI code. If the target repo already has a local SwiftUI performance guide, read that first and treat it as authoritative; use this document to fill gaps, not to override local conventions.

## Mental model

SwiftUI performance is mostly about three things:

- **Identity**: how SwiftUI recognizes the same logical view across updates.
- **Lifetime**: where state storage lives for that identity.
- **Dependencies**: which values a view reads while evaluating `body`.

Prefer designs that preserve stable identity, keep dependency surfaces narrow, and make every code path reachable from `body` cheap and side-effect free.

## State and Observation

Prefer Observation for new feature code when the deployment target allows it.

- Use `@Observable` models for feature state.
- Own them with `@State` in the root view, pass them explicitly to children, and use `@Bindable` only where bindings are required.
- Prefer `@Environment(Type.self)` or explicit parameters over broad `@EnvironmentObject` usage.
- Split "god" observables when different parts of the screen read unrelated fields.
- Mark mutable non-render bookkeeping such as caches, task handles, cancellables, services, and lazy dependencies with `@ObservationIgnored` when they should not participate in invalidation.
- Do not mark immutable `let` dependencies with `@ObservationIgnored`; they are already outside mutable observed state.

Observation is read-tracked. The important design move is not merely "use `@Observable`", but "make each leaf read only what it truly needs." If every row reads the same broad collection or root model, each row can depend on that whole value even when it only needs one derived fact.

## Structural identity

### Avoid `AnyView` in hot paths

Flag `AnyView` in lists, large `ForEach` content, dynamic rows, and frequently updating surfaces. Prefer:

- `@ViewBuilder` functions returning `some View`
- enums plus `switch`
- concrete wrapper views with stable structure

Use `AnyView` only for narrow boundaries where the type erasure is the point.

### Prefer value changes over tree swaps

When state only changes style or behavior, keep one view type and vary values:

```swift
Text(title)
  .fontWeight(isHighlighted ? .bold : .regular)
  .opacity(isDisabled ? 0.4 : 1)
```

Avoid helper modifiers such as `.if`, `.when`, or `.apply(if:)` when they branch between structurally different trees for a styling-only change. Those helpers still lower into `_ConditionalContent`, which can reset state, break animations, and increase work in repeated rows.

Structural branches are fine when the UI truly changes shape, such as loading, loaded, and error states. If state must survive the swap, lift it above the branch.

### Keep one root view per `ForEach` element

For large collections, each element should yield a constant number of root views.

- Prefer filtering before `ForEach` over returning "sometimes nothing".
- Avoid returning a variable number of sibling roots per element.
- If a condition must stay inside the row, wrap it in one stable container.

### Treat `.id(...)` as a sharp tool

Changing `.id(...)` resets state and prevents diffing across the old and new identity.

- Flag `.id(UUID())` and other force-refresh patterns.
- Use explicit identity only when it encodes real stable data or drives a deliberate scroll/animation behavior.

### Prefer native controls plus styles

When a wrapper exists only to style `Button`, `Toggle`, `Label`, or another native control, prefer a `ButtonStyle`, `ToggleStyle`, or related style protocol. Wrapper views are still appropriate when they encode domain semantics, combine multiple controls, or add real behavior.

## Cheap view evaluation

Treat all code reachable from `body` as hot-path code:

- `body`
- computed properties used by `body`
- helper methods called by `body`
- alternate "measured body" implementations

View bodies run on the main thread, and synchronous work reached from `body` has to complete before SwiftUI can finish the update for the next frame.

Flag:

- sorting or filtering large collections during render
- formatter allocation
- parsing, image processing, JSON work, or synchronous I/O
- heavyweight layout calculations
- long-running work in initializers, `onAppear`, or `onChange`

Prefer:

- model-layer precomputation
- derived state updated from meaningful input changes
- cached helpers and formatter reuse
- background preprocessing before render

`@State` is not a generic cache. Use it only when the derived value belongs to the view lifecycle and has a clear update contract.

- Define which input changes refresh the state.
- Prefer model or store precomputation when the value is not view-owned.
- Prefer memoized helpers or background preprocessing when the work is expensive but not stateful UI.

## Lists and large collections

- Prefer `List` for table-like content with system affordances.
- Prefer `ScrollView` plus lazy containers for custom layouts when list affordances are not needed.
- Avoid nested scroll containers such as `ScrollView { List { ... } }`.
- Use stable domain IDs rather than indices, mutable values, or per-render UUIDs.
- Be cautious with `ForEach(0..<count)` when the range is dynamic or rows carry state.
- Avoid `ForEach(items.indices, id: \.self)` when insertions, removals, or reordering can happen.

## Dependencies and layout readers

### Slim down fat parents

Flag views that hold many unrelated `@State` values or read a large observable just to pass fragments downward. Move state closer to the leaf, split models, and pass specific values or bindings.

### Narrow geometry scope

Treat these APIs as hot spots when they feed state or sit above large subtrees: `GeometryReader`, `ScrollViewReader`, `PreferenceKey`, `anchorPreference`, `overlayPreferenceValue`, and `onPreferenceChange`.

- Keep them around only the subtree that needs geometry.
- Move unrelated stateful descendants outside the reader subtree.
- Keep preference payloads small, stable, and tied to the coordinate space where they will be consumed.
- Avoid geometry-driven state loops unless the geometry materially changes the UI.
- Compare or threshold measured values before writing state so tiny layout changes do not create a measure-update-layout cycle.

### Avoid high-volume environment writes

Rapidly writing scroll offsets, geometry, timers, or large arrays into the environment wakes every environment-reading view. Prefer putting a stable observable reference in the environment and mutating fields on that object so only the views that read the changing field update.

Even when SwiftUI decides a dependent view's `body` does not need to run, there is still cost in checking that dependency after the environment value changes.

When reacting to high-frequency signals, prefer thresholds, debouncing, or model-layer coalescing over responding to every tick.

## `ForEach` and state behavior

`@State` is keyed by identity. If row identity shifts, row state can appear to jump or reset.

- Stable IDs matter most when rows own state.
- Keep row-scoped state on a stable row root when child content appears and disappears conditionally.
- In lazy containers, put row-lifetime `@State` on the stable root view returned from `ForEach`. Nested child state can be recreated after offscreen content is rebuilt; lift it to the row root, pass a binding, or move it into a model when it must survive scrolling.
- Treat dynamic index IDs as suspicious whenever the collection mutates.

## Concurrency and lifecycle modifiers

SwiftUI runs on the main actor. Keep synchronous work off the main thread and out of frequent lifecycle hooks.

- Prefer `.task { ... }` for view-scoped async work because SwiftUI cancels it with the view lifecycle.
- Avoid `Task.detached` for view-initiated work unless the lifetime and cancellation story are explicit.
- Do not assume `.task` or `async` makes CPU-heavy synchronous work leave the main actor. Move expensive parsing, image decoding, formatting, or database work into a non-main-actor helper or service; in Swift 6.2+ use `@concurrent` when an async helper must explicitly hop off the caller's actor.
- Flag heavy `.onAppear` and `.onChange` handlers, especially for text input, geometry, timers, and scrolling.
- Avoid per-row network `.task` work in large lists unless it is cached, bounded, or intentionally coordinated.

## Composition before `equatable()`

Use this order:

1. Improve composition and state placement.
2. Narrow Observation dependencies.
3. Reach for `.equatable()` only after measurement shows it is warranted.

Require measured justification for `.equatable()` in non-obvious cases, and verify that the view semantics truly depend only on the Equatable input. Otherwise stale UI is the bill that comes due later.

## Closures in views

### Builder closures

Do not store builder closures on views when you can evaluate them in `init` and store the resulting child view instead:

```swift
struct Container<Content: View>: View {
  private let content: Content

  init(@ViewBuilder content: () -> Content) {
    self.content = content()
  }

  var body: some View {
    content
  }
}
```

Stored escaping builder closures make diffing harder and can drag parent dependencies into children.

### Action closures

Action closures are fine, but captures still matter.

- Prefer method references when they reduce the capture set.
- Use capture lists when only a small subset is needed.
- In hot paths, flag actions that capture a large view model or broad state unnecessarily.

### Manual bindings

Prefer key-path bindings such as `$state` and `$model.property` over `Binding(get:set:)` where possible.

Manual bindings store closures and are harder for SwiftUI to compare across updates. Strongly question them in list rows, text input, and other frequently updating controls. If one is necessary, isolate it in a small subview and document why a key-path binding was insufficient.

## Images and animations

- Decode and downsample large images before rendering.
- Avoid broad animation modifiers that cause a large subtree to animate for tiny state changes.
- Flag `.animation(..., value:)` or `withAnimation` usage that wraps a large container when only a small control, row, or transition should animate. Prefer SwiftUI's scoped `.animation(...) { content in ... }` modifier when the deployment target supports it; otherwise move the animation modifier to the smallest affected view.
- Prefer focused transitions over animating entire container hierarchies.

## Profiling

Use Instruments' SwiftUI template to inspect:

- Update Groups
- Long View Body Updates
- Other Long Updates
- cause-and-effect graphs

Use Update Groups to find when SwiftUI is doing work, Long View Body Updates to find slow `body` evaluation, and the cause-and-effect graph to compare the interaction's expected update fan-out with the actual views that were invalidated. If a tap should update two rows but the graph shows the whole list, narrow the dependencies before reaching for `.equatable()` or other local triage.

When a PR materially changes a large scrolling surface, frequently updated screen, or complex animated area, add a `// PERF:` note when useful so future maintainers know how to reproduce and measure the sensitive path.

## Review checklist

Always ask:

1. Is there `AnyView` in a hot path?
2. Is any code reachable from `body` doing heavy work?
3. Is `@State` being used as an ad hoc cache without a clear input-change contract?
4. Are list identities stable and unique?
5. Does each `ForEach` element produce one stable root?
6. Are parent views, geometry readers, preference chains, or environment writes causing broad invalidation?
7. Is Observation being used with narrow reads and correct ignored state?
8. Is heavy work tied to lifecycle modifiers or the main actor?
9. Are stored builder closures or broad action captures causing avoidable churn?
10. Are manual bindings used where key-path bindings would work?
11. Could similar branches be value-based modifiers instead of tree swaps?
12. Is `.equatable()` backed by real evidence rather than hope?
13. Is animation scoped to the smallest view that owns the visual change?
