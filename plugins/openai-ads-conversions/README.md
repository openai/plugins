# OpenAI Ads Conversions

OpenAI Ads Conversions helps Codex instrument repositories with OpenAI Ads
Measurement Pixel and optional Conversions API (CAPI) tracking. The plugin
packages a reusable skill with public OpenAI Ads documentation references and
local verification helpers.

## Codex Usage

Install `OpenAI Ads Conversions` from the Codex plugin marketplace, start a new
Codex thread in the target repository, and ask Codex to set up OpenAI Ads
conversions tracking.

## Portable Usage

The underlying setup guidance is plain Markdown plus helper scripts. If you
cannot use Codex plugins, use your preferred tool's skill or instruction setup
process to load the files under `skills/openai-ads-conversions-setup/`:

- Provide `SKILL.md` as the agent instructions.
- Keep `references/` available for setup details and reporting expectations.
- Run the helper scripts in `scripts/` locally when validating a generated
  integration.

Other tools may not support Codex skill-loading semantics directly, so follow
that tool's setup instructions and treat this portable path as best effort.

## Deployment Review

Generated instrumentation should be reviewed before deployment. Confirm the
implementation satisfies the advertiser's privacy, security, consent, and data
handling requirements, and never commit CAPI secrets or API keys.
