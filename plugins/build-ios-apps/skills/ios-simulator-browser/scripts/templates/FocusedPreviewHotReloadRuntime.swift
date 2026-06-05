import Darwin
import Foundation
import SwiftUI

// This file is compiled into the reload dylib; the running host resolves these exports with dlsym.
@MainActor private let cachedHotReloadPreviewVariants = previewBrowserPreviewVariants()

private func hotReloadPreviewCString(_ value: String) -> UnsafeMutablePointer<CChar>? {
  strdup(value)
}

@_cdecl("focused_preview_hot_reload_preview_count")
public func focusedPreviewHotReloadPreviewCount() -> Int {
  MainActor.assumeIsolated {
    cachedHotReloadPreviewVariants.count
  }
}

@_cdecl("focused_preview_hot_reload_preview_id")
@MainActor
public func focusedPreviewHotReloadPreviewID(_ previewIndex: Int) -> UnsafeMutablePointer<CChar>? {
  hotReloadPreviewCString(cachedHotReloadPreviewVariants[previewIndex].id)
}

@_cdecl("focused_preview_hot_reload_group_display_name")
@MainActor
public func focusedPreviewHotReloadGroupDisplayName(
  _ previewIndex: Int
) -> UnsafeMutablePointer<CChar>? {
  hotReloadPreviewCString(cachedHotReloadPreviewVariants[previewIndex].groupDisplayName)
}

@_cdecl("focused_preview_hot_reload_preview_display_name")
@MainActor
public func focusedPreviewHotReloadPreviewDisplayName(
  _ previewIndex: Int
) -> UnsafeMutablePointer<CChar>? {
  hotReloadPreviewCString(cachedHotReloadPreviewVariants[previewIndex].displayName)
}

@_cdecl("focused_preview_hot_reload_free_string")
public func focusedPreviewHotReloadFreeString(_ pointer: UnsafeMutablePointer<CChar>?) {
  free(pointer)
}

@MainActor
@_cdecl("focused_preview_hot_reload_make_view")
public func focusedPreviewHotReloadMakeView(
  _ previewIndex: Int
) -> UnsafeMutableRawPointer? {
  let previewVariant = cachedHotReloadPreviewVariants[previewIndex]
  // The host moves the AnyView out of this box and deallocates the storage.
  let view = UnsafeMutablePointer<AnyView>.allocate(capacity: 1)
  view.initialize(to: previewVariant.makeView())
  return UnsafeMutableRawPointer(view)
}
