> Part of the [figma-generate-library skill](../SKILL.md).

# Error Recovery Reference

Protocol for handling failures and incomplete runs across a 20–100+ call design system build.

> **Design files only.** Every snippet here (including `figma.createPage()`) targets Figma Design files (`figma.com/design/...`). `figma.createPage()` throws in both FigJam (`figma.com/board/...`) and Slides (`figma.com/slides/...`).

---

## 1. Core Protocol: STOP → Inspect → Fix → Retry

**`use_figma` is atomic — a failed script does not execute.** If a script errors, no changes are made to the file. There are no partial nodes or half-built state from the failed call itself. Retrying after a fix is safe.

However, in multi-step workflows (20–100+ calls), **previously successful calls** will have created state that persists. If a workflow is abandoned mid-way, nodes from earlier successful calls remain in the file. The cleanup and idempotency patterns in this document handle that scenario.

The recovery sequence for a failed script:

```
1. STOP    — Do not run any more use_figma writes.
2. INSPECT — Read the error message carefully. Optionally call get_metadata or get_screenshot to understand the current file state.
3. FIX     — Correct the script that failed.
4. RETRY   — Re-run the corrected script.
5. PERSIST — Update the state ledger with the outcome.
```

For **abandoned multi-step workflows** (where you need to roll back nodes from previous *successful* calls), use the cleanup protocol in Section 2.

---

## 2. ID-Based Cleanup

### Why name-prefix matching fails

A cleanup script that deletes "all nodes whose name starts with `Button`" will also delete nodes the user may have created manually with that name, or nodes from a previous approved phase. Name-based cleanup has no way to distinguish "orphan from a failed attempt" from "intentional user node."

Furthermore, variant names (`Size=Medium, Style=Primary, State=Default`) do not have consistent prefixes that are safe to target without also hitting legitimate nodes. Record every created ID in the state ledger as soon as its creation call succeeds.

### Cleanup using exact state-ledger IDs

Read the exact IDs from the state ledger, embed `scripts/cleanupOrphans.js`, and pass only those IDs:

```javascript
return await cleanupOrphans({
  nodeIds: ['1:23', '1:47'],
  variableIds: ['VariableID:1:8'],
  collectionIds: ['VariableCollectionId:1:4'],
});
```

After cleanup, inspect the affected page and compare `removedIds` / `skippedIds` with the state ledger before retrying.

---

## 3. Idempotency Patterns: Check-Before-Create

Run an idempotency check at the start of every create operation. Resolve an ID from the state ledger first. If the ledger is unavailable, use a deterministic name scoped to the expected page, collection, and node type, then return the recovered ID.

### Check-before-create for a variable collection

```javascript
const COLLECTION_NAME = 'Color';

const allCollections = await figma.variables.getLocalVariableCollectionsAsync();
const existing = allCollections.find(c => c.name === COLLECTION_NAME);

if (existing) {
  return {
    collectionId: existing.id,
    modeIds: existing.modes.map(m => ({ name: m.name, id: m.modeId })),
    alreadyExisted: true,
  };
}

// Create fresh
const collection = figma.variables.createVariableCollection(COLLECTION_NAME);

// Rename default mode, add second mode
collection.renameMode(collection.modes[0].modeId, 'Light');
const darkModeId = collection.addMode('Dark');

return {
  collectionId: collection.id,
  modeIds: [
    { name: 'Light', id: collection.modes[0].modeId },
    { name: 'Dark',  id: darkModeId },
  ],
};
```

### Check-before-create for a page

```javascript
const PAGE_NAME = 'Button';

let page = figma.root.children.find(p => p.name === PAGE_NAME);

if (page) {
  return { pageId: page.id, alreadyExisted: true };
}

page = figma.createPage();
page.name = PAGE_NAME;

return { pageId: page.id, alreadyExisted: false };
```

### Check-before-create for a component set

```javascript
const PAGE_ID = 'PAGE_ID_FROM_STATE';

const page = await figma.getNodeByIdAsync(PAGE_ID);
await figma.setCurrentPageAsync(page);

const existing = page.findAllWithCriteria({ types: ['COMPONENT_SET'] })
  .filter(n => n.name === 'Button');

if (existing.length > 0) {
  return {
    componentSetId: existing[0].id,
    alreadyExisted: true,
  };
}

// ... proceed with creation
return { componentSetId: null, alreadyExisted: false };
```

---

## 4. State Ledger

### JSON Schema

Maintain a state ledger in your context (not in the Figma file) across calls. This is your source of truth for node IDs, completed steps, and pending validations.

```json
{
  "runId": "ds-build-2024-001",
  "phase": "phase3",
  "step": "component-button/combine-variants",
  "completedSteps": [
    "phase0",
    "phase1/collections",
    "phase1/primitives",
    "phase1/semantics",
    "phase2/pages",
    "phase2/foundations-docs",
    "phase3/component-avatar",
    "phase3/component-icon"
  ],
  "entities": {
    "collections": {
      "primitives": "VariableCollectionId:1234:5678",
      "color":      "VariableCollectionId:1234:5679",
      "spacing":    "VariableCollectionId:1234:5680"
    },
    "variables": {
      "color/bg/primary":         "VariableId:2345:1",
      "color/bg/secondary":       "VariableId:2345:2",
      "color/bg/disabled":        "VariableId:2345:3",
      "color/text/on-primary":    "VariableId:2345:4",
      "color/text/on-secondary":  "VariableId:2345:5",
      "color/text/disabled":      "VariableId:2345:6",
      "spacing/sm":               "VariableId:2345:7",
      "spacing/md":               "VariableId:2345:8",
      "spacing/lg":               "VariableId:2345:9",
      "radius/md":                "VariableId:2345:10"
    },
    "modes": {
      "color/light": "2345:1",
      "color/dark":  "2345:2"
    },
    "pages": {
      "Cover":       "0:1",
      "Foundations": "0:2",
      "Button":      "0:3"
    },
    "components": {
      "Icon":        "3456:1",
      "Avatar":      "3456:2",
      "Button":      "3456:3"
    },
    "componentSets": {
      "Button": "4567:1"
    }
  },
  "pendingValidations": [
    "Button:metadata",
    "Button:screenshot"
  ],
  "userCheckpoints": {
    "phase0": "approved-2024-01-15",
    "phase1": "approved-2024-01-15",
    "phase2": "approved-2024-01-15",
    "component-avatar": "approved-2024-01-15"
  }
}
```

### Persisting between calls

After every successful `use_figma` call:
1. Extract all IDs from the return value
2. Add them to the appropriate `entities` section of the ledger
3. Add the completed step to `completedSteps`
4. Remove from `pendingValidations` if this call validated something
5. Update `phase` and `step` to the current position

### Rehydrating at session start

If a conversation is interrupted and resumed, read the state ledger and verify key entities still exist:

```javascript
// Verify that critical nodes from the ledger still exist
const toVerify = {
  'color-collection':  'VariableCollectionId:1234:5679',
  'button-page':       '0:3',
  'button-componentset': '4567:1',
};

// Batch the lookups — awaiting getNodeByIdAsync per entry serializes the
// round-trips. Resolve them all in parallel with Promise.all, then walk the
// results.
const entries = Object.entries(toVerify);
const nodes = await Promise.all(
  entries.map(([, id]) => figma.getNodeByIdAsync(id).catch(() => null))
);
const results = {};
for (let i = 0; i < entries.length; i++) {
  const [label] = entries[i];
  const node = nodes[i];
  results[label] = node ? { found: true, name: node.name } : { found: false };
}

return results;
```

If any entity is missing, treat the phase that created it as incomplete and re-run from that checkpoint.

---

## 5. Resume Protocol

### Step 1: Inventory deterministic names

First list page IDs and names. Then run one page-scoped inspection per relevant page; do not switch through multiple pages in one call.

```javascript
const PAGE_ID = 'PAGE_ID_FROM_DISCOVERY';
const page = await figma.getNodeByIdAsync(PAGE_ID);
await figma.setCurrentPageAsync(page);

const nodes = page.findAllWithCriteria({
  types: ['FRAME', 'COMPONENT', 'COMPONENT_SET'],
});
return nodes.map(node => ({
  id: node.id,
  type: node.type,
  name: node.name,
  ...(node.type === 'COMPONENT' || node.type === 'COMPONENT_SET'
    ? { description: node.description }
    : {}),
}));
```

Use separate read calls for local variable collections, variables, and styles. Filter each result against the deterministic names in the build plan.

### Step 2: Reconstruct state from inventory

Match names only within their expected entity type and parent page or collection. Add each confirmed ID to the state ledger, then mark the corresponding step as `completedSteps`.

Example mapping:
```
collection named 'Color' on the planned foundations page → entities.collections.color
variable named 'color/bg/primary' in that collection      → entities.variables['color/bg/primary']
page named 'Button'                                      → entities.pages.Button
component set named 'Button' on that page                → entities.componentSets.Button
```

### Step 3: Identify the resume point

The resume point is the first step in the workflow that is NOT in `completedSteps`. If the inventory shows the Button component set exists but the pending validations list shows `'Button:screenshot'`, the resume point is the screenshot validation call, not re-creation.

Use the checkpoint table from the workflow to determine which phase to continue from:

```
Phase 0 complete: all planned pages listed in entities.pages
Phase 1 complete: all planned variables listed in entities.variables with correct scopes
Phase 2 complete: all structural pages + foundations doc frames present
Phase 3 complete (per component): componentSet exists + no pending validations + user checkpoint recorded
```

---

## 6. Failure Taxonomy

### Recoverable Errors

These can be fixed and retried without affecting already-created entities:

| Category | Examples | Recovery |
|---|---|---|
| Layout errors | Variants stacked at (0,0), wrong padding values | Re-run the positioning step only |
| Naming issues | Typo in variant name, wrong casing | Resolve the node by its state-ledger ID and update `name` |
| Missing property wiring | `componentPropertyReferences` not set | Find component set by ID, re-run the property wiring step |
| Variable binding omission | A fill was hardcoded instead of bound | Resolve the node by its state-ledger ID and re-bind the fill |
| Wrong variable bound | Bound to wrong variable ID | Re-bind with correct variable ID |
| Text not visible | Font not loaded before text write | Call `listAvailableFontsAsync()` to verify the font exists, then re-run text creation with `loadFontAsync` |
| Script timeout | Script exceeded time limit before completing | Script is atomic — nothing was created. Reduce scope (fewer nodes per call) and retry |

### Structural Corruption (Requires Rollback or Restart)

These errors leave the file in a state where continuing forward is unreliable:

| Category | Examples | Recovery |
|---|---|---|
| Component cycle | A component instance was accidentally nested inside itself | Full cleanup of the affected component, restart that component from Call 1 |
| combineAsVariants with non-components | Mixed node types passed to combineAsVariants, causing unexpected merges | Remove the malformed component set, re-run from variant creation |
| Variable collection ID drift | Collection was deleted and re-created, old IDs in state ledger are stale | Re-run Phase 1 completely; update all IDs in state ledger |
| Page deletion | A page was deleted after component sets were created on it | Treat as Phase 2 incomplete; re-create the page + re-run affected component creations |
| Mode limit exceeded | `addMode` threw because the plan is Starter or Professional | Redesign variable collection architecture to fit mode limits, restart Phase 1 |

**Recovery from structural corruption**: run `cleanupOrphans` with the exact state-ledger IDs for the affected phase, then restart that phase. Do NOT attempt to patch corrupted structure in-place.

---

## 7. Common Error Table

| Error message | Likely cause | Fix |
|---|---|---|
| `"Cannot create component from node"` | Tried to call `createComponentFromNode` on a node inside a component | Create a fresh component instead: `figma.createComponent()` |
| `"in addMode: Limited to N modes only"` | Plan mode limit hit (Starter=1, Professional=4) | Redesign to use fewer modes or upgrade plan |
| `"setCurrentPageAsync: page does not exist"` | Page was deleted or wrong ID | Re-create the page using the idempotency pattern |
| `"Cannot read properties of null"` | `getNodeByIdAsync` returned null — node was deleted | Run the resume protocol to find what exists, update state ledger |
| `"Expected nodes to be component nodes"` | Passed a non-ComponentNode to `combineAsVariants` | Filter the array: `nodes.filter(n => n.type === 'COMPONENT')` |
| `"in createVariable: Cannot create variable"` | Collection was deleted or ID is wrong | Verify collection exists with `getVariableCollectionByIdAsync` |
| `"font not loaded"` | Called a text property setter without `loadFontAsync` first | Call `await figma.listAvailableFontsAsync()` to discover available fonts and verify the font name, then `await figma.loadFontAsync({ family, style })` before the text operation |
| `"Cannot set properties of a read-only array"` | Tried to mutate fills/strokes in-place | Clone first: `const fills = JSON.parse(JSON.stringify(node.fills))` |
| `"Expected RGBA color"` | Color value out of 0–1 range | Divide RGB 0–255 values by 255: `{ r: 65/255, g: 85/255, b: 143/255 }` |
| `"Cannot add children to a non-parent node"` | Tried to append a child to a leaf node (text, rect) | Ensure the parent is a FrameNode, ComponentNode, or GroupNode |
| `"in combineAsVariants: nodes must be in the same parent"` | Components are on different pages | Move all components to the same page before combining |
| `"Script exceeded time limit"` | Loop creating too many nodes in one call | Split the work: create N/2 variants per call |
| Component set deletes itself | Tried to create a component set with no children | `combineAsVariants` requires at least 1 node — always pass 1+ |
| `addComponentProperty` returns unexpected name | This is normal — `BOOLEAN`/`TEXT`/`INSTANCE_SWAP` get `#id:id` suffix | Save the returned key immediately and use that, not the input name |

---

## 8. Per-Phase Recovery Guidance

### Phase 1 fails (variable creation)

Since `use_figma` is atomic, a failed call creates nothing. The most common scenario is that some calls in Phase 1 succeeded (creating some variables) while a later call failed.

Recovery steps:
1. Run the inventory helper and scope variables by their expected collection and deterministic names
2. Compare against the plan to identify which variables were successfully created and which are still missing
3. If a successfully created variable has wrong values, call `variable.remove()` and recreate it
4. Fix the failed script and retry — it's safe since the failed call created nothing
5. Do NOT proceed to Phase 2 until ALL planned variables exist with correct scopes and code syntax

**The most common Phase 1 failure:** script timeout when creating many variables. Fix: batch variable creation — create at most 20–30 variables per call.

### Phase 2 fails mid-execution (page/file structure)

Symptoms: some pages exist, others are missing; foundations doc frames are incomplete.

Recovery steps:
1. Identify which pages were successfully created by their deterministic names and state-ledger IDs
2. Mark remaining pages as pending and create them in subsequent calls
3. If a foundations doc frame is malformed, pass its exact state-ledger ID to `cleanupOrphans`, then recreate it

Phase 2 failures rarely require Phase 1 rollback unless the page structure itself is corrupted (which is unusual).

### Phase 3 fails (component creation)

This is the most common failure mode in long builds. Since `use_figma` is atomic, a failed call creates nothing — but previous successful calls in the component creation sequence will have created state. Handle by which call in the sequence failed:

```
If failure in Call 1 (page creation):
  → Nothing was created. Fix the script and retry.

If failure in Call 2 (doc frame):
  → Call 1's page exists. Fix Call 2 and retry — idempotency check handles it.

If failure in Call 3 (base component):
  → Calls 1-2 succeeded. Fix Call 3 and retry.

If failure in Call 4 (variant creation):
  → Call 3's base component exists. Fix Call 4 and retry.
  → If you need to restart from Call 3, clean up Call 3's nodes first
    using cleanupOrphans scoped to the component page.

If failure in Call 5 (combineAsVariants + layout):
  → Variant ComponentNodes from Call 4 exist but aren't combined yet.
  → Fix Call 5 and retry.
  → If the component set was already created by a prior attempt of Call 5
    that succeeded, remove it first, then re-run.
If failure in Call 6 (component properties):
  → The component set already exists and is structurally sound.
  → Fix Call 6 and retry — addComponentProperty is safe to retry if
    you first resolve the COMPONENT_SET and check componentPropertyDefinitions there.
  → Idempotency check: if a UID-suffixed `Label#...` property already exists, skip addComponentProperty.
```

**Idempotency for component properties (Call 6 retry):**

```javascript
const candidate = await figma.getNodeByIdAsync(COMPONENT_SET_ID);
if (!candidate || candidate.type !== 'COMPONENT_SET') throw new Error('Expected a component set');
const existingDefs = candidate.componentPropertyDefinitions;
const labelKey = Object.keys(existingDefs).find(key => key.startsWith('Label#'))
  ?? candidate.addComponentProperty('Label', 'TEXT', 'Button');
```

### Phase 4 fails mid-execution (QA / Code Connect)

Phase 4 is non-destructive. Failures here do not corrupt Phase 3 work. Common failures:

- **Accessibility audit finds contrast failures:** do not attempt auto-fix. Report the specific variable IDs and token names that fail, then ask the user which value to update.
- **Naming audit finds duplicates:** list all duplicates with their `key` values, ask user which to keep, then remove the duplicates.
- **Code Connect mapping fails:** treat as incomplete, not broken. Continue and leave as pending.
