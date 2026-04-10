# Drag, Drop, and Pasteboard

## Intent

Use this when desktop drag/drop or pasteboard behavior exceeds what plain SwiftUI modifiers cover comfortably.

## Good fits

- File URL dragging
- Pasteboard interoperability with other macOS apps
- Rich drag previews or AppKit-specific drop validation
- Legacy AppKit views with custom drag types

## Core patterns

- Start with SwiftUI drag/drop APIs when they already cover the use case.
- Drop to AppKit when you need `NSPasteboard`, custom pasteboard types, or older AppKit delegate flows.
- Keep data conversion at the boundary instead of leaking AppKit types through the whole feature.

## Pitfalls

- Do not move your whole list or canvas into AppKit just for one drop target.
- Keep file and pasteboard types explicit and validated.
