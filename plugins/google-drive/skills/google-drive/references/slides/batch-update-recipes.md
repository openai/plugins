# Batch Update Recipes

Use these patterns as copy-and-fill templates. Do not invent raw `batch_update` objects from scratch when one of these fits.

## Rules

- Each request object must set exactly one request type key.
- Use live `objectId` values from `get_slide`.
- Classify the target as a text box, shape, line or connector, or image before choosing a request family.
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

## Update a shape fill and border

```json
[
  {
    "updateShapeProperties": {
      "objectId": "shape-card-1",
      "shapeProperties": {
        "shapeBackgroundFill": {
          "solidFill": {
            "color": {
              "rgbColor": {
                "red": 0.92,
                "green": 0.97,
                "blue": 0.92
              }
            }
          }
        },
        "outline": {
          "outlineFill": {
            "solidFill": {
              "color": {
                "rgbColor": {
                  "red": 0.18,
                  "green": 0.62,
                  "blue": 0.25
                }
              }
            }
          },
          "weight": {
            "magnitude": 19050,
            "unit": "EMU"
          }
        }
      },
      "fields": "shapeBackgroundFill.solidFill.color,outline.outlineFill.solidFill.color,outline.weight"
    }
  }
]
```

Use this for accent bars, card fills, and border color or weight changes when the target is an existing shape.

## Update a line or connector stroke

```json
[
  {
    "updateLineProperties": {
      "objectId": "line-arrow-1",
      "lineProperties": {
        "lineFill": {
          "solidFill": {
            "color": {
              "rgbColor": {
                "red": 0.84,
                "green": 0.18,
                "blue": 0.16
              }
            }
          }
        },
        "weight": {
          "magnitude": 19050,
          "unit": "EMU"
        },
        "dashStyle": "SOLID",
        "endArrow": "FILL_ARROW"
      },
      "fields": "lineFill.solidFill.color,weight,dashStyle,endArrow"
    }
  }
]
```

Use this when the arrow or connector is a line object, not a filled shape.

## Restyle an existing arrow shape

```json
[
  {
    "updateShapeProperties": {
      "objectId": "shape-arrow-1",
      "shapeProperties": {
        "shapeBackgroundFill": {
          "solidFill": {
            "color": {
              "rgbColor": {
                "red": 0.20,
                "green": 0.62,
                "blue": 0.24
              }
            }
          }
        },
        "outline": {
          "propertyState": "NOT_RENDERED"
        }
      },
      "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState"
    }
  }
]
```

Use this when the arrow is a filled shape object and only its color or outline treatment should change.

## Delete and recreate a stale arrow or broken shape

```json
[
  {
    "deleteObject": {
      "objectId": "shape-arrow-old"
    }
  },
  {
    "createShape": {
      "objectId": "shape-arrow-new",
      "shapeType": "DOWN_ARROW",
      "elementProperties": {
        "pageObjectId": "slide-1",
        "size": {
          "width": {
            "magnitude": 260000,
            "unit": "EMU"
          },
          "height": {
            "magnitude": 260000,
            "unit": "EMU"
          }
        },
        "transform": {
          "scaleX": 1,
          "scaleY": 1,
          "translateX": 720000,
          "translateY": 1320000,
          "unit": "EMU",
          "shearX": 0,
          "shearY": 0
        }
      }
    }
  },
  {
    "updateShapeProperties": {
      "objectId": "shape-arrow-new",
      "shapeProperties": {
        "shapeBackgroundFill": {
          "solidFill": {
            "color": {
              "rgbColor": {
                "red": 0.84,
                "green": 0.18,
                "blue": 0.16
              }
            }
          }
        },
        "outline": {
          "propertyState": "NOT_RENDERED"
        }
      },
      "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState"
    }
  }
]
```

Use this when the existing arrow or decorative shape is the wrong type, badly malformed, or too brittle to patch safely in place.

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
- Updating the main headline value text and forgetting the smaller target or benchmark text box nearby
- Treating an arrow or accent bar as “uneditable” without first checking whether it is a shape or a line
- Using `updateShapeProperties` on a connector or `updateLineProperties` on a filled shape
- Stringified JSON instead of structured objects
- Giant batches mixing duplication, deletion, movement, and copy changes all at once
- Calling a visual edit complete because the text changed while the non-text styling stayed stale
- Verifying only the API response and not the next thumbnail
