---
name: daily-slack-approvable-review
description: Scan user-specified Slack channels over the last 24 hours for open, unapproved GitHub PRs carrying the `codex-approvable` label, review them, compose with `codex-approvable-review` for labeled GitHub review-write authority, and either act in GitHub or return a report-only queue. Use when a user wants Codex to triage Slack-surfaced codex-approvable PRs, post review outcomes when clearly asked, or dry-run the queue first.
---

# Daily Slack Codex Approvable Review

## Overview

Turn a small set of Slack channels into a review queue for pull requests labeled
`codex-approvable`. Read Slack as evidence, use GitHub as the source of truth for PR
state and labels, use `deep-code-review` for the substantive review pass when
possible, compose with `codex-approvable-review` for labeled GitHub
review-write authority, then either leave the matching GitHub review outcome or
return a report-only preview.

## Required Inputs

- Require one or more Slack channel names, IDs, or links.
- Use a rolling 24-hour window anchored to the current time unless the user says
  otherwise.
- Treat Slack as read-only. Do not post to Slack unless the user explicitly asks.

## Operating Modes

Choose the lightest mode that satisfies the user's wording:

- **Action mode**: Use only when the user explicitly asks to approve, request
  changes, stamp, review-and-post, or otherwise perform GitHub write actions.
  In this mode, review eligible PRs and submit GitHub review decisions.
- **Report-only mode**: Use when the user asks to scan, triage, preview, dry-run,
  summarize, or inspect without clearly requesting GitHub writes. In this mode,
  gather candidates, review them, and report the approval recommendation without
  posting any GitHub review state or inline comments.

If the request is ambiguous, prefer report-only mode rather than mutating PR
state unexpectedly.

## Workflow

### 1. Build the Slack candidate set

1. Load the Slack capability needed to read the requested channels and nearby
   thread context.
2. Search each requested channel for messages from the last 24 hours.
3. Inspect both parent messages and relevant thread replies when the Slack tool
   exposes them, so PR links hidden in discussion threads are not missed.
4. Extract and deduplicate GitHub pull request URLs.
5. Preserve provenance for each candidate: Slack channel, message/thread link,
   and the timestamp that surfaced it.

### 2. Confirm the PR queue in GitHub

For every deduplicated PR URL:

1. Fetch GitHub PR metadata, changed files, current head SHA, review decision,
   labels, and existing review/comment history.
2. Keep only PRs that are:
   - open,
   - not draft,
   - not already approved,
   - labeled with the exact GitHub label `codex-approvable`.
3. Skip and report PRs that are closed, merged, draft, already approved, missing
   permission, or missing the `codex-approvable` label.
4. Avoid duplicate review spam. If the acting reviewer already submitted an
   approval or request-changes review on the current head SHA, report that state
   instead of posting another equivalent review.

### 3. Review each eligible PR

Use the PR diff and PR-head code as the review source of truth.

1. Prefer to materialize each PR diff in an isolated local checkout or worktree
   when that can be done safely without disturbing the user's active branch.
2. When a safe local diff is available, invoke `deep-code-review` for that PR so
   the review uses its three-pass workflow and final synthesis.
3. If `deep-code-review` cannot be used faithfully because there is no safe local
   PR diff or delegation is unavailable, do not pretend it ran. Perform the best
   available direct review from the remote diff, state that fallback in the final
   report, and do not overstate confidence.
4. Reconcile review findings with existing PR comments so you do not duplicate
   already-raised issues.

### 4. Classify findings and submit the GitHub review

Use practical merge risk, not style preference, to decide the review outcome.

Blocking feedback includes correctness bugs, security or privacy risk, meaningful
regressions, broken contracts, unsafe data handling, or missing validation/tests
that materially increase merge risk.

Non-blocking feedback includes small cleanup, readability, naming, or minor test
suggestions that do not need to block merge.

Then branch by mode:

- In **action mode**:
  - Apply `$codex-approvable-review` for labeled GitHub review-write authority. Do not
    restate or weaken that policy here.
  - If there is no blocking feedback:
    - submit an **Approve** review,
    - leave concise inline comments for worthwhile nits,
    - keep any approval body brief and factual.
  - If there is blocking feedback:
    - submit **Request changes**,
    - leave concise inline comments for each actionable blocker,
    - avoid padding the review with non-actionable commentary.
- In **report-only mode**:
  - do not submit GitHub review state,
  - do not leave inline comments,
  - report the recommended outcome as `would approve`, `would request changes`,
    or `insufficient confidence`.

If review evidence is incomplete enough that approving or requesting changes
would be irresponsible, do not post either state. Report the PR as blocked on
insufficient review confidence.

### 5. Report back to the user

Return a compact per-PR recap with:

- One opening summary line with totals for discovered PR links, eligible PRs,
  reviews posted or recommendations produced, skipped PRs, and blocked PRs
- PR link, repo/number, and title
- Slack provenance that surfaced it
- Review mode used: `deep-code-review` or fallback direct review
- Execution mode used: action or report-only
- Outcome: approved, request-changes, would-approve, would-request-changes,
  skipped, or blocked
- Whether inline comments were left
- Final GitHub approval/request-changes state
- Whether GitHub review-write authority came from the `codex-approvable` policy
- One-line reason for any blocker, skip, or caveat

Prefer a short table followed by only the high-signal caveats.

## Success Criteria

Treat the run as successful only when it:

- searches every requested Slack channel for the full intended window,
- classifies every surfaced PR link as eligible, skipped, or blocked,
- produces one substantiated outcome for every eligible PR,
- writes to GitHub only in action mode and never duplicates current-head reviews,
- reports enough context to audit the run without reopening Slack or GitHub.

## Guardrails

- Never infer PR state or labels from Slack previews alone; confirm with GitHub
  metadata.
- Never approve a PR that was not actually reviewed.
- If `$codex-approvable-review` cannot be applied, do not auto-approve or request changes
  on an inferred or duplicated local policy; report that the composed review
  policy was unavailable.
- Never mutate GitHub review state unless the user's request clearly authorizes
  write actions.
- Never claim `deep-code-review` ran unless its workflow really executed.
- Never duplicate comments that are already present and still applicable.
- Prefer inline GitHub comments over vague top-level review prose when feedback
  can be anchored to code.
- If authentication or connector coverage is missing, stop before write actions
  and report exactly what could not be completed.
