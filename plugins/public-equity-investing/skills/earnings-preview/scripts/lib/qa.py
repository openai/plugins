#!/usr/bin/env python3
"""QA and validation rules.

Two layers:
- Plan validation: required keys, obvious type errors.
- Data validation: required files, required columns, basic sanity checks.

This module is deliberately conservative: "errors" are hard failures, "warnings" require review.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .io_utils import read_table, require_columns

REQUIRED_PLAN_KEYS = [
    "ticker",
    "fiscal_period_id",
    "sector_pack",
    "freeze_time",
    "input_dir",
    "output_dir",
]

# Minimal required input files for deterministic outputs
DEFAULT_INPUT_FILES = {
    "company_master": "company_master.csv",
    "fiscal_period_index": "fiscal_period_index.csv",
    "reported_financials": "reported_financials.csv",
    "kpi_timeseries": "kpi_timeseries.csv",
    "consensus_estimates": "consensus_estimates.csv",
}

OPTIONAL_INPUT_FILES = {
    "guidance_history": "guidance_history.csv",
    "event_calendar": "event_calendar.csv",
    "price_returns": "price_returns.csv",
    "whisper_estimates": "whisper_estimates.csv",
    "qual_notes": "qual_notes.csv",
    "scenario_assumptions": "scenario_assumptions.csv",
    "options_snapshot": "options_snapshot.csv",
}

REQUIRED_COLUMNS = {
    "company_master": ["ticker", "company_name", "sector_pack", "currency_code"],
    "fiscal_period_index": ["fiscal_period_id", "fiscal_year", "fiscal_quarter"],
    "reported_financials": ["ticker", "fiscal_period_id", "metric_id", "value", "unit", "scale"],
    "kpi_timeseries": ["ticker", "fiscal_period_id", "metric_id", "value", "unit", "scale"],
    "consensus_estimates": [
        "ticker",
        "fiscal_period_id",
        "metric_id",
        "estimate_value",
        "statistic",
        "snapshot_datetime",
    ],
    "guidance_history": ["ticker", "fiscal_period_id", "metric_id", "guide_date"],
    "event_calendar": ["ticker", "event_datetime_utc", "event_type"],
    "price_returns": ["ticker", "date"],
    "whisper_estimates": ["ticker", "fiscal_period_id", "metric_id", "snapshot_datetime"],
    "qual_notes": ["ticker", "fiscal_period_id", "note"],
    "scenario_assumptions": ["scenario_name", "metric_id", "delta_type", "delta_value"],
    "options_snapshot": ["ticker", "asof_datetime"],
}


def resolve_input_paths(plan: dict, skill_root: Path) -> dict[str, Path]:
    """Return a dict of input_name -> Path.

    Rules:
    - If plan.inputs.<name> exists, use it (relative to skill root unless absolute)
    - Else default to plan.input_dir/<default_filename>
    """
    input_dir = Path(plan.get("input_dir", ""))
    if not input_dir.is_absolute():
        input_dir = (skill_root / input_dir).resolve()

    overrides = plan.get("inputs", {}) or {}

    paths: dict[str, Path] = {}
    for name, filename in {**DEFAULT_INPUT_FILES, **OPTIONAL_INPUT_FILES}.items():
        if isinstance(overrides, dict) and overrides.get(name):
            p = Path(str(overrides[name]))
            if not p.is_absolute():
                p = (skill_root / p).resolve()
        else:
            p = (input_dir / filename).resolve()
        paths[name] = p
    return paths


def validate_plan(plan: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for k in REQUIRED_PLAN_KEYS:
        if k not in plan or plan.get(k) in (None, ""):
            errors.append(f"Missing required plan field: {k}")

    # Light checks
    if (
        "ticker" in plan
        and isinstance(plan.get("ticker"), str)
        and plan.get("ticker") != plan.get("ticker").upper()
    ):
        warnings.append("Ticker is not uppercase; this is allowed but can cause joins to fail.")

    # Freeze time should look like ISO
    ft = str(plan.get("freeze_time", ""))
    if ft and "T" not in ft:
        warnings.append("freeze_time does not look like ISO8601 (missing 'T').")

    return errors, warnings


def validate_inputs(
    plan: dict, skill_root: Path
) -> tuple[list[str], list[str], dict[str, pd.DataFrame]]:
    """Validate input files and required columns. Returns (errors, warnings, loaded_dfs)."""
    errors: list[str] = []
    warnings: list[str] = []
    dfs: dict[str, pd.DataFrame] = {}

    paths = resolve_input_paths(plan, skill_root)

    # Required files must exist
    for name in DEFAULT_INPUT_FILES.keys():
        p = paths[name]
        if not p.exists():
            errors.append(f"Missing required input file: {name} ({p})")

    # Optional files
    for name in OPTIONAL_INPUT_FILES.keys():
        p = paths[name]
        if not p.exists():
            warnings.append(f"Optional input file not found: {name} ({p})")

    # If required missing, stop early
    if errors:
        return errors, warnings, dfs

    # Load and validate columns
    for name, p in paths.items():
        if not p.exists():
            continue
        try:
            df = read_table(p)
        except Exception as e:
            if name in DEFAULT_INPUT_FILES:
                errors.append(f"Failed reading required file {name}: {p} ({e})")
            else:
                warnings.append(f"Failed reading optional file {name}: {p} ({e})")
            continue

        req_cols = REQUIRED_COLUMNS.get(name)
        if req_cols:
            missing = require_columns(df, req_cols, name)
            if missing:
                msg = f"{name} missing required columns: {missing}"
                if name in DEFAULT_INPUT_FILES:
                    errors.append(msg)
                else:
                    warnings.append(msg)
        dfs[name] = df

    # Period existence checks
    fiscal_period_id = plan.get("fiscal_period_id")
    if fiscal_period_id and "fiscal_period_index" in dfs:
        fpi = dfs["fiscal_period_index"]
        if fiscal_period_id not in set(fpi.get("fiscal_period_id", [])):
            errors.append(f"fiscal_period_id {fiscal_period_id} not found in fiscal_period_index")

    # Consensus availability
    if fiscal_period_id and "consensus_estimates" in dfs:
        ce = dfs["consensus_estimates"]
        mask = (ce.get("ticker") == plan.get("ticker")) & (
            ce.get("fiscal_period_id") == fiscal_period_id
        )
        if mask.sum() == 0:
            errors.append(
                f"No consensus_estimates rows found for {plan.get('ticker')} {fiscal_period_id}"
            )

    return errors, warnings, dfs
