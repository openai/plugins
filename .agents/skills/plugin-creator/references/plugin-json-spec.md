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

- `name`: Plugin identifier (lower-case, hyphen-delimited), used as the plugin folder name and the manifest `name`.
- `version`: Plugin semantic version.
- `description`: One-line description shown in listings.
- `author`: Object with publisher identity.
  - `name`: Display name of the plugin author or team.
  - `email`: Contact email for maintainer questions.
  - `url`: Author/team homepage or profile URL.
- `homepage`: Public documentation page or overview URL for this plugin.
- `repository`: Source code or distribution repo URL.
- `license`: SPDX-style license string (for example `MIT`).
- `keywords`: Array of search/indexing keywords.
- `skills`: Relative path to the plugin skills directory.
- `hooks`: Relative path to hook configuration.
- `mcpServers`: Relative path to MCP configuration.
- `apps`: Relative path to app configuration.
- `interface`: Required block that drives the plugin catalog/UX metadata.

### `interface` fields

- `displayName`: User-facing title shown for the plugin.
- `shortDescription`: Brief subtitle used in compact plugin cards.
- `longDescription`: Longer description used on details screens.
- `developerName`: Human-readable developer/publisher name.
- `category`: Plugin category.
- `capabilities`: Supported high-level plugin capabilities.
- `websiteURL`: Public website for the plugin.
- `privacyPolicyURL`: Privacy policy URL.
- `termsOfServiceURL`: Terms of service URL.
- `defaultPrompt`: Starter prompt shown in composer/UX context.
- `brandColor`: Theme color for the plugin card.
- `composerIcon`: Path to icon asset.
- `logo`: Path to logo asset.
- `screenshots`: List of screenshot asset paths.
