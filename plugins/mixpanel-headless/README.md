# Mixpanel Headless

Analyze Mixpanel data from Codex with the `mixpanel_headless` Python SDK.

This plugin is intentionally separate from `plugins/mixpanel`, which wraps the
hosted Mixpanel connector. `mixpanel-headless` is for coding-agent workflows
where Codex installs a local SDK, writes Python, uses pandas and plotting
libraries, and can compose Mixpanel analysis with local files or other data
sources.

## Skills

| Skill | Purpose |
| --- | --- |
| `mixpanel-headless-setup` | Install `mixpanel_headless` and common analysis dependencies, then verify credentials. |
| `mixpanel-auth` | Check sessions, list/use accounts, run OAuth login, switch projects or workspaces, and manage targets. |
| `mixpanelyst` | Discover event schemas and run segmentation, funnel, retention, flow, and user-profile analyses. |
| `dashboard-expert` | Analyze, create, modify, and explain Mixpanel dashboards. |

## Quick Start

1. Use `mixpanel-headless-setup` to install dependencies and verify auth.
2. Use `mixpanel-auth` if account, project, workspace, or target selection needs setup.
3. Ask an analytics question, such as "Analyze signup dropoff in Mixpanel with Python."

## Authentication

The SDK supports service accounts, browser OAuth, and bearer-token based OAuth.
The recommended first setup command is:

```bash
mp login
```

For non-interactive contexts, configure:

```bash
export MP_OAUTH_TOKEN="<bearer-token>"
export MP_PROJECT_ID="<project-id>"
export MP_REGION="us"
```

Do not paste secrets into chat. Set them in the local shell or credential store.

## Source

The skills are adapted from Mixpanel's public headless SDK plugin:
https://github.com/mixpanel/mixpanel-headless/tree/main/mixpanel-plugin

SDK documentation: https://mixpanel.github.io/mixpanel-headless/
