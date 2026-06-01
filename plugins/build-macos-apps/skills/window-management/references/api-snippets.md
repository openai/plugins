# Window API Snippets

Use these examples after the window role and modifier choices are clear.

```swift
WindowGroup("Destination Video") {
  CatalogView()
    .toolbar(removing: .title)
    .toolbarBackgroundVisibility(.hidden, for: .windowToolbar)
}
```

```swift
Window("About", id: "about") {
  AboutView()
    .toolbar(removing: .title)
    .toolbarBackgroundVisibility(.hidden, for: .windowToolbar)
    .containerBackground(.thickMaterial, for: .window)
}
.windowMinimizeBehavior(.disabled)
.restorationBehavior(.disabled)
```

```swift
WindowGroup("Player", for: Video.self) { $video in
  PlayerView(video: video)
}
.defaultWindowPlacement { content, context in
  let idealSize = content.sizeThatFits(.unspecified)
  let displayBounds = context.defaultDisplay.visibleRect
  let fittedSize = clampToDisplay(idealSize, displayBounds: displayBounds)
  return WindowPlacement(size: fittedSize)
}
.windowIdealPlacement { content, context in
  let idealSize = content.sizeThatFits(.unspecified)
  let displayBounds = context.defaultDisplay.visibleRect
  let zoomedSize = zoomToFit(idealSize, displayBounds: displayBounds)
  let position = centeredPosition(for: zoomedSize, in: displayBounds)
  return WindowPlacement(position, size: zoomedSize)
}
```

```swift
PlayerView(video: video)
  .overlay(alignment: .top) {
    Color.clear
      .frame(height: 48)
      .contentShape(Rectangle())
      .gesture(WindowDragGesture())
      .allowsWindowActivationEvents(true)
  }
```

```swift
Window("Welcome", id: "welcome") {
  WelcomeView()
}
.windowStyle(.plain)
.defaultLaunchBehavior(.presented)
```
