# Compute Creation and Notebook Runtime SQL Binding

Use this reference for Compute creation or Notebook Runtime SQL binding.

## Resolve SQL Warehouse Configuration

1. Bind the current Space and list Computes before selecting configuration.
2. Call `cognitivedb_compute_global_configuration_get` for global defaults and
   allowed configuration ranges. Select the workload category from the live
   type-list contract and the user's workload.
3. Call `cognitivedb_compute_type_list`. Preserve the exact selected type and any
   category evidence; never derive API enums from user-facing labels.
4. Pass the exact returned type to `cognitivedb_compute_spec_list`. Select only a
   returned, currently available `specCode`. For a GPU product, card count is
   represented by the selected spec entry and may already be encoded in its
   `specCode`; do not invent another create argument.
5. After a user changes a choice, validate only that choice and the fields it
   directly determines. Keep all other current evidence. Never reuse values
   from a different Space or earlier session.

For example, “General Compute” does not authorize inventing `general`; a live
tool may return `default`. If the tools do not provide an authoritative and
compatible category, type, and spec, report the capability gap and stop.

## Confirm and Verify SQL Warehouse Creation

Collect unresolved material choices before asking for creation confirmation.
Do not combine those choices with approval of a proposal whose final values are
not yet known. Before confirmation, show the resolved name, Space, category,
type, specification, GPU count and sizing guidance when returned, auto-resume,
auto-suspend, idle delay, description, and known cost or quota impact. Disclose
missing quota or price evidence instead of estimating it.

Call create once. Require its immutable ID to be visible in list and resolvable
by describe with the expected category, type, specification, and settings. If
list sees the ID but describe cannot resolve it, report a service consistency
defect and stop all further lifecycle calls. Do not retry creation.

## Notebook Runtime

- Use `cognitivedb_notebook_runtime_create`. Resolve CPU or GPU and the
  SQL mode before approval. Integrated SQL and Python requires GPU. For an
  existing Warehouse, resolve its exact ID in the current Space and include it
  in the proposal. Runtime specifications are fixed by the tool.
- Include any selected SQL Warehouse in the creation confirmation. Read back
  the Runtime by ID. For an existing Warehouse, verify both IDs in the returned
  binding. If the user also requested start, confirm it separately after
  creation is verified.
- If creation returns a Runtime ID but the requested binding is unconfirmed,
  report both outcomes. The Compute read does not verify the SQL association.
  Use standalone binding only if the failure explicitly establishes that the
  association was not applied. For an unknown outcome, stop and report it.
  For uncertain creation without an ID, follow the ambiguous outcome reference.
- For standalone binding, resolve the Runtime and SQL Warehouse in the current
  Space and confirm both IDs. Integrated Runtimes cannot bind an external
  Warehouse. Call `cognitivedb_notebook_runtime_sql_bind` and verify the returned
  association before reporting completion.
