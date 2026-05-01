# Sideload Zoom Developers

For local sideload testing, use a marketplace root that contains the plugin under `plugins/zoom-developers-plugin-codex/`.

Recommended sideload sandbox:

```text
zoom-developers-plugin-codex-sideload/
├── .agents/plugins/marketplace.json
└── plugins/
    └── zoom-developers-plugin-codex/
        ├── .codex-plugin/plugin.json
        ├── plugin.json
        ├── agents/
        ├── assets/
        ├── commands/
        ├── skills/
        ├── AGENTS.md
        ├── README.md
        └── ...
```

Important details:

- `.agents/plugins/marketplace.json` lives at the marketplace root.
- the marketplace entry points at `./plugins/zoom-developers-plugin-codex`
- `plugins/zoom-developers-plugin-codex/.codex-plugin/plugin.json` is the canonical manifest
- `plugins/zoom-developers-plugin-codex/plugin.json` can be used as a compatibility copy for installers that probe the plugin root

Create a clean sideload sandbox from this repo:

```bash
REPO="/path/to/zoom-developers-plugin-codex"
SIDELOAD="/tmp/zoom-developers-plugin-codex-sideload"

rm -rf "$SIDELOAD"
mkdir -p "$SIDELOAD/plugins/zoom-developers-plugin-codex"

rsync -a \
  --exclude ".git" \
  --exclude ".DS_Store" \
  --exclude "plugins" \
  "$REPO"/ "$SIDELOAD/plugins/zoom-developers-plugin-codex"/

mkdir -p "$SIDELOAD/.agents/plugins"
cat > "$SIDELOAD/.agents/plugins/marketplace.json" <<'JSON'
{
  "name": "zoom-developers-local",
  "interface": {
    "displayName": "Zoom Developers Local"
  },
  "plugins": [
    {
      "name": "zoom-developers-plugin-codex",
      "source": {
        "source": "local",
        "path": "./plugins/zoom-developers-plugin-codex"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
JSON

cp \
  "$SIDELOAD/plugins/zoom-developers-plugin-codex/.codex-plugin/plugin.json" \
  "$SIDELOAD/plugins/zoom-developers-plugin-codex/plugin.json"
```

Then point Codex at the sideload marketplace root and install `Zoom Developers`.
