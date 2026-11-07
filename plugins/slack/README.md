# Slack

**Warning: this plugin is a public OAuth client.** Its OAuth `client_id` is
published in [`.mcp.json`](.mcp.json), and no client secret is included. The public
ID can be copied to impersonate the client in OAuth requests; it cannot prove
that a request comes from this plugin. Access to a Slack account still requires
user authorization.

For more context, see Okta's
[The Identity of OAuth Public Clients](https://developer.okta.com/blog/2022/06/01/oauth-public-client-identity).

## Connect separate Slack workspaces in Codex

Being a member of several Slack organizations does not authorize the connector
in all of them. Each independent workspace needs its own OAuth authorization.
For Enterprise Grid installations, a tool's `team_id` can select an already
authorized workspace; it does not add an independent organization's credentials.
Slack can ignore `team_id` for a single-workspace token.

Codex supports separately named MCP connections to the same server. Register one
name per workspace, using this plugin's endpoint and public OAuth client ID:

```sh
codex mcp add slack-acme --url https://mcp.slack.com/mcp --oauth-client-id 11843774967.11905492103734
codex mcp login slack-acme

codex mcp add slack-beta --url https://mcp.slack.com/mcp --oauth-client-id 11843774967.11905492103734
codex mcp login slack-beta
```

Use recognizable names instead of `acme` and `beta`. At each OAuth screen, select
and confirm the intended Slack workspace. A successful login is not proof that
the correct workspace was selected. Workspace app approval policies still apply.
Keep connection names stable: Codex's OAuth credential identity includes both the
server name and URL. Logging in repeatedly under one name replaces that
connection's authorization rather than creating workspace selection.

Repeat for additional workspaces, including a setup with fifteen independent
connections. This is a connection setup pattern, not a change to the hosted
connector's account picker or a claim that fifteen live accounts were tested.
Separate connections expose separate tool namespaces. Confirm the workspace
using each connection's available read-only metadata before using it. If identity
cannot be established, stop before using that connection for a targeted action.

The optional [configuration example](examples/multi-workspace.toml) shows two
connections with final message/file publication prompts and freely available
draft preparation. It starts with both connections disabled. Merge its fields
into the corresponding existing configuration entries, authenticate each, then
enable the intended connections. Do not append duplicate TOML tables after
running `codex mcp add`, overwrite unrelated configuration, or put tokens in the
example. Per-tool prompts do not remove Slack's platform-controlled app labels.

Setting one connection's `enabled` field to `false` disables it without logging
out. `codex mcp logout <name>` removes that named login; it is not necessary when
switching between connected workspaces. Removing a connection's explicit
approval overrides restores its inherited tool policy; it does not guarantee
that sends become automatic.

## Route work to the correct workspace

- Resolve the requested workspace to its verified connection before searching
  channels, resolving users, reading messages, or preparing a post.
- Keep connection, workspace, conversation ID, and reply `thread_ts` together.
  Channel names such as `#general` are not unique across organizations.
- A search result from one connection does not establish a destination in
  another. Discover channel and user IDs again under the destination connection.
- If the requested workspace is missing, ask for that workspace's authorization.
  Do not silently use the default workspace, replace another login, or describe
  a default-workspace search as covering every organization.
- Show workspace, channel/recipient, content, attachments, and any reply target
  before final publication when the user has requested send confirmation.

The bundled `slack-workspaces` skill follows this routing workflow. Connecting
multiple workspaces does not itself authorize cross-workspace copying or posting.

References: [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp),
[Slack OAuth installations](https://docs.slack.dev/tools/node-slack-sdk/oauth/),
[Slack Enterprise workspace routing](https://docs.slack.dev/enterprise/developing-for-enterprise-orgs/).
