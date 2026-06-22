# GitHub

Use the GitHub plugin to inspect repositories, triage pull requests and issues,
debug CI, and prepare code changes for review.

## App Connector for ChatGPT-login Codex sessions

For Codex sessions signed in with ChatGPT, this plugin uses the GitHub App
Connector declared in [`.app.json`](.app.json). Codex prompts you to connect
GitHub, manages the connector authentication, and makes the authorized GitHub
tools available to the plugin; no PAT environment variable is required.

## MCP setup for API-key Codex sessions

This plugin includes GitHub's hosted MCP server declaration. For PAT creation,
permissions, secure storage, and verification, follow GitHub's
[official Codex installation guide](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md).

The plugin reads the token from the `GITHUB_PAT_TOKEN` environment variable.
