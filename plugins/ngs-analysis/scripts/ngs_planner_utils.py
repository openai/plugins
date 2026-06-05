#!/usr/bin/env python3
"""Shared table and command-plan helpers for NGS runner build-outs."""

from __future__ import annotations

import csv
import shlex
from pathlib import Path
from typing import Any

from ngs_run_utils import write_text


def detect_delimiter(path: Path) -> str:
    if path.suffix.lower() in {".tsv", ".tab"}:
        return "\t"
    return ","


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=detect_delimiter(path))
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
        return rows, list(reader.fieldnames or [])


def resolve_path(raw: str | None, base: Path) -> Path | None:
    if not raw:
        return None
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def shell_join(cmd: list[str | Path]) -> str:
    return shlex.join([str(item) for item in cmd])


def write_command_script(
    path: Path, commands: list[str], *, header: list[str] | None = None
) -> None:
    lines = ["#!/usr/bin/env bash", "set -euo pipefail"]
    if header:
        lines.extend(header)
    lines.extend(commands)
    write_text(path, "\n".join(lines) + "\n")


def command_plan_entry(
    name: str, command: list[str | Path] | str, *, outputs: list[str] | None = None
) -> dict[str, Any]:
    command_string = command if isinstance(command, str) else shell_join(command)
    return {"name": name, "command": command_string, "outputs": outputs or []}


def normalize_sample_name(value: str | None, fallback: str) -> str:
    value = (value or "").strip()
    if not value:
        return fallback
    safe = []
    for char in value:
        safe.append(char if char.isalnum() or char in {"_", "-", "."} else "_")
    return "".join(safe).strip("_") or fallback
