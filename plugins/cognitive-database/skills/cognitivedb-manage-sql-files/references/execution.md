# SQL File Snapshot Validation and Execution

## Complete-file precheck

Resolve one exact personal file and the execution context from user choices and
live context tools. After materialization, use its returned immutable ID without
resolving the name again. Do not fetch content merely to preflight execution,
count preview statements, or infer equality from file size. The execution Tool
reads the complete snapshot, substitutes variables, validates every statement,
and binds its summary and context to runtime confirmation before submission.
This is the full-file precheck; no separate dry-run capability is assumed.
Local artifact digests check preparation/transfer integrity only; they do not
replace the Tool's remote snapshot fingerprint or prove remote content equality.

For an explicit expected count, bind whether it counts queries or all statements,
the count, and the permitted operation classes to task approval. Require read-only
scope only for a read-only request; an approved initialization or mixed SQL File
may contain supported DDL or DML. Check the complete snapshot's matching count
and operation classes when exposed before submission; a mismatch must not be
approved. If unavailable, disclose the verification gap rather than inspecting
truncated previews or searching for copies.
Compare the receipt's `totalStatements` with an expected total-statement count,
or with a query count only when verified operation classes establish that every
statement is a counted query. For a mixed file, verify query count separately
when exposed; never infer a mismatch from the total alone. An observed matching-
scope count mismatch blocks further runs and requires reporting the submitted
execution. Unavailable counts remain unverified. Submission counts alone do not
establish successful completion or correct query results.

## Approval and repetition

Bind task approval to the exact file, Compute, Catalog, Schema, variable names,
result limit, and requested repeat count. One explicit approval may cover the
listed successive executions with unchanged content and context, unless the
live contract requires separate task approvals. Do not ask additional generic
approval questions for the same plan. Every execution still passes the live
Tool's snapshot-bound runtime confirmation; task approval cannot replace it.
A content, target, Compute, variable, result-limit, or repeat-count change
invalidates the relevant approval. For a generated artifact, return content or
validation changes to the supplying specialization before executing.
Keep sensitive variable values out of user-facing confirmations and reports.

Submit runs successively, proceeding only after the preceding run is terminal
and its required coverage is checked. Stop on failure, cancellation, count
mismatch, or unknown outcome; never submit a replacement for an uncertain run.
Use the result limit appropriate to the requested evidence and keep it fixed
across compared runs. A small row limit bounds returned data, not suite coverage
or proof of result correctness.

## Context and tracking

Apply `cognitivedb-gpu-workload-guidance` for a GPU SQL File only when its content
is already available through authorized inspection. Do not retrieve hidden
content just for classification. Bind one exact compatible runnable Compute;
reuse an exact user-selected or still-runnable session-approved Compute without
reopening the choice. Load `cognitivedb-manage-computes` only for a material
Compute choice, incompatibility, lifecycle action, or verified resource shortfall.
Treat Suspended with Auto Resume as usable only when the live execution contract
supports it. After an approved start, verify Started and resolve execution context
once again because runnable state changed.

Preserve the exact returned execution reference. On a nonterminal response,
check status promptly, then at most five more times per turn with 2–10 second
backoff, subject to stricter live polling limits. If still running, report ID
and progress. Never describe a failure as awaiting confirmation or retry with
another file. At terminal, use a complete statement-status summary when supported
and only status is needed; otherwise retrieve the evidence required by the live
contract. Do not request result rows to seek undocumented timing fields.
Truncated rows cannot support complete data claims.

For cancellation, present the execution, file, target, completed-statement impact,
and partial-change risk; present the confirmation directly, cancel once
after approval, then read status once. Only `CANCELED` confirms cancellation.
Statements are ordered but not atomic: report earlier mutations on failure.

## Verification and disposition

Keep successful-statement coverage, timing evidence, and result correctness
separate for each run. Never extend one run's verification to another run.
Once a generated artifact is accepted, this Skill owns materialization,
snapshot confirmation, execution tracking, and statement-status reporting; do
not return it to an inline owner merely because it contains DDL or DML.
Hand exact successful DML/CTAS targets to `cognitivedb-data-analysis` and DDL
targets to `cognitivedb-manage-data-assets` for bounded verification, with execution
ID and statement index. Handoff does not authorize a new operation, but does not
invalidate approval already bound to the identical operation in the current task.

After terminal execution and verification, ask whether to retain or delete each
execution-only file unless disposition is already chosen. On no answer or
cancellation, keep it and report the immutable ID. Delete only after approval
of that exact ID and verify absence; execution approval is not deletion approval.
