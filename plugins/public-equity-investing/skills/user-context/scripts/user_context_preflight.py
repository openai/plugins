#!/usr/bin/env python3
"""Inspect Public Equity Investing user-context state without mutating it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from state_paths import PLUGIN_LABEL, STATE_DIR_HELP, resolve_state_dir

SKILL_ROOT = Path(__file__).resolve().parents[1]
USER_CONTEXT_CONFIG = SKILL_ROOT / "plugin-author-config/user-context-config.md"
SOURCE_CATEGORY_CONFIG = SKILL_ROOT / "plugin-author-config/source-category-config.json"
DEFAULT_CATEGORIES_MARKER = "## Default Categories"
SAVED_CONTEXT_HEADING = "## Saved Links And Context"
SAVED_CONTEXT_PLACEHOLDER = "status: not provided"
COMPLETE_ONBOARDING_STATUSES = {"complete", "completed", "quiet"}
TERMINAL_ONBOARDING_STATUSES = COMPLETE_ONBOARDING_STATUSES | {"deferred"}
RESOLVED_STEP_STATUSES = {"accepted", "complete", "completed", "selected", "skipped"}
TERMINAL_STEP_STATUSES = {"declined", "deferred", "quiet"}
HERO_PROMPT_OPTIONS = ["earnings-deep-dive", "long-short-pitch", "idea-generation"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Inspect {PLUGIN_LABEL} local user-context state without changing it."
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=None,
        help="Codex home directory. Defaults to $CODEX_HOME or ~/.codex.",
    )
    parser.add_argument("--state-dir", type=Path, default=None, help=STATE_DIR_HELP)
    return parser.parse_args()


def configured_categories() -> list[str]:
    config_text = USER_CONTEXT_CONFIG.read_text(encoding="utf-8")
    if DEFAULT_CATEGORIES_MARKER not in config_text:
        raise ValueError("user-context-config.md must include a Default Categories section")
    category_text = config_text.split(DEFAULT_CATEGORIES_MARKER, 1)[1]
    categories = re.findall(r"(?m)^# (.+)$", category_text)
    if not categories:
        raise ValueError("user-context-config.md must define at least one category")
    return categories


def configured_source_categories() -> dict[str, dict[str, Any]]:
    payload = json.loads(SOURCE_CATEGORY_CONFIG.read_text(encoding="utf-8"))
    categories = payload.get("categories")
    if not isinstance(categories, dict) or not categories:
        raise ValueError("source-category-config.json must define a non-empty categories object")
    for category_id, metadata in categories.items():
        if not isinstance(category_id, str) or not category_id:
            raise ValueError("source-category-config.json contains an invalid category id")
        if not isinstance(metadata, dict):
            raise ValueError(
                f"source-category-config.json category {category_id} must be an object"
            )
    return categories


def read_user_context(path: Path, errors: list[str]) -> tuple[str, str | None]:
    if not path.exists():
        return "missing", None
    try:
        return "present", path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"Could not read user-context.md: {exc}")
        return "unreadable", None


def read_onboarding_state(path: Path, errors: list[str]) -> tuple[str, dict[str, Any] | None]:
    if not path.exists():
        return "missing", None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Could not parse onboarding-state.json: {exc.msg}")
        return "malformed", None
    except OSError as exc:
        errors.append(f"Could not read onboarding-state.json: {exc}")
        return "unreadable", None
    if not isinstance(payload, dict):
        errors.append("Could not parse onboarding-state.json: expected a JSON object")
        return "malformed", None
    return "present", payload


def saved_context_by_category(user_context: str | None, categories: list[str]) -> dict[str, str]:
    if user_context is None:
        return {}
    sections = {
        match.group("name").strip(): match.group("body")
        for match in re.finditer(r"(?ms)^# (?P<name>.+?)\n(?P<body>.*?)(?=^# |\Z)", user_context)
    }
    saved_context: dict[str, str] = {}
    for category in categories:
        section = sections.get(category)
        if section is None:
            continue
        saved_context_match = re.search(
            rf"(?ms)^{re.escape(SAVED_CONTEXT_HEADING)}\s*\n(?P<body>.*?)(?=^## |\Z)",
            section,
        )
        if saved_context_match is None:
            continue
        saved_text = saved_context_match.group("body").strip()
        if saved_text and saved_text != SAVED_CONTEXT_PLACEHOLDER:
            saved_context[category] = saved_text
    return saved_context


def build_source_category_plan(
    source_categories: dict[str, dict[str, Any]],
    onboarding_state: dict[str, Any] | None,
    errors: list[str],
) -> dict[str, Any]:
    raw_confirmation = (
        onboarding_state.get("connector_confirmation") if onboarding_state is not None else None
    )
    if raw_confirmation is None:
        raw_confirmation = {}
    elif not isinstance(raw_confirmation, dict):
        errors.append("Could not inspect connector_confirmation: expected a JSON object")
        raw_confirmation = {}

    categories: dict[str, dict[str, Any]] = {}
    for category_id, metadata in source_categories.items():
        raw_route = raw_confirmation.get(category_id)
        configured_route = dict(raw_route) if isinstance(raw_route, dict) and raw_route else None
        route_status = str((configured_route or {}).get("status") or "").casefold()
        entry: dict[str, Any] = {
            "label": metadata.get("label") or category_id,
            "preferred_apps": list(metadata.get("preferred_apps") or []),
            "confirmation_status": "saved_unverified" if configured_route else "unconfigured",
            "setup_required": configured_route is None or route_status != "active",
            "state_scope": "onboarding_only_not_durable_connector_readiness",
            "readiness_status": "unverified",
            "eager_read": False,
        }
        preferred_plugins = list(metadata.get("preferred_plugins") or [])
        if preferred_plugins:
            entry["preferred_plugins"] = preferred_plugins
        relevant_skills = list(metadata.get("relevant_skills") or [])
        if relevant_skills:
            entry["relevant_skills"] = relevant_skills
        if configured_route is not None:
            entry["configured_route"] = configured_route
        categories[category_id] = entry

    return {
        "resolution": "explicit_setup_then_attempt_actual_reads_only_when_a_workflow_needs_the_source",
        "readiness_claimed": False,
        "has_setup_gaps": any(entry["setup_required"] for entry in categories.values()),
        "categories": categories,
    }


def onboarding_is_incomplete(
    status: Any,
    state_status: str,
    onboarding_state: dict[str, Any] | None,
) -> bool:
    if state_status != "present" or not isinstance(status, str):
        hero_prompt_status = block_status(onboarding_state, "hero_prompt_choice")
        return hero_prompt_status not in RESOLVED_STEP_STATUSES | TERMINAL_STEP_STATUSES
    return status.casefold() not in COMPLETE_ONBOARDING_STATUSES


def block_status(onboarding_state: dict[str, Any] | None, block_name: str) -> str | None:
    if onboarding_state is None:
        return None
    block = onboarding_state.get(block_name)
    if not isinstance(block, dict):
        return None
    status = block.get("status")
    return status.casefold() if isinstance(status, str) else None


def read_automation_state(
    onboarding_state: dict[str, Any] | None,
    errors: list[str],
) -> dict[str, Any]:
    if onboarding_state is None:
        return {}
    automations = onboarding_state.get("automations")
    if automations is None:
        return {}
    if not isinstance(automations, dict):
        errors.append("Could not inspect automations: expected a JSON object")
        return {}
    return automations


def onboarding_progress(onboarding_state: dict[str, Any] | None) -> dict[str, Any]:
    steps = [
        ("intro_defaults", "Intro and defaults", "orientation"),
        ("connectors_plugins", "Connectors and plugins", "source_setup"),
        ("automation", "Automation", "automations"),
        ("hero_workflows", "Hero workflows", "hero_prompt_choice"),
    ]
    task_list = []
    for step_id, label, block_name in steps:
        status = block_status(onboarding_state, block_name)
        if status in RESOLVED_STEP_STATUSES:
            progress_status = "completed"
        elif status in TERMINAL_STEP_STATUSES:
            progress_status = status
        else:
            progress_status = "pending"
        task_list.append({"id": step_id, "label": label, "status": progress_status})
    return {"task_list": task_list, "hero_prompt_options": HERO_PROMPT_OPTIONS}


def next_action(
    onboarding_state_status: str,
    onboarding_state: dict[str, Any] | None,
    onboarding_status: Any,
) -> dict[str, str] | None:
    if onboarding_state_status in {"malformed", "unreadable"}:
        return {
            "id": "repair_onboarding_state",
            "copy_ref": "skills/user-context/references/onboarding.md#state-repair-response-template",
        }
    if isinstance(onboarding_status, str):
        if onboarding_status.casefold() in TERMINAL_ONBOARDING_STATUSES:
            return None

    orientation_status = block_status(onboarding_state, "orientation")
    if orientation_status in TERMINAL_STEP_STATUSES:
        return None
    if orientation_status not in RESOLVED_STEP_STATUSES:
        return {
            "id": "offer_orientation",
            "copy_ref": "skills/user-context/references/onboarding.md#orientation-response-template",
        }

    source_setup_status = block_status(onboarding_state, "source_setup")
    if source_setup_status not in RESOLVED_STEP_STATUSES | TERMINAL_STEP_STATUSES:
        return {
            "id": "configure_sources",
            "copy_ref": "skills/user-context/references/onboarding.md#source-setup-response-template",
        }
    automations_status = block_status(onboarding_state, "automations")
    if automations_status not in RESOLVED_STEP_STATUSES | TERMINAL_STEP_STATUSES:
        return {
            "id": "configure_default_automation",
            "copy_ref": "skills/user-context/references/onboarding.md#automation-setup-response-template",
        }
    hero_prompt_status = block_status(onboarding_state, "hero_prompt_choice")
    if hero_prompt_status not in RESOLVED_STEP_STATUSES | TERMINAL_STEP_STATUSES:
        return {
            "id": "choose_hero_workflow",
            "copy_ref": "skills/user-context/references/onboarding.md#hero-workflow-response-template",
        }
    return None


def main() -> int:
    args = parse_args()
    state_dir = resolve_state_dir(args.codex_home, args.state_dir)
    errors: list[str] = []

    try:
        categories = configured_categories()
        source_categories = configured_source_categories()
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"Invalid {PLUGIN_LABEL} bundled user-context config: {exc}", file=sys.stderr)
        return 1

    user_context_status, user_context = read_user_context(state_dir / "user-context.md", errors)
    onboarding_state_status, onboarding_state = read_onboarding_state(
        state_dir / "onboarding-state.json",
        errors,
    )
    onboarding_status = onboarding_state.get("status") if onboarding_state is not None else None
    saved_context = saved_context_by_category(user_context, categories)

    payload = {
        "initialized": user_context_status == "present" and onboarding_state_status == "present",
        "state_dir": str(state_dir),
        "user_context_status": user_context_status,
        "onboarding_state_status": onboarding_state_status,
        "onboarding_status": onboarding_status,
        "onboarding_incomplete": onboarding_is_incomplete(
            onboarding_status,
            onboarding_state_status,
            onboarding_state,
        ),
        "next_action": next_action(
            onboarding_state_status,
            onboarding_state,
            onboarding_status,
        ),
        "saved_context": saved_context,
        "empty_categories": [category for category in categories if category not in saved_context],
        "source_category_plan": build_source_category_plan(
            source_categories,
            onboarding_state,
            errors,
        ),
        "automation_state": read_automation_state(onboarding_state, errors),
        "onboarding_progress": onboarding_progress(onboarding_state),
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
