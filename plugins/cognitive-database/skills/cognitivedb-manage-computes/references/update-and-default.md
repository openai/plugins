# Compute Update and Default Selection

Use this reference before updating a Compute or setting it as default.

## Update

Resolve one exact ID and obtain an authoritative current snapshot, then preserve
every field the user did not request to change. Use list to discover or
disambiguate a name. When the user supplies an immutable ID, describe may resolve
and inspect it directly. If list already returns the exact ID and every current
field needed for the proposal, do not repeat describe only for ceremony; call it
when list evidence is incomplete. Reject an empty update. Before changing
specification, resolve the current type and verify the requested `specCode` with
`cognitivedb_compute_spec_list`. Validate configuration fields against live
`cognitivedb_compute_global_configuration_get` evidence.

Show an exact before/after diff plus cost, capacity, interruption, auto-resume,
and auto-suspend impact that is known from live evidence. Confirm that exact
diff, update once, then describe the same ID and verify only the requested
fields changed.

## Set Default

Resolve the exact candidate and inspect the current default. Explain the
consumer-selection impact, confirm the exact ID, call set-default once, then
list and verify the effective default. Do not imply that setting a default
starts the Compute or changes its configuration unless live evidence says so.
