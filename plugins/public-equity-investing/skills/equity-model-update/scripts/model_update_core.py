from __future__ import annotations

from datetime import datetime
from pathlib import Path

from model_update_artifacts import build_change_log, build_tieout_checklist
from model_update_fields import CHANGE_LOG_FIELDS, SOURCE_TO_MODEL_FIELDS, TIEOUT_FIELDS
from model_update_io import load_rows, write_csv, write_run_log
from model_update_rows import build_source_to_model_rows


def output_paths(out_dir: Path) -> dict[str, str]:
    return {
        "source_to_model": str(out_dir / "source_to_model.csv"),
        "change_log": str(out_dir / "change_log.csv"),
        "tieout_checklist": str(out_dir / "tieout_checklist.csv"),
        "run_log": str(out_dir / "run_log.json"),
        "manifest": str(out_dir / "manifest.json"),
    }


def log_failure(
    out_dir: Path,
    input_csv: Path,
    row_count: int,
    outputs: dict[str, str],
    warnings: list[str],
    failures: list[str],
) -> int:
    write_run_log(
        out_dir / "run_log.json",
        status="failed",
        input_path=input_csv,
        row_count=row_count,
        outputs=outputs,
        warnings=warnings,
        failures=failures,
    )
    for failure in failures:
        print(f"ERROR: {failure}")
    return 1


def materialize(input_csv: Path, out_dir: Path, run_date: datetime, stale_days: int) -> int:
    rows = load_rows(input_csv)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = output_paths(out_dir)
    source_rows, warnings, failures = build_source_to_model_rows(rows, run_date, stale_days)

    if failures:
        return log_failure(out_dir, input_csv, len(rows), outputs, warnings, failures)

    write_csv(out_dir / "source_to_model.csv", source_rows, SOURCE_TO_MODEL_FIELDS)
    write_csv(out_dir / "change_log.csv", build_change_log(source_rows), CHANGE_LOG_FIELDS)
    write_csv(out_dir / "tieout_checklist.csv", build_tieout_checklist(source_rows), TIEOUT_FIELDS)
    source_basis = [
        {
            "source_id": row.get("source_id", ""),
            "source_name": row.get("source_name", ""),
            "source_location": row.get("source_location", ""),
            "evidence_label": row.get("evidence_label", ""),
            "as_of_date": row.get("as_of_date", ""),
            "confidence": row.get("confidence", ""),
        }
        for row in source_rows
        if row.get("source_id")
    ]
    write_run_log(
        out_dir / "run_log.json",
        status="completed",
        input_path=input_csv,
        row_count=len(rows),
        outputs=outputs,
        warnings=warnings,
        failures=[],
        source_basis=source_basis,
    )
    print(f"Wrote equity model update artifacts to {out_dir}")
    return 0
