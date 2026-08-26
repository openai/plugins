import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_google_calendar_blob_assets_preserve_public_icons() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    hashes = tomllib.loads((REPO_ROOT / "manage" / "blob_data.hashes").read_text())
    expected_assets = {
        "plugins/google-calendar/assets/icon.png",
        "plugins/google-calendar/assets/logo.png",
    }

    configured = {
        path
        for path in pyproject["tool"]["applied_manage"]["blob_data"]
        if path.startswith("plugins/google-calendar/")
    }
    recorded = {
        entry["name"]
        for entry in hashes["file"]
        if entry["name"].startswith("plugins/google-calendar/")
    }

    assert configured == expected_assets
    assert recorded == expected_assets
