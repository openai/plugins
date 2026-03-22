# Batch Update Recipes

Use these patterns as copy-and-fill templates. Do not invent raw `batch_update` objects from scratch when one of these fits.

## Rules

- Each request object must set exactly one request type key.
- Use live `objectId` values from `get_slide`.
- Keep batches small.
- Re-fetch a thumbnail after every batch.
- Prefer exact field masks. Do not use guessed field names.

## Duplicate a strong slide

```json
[
  {
    "duplicateObject": {
      "objectId": "slide-strong-1"
    }
  }
]
```

Use this when one sibling slide already has the right structure and you want to clone that pattern.

## Delete a stale element

```json
[
  {
    "deleteObject": {
      "objectId": "shape-stale-1"
    }
  }
]
```

Use this before adding new structure if the old element is clearly redundant or overlapping.

## Replace repeated placeholder text everywhere

```json
[
  {
    "replaceAllText": {
      "containsText": {
        "text": "{{TITLE}}",
        "matchCase": true
      },
      "replaceText": "Q2 Business Review"
    }
  }
]
```

Use this for deterministic placeholder replacement. Do not use it when only one specific object should change.

## Clear and rewrite a single text box

```json
[
  {
    "deleteText": {
      "objectId": "shape-body-1",
      "textRange": {
        "type": "ALL"
      }
    }
  },
  {
    "insertText": {
      "objectId": "shape-body-1",
      "insertionIndex": 0,
      "text": "Updated body copy"
    }
  }
]
```

Use this when a specific text box should be preserved structurally but its content must reset.

## Move or scale an existing element

```json
[
  {
    "updatePageElementTransform": {
      "objectId": "shape-hero-1",
      "applyMode": "ABSOLUTE",
      "transform": {
        "scaleX": 1,
        "scaleY": 1,
        "translateX": 720000,
        "translateY": 1080000,
        "unit": "EMU",
        "shearX": 0,
        "shearY": 0
      }
    }
  }
]
```

Use this for geometry adjustments when the object already exists and only its position or scale is wrong.

## Create a new rectangle placeholder

```json
[
  {
    "createShape": {
      "objectId": "shape-new-placeholder-1",
      "shapeType": "TEXT_BOX",
      "elementProperties": {
        "pageObjectId": "slide-1",
        "size": {
          "width": {
            "magnitude": 4000000,
            "unit": "EMU"
          },
          "height": {
            "magnitude": 900000,
            "unit": "EMU"
          }
        },
        "transform": {
          "scaleX": 1,
          "scaleY": 1,
          "translateX": 900000,
          "translateY": 700000,
          "unit": "EMU",
          "shearX": 0,
          "shearY": 0
        }
      }
    }
  }
]
```

Use this when rebuilding a content zone is simpler than repairing a broken element.

## Insert text into a newly created text box

```json
[
  {
    "insertText": {
      "objectId": "shape-new-placeholder-1",
      "insertionIndex": 0,
      "text": "Section overview"
    }
  }
]
```

Use this immediately after `createShape` for text boxes.

## Common Failure Modes

- Wrong request key count: one object containing both `insertText` and `deleteObject`
- Guessed IDs instead of IDs from `get_slide`
- Stringified JSON instead of structured objects
- Giant batches mixing duplication, deletion, movement, and copy changes all at once
- Verifying only the API response and not the next thumbnail
