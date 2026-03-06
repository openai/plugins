# Plugin JSON sample spec

```json
{
  "name": "plugin-name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "skills": "./skills/",
  "hooks": "./hooks.json",
  "mcpServers": "./mcp.json",
  "apps": "./app.json",
  "interface": {
    "displayName": "Plugin Display Name",
    "shortDescription": "Short description for subtitle",
    "longDescription": "Long description for details page",
    "developerName": "OpenAI",
    "category": "Productivity",
    "capabilities": ["Interactive", "Write"],
    "websiteURL": "https://openai.com/",
    "privacyPolicyURL": "https://openai.com/policies/row-privacy-policy/",
    "termsOfServiceURL": "https://openai.com/policies/row-terms-of-use/",
    "defaultPrompt": "Starter prompt for trying a plugin",
    "brandColor": "#3B82F6",
    "composerIcon": "./assets/icon.png",
    "logo": "./assets/logo.png",
    "screenshots": [
      "./assets/screenshot1.png",
      "./assets/screenshot2.png",
      "./assets/screenshot3.png"
    ]
  }
}
```

## Field guide

### Top-level fields

- `name`: Plugin identifier (kebab-case, no spaces). Required if `plugin.json` is provided and used as manifest name and component namespace.
- `version`: Plugin semantic version.
- `description`: Short purpose summary.
- `author`: Publisher identity object.
  - `name`: Author or team name.
  - `email`: Contact email.
  - `url`: Author/team homepage or profile URL.
- `homepage`: Documentation URL for plugin usage.
- `repository`: Source code URL.
- `license`: License identifier (for example `MIT`, `Apache-2.0`).
- `keywords`: Search/discovery tags.
- `skills`: Relative path to skill directories/files.
- `hooks`: Hook config path.
- `mcpServers`: MCP config path.
- `apps`: App manifest path for plugin integrations.
- `interface`: Interface/UX metadata block for plugin presentation.

### `interface` fields

- `displayName`: User-facing title shown for the plugin.
- `shortDescription`: Brief subtitle used in compact views.
- `longDescription`: Longer description used on details screens.
- `developerName`: Human-readable publisher name.
- `category`: Plugin category bucket.
- `capabilities`: Capability list from implementation.
- `websiteURL`: Public website for the plugin.
- `privacyPolicyURL`: Privacy policy URL.
- `termsOfServiceURL`: Terms of service URL.
- `defaultPrompt`: Starter prompt shown in composer/UX context.
- `brandColor`: Theme color for the plugin card.
- `composerIcon`: Path to icon asset.
- `logo`: Path to logo asset.
- `screenshots`: List of screenshot asset paths.
  - Screenshot entries must be PNG filenames and stored under `./assets/`.
  - Keep file paths relative to plugin root.

### Path conventions and defaults

- Path values should be relative and begin with `./`.
- `skills`, `hooks`, and `mcpServers` are supplemented on top of default component discovery; they do not replace defaults.
- Custom path values must follow the plugin root convention and naming/namespacing rules.
- This repo’s scaffold writes `.codex-plugin/plugin.json`; treat that as the manifest location this skill generates.
