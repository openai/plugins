# Render Codex Plugin

Use Render from Codex to deploy apps, validate `render.yaml`, debug failed deploys, monitor services, and work through common platform workflows.

## What you get

- Bundled Render skills for deployment, debugging, monitoring, migrations, and workflows
- A helper script at `scripts/validate-render-yaml.sh` for `render blueprints validate`
- Plugin metadata and assets for Codex installation

## Install the plugin

Install the plugin from the Codex plugin library in the app when it is available there. That is the preferred install path for most users.

Use the local install flow below for development, testing, or pre-release access.

## Install locally for development

1. Copy the plugin into `~/.codex/plugins/render`:

```bash
mkdir -p ~/.codex/plugins
rsync -a ./ ~/.codex/plugins/render/
```

2. Add the plugin to `~/.agents/plugins/marketplace.json`.

If the file already exists, add the `render` entry to the existing `plugins` array.

```json
{
  "name": "local-plugins",
  "interface": {
    "displayName": "Local Plugins"
  },
  "plugins": [
    {
      "name": "render",
      "source": {
        "source": "local",
        "path": "./.codex/plugins/render"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

3. Restart Codex.
4. Open the plugin directory in Codex and install `Render` from your marketplace.

## Get started

Use the plugin to:

- Deploy a project to Render
- Validate and troubleshoot `render.yaml`
- Debug failed deploys and check service status
- Work through common setup and migration tasks

Good first prompts:

- `Help me deploy this project to Render.`
- `Help me validate my render.yaml for Render.`
- `Debug a failed Render deployment.`

## Set up the Render CLI

Many Render workflows depend on the Render CLI.

1. Install the Render CLI:

```bash
brew install render
```

2. Authenticate:

```bash
render login
```

3. Verify access:

```bash
render whoami -o json
```

If `render whoami -o json` fails, fix authentication before you rely on Render workflows in Codex.

## For maintainers

Run the sync script to refresh `skills/` from [render-oss/skills](https://github.com/render-oss/skills):

```bash
./scripts/sync-skills.sh
```

GitHub Actions also runs `.github/workflows/sync-skills.yml` each day and opens a pull request when upstream skills change.

## License

MIT. See [LICENSE](LICENSE).
