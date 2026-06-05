# Metabase Codex Plugin

The official [Codex](https://developers.openai.com/codex/) MCP Plugin for [Metabase](https://www.metabase.com/). Developed and maintained by the Metabase Team.

## What's included

- Skill: `setup-metabase-mcp` (`skills/setup-metabase-mcp/SKILL.md`)
- MCP server config: `.mcp.json`

Current scope: **skills + MCP config only** (no rules, agents, commands, or hooks yet).

## Connecting to your Metabase

After installing the plugin, just ask Codex to set up your Metabase MCP server:

Just type: "Set up my Metabase MCP"

The `setup-metabase-mcp` skill will guide you through the rest. Codex will:

- Ask for your Metabase URL.
- Verify that your Metabase is version 60 or higher.
- Update your plugin's config with your Metabase's URL.

You'll need a valid login to your Metabase.

## How to test the Metabase plugin locally

1. Clone this repo.

2. Set up a local marketplace that points at the cloned plugin.

```sh
mkdir -p ~/codex-local/.agents/plugins ~/codex-local/plugins
cp --recursive /path/to/metabase-codex-plugin ~/codex-local/plugins/metabase
```

Note the `--recursive` flag; you need to copy the directory and its sub-directories because Codex caches a copy of the plugin and won't resolve symlinks when loading local plugins.

Then create `~/codex-local/.agents/plugins/marketplace.json`:

```json
{
  "name": "local-dev",
  "interface": { "displayName": "Local Dev" },
  "plugins": [
    {
      "name": "metabase",
      "source": { "source": "local", "path": "./plugins/metabase" },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "Data"
    }
  ]
}
```

3. Register the marketplace with Codex.

```sh
codex plugin marketplace add ~/codex-local
```

4. Open Codex and install **Metabase** from the **Local Dev** marketplace:
   - **Codex CLI:** run the `/plugins` slash command.
   - **Codex Desktop:** open the **Plugins** menu and enable it there.

   Then ask Codex to "Set up my Metabase MCP".

Codex will automatically pick up the `setup-metabase-mcp` skill from the plugin and run it — no need to invoke it explicitly. The skill configures your `.mcp.json` at `~/.codex/plugins/cache/local-dev/metabase/<version>/.mcp.json`.

5. Once your `.mcp.json` is configured, restart Codex, and you should be good to go.

## Attribution

The `setup-metabase-mcp` skill is adapted from the [Datadog MCP Setup](https://github.com/datadog-labs/cursor-plugin/blob/main/skills/datadog-mcp-setup/SKILL.md).
