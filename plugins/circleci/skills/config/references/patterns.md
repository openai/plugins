# Config Patterns Reference

Use this reference when reviewing or designing common CircleCI workflow and deploy patterns such as approval gates, branch/tag filters, scheduled workflows, and release routing.

Sources:
- [Workflow orchestration](https://circleci.com/docs/workflows/)
- [Configuration reference](https://circleci.com/docs/reference/configuration-reference/)
- [Using branch filters](https://circleci.com/docs/using-branch-filters/)
- [Dynamic configuration overview](https://circleci.com/docs/dynamic-config)

## Common Workflow Patterns

### Build-Test-Approve-Deploy

- Use a normal build/test chain for validation.
- Insert a `type: approval` job before production deploys.
- Treat approval as orchestration only; the real deploy authorization should still come from the downstream job's context and permissions.

### Mainline Staging, Tagged Production

- Run build/test on branches such as `main`.
- Auto-deploy to staging from the validated mainline path.
- Trigger production deploys from version tags so the release event is explicit and auditable.

### Scheduled Maintenance Or Nightly Workflows

- Use schedule triggers for nightly or periodic tasks.
- Restrict scheduled workflows with branch filters or workflow `when` conditions so only the intended workflow runs.
- Prefer pipeline parameters or workflow conditionals when one config supports several scheduled routines.

### Dynamic Or Conditional Workflows

- Use workflow `when` or expression-based filters when the work should depend on branch, tag, trigger source, or parameters.
- Consider dynamic configuration when static YAML creates too many mostly-idle workflows or duplicated job graphs.

## Filters And Release Routing

- Put branch/tag execution rules in workflows, not legacy job-level branching.
- Regex filters must match the full branch or tag string.
- CircleCI does not run workflows for tags unless tag filters are declared explicitly.
- If a tag-filtered job requires upstream jobs, those upstream jobs also need compatible tag filters.
- Use narrow filters so deploy or publish jobs only run on the exact release routes intended.

## Approval And Promotion Guidance

- Approval jobs can have any name and exist only in the workflow graph.
- Keep approvals close to the sensitive action they gate.
- Pair production deploy jobs with restricted contexts or environment-specific secrets, not approval alone.
- Prefer explicit environment promotion paths over rebuilding separately for each environment when the same artifact can be promoted safely.

## Smells To Flag

- Deploy jobs that run on every branch because filters are missing or too broad.
- Approval jobs that gate nothing sensitive or appear too early in the graph.
- Tag release workflows whose dependencies are missing matching tag filters.
- Several near-duplicate workflows that differ only by branch or trigger condition.
- Schedule triggers that launch every workflow because no workflow-level condition narrows the run.

## Common Fixes To Suggest

- Add workflow-level branch or tag filters to release jobs.
- Move approval jobs directly before production-facing steps.
- Collapse duplicate workflows with expressions or parameters.
- Use tags for production release routing and branches for continuous validation.
- Use dynamic config only after simpler filters and parameterization become too hard to maintain.
