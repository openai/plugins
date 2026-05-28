# Direct Request Composition

When to read: before writing non-meeting Google Docs connector `batchUpdate` requests directly, including content writes into connector-created basic docs.

## Contents

- Objective
- Calendar-Backed Meeting Notes
- Connector-Created Basic Docs
- What To Extract From `get_document`
- Index Rules
- Connector Call Shape
- Plain Section Insert
- Bullet Insert
- Supported Smart Chips
- Verification Readback

## Objective

Prepare `documents.batchUpdate` request objects directly from connector readback.

API basis:

- `documents.batchUpdate` takes a `requests[]` array plus optional `writeControl`; Google validates every request before applying the batch and applies valid batches atomically.
- A successful batch response includes `documentId`, `replies[]`, and `writeControl`.
- `Location` supports `index`, optional `segmentId`, and `tabId`; include `tabId` whenever the document has tabs.
- `insertText`, `insertDate`, and `insertRichLink` must insert inside an existing paragraph, not at a table start boundary.
- See the Google Docs API reference for current request shapes: https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate and https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request

Use this process:

1. Read the destination with the connector. If the destination was just created by `mcp__codex_apps__google_drive._create_file`, this read establishes the body index, `tabId`, and revision state before content writes.
2. Extract only the relevant structure into short working notes.
3. Build a small index ledger for the intended insertion or replacement.
4. Call `mcp__codex_apps__google_drive._batch_update_document` with structured `requests` objects.
5. Re-read the edited region and verify element types and styles.

## Calendar-Backed Meeting Notes

For calendar-backed Meeting notes blocks, read `reference-meeting-notes-direct.md` instead of this file. That reference owns the event lookup, Meeting notes shape, empty placeholders, attendee chips, declined-attendee styling, and fast verification rules.

## Connector-Created Basic Docs

For blank or basic new Google Docs, read `reference-native-create-direct.md` first. Use this file only when that new document needs content inserted with direct `batchUpdate` requests.

## What To Extract From `get_document`

For each target area, write down:

- document id, URL, `revisionId`, and `tabId`
- paragraph `startIndex` and `endIndex`
- paragraph `namedStyleType`, list/bullet state, and relevant paragraph style fields
- element sequence and ranges, especially `textRun`, `dateElement`, `person`, `richLink`, and inline objects
- table number, table start index, row/column count, cell ranges, and cell text when editing tables
- a nearby style anchor that already looks like the intended output

Use a compact local note format like:

```text
tab=t.0 rev=REV
p 100-113 HEADING_2: TEXT "Launch risks\n"
p 113-154 NORMAL_TEXT: TEXT "Risk one.\nRisk two.\n"
```

Those notes are for reasoning only; do not send them to the connector.

## Index Rules

- Google Docs indexes are UTF-16 code units.
- Newline is one code unit.
- `insertDate`, `insertPerson`, and `insertRichLink` each occupy one code unit after insertion.
- Requests in one batch execute in order, and later request indexes refer to the document after earlier requests in the same batch.
- For complicated insertions, maintain a running index ledger:

```text
I = insertion start
insertText "Status: " at I            -> next I + 8
insertDate at I+8                     -> next I + 9
insertText "\nOwner: " at I+9         -> next I + 17
insertPerson at I+17                  -> next I + 18
```

Prefer inserting a stable text skeleton first, then applying paragraph styles, bullets, links, and other formatting in the same batch. Reserve follow-up formatting batches for issues discovered by readback.

## Connector Call Shape

Use structured request objects:

```json
{
  "document_id": "DOC_ID",
  "write_control": {
    "requiredRevisionId": "REVISION_ID_FROM_FRESH_READ"
  },
  "requests": [
    {
      "insertText": {
        "location": {
          "index": 100,
          "tabId": "t.0"
        },
        "text": "New section\n"
      }
    }
  ]
}
```

Omit `write_control` only when the write intentionally applies to the latest revision. Never stringify `requests` or `write_control`.

Placeholder values in examples, such as `DOC_ID`, `EVENT_START_RFC3339`, and example email addresses, must be replaced with values from connector readback or source data before calling the connector.

## Plain Section Insert

To add a peer section at index `I`:

```json
[
  {
    "insertText": {
      "location": {
        "index": 100,
        "tabId": "t.0"
      },
      "text": "Launch risks\nRisk one.\nRisk two.\n"
    }
  },
  {
    "updateParagraphStyle": {
      "range": {
        "startIndex": 100,
        "endIndex": 113,
        "tabId": "t.0"
      },
      "paragraphStyle": {
        "namedStyleType": "HEADING_2"
      },
      "fields": "namedStyleType"
    }
  }
]
```

After inserting text, calculate style ranges from the inserted text length, not from guessed rendered layout. If the surrounding heading has explicit local text styling, add `updateTextStyle` for the heading range after matching the paragraph style.

## Bullet Insert

Insert plain lines first, then create bullets over the range that contains only the intended bullet paragraphs:

```json
[
  {
    "insertText": {
      "location": {
        "index": 200,
        "tabId": "t.0"
      },
      "text": "First bullet\nSecond bullet\n"
    }
  },
  {
    "createParagraphBullets": {
      "range": {
        "startIndex": 200,
        "endIndex": 227,
        "tabId": "t.0"
      },
      "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
    }
  }
]
```

If the peer template uses a specific existing list style, read the peer bullet paragraphs and match their visible list behavior as closely as the connector supports.

## Supported Smart Chips

Replace placeholder values such as `EVENT_START_RFC3339`, `DOC_ID`, and example email addresses with live source values before writing.

Date chip:

```json
{
  "insertDate": {
    "location": {
      "index": 100,
      "tabId": "t.0"
    },
    "dateElementProperties": {
      "timestamp": "EVENT_START_RFC3339",
      "locale": "en",
      "dateFormat": "DATE_FORMAT_MONTH_DAY_YEAR_ABBREVIATED",
      "timeFormat": "TIME_FORMAT_DISABLED"
    }
  }
}
```

Person chip:

```json
{
  "insertPerson": {
    "location": {
      "index": 101,
      "tabId": "t.0"
    },
    "personProperties": {
      "email": "person@example.com"
    }
  }
}
```

Rich link:

```json
{
  "insertRichLink": {
    "location": {
      "index": 102,
      "tabId": "t.0"
    },
    "richLinkProperties": {
      "uri": "https://docs.google.com/document/d/DOC_ID/edit"
    }
  }
}
```

For date chips, omit output-only `displayText`. Include `timeZoneId` only when the selected `timeFormat` requires a timezone display.

## Verification Readback

After a write:

1. Re-read the edited area with one connector read path that exposes the fields needed for verification.
2. Confirm the response contains the expected `dateElement`, `person`, and `richLink` element types when chips were requested.
3. Confirm paragraph styles, links, list state, tables, and images match the intended shape where relevant.
4. Confirm no leftover placeholder text, unintended empty bullets, duplicate sections, or wrong-tab insertion exists.
5. If the connector response to `mcp__codex_apps__google_drive._batch_update_document` lacks `documentId`, `replies`, or `writeControl`, treat the write status as suspect and verify by readback before continuing.
