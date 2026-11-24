# Query History Scope and Evidence

Use this reference for requested execution history or historical error details.
Query History reads do not require selecting or starting a Compute.

## Identity and Scope

- Resolve "my" using the authenticated current user, not an owner, Space creator,
  or the users appearing in a result page. Keep the current Space fixed.
- Apply a current-user filter when supported and permitted by the live contract.
  Otherwise rely on default scope only when authoritative evidence establishes
  that it is restricted to the current user. Visibility may include other users;
  matching users in one page alone do not establish a self-only default.
- If self-only scope cannot be established, disclose the limitation. Do not label
  a Space-wide result as personal history or request permission changes merely
  to answer a personal-history question.
- Check returned user identifiers against the resolved identity. If records fall
  outside the requested scope, exclude them from the personal result, report the
  mismatch, and stop instead of asserting a complete personal history.

## Time and Pagination

- Use the live contract's timestamp format, timezone, range limits, and boundary
  semantics. Split a wider requested period into supported windows; do not guess
  alternate timestamp formats when a range is rejected. If the failure provides
  no actionable constraint, report it instead of probing speculative boundaries.
- Use returned cursors within each window. Preserve the filters while advancing;
  deduplicate execution IDs across overlapping boundaries. For latest-N requests,
  visit newest windows first and stop when N matching records have been obtained.
- Report requested and actually covered periods, returned count, and remaining
  pages. For an all-records request, report incomplete coverage if a tool limit,
  failure, or execution budget prevents completion; do not silently narrow it.

## Failure Details

- Select the requested failed execution from the verified scope and read its
  exact detail. Distinguish SQL previews from complete SQL and never execute them.
- Explain a failure only from returned error detail and relevant execution
  evidence. A missing detail is not evidence of success, expiry, or permission
  denial. State what is unavailable and leave the cause unresolved unless the
  contract or structured result establishes it.
- Do not infer retention periods from record age or probe unrelated dates to
  find a presumed expiry boundary. Preserve the failed execution identifier and
  finish with the evidence gap when no actionable diagnostic is returned.
