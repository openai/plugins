# Auth and Setup

## Table of Contents

- Actor selection checklist
- CLI-first local testing
- Choosing the auth path
- Choosing SDK vs REST
- Inspecting an existing codebase
- Common secrets and config
- Official Box starting points

## Actor selection checklist

Choose the acting identity before you choose endpoints or debug errors:

- Connected user: use when the product acts on behalf of an end user who linked their Box account.
- Enterprise service account: use when the backend runs unattended against enterprise-managed content.
- App user: use when the product provisions managed Box identities per tenant or workflow.
- Existing token from the platform: use when the surrounding app already resolved auth and passes the token into the Box layer.

Always capture which actor you are using in logs, test output, and the final answer. Many Box bugs are actually actor mismatches.

## CLI-first local testing

When the task is a local smoke test, quick inspection, or one-off verification from Codex, prefer Box CLI before raw REST if `box` is already installed and authenticated.

- Check CLI auth safely with `box users:get me --json`.
- If CLI auth is missing:
  - Fastest OAuth path: `box login -d`
  - Use your own Box app: `box login --platform-app`
  - Use an app config file: `box configure:environments:add PATH`
- Use `--as-user <id>` when you need to verify behavior as a managed user or another actor allowed by the current Box environment.
- Use `-t <token>` only when the task explicitly requires a direct bearer token instead of the current CLI environment.
- Avoid `box configure:environments:get --current` as a routine auth check because it can print sensitive environment details.
- Prefer the bundled `scripts/box_cli_smoke.py` wrapper when you want deterministic CLI-based verification from the skill.

## Choosing the auth path

- Reuse the repository's existing Box auth flow if one already exists.
- Use a user-auth flow when end users connect their own Box accounts and the app acts as that user.
- Use the enterprise or server-side pattern already approved for the Box app when the backend runs unattended or manages enterprise content.
- Treat impersonation, app-user usage, token exchange, or downscoping as advanced changes. Add them only when the product requirements clearly demand them.
- Verify the exact flow against the current auth guides before introducing a new auth path or changing scopes.

## Choosing SDK vs REST

- Use an official Box SDK when the target language already has one in the codebase or the team prefers SDK-managed models and pagination.
- Use direct REST calls when the project already centers on a generic HTTP client, only a few endpoints are needed, or SDK support does not match the feature set.
- Avoid mixing SDK abstractions and handwritten REST calls for the same feature unless there is a clear gap.
- Preserve the project's existing retry, logging, and error-normalization patterns.

## Inspecting an existing codebase

Search for:

- `box`
- `BOX_`
- `client_id`
- `client_secret`
- `enterprise`
- `shared_link`
- `webhook`
- `metadata`

Confirm:

- Where access tokens are issued, refreshed, or injected
- Whether requests are user-scoped, service-account-scoped, or app-user-scoped
- Whether the codebase already has pagination, retry, and rate-limit helpers
- Whether webhook verification already exists
- Whether file and folder IDs are persisted in a database, config, or user settings

## Common secrets and config

- Client ID and client secret
- Private key material or app config used by the approved Box auth flow
- Enterprise ID, user ID, or app-user identifiers when relevant
- Webhook signing secrets
- Default folder IDs
- Metadata template identifiers and field names
- Shared link defaults such as access level or expiration policy
- Box CLI environment names or `--as-user` conventions when the team uses CLI-based operations

## Official Box starting points

- Developer guides: https://developer.box.com/guides
- API reference root: https://developer.box.com/reference
- SDK overview: https://developer.box.com/guides/tooling/sdks/
- Authentication guides: https://developer.box.com/guides/authentication/
- CLI guides: https://developer.box.com/guides/cli
- CLI OAuth quick start: https://developer.box.com/guides/cli/quick-start

Check the current Box docs before introducing a new auth model, changing scopes, or changing Box AI behavior, because auth guidance and SDK coverage can evolve independently from the content endpoints.
