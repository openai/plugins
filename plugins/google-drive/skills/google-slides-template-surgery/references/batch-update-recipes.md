# Batch Update Recipes

Use these patterns as copy-and-fill templates. Do not invent raw `batch_update` objects from scratch when one of these fits.

## Rules

- Each request object must set exactly one request type key.
- Use live `objectId` values from `get_slide`.
- Classify the target as a text box, shape, line or connector, or image before choosing a request family.
- Remember that Slides `translateX` and `translateY` place the element's upper-left corner, not its center.
- When centering a new element relative to another object, compute the target top-left from the desired visual center and the new element's rendered width and height.
- Keep batches small.
- Re-fetch a thumbnail after every batch.
- If the batch changed visible layout or styling, continue through [visual-change-loop](./visual-change-loop.md) and do not stop before the third fresh review.
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

## Few-shot: normalize a repeated card family against a polished target

Use this pattern when you have:
- a stale slide that is structurally close but visually loose, and
- a stronger manually polished target slide that shows the intended row spacing, text hierarchy, and primitive sizes.

Representative stale-to-polished delta from a dashboard card:
- stale card: label, value, target, arrow, delta, and accent bar exist, but their baselines drift and same-state primitives are not normalized
- polished card: label is smaller than the value, target is lighter and smaller than the value, delta color matches the arrow and accent bar, and the bar and arrow use the same size treatment as sibling cards

Common middle state after pass 1:
- the stale slide is better because colors and core objects are now present, but the repeated family still looks rough
- same-role primitives are present but not normalized, such as uneven bar heights, drifting arrow scales, or delta rows that sit on slightly different baselines
- hierarchy is improved, but the slide still needs a second pass to align sibling cards into one system rather than a set of individually readable fixes

Treat that middle state as contrast, not as a recipe to copy. Use it to decide what pass 2 must clean up before the slide is presentation-ready.

```json
[
  {
    "updatePageElementTransform": {
      "objectId": "card-1-bar",
      "applyMode": "ABSOLUTE",
      "transform": {
        "scaleX": 0.0467,
        "scaleY": 0.537,
        "translateX": 300000,
        "translateY": 951500,
        "unit": "EMU",
        "shearX": 0,
        "shearY": 0
      }
    }
  },
  {
    "updateShapeProperties": {
      "objectId": "card-1-bar",
      "shapeProperties": {
        "shapeBackgroundFill": {
          "solidFill": {
            "color": {
              "rgbColor": {
                "red": 0.20392157,
                "green": 0.65882355,
                "blue": 0.3254902
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
  },
  {
    "updateTextStyle": {
      "objectId": "card-1-label",
      "textRange": {
        "type": "ALL"
      },
      "style": {
        "fontSize": {
          "magnitude": 16,
          "unit": "PT"
        }
      },
      "fields": "fontSize"
    }
  },
  {
    "updatePageElementTransform": {
      "objectId": "card-1-label",
      "applyMode": "ABSOLUTE",
      "transform": {
        "scaleX": 0.5333,
        "scaleY": 0.1117,
        "translateX": 470050,
        "translateY": 943350,
        "unit": "EMU",
        "shearX": 0,
        "shearY": 0
      }
    }
  },
  {
    "updateTextStyle": {
      "objectId": "card-1-value",
      "textRange": {
        "type": "ALL"
      },
      "style": {
        "fontSize": {
          "magnitude": 24,
          "unit": "PT"
        },
        "bold": true
      },
      "fields": "fontSize,bold"
    }
  },
  {
    "updatePageElementTransform": {
      "objectId": "card-1-value",
      "applyMode": "ABSOLUTE",
      "transform": {
        "scaleX": 0.5,
        "scaleY": 0.1333,
        "translateX": 520000,
        "translateY": 1200100,
        "unit": "EMU",
        "shearX": 0,
        "shearY": 0
      }
    }
  },
  {
    "updateTextStyle": {
      "objectId": "card-1-target",
      "textRange": {
        "type": "ALL"
      },
      "style": {
        "fontSize": {
          "magnitude": 12,
          "unit": "PT"
        },
        "foregroundColor": {
          "opaqueColor": {
            "rgbColor": {
              "red": 0.47058824,
              "green": 0.5019608,
              "blue": 0.54901963
            }
          }
        }
      },
      "fields": "fontSize,foregroundColor"
    }
  },
  {
    "updatePageElementTransform": {
      "objectId": "card-1-target",
      "applyMode": "ABSOLUTE",
      "transform": {
        "scaleX": 0.5,
        "scaleY": 0.06,
        "translateX": 520000,
        "translateY": 1629950,
        "unit": "EMU",
        "shearX": 0,
        "shearY": 0
      }
    }
  },
  {
    "updatePageElementTransform": {
      "objectId": "card-1-arrow",
      "applyMode": "ABSOLUTE",
      "transform": {
        "scaleX": 0.0867,
        "scaleY": 0.0867,
        "translateX": 520000,
        "translateY": 2199950,
        "unit": "EMU",
        "shearX": 0,
        "shearY": 0
      }
    }
  },
  {
    "updateShapeProperties": {
      "objectId": "card-1-arrow",
      "shapeProperties": {
        "shapeBackgroundFill": {
          "solidFill": {
            "color": {
              "rgbColor": {
                "red": 0.20392157,
                "green": 0.65882355,
                "blue": 0.3254902
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
  },
  {
    "updateTextStyle": {
      "objectId": "card-1-delta",
      "textRange": {
        "type": "ALL"
      },
      "style": {
        "fontSize": {
          "magnitude": 14,
          "unit": "PT"
        },
        "bold": true,
        "foregroundColor": {
          "opaqueColor": {
            "rgbColor": {
              "red": 0.20392157,
              "green": 0.65882355,
              "blue": 0.3254902
            }
          }
        }
      },
      "fields": "fontSize,bold,foregroundColor"
    }
  },
  {
    "updatePageElementTransform": {
      "objectId": "card-1-delta",
      "applyMode": "ABSOLUTE",
      "transform": {
        "scaleX": 0.3667,
        "scaleY": 0.1117,
        "translateX": 780100,
        "translateY": 2161450,
        "unit": "EMU",
        "shearX": 0,
        "shearY": 0
      }
    }
  }
]
```

Use this as a geometry-and-style template, not as a one-card-only fix.

- Apply the same primitive sizes across sibling cards in the same family:
  - accent bars should share one width treatment
  - arrows should share one scale treatment
  - labels, primary values, targets, and deltas should share a consistent type hierarchy
- Apply one state palette across the whole row or deck slice. If the source says `GREEN`, do not let some same-state bars, arrows, or delta labels drift to slightly different greens.
- Normalize both geometry and style. A card is still stale if the numbers updated but the bar height, arrow scale, or label baseline differs from its siblings.
- If a polished target slide exists, use its transforms as the alignment source of truth instead of eyeballing each card independently.

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

## Create a tight single-line label

```json
[
  {
    "createShape": {
      "objectId": "shape-small-label-1",
      "shapeType": "TEXT_BOX",
      "elementProperties": {
        "pageObjectId": "slide-1",
        "size": {
          "width": {
            "magnitude": 1400000,
            "unit": "EMU"
          },
          "height": {
            "magnitude": 320000,
            "unit": "EMU"
          }
        },
        "transform": {
          "scaleX": 1,
          "scaleY": 1,
          "translateX": 1320000,
          "translateY": 2260000,
          "unit": "EMU",
          "shearX": 0,
          "shearY": 0
        }
      }
    }
  },
  {
    "insertText": {
      "objectId": "shape-small-label-1",
      "insertionIndex": 0,
      "text": "110%"
    }
  },
  {
    "updateTextStyle": {
      "objectId": "shape-small-label-1",
      "textRange": {
        "type": "ALL"
      },
      "style": {
        "fontSize": {
          "magnitude": 12,
          "unit": "PT"
        }
      },
      "fields": "fontSize"
    }
  }
]
```

Use this for a small benchmark, caption, or one-line helper label.

- Keep the text box footprint tight to the intended label. Do not reuse a tall placeholder box for a short single-line value.
- The `translateX` and `translateY` values above are top-left coordinates, not the label's center point.
- If the desired visual center is `C`, compute the top-left as `C - (width / 2, height / 2)` before sending the request.
- If the next thumbnail shows the text sitting visibly low or off-center, tighten the text-box height or nudge the top-left in a second pass. Treat that as a geometry miss, not a reason to stop.
- If this label lives next to another text box, verify both boxes together after the write. Do not treat a local text update as successful if the new label now crowds or overlaps its neighbor.
- Use both checks after the write: inspect the thumbnail for rendered collisions and re-read the slide structure for text-box geometry. If those signals disagree, err on the side of caution and keep treating the label placement as unfinished.

## Common Failure Modes

- Wrong request key count: one object containing both `insertText` and `deleteObject`
- Guessed IDs instead of IDs from `get_slide`
- Updating the main headline value text and forgetting the smaller target or benchmark text box nearby
- Treating an arrow or accent bar as “uneditable” without first checking whether it is a shape or a line
- Using `updateShapeProperties` on a connector or `updateLineProperties` on a filled shape
- Assuming `translateX` and `translateY` target the element center instead of the upper-left corner
- Creating a large or tall text box for a tiny one-line label, then leaving the label visually low inside the box
- Fixing one text box while leaving its adjacent text box colliding, overlapping, or starved for padding
- Trusting the thumbnail alone when refreshed slide geometry still suggests risky overflow or neighboring text-box collisions
- Updating one repeated card or primitive in isolation and leaving sibling cards with mismatched bar heights, arrow scales, or text baselines
- Letting same-state colors drift so one "green" bar, arrow, or delta label does not match the others
- Stringified JSON instead of structured objects
- Giant batches mixing duplication, deletion, movement, and copy changes all at once
- Calling a visual edit complete because the text changed while the non-text styling stayed stale
- Verifying only the API response and not the next thumbnail
