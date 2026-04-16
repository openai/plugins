# Persisting Data Reference

Use this reference when deciding whether data belongs in a cache, workspace, or artifact, or when a pipeline is moving too much data between jobs.

Sources:
- [Persisting data overview](https://circleci.com/docs/guides/optimize/persist-data/)
- [Artifacts guide](https://circleci.com/docs/guides/optimize/artifacts/)
- [CircleCI concepts: data persistence](https://circleci.com/docs/guides/about-circleci/concepts/)

## Choose The Right Mechanism

- Use caches for non-vital data that speeds up future runs, such as package-manager download stores.
- Use workspaces for data that must move between jobs in the same workflow.
- Use artifacts for outputs that humans need to inspect after the job completes, such as reports, screenshots, logs, packages, or coverage HTML.

## Decision Rules

- If later jobs must execute with the data, prefer a workspace.
- If later pipelines may benefit from the data but correctness does not depend on it, prefer a cache.
- If the data is for debugging, audit, or download after the run, prefer artifacts.
- If the same files are both attached as a workspace and uploaded as artifacts, make sure each path has a distinct purpose.

## Workspace Guidance

- Keep persisted paths narrow. `attach_workspace` recreates the entire attached content, so oversized workspaces can become a major tax.
- Workspaces are additive-only within a workflow. Downstream jobs receive the union of upstream layers.
- When upstream jobs run concurrently, layer application order is undefined.
- If concurrent jobs persist the same filename, attaching the workspace can fail.
- Use workspaces for handoff data, not as a generic scratch backup of the project root.

## Artifact Guidance

- Upload raw test XML, screenshots, core dumps, deploy bundles, and other inspection-oriented outputs as artifacts.
- Prefer storing debugging artifacts on failure paths or only for the jobs that need them.
- Use artifacts to debug test metadata setup, especially when `store_test_results` is present but CircleCI features are not behaving as expected.

## Cache Guidance

- Cache only data that is safe to lose and cheap to reuse.
- Prefer language/tool download stores rather than broad build directories.
- Do not use caches as the primary handoff mechanism between jobs in the same workflow.

## Smells To Flag

- Persisting the project root to a workspace without a clear downstream need.
- Attaching a workspace in jobs that only use fresh checkout output.
- Uploading large artifacts that nobody inspects or downloads.
- Using both cache and workspace for the same dependency tree without a clear reason.
- Using artifacts as an input to later jobs instead of a workspace.

## Common Fixes To Suggest

- Replace oversized workspaces with a smaller list of exact directories or files.
- Replace workspace usage with artifacts when the data is only for inspection.
- Replace workspace usage with caches when the goal is speeding up future workflows rather than handing off exact outputs.
- Remove duplicate persistence where the same output is saved in more than one mechanism without a distinct consumer.
