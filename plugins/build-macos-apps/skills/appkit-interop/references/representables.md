# Representables

## Intent

Use this when wrapping an AppKit control or controller for a SwiftUI macOS app.

## Choose the wrapper type

- Use `NSViewRepresentable` for a view-level bridge such as `NSTextView`, `NSScrollView`, or a custom AppKit control.
- Use `NSViewControllerRepresentable` when you need controller lifecycle, delegate coordination, or AppKit presentation logic.

## Skeleton

```swift
struct LegacyTextView: NSViewRepresentable {
  @Binding var text: String

  func makeCoordinator() -> Coordinator {
    Coordinator(text: $text)
  }

  func makeNSView(context: Context) -> NSScrollView {
    let scrollView = NSScrollView()
    let textView = NSTextView()
    textView.delegate = context.coordinator
    scrollView.documentView = textView
    return scrollView
  }

  func updateNSView(_ nsView: NSScrollView, context: Context) {
    guard let textView = nsView.documentView as? NSTextView else { return }
    if textView.string != text {
      textView.string = text
    }
  }

  final class Coordinator: NSObject, NSTextViewDelegate {
    @Binding var text: String

    init(text: Binding<String>) {
      _text = text
    }

    func textDidChange(_ notification: Notification) {
      guard let textView = notification.object as? NSTextView else { return }
      text = textView.string
    }
  }
}
```

## Pitfalls

- Avoid infinite update loops by only pushing state into AppKit when values actually changed.
- Keep delegates and target-action wiring in the coordinator.
- If the wrapper grows into a full screen, re-evaluate the boundary.
