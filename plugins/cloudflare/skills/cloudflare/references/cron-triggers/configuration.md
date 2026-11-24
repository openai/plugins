# Cron Triggers Configuration

Fetch the documentation for the configuration operation before changing schedules.

| Task | Documentation |
| --- | --- |
| Add a handler and configure triggers, including per-environment schedules and deployment propagation | [Add a Cron Trigger](https://developers.cloudflare.com/workers/configuration/cron-triggers/index.md#add-a-cron-trigger) |
| Choose an expression, interpret weekday numbering, or check supported extensions | [Supported cron expressions](https://developers.cloudflare.com/workers/configuration/cron-triggers/index.md#supported-cron-expressions) |
| Remove schedules or distinguish omission from an empty configuration | [Remove a Cron Trigger](https://developers.cloudflare.com/workers/configuration/cron-triggers/index.md#remove-a-cron-trigger) |
| Configure renewable-energy execution locations | [Green Compute](https://developers.cloudflare.com/workers/configuration/cron-triggers/index.md#green-compute) |
| Check trigger counts and execution budgets | [Workers limits](https://developers.cloudflare.com/workers/platform/limits/index.md) |
| Schedule Workflow instances directly | [Schedule a Workflow directly](https://developers.cloudflare.com/workflows/build/trigger-workflows/index.md#schedule-a-workflow-directly) |

Identify the target environment and the intended business timezone before choosing an expression. Review which schedules a deployment will replace, and use the documented propagation behavior when planning a rollout. For Green Compute, follow its account-level configuration rather than inferring settings from Worker placement.

See [api.md](./api.md) for implementation and [gotchas.md](./gotchas.md) for verification.
