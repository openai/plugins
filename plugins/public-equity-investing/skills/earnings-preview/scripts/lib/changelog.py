#!/usr/bin/env python3
"""Changelog generation.

If a previous run_manifest.json exists in the output folder, diff it against the new manifest.
This is intentionally simple and only diffs file hashes and top-level plan settings.
"""

from __future__ import annotations

from pathlib import Path

from .io_utils import read_json


def diff_manifests(prev: dict, curr: dict) -> list[str]:
    lines: list[str] = []

    # Top-level fields
    for key in ["freeze_time", "consensus_statistic", "sector_pack", "fiscal_period_id"]:
        pv = prev.get(key)
        cv = curr.get(key)
        if pv != cv:
            lines.append(f"- {key}: {pv} -> {cv}")

    # Input file hashes
    prev_files = (prev.get("inputs", {}) or {}).get("files", {}) or {}
    curr_files = (curr.get("inputs", {}) or {}).get("files", {}) or {}
    for name in sorted(set(prev_files) | set(curr_files)):
        ph = (prev_files.get(name) or {}).get("sha256")
        ch = (curr_files.get(name) or {}).get("sha256")
        if ph != ch:
            lines.append(f"- input {name}: {ph} -> {ch}")

    if not lines:
        return ["- No changes vs prior manifest."]
    return lines


def maybe_write_changelog(output_run_dir: Path, new_manifest: dict) -> None:
    prev_path = output_run_dir / "run_manifest.previous.json"
    if not prev_path.exists():
        return
    prev = read_json(prev_path)
    if not isinstance(prev, dict):
        return
    lines = diff_manifests(prev, new_manifest)
    out_path = output_run_dir / "changelog.md"
    out_path.write_text("# Changelog\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
