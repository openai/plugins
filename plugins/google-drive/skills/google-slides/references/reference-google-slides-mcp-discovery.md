# Google Slides MCP Discovery Reference

`mcp__codex_apps__google_drive_*` tools are very similar to the Google Slides API, but has some small differences. 
Use this file to understand the differences, so you know how to call `mcp__codex_apps__google_drive_*` tools correctly. 

This file does not define new tools. It explains how to translate between the public Google Slides API shape and the Google Drive MCP wrapper shape so agents stop mixing REST fields, connector wrapper fields, and raw batchUpdate request bodies.

When in doubt, you can always curl the official Slides discovery for the underlying API: `https://slides.googleapis.com/$discovery/rest?version=v1`.


## Service Overview

- Connector namespace in Codex: `mcp__codex_apps__google_drive`.
- Slides scope: read Google Slides presentations, inspect slides/tables/text/outline, create native Slides files, move/rename Drive files, and apply raw Google Slides `presentations.batchUpdate` requests through the connector wrapper.
- Authentication and OAuth scopes are hidden by the connector. Models should not ask the user for OAuth tokens when using these MCP tools.
- Target identity is explicit: use a raw presentation id or a Google Slides URL accepted by the wrapper. Always prefer a fresh connector read before a write.
- The connector wrapper uses snake_case arguments such as `presentation_id`, `presentation_url`, `write_control`, and `image_uris`.
- Raw Slides request objects inside `_batch_update_presentation.requests[]` keep the official Google Slides REST camelCase names and field names, such as `updateTableBorderProperties`, `textRange`, and `writeControl`'s inner `requiredRevisionId` equivalent.
- Full MCP tool names use the `mcp__codex_apps__google_drive_*` form. In Node examples, call `tools["mcp__codex_apps__google_drive_get_presentation"]` with an argument object, not short aliases or dot-call helpers.
- Treat Drive file lifecycle operations and Slides content operations as separate surfaces: `_create_file` and `_update_file` are Drive operations; `_batch_update_presentation` is the Slides content update wrapper.


## Google Slides API vs Google Drive MCP

Use this table when translating examples from `https://slides.googleapis.com/$discovery/rest?version=v1`, public Google Slides docs, or prior REST habits into connector calls.

| Concept | Public Google Slides API | Google Drive MCP | What the model should do |
| --- | --- | --- | --- |
| Call surface | HTTP REST methods such as `POST /v1/presentations/{presentationId}:batchUpdate`. | MCP tools named `mcp__codex_apps__google_drive_*`. | Call the MCP tool directly; do not construct REST URLs. |
| Auth | OAuth scopes and bearer tokens are explicit in discovery docs. | Auth is handled by the connector. | Do not ask the user for OAuth tokens or scopes. |
| Presentation target | `presentationId` is a path parameter. | `presentation_id` or `presentation_url` is a wrapper argument. | Put the deck id or URL in the MCP wrapper, not inside `requests[]`. |
| Batch update body | JSON body has `requests` and optional `writeControl`. | Wrapper has `requests` and optional `write_control`. | Use `write_control` at MCP wrapper level; do not send wrapper fields in REST casing. |
| Individual requests | `requests[]` items use official camelCase keys and fields. | Same: raw request objects inside `requests[]` use official camelCase. | Use `updateTableBorderProperties`, `textRange`, `objectId`, etc. inside request objects. |
| Request typing | Discovery enumerates the `Request` union and field schemas. | MCP metadata exposes `requests: object[]`. | Missing request-specific MCP typing is not evidence of unsupported request types. |
| Local images | REST image fields require public URLs such as `url` or `imageUrl`. | Connector adds `image_uris` for local/generated image bytes. | Use `image_uris` only at wrapper level when passing local files. |
| Response | Discovery defines `BatchUpdatePresentationResponse`. | MCP return shape is connector-specific and not documented like discovery. | Verify important writes with connector readback and thumbnails. |
| File lifecycle | Slides REST focuses on presentation content APIs. | `_create_file` and `_update_file` are Drive file operations exposed in the same connector namespace. | Use Drive operations for create/rename/move; use `_batch_update_presentation` for slide content edits. |

## Method Catalog

| MCP method | Purpose | Official Slides mapping | Notes |
| --- | --- | --- | --- |
| `_get_presentation` | Read deck metadata and slide content. | Conceptually maps to `presentations.get`. | Use when page elements, object ids, transforms, charts, layouts, or notes may matter. |
| `_get_presentation_text` | Read text-only presentation content. | Conceptually maps to `presentations.get` plus connector text extraction. | Lower payload; do not rely on it for charts/images/layout. |
| `_get_presentation_outline` | Read compact slide outline with slide numbers/object ids. | Connector convenience over `presentations.get`. | Good first pass for slide targeting. |
| `_get_slide` | Read one slide by slide object id. | Conceptually maps to selecting one page from `presentations.get`. | Use before slide-level writes to capture live ids and geometry. |
| `_get_presentation_tables` | Read table structures and cell text with coordinates. | Connector convenience over table page elements in `presentations.get`. | Use for table inspection before table edits. |
| `_batch_update_presentation` | Apply Google Slides batchUpdate requests. | Maps to `presentations.batchUpdate`. | Outer wrapper differs; inner `requests[]` follows official REST shape. |
| `_create_file` | Create a native Google Workspace file. | Drive file creation, not a Slides REST method. | For Slides, use only `mime_type = application/vnd.google-apps.presentation`. |
| `_update_file` | Rename or move a Drive file. | Drive metadata/parents update, not a Slides REST method. | Use for deck rename/move only; not presentation content edits. |

## Method Schemas

### `_get_presentation`

- Purpose: Read deck metadata and full slide content.
- Official mapping: presentations.get.
- Input schema:

```ts
{
  "presentation_id"?: string | null,
  "presentation_url"?: string | null
}
```

- Model notes: Pass either a raw presentation id or a Google Slides URL. Use this before writes when object IDs, charts, images, transforms, or layouts may matter.

### `_get_presentation_text`

- Purpose: Read lower-payload text-only deck content.
- Official mapping: presentations.get plus connector text extraction.
- Input schema:

```ts
{
  "presentation_id"?: string | null,
  "presentation_url"?: string | null
}
```

- Model notes: Good for summarization; insufficient for layout, chart, table, image, or object-id work.

### `_get_presentation_outline`

- Purpose: Read a stable compact outline for slide targeting.
- Official mapping: connector convenience over presentations.get.
- Input schema:

```ts
{
  "presentation_url": string
}
```

- Model notes: Response includes slide numbers, slide object ids, compact text, and revision metadata when available.

### `_get_slide`

- Purpose: Read one slide by object id.
- Official mapping: connector convenience over presentations.get pages.
- Input schema:

```ts
{
  "presentation_id"?: string | null,
  "presentation_url"?: string | null,
  "slide_object_id": string
}
```

- Model notes: Use the slide resource object id, not the slide number. Use before writing to that slide.

### `_get_presentation_tables`

- Purpose: Read table structures with row/column coordinates preserved.
- Official mapping: connector convenience over table page elements.
- Input schema:

```ts
{
  "presentation_url": string
}
```

- Model notes: Use before table updates such as row, column, cell, and border edits.

### `_batch_update_presentation`

- Purpose: Apply raw Google Slides content updates.
- Official mapping: presentations.batchUpdate.
- Input schema:

```ts
{
  "presentation_id"?: string | null,
  "presentation_url"?: string | null,
  "requests": object[],
  "write_control"?: {
    "requiredRevisionId"?: string | null
  } | null,
  "image_uris"?: string
}
```

- Model notes: Each request object must set exactly one top-level official Slides request key. Do not pass stringified JSON.

### `_create_file`

- Purpose: Create a native Google file; scoped here to Slides deck creation.
- Official mapping: Drive files.create, not Slides discovery.
- Input schema:

```ts
{
  "mime_type": "application/vnd.google-apps.presentation",
  "title": string
}
```

- Model notes: Only include this in Slides workflows when creating a blank native Slides deck.

### `_update_file`

- Purpose: Rename or move an existing Drive file.
- Official mapping: Drive files.update, not Slides discovery.
- Input schema:

```ts
{
  "fileId": string,
  "name"?: string | null,
  "addParents"?: string | null,
  "removeParents"?: string | null
}
```

- Model notes: Use for Drive metadata/parent operations only. Do not use for slide content updates.

## Connector Differences From Official Slides Discovery

| Area | Official discovery | Google Drive MCP | Model consequence |
| --- | --- | --- | --- |
| Target id | REST path parameter `presentationId`. | Wrapper arg `presentation_id` or `presentation_url`. | Do not put `presentationId` inside the request body. |
| Wrapper naming | Body field `writeControl`. | Wrapper field `write_control`. | Use snake_case only at wrapper level. |
| Request naming | `requests[]` items use camelCase request keys. | Same inner camelCase request keys. | Keep `updateTableBorderProperties`, not `update_table_border_properties`. |
| Request typing | `requests.items.$ref = Request` with 44 named union arms. | `requests: object[]`. | Missing MCP field typing is not evidence of unsupported request keys. |
| Image bytes | Image requests use public URL fields such as `url` or `imageUrl`. | Adds connector-only `image_uris` sidecar for local/generated images. | Pair local image placeholders with `image_uris`; raw Slides REST cannot do this. |
| Auth/scopes | Discovery lists OAuth scopes. | Connector manages auth. | Models should not request bearer tokens. |
| Response schema | `BatchUpdatePresentationResponse` has `presentationId`, `replies`, `writeControl`. | Tool metadata does not expose a comparable return schema. | Treat return shape as connector-specific; verify by readback. |
| File lifecycle | Slides discovery covers presentation get/create/batchUpdate. | `_create_file` and `_update_file` are Drive operations included for deck create/rename/move. | Do not confuse Drive metadata updates with slide content updates. |

## Batch Update Wrapper

Official `presentations.batchUpdate` evidence:

```json
{
  "id": "slides.presentations.batchUpdate",
  "httpMethod": "POST",
  "path": "v1/presentations/{presentationId}:batchUpdate",
  "request": {
    "$ref": "BatchUpdatePresentationRequest"
  },
  "response": {
    "$ref": "BatchUpdatePresentationResponse"
  },
  "bodyProperties": [
    "requests",
    "writeControl"
  ]
}
```

MCP wrapper shape:

```ts
tools["mcp__codex_apps__google_drive_batch_update_presentation"]({
  presentation_id?: string | null,
  presentation_url?: string | null,
  requests: Array<Record<string, unknown>>,
  write_control?: { requiredRevisionId?: string | null } | null,
  image_uris?: string,
})
```

Rules:

- The outer wrapper is connector-specific.
- `requests` must be an array of structured objects, not JSON strings.
- Each request object must have exactly one top-level request key.
- Inner request keys and fields use official Slides REST camelCase.
- Use `write_control.requiredRevisionId` only when intentionally guarding against concurrent edits.
- For local/generated images, put the local path in `image_uris` and use the same non-public placeholder in the request URL field as required by connector metadata.

## Batch Update Request Catalog

Official discovery currently exposes 44 `Request` union arms. The MCP wrapper is raw pass-through for request items, so the catalog below uses official request names and fields while noting connector-specific coverage.

| Request key | Official `$ref` | Official request fields | Official reply | MCP support note |
| --- | --- | --- | --- | --- |
| `createImage` | `CreateImageRequest` | `elementProperties, objectId, url` | `CreateImageResponse` | raw pass-through plus connector `image_uris` sidecar when local bytes are used |
| `createLine` | `CreateLineRequest` | `category, elementProperties, lineCategory, objectId` | `CreateLineResponse` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `createParagraphBullets` | `CreateParagraphBulletsRequest` | `bulletPreset, cellLocation, objectId, textRange` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `createShape` | `CreateShapeRequest` | `elementProperties, objectId, shapeType` | `CreateShapeResponse` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `createSheetsChart` | `CreateSheetsChartRequest` | `chartId, elementProperties, linkingMode, objectId, spreadsheetId` | `CreateSheetsChartResponse` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `createSlide` | `CreateSlideRequest` | `insertionIndex, objectId, placeholderIdMappings, slideLayoutReference` | `CreateSlideResponse` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `createTable` | `CreateTableRequest` | `columns, elementProperties, objectId, rows` | `CreateTableResponse` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `createVideo` | `CreateVideoRequest` | `elementProperties, id, objectId, source` | `CreateVideoResponse` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `deleteObject` | `DeleteObjectRequest` | `objectId` | `empty reply` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `deleteParagraphBullets` | `DeleteParagraphBulletsRequest` | `cellLocation, objectId, textRange` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `deleteTableColumn` | `DeleteTableColumnRequest` | `cellLocation, tableObjectId` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `deleteTableRow` | `DeleteTableRowRequest` | `cellLocation, tableObjectId` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `deleteText` | `DeleteTextRequest` | `cellLocation, objectId, textRange` | `empty reply` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `duplicateObject` | `DuplicateObjectRequest` | `objectId, objectIds` | `DuplicateObjectResponse` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `groupObjects` | `GroupObjectsRequest` | `childrenObjectIds, groupObjectId` | `GroupObjectsResponse` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `insertTableColumns` | `InsertTableColumnsRequest` | `cellLocation, insertRight, number, tableObjectId` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `insertTableRows` | `InsertTableRowsRequest` | `cellLocation, insertBelow, number, tableObjectId` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `insertText` | `InsertTextRequest` | `cellLocation, insertionIndex, objectId, text` | `empty reply` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `mergeTableCells` | `MergeTableCellsRequest` | `objectId, tableRange` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `refreshSheetsChart` | `RefreshSheetsChartRequest` | `objectId` | `empty reply` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `replaceAllShapesWithImage` | `ReplaceAllShapesWithImageRequest` | `containsText, imageReplaceMethod, imageUrl, pageObjectIds, replaceMethod` | `ReplaceAllShapesWithImageResponse` | raw pass-through plus connector `image_uris` sidecar when local bytes are used |
| `replaceAllShapesWithSheetsChart` | `ReplaceAllShapesWithSheetsChartRequest` | `chartId, containsText, linkingMode, pageObjectIds, spreadsheetId` | `ReplaceAllShapesWithSheetsChartResponse` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `replaceAllText` | `ReplaceAllTextRequest` | `containsText, pageObjectIds, replaceText` | `ReplaceAllTextResponse` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `replaceImage` | `ReplaceImageRequest` | `imageObjectId, imageReplaceMethod, url` | `empty reply` | raw pass-through plus connector `image_uris` sidecar when local bytes are used |
| `rerouteLine` | `RerouteLineRequest` | `objectId` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `ungroupObjects` | `UngroupObjectsRequest` | `objectIds` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `unmergeTableCells` | `UnmergeTableCellsRequest` | `objectId, tableRange` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateImageProperties` | `UpdateImagePropertiesRequest` | `fields, imageProperties, objectId` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateLineCategory` | `UpdateLineCategoryRequest` | `lineCategory, objectId` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateLineProperties` | `UpdateLinePropertiesRequest` | `fields, lineProperties, objectId` | `empty reply` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `updatePageElementAltText` | `UpdatePageElementAltTextRequest` | `description, objectId, title` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updatePageElementTransform` | `UpdatePageElementTransformRequest` | `applyMode, objectId, transform` | `empty reply` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `updatePageElementsZOrder` | `UpdatePageElementsZOrderRequest` | `operation, pageElementObjectIds` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updatePageProperties` | `UpdatePagePropertiesRequest` | `fields, objectId, pageProperties` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateParagraphStyle` | `UpdateParagraphStyleRequest` | `cellLocation, fields, objectId, style, textRange` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateShapeProperties` | `UpdateShapePropertiesRequest` | `fields, objectId, shapeProperties` | `empty reply` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `updateSlideProperties` | `UpdateSlidePropertiesRequest` | `fields, objectId, slideProperties` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateSlidesPosition` | `UpdateSlidesPositionRequest` | `insertionIndex, slideObjectIds` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateTableBorderProperties` | `UpdateTableBorderPropertiesRequest` | `borderPosition, fields, objectId, tableBorderProperties, tableRange` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateTableCellProperties` | `UpdateTableCellPropertiesRequest` | `fields, objectId, tableCellProperties, tableRange` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateTableColumnProperties` | `UpdateTableColumnPropertiesRequest` | `columnIndices, fields, objectId, tableColumnProperties` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateTableRowProperties` | `UpdateTableRowPropertiesRequest` | `fields, objectId, rowIndices, tableRowProperties` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |
| `updateTextStyle` | `UpdateTextStyleRequest` | `cellLocation, fields, objectId, style, textRange` | `empty reply` | explicitly mentioned in current MCP metadata or Slides MCP reference examples |
| `updateVideoProperties` | `UpdateVideoPropertiesRequest` | `fields, objectId, videoProperties` | `empty reply` | raw pass-through; not explicitly listed in current MCP docs/examples |

## Examples

### Read Deck

```ts
await tools["mcp__codex_apps__google_drive_get_presentation"]({
  presentation_url: "https://docs.google.com/presentation/d/PRESENTATION_ID/edit",
});
```

### Read Slide

```ts
await tools["mcp__codex_apps__google_drive_get_slide"]({
  presentation_id: "PRESENTATION_ID",
  slide_object_id: "s01_overview",
});
```

### Update Text

```ts
await tools["mcp__codex_apps__google_drive_batch_update_presentation"]({
  presentation_id: "PRESENTATION_ID",
  requests: [
    {
      deleteText: {
        objectId: "body_textbox_object_id",
        textRange: { type: "ALL" },
      },
    },
    {
      insertText: {
        objectId: "body_textbox_object_id",
        insertionIndex: 0,
        text: "Updated body copy",
      },
    },
  ],
});
```

### Update Table Border

```ts
await tools["mcp__codex_apps__google_drive_batch_update_presentation"]({
  presentation_id: "PRESENTATION_ID",
  requests: [
    {
      updateTableBorderProperties: {
        objectId: "table_object_id",
        borderPosition: "OUTER",
        tableBorderProperties: {
          tableBorderFill: {
            solidFill: {
              color: {
                rgbColor: { red: 0.1, green: 0.2, blue: 0.3 },
              },
            },
          },
          weight: { magnitude: 2, unit: "PT" },
        },
        fields: "tableBorderFill.solidFill.color,weight",
      },
    },
  ],
});
```

### Insert Image With `image_uris`

```ts
await tools["mcp__codex_apps__google_drive_batch_update_presentation"]({
  presentation_id: "PRESENTATION_ID",
  requests: [
    {
      createImage: {
        objectId: "image_01",
        url: "/tmp/generated-image.png",
        elementProperties: {
          pageObjectId: "s01_overview",
          size: {
            width: { magnitude: 240, unit: "PT" },
            height: { magnitude: 160, unit: "PT" },
          },
          transform: {
            scaleX: 1,
            scaleY: 1,
            translateX: 1000000,
            translateY: 1000000,
            unit: "EMU",
          },
        },
      },
    },
  ],
  image_uris: "/tmp/generated-image.png",
});
```

Official Slides REST requires image URLs to be public and has no `image_uris` field. `image_uris` is connector-only.

### Invalid Anti-Example: Stringified Request

```ts
await tools["mcp__codex_apps__google_drive_batch_update_presentation"]({
  presentation_id: "PRESENTATION_ID",
  requests: [
    JSON.stringify({
      deleteObject: { objectId: "shape_id" },
    }),
  ],
});
```

Invalid because `requests` must contain structured objects, not stringified JSON.

## Model Use Rules

- Read before write. Use `_get_presentation`, `_get_presentation_outline`, `_get_slide`, or `_get_presentation_tables` depending on the task.
- Use live object IDs from connector reads. Do not invent existing object IDs.
- For new object IDs, use valid Slides IDs: 5-50 characters, start with alphanumeric or underscore, then alphanumeric, underscore, hyphen, or colon.
- Each batch request object gets one top-level request key.
- Do not string-encode request objects.
- Keep wrapper fields snake_case and inner request fields camelCase.
- Keep slide/table geometry inside the page unless intentionally full-bleed.
- Do not infer unsupported just because a request key lacks an MCP example; unlisted official request types are intended to pass through as raw request objects.
- Treat API success as insufficient for visible slide edits. Re-read connector state and use thumbnails when visual layout matters.
- Use `_update_file` only for Drive metadata or parent-folder changes. Use `_batch_update_presentation` for slide content changes.

## What This Reference Is Not

- Not a replacement for the official Google Slides discovery document.
- Not a complete Drive MCP catalog.
- Not proof that every raw request was runtime-tested through the connector.
- Not a new skill or plugin; it is a reference inside the Google Slides skill.
