# Meeting Notes Direct Requests

When to read: for calendar-backed requests to add or update a Google Docs Meeting notes-like block in an existing Google Doc.

Use this as the complete operational reference for a normal request such as "add meeting notes for today's meeting from my calendar." If the task also needs tables, figures, citations, import/export, or non-meeting-notes content, read the matching task reference as well.

## Contents

- Target Connector Flow
- Style Rules
- What To Extract
- Index Rules
- Skeleton Pattern
- Verification Readback

## Target Connector Flow

1. Resolve relative dates explicitly in the local timezone.
2. Search Calendar once inside that date window with the broadest meeting-type term from the user request, such as `standup`, `sync`, `review`, or `1:1`, then filter returned events locally using the remaining project/title terms, attendees, and time window. Avoid starting with a combined narrow query made from every prompt keyword; if the broad query misses, use one fallback search with the exact title from the doc or prompt.
3. Read the selected Calendar event once and use the raw event payload for title, time, `htmlLink`, attendees, and declined status.
4. Read the destination with one full `mcp__codex_apps__google_drive._get_document`. Extract `documentId`, `revisionId`, `tabId`, insertion index, peer heading style, peer bullet style, and attendee-chip pattern.
5. Write the block with `mcp__codex_apps__google_drive._batch_update_document`, passing structured `requests` objects. Split only for API limits such as the 10 `insertPerson` cap.
6. Re-read with one connector read path that exposes the fields needed for verification. Avoid multiple adjacent paragraph-range reads; if verification depends on chips, list state, paragraph styles, or several nearby paragraphs, use one full `_get_document`. For table-only verification, use one `_get_document_tables`.
7. Do not export HTML or PDF for text-only meeting notes. Connector readback is the verification surface for chips, bullets, headings, and target identity.

## Style Rules

- Apply the meeting heading style only to the heading paragraph.
- Explicitly set attendee, blank separator, `Notes`, `Action items`, and bullet paragraphs to `NORMAL_TEXT` unless the peer block shows a different style.
- If no note content is available, insert one empty bullet paragraph under `Notes`, then one additional blank separator paragraph before `Action items`. Apply `BULLET_DISC_CIRCLE_SQUARE` only to the empty bullet paragraph.
- If no action-item content is available, insert one empty paragraph under `Action items`, apply `BULLET_CHECKBOX` to that paragraph, and leave one final blank paragraph after it. This matches the Google Docs UI Meeting notes block.
- If note/action content is available, create bullets only over the populated note/action paragraphs, never over labels or blank separators. Use checkboxes for action-item paragraphs when matching the UI Meeting notes block.
- For declined attendees, apply `strikethrough:true` only to the declined person-chip or text ranges.
- Add `strikethrough:false` to separator spaces and paragraph newlines adjacent to declined attendees so the style does not leak into the rest of the block.
- If a second attendee batch is needed, re-read the attendee paragraph first and insert before its newline using the live index.

## What To Extract

From the destination `_get_document` response, record compact working notes for:

- document id, URL, `revisionId`, and `tabId`
- insertion paragraph `startIndex` and `endIndex`
- peer heading `namedStyleType`, list/bullet state, and relevant paragraph/text style fields
- peer attendee element sequence and ranges, especially `textRun`, `dateElement`, `person`, and `richLink`
- existing nearby meeting-notes blocks for structure and duplicate checks

From the Calendar event, use the raw fields:

- start timestamp and timezone
- title
- `htmlLink` for the event link
- attendees with email, display name, and `responseStatus`

Do not reconstruct attendee lists from memory or summary output.

## Index Rules

- Google Docs indexes are UTF-16 code units.
- Newline is one code unit.
- `insertDate`, `insertPerson`, and `insertRichLink` each occupy one code unit after insertion.
- Requests in one batch execute in order, and later request indexes refer to the document after earlier requests in the same batch.
- Maintain a running index ledger for heading, attendees, labels, notes, and action items.

## Skeleton Pattern

This example demonstrates index movement for one attendee, an empty `Notes` bullet, one blank line before `Action items`, an empty action-item checkbox, and one final blank paragraph. Replace every placeholder with connector readback or Calendar event values before calling the connector. Recalculate indexes exactly from the chosen insertion index and actual attendee/note/action counts.

```json
{
  "document_id": "DOC_ID",
  "write_control": {
    "requiredRevisionId": "REVISION_ID_FROM_FRESH_READ"
  },
  "requests": [
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
    },
    {
      "insertText": {
        "location": {
          "index": 101,
          "tabId": "t.0"
        },
        "text": " | "
      }
    },
    {
      "insertRichLink": {
        "location": {
          "index": 104,
          "tabId": "t.0"
        },
        "richLinkProperties": {
          "uri": "EVENT_HTML_LINK"
        }
      }
    },
    {
      "insertText": {
        "location": {
          "index": 105,
          "tabId": "t.0"
        },
        "text": "\nAttendees: "
      }
    },
    {
      "insertPerson": {
        "location": {
          "index": 117,
          "tabId": "t.0"
        },
        "personProperties": {
          "email": "attendee@example.com"
        }
      }
    },
    {
      "insertText": {
        "location": {
          "index": 118,
          "tabId": "t.0"
        },
        "text": "\n\nNotes\n\n\nAction items\n\n\n"
      }
    },
    {
      "updateParagraphStyle": {
        "range": {
          "startIndex": 100,
          "endIndex": 106,
          "tabId": "t.0"
        },
        "paragraphStyle": {
          "namedStyleType": "HEADING_2"
        },
        "fields": "namedStyleType"
      }
    },
    {
      "updateParagraphStyle": {
        "range": {
          "startIndex": 106,
          "endIndex": 143,
          "tabId": "t.0"
        },
        "paragraphStyle": {
          "namedStyleType": "NORMAL_TEXT"
        },
        "fields": "namedStyleType"
      }
    },
    {
      "createParagraphBullets": {
        "range": {
          "startIndex": 126,
          "endIndex": 127,
          "tabId": "t.0"
        },
        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
      }
    },
    {
      "createParagraphBullets": {
        "range": {
          "startIndex": 141,
          "endIndex": 142,
          "tabId": "t.0"
        },
        "bulletPreset": "BULLET_CHECKBOX"
      }
    }
  ]
}
```

If there are more than 10 attendees with email chips, split the attendees across sequential `mcp__codex_apps__google_drive._batch_update_document` calls because `insertPerson` is limited per batch. If using revision-guarded writes, re-read and refresh `write_control.requiredRevisionId` between batches.

For declined attendees, insert the person chip or name, then apply:

```json
{
  "updateTextStyle": {
    "range": {
      "startIndex": 117,
      "endIndex": 118,
      "tabId": "t.0"
    },
    "textStyle": {
      "strikethrough": true
    },
    "fields": "strikethrough"
  }
}
```

For separator/newline ranges that touch declined attendee chips, explicitly clear leaked strikethrough:

```json
{
  "updateTextStyle": {
    "range": {
      "startIndex": 118,
      "endIndex": 119,
      "tabId": "t.0"
    },
    "textStyle": {
      "strikethrough": false
    },
    "fields": "strikethrough"
  }
}
```

## Verification Readback

After the write:

1. Re-read the edited area with one connector read path.
2. Confirm the expected `dateElement`, `person`, and `richLink` element types when chips were requested.
3. Confirm paragraph styles, links, and list state match the intended Meeting notes shape: one empty bullet under `Notes`, one blank line before `Action items`, one empty checkbox under `Action items`, and one final blank paragraph when no content was provided.
4. Confirm no leftover placeholder text, unintended extra empty bullets, or wrong-tab insertion exists.
5. If the connector response to `mcp__codex_apps__google_drive._batch_update_document` lacks `documentId`, `replies`, or `writeControl`, treat the write status as suspect and verify by readback before continuing.
