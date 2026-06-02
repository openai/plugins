---
name: figma-create-new-file
description: "**MANDATORY prerequisite** — you MUST invoke this skill BEFORE every `create_new_file` tool call. NEVER call `create_new_file` directly without loading this skill first. Trigger whenever the user wants a new blank Figma file — a new design, FigJam, or Slides file — or when you need a fresh file before calling `use_figma`. Usage — /figma-create-new-file [editorType] [fileName] (e.g. /figma-create-new-file figjam My Whiteboard, /figma-create-new-file slides Q3 Review)"
disable-model-invocation: false
---

# create_new_file — Create a New Figma File

**MANDATORY: load this skill before every `create_new_file` tool call.** It encodes the plan-resolution decision tree, the editor-type contract, and the post-creation handoff to `use_figma`.

Use the `create_new_file` MCP tool to create a new blank Figma file in the user's drafts folder. This is typically used before `use_figma` when you need a fresh file to work with.

## Skill Arguments

This skill accepts optional arguments: `/figma-create-new-file [editorType] [fileName]`

- **editorType**: `design` (default), `figjam`, or `slides`
- **fileName**: Name for the new file (defaults to "Untitled")

Examples:
- `/figma-create-new-file` — creates a design file named "Untitled"
- `/figma-create-new-file figjam My Whiteboard` — creates a FigJam file named "My Whiteboard"
- `/figma-create-new-file design My New Design` — creates a design file named "My New Design"
- `/figma-create-new-file slides Q3 Review` — creates a Slides presentation named "Q3 Review"

Parse the arguments from the skill invocation. If editorType is not provided, default to `"design"`. If fileName is not provided, default to `"Untitled"`.

## Workflow

### Step 1: Resolve the planKey

The `create_new_file` tool requires a `planKey` parameter. Follow this decision tree:

1. **User already provided a planKey** (e.g. from a previous `whoami` call or in their prompt) → use it directly, skip to Step 2.

2. **No planKey available** → call the `whoami` tool. The response contains a `plans` array. Each plan has a `key`, `name`, `seat`, and `tier`.

   - **Single plan**: use its `key` field automatically.
   - **Multiple plans**: ask the user which team or organization they want to create the file in, then use the corresponding plan's `key`.

### Step 2: Call create_new_file

Call the `create_new_file` tool with:

| Parameter    | Required | Description |
|-------------|----------|-------------|
| `planKey`   | Yes      | The plan key from Step 1 |
| `fileName`  | Yes      | Name for the new file |
| `editorType`| Yes      | `"design"`, `"figjam"`, or `"slides"` |

Example:
```json
{
  "planKey": "team:123456",
  "fileName": "My New Design",
  "editorType": "design"
}
```

### Step 3: Use the result

The tool returns:
- `file_key` — the key of the newly created file
- `file_url` — a direct URL to open the file in Figma

Use the `file_key` for subsequent tool calls like `use_figma`.

## Important Notes

- The file is created in the user's **drafts folder** for the selected plan.
- Supported editor types are `"design"`, `"figjam"`, and `"slides"`.
- If `use_figma` is your next step, load the `figma-use` skill before calling it.

## Editor-specific notes

### Slides — newly created files have an empty grid

A `slides` file produced by this tool starts with **zero rows and zero slides** — `figma.getSlideGrid()` returns `[]`, not a default first slide. The page's only child is the `SLIDE_GRID` node itself, which is empty until you create content. The first call to `figma.createSlide()` implicitly creates row 0 and inserts the new slide there.

If your follow-up `use_figma` script assumes at least one slide exists (e.g. to read theme tokens off it), guard for the empty case or call `createSlide()` first. See [figma-use-slides → slide-grid](../figma-use-slides/references/slide-grid.md) for full details.
