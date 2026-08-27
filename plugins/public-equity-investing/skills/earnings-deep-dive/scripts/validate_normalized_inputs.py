#!/usr/bin/env python3
"""Validate normalized CSV inputs (metrics/estimates/guidance/quotes/driver updates).

Rules enforced:
- Required columns exist
- Non-empty rows for required deliverables
- For any non-MISSING metric value, SourceTag must be present and not MISSING
- Non-GAAP rows must include comparable GAAP metric + reconciliation source

Exit codes:
  0 = valid (may still have warnings)
  1 = errors found
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

if __name__ == "__main__" and any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
    print("Usage: python scripts/validate_normalized_inputs.py plan.json")
    print("Validate normalized CSV inputs for the earnings deep-dive pipeline.")
    raise SystemExit(0)

import pandas as pd

try:
    from .utils.io_utils import ensure_dir, read_json, write_text
    from .utils.validation_utils import as_float_or_none, is_missing, require_columns
except ImportError:
    from utils.io_utils import ensure_dir, read_json, write_text
    from utils.validation_utils import as_float_or_none, is_missing, require_columns


REQ_METRICS = [
    "MetricName",
    "Period",
    "Value",
    "Units",
    "GAAP_Flag",
    "Segment",
    "IsTearSheet",
    "DisplayOrder",
    "SourceTag",
]

REQ_ESTIMATES = [
    "MetricName",
    "Period",
    "EstimateType",
    "Value",
    "Units",
    "AsOf",
    "Source",
]

REQ_GUIDANCE = [
    "MetricName",
    "Period",
    "Low",
    "High",
    "Units",
    "GAAP_Flag",
    "SourceTag",
]

REQ_QUOTES = [
    "Section",
    "Speaker",
    "Questioner",
    "TopicTag",
    "QuoteText",
    "SourceTag",
]

REQ_DRIVER_UPDATES = [
    "DriverID",
    "Period",
    "NewValue",
    "Units",
    "Why",
    "SourceTag",
]


def _read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _validate_metrics(df: pd.DataFrame, require_source_tags: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_cols = require_columns(df, REQ_METRICS)
    if missing_cols:
        errors.append(f"metrics.csv missing columns: {missing_cols}")
        return errors, warnings

    # Basic row checks
    if len(df) == 0:
        errors.append("metrics.csv has no rows")
        return errors, warnings

    for i, row in df.iterrows():
        metric = row.get("MetricName")
        value = row.get("Value")
        src = row.get("SourceTag")
        gaap_flag = str(row.get("GAAP_Flag") or "").strip()

        if is_missing(metric):
            errors.append(f"metrics.csv row {i + 2}: MetricName is required")

        if not is_missing(value):
            # Only enforce SourceTag when the metric is present
            if require_source_tags and is_missing(src):
                errors.append(
                    f"metrics.csv row {i + 2} ({metric}): Value present but SourceTag is MISSING"
                )

        if gaap_flag == "Non-GAAP":
            comp = row.get("ComparableGAAPMetricName")
            recon = row.get("ReconciliationSourceTag")
            if is_missing(comp) or is_missing(recon):
                errors.append(
                    f"metrics.csv row {i + 2} ({metric}): Non-GAAP requires ComparableGAAPMetricName and ReconciliationSourceTag"
                )

    return errors, warnings


def _validate_estimates(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_cols = require_columns(df, REQ_ESTIMATES)
    if missing_cols:
        errors.append(f"estimates.csv missing columns: {missing_cols}")
        return errors, warnings

    allowed = {"Consensus", "Internal", "Whisper"}
    for i, row in df.iterrows():
        et = str(row.get("EstimateType") or "").strip()
        if et and et not in allowed:
            errors.append(
                f"estimates.csv row {i + 2}: EstimateType must be one of {sorted(allowed)}"
            )
    return errors, warnings


def _validate_guidance(df: pd.DataFrame, require_source_tags: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_cols = require_columns(df, REQ_GUIDANCE)
    if missing_cols:
        errors.append(f"guidance.csv missing columns: {missing_cols}")
        return errors, warnings

    for i, row in df.iterrows():
        metric = row.get("MetricName")
        low = as_float_or_none(row.get("Low"))
        high = as_float_or_none(row.get("High"))
        src = row.get("SourceTag")

        if require_source_tags and (low is not None or high is not None) and is_missing(src):
            errors.append(
                f"guidance.csv row {i + 2} ({metric}): guidance present but SourceTag is MISSING"
            )

        if low is not None and high is not None and low > high:
            errors.append(f"guidance.csv row {i + 2} ({metric}): Low > High")

        if (low is None) ^ (high is None):
            warnings.append(
                f"guidance.csv row {i + 2} ({metric}): only one of Low/High is populated"
            )

    return errors, warnings


def _validate_quotes(df: pd.DataFrame, require_source_tags: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_cols = require_columns(df, REQ_QUOTES)
    if missing_cols:
        errors.append(f"quotes.csv missing columns: {missing_cols}")
        return errors, warnings

    allowed = {"Prepared", "Q&A"}
    for i, row in df.iterrows():
        section = str(row.get("Section") or "").strip()
        if section and section not in allowed:
            errors.append(f"quotes.csv row {i + 2}: Section must be Prepared or Q&A")

        qt = row.get("QuoteText")
        if not is_missing(qt) and require_source_tags and is_missing(row.get("SourceTag")):
            errors.append(f"quotes.csv row {i + 2}: QuoteText present but SourceTag is MISSING")

    return errors, warnings


def _validate_driver_updates(
    df: pd.DataFrame, require_source_tags: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_cols = require_columns(df, REQ_DRIVER_UPDATES)
    if missing_cols:
        errors.append(f"driver_updates.csv missing columns: {missing_cols}")
        return errors, warnings

    for i, row in df.iterrows():
        dv = row.get("NewValue")
        if not is_missing(dv) and as_float_or_none(dv) is None:
            warnings.append(
                f"driver_updates.csv row {i + 2}: NewValue is non-numeric (will be written as text)"
            )

        if require_source_tags and not is_missing(dv) and is_missing(row.get("SourceTag")):
            errors.append(
                f"driver_updates.csv row {i + 2}: NewValue present but SourceTag is MISSING"
            )

    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_normalized_inputs.py plan.json")
        return 1

    plan_path = sys.argv[1]
    plan = read_json(plan_path)

    out_dir = plan.get("outputs", {}).get("output_dir", "output")
    audit_dir = ensure_dir(str(Path(out_dir) / "audit"))

    require_source_tags = bool(plan.get("controls", {}).get("require_source_tags", True))

    norm = plan.get("inputs", {}).get("normalized", {})
    paths = {
        "metrics": norm.get("metrics_csv"),
        "estimates": norm.get("estimates_csv"),
        "guidance": norm.get("guidance_csv"),
        "quotes": norm.get("quotes_csv"),
        "driver_updates": norm.get("driver_updates_csv"),
    }

    errors: list[str] = []
    warnings: list[str] = []

    dfs: dict[str, pd.DataFrame] = {}
    for k, p in paths.items():
        if not p:
            errors.append(f"Plan missing normalized path for {k}")
            continue
        if not Path(p).exists():
            errors.append(f"Missing file: {p} (copy from assets/templates)")
            continue
        try:
            dfs[k] = _read_csv(p)
        except Exception as e:
            errors.append(f"Failed to read {p}: {e}")

    if "metrics" in dfs:
        e, w = _validate_metrics(dfs["metrics"], require_source_tags)
        errors += e
        warnings += w
    if "estimates" in dfs:
        e, w = _validate_estimates(dfs["estimates"])
        errors += e
        warnings += w
    if "guidance" in dfs:
        e, w = _validate_guidance(dfs["guidance"], require_source_tags)
        errors += e
        warnings += w
    if "quotes" in dfs:
        e, w = _validate_quotes(dfs["quotes"], require_source_tags)
        errors += e
        warnings += w
    if "driver_updates" in dfs:
        e, w = _validate_driver_updates(dfs["driver_updates"], require_source_tags)
        errors += e
        warnings += w

    # Render report
    lines: list[str] = []
    lines.append("# Normalized Inputs Validation Report\n")
    lines.append(f"Plan: `{plan_path}`\n")

    if warnings:
        lines.append("## Warnings")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    if errors:
        lines.append("## Errors")
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")

    if not errors:
        lines.append("✅ Inputs are valid (warnings may exist).")

    report_path = audit_dir / "ValidationReport_NormalizedInputs.md"
    write_text("\n".join(lines), str(report_path))

    # Console
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print(f"\nSee {report_path}")
        return 1

    print(f"Inputs valid. See {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
