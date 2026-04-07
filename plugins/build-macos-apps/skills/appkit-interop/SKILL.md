---
name: appkit-interop
description: Decide when and how to bridge a macOS app from SwiftUI into AppKit. Use when implementing NSViewRepresentable or NSViewControllerRepresentable, accessing NSWindow or the responder chain, presenting panels, customizing menus, or handling desktop behaviors that SwiftUI does not model cleanly.
---

# AppKit Interop

## Quick Start

Use this skill when SwiftUI is close but not quite enough for native macOS behavior.
Keep the bridge as small and explicit as possible. SwiftUI should usually remain
the source of truth, while AppKit handles the imperative edge.

## Choose The Smallest Bridge

- Use pure SwiftUI when the required behavior already exists in scenes, toolbars, commands, inspectors, or standard controls.
- Use `NSViewRepresentable` when you need a specific AppKit view with lightweight lifecycle needs.
- Use `NSViewControllerRepresentable` when you need controller lifecycle, delegation, or presentation coordination.
- Use direct AppKit window or app hooks when you need `NSWindow`, responder-chain, menu validation, panels, or app-level behavior.

## Workflow

1. Name the capability gap precisely.
   - Window behavior
   - Text system behavior
   - Menu validation
   - Drag and drop
   - File open/save panels
   - First responder control

2. Pick the smallest boundary that solves it.
   - Avoid porting a whole screen to AppKit when one wrapped control or coordinator would do.

3. Keep ownership explicit.
   - SwiftUI owns value state, selection, and observable models.
   - AppKit objects stay inside the representable, coordinator, or bridge object.

4. Expose a narrow interface back to SwiftUI.
   - Bindings for editable state
   - Small callbacks for events
   - Focused bridge services only when necessary

5. Validate lifecycle assumptions.
   - SwiftUI may recreate representables.
   - Coordinators exist to hold delegate and target-action glue, not as a second app architecture.

## References

- `references/representables.md`: choosing between view and view-controller wrappers, plus coordinator patterns.
- `references/window-panels.md`: window access, utility windows, and open/save panels.
- `references/responder-menus.md`: first responder, command routing, and menu validation.
- `references/drag-drop-pasteboard.md`: pasteboard, file URLs, and desktop drag/drop edges.

## Guardrails

- Do not duplicate the source of truth between SwiftUI and AppKit.
- Do not let `Coordinator` become an unstructured dumping ground.
- Do not store long-lived `NSView` or `NSWindow` instances globally without a strong ownership reason.
- Prefer a tiny tested bridge over rewriting the feature in raw AppKit.
- If a pattern can remain entirely in `swiftui-patterns`, keep it there.

## Output Expectations

Provide:
- the exact SwiftUI limitation being crossed
- the smallest recommended bridge type
- the data-flow boundary between SwiftUI and AppKit
- the lifecycle or validation risks to watch
