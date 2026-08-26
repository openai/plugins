from __future__ import annotations

import re
from datetime import datetime

from model_update_dates import freshness
from model_update_format import first_number, first_text, fmt_number, text
from model_update_validate import resolve_action, validate_mapping_row

EPS_DISTORTION_TERMS = (
    "asset sale",
    "below-the-line",
    "equity investment",
    "fair value",
    "fx",
    "gain",
    "impairment",
    "litigation",
    "loss",
    "mark-to-market",
    "non-operating",
    "non-recurring",
    "one-time",
    "pension",
    "restructuring",
    "share count",
    "tax",
)

NON_UPDATE_TREATMENTS = {
    "reference_only",
    "missing_model_architecture",
    "rebuild_required",
    "assumption_required",
}


def mapping_treatment(row: dict[str, str]) -> str:
    raw = first_text(row, ("mapping_treatment", "model_treatment", "updateability")).lower()
    normalized = re.sub(r"[-\s]+", "_", raw).strip("_")
    aliases = {
        "informational": "reference_only",
        "missing_architecture": "missing_model_architecture",
        "missing_model_line": "missing_model_architecture",
        "safe": "safe_update",
        "update_candidate": "safe_update",
    }
    if normalized:
        return aliases.get(normalized, normalized)
    action = text(row.get("update_action")).lower()
    if action in NON_UPDATE_TREATMENTS:
        return action
    return "safe_update"


def treatment_action(treatment: str, fallback_action: str) -> str:
    return {
        "reference_only": "reference_only",
        "missing_model_architecture": "rebuild_required",
        "rebuild_required": "rebuild_required",
        "assumption_required": "input_required",
    }.get(treatment, fallback_action)


def treatment_status(treatment: str, flags: list[str]) -> tuple[str, str]:
    if treatment == "reference_only":
        return "reference_only", ""
    if treatment == "missing_model_architecture":
        return "blocked_missing_model_architecture", "missing_model_architecture"
    if treatment == "rebuild_required":
        return "blocked_rebuild_required", "rebuild_required"
    if treatment == "assumption_required":
        return "blocked_assumption_required", "assumption_required"
    return ("blocked", "") if flags else ("ready_for_review", "")


def eps_quality_flags(row: dict[str, str], model_line: str, source_metric: str) -> list[str]:
    combined_metric = f"{model_line} {source_metric}".lower()
    if "eps" not in combined_metric and "net income" not in combined_metric:
        return []

    flags: list[str] = []
    basis = first_text(row, ("earnings_basis", "gaap_flag", "metric_basis"))
    notes = " ".join(
        first_text(row, (field,)) for field in ("notes", "commentary", "source_note", "issue_flags")
    ).lower()

    if not basis:
        flags.append("eps_basis_missing")
    if any(term in notes for term in EPS_DISTORTION_TERMS):
        flags.append("eps_quality_review_required")
    normalized_basis = basis.lower().replace("_", "-").strip()
    if (
        normalized_basis.startswith("gaap")
        and not normalized_basis.startswith("non-gaap")
        and "adjust" not in notes
        and "operating" not in notes
    ):
        flags.append("gaap_eps_requires_recurring_driver_check")

    return flags


def build_source_to_model_row(
    row: dict[str, str],
    model_line: str,
    source_metric: str,
    source_id: str,
    proposed: float | None,
    current: float | None,
    treatment: str,
    fresh_status: str,
    flags: list[str],
) -> dict[str, str]:
    is_update_candidate = treatment not in NON_UPDATE_TREATMENTS
    delta = (
        proposed - current
        if is_update_candidate and proposed is not None and current is not None
        else None
    )
    delta_pct = delta / abs(current) if delta is not None and current not in (None, 0) else None
    flags = flags + eps_quality_flags(row, model_line, source_metric)
    action = treatment_action(treatment, resolve_action(row, proposed, current, delta))
    confidence = text(row.get("confidence")) or ("low" if flags else "medium")
    current_text = first_text(row, ("current_model_value", "model_value"))
    proposed_text = fmt_number(proposed) if is_update_candidate else ""
    workbook_sheet = first_text(row, ("workbook_sheet", "target_sheet", "model_sheet", "sheet"))
    workbook_cell = first_text(row, ("workbook_cell", "target_cell", "model_cell", "cell"))
    review_status, blocked_reason = treatment_status(treatment, flags)

    return {
        "company": text(row.get("company")),
        "ticker": text(row.get("ticker")),
        "fiscal_period": first_text(row, ("fiscal_period", "period")),
        "model_section": first_text(row, ("model_section", "tab")),
        "model_line": model_line,
        "mapping_treatment": treatment,
        "workbook_sheet": workbook_sheet,
        "workbook_cell": workbook_cell,
        "source_metric": source_metric,
        "source_value": first_text(row, ("source_value", "actual_value")),
        "current_model_value": current_text,
        "proposed_model_value": proposed_text,
        "prior_value": first_text(row, ("prior_value",)) or current_text,
        "new_value": (first_text(row, ("new_value",)) or proposed_text)
        if is_update_candidate
        else "",
        "delta": fmt_number(delta),
        "delta_pct": "" if delta_pct is None else f"{delta_pct:.2%}",
        "update_action": action,
        "overwrite_formula_allowed": first_text(
            row,
            ("overwrite_formula_allowed", "allow_formula_overwrite", "formula_overwrite_allowed"),
        ),
        "source_id": source_id,
        "source_name": text(row.get("source_name")),
        "source_location": text(row.get("source_location")),
        "evidence_label": text(row.get("evidence_label")) or "fact_source_reported",
        "as_of_date": first_text(row, ("as_of_date", "source_as_of_date")),
        "freshness_status": fresh_status,
        "confidence": confidence,
        "review_status": review_status,
        "applied_to_workbook": "",
        "blocked_reason": blocked_reason,
        "issue_flags": "; ".join(flags),
    }


def build_source_to_model_rows(
    rows: list[dict[str, str]],
    run_date: datetime,
    stale_days: int,
) -> tuple[list[dict[str, str]], list[str], list[str]]:
    output: list[dict[str, str]] = []
    warnings: list[str] = []
    failures: list[str] = []

    for index, row in enumerate(rows, start=2):
        source_id = text(row.get("source_id"))
        model_line = first_text(row, ("model_line", "model_line_item"))
        source_metric = first_text(row, ("source_metric", "metric"))
        treatment = mapping_treatment(row)
        proposed = (
            first_number(row, ("proposed_model_value", "source_value", "actual_value"))
            if treatment not in NON_UPDATE_TREATMENTS
            else None
        )
        current = first_number(row, ("current_model_value", "model_value"))
        fresh_status, fresh_warning = freshness(row, run_date, stale_days)
        row_flags, row_warnings, row_failures = validate_mapping_row(
            row,
            index,
            source_id,
            model_line,
            source_metric,
            proposed,
            fresh_warning,
            proposed_required=treatment not in NON_UPDATE_TREATMENTS,
        )

        warnings.extend(row_warnings)
        failures.extend(row_failures)
        output.append(
            build_source_to_model_row(
                row,
                model_line,
                source_metric,
                source_id,
                proposed,
                current,
                treatment,
                fresh_status,
                row_flags,
            )
        )

    return output, warnings, failures
