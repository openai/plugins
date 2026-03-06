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
- `version`: Plugin semantic version (for example `1.2.0`); use your release versioning scheme and bump when behavior or schema changes.
- `description`: One-line description shown in listings; keep concise and user-facing.
- `author`: Object with publisher identity.
  - `name`: Display name of the plugin author or team.
  - `email`: Contact email for maintainer questions.
  - `url`: Author/team homepage or profile URL.
- `homepage`: Public documentation page or overview URL for this plugin.
- `repository`: Source code or distribution repo URL.
- `license`: SPDX-style license string (for example `MIT`).
- `keywords`: Array of search/indexing keywords.
- `skills`: Relative path to the plugin skills directory; example in canonical spec is `./skills/`.
- `hooks`: Relative path to hook configuration; example is `./hooks.json`.
- `mcpServers`: Relative path to MCP configuration; example is `./mcp.json`.
- `apps`: Relative path to app configuration; example is `./app.json`.
- `interface`: Required block that drives the plugin catalog/UX metadata.

### `interface` fields

- `displayName`: User-facing title shown for the plugin.
- `shortDescription`: Brief subtitle used in compact plugin cards.
- `longDescription`: Longer description used on details screens.
- `developerName`: Human-readable developer/publisher name.
- `category`: Plugin category bucket.
- `capabilities`: Supported high-level plugin capabilities, as a string list.
  - Use the capabilities from your actual implementation; the sample uses `["Interactive", "Write"]`.
- `websiteURL`: Public website for the plugin.
- `privacyPolicyURL`: Privacy policy URL.
- `termsOfServiceURL`: Terms of service URL.
- `defaultPrompt`: Starter prompt shown in composer/UX context.
- `brandColor`: Theme color for the plugin card in hex format (example: `#3B82F6`).
- `composerIcon`: Path to icon asset.
  - Prefer PNG/WebP-compatible image path string.
  - In the example, this lives under `./assets/icon.png`.
- `logo`: Path to logo asset.
  - Prefer PNG/WebP-compatible image path string.
  - In the example, this lives under `./assets/logo.png`.
- `screenshots`: List of screenshot asset paths.
  - Screenshot entries must be PNG filenames and stored under `./assets/` (for example `./assets/screenshot1.png`).
  - Keep file paths relative to plugin root.
