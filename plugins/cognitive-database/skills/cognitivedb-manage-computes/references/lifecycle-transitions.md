# Compute Lifecycle Transitions

Use this reference for start, stop, or retained cache cleanup.

## Transition Gate

- Validate each requested start or stop against fresh state and the live
  contract. Confirm each transition separately.
- If the requested terminal state is already observed, report it and do not
  call the mutation tool.
- Do not switch to another lifecycle operation after a state conflict unless
  the user approves a newly proposed transition.

## Verify Start or Stop

Use the tool's bounded wait when completion is requested. If it returns an
accepted or uncertain result, describe the same Compute once and report the
observed state. Claim completion only when the requested terminal state is
observed.

## Retained Cache Cleanup

- If cache state is `CLEARING`, report cleanup in progress. If it is
  `NOT_RETAINED`, report that there is no cache to clear. Otherwise require a
  stopped Compute with `dataCache.canClear` true before requesting approval.
  Include possible initial query slowdown in the confirmation.
- Call `cognitivedb_compute_clear_cache` once after confirmation. Use bounded
  wait when completion is requested. For an accepted or uncertain result,
  describe the same Compute once. Report completion only for
  `NOT_RETAINED`, failure for `CLEANUP_FAILED`, and an unverified outcome if
  the state is missing.
