# Sideload Zoom

For local sideload testing, use a marketplace root that contains the plugin under `plugins/zoom/`.

Recommended sideload sandbox:

```text
zoom-sideload/
├── .agents/plugins/marketplace.json
└── plugins/
    └── zoom/
        ├── .codex-plugin/plugin.json
        ├── plugin.json
        ├── .app.json
        ├── assets/
        ├── AGENTS.md
        └── README.md
```

Important details:

- `.agents/plugins/marketplace.json` lives at the marketplace root.
- the marketplace entry points at `./plugins/zoom`
- `plugins/zoom/.codex-plugin/plugin.json` is the canonical manifest
- `plugins/zoom/plugin.json` can be used as a compatibility copy for installers that probe the plugin root
- `plugins/zoom/.app.json` enables the Zoom app connector

Create a clean sideload sandbox from this repo:

```bash
REPO="/path/to/zoom-plugin-codex"
SIDELOAD="/tmp/zoom-sideload"

rm -rf "$SIDELOAD"
mkdir -p "$SIDELOAD/plugins/zoom"

rsync -a \
  --exclude ".git" \
  --exclude ".DS_Store" \
  --exclude "plugins" \
  "$REPO"/ "$SIDELOAD/plugins/zoom"/

mkdir -p "$SIDELOAD/.agents/plugins"
cat > "$SIDELOAD/.agents/plugins/marketplace.json" <<'JSON'
{
  "name": "zoom-local",
  "interface": {
    "displayName": "Zoom Local"
  },
  "plugins": [
    {
      "name": "zoom",
      "source": {
        "source": "local",
        "path": "./plugins/zoom"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
JSON

cp \
  "$SIDELOAD/plugins/zoom/.codex-plugin/plugin.json" \
  "$SIDELOAD/plugins/zoom/plugin.json"
```

Then point Codex at the sideload marketplace root and install `Zoom`.
