import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "gmail"
GMAIL_CONNECTOR_ID = "connector_2128aebfecb84f64a069897515042a44"


def test_gmail_plugin_manifest_and_skill_paths_exist() -> None:
    manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())
    app_config = json.loads((PLUGIN_ROOT / ".app.json").read_text())

    assert manifest["name"] == "gmail"
    assert manifest["skills"] == "./skills/"
    assert manifest["apps"] == "./.app.json"
    assert (
        manifest["repository"]
        == "https://github.com/openai/openai/tree/master/chatgpt/oai-maintained-plugins"
    )
    assert (PLUGIN_ROOT / "skills" / "gmail" / "SKILL.md").is_file()
    assert {path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")} == {"gmail"}
    assert (PLUGIN_ROOT / "assets" / "gmail-small.svg").is_file()
    blob_data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())["tool"]["applied_manage"][
        "blob_data"
    ]
    assert "plugins/gmail/assets/gmail.png" in blob_data
    assert "plugins/gmail/skills/gmail/assets/gmail.png" in blob_data
    assert app_config["apps"]["gmail"]["id"] == GMAIL_CONNECTOR_ID


def test_pasted_gmail_link_workflow_is_bounded_and_fast_fails() -> None:
    workflow = (PLUGIN_ROOT / "skills" / "gmail" / "SKILL.md").read_text()

    assert "`mail.google.com`" in workflow
    assert "/mail/u/<decimal account-index>/#<view>/<token>" in workflow
    assert "/mail/#<view>/<token>" in workflow
    assert 'default `id_type="message"`' in workflow
    assert 'id_type="thread"`' in workflow
    assert "Never broaden into search" in workflow
    assert "After mismatch or two exact misses, stop" in workflow
    assert "sender + subject + approximate date" in workflow


def test_pasted_gmail_link_evals_cover_success_and_recovery() -> None:
    eval_file = json.loads((PLUGIN_ROOT / "skills" / "gmail" / "evals" / "evals.json").read_text())
    evals = eval_file["evals"]
    prompts = [case["prompt"] for case in evals]

    assert eval_file["skill_name"] == "gmail"
    assert len(evals) == 6
    assert any("#all/18f7abc123" in prompt for prompt in prompts)
    assert any("#inbox/18f7def456?attachment_id=" in prompt for prompt in prompts)
    assert any("#search/from%3Aalice/project-update" in prompt for prompt in prompts)
    assert any(
        "neither the message-ID nor thread-ID lookup finds it" in prompt for prompt in prompts
    )
    assert any("weekly project update" in prompt for prompt in prompts)
    assert any("literal line breaks" in prompt for prompt in prompts)


def test_outgoing_email_contract_omits_body_format_support_details() -> None:
    skill = (PLUGIN_ROOT / "skills" / "gmail" / "SKILL.md").read_text()

    assert "Markdown" not in skill
    assert "plain text" not in skill
    assert "plain-text" not in skill
    assert "HTML" not in skill
    assert "places a `note` above it" in skill
    assert '`to: "me"`' in skill


def test_write_receipts_are_truthful_without_exposing_internal_ids() -> None:
    skill = (PLUGIN_ROOT / "skills" / "gmail" / "SKILL.md").read_text()
    writes = skill.split("## Writes", 1)[1].split("## Triage", 1)[0]

    assert "user-meaningful context" in writes
    assert "Do not expose raw message or thread identifiers" in writes
    assert (
        "If the action only created a draft, say so explicitly and never imply it was sent"
        in writes
    )
    assert "Include the relevant message or thread identifier" not in writes


def test_gmail_plugin_is_registered_in_marketplace() -> None:
    marketplace = json.loads((REPO_ROOT / "marketplace.json").read_text())
    entry = next(plugin for plugin in marketplace["plugins"] if plugin["name"] == "gmail")

    assert entry["source"]["path"] == "./plugins/gmail"
    assert entry["policy"]["installation"] == "AVAILABLE"
    assert entry["policy"]["authentication"] == "ON_INSTALL"
    assert entry["category"] == "Communication"
