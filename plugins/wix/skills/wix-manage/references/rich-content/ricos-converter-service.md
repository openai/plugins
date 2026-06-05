---
name: "Ricos Converter Service"
description: Validates and converts content between Ricos documents and HTML/Markdown/plain text using the Ricos Documents API. Covers plugin configuration, format conversion in both directions, and document validation.
---
# Rich Content (Ricos) Converter Service

This recipe covers how to validate and convert content between Ricos documents (Wix's rich content format) and other formats like HTML, Markdown, and plain text.

## Overview

Ricos is Wix's rich content format used across various Wix applications (Blog, Stores, etc.). The [Ricos Documents API](https://dev.wix.com/docs/api-reference/assets/rich-content/ricos-documents/introduction) provides:
- **Validation**: Check if a document conforms to the Ricos format
- **Convert to Ricos**: Transform HTML, Markdown, or plain text into a Ricos document
- **Convert from Ricos**: Transform a Ricos document back to HTML, Markdown, or plain text

Learn more about [Rich Content](https://dev.wix.com/docs/api-reference/articles/work-with-wix-apis/platform/about-rich-content) and [Ricos document structure](https://dev.wix.com/docs/ricos/getting-started/introduction).

## Required API Endpoints

| Method | Endpoint | Docs |
|--------|----------|------|
| Validate Document | `POST https://www.wixapis.com/ricos/v1/ricos-document/validate` | [Schema](https://dev.wix.com/docs/api-reference/assets/rich-content/ricos-documents/validate-document) |
| Convert To Ricos | `POST https://www.wixapis.com/ricos/v1/ricos-document/convert/to-ricos` | [Schema](https://dev.wix.com/docs/api-reference/assets/rich-content/ricos-documents/convert-to-ricos-document) |
| Convert From Ricos | `POST https://www.wixapis.com/ricos/v1/ricos-document/convert/from-ricos` | [Schema](https://dev.wix.com/docs/api-reference/assets/rich-content/ricos-documents/convert-from-ricos-document) |

---

## Available Plugins

Plugins determine which content types are recognized when validating or converting. Specify them as uppercase enum values:

| Plugin Enum | Description |
|-------------|-------------|
| `ACTION_BUTTON` | Call-to-action buttons |
| `AUDIO` | Audio content |
| `CODE_BLOCK` | Code snippets |
| `COLLAPSIBLE_LIST` | Expandable/collapsible lists |
| `DIVIDER` | Section dividers |
| `EMOJI` | Emoji support |
| `FILE` | File attachments |
| `FONT_FAMILY` | Font family selection |
| `GALLERY` | Image galleries |
| `GIPHY` | GIF integration |
| `HASHTAG` | Hashtag support |
| `HEADING` | Headings (h1-h6) |
| `HTML` | Raw HTML blocks |
| `IMAGE` | Images |
| `INDENT` | Text indentation |
| `LAYOUT` | Layout containers |
| `LINE_SPACING` | Line spacing control |
| `LINK` | Hyperlinks |
| `LINK_BUTTON` | Link buttons |
| `LINK_PREVIEW` | Link previews |
| `MENTIONS` | @mentions |
| `POLL` | Polls |
| `SPOILER` | Spoiler/hidden content |
| `TABLE` | Tables |
| `TEXT_COLOR` | Text color |
| `TEXT_HIGHLIGHT` | Text highlighting |
| `VERTICAL_EMBED` | Vertical embeds |
| `VIDEO` | Video content |

### IMPORTANT NOTES:
- Plugin values must be **UPPERCASE** enum strings (e.g., `"HEADING"`, not `"heading"`)
- Content using unsupported plugins will result in validation violations
- When converting HTML, only elements matching your plugins are converted

---

## Step 1: Validate a Ricos Document

Check if a document conforms to the Ricos format and optionally fix issues.

**Endpoint**: `POST https://www.wixapis.com/ricos/v1/ricos-document/validate` ([docs](https://dev.wix.com/docs/api-reference/assets/rich-content/ricos-documents/validate-document))

**Request Body**:
```json
{
  "document": {
    "nodes": [
      {
        "type": "PARAGRAPH",
        "id": "p1",
        "nodes": [
          {
            "type": "TEXT",
            "id": "t1",
            "textData": {
              "text": "Hello World",
              "decorations": []
            }
          }
        ],
        "paragraphData": {}
      }
    ]
  },
  "plugins": ["HEADING", "LINK", "IMAGE", "TEXT_COLOR"],
  "fixDocument": true
}
```

**Response**:
```json
{
  "valid": true,
  "violations": [],
  "validDocument": {
    "nodes": [
      {
        "type": "PARAGRAPH",
        "id": "p1",
        "nodes": [
          {
            "type": "TEXT",
            "id": "t1",
            "textData": {
              "text": "Hello World",
              "decorations": []
            }
          }
        ],
        "paragraphData": {}
      }
    ]
  }
}
```

---

## Step 2: Convert HTML to Ricos

Transform HTML content into Ricos document format.

**Endpoint**: `POST https://www.wixapis.com/ricos/v1/ricos-document/convert/to-ricos` ([docs](https://dev.wix.com/docs/api-reference/assets/rich-content/ricos-documents/convert-to-ricos-document))

**Request Body**:
```json
{
  "html": "<h1>Welcome</h1><p>This is a <strong>bold</strong> paragraph with a <a href=\"https://example.com\">link</a>.</p>",
  "options": {
    "plugins": ["HEADING", "LINK", "TEXT_COLOR", "TEXT_HIGHLIGHT"]
  }
}
```

**Response**:
```json
{
  "document": {
    "nodes": [
      {
        "type": "HEADING",
        "id": "",
        "headingData": { "level": 1 },
        "nodes": [
          { "type": "TEXT", "textData": { "text": "Welcome", "decorations": [] } }
        ]
      },
      {
        "type": "PARAGRAPH",
        "id": "",
        "nodes": [
          { "type": "TEXT", "textData": { "text": "This is a ", "decorations": [] } },
          { "type": "TEXT", "textData": { "text": "bold", "decorations": [{ "type": "BOLD", "fontWeightValue": 700 }] } },
          { "type": "TEXT", "textData": { "text": " paragraph with a ", "decorations": [] } },
          { "type": "TEXT", "textData": { "text": "link", "decorations": [{ "type": "LINK", "linkData": { "link": { "url": "https://example.com", "target": "SELF" } } }] } },
          { "type": "TEXT", "textData": { "text": ".", "decorations": [] } }
        ]
      }
    ],
    "metadata": { "version": 1 }
  }
}
```

---

## Step 3: Convert Markdown to Ricos

Uses the same endpoint as HTML conversion, with `markdown` instead of `html`.

**Request Body**:
```json
{
  "markdown": "# Welcome\n\nThis is a **bold** paragraph with a [link](https://example.com).",
  "options": {
    "plugins": ["HEADING", "LINK", "CODE_BLOCK"]
  }
}
```

---

## Step 4: Convert Plain Text to Ricos

**Request Body**:
```json
{
  "plainText": "This is plain text content.\n\nIt will be converted to paragraphs.",
  "options": {
    "plugins": []
  }
}
```

---

## Step 5: Convert Ricos to HTML / Markdown / Plain Text

Convert a Ricos document back to another format.

**Endpoint**: `POST https://www.wixapis.com/ricos/v1/ricos-document/convert/from-ricos` ([docs](https://dev.wix.com/docs/api-reference/assets/rich-content/ricos-documents/convert-from-ricos-document))

**Request Body (to HTML)**:
```json
{
  "document": {
    "nodes": [
      {
        "type": "HEADING",
        "id": "h1",
        "headingData": { "level": 1 },
        "nodes": [
          { "type": "TEXT", "id": "t1", "textData": { "text": "Welcome", "decorations": [] } }
        ]
      },
      {
        "type": "PARAGRAPH",
        "id": "p1",
        "nodes": [
          { "type": "TEXT", "id": "t2", "textData": { "text": "Hello world with ", "decorations": [] } },
          { "type": "TEXT", "id": "t3", "textData": { "text": "bold", "decorations": [{ "type": "BOLD", "fontWeightValue": 700 }] } }
        ],
        "paragraphData": {}
      }
    ]
  },
  "targetFormat": "HTML"
}
```

**Response**:
```json
{
  "html": "<h1>Welcome</h1><p>Hello world with <span style=\"font-weight: 700\">bold</span></p>"
}
```

**Target format options**: `"HTML"`, `"MARKDOWN"`, `"PLAIN_TEXT"`

For plain text, you can include optional settings:
```json
{
  "document": { "nodes": [...] },
  "targetFormat": "PLAIN_TEXT",
  "plainTextOptions": {
    "includeLinks": true,
    "includeMediaLinks": true
  }
}
```

---

## Common Use Cases

### Blog Post Content Import
When importing blog content from external sources:
1. Convert HTML/Markdown to Ricos format using Convert To Ricos
2. Validate the converted document with `fixDocument: true`
3. Use the validated document in the Blog Posts API

### Rich Content Validation Before Saving
Before saving rich content:
1. Validate with `fixDocument: true`
2. Use the returned `validDocument` for saving
3. Check `violations` array for any issues

### Round-Trip Conversion
Convert between formats for editing workflows:
1. Convert Ricos to Markdown for a Markdown editor
2. Convert edited Markdown back to Ricos for storage
3. See [Sample Flows](https://dev.wix.com/docs/api-reference/assets/rich-content/ricos-documents/sample-flows) for a detailed example

---

## Gotchas & Troubleshooting
- Maximum content length: 10,000 characters for HTML, Markdown, or plain text
- Plugin limits: Maximum 100 plugins per request
- Plugin name max length: 30 characters
- If converting HTML with images but `IMAGE` plugin not specified, images are silently dropped
- Always validate converted content before using in production
- The plain text `convert/from-ricos` response concatenates text without separators between nodes — use `includeLinks: true` in `plainTextOptions` if you need link URLs preserved
