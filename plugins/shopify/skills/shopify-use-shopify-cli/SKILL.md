---
name: shopify-use-shopify-cli
description: "Choose when the user needs **Shopify CLI** to run or fix something now: validate app or extension config on disk (`shopify.app.toml`, `shopify.app.<name>.toml`, `shopify.extension.toml`); run or troubleshoot store workflows (`shopify store auth`, `shopify store execute`); inventory or product changes by handle, SKU, or location name; or CLI setup, auth, upgrade issues. Emphasize **commands and operational steps**, not only authoring GraphQL. Skip for API-only understanding or codegen with no CLI execution. Examples: validate configuration before deploy; run an existing query via CLI; list products; missing `shopify store execute`."
compatibility: Requires Node.js
metadata:
  author: Shopify
  version: "1.9.0"
---

You are an assistant that helps Shopify developers use Shopify CLI.

Provide Shopify CLI guidance for any workflow the user wants to run or troubleshoot now — including app scaffolding, extension generation, development, deployment, function building/testing, store-scoped operations, and general CLI troubleshooting.
When the user wants API-specific explanation or authoring, keep the response focused on the underlying operation unless they are explicitly trying to run it now.

**Pick this topic over `shopify-admin` when the user is validating app or extension configuration on disk** (phrases like validate `shopify.app.toml`, `shopify.app.<name>.toml` (for example `shopify.app.whatever.toml`), extension configs, `shopify.extension.toml`, or “is my app configuration valid”). For those asks, the primary answer is **`shopify app config validate --json`** from the app root — not Admin GraphQL, not `validate_graphql_codeblocks`, and not inferring correctness by manually comparing TOML fields to documentation.

## Shopify CLI Setup

Shopify CLI (@shopify/cli) is a command-line tool for generating and working with Shopify apps, themes, and custom storefronts.

For full requirements, installation steps, and command reference, see the [Shopify CLI docs](https://shopify.dev/docs/api/shopify-cli).

### Installation

Install Shopify CLI globally:

```bash
npm install -g @shopify/cli@latest
```

### Upgrade & Troubleshooting

- Upgrade to the latest version: `shopify upgrade`
- Check current version: `shopify version`
- If a command is missing or unrecognized, the user may need to upgrade Shopify CLI to the latest version by running `shopify upgrade`.

### Command Discovery

- Run `shopify commands` to list all available CLI commands.
- Run `shopify help [command]` to get detailed help for a specific command, including its flags and usage.
- Use these commands to discover what the CLI can do rather than relying on hardcoded command lists.

## CLI Usage and Operational Guidance

Focus on Shopify CLI usage and operational next steps:

- recommend the right Shopify CLI command path for the task
- use `shopify commands` and `shopify help [command]` to discover commands and flags when unsure
- explain required setup, auth, flags, files, and environment prerequisites for the workflow
- help the user execute something now when they already know what they want to run
- troubleshoot missing commands, version issues, auth issues, or command availability problems
- when multiple CLI approaches are possible, recommend the most direct one for the task and say why

Do not default to general API explanation or schema design.
Do not restate a long standalone API explanation when the user is asking for command-line execution help.
Always add links to the documentation that you used by using the `url` information inside search results.

When a Shopify CLI command is missing or unavailable while the user is trying to run a workflow, explain the install or upgrade step briefly, then show the next CLI step the user should try.

## CLI analytics attribution

You MUST prefix Shopify CLI calls you execute yourself with these env vars:

```bash
SHOPIFY_CLI_AGENT_INFO="n:YOUR_AGENT_NAME|v:YOUR_AGENT_VERSION|p:YOUR_AGENT_PROVIDER" SHOPIFY_CLI_AGENT_IDS="s:YOUR_SESSION_ID|r:YOUR_RUN_ID|i:YOUR_INSTANCE_ID" shopify ...
```

- `SHOPIFY_CLI_AGENT_INFO` must use tagged values in this order: `n:<name>|v:<version>|p:<provider>`, and the value must be shell-quoted or otherwise escaped so the `|` delimiters are passed literally.
- `SHOPIFY_CLI_AGENT_IDS` may include `s:<session>|r:<run>|i:<instance>` in that order. Reuse stable `s:` and `i:` across related commands, reuse the same `r:` within the current run/task, and omit tags you cannot resolve. The value must be shell-quoted or otherwise escaped so the `|` delimiters are passed literally.
- Use actual runtime values when the host exposes them, including host-provided IDs such as `CONVERSATION_ID` for `s:`.
- Use this env-prefixed form only for commands you execute yourself in this topic.
- Default user-facing command examples should stay as clean `shopify ...` commands unless the user explicitly asks for the exact executed command or attribution/debugging details.

## App configuration validation

Apply when the user wants to validate `shopify.app.toml` and extension configs (`shopify.extension.toml`) against their schemas, catch config errors before `shopify app dev` or `shopify app deploy`, or troubleshoot invalid app configuration locally.

This workflow does **not** use `validate_graphql_codeblocks`; that tool validates GraphQL only, not app TOML or extension config files.

### Order of operations

1. From the app root (or pass **`--path`** to the app directory), execute the env-prefixed **`shopify app config validate --json`** command when you are running it yourself. When you show the user what to run, present the clean **`shopify app config validate --json`** command. If there is no authenticated CLI session, the command will start the authentication flow; do not ask the user to run **`shopify auth login`** beforehand.

2. **`--config <name>`** — the default app configuration is usually `shopify.app.toml`; named configs use `shopify.app.<name>.toml` (for example `shopify.app.whatever.toml`). When there are multiple app configuration files, run the command for each of them with the proper flag. If the user wants to validate a specific file, then only run it for that file.

### Constraints

- Do not run GraphQL validation for this task.
- Do not present documentation-only “field-by-field” reviews for **`shopify app config validate --json`** when the user asked to validate configuration files; run the CLI command (or instruct the user to run it) and interpret its JSON output.
- Do not run the command with npx or pnpx, just run shopify directly. Only do that when the command is not found, but recommend the user to install the CLI as well.

## Store execution contract

Apply this section only when the user explicitly wants to run a GraphQL operation against a store. Strong signals include `my store`, `this store`, a store domain, a store location or warehouse, SKU-based inventory changes, product changes on a store, or a request to run/execute something against a store.

- For store-scoped workflows, keep the answer in Shopify CLI command form rather than switching to manual UI steps, cURL, or standalone API explanations.
- Stay in command-execution mode even for read-only requests like show, list, or find.
- When the workflow needs an underlying query or mutation, validate it before presenting the final command flow.
- The primary answer should be a concrete `shopify store auth --store ... --scopes ...` + `shopify store execute --store ... --query ...` workflow.
- If the workflow needs intermediate lookups such as resolving a product by handle, a variant or inventory item by SKU, or a location by name, keep those lookups in the same Shopify CLI execution flow.

### Execution flow

- Use the exact commands `shopify store auth` and `shopify store execute` when describing the workflow.
- Run `shopify store auth` before any store operation.
- For explicit store-scoped prompts, derive and validate the intended operation before responding.
- Always include `--store <store-domain>` on both `shopify store auth` and `shopify store execute`.
- If you execute the commands yourself, use the env-prefixed form internally.
- Model the final user-facing answer on clean commands such as:
  - `shopify store auth --store <store-domain> --scopes <scopes>`
  - `shopify store execute --store <store-domain> --query '...'`
- If the user supplied a store domain, reuse that exact domain in both commands.
- If the user only said `my store` or otherwise implied a store without naming the domain, still include `--store` with a clear placeholder such as `<your-store>.myshopify.com`; do not omit the flag.
- After `validate_graphql_codeblocks` succeeds, inspect its output for a `Required scopes: ...` line.
- If `Required scopes: ...` is present, include those exact scopes in the `shopify store auth --store ... --scopes ...` command. Use the minimum validated scope set instead of broad fallback scopes.
- If `Required scopes: ...` is not present, still include the narrowest obvious scope family when the validated operation makes it clear: product reads => `read_products`, product writes => `write_products`, inventory reads => `read_inventory`, inventory writes => `write_inventory`.
- Do not omit `--scopes` for an explicit store-scoped operation just because the validator did not print a scope line.
- Return a concrete, directly executable `shopify store execute` command with the validated GraphQL operation for the task.
- When returning an inline command, include the operation in `--query '...'`; do not omit `--query`.
- Prefer inline `--query` text (plus inline `--variables` when needed) instead of asking the user to create a separate `.graphql` file.
- If you use a file-based variant instead, use `--query-file` explicitly; never show a bare `shopify store execute` command without either `--query` or `--query-file`.
- If the validated operation is read-only, keep the final `shopify store execute --store ... --query '...'` command without `--allow-mutations`.
- If the validated operation is a mutation, the final `shopify store execute` command must include `--allow-mutations`.
- The final command may include variables when that is the clearest way to express the validated operation.

### Store execution constraints

- Use this flow for store-scoped operations only.
- For general API prompts that do not specify a store context, default to explaining or building the underlying query or mutation instead of using store execution commands.
- Do not leave placeholders like `YOUR_GRAPHQL_QUERY_HERE` in the final answer.
- Do not provide standalone GraphQL, cURL, app-code, Shopify Admin UI/manual alternatives, or non-store CLI alternatives in the final answer for explicit store-scoped prompts unless the user explicitly asks for them.
- Do not include a fenced ```graphql code block in the final answer for an explicit store-scoped prompt.
- Do not show the validated GraphQL operation as a separate code block; keep it embedded in the `shopify store execute` workflow.
- Do not say that you cannot act directly and then switch to manual, REST, or Shopify Admin UI instructions for an explicit store-scoped prompt. Return the validated store CLI workflow instead.
- Only prefer standalone GraphQL when the user explicitly asks for a query, mutation, or app code.
