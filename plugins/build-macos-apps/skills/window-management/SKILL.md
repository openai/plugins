---
name: window-management
description: Customize macOS 15+ SwiftUI windows and scene behavior using Window, WindowGroup, and macOS window modifiers. Use when styling or hiding window toolbars and titles, extending drag regions with WindowDragGesture, replacing window backgrounds with materials, disabling minimize or restoration for utility windows, setting default or ideal window placement from content/display size, creating borderless windows, or tuning default launch behavior.
---

# Window Management

## Overview

Use this skill to tailor each SwiftUI window to its job. Start by identifying
which scene owns the window (`Window`, `WindowGroup`, or a dedicated utility
scene), then customize the toolbar/title area, background material, resize and
restoration behavior, and initial or zoomed placement.

Prefer scene and window modifiers over ad hoc AppKit bridges when SwiftUI offers
the behavior directly. Keep each window purpose-built: a main browser window, an
About window, and a media player window usually want different chrome,
resizability, restoration, and placement rules.

These APIs are macOS 15+ SwiftUI window/scene customizations. For older
deployment targets, expect to use more AppKit bridging or availability guards.

## Workflow

1. Inspect the relevant scene declaration and classify the window role:
   main app navigation, inspector/detail utility, About/support window, media
   playback window, welcome window, or a borderless custom surface.
2. Adjust toolbar and title presentation to match the content.
3. If the toolbar background or entire toolbar is hidden, make sure the window
   still has a usable drag region.
4. Refine window behavior for that role: minimize availability, restoration,
   resize expectations, and whether the window should appear at launch.
5. Set default placement for newly opened windows and ideal placement for zoom
   behavior when content and display size matter.
6. Build and launch the app with `build-run-debug` to verify the result in
   a real foreground `.app` bundle.
7. If SwiftUI scene/window modifiers are not enough, switch to `appkit-interop`
   for a narrow `NSWindow` bridge rather than spreading AppKit through the view
   tree.

## Toolbar And Title

- Use `.toolbar(removing: .title)` when the window title should stay associated
  with the window for accessibility and menus, but not be visibly drawn in the
  title bar.
- Use `.toolbarBackgroundVisibility(.hidden, for: .windowToolbar)` when large
  media or hero content should visually extend to the top edge of the window.
- If the window still needs close/minimize/full-screen controls, remove only the
  title and toolbar background. If the toolbar should disappear entirely, use
  `.toolbarVisibility(.hidden, for: .windowToolbar)` instead.
- Remove custom toolbar backgrounds and manually painted titlebar fills before
  layering new SwiftUI toolbar APIs on top.
- Keep the window's logical title meaningful even if hidden; the system can
  still use it for accessibility and menu items. These are visual changes only.

## Drag Regions

- If a toolbar background is hidden or the toolbar is removed entirely, use
  `WindowDragGesture()` to extend the draggable area into your content.
- Attach the gesture to a transparent overlay or non-interactive header region
  that does not steal gestures from real controls.
- For a media player with custom playback controls, insert the drag overlay
  between the video content and the controls so AVKit or transport controls keep
  receiving input.
- Pair the drag gesture with `.allowsWindowActivationEvents(true)` so clicking
  and immediately dragging a background window still activates and moves it.

## Background And Materials

- Use `.containerBackground(.thickMaterial, for: .window)` when a utility window
  or About window should replace the default window background with a subtle
  frosted material.
- Prefer system materials for stylized windows instead of hardcoded translucent
  colors.
- Use this especially for fixed-content utility windows where a softer backdrop
  is part of the design.

## Window Behavior

- Use `.windowMinimizeBehavior(.disabled)` for always-reachable utility windows
  such as a custom About window where minimizing adds little value.
- Disable the green zoom control through fixed sizing or window constraints when
  the window's content has one intended size.
- Use `.restorationBehavior(.disabled)` for windows that should not reopen on
  next launch, such as About panels, transient support/info windows, or
  first-run welcome surfaces.
- Keep state restoration enabled for primary document or navigation windows when
  reopening prior size and position is desirable.
- By default, SwiftUI respects the user's system-wide macOS state restoration
  setting. Use `restorationBehavior(...)` only when a specific window should
  intentionally opt into or out of that system behavior.
- Use `.defaultLaunchBehavior(.presented)` for windows that should appear first
  on launch, such as a welcome window, and choose that behavior intentionally
  rather than relying on side effects from scene creation order.

## Window Placement

- Use `.defaultWindowPlacement { content, context in ... }` to control the
  initial size and optional position of newly opened windows.
- Inside the placement closure, call `content.sizeThatFits(.unspecified)` to get
  the content's ideal size.
- Read `context.defaultDisplay.visibleRect` to get the display's usable region
  after accounting for the menu bar and Dock.
- Return `WindowPlacement(size: size)` with a size clamped to the visible rect
  when media or document content may be larger than the display. If no position
  is provided, the window is centered by default.
- Use `.windowIdealPlacement { content, context in ... }` to control what
  happens when the user chooses Zoom from the Window menu or Option-clicks the
  green toolbar button. For media windows, preserve aspect ratio and grow to the
  largest size that fits the display.
- Treat default placement and ideal placement as separate policies:
  - default placement controls where a new window first appears,
  - ideal placement controls how large a zoomed window should become.
- Always consider external displays and rotated/narrow screens when sizing
  player windows or document windows from content dimensions.

## Borderless And Specialized Windows

- Use `.windowStyle(.plain)` for borderless or highly custom chrome windows, but
  make sure the content still provides a clear drag/move affordance and visible
  context.
- For a borderless player, HUD, or welcome window, decide upfront whether losing
  standard titlebar affordances is worth the custom presentation.
- Keep one clear path back to regular window management if the plain style makes
  the window feel invisible or hard to move.

## API Snippets

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

## Review Checklist

- The scene type matches the window's role and lifecycle.
- Hidden titles still leave a meaningful logical title for accessibility and
  menus.
- Toolbar background removal is intentional and does not hurt titlebar legibility
  or window control placement.
- Windows with hidden or removed toolbars still have a reliable drag region and
  support click-then-drag activation from the background.
- Utility windows have restoration/minimize behavior that matches their purpose.
- Restoration overrides are used only when a scene should intentionally differ
  from the user's system-wide setting.
- Default and ideal placement use `content.sizeThatFits(.unspecified)` and
  `context.defaultDisplay.visibleRect` when content/display size matters.
- Media windows preserve aspect ratio and fit on small or rotated displays.
- Borderless windows still have a usable move/drag affordance.

## Guardrails

- Do not use `.toolbar(removing: .title)` just to hide a title you forgot to set.
  Keep the underlying window title meaningful.
- Do not hide the toolbar background or the whole toolbar without replacing the
  lost drag affordance.
- Do not disable restoration on the main document/navigation window unless the
  user explicitly wants a fresh-start app every launch.
- Do not hardcode one monitor size or assume a single-display setup when sizing
  player windows.
- Do not reach for `NSWindow` mutation before checking whether
  `.windowMinimizeBehavior`, `.restorationBehavior`, `.defaultWindowPlacement`,
  `.windowIdealPlacement`, `.windowStyle`, or `.defaultLaunchBehavior` already
  solve the problem.
- Do not leave a plain borderless window without any obvious drag or close path.

## When To Use Other Skills

- Use `swiftui-patterns` for broader scene, commands, settings, sidebar,
  and inspector architecture.
- Use `liquid-glass` when the main question is modern macOS visual treatment,
  Liquid Glass, or system material adoption.
- Use `appkit-interop` if a custom window behavior truly requires `NSWindow`,
  `NSPanel`, or responder-chain control.
- Use `build-run-debug` to launch and verify the resulting windows.
