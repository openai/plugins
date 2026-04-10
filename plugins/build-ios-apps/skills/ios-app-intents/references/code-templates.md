# Code templates

These templates are intentionally generic. Rename types and services to fit the app.

## Open-app handoff intent

```swift
import AppIntents

struct OpenComposerIntent: AppIntent {
  static let title: LocalizedStringResource = "Open composer"
  static let description = IntentDescription("Open the app to compose content")
  static let openAppWhenRun = true

  @Parameter(
    title: "Prefilled text",
    inputConnectionBehavior: .connectToPreviousIntentResult
  )
  var text: String?

  func perform() async throws -> some IntentResult {
    await MainActor.run {
      AppIntentRouter.shared.handledIntent = .init(intent: self)
    }
    return .result()
  }
}
```

Scene-side handoff:

```swift
import AppIntents
import Observation

@Observable
final class AppIntentRouter {
  struct HandledIntent: Equatable {
    let id = UUID()
    let intent: any AppIntent

    static func == (lhs: Self, rhs: Self) -> Bool {
      lhs.id == rhs.id
    }
  }

  static let shared = AppIntentRouter()
  var handledIntent: HandledIntent?

  private init() {}
}

private func handleIntent() {
  guard let intent = appIntentRouter.handledIntent?.intent else { return }

  if let composerIntent = intent as? OpenComposerIntent {
    appRouter.presentComposer(prefilledText: composerIntent.text ?? "")
  } else if let sectionIntent = intent as? OpenSectionIntent {
    selectedTab = sectionIntent.section.toTab
  }
}
```

## Inline action intent

```swift
import AppIntents

struct CreateItemIntent: AppIntent {
  static let title: LocalizedStringResource = "Create item"
  static let description = IntentDescription("Create a new item without opening the app")
  static let openAppWhenRun = false

  @Parameter(title: "Title")
  var title: String

  @Parameter(title: "Workspace")
  var workspace: WorkspaceEntity

  func perform() async throws -> some IntentResult & ProvidesDialog {
    do {
      try await ItemService.shared.createItem(title: title, workspaceID: workspace.id)
      return .result(dialog: "Created \(title).")
    } catch {
      return .result(dialog: "Could not create the item. Please try again.")
    }
  }
}
```

## Fixed selection with `AppEnum`

```swift
import AppIntents

enum SectionIntentValue: String, AppEnum {
  case inbox
  case projects
  case settings

  static var typeDisplayName: LocalizedStringResource { "Section" }
  static let typeDisplayRepresentation: TypeDisplayRepresentation = "Section"

  static var caseDisplayRepresentations: [Self: DisplayRepresentation] {
    [
      .inbox: "Inbox",
      .projects: "Projects",
      .settings: "Settings",
    ]
  }

  var toTab: AppTab {
    switch self {
    case .inbox: .inbox
    case .projects: .projects
    case .settings: .settings
    }
  }
}

struct OpenSectionIntent: AppIntent {
  static let title: LocalizedStringResource = "Open section"
  static let openAppWhenRun = true

  @Parameter(title: "Section")
  var section: SectionIntentValue

  func perform() async throws -> some IntentResult {
    await MainActor.run {
      AppIntentRouter.shared.handledIntent = .init(intent: self)
    }
    return .result()
  }
}
```

## Entity and query

```swift
import AppIntents

struct WorkspaceEntity: AppEntity, Identifiable {
  let workspace: Workspace

  var id: String { workspace.id }

  static let typeDisplayRepresentation: TypeDisplayRepresentation = "Workspace"
  static let defaultQuery = WorkspaceQuery()

  var displayRepresentation: DisplayRepresentation {
    DisplayRepresentation(title: "\(workspace.name)")
  }
}

struct WorkspaceQuery: EntityQuery {
  func entities(for identifiers: [WorkspaceEntity.ID]) async throws -> [WorkspaceEntity] {
    let workspaces = try await WorkspaceStore.shared.workspaces(matching: identifiers)
    return workspaces.map(WorkspaceEntity.init)
  }

  func suggestedEntities() async throws -> [WorkspaceEntity] {
    try await WorkspaceStore.shared.recentWorkspaces().map(WorkspaceEntity.init)
  }

  func defaultResult() async -> WorkspaceEntity? {
    guard let workspace = try? await WorkspaceStore.shared.currentWorkspace() else { return nil }
    return WorkspaceEntity(workspace: workspace)
  }
}
```

## Dependent query

```swift
import AppIntents

struct ProjectEntity: AppEntity, Identifiable {
  let project: Project

  var id: String { project.id }

  static let typeDisplayRepresentation: TypeDisplayRepresentation = "Project"
  static let defaultQuery = ProjectQuery()

  var displayRepresentation: DisplayRepresentation {
    DisplayRepresentation(title: "\(project.name)")
  }
}

struct ProjectSelectionIntent: WidgetConfigurationIntent {
  static let title: LocalizedStringResource = "Project widget configuration"

  @Parameter(title: "Workspace")
  var workspace: WorkspaceEntity?

  @Parameter(title: "Project")
  var project: ProjectEntity?
}

struct ProjectQuery: EntityQuery {
  @IntentParameterDependency<ProjectSelectionIntent>(\.$workspace)
  var workspace

  func entities(for identifiers: [ProjectEntity.ID]) async throws -> [ProjectEntity] {
    try await fetchProjects().filter { identifiers.contains($0.id) }.map(ProjectEntity.init)
  }

  func suggestedEntities() async throws -> [ProjectEntity] {
    try await fetchProjects().map(ProjectEntity.init)
  }

  func defaultResult() async -> ProjectEntity? {
    try? await fetchProjects().first.map(ProjectEntity.init)
  }

  private func fetchProjects() async throws -> [Project] {
    guard let workspaceID = workspace?.id else { return [] }
    return try await ProjectStore.shared.projects(in: workspaceID)
  }
}
```

## Widget configuration intent

```swift
import AppIntents
import WidgetKit

struct ActivityWidgetConfiguration: WidgetConfigurationIntent {
  static let title: LocalizedStringResource = "Activity widget configuration"
  static let description = IntentDescription("Choose which workspace and filter the widget should show")

  @Parameter(title: "Workspace")
  var workspace: WorkspaceEntity?

  @Parameter(title: "Filter")
  var filter: ActivityFilterEntity?
}
```

## App shortcuts provider

```swift
import AppIntents

struct AppShortcuts: AppShortcutsProvider {
  static var appShortcuts: [AppShortcut] {
    AppShortcut(
      intent: OpenComposerIntent(),
      phrases: [
        "Open composer in \(.applicationName)",
        "Draft with \(.applicationName)",
      ],
      shortTitle: "Open composer",
      systemImageName: "square.and.pencil"
    )

    AppShortcut(
      intent: CreateItemIntent(),
      phrases: [
        "Create item with \(.applicationName)",
        "Add a task in \(.applicationName)",
      ],
      shortTitle: "Create item",
      systemImageName: "plus.circle"
    )
  }
}
```

## Inline file input

```swift
import AppIntents
import UniformTypeIdentifiers

struct ImportAttachmentIntent: AppIntent {
  static let title: LocalizedStringResource = "Import attachment"
  static let openAppWhenRun = false

  @Parameter(
    title: "Files",
    supportedContentTypes: [.image, .pdf, .plainText],
    inputConnectionBehavior: .connectToPreviousIntentResult
  )
  var files: [IntentFile]

  func perform() async throws -> some IntentResult & ProvidesDialog {
    guard !files.isEmpty else {
      return .result(dialog: "No files were provided.")
    }

    for file in files {
      guard let url = file.fileURL else { continue }
      _ = url.startAccessingSecurityScopedResource()
      defer { url.stopAccessingSecurityScopedResource() }
      try await AttachmentImporter.shared.importFile(at: url)
    }

    return .result(dialog: "Imported \(files.count) file(s).")
  }
}
```
