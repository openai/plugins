# Slack

**Warning: this plugin is a public OAuth client.** Its OAuth `client_id` is
published in [`.mcp.json`](.mcp.json), and no client secret is included. The public
ID can be copied to impersonate the client in OAuth requests; it cannot prove
that a request comes from this plugin. Access to a Slack account still requires
user authorization.

For more context, see Okta's
[The Identity of OAuth Public Clients](https://developer.okta.com/blog/2022/06/01/oauth-public-client-identity).
