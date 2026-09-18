# OpenAI Developers Plugin

This plugin is the Codex-facing bundle for OpenAI developer workflows. It pairs OpenAI Platform workflows with Codex's native OpenAI docs skill guidance so users can build AI applications, agents, and ChatGPT Apps, then connect those projects to `platform.openai.com`.

## What Is Included

- `.codex-plugin/plugin.json` declares the Codex plugin metadata and user-facing `OpenAI Developers` brand.
- `.app.json` exposes the `openai-platform` app connector used to work with the OpenAI Platform.
- `.mcp.json` and `mcp/server.mjs` provide an editable local destination confirmation form for the API-key setup flow and the DevDay agenda MCP App.
- `skills/openai-platform-api-key/` handles encrypted API-key creation and local project setup; its preferred flow uses the OpenAI Platform connector-owned picker for the key name, organization, and project, then requests local confirmation of the env-file destination before writing locally.
- `skills/openai-api-troubleshooting/` classifies common runtime API failures and routes users to the right next step.
- `assets/openai-platform.png` is intentionally shared by both the plugin tile and the bundled OpenAI Platform app tile.
- `skills/agents-sdk/` builds, runs, deploys and evaluates Agents SDK apps.
- `skills/build-chatgpt-app/` scaffolds, refactors, and troubleshoots ChatGPT Apps SDK projects.
- `skills/chatgpt-app-submission/` generates `chatgpt-app-submission.json` for ChatGPT Apps submissions.
- `skills/devday-guide/` answers explicit OpenAI DevDay questions from public sources and can render a compact personal agenda. It needs no account connection or additional packages; after the event it helps people find published recordings and continue with the existing developer workflows.

## DevDay extension

`open_devday_agenda` opens the public program in the conversation's side panel on supporting hosts. It registers one MCP App resource and a thread entrypoint through the existing stdio server. There is no new server, dependency, global navigation entry, or account connection. The view uses the launch result directly; the skill verifies the official site before supplying event data.

Attendees choose activities, switch timezones, and select **Use plan in chat** to attach their current plan to the next message. They can ask about overlapping activities or an earlier departure. The view supports the OpenAI model-context lifecycle, keeps choices when an attachment is removed, and never sends a message automatically. Download uses the host's supported download action. Unavailable host capabilities produce a useful fallback instead of pretending the operation succeeded.

The compact JSON-RPC bridge implements MCP Apps protocol `2026-01-26` and the OpenAI UI entrypoint/model-context extensions. It accepts messages only from its embedding parent and negotiated origin. HTML is shared with the offline renderer. No schedule or personal plan is stored in the plugin or shared between tool calls.

### Test in ChatGPT

Install a private test release containing this complete plugin through the supported plugin publishing workflow; installing only the skill will not register the MCP App. This source branch and its local tests do not update an installed release.

1. Select that test plugin and ask: “Use the DevDay guide to check the public 2026 schedule and open my agenda. I’m interested in agents and leaving at 4 p.m.”
2. Confirm `open_devday_agenda` opens the agenda in the side panel, with a public source and check date. A JSON tool result alone does not prove UI placement.
3. Change the selection and timezone, then click **Use plan in chat**. Ask “What overlaps in my selected plan?” and confirm the answer uses the attached choices.
4. Remove the attachment. Choices should remain in the view and no attachment should reappear automatically. Try a download if the host advertises that capability.

External event facts must remain publicly verified. Synthetic test fixtures are never an attendee schedule. Real ChatGPT installation, side-panel placement, and conversation behavior must be checked separately from local protocol tests.

## Local Validation

```bash
node --test plugins/openai-developers/tests/openai-platform-api-key.test.mjs
node --test plugins/openai-developers/tests/devday-extension.test.mjs
python3 -m unittest discover -s plugins/openai-developers/tests -p 'test_devday_agenda.py'
python plugins/internal-distribution/scripts/validate_distribution.py
```
