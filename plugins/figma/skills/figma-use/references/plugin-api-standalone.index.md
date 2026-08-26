# Plugin API Index

> Full typings: `plugin-api-standalone.d.ts` (11,327 lines)
> Grep by symbol name to jump to definition. All `L#` line numbers refer to that file.

---

## figma.\* — PluginAPI (L24)

### Identity & State

| Member                          | Type                                                                             |
| ------------------------------- | -------------------------------------------------------------------------------- |
| `apiVersion`                    | `'1.0.0'`                                                                        |
| `editorType`                    | `'figma' \| 'figjam' \| 'dev' \| 'slides' \| 'buzz'`                             |
| `mode`                          | `'default' \| 'textreview' \| 'inspect' \| 'codegen' \| 'linkpreview' \| 'auth'` |
| `fileKey`                       | `string \| undefined`                                                            |
| `root`                          | `DocumentNode`                                                                   |
| `currentPage`                   | `PageNode` — **read-only**; sync setter `figma.currentPage = page` does NOT work and throws; use `await figma.setCurrentPageAsync(page)` instead |
| `currentUser`                   | `User \| null`                                                                   |
| `mixed`                         | `unique symbol` — sentinel for mixed values in selection                         |
| `skipInvisibleInstanceChildren` | `boolean`                                                                        |

### Navigation & Lookup

| Method                      | Returns                                                 |
| --------------------------- | ------------------------------------------------------- |
| `setCurrentPageAsync(page)` | `Promise<void>` — **MUST use this**; sync setter `figma.currentPage = page` does NOT work |
| `getNodeByIdAsync(id)`      | `Promise<BaseNode \| null>`                             |
| `getNodeById(id)`           | `BaseNode \| null`                                      |
| `getStyleByIdAsync(id)`     | `Promise<BaseStyle \| null>`                            |
| `getStyleById(id)`          | `BaseStyle \| null`                                     |

### Create Nodes

| Method                              | Returns                     |
| ----------------------------------- | --------------------------- |
| `createFrame()`                     | `FrameNode`                 |
| `createAutoLayout(direction?)`      | `FrameNode`                 |
| `createComponent()`                 | `ComponentNode`             |
| `createComponentFromNode(node)`     | `ComponentNode`             |
| `createRectangle()`                 | `RectangleNode`             |
| `createEllipse()`                   | `EllipseNode`               |
| `createLine()`                      | `LineNode`                  |
| `createPolygon()`                   | `PolygonNode`               |
| `createStar()`                      | `StarNode`                  |
| `createVector()`                    | `VectorNode`                |
| `createText()`                      | `TextNode`                  |
| `createSection()`                   | `SectionNode`               |
| `createPage()`                      | `PageNode` — **Design files only** (`figma.com/design/...`); throws in both FigJam (`figma.com/board/...`) and Slides (`figma.com/slides/...`) |
| `createSlice()`                     | `SliceNode`                 |
| `createBooleanOperation()`          | `BooleanOperationNode`      |
| `createTable(rows?, cols?)`         | `TableNode`                 |
| `createImage(data: Uint8Array)`     | `Image`                     |
| `createNodeFromSvg(svg)`            | `FrameNode`                 |
| `createNodeFromJSXAsync(jsx)`       | `Promise<SceneNode>`        |
| `importComponentByKeyAsync(key)`    | `Promise<ComponentNode>`    |
| `importComponentSetByKeyAsync(key)` | `Promise<ComponentSetNode>` |
| `importStyleByKeyAsync(key)`        | `Promise<BaseStyle>`        |

### Styles (Local)

| Method                             | Returns         |
| ---------------------------------- | --------------- |
| `createPaintStyle()`               | `PaintStyle`    |
| `createTextStyle()`                | `TextStyle`     |
| `createEffectStyle()`              | `EffectStyle`   |
| `createGridStyle()`                | `GridStyle`     |
| `getLocalPaintStyles()` / `Async`  | `PaintStyle[]`  |
| `getLocalTextStyles()` / `Async`   | `TextStyle[]`   |
| `getLocalEffectStyles()` / `Async` | `EffectStyle[]` |
| `getLocalGridStyles()` / `Async`   | `GridStyle[]`   |

### Fonts

| Method                      | Notes                              |
| --------------------------- | ---------------------------------- |
| `loadFontAsync(fontName)`   | **MUST call before any text edit** |
| `listAvailableFontsAsync()` | `Promise<Font[]>`                  |
| `hasMissingFont`            | `boolean`                          |

### Plugin Lifecycle

| Method                                  | Notes                                                        |
| --------------------------------------- | ------------------------------------------------------------ |
| `closePlugin(message?)`                 | Auto-called; use `return` instead to pass results back       |
| `closePluginWithFailure(message?)`      | Auto-called on errors; do not call manually                  |
| `commitUndo()`                          | Snapshot to undo history                                     |
| `triggerUndo()`                         | Revert to last snapshot                                      |
| `saveVersionHistoryAsync(title, desc?)` | `Promise<VersionHistoryResult>`                              |
| `notify(message, options?)`             | **throws "not implemented" in use_figma — do not use** |
| `openExternal(url)`                     | Opens URL in browser                                         |

### Sub-APIs (properties on figma)

| Property              | Interface                | L#    |
| --------------------- | ------------------------ | ----- |
| `figma.variables`     | `VariablesAPI`           | L2016 |
| `figma.ui`            | `UIAPI`                  | L2604 |
| `figma.util`          | `UtilAPI`                | L2691 |
| `figma.constants`     | `ConstantsAPI`           | L2809 |
| `figma.clientStorage` | `ClientStorageAPI`       | L2531 |
| `figma.viewport`      | `ViewportAPI`            | L3086 |
| `figma.parameters`    | `ParametersAPI`          | L3292 |
| `figma.teamLibrary`   | `TeamLibraryAPI`         | L2372 |
| `figma.annotations`   | `AnnotationsAPI`         | L2187 |
| `figma.codegen`       | `CodegenAPI`             | L2871 |
| `figma.textreview?`   | `TextReviewAPI`          | L3166 |
| `figma.payments?`     | `PaymentsAPI`            | L2420 |
| `figma.buzz`          | `BuzzAPI`                | L2211 |
| `figma.timer?`        | `TimerAPI` (FigJam only) | L3053 |

---

## VariablesAPI — figma.variables (L2016)

```
getVariableByIdAsync(id)                 Promise<Variable | null>    ← preferred; sync deprecated
getVariableCollectionByIdAsync(id)       Promise<VariableCollection | null>    ← preferred; sync deprecated
getLocalVariablesAsync(type?)            Promise<Variable[]>         ← preferred; filter by VariableResolvedDataType; sync deprecated
getLocalVariableCollectionsAsync()       Promise<VariableCollection[]>    ← preferred; sync deprecated
createVariable(name, collection, type)   Variable
createVariableCollection(name)           VariableCollection
createVariableAlias(variable)            VariableAlias
importVariableByKeyAsync(key)            Promise<Variable>
setBoundVariableForPaint(paint, field, variable)    → returns NEW paint — reassign
setBoundVariableForEffect(effect, field, variable)  → returns NEW effect — reassign
setBoundVariableForLayoutGrid(grid, field, variable)
```

**Variable (L10153):** `name`, `resolvedType`, `codeSyntax`, `scopes`, `hiddenFromPublishing`, `valuesByMode`, `variableCollectionId`

- `setVariableCodeSyntax(platform, value)` — platform: `'WEB' | 'ANDROID' | 'iOS'`
- `setValueForMode(collectionId, modeId, value)`
- `remove()`

**VariableCollection (L10367):** `name`, `modes`, `variableIds`, `defaultModeId`, `hiddenFromPublishing`

- `addMode(name)` → `modeId`; `removeMode(modeId)`; `renameMode(modeId, name)`

---

## Node Types

### Concrete Scene Nodes

| Node                   | L#     | Key characteristics                                |
| ---------------------- | ------ | -------------------------------------------------- |
| `DocumentNode`         | L8909  | Root; `children: PageNode[]`                       |
| `PageNode`             | L9068  | `children`, local styles, `backgrounds`            |
| `FrameNode`            | L9260  | `DefaultFrameMixin` — auto-layout, clips, children |
| `GroupNode`            | L9270  | Children only, no auto-layout                      |
| `ComponentNode`        | L9627  | Like Frame + publishable                           |
| `ComponentSetNode`     | L9602  | Variant set container                              |
| `InstanceNode`         | L9668  | Like Frame; `mainComponent`, `detach()`            |
| `RectangleNode`        | L9327  | `DefaultShapeMixin` + corners                      |
| `EllipseNode`          | L9359  | + `arcData`                                        |
| `LineNode`             | L9345  |                                                    |
| `PolygonNode`          | L9379  |                                                    |
| `StarNode`             | L9399  |                                                    |
| `VectorNode`           | L9425  | Vector paths                                       |
| `TextNode`             | L9442  | Rich text, fonts, segments                         |
| `TextPathNode`         | L9513  | Text along path                                    |
| `BooleanOperationNode` | L9741  | `booleanOperation` property                        |
| `SliceNode`            | L9317  | Export only                                        |
| `SectionNode`          | L10703 | Grouping + fills                                   |
| `TableNode`            | L9811  | `TableCellNode` children                           |

**FigJam only:** `StickyNode` L9761, `ConnectorNode` L10070, `ShapeWithTextNode` L9948, `StampNode` L9787, `CodeBlockNode` L10029, `EmbedNode` L10610, `LinkUnfurlNode` L10650, `MediaNode` L10670

**Slides only:** `SlideNode` L10733, `SlideRowNode` L10758, `SlideGridNode` L10771

**Union types:**

```
type SceneNode  (L10866) = FrameNode | GroupNode | SliceNode | RectangleNode | LineNode
  | EllipseNode | PolygonNode | StarNode | VectorNode | TextNode | ComponentSetNode
  | ComponentNode | InstanceNode | BooleanOperationNode | SectionNode | ...
type BaseNode   (L10862) = DocumentNode | PageNode | SceneNode
```

---

## Mixin Interfaces

| Mixin                        | L#    | Provides                                                                                        |
| ---------------------------- | ----- | ----------------------------------------------------------------------------------------------- |
| `BaseNodeMixin`              | L5284 | `id`, `name`, `type`, `parent`, `remove()`, plugin data                                         |
| `SceneNodeMixin`             | L5535 | `visible`, `locked`, `opacity`, variable bindings                                               |
| `ChildrenMixin`              | L5747 | `children`, `appendChild()`, `insertChild()`, `findAll()`, `findOne()`, `findAllWithCriteria()` |
| `LayoutMixin`                | L6084 | `x`, `y`, `width`, `height`, `rotation`, `resize()`, `rescale()`                                |
| `AutoLayoutMixin`            | L6385 | `layoutMode`, axis alignment, padding, `itemSpacing`, `layoutSizingHorizontal/Vertical`         |
| `AutoLayoutChildrenMixin`    | L7013 | `layoutAlign`, `layoutGrow`, sizing — **set AFTER `appendChild()`**                             |
| `GridLayoutMixin`            | L6888 | CSS Grid tracks, gap, template                                                                  |
| `GridChildrenMixin`          | L7076 | grid child positioning                                                                          |
| `GeometryMixin`              | L7434 | `fills`, `strokes`, `strokeWeight`, `strokeAlign`                                               |
| `MinimalFillsMixin`          | L7277 | `fills` only                                                                                    |
| `MinimalStrokesMixin`        | L7195 | `strokes`, `strokeWeight`                                                                       |
| `BlendMixin`                 | L6288 | `opacity`, `blendMode`, `isMask`, `effects`                                                     |
| `CornerMixin`                | L7486 | `cornerRadius`, `cornerSmoothing`                                                               |
| `RectangleCornerMixin`       | L7509 | Per-corner radii                                                                                |
| `ExportMixin`                | L7526 | `exportSettings`, `exportAsync()`                                                               |
| `ReactionMixin`              | L7653 | `reactions` (prototyping)                                                                       |
| `PublishableMixin`           | L7824 | `description`, `key`, `getPublishStatusAsync()`                                                 |
| `VariantMixin`               | L8131 | `variantProperties`                                                                             |
| `ComponentPropertiesMixin`   | L8178 | `componentProperties`, `addComponentProperty()`                                                 |
| `PluginDataMixin`            | L5443 | `getSharedPluginData()`, `setSharedPluginData()`, `getSharedPluginDataKeys()`                     |
| `FramePrototypingMixin`      | L7600 | `overflowDirection`, `numberOfFixedChildren`                                                    |
| `BaseFrameMixin`             | L7888 | ChildrenMixin + LayoutMixin + AutoLayoutMixin + GeometryMixin + …                               |
| `DefaultFrameMixin`          | L7946 | BaseFrameMixin + FramePrototypingMixin + ReactionMixin                                          |
| `DefaultShapeMixin`          | L7877 | BlendMixin + GeometryMixin + LayoutMixin + ExportMixin + ReactionMixin                          |
| `ExplicitVariableModesMixin` | L9033 | `setExplicitVariableModeForCollection()`                                                        |

---

## Paint & Fill (L4302)

| Type            | L#    | Notes                                                                             |
| --------------- | ----- | --------------------------------------------------------------------------------- |
| `SolidPaint`    | L4302 | `type:'SOLID'`, `color: RGB`, `opacity`, `visible`, `blendMode`                   |
| `GradientPaint` | L4357 | `type: 'GRADIENT_LINEAR\|RADIAL\|ANGULAR\|DIAMOND'`, `gradientStops: ColorStop[]` |
| `ImagePaint`    | L4377 | `type:'IMAGE'`, `imageHash`, `scaleMode`                                          |
| `VideoPaint`    | L4413 | `type:'VIDEO'`                                                                    |
| `PatternPaint`  | L4449 | `type:'PATTERN'`                                                                  |
| `type Paint`    | L4481 | Union of all five                                                                 |
| `ColorStop`     | L4271 | `{ position: number, color: RGBA }`                                               |
| `ImageFilters`  | L4290 | exposure, contrast, saturation, etc.                                              |

> **CRITICAL**: Fills/strokes are **read-only arrays** — clone, modify, reassign.

---

## Effects (L3966)

| Type                               | L#    |
| ---------------------------------- | ----- |
| `DropShadowEffect`                 | L3966 |
| `InnerShadowEffect`                | L4009 |
| `BlurEffect` (Normal/Progressive)  | L4048 |
| `NoiseEffect` (Mono/Duo/Multitone) | L4105 |
| `TextureEffect`                    | L4180 |
| `GlassEffect`                      | L4209 |
| `type Effect`                      | L4250 |

---

## Typography

| Type                | L#    | Notes                                                                                  |
| ------------------- | ----- | -------------------------------------------------------------------------------------- |
| `FontName`          | L3697 | `{ family: string, style: string }`                                                    |
| `TextNode`          | L9442 | `characters`, `textAlignHorizontal`, `fontSize`, `fontName`, `getStyledTextSegments()` |
| `StyledTextSegment` | L4882 | Per-range text properties                                                              |
| `LetterSpacing`     | L4826 | `{ value, unit: 'PIXELS'\|'PERCENT' }`                                                 |
| `LineHeight`        | L4830 | `{ value, unit } \| { unit: 'AUTO' }`                                                  |
| `TextCase`          | L3701 | `'ORIGINAL'\|'UPPER'\|'LOWER'\|'TITLE'\|'SMALL_CAPS'`                                  |
| `TextDecoration`    | L3702 | `'NONE'\|'UNDERLINE'\|'STRIKETHROUGH'`                                                 |
| `OpenTypeFeature`   | L3728 | Ligatures, numerals, etc.                                                              |

---

## Variables & Bindings

| Type                          | L#     | Notes                                                         |
| ----------------------------- | ------ | ------------------------------------------------------------- |
| `Variable`                    | L10153 | Core variable object                                          |
| `VariableCollection`          | L10367 | Collection of variables + modes                               |
| `VariableAlias`               | L10121 | Reference to another variable                                 |
| `VariableValue`               | L10125 | `boolean \| string \| number \| RGB \| RGBA \| VariableAlias` |
| `VariableResolvedDataType`    | L10120 | `'BOOLEAN' \| 'COLOR' \| 'FLOAT' \| 'STRING'`                 |
| `VariableDataType`            | L5023  | Includes `'VARIABLE_ALIAS' \| 'EXPRESSION'`                   |
| `VariableScope`               | L10126 | Where variable can be applied                                 |
| `CodeSyntaxPlatform`          | L10152 | `'WEB' \| 'ANDROID' \| 'iOS'`                                 |
| `VariableBindableNodeField`   | L5686  | Node fields that accept variable binding                      |
| `VariableBindableTextField`   | L5713  | Text-specific bindable fields                                 |
| `VariableBindablePaintField`  | L5722  | `'color'`                                                     |
| `VariableBindableEffectField` | L5725  | `'color'\|'radius'\|'spread'\|'offsetX'\|'offsetY'`           |

---

## Styles

| Interface        | L#     | Notes                                                  |
| ---------------- | ------ | ------------------------------------------------------ |
| `BaseStyleMixin` | L10926 | `name`, `id`, `key`, `type`, `description`, `remove()` |
| `PaintStyle`     | L10951 | `type:'PAINT'`, `paints: Paint[]`                      |
| `TextStyle`      | L10967 | `type:'TEXT'`, font properties                         |
| `EffectStyle`    | L11036 | `type:'EFFECT'`, `effects: Effect[]`                   |
| `GridStyle`      | L11052 | `type:'GRID'`, `layoutGrids`                           |
| `type BaseStyle` | L11068 | Union of all four                                      |
| `type StyleType` | L10904 | `'PAINT' \| 'TEXT' \| 'EFFECT' \| 'GRID'`              |

---

## Primitives & Geometry

| Type             | L#    | Shape                                         |
| ---------------- | ----- | --------------------------------------------- |
| `Vector`         | L3667 | `{ x: number, y: number }`                    |
| `Rect`           | L3671 | `{ x, y, width, height }`                     |
| `RGB`            | L3680 | `{ r, g, b }` — **0–1 range, not 0–255**      |
| `RGBA`           | L3688 | `{ r, g, b, a }` — **0–1 range**              |
| `Transform`      | L3666 | `[[a,b,tx],[c,d,ty]]` 2×3 affine matrix       |
| `ArcData`        | L3958 | `{ startingAngle, endingAngle, innerRadius }` |
| `Constraints`    | L4264 | `{ horizontal, vertical }: ConstraintType`    |
| `ConstraintType` | L4260 | `'MIN'\|'CENTER'\|'MAX'\|'STRETCH'\|'SCALE'`  |
| `VectorPath`     | L4792 | `{ windingRule, data: string }`               |
| `VectorNetwork`  | L4775 | vertices + segments + regions                 |
| `Guide`          | L4482 | `{ axis, offset }`                            |

---

## Prototyping

| Type                  | L#    | Notes                                                     |
| --------------------- | ----- | --------------------------------------------------------- |
| `Reaction`            | L5015 | trigger + action pair                                     |
| `Trigger`             | L5146 | what initiates the reaction                               |
| `Action`              | L5064 | what happens                                              |
| `Transition`          | L5145 | `SimpleTransition \| DirectionalTransition`               |
| `Easing`              | L5182 | easing curve definition                                   |
| `Navigation`          | L5178 | `'NAVIGATE'\|'SWAP'\|'OVERLAY'\|'SCROLL_TO'\|'CHANGE_TO'` |
| `OverflowDirection`   | L5215 | `'NONE'\|'HORIZONTAL'\|'VERTICAL'\|'BOTH'`                |
| `OverlayPositionType` | L5219 | overlay placement                                         |

---

## Events & Changes

| Type                  | L#    | Notes                                                           |
| --------------------- | ----- | --------------------------------------------------------------- |
| `ArgFreeEventType`    | L11   | `'selectionchange'\|'currentpagechange'\|'close'\|timer events` |
| `RunEvent`            | L3321 | plugin run with parameters                                      |
| `DropEvent`           | L3339 | drag-and-drop                                                   |
| `DocumentChangeEvent` | L3359 | any document change                                             |
| `NodeChangeEvent`     | L3626 | node property changes                                           |
| `NodeChangeProperty`  | L3499 | all watchable property names                                    |
| `StyleChangeEvent`    | L3365 | style create/delete/update                                      |
| `DocumentChange`      | L3489 | `CreateChange \| DeleteChange \| PropertyChange`                |
| `TextReviewEvent`     | L3657 | text review mode                                                |

---

## Export

| Type                        | L#    | Notes                                         |
| --------------------------- | ----- | --------------------------------------------- |
| `ExportSettingsImage`       | L4561 | PNG/JPG/WEBP/BMP                              |
| `ExportSettingsSVG`         | L4634 |                                               |
| `ExportSettingsPDF`         | L4653 |                                               |
| `ExportSettingsREST`        | L4667 |                                               |
| `ExportSettingsConstraints` | L4554 | `{ type: 'SCALE'\|'WIDTH'\|'HEIGHT', value }` |

---

## Key Sub-API Surfaces

**ClientStorageAPI (L2531):** `getAsync(key)`, `setAsync(key, value)`, `keysAsync()`, `deleteAsync(key)`

**ViewportAPI (L3086):** `center: Vector`, `zoom: number`, `scrollAndZoomIntoView(nodes)`, `bounds: Rect`

**UtilAPI (L2691):** `solidPaint(hex, opacity?)`, `rgba(r,g,b,a?)`, `rgb(r,g,b)`, `colorToHex(color)`, `loadImageAsync(url)`, `clone(val)`

**TeamLibraryAPI (L2372):** `getAvailableLibraryVariableCollectionsAsync()`, `importVariableByKeyAsync(key)`

**Image (L11069):** `hash`, `getBytesAsync()`, `getSizeAsync()`

---

## All Symbols (flat — grep these against the .d.ts file)

To find any symbol: `grep -n "^interface Foo\|^type Foo\|^declare type Foo" plugin-api-standalone.d.ts`

```
PluginAPI               VariablesAPI            AnnotationsAPI          TeamLibraryAPI
UIAPI                   UtilAPI                 ViewportAPI             ClientStorageAPI
ConstantsAPI            CodegenAPI              PaymentsAPI             TextReviewAPI
ParametersAPI           TimerAPI                BuzzAPI                 DevResourcesAPI

DocumentNode            PageNode                FrameNode               GroupNode
ComponentNode           ComponentSetNode        InstanceNode            RectangleNode
EllipseNode             LineNode                PolygonNode             StarNode
VectorNode              TextNode                TextPathNode            BooleanOperationNode
SliceNode               SectionNode             TableNode               TableCellNode
StickyNode              ConnectorNode           ShapeWithTextNode       StampNode
CodeBlockNode           EmbedNode               LinkUnfurlNode          MediaNode
WidgetNode              SlideNode               SlideRowNode            SlideGridNode
TransformGroupNode      HighlightNode           WashiTapeNode

BaseNodeMixin           SceneNodeMixin          ChildrenMixin           LayoutMixin
AutoLayoutMixin         AutoLayoutChildrenMixin GridLayoutMixin         GridChildrenMixin
GeometryMixin           MinimalFillsMixin       MinimalStrokesMixin     BlendMixin
MinimalBlendMixin       CornerMixin             RectangleCornerMixin    ExportMixin
ReactionMixin           PublishableMixin        VariantMixin            ComponentPropertiesMixin
PluginDataMixin         DevResourcesMixin       DevStatusMixin          StickableMixin
ConstraintMixin         DimensionAndPositionMixin AspectRatioLockMixin  FramePrototypingMixin
BaseFrameMixin          DefaultFrameMixin       DefaultShapeMixin       OpaqueNodeMixin
VectorLikeMixin         ComplexStrokesMixin     IndividualStrokesMixin  ContainerMixin
AnnotationsMixin        MeasurementsMixin       ExplicitVariableModesMixin

Variable                VariableCollection      VariableAlias           ExtendedVariableCollection
LibraryVariableCollection LibraryVariable
VariableValue           VariableResolvedDataType VariableDataType       VariableScope
CodeSyntaxPlatform      VariableBindableNodeField VariableBindableTextField
VariableBindablePaintField VariableBindableEffectField VariableBindableLayoutGridField

SolidPaint              GradientPaint           ImagePaint              VideoPaint
PatternPaint            Paint                   ColorStop               ImageFilters
DropShadowEffect        InnerShadowEffect       BlurEffect              NoiseEffect
TextureEffect           GlassEffect             Effect
LayoutGrid              RowsColsLayoutGrid      GridLayoutGrid

PaintStyle              TextStyle               EffectStyle             GridStyle
BaseStyle               BaseStyleMixin          StyleType

FontName                Font                    LetterSpacing           LineHeight
TextCase                TextDecoration          TextDecorationStyle     FontStyle
OpenTypeFeature         StyledTextSegment       LeadingTrim

Vector                  Rect                    RGB                     RGBA
Transform               ArcData                 Constraints             ConstraintType
VectorPath              VectorNetwork           VectorVertex            VectorSegment
VectorRegion            Guide                   BlendMode               MaskType

Reaction                Trigger                 Action                  Transition
Easing                  Navigation              OverflowDirection       OverlayPositionType
OverlayBackground       PublishStatus

ArgFreeEventType        RunEvent                DropEvent               DocumentChangeEvent
NodeChangeEvent         NodeChangeProperty      StyleChangeEvent        DocumentChange
TextReviewEvent         SlidesViewChangeEvent   CanvasViewChangeEvent

ExportSettingsImage     ExportSettingsSVG       ExportSettingsPDF       ExportSettingsREST
ExportSettingsConstraints

User                    ActiveUser              BaseUser                Image
Video                   VersionHistoryResult    FindAllCriteria
```

---

## Additional APIs (available via use_figma)

### Node Methods

| Method / Property             | Returns / Type    | Description |
| ----------------------------- | ----------------- | ----------- |
| `node.query(selector)`        | `QueryResult`     | CSS-like selector search within subtree |
| `node.matches(selector)`      | `boolean`         | Test if node matches a selector |
| `node.set(props)`             | `this`            | Set multiple properties at once, chainable |
| `await node.screenshot(opts?)` | `Promise<void>`  | Capture PNG inline in tool response |
| `node.placeholder`            | `boolean`         | Show/hide shimmer overlay |

### figma.io Namespace

| Method                        | Returns           | Description |
| ----------------------------- | ----------------- | ----------- |
| `figma.io.write(path, data)`  | `void`            | Write image/data to be returned in tool response |

### Types

| Type                | Description |
| ------------------- | ----------- |
| `QueryResult`       | Iterable result from `node.query()` with `.first()`, `.last()`, `.each()`, `.map()`, `.filter()`, `.values()`, `.set()`, `.query()` |
| `ScreenshotOptions` | `{ scale?: number, contentsOnly?: boolean }` |
