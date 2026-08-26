#!/usr/bin/env python3
"""Initialize local Public Equity Investing user-context foundation files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from state_paths import PLUGIN_LABEL, STATE_DIR_HELP, resolve_state_dir

SKILL_ROOT = Path(__file__).resolve().parents[1]
USER_CONTEXT_TEMPLATE = SKILL_ROOT / "plugin-author-config/user-context-config.md"
ONBOARDING_STATE_TEMPLATE = SKILL_ROOT / "references/onboarding-state-template.json"

USER_CONTEXT_NOTE = """<!--
Public Equity Investing user-context scaffold. This file is user-editable.
Unresolved `status: not provided` entries are setup prompts, not saved facts.
-->

"""

DEFAULT_CATEGORIES_MARKER = "## Default Categories"
SAVED_CONTEXT_HEADING = "## Saved Links And Context"
SAVED_CONTEXT_PLACEHOLDER = "status: not provided"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Create missing {PLUGIN_LABEL} local state files from bundled templates."
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=None,
        help="Codex home directory. Defaults to $CODEX_HOME or ~/.codex.",
    )
    parser.add_argument("--state-dir", type=Path, default=None, help=STATE_DIR_HELP)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing user-context.md and onboarding-state.json.",
    )
    return parser.parse_args()


def validate_json(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)


def build_user_context_scaffold() -> str:
    template_text = USER_CONTEXT_TEMPLATE.read_text(encoding="utf-8")
    if DEFAULT_CATEGORIES_MARKER not in template_text:
        raise ValueError("user-context-config.md must include a Default Categories section")
    category_text = template_text.split(DEFAULT_CATEGORIES_MARKER, 1)[1].strip()
    sections = [
        section.strip() for section in re.split(r"(?m)(?=^# .+$)", category_text) if section.strip()
    ]
    if not sections:
        raise ValueError("user-context-config.md must define at least one category")

    rendered_sections = []
    for section in sections:
        if not section.startswith("# "):
            raise ValueError("user-context-config.md category entries must start with H1 headings")
        if SAVED_CONTEXT_HEADING in section:
            raise ValueError("the initializer owns saved-context placeholders")
        rendered_sections.append(
            f"{section.rstrip()}\n\n{SAVED_CONTEXT_HEADING}\n\n{SAVED_CONTEXT_PLACEHOLDER}"
        )
    return "\n\n".join(rendered_sections) + "\n"


def write_text_if_needed(path: Path, text: str, overwrite: bool) -> str:
    existed = path.exists()
    if existed and not overwrite:
        return "preserved"
    path.write_text(text, encoding="utf-8")
    return "overwritten" if existed else "created"


def main() -> int:
    args = parse_args()
    state_dir = resolve_state_dir(args.codex_home, args.state_dir)

    missing_templates = [
        str(path.relative_to(SKILL_ROOT))
        for path in (USER_CONTEXT_TEMPLATE, ONBOARDING_STATE_TEMPLATE)
        if not path.exists()
    ]
    if missing_templates:
        print(f"Missing {PLUGIN_LABEL} bundled state source(s):", file=sys.stderr)
        for missing in missing_templates:
            print(f"- {missing}", file=sys.stderr)
        return 1

    try:
        user_context_scaffold = build_user_context_scaffold()
        validate_json(ONBOARDING_STATE_TEMPLATE)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid {PLUGIN_LABEL} bundled state source: {exc}", file=sys.stderr)
        return 1

    state_dir.mkdir(parents=True, exist_ok=True)
    user_context_path = state_dir / "user-context.md"
    onboarding_state_path = state_dir / "onboarding-state.json"

    user_context_result = write_text_if_needed(
        user_context_path,
        USER_CONTEXT_NOTE + user_context_scaffold,
        args.overwrite,
    )
    onboarding_state_result = write_text_if_needed(
        onboarding_state_path,
        ONBOARDING_STATE_TEMPLATE.read_text(encoding="utf-8"),
        args.overwrite,
    )

    try:
        validate_json(onboarding_state_path)
    except json.JSONDecodeError as exc:
        print(f"Invalid written {PLUGIN_LABEL} state JSON: {exc}", file=sys.stderr)
        return 1

    print(f"{PLUGIN_LABEL} state directory: {state_dir}")
    print(f"user-context.md: {user_context_result}")
    print(f"onboarding-state.json: {onboarding_state_result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
