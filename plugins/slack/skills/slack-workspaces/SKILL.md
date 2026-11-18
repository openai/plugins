---
name: slack-workspaces
description: Configure separate Slack workspace connections and route reads, drafts, replies, and posts to the correct organization. Use for multiple Slack workspaces, missing workspace access, or ambiguous workspace and channel destinations.
---

# Slack workspace connections

Use the existing Slack tools and native MCP OAuth. Do not build a second token
store, scrape Slack sessions, or copy credentials between connections.

## Establish authorized coverage

1. Identify the user's intended workspace. Use accessible workspace metadata
   when available. List all pages before claiming complete coverage.
2. Distinguish independently authorized connections from Enterprise Grid team
   selection. Membership in fifteen organizations is not proof of fifteen
   authorized installations. `team_id` only selects within authorized coverage
   and can be ignored for a single-workspace token.
3. For separate logins, use one stable, recognizable MCP server name per
   workspace. Reuse the official endpoint and public client ID; let Codex manage
   OAuth credentials. The user chooses and authorizes the workspace in Slack's
   OAuth flow. Never overwrite an existing name to connect a different workspace.
4. Verify the resulting workspace identity through that connection's available
   read-only metadata. If no identity evidence is available, say what remains
   unverified and do not perform a targeted action through an assumed connection.
5. If a connection is missing or expired, ask for its authorization. Keep other
   connections intact; do not log them out or silently fall back to a default.
   Do not restart the app or unrelated MCP servers to add a connection.

For example, replace `slack-acme` with an unused name for the intended workspace:

```sh
codex mcp add slack-acme --url https://mcp.slack.com/mcp --oauth-client-id 11843774967.11905492103734
codex mcp login slack-acme
```

Repeat with a different name for each independent organization. Do not replace
the hosted connector's configuration or reuse its credential files.

## Preserve the destination

Keep `(connection, workspace, conversation ID, thread_ts)` together throughout
the workflow. Resolve users, channels, and DMs under the selected connection.
Never reuse a conversation ID, user ID, upload ID, or reply timestamp discovered
under a different connection without verifying it at the destination.

If `#general` or another name has several workspace matches, use the workspace
already specified by the user or established in the current task. Otherwise,
ask which workspace before reading or posting to a particular destination.
Do not let a name match in the default workspace decide the target.

For an authorized cross-workspace read, search each selected connection and
label findings with their workspace. Preserve pagination separately for each
connection. Honor rate-limit retry guidance; report partial coverage when one
workspace is unavailable. Do not claim a default-workspace query searched all
organizations or transfer private source content into another workspace unless
the user authorized that transfer.

## Prepare and publish

Draft through the selected connection without sending. For replies, use a real
root `thread_ts` from that conversation and do not broadcast unless requested.
If the user wants confirmation before final publication, show the workspace,
channel or recipient, exact content, attachments, and reply target, then obtain
that approval. Reuse an existing exact approval; do not ask again for preparation.

Preserve the user's switchable send-confirmation preference for every named
connection. Do not promise that policy changes remove Slack's app/sender labels.
Keep uploads and their finalization under the same connection. If a send's
outcome is unknown, reconcile it before retrying. Verify live posting only after
an authorized real send; OAuth success and synthetic tests do not prove delivery.
