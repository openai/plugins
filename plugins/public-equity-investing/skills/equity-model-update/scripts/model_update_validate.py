from __future__ import annotations

from model_update_fields import TRUTHY
from model_update_format import text


def wants_workbook_write(row: dict[str, str]) -> bool:
    fields = ("workbook_write_requested", "direct_workbook_write", "write_to_workbook")
    return any(text(row.get(field)).lower() in TRUTHY for field in fields)


def resolve_action(
    row: dict[str, str], proposed: float | None, current: float | None, delta: float | None
) -> str:
    requested = text(row.get("update_action"))
    if requested:
        return requested
    if proposed is None:
        return "input_required"
    if current is None:
        return "add_or_map"
    if abs(delta or 0.0) > 1e-9:
        return "update"
    return "no_change"


def validate_mapping_row(
    row: dict[str, str],
    index: int,
    source_id: str,
    model_line: str,
    source_metric: str,
    proposed: float | None,
    fresh_warning: str | None,
    proposed_required: bool = True,
) -> tuple[list[str], list[str], list[str]]:
    flags: list[str] = []
    warnings: list[str] = []
    failures: list[str] = []

    if not source_id:
        flags.append("missing_source_id")
        failures.append(f"row {index}: source_id is required")
    if wants_workbook_write(row):
        flags.append("workbook_update_requires_safe_copy")
        warnings.append(
            f"row {index}: workbook update requested; use materialize_workbook_update.py for a copied XLSX update"
        )
    if not model_line:
        flags.append("missing_model_line")
        failures.append(f"row {index}: model_line is required")
    if not source_metric:
        flags.append("missing_source_metric")
        warnings.append(f"row {index}: source_metric is missing")
    if proposed_required and proposed is None:
        flags.append("missing_proposed_value")
        warnings.append(f"row {index}: proposed value is missing or non-numeric")
    if fresh_warning:
        flags.append(fresh_warning.split()[0])
        warnings.append(f"row {index}: {fresh_warning}")
    return flags, warnings, failures
