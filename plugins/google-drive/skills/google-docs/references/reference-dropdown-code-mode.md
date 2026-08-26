# Native Dropdown Code Mode

When to read: the user asks to create a native Google Docs dropdown, replace its ordered options, or set its selected value. Do not read this reference for preservation-only work.

## Contents

1. Capability gate
2. Pre-write route
3. Trusted components
4. Task workspace
5. Semantic inventory and task contract
6. One-stage plans
7. Validation and bridge execution
8. Multi-stage tasks
9. Ambiguous outcomes and reconciliation
10. Final verification and cleanup

## Capability Gate

Exact dropdown mutation requires both authenticated connector capabilities:

- `getDocumentDropdowns`
- `updateDocumentDropdown`

Discover capabilities before promising an exact dropdown result and before any write. The read capability must return native semantic metadata: document identity, revision, tab, dropdown identity when the provider exposes one, UTF-16 location, ordered options, selected value, and a stable semantic signature. The write capability must support one guarded `create`, `replace_options`, or `set_selected_value` operation and return the updated semantic record plus a post-write revision.

The connector action contract is:

- `get_document_dropdowns`: accepts `document_id` or `document_url`, optional `tab_id`, and an optional bounded structural selector. It returns document identity, revision, and native dropdown records with provider ID when available, tab/segment UTF-16 range, paragraph or table-cell container, ordered options, selected value, provider-supported color/style metadata, display text, and stable semantic signature.
- `update_document_dropdown`: accepts exact document and tab, `required_revision_id`, idempotency key, and exactly one connector-native operation. Existing mutations prefer `dropdown_id`; when unavailable they require a unique frozen binding locator plus semantic signature. Creation requires an exact location and surrounding anchor signature. Every operation carries expected-before conditions, and the response returns the updated record, outcome class, and post-write revision.

The connector must reject stale revisions, ambiguous anchors, duplicate labels, selected values outside the option set, unsupported provider values, missing dropdown targets, and document/tab mismatch before applying. It must expose one of `applied`, `rejected_before_apply`, `stale_revision`, `ambiguous_anchor`, `rate_limited_before_apply`, `unknown_application_state`, `applied_readback_failed`, or `verification_failed`. Provider integration must also register the two actions in MCP discovery and golden fixtures, Drive source attribution, user-facing activity labels, and Google Workspace write analytics. The plugin-side executor consumes those contracts but cannot manufacture the external connector actions.

If either capability is missing, or readback cannot distinguish a native dropdown from styled text, stop before writing. Preservation-only edits may continue on the direct path. Do not substitute public Docs `batchUpdate`, a private Google RPC, Browser Use, or UI automation. Do not silently flatten the requested dropdown to text.

The `google-docs-cm` skill and its branch are reference material only. Never load, import, invoke, install, route to, or depend on them. This reference and the checked-in files under `google-docs` are the only allowed code-mode implementation.

Serialized `google-docs-v2-dropdown-*` kind values are the established version-1 dropdown protocol identifiers. Retain them for executor compatibility; they do not refer to the V2 skill directory.

## Pre-Write Route

Resolve the route before the first document mutation:

| Intent | Route |
| --- | --- |
| No dropdown involvement | Direct connector workflow |
| Preserve an existing dropdown | Direct workflow plus the preservation manifest |
| Edit nearby text without touching the dropdown | Direct workflow with ranges split around the control |
| Create a native dropdown | Checked-in Google Docs dropdown code mode |
| Replace ordered dropdown options | Checked-in Google Docs dropdown code mode |
| Change the selected value | Checked-in Google Docs dropdown code mode |
| Ordinary text or table changes plus any dropdown mutation | Checked-in Google Docs dropdown code mode for the entire task |
| Plain-text approximation explicitly approved by the user | Direct workflow; identify the output as an approximation |
| Required connector actions unavailable | Stop before writing |

Use `runtime/dropdown-routing.mjs` for the deterministic decision. Exact mutation requires the established `google_docs_v2_dropdown_code_mode` feature flag and both connector capabilities. The legacy flag name is part of the existing runtime contract and does not refer to the V2 skill directory. A `dropdown-code-mode` decision owns every write in the task. Never alternate direct and code-mode writers in one mutating trajectory.

If a task originally classified as preservation-only later requires dropdown mutation, stop the direct trajectory, reread the live document, rebuild the preservation inventory, and begin a new code-mode trajectory from the current revision. Do not reuse stale indexes or issue a dropdown write after an earlier untracked direct write.

## Trusted Components

Only these checked-in Google Docs components may participate:

- `runtime/dropdown-inventory.mjs`: normalizes authoritative document structure and dropdown metadata.
- `runtime/dropdown-contract.mjs`: freezes target identity, source denylist, protected surfaces, native dropdown bindings, and opaque controls.
- `runtime/dropdown-plan.mjs`: validates a single guarded mutating stage.
- `scripts/build_docs_dropdown_inventory.mjs`: creates the normalized inventory artifact.
- `scripts/freeze_docs_dropdown_contract.mjs`: creates the frozen task contract.
- `scripts/validate_docs_dropdown_plan.mjs`: creates the hash-bound validation sidecar.
- `scripts/create_docs_dropdown_execution_context.mjs`: creates the bridge execution context.
- `host/docs-dropdown-executor.mjs`: performs preflight, one mutation, and post-write verification.
- `host/docs-dropdown-file-bridge.mjs`: evaluates only the checked-in executor and persists compact immutable artifacts.

Do not execute model-authored JavaScript, arbitrary helper scripts, embedded private RPCs, nested connector writers, or any code copied from another skill. A model may author JSON plan artifacts only.

The trusted executor resolves only `getDocument`, `getDocumentTables` when needed, `batchUpdateDocument`, `getDocumentDropdowns`, and `updateDocumentDropdown`. Connector adapters may map installed action names to those capability names, but may not broaden the capability set.

## Task Workspace

Create one thread-scoped scratch directory outside user deliverables and keep it untracked. Use restrictive permissions. Keep source snapshots, inventory, contracts, stage plans, validation sidecars, checkpoints, receipts, and manifests there.

Use a new immutable output directory for each stage. Never overwrite a prior stage artifact. Suggested layout:

```text
<scratch>/google-docs-dropdown/<task-id>/
  source/
    document.json
    dropdowns.json
  task/
    inventory.json
    contract.json
    execution-context.json
  stages/
    001-docs-edit/
      plan.json
      validation.json
      result/
    002-dropdown-create/
      plan.json
      validation.json
      result/
```

Keep raw connector payloads and document content out of the model-facing bridge result. The bridge returns only compact status, hashes, artifact paths, counts, and sanitized errors.

## Semantic Inventory And Task Contract

Read the live target with authoritative `get_document` structure and `get_document_dropdowns` metadata from the same revision. Include tables when container coordinates matter. Then build the normalized inventory:

```sh
node scripts/build_docs_dropdown_inventory.mjs \
  --document /absolute/task/source/document.json \
  --dropdowns /absolute/task/source/dropdowns.json \
  --output /absolute/task/task/inventory.json
```

Only provider-identified native dropdown records become `dropdownControl` bindings with `fidelityClass: "exact-writable"`. Private-use characters or other unmatched placeholders become `opaqueTemplateControl` bindings with `fidelityClass: "copy-only"`. Never infer that a private-use glyph is a dropdown.

Freeze the task contract before planning a write. The decisions file contains the selected tab, immutable source document IDs, protected tabs, and protected ranges:

```sh
node scripts/freeze_docs_dropdown_contract.mjs \
  --inventory /absolute/task/task/inventory.json \
  --decisions /absolute/task/task/decisions.json \
  --output /absolute/task/task/contract.json
```

Every discovered dropdown and opaque control is frozen into the contract, even if the model-authored plan does not mention it. A reusable source template must be copied first, and the source document ID must be placed in `sourceDocumentIds`. The source can never become the target.

## One-Stage Plans

Each plan artifact contains exactly one mutating stage and is bound to one document revision, selected tab, inventory hash, and task contract. Valid stage types are:

- `docs_batch_update`
- `dropdown_create`
- `dropdown_replace_options`
- `dropdown_set_selected`

Use native Google Docs request objects under `stage.call.requests` for `docs_batch_update`. Include `write_control.requiredRevisionId`, an `expectedBefore` object bound to the live revision and frozen binding hash, and an `expectedAfter` object requiring both a revision change and preserved semantic bindings. Broad `replaceAllText`, named-range replacement, and writes intersecting frozen semantic controls are rejected.

Dropdown stages pass connector-native `update_document_dropdown` arguments. Do not invent a generic semantic mutation language. A create operation must include an exact UTF-16 location, tab, surrounding anchor signature, ordered nonempty unique options, selected value when requested, expected-before conditions, revision, and idempotency key. Mutations of existing dropdowns must use the provider dropdown ID when available.

Example stage skeleton:

```json
{
  "version": 1,
  "kind": "google-docs-v2-dropdown-plan",
  "target": {
    "documentId": "TARGET_ID",
    "title": "Target title",
    "tabId": "t.0",
    "expectedRevisionId": "REVISION"
  },
  "baseSnapshot": {"sha256": "INVENTORY_HASH"},
  "contract": {
    "targetBindingsHash": "BINDINGS_HASH",
    "decisionHash": "DECISION_HASH"
  },
  "stage": {
    "id": "002-dropdown-create",
    "type": "dropdown_create",
    "call": {
      "document_id": "TARGET_ID",
      "required_revision_id": "REVISION",
      "idempotency_key": "TASK_AND_STAGE_UNIQUE_KEY",
      "operation": {
        "type": "create",
        "location": {"tabId": "t.0", "segmentId": null, "index": 120},
        "anchor": {"beforeHash": "HASH", "afterHash": "HASH"},
        "options": [
          {"label": "TBD", "color": "GRAY"},
          {"label": "Ready", "color": "GREEN"}
        ],
        "selected_value": "TBD",
        "expected_before": {"dropdownAbsent": true}
      }
    },
    "expectedAfter": {
      "options": [
        {"label": "TBD", "color": "GRAY"},
        {"label": "Ready", "color": "GREEN"}
      ],
      "selectedValue": "TBD"
    }
  }
}
```

The expected-after state must fully describe the requested dropdown semantics. The selected value must belong to the desired option set. Labels must be nonempty and unique, and option order is significant.

## Validation And Bridge Execution

Create the execution context and validate the plan before connector access:

```sh
node scripts/create_docs_dropdown_execution_context.mjs \
  --workspace-root /absolute/task \
  --target-document-id TARGET_ID \
  --executor /absolute/repo/plugins/google-drive/skills/google-docs/host/docs-dropdown-executor.mjs \
  --output /absolute/task/task/execution-context.json

node scripts/validate_docs_dropdown_plan.mjs \
  --plan /absolute/task/stages/002-dropdown-create/plan.json \
  --inventory /absolute/task/task/inventory.json \
  --contract /absolute/task/task/contract.json \
  --executor /absolute/repo/plugins/google-drive/skills/google-docs/host/docs-dropdown-executor.mjs \
  --output /absolute/task/stages/002-dropdown-create/validation.json
```

The validation sidecar binds the exact plan, inventory, contract, and trusted executor hashes. Invoke `executeDocsDropdownPlanFromFiles` from the checked-in file bridge with absolute paths, the mounted authenticated connector tools, and a new result directory. The bridge rejects executable plan files, path traversal, changed hashes, an existing result directory, target mismatch, and an untrusted executor path.

The executor then:

1. rereads live document and dropdown state
2. verifies document, title, tab, revision, source denylist, and every frozen semantic binding
3. independently validates the stage scope
4. dispatches exactly one guarded mutation
5. rereads document structure and dropdown metadata
6. proves the revision changed, expected dropdown state holds, and surrounding frozen structures were preserved
7. returns a sanitized receipt

Never report success from the mutation response alone.

## Multi-Stage Tasks

For ordinary Docs edits plus dropdown mutation, select code mode before the first write and use it for all stages:

1. Freeze one task-level preservation intent from the first live revision.
2. Materialize and execute one `docs_batch_update` stage.
3. Reread document structure and dropdown metadata.
4. Rebuild the inventory and re-freeze the contract against the new revision while retaining source denylist and preservation decisions.
5. Materialize and execute one dropdown stage.
6. Reread and rebase again before every additional dropdown.
7. Perform final whole-task verification.

Never precompute later indexes, revisions, or anchors. One dropdown operation is allowed per connector call and per plan artifact.

## Ambiguous Outcomes And Reconciliation

Do not automatically retry a mutation that returns `unknown_application_state`. Retrying may create a duplicate dropdown or repeat a selection/options change.

Use read-only reconciliation through `reconcileUnknownDropdownMutation` in the trusted executor. Reconciliation must use the same document ID, tab, idempotency key, dropdown ID or creation anchor, and expected-after state. Continue only when authoritative readback proves either:

- the original operation applied exactly once and matches the expected state; or
- the original operation did not apply and a fresh, newly validated stage may be attempted.

If readback remains ambiguous, stop and report the unknown state. Treat `stale_revision` by rereading, rebuilding the inventory, refreezing the contract, and revalidating. Treat `applied_readback_failed` as potentially applied; reconcile rather than retry. Treat `verification_failed` as a failed task even if the connector returned success.

## Final Verification And Cleanup

Final verification must classify every relevant control:

- `connector-proven native dropdown`: authoritative metadata confirms ordered options, selected value, identity, and tab after mutation.
- `copy-preserved opaque control`: a copy or preservation manifest proves its opaque signature and surrounding structure remained unchanged; semantics are not claimed.
- `user-approved text approximation`: the user explicitly accepted a non-native substitute.
- `unverified`: required semantic metadata or readback was unavailable.

Verify source templates and source tabs remain unchanged, all unrelated dropdowns and opaque controls retain their frozen signatures, ordinary text/table changes match their declared scope, and no full-document rebuild occurred.

After successful handoff, remove thread-scoped raw snapshots and connector payloads unless retention is required for debugging. Retain only the compact receipt/manifest needed by the surrounding execution environment. Never log document text, option labels, people, signed URLs, or raw connector payloads in analytics.
