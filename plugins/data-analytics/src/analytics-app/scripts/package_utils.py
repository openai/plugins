#!/usr/bin/env python3
"""Shared helpers for generated data analytics app packages."""

from __future__ import annotations

import fnmatch
import json
import shutil
from pathlib import Path
from typing import Any


class ContractError(Exception):
    """Raised when an analytics app package does not satisfy its contract."""


ALLOWED_SOURCE_EXTENSIONS = {".csv", ".json", ".md", ".sql", ".tsv", ".txt"}
SENSITIVE_FILE_NAMES = {".env", ".env.local", ".env.production", ".env.staging"}
SENSITIVE_FILE_GLOBS = {"*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*", "id_ed25519*"}
SENSITIVE_SCAN_SKIP_DIRS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".vite",
    "build",
    "dist",
    "node_modules",
    "__pycache__",
}
TEMPLATE_IGNORE_PATTERNS = (
    ".dashboard-data",
    ".report-data",
    "dist",
    "node_modules",
)


def slugify(value: str, fallback: str) -> str:
    chars: list[str] = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
            previous_dash = False
        elif not previous_dash:
            chars.append("-")
            previous_dash = True
    slug = "".join(chars).strip("-")
    return slug or fallback


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ContractError(f"Missing required file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")


def copy_template(template: Path, output: Path, *, force: bool = False) -> None:
    output = output.resolve()
    if output.exists() and any(output.iterdir()) and not force:
        raise RuntimeError(f"{output} already exists and is not empty; pass --force to replace it")
    if output.exists() and force:
        shutil.rmtree(output)
    shutil.copytree(
        template,
        output,
        ignore=shutil.ignore_patterns(*TEMPLATE_IGNORE_PATTERNS),
    )


def require_string(obj: dict[str, Any], field: str, path: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{path}.{field} must be a non-empty string")
    return value


def optional_list(obj: dict[str, Any], field: str, path: str) -> list[Any]:
    value = obj.get(field, [])
    if not isinstance(value, list):
        raise ContractError(f"{path}.{field} must be a list when present")
    return value


def require_list(obj: dict[str, Any], field: str, path: str) -> list[Any]:
    value = obj.get(field)
    if not isinstance(value, list):
        raise ContractError(f"{path}.{field} must be a list")
    return value


def require_unique_ids(items: list[Any], field_path: str) -> None:
    seen: set[str] = set()
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            continue
        if item_id in seen:
            raise ContractError(f"{field_path}[{idx}].id must be unique")
        seen.add(item_id)


def validate_relative_source_path(
    root: Path, source_path: str, path: str, package_label: str = "analytics app package"
) -> None:
    candidate = (root / source_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ContractError(f"{path}.path must stay inside the {package_label}") from exc
    if candidate.is_dir():
        raise ContractError(f"{path}.path must point to a file, not a directory")
    if candidate.suffix.lower() not in ALLOWED_SOURCE_EXTENSIONS:
        raise ContractError(f"{path}.path must use one of {sorted(ALLOWED_SOURCE_EXTENSIONS)}")


def validate_no_sensitive_files(root: Path, package_label: str = "analytics app") -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SENSITIVE_SCAN_SKIP_DIRS for part in relative.parts[:-1]):
            continue
        name = path.name
        if name in SENSITIVE_FILE_NAMES or any(
            fnmatch.fnmatch(name, pattern) for pattern in SENSITIVE_FILE_GLOBS
        ):
            raise ContractError(
                f"{package_label} package must not include sensitive files: {relative}"
            )
