# GitHub

Use the GitHub plugin to inspect repositories, triage pull requests and issues,
debug CI, and prepare code changes for review.

## MCP setup for API-key Codex sessions

This plugin includes GitHub's hosted MCP server declaration. For PAT creation,
permissions, secure storage, and verification, follow GitHub's
[official Codex installation guide](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md).

The plugin reads the token from the `GITHUB_PAT_TOKEN` environment variable.
