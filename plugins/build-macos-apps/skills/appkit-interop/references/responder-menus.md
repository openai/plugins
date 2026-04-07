# Responder Chain and Menus

## Intent

Use this when command handling depends on the active window, first responder, or AppKit menu validation.

## Core patterns

- Start with SwiftUI `commands`, `FocusedValue`, and focused scene state.
- Use AppKit responder-chain hooks only when command routing or validation truly depends on the underlying responder system.
- Keep menu enablement rules close to the state they depend on.

## Good fits for AppKit

- Validating whether a menu item should be enabled
- Routing actions through the current first responder
- Integrating with existing AppKit document or text behaviors

## Pitfalls

- Do not recreate AppKit-style global command handling when SwiftUI focused values would work.
- Avoid scattering command logic between SwiftUI closures and AppKit selectors without a clear boundary.
