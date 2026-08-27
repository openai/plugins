#!/usr/bin/env python3
"""Shared Public Equity Investing state path resolution."""

from __future__ import annotations

import os
from pathlib import Path

MARKETPLACE_ID = "openai-monorepo"
PLUGIN_ID = "public-equity-investing"
PLUGIN_LABEL = "Public Equity Investing"
STATE_FILENAMES = (
    "user-context.md",
    # Legacy readiness state is never created or read, but reset should clear it.
    "category-state.json",
    "onboarding-state.json",
)

STATE_DIR_HELP = (
    f"{PLUGIN_LABEL} state directory. Defaults to "
    f"<codex-home>/state/plugins/{MARKETPLACE_ID}/{PLUGIN_ID}."
)


def default_codex_home() -> Path:
    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        return Path(env_home).expanduser()
    return Path.home() / ".codex"


def configured_state_dir(codex_home: Path) -> Path:
    return codex_home / "state/plugins" / MARKETPLACE_ID / PLUGIN_ID


def resolve_state_dir(codex_home: Path | None, state_dir: Path | None) -> Path:
    if state_dir:
        return state_dir.expanduser()

    resolved_home = codex_home.expanduser() if codex_home else default_codex_home()
    return configured_state_dir(resolved_home)
