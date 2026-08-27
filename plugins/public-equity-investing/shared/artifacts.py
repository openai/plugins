"""Shared deterministic artifact helpers for Public Equity Investing scripts.

These helpers standardize the boring but important bookkeeping around run logs,
output manifests, status labels, source basis, and warning/failure payloads.
They intentionally do not contain finance logic.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

STATUS_FAILED = "failed"
STATUS_COMPLETED = "completed"

MODEL_STATUS_NOT_DECISION_READY = "not-decision-ready"
MODEL_STATUS_SCREEN_GRADE = "screen-grade"
MODEL_STATUS_SENIOR_REVIEW_READY = "senior-review-ready"
MODEL_STATUS_DECISION_GRADE = "decision-grade"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: str | Path, obj: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def artifact_paths(output_dir: Path, filenames: Mapping[str, str]) -> dict[str, str]:
    return {key: str(output_dir / filename) for key, filename in filenames.items()}


def output_manifest(
    paths: Mapping[str, str],
    *,
    required: Iterable[str] | None = None,
    optional: Iterable[str] | None = None,
    written: Iterable[str] | None = None,
    descriptions: Mapping[str, str] | None = None,
    artifact_roles: Mapping[str, str] | None = None,
    hidden_unless_requested: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    required_keys = set(required or paths.keys())
    optional_keys = set(optional or [])
    written_keys = set(written or [])
    descriptions = descriptions or {}
    artifact_roles = artifact_roles or {}
    hidden_keys = set(hidden_unless_requested or [])
    return [
        {
            "key": key,
            "path": path,
            "required": key in required_keys and key not in optional_keys,
            "written": key in written_keys,
            "artifact_role": artifact_roles.get(key, "support_artifact"),
            "hidden_unless_requested": key in hidden_keys,
            "description": descriptions.get(key, "Deterministic Public Equity Investing artifact."),
        }
        for key, path in paths.items()
    ]


def normalize_message_items(items: Sequence[Any] | None) -> list[Any]:
    if not items:
        return []
    seen: set[str] = set()
    normalized: list[Any] = []
    for item in items:
        marker = (
            json.dumps(item, sort_keys=True, default=str) if isinstance(item, dict) else str(item)
        )
        if marker in seen:
            continue
        seen.add(marker)
        normalized.append(item)
    return normalized


def status_from_findings(
    hard_failures: Sequence[Any] | None,
    warnings: Sequence[Any] | None,
    *,
    placeholder_active: bool = False,
) -> str:
    if hard_failures:
        return MODEL_STATUS_NOT_DECISION_READY
    if placeholder_active:
        return MODEL_STATUS_SCREEN_GRADE
    if warnings:
        return MODEL_STATUS_SCREEN_GRADE
    return MODEL_STATUS_SENIOR_REVIEW_READY


def build_run_log(
    *,
    hard_failures: Sequence[Any] | None,
    warnings: Sequence[Any] | None,
    outputs: Mapping[str, str],
    output_manifest_rows: Sequence[Mapping[str, Any]],
    source_basis: Sequence[Mapping[str, Any]] | None = None,
    assumptions: Mapping[str, Any] | None = None,
    checks: Mapping[str, Any] | None = None,
    p0_handoff: Mapping[str, Any] | None = None,
    model_status: str | None = None,
    workbook_mode: str = "deterministic_export",
    artifact_level: str = "deterministic_export",
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    hard = normalize_message_items(hard_failures)
    warns = normalize_message_items(warnings)
    run_log: dict[str, Any] = {
        "status": STATUS_FAILED if hard else STATUS_COMPLETED,
        "model_status": model_status or status_from_findings(hard, warns),
        "workbook_mode": workbook_mode,
        "artifact_level": artifact_level,
        "generated_at": utc_now_iso(),
        "source_basis": list(source_basis or []),
        "hard_failures": hard,
        "warnings": warns,
        "assumptions": dict(assumptions or {}),
        "checks": dict(checks or {}),
        "outputs": dict(outputs),
        "output_manifest": [dict(row) for row in output_manifest_rows],
        "p0_handoff": dict(p0_handoff or {}),
    }
    if extra:
        run_log.update(extra)
    return run_log


def write_run_log_bundle(output_dir: Path, run_log: Mapping[str, Any]) -> None:
    write_json(output_dir / "run_log.json", dict(run_log))
    manifest: dict[str, Any] = {"outputs": list(run_log.get("output_manifest", []))}
    if "primary_human_deliverable" in run_log:
        manifest["primary_human_deliverable"] = run_log.get("primary_human_deliverable")
    if "support_artifacts" in run_log:
        manifest["support_artifacts"] = list(run_log.get("support_artifacts", []))
    write_json(output_dir / "manifest.json", manifest)
