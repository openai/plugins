import Foundation
import SnapshotPreviewsCore
import SwiftUI

// MARK: - PreviewVariant

struct PreviewVariant: Identifiable {
  let id: String
  let groupDisplayName: String
  let displayName: String
  let makeView: @MainActor () -> AnyView
}

@MainActor
func previewBrowserPreviewVariants() -> [PreviewVariant] {
  previewBrowserPreviewTypes().flatMap { previewType in
    previewType.previews.enumerated().map { index, preview in
      PreviewVariant(
        id: "\(previewType.typeName):\(index)",
        groupDisplayName: previewType.displayName,
        displayName: preview.displayName ?? "Preview",
        makeView: { AnyView(preview.view()) }
      )
    }
  }
}

@MainActor
private func previewBrowserPreviewTypes() -> [PreviewType] {
  let previewTypes = FindPreviews.findPreviews(
    included: nil,
    excluded: nil,
    includedModules: previewBrowserIncludedModules,
    excludedModules: nil
  )

  // Keep the updated registrations added by a newly loaded package dylib.
  var retainedTypeNames = Set<String>()
  let newestPreviewTypes = previewTypes.reversed().filter { previewType in
    retainedTypeNames.insert(previewType.typeName).inserted
  }.reversed()

  guard let filters = previewBrowserFilters else {
    return Array(newestPreviewTypes)
  }

  return newestPreviewTypes.compactMap { previewType in
    var filteredType = previewType
    filteredType.previews = previewType.previews.filter { preview in
      matchesFilter(
        typeName: previewType.typeName,
        groupDisplayName: previewType.displayName,
        displayName: preview.displayName ?? "Preview",
        filters: filters
      )
    }
    return filteredType.previews.isEmpty ? nil : filteredType
  }
}

private func matchesFilter(
  typeName: String,
  groupDisplayName: String,
  displayName: String,
  filters: [String]
) -> Bool {
  let candidates = [typeName, groupDisplayName, displayName]
  return filters.contains { filter in
    candidates.contains {
      $0.range(of: filter, options: [.regularExpression, .caseInsensitive]) != nil
    }
  }
}
