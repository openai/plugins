import Darwin
import Foundation
import Observation
import SwiftUI

// MARK: - FocusedPreviewApp

@main
@MainActor
struct FocusedPreviewApp: App {
  var body: some Scene {
    WindowGroup {
      FocusedPreviewRootView()
    }
  }
}

// MARK: - FocusedPreviewStore

@MainActor
@Observable
private final class FocusedPreviewStore {
  nonisolated private static let hotReloadRequestedNotificationName = "dev.swiftui-preview-browser.reload"

  // MARK: Lifecycle

  init() {
    previewVariants = previewBrowserPreviewVariants()
    observeReloadRequests()
  }

  deinit {
    CFNotificationCenterRemoveObserver(
      CFNotificationCenterGetDarwinNotifyCenter(),
      UnsafeRawPointer(Unmanaged.passUnretained(self).toOpaque()),
      CFNotificationName(Self.hotReloadRequestedNotificationName as CFString),
      nil
    )
  }

  // MARK: Internal

  private(set) var previewVariants: [PreviewVariant]
  var selectedPageIndex = 0 {
    didSet {
      let clampedPageIndex = Self.clampedPageIndex(selectedPageIndex, for: previewVariants)
      guard selectedPageIndex != clampedPageIndex else { return }
      selectedPageIndex = clampedPageIndex
    }
  }

  func loadHotReloadIfNeeded() {
    guard
      let manifest = HotReloadManifest(url: PreviewBrowserFiles.manifestURL),
      manifest.token != lastHotReloadToken
    else {
      return
    }

    lastHotReloadToken = manifest.token
    let handle = dlopen(manifest.dylibPath, RTLD_NOW | RTLD_LOCAL)
    guard let handle else {
      let error =
        if let errorPointer = dlerror() {
          String(cString: errorPointer)
        } else {
          "unknown dlopen error"
        }
      writeStatus(phase: "error", error: error)
      return
    }

    hotReloadHandlesToKeepAlive.append(handle)
    let hotReloadPreviewVariants = Self.hotReloadPreviewVariants(
      handle: handle,
      generation: manifest.token
    )
    guard !hotReloadPreviewVariants.isEmpty else {
      writeStatus(phase: "error", error: "No previews found in generation \(manifest.token)")
      return
    }

    replacePreviewVariants(with: hotReloadPreviewVariants)
    writeStatus(phase: "reloaded", error: nil)
  }

  // MARK: Private

  @ObservationIgnored private var hotReloadHandlesToKeepAlive = [UnsafeMutableRawPointer]()
  @ObservationIgnored private var lastHotReloadToken: String?
  @ObservationIgnored private let statusWriter = HostStatusWriter()
  @ObservationIgnored private var pendingStatusWrite: Task<Void, Never>?

  private static func hotReloadPreviewVariants(
    handle: UnsafeMutableRawPointer,
    generation: String
  ) -> [PreviewVariant] {
    guard
      let previewCountSymbol = dlsym(handle, "focused_preview_hot_reload_preview_count"),
      let idSymbol = dlsym(handle, "focused_preview_hot_reload_preview_id"),
      let groupDisplayNameSymbol = dlsym(handle, "focused_preview_hot_reload_group_display_name"),
      let displayNameSymbol = dlsym(handle, "focused_preview_hot_reload_preview_display_name"),
      let freeStringSymbol = dlsym(handle, "focused_preview_hot_reload_free_string"),
      let makeViewSymbol = dlsym(handle, "focused_preview_hot_reload_make_view")
    else {
      return []
    }

    let previewCount = unsafeBitCast(
      previewCountSymbol,
      to: HotReloadPreviewCountFunction.self
    )
    let id = unsafeBitCast(
      idSymbol,
      to: HotReloadPreviewStringFunction.self
    )
    let groupDisplayName = unsafeBitCast(
      groupDisplayNameSymbol,
      to: HotReloadPreviewStringFunction.self
    )
    let displayName = unsafeBitCast(
      displayNameSymbol,
      to: HotReloadPreviewStringFunction.self
    )
    let freeString = unsafeBitCast(
      freeStringSymbol,
      to: HotReloadPreviewFreeStringFunction.self
    )
    let makeView = unsafeBitCast(
      makeViewSymbol,
      to: HotReloadPreviewMakeViewFunction.self
    )

    return (0..<previewCount()).compactMap { previewIndex -> PreviewVariant? in
      guard
        let id = hotReloadPreviewString(id(previewIndex), freeString: freeString),
        let groupDisplayName = hotReloadPreviewString(
          groupDisplayName(previewIndex),
          freeString: freeString
        ),
        let displayName = hotReloadPreviewString(displayName(previewIndex), freeString: freeString)
      else {
        return nil
      }

      return PreviewVariant(
        id: "\(generation):\(id)",
        groupDisplayName: groupDisplayName,
        displayName: displayName,
        makeView: {
          guard let viewPointer = makeView(previewIndex) else {
            return AnyView(EmptyView())
          }
          let view = viewPointer.assumingMemoryBound(to: AnyView.self)
          let anyView = view.move()
          view.deallocate()
          return anyView
        }
      )
    }
  }

  private static func clampedPageIndex(_ index: Int, for variants: [PreviewVariant]) -> Int {
    min(max(0, index), max(0, variants.count - 1))
  }

  private func replacePreviewVariants(with variants: [PreviewVariant]) {
    let clampedPageIndex = Self.clampedPageIndex(selectedPageIndex, for: variants)
    previewVariants = variants
    selectedPageIndex = clampedPageIndex
  }

  private func observeReloadRequests() {
    do {
      try FileManager.default.createDirectory(
        at: PreviewBrowserFiles.directoryURL,
        withIntermediateDirectories: true
      )
    } catch {
      print("Unable to create status directory: \(error.localizedDescription)")
    }
    writeStatus(phase: "running", error: nil)

    let hotReloadRequestedCallback: CFNotificationCallback = { _, observer, _, _, _ in
      guard let observer else { return }
      let store = Unmanaged<FocusedPreviewStore>
        .fromOpaque(observer)
        .takeUnretainedValue()
      Task<Void, Never> {
        store.loadHotReloadIfNeeded()
      }
    }

    CFNotificationCenterAddObserver(
      CFNotificationCenterGetDarwinNotifyCenter(),
      UnsafeRawPointer(Unmanaged.passUnretained(self).toOpaque()),
      hotReloadRequestedCallback,
      Self.hotReloadRequestedNotificationName as CFString,
      nil,
      .deliverImmediately
    )
  }

  private func writeStatus(phase: String, error: String?) {
    pendingStatusWrite = Task { [statusWriter, lastHotReloadToken, previousStatusWrite = pendingStatusWrite] in
      await previousStatusWrite?.value
      await statusWriter.write(phase: phase, lastToken: lastHotReloadToken, lastError: error)
    }
  }
}

private typealias HotReloadPreviewCountFunction = @convention(c) () -> Int
private typealias HotReloadPreviewStringFunction = @convention(c) (Int) -> UnsafeMutablePointer<CChar>?
private typealias HotReloadPreviewFreeStringFunction = @convention(c) (UnsafeMutablePointer<CChar>?) -> Void
private typealias HotReloadPreviewMakeViewFunction = @convention(c) (Int) -> UnsafeMutableRawPointer?

private func hotReloadPreviewString(
  _ pointer: UnsafeMutablePointer<CChar>?,
  freeString: HotReloadPreviewFreeStringFunction
) -> String? {
  guard let pointer else { return nil }
  defer { freeString(pointer) }
  return String(cString: pointer)
}

// MARK: - HostStatus

private struct HostStatus: Encodable {
  let pid: Int
  let phase: String
  let lastToken: String?
  let lastError: String?
}

// MARK: - PreviewBrowserFiles

private enum PreviewBrowserFiles {
  static let directoryURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    .appendingPathComponent("swiftui-preview-browser", isDirectory: true)
  static let manifestURL = directoryURL.appendingPathComponent("reload.json", isDirectory: false)
  static let statusURL = directoryURL.appendingPathComponent("status.json", isDirectory: false)
}

// MARK: - HostStatusWriter

private actor HostStatusWriter {
  private let encoder = JSONEncoder()

  func write(phase: String, lastToken: String?, lastError: String?) {
    let status = HostStatus(
      pid: Int(getpid()),
      phase: phase,
      lastToken: lastToken,
      lastError: lastError
    )
    do {
      let data = try encoder.encode(status)
      try data.write(to: PreviewBrowserFiles.statusURL, options: .atomic)
    } catch {
      print("Unable to write host status: \(error.localizedDescription)")
    }
  }
}

// MARK: - HotReloadManifest

private struct HotReloadManifest: Decodable {
  let token: String
  let dylibPath: String

  init?(url: URL) {
    do {
      let data = try Data(contentsOf: url)
      self = try JSONDecoder().decode(Self.self, from: data)
    } catch {
      print("Unable to load hot reload manifest: \(error.localizedDescription)")
      return nil
    }
  }
}

// MARK: - FocusedPreviewRootView

@MainActor
private struct FocusedPreviewRootView: View {
  var body: some View {
    if store.previewVariants.isEmpty {
      ContentUnavailableView(
        "No SwiftUI previews found",
        systemImage: "rectangle.on.rectangle.slash",
        description: Text("Try a different package or preview filter.")
      )
    } else {
      PreviewPager(
        variants: store.previewVariants,
        selectedPageIndex: $store.selectedPageIndex
      )
      .safeAreaPadding(.top)
      .overlay(alignment: .topTrailing) {
        previewControlsToggleButton
          .padding(16)
      }
      .background(Color(.systemGroupedBackground))
      .ignoresSafeArea(edges: .bottom)
    }
  }

  // MARK: Private

  @State private var store = FocusedPreviewStore()
  @State private var isPreviewControlsPresented = false

  private var previewControlsToggleButton: some View {
    Button(action: togglePreviewControls) {
      Image(systemName: "ellipsis.circle")
        .font(.body.weight(.semibold))
        .frame(width: 36, height: 36)
        .background(.regularMaterial)
        .clipShape(Circle())
        .overlay {
          Circle()
            .strokeBorder(Color.primary.opacity(0.08))
        }
    }
    .buttonStyle(.plain)
    .accessibilityLabel(
      isPreviewControlsPresented
        ? "Hide preview controls"
        : "Show preview controls"
    )
    .popover(
      isPresented: $isPreviewControlsPresented,
      attachmentAnchor: .rect(.bounds),
      arrowEdge: .top
    ) {
      PreviewControls(
        variant: store.previewVariants[store.selectedPageIndex],
        selectedPageIndex: $store.selectedPageIndex,
        previewCount: store.previewVariants.count
      )
        .presentationCompactAdaptation(.popover)
    }
  }

  private func togglePreviewControls() {
    withAnimation(.snappy) {
      isPreviewControlsPresented.toggle()
    }
  }
}

// MARK: - PreviewControls

@MainActor
private struct PreviewControls: View {
  let variant: PreviewVariant
  @Binding var selectedPageIndex: Int
  let previewCount: Int

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      HStack(spacing: 16) {
        pagingButton(
          systemImage: "chevron.left",
          accessibilityLabel: "Previous preview",
          isEnabled: selectedPageIndex > 0,
          action: { selectedPageIndex -= 1 }
        )

        Spacer(minLength: 0)

        Text(verbatim: "\(selectedPageIndex + 1) / \(previewCount)")
          .font(.caption.monospacedDigit())
          .foregroundStyle(.secondary)

        Spacer(minLength: 0)

        pagingButton(
          systemImage: "chevron.right",
          accessibilityLabel: "Next preview",
          isEnabled: selectedPageIndex + 1 < previewCount,
          action: { selectedPageIndex += 1 }
        )
      }
      .padding(.horizontal, 4)

      VStack(alignment: .center, spacing: 4) {
        Text(variant.groupDisplayName)
          .font(.headline)
          .multilineTextAlignment(.center)

        Text(variant.displayName)
          .font(.subheadline.weight(.semibold))
          .foregroundStyle(.secondary)
          .multilineTextAlignment(.center)
      }
      .frame(maxWidth: .infinity)
      .padding(.horizontal, 4)
    }
    .padding(12)
    .padding(.bottom, 4)
    .frame(width: 320)
  }

  private func pagingButton(
    systemImage: String,
    accessibilityLabel: String,
    isEnabled: Bool,
    action: @escaping () -> Void
  ) -> some View {
    Button(action: action) {
      Image(systemName: systemImage)
        .font(.body.weight(.semibold))
        .frame(width: 28, height: 36)
    }
    .buttonStyle(.plain)
    .foregroundStyle(isEnabled ? .primary : .tertiary)
    .disabled(!isEnabled)
    .accessibilityLabel(accessibilityLabel)
  }
}

// MARK: - PreviewPager

@MainActor
private struct PreviewPager: View {
  let variants: [PreviewVariant]
  @Binding var selectedPageIndex: Int

  var body: some View {
    TabView(selection: $selectedPageIndex) {
      ForEach(Array(variants.enumerated()), id: \.element.id) { variantIndex, variant in
        variant.makeView()
          .tag(variantIndex)
      }
    }
    .tabViewStyle(.page(indexDisplayMode: .never))
  }
}
