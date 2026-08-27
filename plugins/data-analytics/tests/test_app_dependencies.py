import json
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def test_data_analytics_declares_no_required_apps() -> None:
    manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())
    app_config = json.loads((PLUGIN_ROOT / ".app.json").read_text())

    assert manifest["apps"] == "./.app.json"

    required_apps = [
        app_name
        for app_name, config in app_config["apps"].items()
        if config.get("optional") is not True
    ]

    assert required_apps == []
    assert app_config["apps"]["sites"] == {
        "id": "connector_20205bf7d4e99a89d7154bb849718324",
        "optional": True,
        "category": "Application hosting",
    }
