from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("input CSV must include a header row")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError("input CSV must include at least one row")
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_run_log(
    path: Path,
    *,
    status: str,
    input_path: Path,
    row_count: int,
    outputs: dict[str, str],
    warnings: list[str],
    failures: list[str],
    source_basis: list[dict[str, str]] | None = None,
    artifact_level: str = "deterministic_export",
    workbook_mode: str = "update_map_export",
    primary_human_deliverable: str | None = None,
    support_artifacts: list[str] | None = None,
    workbook_preflight: dict[str, object] | None = None,
    workbook_update_summary: dict[str, object] | None = None,
    recalculation_warning: dict[str, object] | None = None,
    capability_boundary: str | None = None,
    artifact_readiness: str | None = None,
    model_readiness: str | None = None,
) -> None:
    descriptions = {
        "updated_model": "Copied XLSX model with safe mapped input updates and review tabs.",
        "model_update_control_pack": "Copied XLSX workbook with review/control tabs; model cells were not edited.",
        "source_to_model": "Source-to-model mapping with treatment and updateable-value deltas.",
        "change_log": "Review-ready model change log.",
        "tieout_checklist": "Model audit handoff checklist.",
        "model_update_citations": "Workbook/sheet/cell provenance for changed and blocked model targets.",
        "run_log": "Status, warnings, hard failures, workbook preflight, and output manifest.",
        "manifest": "Machine-readable output manifest.",
    }
    output_manifest = [
        {
            "key": key,
            "path": artifact_path,
            "required": True,
            "written": key in {"run_log", "manifest"} or Path(artifact_path).exists(),
            "description": descriptions.get(key, "Generated artifact."),
        }
        for key, artifact_path in outputs.items()
    ]
    support_artifacts = support_artifacts or [
        artifact_path
        for artifact_path in outputs.values()
        if primary_human_deliverable is None or artifact_path != primary_human_deliverable
    ]
    if model_readiness is None:
        if failures:
            model_readiness = "not_ready_validation_failure"
        elif workbook_mode == "xlsx_control_pack":
            model_readiness = "not_updated_requires_mapping_or_rebuild"
        elif workbook_mode == "xlsx_update_copy":
            model_readiness = "updated_requires_tieout"
        else:
            model_readiness = "mapping_package_ready_for_review"
    if artifact_readiness is None:
        artifact_readiness = "not_ready" if failures else "ready_for_review"
    payload = {
        "status": status,
        "model_status": model_readiness,
        "artifact_readiness": artifact_readiness,
        "model_readiness": model_readiness,
        "artifact_level": artifact_level,
        "workbook_mode": workbook_mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path),
        "row_count": row_count,
        "source_basis": source_basis or [],
        "outputs": outputs,
        "primary_human_deliverable": primary_human_deliverable,
        "support_artifacts": support_artifacts,
        "output_manifest": output_manifest,
        "warnings": warnings,
        "hard_failures": failures,
        "missing_source_id_count": sum("source_id is required" in item for item in failures),
        "workbook_write_rejected_count": sum(
            "original workbook mutation" in item for item in failures
        ),
        "model_audit_tieout_required": True,
        "handoff_skill": "model-audit-tieout",
        "capability_boundary": capability_boundary
        or "CSV update-map materializer only; use the workbook materializer for safe copied-XLSX updates",
    }
    if workbook_preflight is not None:
        payload["workbook_preflight"] = workbook_preflight
    if workbook_update_summary is not None:
        payload["workbook_update_summary"] = workbook_update_summary
    if recalculation_warning is not None:
        payload["recalculation_warning"] = recalculation_warning
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest_path = path.parent / "manifest.json"
    manifest_payload = {
        "artifact_mode": workbook_mode,
        "primary_human_deliverable": primary_human_deliverable,
        "human_deliverables": [primary_human_deliverable] if primary_human_deliverable else [],
        "support_artifacts": support_artifacts,
        "outputs": output_manifest,
    }
    manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")
