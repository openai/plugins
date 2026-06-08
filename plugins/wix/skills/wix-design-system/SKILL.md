---
name: wix-design-system
description: Wix Design System component reference. Use when building UI with @wix/design-system, choosing components, checking props and examples, or writing tests with component testkits. Triggers on "what component", "how do I make", "WDS", "show me props", "testkit", "driver", or component names like Button, Card, Modal, Box, Text.
---

# WDS Documentation Navigator

**Prerequisite:** `@wix/design-system` must be installed (`npm i @wix/design-system` or `yarn add @wix/design-system`).

## Helper Script

This skill bundles `scripts/wds.cjs` — a Node.js helper that auto-discovers `@wix/design-system` in node_modules (handles monorepos and workspaces) and provides focused lookups. Run it from the user's project directory using the absolute path to the bundled script:

```bash
# WDS is the absolute path to this skill's scripts/wds.cjs
WDS="<this-skill-dir>/scripts/wds.cjs"

node $WDS search <keyword>                 # Find components by keyword
node $WDS component <Name>                 # Get props + example list (one component)
node $WDS components <Name1> <Name2>...    # Same as `component`, but for several at once
node $WDS example <Name> "<ExampleName>"   # Get a specific example
node $WDS testkit <Name> [method]          # Get testkit imports + driver API
node $WDS icons <query>                    # Search for icons
```

## Workflow

### Step 1: Find the right component

```bash
node $WDS search table
node $WDS search form input validation
node $WDS search modal dialog popup
```

Multiple keywords are OR-matched. Returns component names, descriptions, and usage guidance.

### Step 2: Get props and available examples

```bash
node $WDS component Button
```

Returns the full props list (types and descriptions) plus a list of all available examples. For large prop files (>200 lines), returns a summary with prop names and types.

If you already know which several components you'll need (e.g. after Step 1 returned a shortlist), prefer the batch form to avoid one round-trip per component:

```bash
node $WDS components Button Card Table Input Text Thumbnail
```

Output is each component's props block separated by `---`. Missing components are logged to stderr and skipped; the command only fails if every requested component is missing.

### Step 3: Get a specific example

```bash
node $WDS example Button "Loading state"
```

Returns the example description and JSX code. Matching is case-insensitive and supports substrings (e.g., "loading" matches "Loading state").

### Step 4: Write tests with the component testkit

```bash
node $WDS testkit Button             # Imports + full driver API for Button
node $WDS testkit Button click       # Just the click() method details
```

Returns import snippets for unidriver, vanilla, puppeteer, and playwright flavors plus the driver method API (name, args, return type, description). Method name matching is case-insensitive substring.

### Step 5: Find icons

```bash
node $WDS icons Add Edit Delete
```

Icons are from `@wix/wix-ui-icons-common`. Each icon has a `Small` variant (e.g., `Add` + `AddSmall`).

## Fallback: Direct File Access

If the script is unavailable, docs are at `node_modules/@wix/design-system/dist/docs/`:

- `components.md` — component catalog (~978 lines, grep only)
- `components/{Name}Props.md` — props per component
- `components/{Name}Examples.md` — examples per component (grep `^### ` for section list)
- `components/{Name}Testkit.md` — testkit imports + driver API per component (grep `^### ` for method list)
- `testkits.md` — testkit catalog (list of components with generated testkit docs)
- `icons.md` — icon catalog (~818 lines, grep only)

Don't read these files fully. Grep for keywords, then read specific sections with offset/limit. See [references/file-structure.md](references/file-structure.md) for the exact docs file layout and section shapes.

---

## Quick Component Mapping (Design to WDS)

| Design Element | WDS Component | Notes |
| --- | --- | --- |
| Rectangle/container | `<Box>` | Layout wrapper |
| Text button | `<TextButton>` | Secondary actions |
| Input with label | `<FormField>` + `<Input>` | Wrap inputs |
| Toggle | `<ToggleSwitch>` | On/off settings |
| Modal | `<Modal>` + `<CustomModalLayout>` | Use together |
| Grid | `<Layout>` + `<Cell>` | Responsive |

## Spacing (px to SP conversion)

When designer specifies pixels, convert to the nearest SP token:

| Token | Classic | Studio |
| --- | --- | --- |
| `SP1` | 6px | 4px |
| `SP2` | 12px | 8px |
| `SP3` | 18px | 12px |
| `SP4` | 24px | 16px |
| `SP5` | 30px | 20px |
| `SP6` | 36px | 24px |

```tsx
<Box gap="SP2" padding="SP3">
```

Only use SP tokens for `gap`, `padding`, `margin` — not for width/height.

## Imports

```tsx
import { Button, Card, Image } from "@wix/design-system";
import { Add, Edit, Delete } from "@wix/wix-ui-icons-common";
```
