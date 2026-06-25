# digitalocean

This directory packages the upstream [digitalocean/CodexPlugin](https://github.com/digitalocean/CodexPlugin) runtime content for the `openai/plugins` marketplace. The provisioning skill is discovered by Codex through its `SKILL.md` frontmatter.

## What is included

- `skills/provision-droplet/` from the upstream plugin
- `.app.json` for the connected DigitalOcean app
- Python helpers for SSH key generation and local SSH configuration
- The upstream SSH config template and DigitalOcean assets

## Codex compatibility notes

- The upstream plugin id is `digitalocean-codex-workspace`; this import uses the local plugin id `digitalocean`.
- The connected app manifest uses the repository's standard ID-only shape.
- The provisioning workflow and helper scripts are included without behavioral changes.

## Upstream source

- Repo: [digitalocean/CodexPlugin](https://github.com/digitalocean/CodexPlugin)
- Imported commit: `6be47f6207d3ff553a706c8e5483e6fa02793d94`
- Imported version: `0.2.2`
- Local plugin id: `digitalocean`

## Components

```text
digitalocean/
├── .codex-plugin/plugin.json
├── .app.json
├── assets/
│   ├── logo.png
│   └── logo-dark.png
└── skills/provision-droplet/
    ├── SKILL.md
    ├── ssh_config.tmpl
    └── scripts/
        ├── keygen.py
        └── configure_ssh.py
```

The skill provisions a droplet from the DigitalOcean Codex Universal image, uploads an SSH key through the connected DigitalOcean app, configures local SSH access, and hands the resulting host off to the Codex desktop app.
