---
name: circleci-config
description: Optimize CircleCI configuration for speed, reliability, and maintainability. Use when users ask to improve `.circleci/config.yml`, reduce CI runtime, tune caching/workspaces/parallelism, remove pipeline waste, or fix flaky pipeline behavior caused by configuration choices.
---

# CircleCI Config

## Overview

Use this skill to improve CircleCI performance and stability without changing product behavior. Focus on measured bottlenecks first, then implement the smallest safe config changes with clear validation criteria.

Read `references/cache-optimization.md` when the request involves `save_cache`, `restore_cache`, `persist_to_workspace`, `attach_workspace`, cache key design, dependency caching, lockfiles, or complaints about low cache hit rates, oversized caches, or wasted persistence steps.
Read `references/persisting-data.md` when the request involves choosing between caches, workspaces, and artifacts, or when data is being moved between jobs inefficiently.
Read `references/test-results-and-splitting.md` when the request involves slow test jobs, parallelism, flaky test visibility, missing JUnit XML, or `circleci tests run`.
Read `references/patterns.md` when the request involves approvals, branch/tag filters, schedules, deploy flow structure, or environment promotion patterns.

## Inputs To Gather

- `.yaml` and `.yml` files in `.circleci/` and any reusable config fragments
- Current pain points: duration, flakiness, cost, or maintainability
- Baseline metrics: slowest jobs, most frequent retries/failures, queue and run times
- Risk tolerance for structural changes

## Workflow

1. Build a baseline.
   - Identify top 1-3 longest jobs and top flaky jobs.
   - Capture before metrics (duration, pass rate, retries).
2. Remove pipeline waste.
   - Eliminate duplicate jobs/workflows.
   - Tighten branch/tag filters and workflow triggers.
3. Improve dependency and artifact flow.
   - Fix cache keys to include deterministic lockfile checks.
   - Use workspaces/artifacts to avoid rebuilding identical outputs.
   - Prefer cache scopes that are narrow, reproducible, and cheap to restore.
4. Apply safe parallelism.
   - Parallelize only proven bottlenecks.
   - Keep fan-out/fan-in readable and deterministic.
5. Validate impact.
   - Define expected metric changes and acceptance criteria before finalizing.

## Guardrails

- Prefer configuration fixes before proposing application code changes.
- Do not add blanket retries to hide deterministic failures.
- Preserve deployment safety gates while optimizing build/test stages.
- Keep changes incremental and easy to revert.
- Prefer language-specific cache directories over broad project snapshots.
- Avoid cache keys that rotate every run unless the user explicitly wants effectively write-only caches.

## Output Contract

Provide:

1. Baseline bottleneck summary.
2. Proposed or applied config changes with rationale.
3. Expected runtime/reliability impact.
4. Validation plan and rollback note.
