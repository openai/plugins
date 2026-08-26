import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "gmail"
GMAIL_CONNECTOR_ID = "connector_2128aebfecb84f64a069897515042a44"


def test_gmail_plugin_manifest_and_app_paths_exist() -> None:
    manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())
    app_config = json.loads((PLUGIN_ROOT / ".app.json").read_text())

    assert manifest["name"] == "gmail"
    assert "skills" not in manifest
    assert manifest["apps"] == "./.app.json"
    assert (
        manifest["repository"]
        == "https://github.com/openai/openai/tree/master/chatgpt/oai-maintained-plugins"
    )
    assert (PLUGIN_ROOT / "assets" / "gmail-small.svg").is_file()
    blob_data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())["tool"]["applied_manage"][
        "blob_data"
    ]
    assert "plugins/gmail/assets/gmail.png" in blob_data
    assert app_config["apps"]["gmail"]["id"] == GMAIL_CONNECTOR_ID


def test_gmail_plugin_is_registered_in_marketplace() -> None:
    marketplace = json.loads((REPO_ROOT / "marketplace.json").read_text())
    entry = next(plugin for plugin in marketplace["plugins"] if plugin["name"] == "gmail")

    assert entry["source"]["path"] == "./plugins/gmail"
    assert entry["policy"]["installation"] == "AVAILABLE"
    assert entry["policy"]["authentication"] == "ON_INSTALL"
    assert entry["category"] == "Communication"
