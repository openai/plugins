# Catalog Lifecycle

Use this reference before creating, updating, or deleting a Catalog.

For creation, list in the bound Space, reject duplicate names, validate only
live-schema fields, show the final metadata and scope, confirm, create once,
then list Catalogs once and match one exact target. Verify the Space binding and
requested metadata; stop if the created resource cannot be uniquely matched.

For update, resolve one exact Catalog in the bound Space, inspect current metadata
and contents, show an exact before/after diff, confirm, update only requested
fields, and verify omitted fields were preserved.

After an uncertain create, complete the exact-name search. Report success for
one matching Catalog; retry once only when the name is absent; stop on a
conflict or non-unique result. After an uncertain update, read the exact target.
Report success when all approved fields match; retry once only when every field
still matches the before-state; stop on a partial change.

For deletion, use the dedicated impact result and live cascade declaration.
Show the exact target, Space, and visible impact before confirmation. Delete
once and verify that target is absent. If cascade behavior or the result is
uncertain, stop and report it without retry.
