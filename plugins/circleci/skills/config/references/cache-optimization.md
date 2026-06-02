# Cache Optimization Reference

Use this reference when improving CircleCI dependency caching, cache keys, or cache ROI.

Source: [CircleCI docs, "Caching strategies"](https://circleci.com/docs/guides/optimize/caching-strategy/)

## Goals

- Aim for high cache ROI: CircleCI recommends roughly 10x-20x restored bytes versus saved bytes.
- Prefer caches that improve repeat runs without creating stale or branch-crossing dependency problems.
- Keep caches small enough that restore/save time does not cancel out the benefit.

## Default Recommendations

- Prefer lockfile-based keys such as `{{ checksum "package-lock.json" }}` or `{{ checksum "yarn.lock" }}`.
- Add a manual version prefix like `v1-...` so the cache can be invalidated intentionally.
- Split unrelated directories into separate caches instead of storing many paths under one key.
- Reorder workflows or combine similar jobs when parallel jobs would all save the same cache independently.
- Cache expensive compiled outputs only when rebuild cost is significant and the cache input is deterministic.

## Key Design Rules

- Avoid overly strict keys that only hit once, such as commit-SHA keys.
- Avoid effectively write-only keys such as `{{ epoch }}`.
- Recommend avoiding the `.Revision` template unless the user is explicitly trying to cache source code snapshots or another per-revision artifact.
- Prefer stable prefixes plus lockfile checksums over templates that change every pipeline.
- When a dependency manager supports it safely, start with one exact key and add fallback keys only if misses are proving expensive.

## Partial Restore Guidance

- Treat partial restore keys as a tradeoff, not a default.
- Some dependency managers handle partial restores well; others can install on top of stale trees and create confusing failures.
- If partial restores are risky for the ecosystem in question, prefer a single exact versioned key first.
- If you do use fallback keys, keep the search scope narrow enough to avoid restoring incompatible dependencies from unrelated branches or toolchain versions.

## Node Guidance

### `npm ci`

- When the workflow uses `npm ci`, suggest caching `~/.npm` instead of `node_modules`.
- Rationale: `npm ci` deletes `node_modules` before installing, so caching `node_modules` usually adds transfer time without improving correctness or speed.
- Favor keys like `v1-npm-{{ checksum "package-lock.json" }}`.
- Include Node or npm version in the version prefix when toolchain upgrades frequently cause invalid caches.

Example:

```yaml
- restore_cache:
    keys:
      - v1-npm-{{ checksum "package-lock.json" }}
- run: npm ci
- save_cache:
    key: v1-npm-{{ checksum "package-lock.json" }}
    paths:
      - ~/.npm
```

### Yarn

- Cache the package-manager cache directory, not the whole dependency tree, unless the project has measured evidence to justify something broader.
- Prefer an explicit cache folder so the saved path matches the install command.

Example:

```yaml
- restore_cache:
    keys:
      - v1-yarn-{{ checksum "yarn.lock" }}
- run: yarn --frozen-lockfile --cache-folder ~/.cache/yarn
- save_cache:
    key: v1-yarn-{{ checksum "yarn.lock" }}
    paths:
      - ~/.cache/yarn
```

## Review Checklist

- Is the cache path the package manager's reusable download/store directory?
- Does the key change when declared dependencies change?
- Is there a clear reason for every cached path?
- Would a workspace or artifact be a better fit than a cache?
- Are multiple jobs redundantly saving the same cache?
- Is the restore/save time likely to pay back over repeated runs?

## Unused Persistence Audit

- Look for `save_cache` steps whose cached paths are never read by later commands in the same job or by restored paths in later jobs.
- Look for `restore_cache` steps that restore directories no subsequent install, build, or test command actually touches.
- Look for `persist_to_workspace` paths that no downstream job consumes after `attach_workspace`.
- Look for `attach_workspace` steps that mount data which no later command reads, copies, or executes.
- Treat these as pipeline waste first, not as harmless redundancy: they cost time on every run even when they do not change behavior.

## Detection Heuristics

- Trace each cached or persisted path to a concrete later consumer command.
- If a path is restored but the job still performs a clean install into a different location, the restore is probably dead weight.
- If a workspace is attached at one directory but later steps only use freshly checked-out source or regenerated outputs, the attach is probably unnecessary.
- If multiple jobs persist the same build output and only one downstream job reads it, simplify the fan-out or persist once.
- Be skeptical of broad paths like the project root, `node_modules`, build directories, or home-directory globs unless a later step clearly depends on them.

## Fix Patterns For Unused Data Movement

- Remove `restore_cache` when no later step reads the restored path.
- Remove `save_cache` when the matching restore path is unused or when the key almost never hits.
- Replace broad workspace persistence with the smallest directories actually consumed downstream.
- Replace workspace transfers with artifacts only when the data is for inspection rather than downstream execution.
- Move shared build outputs into one upstream producer job and attach them only in the jobs that actually consume them.

## Common Fixes To Suggest

- Replace `{{ epoch }}`, commit SHA, or similarly strict keys with versioned lockfile checksums.
- Replace broad multi-directory caches with smaller per-tool caches.
- Move repeated build outputs to workspaces when they are passed within one workflow.
- Remove caches that are rarely hit or cost more to restore than to recreate.
- Remove cache/workspace save and restore steps that do not feed any later command.
