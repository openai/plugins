---
name: wrangler
description: Run or troubleshoot Wrangler CLI commands in projects that have a wrangler.jsonc, wrangler.json, or wrangler.toml file, including local development, Previews, deployment, and resource management. For new projects and projects without a Wrangler configuration file, use the cf CLI instead.
---

# Wrangler CLI

Use this skill only when the project has `wrangler.jsonc`, `wrangler.json`, or `wrangler.toml` and no `cloudflare.config.ts`, or when the user asks for Wrangler. For a new project, a project with `cloudflare.config.ts`, or a project with no Cloudflare configuration, use the Cloudflare CLI (`cf`) instead: load the `cf-cli` skill if it is installed, or follow [Use cf with coding agents](https://developers.cloudflare.com/cf/agents/index.md). Do not add Wrangler to those projects.

Use the project's Wrangler version and retrieve the relevant documentation before writing commands or configuration. CLI flags and configuration fields change; do not rely on memorized examples.

## Inspect the Project

- Find the package manager, installed Wrangler version, package scripts, framework, and Wrangler config. Run commands through the project's scripts or package manager so they use its local version. Install dependencies using the existing lockfile when needed; do not silently upgrade Wrangler to match current docs. If the project has a Wrangler configuration file but Wrangler is not a dependency, follow the [installation guide](https://developers.cloudflare.com/workers/wrangler/install-and-update/index.md) to add it locally.
- Identify the config used by the build or deploy command, including framework-generated config. Edit its source rather than generated output.
- Establish the target account, Worker, environment, and resource before running commands that change them. For data operations, determine whether the target is local or remote.

## Retrieve What the Task Needs

Use the Cloudflare MCP `docs` tool if available, or fetch the relevant linked page directly. Follow links to the specific command or product involved; avoid loading the entire reference. If a page moves, rediscover it through the [Wrangler command index](https://developers.cloudflare.com/workers/wrangler/commands/index.md) or Cloudflare docs search.

| Task | Source |
| --- | --- |
| Discover commands and flags, including resource management, deployments, rollback, and diagnostics | Project-local `wrangler --help` and `wrangler <command> --help`; [command reference](https://developers.cloudflare.com/workers/wrangler/commands/index.md) |
| Edit config or add a binding | Installed `wrangler/config-schema.json` (usually under `node_modules`); [configuration reference](https://developers.cloudflare.com/workers/wrangler/configuration/index.md) |
| Deploy a framework application | [Framework guides](https://developers.cloudflare.com/workers/framework-guides/index.md); follow the guide for the project's existing framework and adapter |
| Migrate an application to Workers when requested | [Pages to Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/index.md); [Vercel to Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/vercel-to-workers/index.md) |
| Configure staging or production | [Environments](https://developers.cloudflare.com/workers/wrangler/environments/index.md) |
| Set secrets locally, in CI, or on a deployed Worker | [Secrets](https://developers.cloudflare.com/workers/configuration/secrets/index.md) |
| Generate binding and runtime types | [TypeScript](https://developers.cloudflare.com/workers/languages/typescript/index.md) |
| Run locally or choose a testing approach | [Local development](https://developers.cloudflare.com/workers/local-development/index.md); [testing](https://developers.cloudflare.com/workers/testing/index.md) |
| Choose roles, scopes, or API token permissions for Wrangler | [Roles and permissions](https://developers.cloudflare.com/workers/authorization/index.md); [Workers roles and permissions](https://developers.cloudflare.com/workers/authorization/workers/index.md#wrangler) |
| Create or manage a branch or pull request environment | [Previews overview](https://developers.cloudflare.com/workers/previews/index.md); [get started](https://developers.cloudflare.com/workers/previews/get-started/index.md); [configuration](https://developers.cloudflare.com/workers/previews/configuration/index.md) |
| Decide whether Preview resources are isolated or shared | [Resources and isolation](https://developers.cloudflare.com/workers/previews/resources/index.md), including its current limitations |
| Configure Preview URLs, access, debugging, or CI | [Custom domains](https://developers.cloudflare.com/workers/previews/custom-domains/index.md); [test and debug](https://developers.cloudflare.com/workers/previews/test-and-debug/index.md); [examples](https://developers.cloudflare.com/workers/previews/examples/index.md) |
| Choose between Previews, Version URLs, and Wrangler environments | [Compare workflows](https://developers.cloudflare.com/workers/previews/compare-workflows/index.md) |
| Diagnose authentication or select an account | [General commands](https://developers.cloudflare.com/workers/wrangler/commands/general/index.md), including `whoami`; [authentication profiles](https://developers.cloudflare.com/workers/wrangler/profiles/index.md) |
| Deploy an unauthenticated prototype | [Claim deployments](https://developers.cloudflare.com/workers/platform/claim-deployments/index.md) for eligibility, expiry, and claim URL handling; use a permanent account for production or CI |

Use installed help and schema to check whether documented features exist in the project's version. If a required feature needs an upgrade, make that dependency explicit. If retrieval is unavailable, state the gap and use available local evidence rather than inventing syntax.

## Apply the Change

- Prefer `wrangler.jsonc` for new config. Set a new project's [compatibility date](https://developers.cloudflare.com/workers/configuration/compatibility-dates/index.md) to today; review runtime changes and test when advancing an existing project's date. Preserve existing project conventions and avoid incidental format migrations.
- Check environment inheritance before adding bindings or variables. Some fields must be specified separately for each environment; a working default config does not establish that staging is configured.
- With the Cloudflare Vite plugin, select the environment via `CLOUDFLARE_ENV` at dev or build time. Deploy the resulting build; setting an environment at deploy time does not retarget its flattened config. See [Vite environments](https://developers.cloudflare.com/workers/vite-plugin/reference/cloudflare-environments/index.md).
- Reconcile dashboard changes with the config before deploying: Wrangler can overwrite dashboard variables and routes. When binding existing resources, verify their identifiers; omitted identifiers can trigger [automatic provisioning](https://developers.cloudflare.com/workers/wrangler/configuration/index.md#automatic-provisioning).
- Distinguish local simulation from remote bindings during development. A locally running Worker can still access real resources; check the selected bindings before testing writes.
- Before a remote command, identify the authenticated member or API token and retrieve the current role and scope required for the exact operation. Prefer the narrowest scope that satisfies the user's intent. The `wrangler login` OAuth flow does not support granular authorization; use an account-owned API token when granular access is required, and never ask the user to paste its value into chat.
- Keep secret values out of command arguments, source code, and logs. Use the documented interactive input or protected file/stdin mechanism for the command. Local secret files must be ignored by version control and are not automatically uploaded as deployed secrets. For missing local secrets, check file precedence and any `secrets.required` declaration in the secrets docs.
- Treat `wrangler secret put` and `secret delete` as deployments: they create a version and deploy it immediately. Use the documented `wrangler versions secret` workflow when the change must be staged.
- Before a rollback, check [rollback limitations](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/index.md): connected resources and their data are not rolled back with Worker code.

## Work with Workers Previews

- Workers Previews requires project-local Wrangler 4.135.0 or later; project commands do not use a newer global installation. Check the project's pinned version and make any required dependency upgrade explicit.
- Use Previews for branch and pull request environments under the same Worker. Use Version URLs to inspect a specific uploaded version with production resources, and Wrangler environments for persistent, separately deployed Workers. Follow [Compare workflows](https://developers.cloudflare.com/workers/previews/compare-workflows/index.md) rather than adapting an older aliased Version URL workflow.
- First inspect how the user manages production configuration and deployments. Configure Preview domains through the same configuration system as production, such as Wrangler, the dashboard, or Terraform. Run Preview deployments through the user's existing path, such as the local CLI, Workers Builds, or external CI, unless the user requests a different workflow. Mirror the management approach, not production resource bindings or data.
- Before deploying, follow the current [configuration placement table](https://developers.cloudflare.com/workers/previews/configuration/index.md#what-goes-in-the-previews-block) and [resource matrix and limitations](https://developers.cloudflare.com/workers/previews/resources/index.md). Do not infer isolation from the Preview name or allow writes to production resources unless the user explicitly intends to share them.
- Tell the user that Preview URLs are public unless access controls are configured, then let them decide whether to protect the URLs. Follow the [custom domain and access guidance](https://developers.cloudflare.com/workers/previews/custom-domains/index.md) for the chosen setup.
- Confirm which Worker or Wrangler environment the user intends to target. When targeting a Wrangler environment, pass the same `--env` value to every Preview command; omitting it targets the top-level Worker.

## Validate

After changing config or bindings in a TypeScript project, regenerate types with the project's `wrangler types` command rather than hand-editing generated declarations. Run the relevant existing typecheck or tests.

For deployment changes, use the project's build workflow and `wrangler deploy --dry-run` where supported, with the intended config and environment. A successful dry run checks the build and packaging; it does not prove remote resources or runtime behavior work. Use task-specific local or remote checks as appropriate to the requested work.

For Previews, a returned URL does not validate behavior that depends on bindings Wrangler reports as missing. Validate the behavior the user requested, using Preview-specific logs and configuration when needed. Writes to production resources, destructive testing, and deletion of named Previews must match the user's explicit intent.

Report what changed, the target environment, checks performed, and any unresolved validation gaps. Link the documentation used when the result depends on current command or configuration behavior.

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
