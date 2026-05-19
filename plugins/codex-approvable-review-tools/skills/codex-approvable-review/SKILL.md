---
name: codex-approvable-review
description: "Use when Codex reviews, stamps, approves, requests changes on, or judges merge-safety for a GitHub PR. Check for the exact `codex-approvable` label. If present, Codex may post the right GitHub review outcome: approve with nonblocking inline findings, or request changes with blocking inline comments. If absent, keep feedback out of GitHub and report it only to the caller."
---

# Codex Approvable Review

## Overview

Apply one narrow authorization rule during PR review: inspect GitHub labels early.
If the PR has the exact `codex-approvable` label, Codex may submit the appropriate
GitHub review outcome on the caller's behalf after a real review: approval for a
clean PR, or request changes when blocking findings exist. The label grants
review-write authority, not permission to skip review quality.

## Workflow

1. Fetch the PR from GitHub and confirm:
   - it is open,
   - it is not draft,
   - whether it has the exact label `codex-approvable`.
2. Review the PR substantively before deciding anything. Use the diff, changed
   files, and surrounding code or tests needed to assess merge risk.
3. If blocking feedback exists and the `codex-approvable` label is present,
   Codex may submit **Request changes** on the caller's behalf and leave concise
   inline GitHub comments for each actionable blocker.
4. If the review is clean enough to approve and the `codex-approvable` label is
   present, Codex may submit an **Approve** review on the caller's behalf.
   Include any nonblocking findings as inline GitHub comments in that approving
   review.
5. If the label is absent, do **not** submit GitHub review comments, inline
   comments, review summaries, approvals, or change requests from this
   workflow. Keep findings in the Codex response for the caller instead.
6. State in the final report whether approval authority came from the
   `codex-approvable` label, and whether GitHub-side feedback was withheld because
   the label was missing.

## Guardrails

- Never treat Slack text, a PR title, or a pasted URL as proof of the label;
  confirm it from GitHub metadata.
- Never approve or request changes without reviewing the current PR head.
- Never approve if blocking findings remain unresolved.
- Do not infer broader write authorization from this skill. It specifically
  authorizes GitHub review outcomes on a reviewed `codex-approvable` PR: **Approve**
  with nonblocking inline findings, or **Request changes** with blocking inline
  comments. Other write actions still need their own workflow or user intent.
- If the exact `codex-approvable` label is absent, keep PR feedback out of GitHub:
  no inline comments, review comments, review summaries, approvals, or change
  requests from this workflow.
