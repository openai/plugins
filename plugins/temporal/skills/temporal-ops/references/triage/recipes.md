# Recipes

End-to-end triage walkthroughs. Each recipe stitches sibling files into a single narrative for a common incident shape. Commands below are copied forward from the sibling files with pointers back to where the flag set and citations live; this file is not independent ground truth for command syntax.

Confidence checkpoints follow the skill convention in [runtime-errors.md](runtime-errors.md#why-these-errors-are-hard): label a proposed root cause low/medium/high based on corroborating signals, not feel.

## Table of Contents

- [Stuck workflow at 3am](#stuck-workflow-at-3am)
- [Cert expired, workers offline](#cert-expired-workers-offline)
- [Task-queue backlog mystery](#task-queue-backlog-mystery)
- [Non-determinism caught in prod](#non-determinism-caught-in-prod)

## Stuck workflow at 3am

**Page text:** "Workflow `order-1234` is stuck, status Running, no progress for 2 hours."

**Goal:** classify the stuck-ness shape (pending operation vs. WFT-failure loop vs. timer) and apply the matching recovery.

**Steps:**

1. **Confirm the status is Open.** Run the primary inspection command — see [workflow-stuck.md → The primary inspection command: `temporal workflow describe`](workflow-stuck.md#the-primary-inspection-command-temporal-workflow-describe) for the full flag table:

   ```bash
   temporal workflow describe \
       --workflow-id order-1234 \
       --namespace <ns>
   ```

   If `workflowExecutionInfo.status` is anything other than `Running`, the workflow is Closed and this recipe does not apply — see [workflow-stuck.md → Workflow Execution Status values](workflow-stuck.md#workflow-execution-status-values).

2. **Rule out the worker layer.** Most 3am "stuck workflow" pages are really worker outages. Check pollers on the Workflow's Task Queue — full discrimination in [worker-health.md → Inspecting a Task Queue with `temporal task-queue describe`](worker-health.md#inspecting-a-task-queue-with-temporal-task-queue-describe):

   ```bash
   temporal task-queue describe \
       --task-queue <q> \
       --namespace <ns>
   ```

   For deeper worker-level insights, use `temporal worker describe` to see individual worker status, build IDs, and deployment info:

   ```bash
   temporal worker describe \
       --task-queue <q> \
       --namespace <ns>
   ```

   If no recent pollers (`LastAccessTime` aged out after 5 minutes per [worker-health.md → What "no pollers" looks like](worker-health.md#what-no-pollers-looks-like)), stop here and route to worker-health.md. If `describe` itself fails, back off to [connectivity.md](connectivity.md), [certificates.md](certificates.md), [authentication.md](authentication.md), or [rate-limits.md](rate-limits.md).

3. **Read the pending sections on `describe`.** Per [workflow-stuck.md → What to look at first](workflow-stuck.md#the-primary-inspection-command-temporal-workflow-describe), the partitioning checks after status are: which pending sections are present (`Pending Activities`, `Pending Child Workflows`, `Pending Nexus Operations`, `pendingWorkflowTask`), and whether `historyLength` is climbing between successive describes.

4. **Export the Event History if you need the last meaningful event.** Command form from [workflow-stuck.md → Inspecting the Event History: `temporal workflow show`](workflow-stuck.md#inspecting-the-event-history-temporal-workflow-show):

   ```bash
   temporal workflow show --workflow-id order-1234 --namespace <ns> --output json > history.json
   ```

   To locate the scheduling event with no matching terminal event, follow [workflow-stuck.md → Finding the last meaningful event](workflow-stuck.md#inspecting-the-event-history-temporal-workflow-show). That section warns that `ActivityTaskStarted` is only written *with* its terminal event — so a gap between `ActivityTaskScheduled` and a terminal event does not imply the Activity is unpicked. Read the Pending Activities block on `describe` for retry state.

5. **Classify and route.** Map the evidence to the owning section:

   | Evidence on `describe` / history | Route |
   |---|---|
   | Pending Activity, attempts climbing, `LastAttemptFailure` present | [workflow-stuck.md → Pending activities](workflow-stuck.md#pending-activities) |
   | Pending Activity, no attempts yet, only `ActivityTaskScheduled` in history | [worker-health.md → What "no pollers" looks like](worker-health.md#what-no-pollers-looks-like) (back to step 2) |
   | Pending Child Workflow | [workflow-stuck.md → Pending child workflows](workflow-stuck.md#pending-child-workflows) — recurse into the child |
   | Waiting on a Signal that never arrives | [workflow-stuck.md → Pending signals, cancellations, and updates](workflow-stuck.md#pending-signals-cancellations-and-updates) |
   | Pending Nexus Operation, `State: Blocked` or `BackingOff` | [workflow-stuck.md → Pending Nexus Operations](workflow-stuck.md#pending-nexus-operations) |
   | `pendingWorkflowTask.attempt` > 1 and `WorkflowTaskFailed` events accumulating | [workflow-stuck.md → Pending Workflow Task and WorkflowTaskFailed loops](workflow-stuck.md#pending-workflow-task-and-workflowtaskfailed-loops); if cause is Nondeterminism, [non-determinism.md](non-determinism.md) |
   | Last non-bookkeeping event is `TimerStarted` with a future fire time | [workflow-stuck.md → Timer-based waits](workflow-stuck.md#timer-based-waits) — not stuck |

6. **Apply recovery.** Use the commands in [workflow-stuck.md → Recovery commands](workflow-stuck.md#recovery-commands):
   - Waiting on a Signal that was never sent: `temporal workflow signal` with the correct name and Workflow ID.
   - Long-running Activity wedged without heartbeat: `temporal activity pause` / `unpause` / `reset`.
   - Reset past a bad deploy: `temporal workflow reset --event-id <id-before-divergence>` (valid reset points are `WorkflowTaskStarted`, `WorkflowTaskCompleted`, `WorkflowTaskTimedOut`, `WorkflowTaskFailed`).
   - Unrecoverable: `temporal workflow terminate --reason <reason>`.

7. **Verify.** Re-run step 1; new events should be arriving, or the Workflow should be Closed as intended.

**Confidence:** high when the pending-section evidence and the last meaningful event agree on a single route. Drop confidence when step 2 passes (fresh pollers) but the history still shows only `ActivityTaskScheduled` with no terminal event and no retry attempts — per [workflow-stuck.md → Pending activities](workflow-stuck.md#pending-activities), that mismatch hints at a Task Queue name / Build ID routing issue rather than a missing-pollers outage. (Confidence framing is a skill convention; see [runtime-errors.md](runtime-errors.md#why-these-errors-are-hard).)

## Cert expired, workers offline

**Page text:** "Workers across the fleet disconnected overnight. Logs repeat `x509: certificate has expired or is not yet valid`."

**Goal:** rotate to a valid cert without cutting live traffic; remove the expired trust material only after the new path is verified.

**Steps:**

1. **Confirm the failure is TLS-layer cert expiry.** Reproduce the handshake from an affected host using the canonical `openssl s_client` form in [certificates.md → openssl recipes → Test a live endpoint](certificates.md#openssl-recipes):

   ```bash
   openssl s_client -connect <namespace>.<account>.tmprl.cloud:7233 \
       -servername <namespace>.<account>.tmprl.cloud \
       -showcerts -cert client.pem -key client.key \
       -tls1_2 </dev/null
   ```

   `Verify return code: 10 (certificate has expired)` or client-side `x509: certificate has expired or is not yet valid` confirms the layer-3 diagnosis; full interpretation in the [Handshake failure table](certificates.md#handshake-failure). Rule out clock skew first (`date -u`) per [certificates.md → Expired or not-yet-valid](certificates.md#expired-or-not-yet-valid).

2. **Identify whether the CA or only the leaf expired.** Commands from [certificates.md → openssl recipes → Inspect a local cert](certificates.md#openssl-recipes):

   ```bash
   openssl x509 -enddate -noout -in client.pem
   openssl x509 -enddate -noout -in ca.pem
   ```

   CA still valid → regenerate only the leaf. CA itself expired → upload a new CA before any client can reconnect; an expired root invalidates all downstream certs per [certificates.md → Expired or not-yet-valid](certificates.md#expired-or-not-yet-valid).

3. **Leaf-only rotation (CA still valid).** Canonical `tcld` form is in [certificates.md → openssl recipes → Issue a new leaf with tcld](certificates.md#openssl-recipes):

   ```bash
   tcld generate-certificates end-entity-certificate \
       --organization <org> \
       --validity-period 364d \
       --ca-certificate-file ca.pem --ca-key-file ca.key \
       --certificate-file new-certs/client.pem --key-file new-certs/client.key
   # Command and modifiers:
   ```

   Distribute `new-certs/client.pem` and `new-certs/client.key` to workers via the existing secret-distribution path. Restart workers. Skip to step 6.

4. **CA + leaf rotation (CA expired or rolling over).** Use the zero-downtime pattern documented in [certificates.md → Rotation and expiry notifications](certificates.md#rotation-and-expiry-notifications):

   ```bash
   # New CA — default is ECDSA P-384; add --rsa to switch to RSA 4096
   tcld generate-certificates certificate-authority-certificate \
       --organization <org> \
       --validity-period 1y \
       --ca-certificate-file new-ca/ca.pem --ca-key-file new-ca/ca.key
   # Command and modifiers:

   # Add the new CA to the Namespace *before* removing the old one.
   # Full flag set in certificates.md → Accepted client CA set.
   tcld namespace accepted-client-ca add \
       --namespace <namespace>.<account> \
       --ca-certificate-file new-ca/ca.pem

   # New leaf signed by the new CA
   tcld generate-certificates end-entity-certificate \
       --organization <org> \
       --validity-period 364d \
       --ca-certificate-file new-ca/ca.pem --ca-key-file new-ca/ca.key \
       --certificate-file new-certs/client.pem --key-file new-certs/client.key
   ```

   For a bundle-based rollover (concat old + new, then later new-only) use `tcld namespace accepted-client-ca set` as documented in [certificates.md → Accepted client CA set (mTLS Cloud)](certificates.md#accepted-client-ca-set-mtls-cloud).

5. **Verify the chain locally before distribution** — see [certificates.md → openssl recipes → Verify a chain](certificates.md#openssl-recipes):

   ```bash
   openssl verify -CAfile new-ca/ca.pem new-certs/client.pem   # expect: OK
   ```

   If this fails locally it will fail at the peer. Do not distribute.

6. **Distribute and confirm workers reconnect.** Push new leaf (and new CA if rotated) to the worker secret store and restart. Re-probe a critical queue per [worker-health.md → Inspecting a Task Queue with `temporal task-queue describe`](worker-health.md#inspecting-a-task-queue-with-temporal-task-queue-describe):

   ```bash
   temporal task-queue describe \
       --task-queue <critical-queue> \
       --namespace <namespace>.<account>
   ```

   Fresh pollers with recent `LastAccessTime` values mean the new credentials are accepted — see the interpretation matrix in that section.

7. **Remove the old CA only after everything is green.** List first, then remove by fingerprint (safer than by PEM); `--fp` is the alias for `--ca-certificate-fingerprint`:

   ```bash
   tcld namespace accepted-client-ca list --namespace <namespace>.<account>
   # Command:

   tcld namespace accepted-client-ca remove \
       --namespace <namespace>.<account> \
       --fp <old-ca-fingerprint>
   # Command:
   # --ca-certificate-fingerprint / --fp:
   ```

   Get the fingerprint with `openssl x509 -in old-ca.pem -noout -fingerprint` (see [certificates.md → openssl recipes](certificates.md#openssl-recipes)).

8. **Post-incident.** Cloud sends "Certificate Expiring in 15 days" notifications per [certificates.md → Rotation and expiry notifications](certificates.md#rotation-and-expiry-notifications); verify recipients are current and add an internal `openssl x509 -enddate` cron against the certs in use.

**Confidence:** high once step 1 prints an expiry matching the incident, step 5 returns `OK`, and step 6 shows fresh pollers. If pollers are still stale after redeploy, peel the wrapped cause: `UNAVAILABLE` with a `tls:` cause is still layer 3; `UNAUTHENTICATED` after a clean handshake is a post-TLS rejection (certificate filter or role) — route to [authentication.md → mTLS authentication after TLS completes](authentication.md#mtls-authentication-after-tls-completes).

## Task-queue backlog mystery

**Page text:** "Task queue `payments-v2` has a growing backlog. Workers report as up."

**Goal:** decide whether the backlog is a worker-polling problem, a versioning / Build ID routing problem, an auth or rate-limit regression, or a genuine capacity shortfall.

**Steps:**

1. **Read the Task Queue statistics and poller list** — one call, interpretation matrix in [worker-health.md → Inspecting a Task Queue](worker-health.md#inspecting-a-task-queue-with-temporal-task-queue-describe):

   ```bash
   temporal task-queue describe --task-queue payments-v2 --namespace <ns>
   ```

   The statistics block (`ApproximateBacklogCount`, `ApproximateBacklogAge`, `TasksAddRate`, `TasksDispatchRate`, `BacklogIncreaseRate`) quantifies how fast the queue is growing; the pollers block covers no pollers, stale `LastAccessTime`, and identity mismatches.

2. **No pollers** → [worker-health.md → What "no pollers" looks like](worker-health.md#what-no-pollers-looks-like). Recipe ends.

3. **If pollers look fine, check Build ID / versioning routing.** Re-run `describe` with versioning flags per [worker-health.md → Reachability and versioning](worker-health.md#inspecting-a-task-queue-with-temporal-task-queue-describe):

   ```bash
   temporal task-queue describe --task-queue payments-v2 --namespace <ns> \
       --select-build-id "<current-build-id>" --report-reachability
   ```

   If the Build ID Workflows route to is not listed as reachable (e.g. a decommissioned cohort), tasks are being sent to a version that no longer has Workers. worker-health.md also covers the Worker-Deployments alternative `temporal worker deployment describe-version`.

4. **Scan worker logs for layer regressions.** Routing table in [worker-health.md → Worker log signatures](worker-health.md#worker-log-signatures):

   | Worker log shape | Route |
   |---|---|
   | gRPC `UNAUTHENTICATED` / `PERMISSION_DENIED` | [authentication.md](authentication.md) |
   | gRPC `RESOURCE_EXHAUSTED` | [rate-limits.md → Identifying which limit was hit](rate-limits.md#identifying-which-limit-was-hit) |
   | `x509:` / `tls:` | [certificates.md](certificates.md) |
   | Repeating `WorkflowTaskFailed` on one Workflow | Poison task — see step 5 |

5. **Check for a poison task.** If the same Workflow keeps failing its WFT, read its history per [workflow-stuck.md → Pending Workflow Task and WorkflowTaskFailed loops](workflow-stuck.md#pending-workflow-task-and-workflowtaskfailed-loops). If the cause is Nondeterminism, escalate to the non-determinism recipe below.

6. **Pollers fresh, no auth/rate-limit/poison signals, schedule-to-start latency high** → the ceiling is the Worker, not the server. See [worker-health.md → Schedule-to-start latency](worker-health.md#schedule-to-start-latency) and [→ Worker task slots](worker-health.md#worker-task-slots). Sizing / tuning lives in `skill-temporal-deploy`; this skill has done its job by proving the earlier layers healthy.

**Confidence:** high if one signal from steps 3–5 fires and matches the backlog's start time. Low if steps 1–5 are all clean — that pattern is almost always "not enough workers," and worker-health.md flags it: low Poll Success Rate + low schedule-to-start latency + low host utilization can even indicate *too many* Workers (see [worker-health.md → Cloud Namespace-level poller limits](worker-health.md#cloud-namespace-level-poller-limits)).

## Non-determinism caught in prod

**Page text:** "Workers log repeated non-determinism errors. Workflow `reconcile-9999` has many `WorkflowTaskFailed` events in a row."

**Goal:** confirm the WFT-failure cause is Nondeterminism, reproduce locally against the right source commit, and pick a remediation path.

**Steps:**

1. **Confirm the cause is Nondeterminism.** Export the history with the form from [workflow-stuck.md → Inspecting the Event History](workflow-stuck.md#inspecting-the-event-history-temporal-workflow-show), then follow [non-determinism.md → Identifying ND from the Event History](non-determinism.md#identifying-nd-from-the-event-history) to inspect each `WorkflowTaskFailed` event's `workflowTaskFailedEventAttributes.cause`:

   ```bash
   temporal workflow show --workflow-id reconcile-9999 --namespace <ns> --output json > history.json
   ```

   The cross-SDK cause value is "Nondeterminism" on the `WorkflowTaskFailedCause` enum. If the cause is something else, route via [workflow-stuck.md → Pending Workflow Task and WorkflowTaskFailed loops](workflow-stuck.md#pending-workflow-task-and-workflowtaskfailed-loops).

2. **Capture the worker error text.** Per [non-determinism.md → Per-SDK error shape](non-determinism.md#per-sdk-error-shape), only TypeScript has a doc-pinned class (`DeterminismViolationError`); other SDKs emit per-SDK errors. The message usually names the offending Command vs. expected Event — that's what pins the divergence.

3. **Reproduce locally against the *deployed* commit** (not `main`) — per [replay.md → Prerequisites](replay.md#prerequisites), replaying newer source against an older recording can produce divergence for a different reason than the bug being triaged.

   - **Interactive (TypeScript only):** VS Code extension — [replay.md → The VS Code extension](replay.md#the-vs-code-extension-typescript-only-interactive). Point it at `history.json`.
   - **Headless / CI (any supported SDK):** SDK replayer — [replay.md → Step 2](replay.md#step-2--run-the-sdk-replayer-all-supported-sdks). For Go/Java, set `TEMPORAL_DEBUG=true` while stepping ([replay.md → TEMPORAL_DEBUG](replay.md#temporal_debug-suppress-the-deadlock-detector-while-stepping)).

   Interpret per [replay.md → Interpreting a replay that diverges](replay.md#interpreting-a-replay-that-diverges) / [→ succeeds](replay.md#interpreting-a-replay-that-succeeds). Replay against the deployed commit fails with the same error → diagnosis stands. Replay succeeds → deployed Workers are on different code; find them before fixing.

4. **Identify the change.** Diff the deployed commit against the previous known-working commit. Canonical divergence shapes are listed in [non-determinism.md → What the docs call out as ND-inducing patterns](non-determinism.md#what-the-docs-call-out-as-nd-inducing-patterns) — command-order changes, Activity name changes, Timer-duration changes to/from zero (per-SDK), and intrinsic ND (random branches, map iteration order, wall-clock reads).

5. **Pick a remediation path** from [non-determinism.md](non-determinism.md):

   | Situation | Remediation |
   |---|---|
   | Worker Versioning already in place and this Workflow Type can be pinned going forward | [→ Worker Versioning (preferred)](non-determinism.md#remediation-worker-versioning-preferred). Adopting Versioning mid-incident does not fix already-looping Workflows. |
   | In-flight Workflows must complete under both old and new behavior | [→ per-SDK patching](non-determinism.md#remediation-per-sdk-patching) — `GetVersion` / `patched` branch. SDK API details in `skill-temporal-developer`. |
   | Bad commit cleanly revertible, divergences not yet widespread | [→ Fix the Worker code and redeploy](non-determinism.md#remediation-fix-and-redeploy-or-reset-past-the-divergence) — revert, let the server-side WFT-retry loop succeed on new Workers. |
   | Workflows already wedged past the divergence | [→ Reset the Workflow past the divergence](non-determinism.md#remediation-fix-and-redeploy-or-reset-past-the-divergence) — `temporal workflow reset --event-id <last-good-WorkflowTaskCompleted>`. Valid reset points: `WorkflowTaskStarted`, `WorkflowTaskCompleted`, `WorkflowTaskTimedOut`, `WorkflowTaskFailed`. Confirm with the business owner — events after the reset point are re-executed. |

6. **Verify.** Local replay of the failing history should now succeed. After deploy, re-run `temporal workflow describe`; `pendingWorkflowTask.attempt` should stop climbing and new non-bookkeeping events should arrive.

7. **Post-incident: add a replay regression test.** Put each production history into a bulk replayer in CI (`WorkflowReplayer.replayWorkflowExecutions` / `Worker.runReplayHistories` / `Replayer.replay_workflows`) per [replay.md → Step 2](replay.md#step-2--run-the-sdk-replayer-all-supported-sdks), so the next regression fails CI.

**Confidence checkpoints:**
- After step 1: high that it's ND *iff* the JSON inspection returns the Nondeterminism cause on at least one `WorkflowTaskFailed` event. Without that, do not prescribe patching or reset — the WFT is failing for a different reason.
- After step 3: if local replay reproduces against the deployed commit, high that the deployed code is the cause. If replay *succeeds* against that commit, the deployed Workers are on different code; find the real build before picking a remediation.

See the whole-stack picture in [diagnostic-ladder.md](diagnostic-ladder.md).
