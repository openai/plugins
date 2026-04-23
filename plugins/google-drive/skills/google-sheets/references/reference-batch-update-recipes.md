# Batch Update Recipes

Use these patterns as copy-and-fill templates. The goal is request-shape recall, not a second copy of the Sheets docs.

## Rules

- Each request object must set exactly one request type key.
- Use exact Google field names and structured objects instead of stringified JSON.
- Prefer `sheetId` from `get_spreadsheet_metadata` when building `GridRange`, `GridCoordinate`, or `DimensionRange`.
- For `GridRange`, row and column indexes are zero-based, start-inclusive, and end-exclusive.
- For update-style requests, set a precise `fields` mask. Do not include the root object name in the mask.
- Keep batches logically clustered. Group edits that should succeed or fail together, but do not mix unrelated table rewrites, formatting passes, and structure changes into one mega-batch.

## Coordinate Templates

Use these shapes repeatedly:

```json
{
  "sheetId": 123456789,
  "startRowIndex": 0,
  "endRowIndex": 10,
  "startColumnIndex": 0,
  "endColumnIndex": 4
}
```

`GridRange` for rectangular regions.

```json
{
  "sheetId": 123456789,
  "rowIndex": 0,
  "columnIndex": 0
}
```

`GridCoordinate` for a single starting cell.

```json
{
  "sheetId": 123456789,
  "dimension": "ROWS",
  "startIndex": 1,
  "endIndex": 4
}
```

`DimensionRange` for whole rows or columns.

## High-Signal Request Families

Reach for these first:

- Content and formulas: `updateCells`, `appendCells`, `repeatCell`, `copyPaste`, `autoFill`
- Row and column layout: `insertDimension`, `deleteDimension`, `moveDimension`, `updateDimensionProperties`, `autoResizeDimensions`
- Table operations: `sortRange`, `setBasicFilter`, `clearBasicFilter`, `deleteDuplicates`, `trimWhitespace`
- Validation and protection: `setDataValidation`, `addProtectedRange`, `updateProtectedRange`, `deleteProtectedRange`
- Sheet structure: `addSheet`, `deleteSheet`, `duplicateSheet`, `updateSheetProperties`

For the full request catalog, use the official reference linked below.

## Write A Fixed Block Of Values Or Formulas

Use `updateCells` for a known rectangle. This is the most common raw write recipe.

```json
[
  {
    "updateCells": {
      "range": {
        "sheetId": 123456789,
        "startRowIndex": 0,
        "endRowIndex": 2,
        "startColumnIndex": 0,
        "endColumnIndex": 2
      },
      "rows": [
        {
          "values": [
            { "userEnteredValue": { "stringValue": "Owner" } },
            { "userEnteredValue": { "stringValue": "Status" } }
          ]
        },
        {
          "values": [
            { "userEnteredValue": { "stringValue": "Alex" } },
            { "userEnteredValue": { "formulaValue": "=IF(B1=\"\",\"Missing\",\"Ready\")" } }
          ]
        }
      ],
      "fields": "userEnteredValue"
    }
  }
]
```

## Format A Header Row And Freeze It

Use `repeatCell` for shared formatting across a range, then `updateSheetProperties` for sheet-level behavior.

```json
[
  {
    "repeatCell": {
      "range": {
        "sheetId": 123456789,
        "startRowIndex": 0,
        "endRowIndex": 1
      },
      "cell": {
        "userEnteredFormat": {
          "backgroundColorStyle": {
            "rgbColor": {
              "red": 0.12,
              "green": 0.47,
              "blue": 0.71
            }
          },
          "textFormat": {
            "bold": true,
            "foregroundColorStyle": {
              "rgbColor": {
                "red": 1,
                "green": 1,
                "blue": 1
              }
            }
          }
        }
      },
      "fields": "userEnteredFormat(backgroundColorStyle,textFormat)"
    }
  },
  {
    "updateSheetProperties": {
      "properties": {
        "sheetId": 123456789,
        "gridProperties": {
          "frozenRowCount": 1
        }
      },
      "fields": "gridProperties.frozenRowCount"
    }
  }
]
```

## Append New Rows

Use `appendCells` when the user wants to add new rows after the existing data.

```json
[
  {
    "appendCells": {
      "sheetId": 123456789,
      "rows": [
        {
          "values": [
            { "userEnteredValue": { "stringValue": "2026-03-13" } },
            { "userEnteredValue": { "numberValue": 42 } },
            { "userEnteredValue": { "stringValue": "complete" } }
          ]
        }
      ],
      "fields": "userEnteredValue"
    }
  }
]
```

## Resize Or Delete Rows Or Columns

Use `updateDimensionProperties` for size changes and `deleteDimension` for destructive row or column removal.

```json
[
  {
    "updateDimensionProperties": {
      "range": {
        "sheetId": 123456789,
        "dimension": "COLUMNS",
        "startIndex": 0,
        "endIndex": 3
      },
      "properties": {
        "pixelSize": 180
      },
      "fields": "pixelSize"
    }
  },
  {
    "deleteDimension": {
      "range": {
        "sheetId": 123456789,
        "dimension": "ROWS",
        "startIndex": 10,
        "endIndex": 12
      }
    }
  }
]
```

## Sort A Table And Turn On A Basic Filter

Use this for spreadsheet workflows that should behave like a table view instead of manual row shuffling.

```json
[
  {
    "sortRange": {
      "range": {
        "sheetId": 123456789,
        "startRowIndex": 1,
        "startColumnIndex": 0,
        "endColumnIndex": 5
      },
      "sortSpecs": [
        {
          "dimensionIndex": 2,
          "sortOrder": "ASCENDING"
        }
      ]
    }
  },
  {
    "setBasicFilter": {
      "filter": {
        "range": {
          "sheetId": 123456789,
          "startRowIndex": 0,
          "startColumnIndex": 0,
          "endColumnIndex": 5
        }
      }
    }
  }
]
```

## Add Dropdown Validation

Use `setDataValidation` for restricted inputs, including status dropdowns.

```json
[
  {
    "setDataValidation": {
      "range": {
        "sheetId": 123456789,
        "startRowIndex": 1,
        "endRowIndex": 200,
        "startColumnIndex": 3,
        "endColumnIndex": 4
      },
      "rule": {
        "condition": {
          "type": "ONE_OF_LIST",
          "values": [
            { "userEnteredValue": "todo" },
            { "userEnteredValue": "in_progress" },
            { "userEnteredValue": "done" }
          ]
        },
        "strict": true,
        "showCustomUi": true
      }
    }
  }
]
```

## Common Failure Modes

- Confusing `spreadsheets.batchUpdate` with `spreadsheets.values.batchUpdate`
- Stringifying the `requests` array instead of sending structured objects
- Using A1 notation where the request expects `GridRange` or `DimensionRange`
- Forgetting that indexes are zero-based and end-exclusive
- Omitting `fields` on update-style requests
- Filling validated cells from plain range reads and missing the dropdown's actual allowed values
- Mixing too many unrelated operations into one batch

## Official References

- Request catalog: https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/request
- Sheets API samples index: https://developers.google.com/workspace/sheets/api/samples
- Basic writing samples: https://developers.google.com/workspace/sheets/api/samples/writing
- Basic formatting samples: https://developers.google.com/workspace/sheets/api/samples/formatting
- Row and column samples: https://developers.google.com/workspace/sheets/api/samples/rowcolumn
- Sheet operations samples: https://developers.google.com/workspace/sheets/api/samples/sheet
