# Compute Deletion and Recovery

Use this reference before deleting or after any ambiguous Compute mutation.

## Delete

Resolve one immutable ID and obtain an authoritative current snapshot. Use list
for discovery or ambiguity and describe when an immutable ID is supplied or list
evidence is incomplete. Before confirmation, show resource type, exact name and
ID, current Space, state, configuration, visible
dependencies, and declared cascade behavior. State any dependency or cascade
information that the live tools cannot inspect. Confirm the exact target,
delete once, then list and verify that exact ID is absent.

## Ambiguous Outcomes

After an uncertain mutation, read the exact target once before retrying. If
creation returned no ID, list the current Space for the proposed exact name.
Retry only when evidence establishes that the operation did not take effect.
Retry the same GPU Notebook Runtime creation only with its original request ID
and identical arguments.
If the outcome or association remains unknown, report it with the available
correlation evidence.
