# OpenAI Developers Plugin

This plugin is the Codex-facing bundle for OpenAI developer workflows. It pairs OpenAI Platform workflows with Codex's native OpenAI docs skill guidance so users can build AI applications, agents, and ChatGPT Apps, then connect those projects to `platform.openai.com`.

## What Is Included

- `.codex-plugin/plugin.json` declares the Codex plugin metadata and user-facing `OpenAI Developers` brand.
- `.app.json` exposes the `openai-platform` app connector used to work with the OpenAI Platform.
- `.mcp.json` and `mcp/server.mjs` provide an editable local destination confirmation form for the API-key setup flow.
- `skills/openai-platform-api-key/` handles encrypted API-key creation and local project setup; its preferred flow uses the OpenAI Platform connector-owned picker for the key name, organization, and project, then requests local confirmation of the env-file destination before writing locally.
- `skills/openai-api-troubleshooting/` classifies common runtime API failures and routes users to the right next step.
- `assets/openai-platform.png` is intentionally shared by both the plugin tile and the bundled OpenAI Platform app tile.
- `skills/agents-sdk/` builds, runs, deploys and evaluates Agents SDK apps.
- `skills/build-chatgpt-app/` scaffolds, refactors, and troubleshoots ChatGPT Apps SDK projects.
- `skills/chatgpt-app-submission/` generates `chatgpt-app-submission.json` for ChatGPT Apps submissions.

## Local Validation

```bash
node --test plugins/openai-developers/tests/openai-platform-api-key.test.mjs
python plugins/internal-distribution/scripts/validate_distribution.py
```
