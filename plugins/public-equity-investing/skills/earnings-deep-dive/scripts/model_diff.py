#!/usr/bin/env python3
"""Produce a signal-oriented model diff using DriverRegistry + OutputRegistry.

This diff intentionally ignores "cell noise" and compares only mapped drivers and key outputs.

Notes:
- openpyxl does not recalc formulas. Output values may reflect cached Excel calculation state.
- If cached values are missing, the diff will show formulas instead.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

if __name__ == "__main__" and any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
    print(
        "Usage: python scripts/model_diff.py plan.json output/audit/WhatChanged_Diff.csv [new_model_path]"
    )
    print("Produce a signal-oriented model diff from driver and output registries.")
    raise SystemExit(0)

import openpyxl
import pandas as pd

try:
    from .utils.excel_utils import _resolve_named_range
    from .utils.io_utils import ensure_dir, read_json
    from .utils.validation_utils import as_float_or_none, is_missing
except ImportError:
    from utils.excel_utils import _resolve_named_range
    from utils.io_utils import ensure_dir, read_json
    from utils.validation_utils import as_float_or_none, is_missing


def _read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _get_cell(
    wb: openpyxl.Workbook,
    mapping_type: str,
    sheet: str | None,
    cell: str | None,
    named_range: str | None,
) -> tuple[str, str]:
    if mapping_type == "NamedRange":
        if not named_range:
            raise ValueError("NamedRange mapping requires NamedRange")
        loc = _resolve_named_range(wb, named_range)
        return loc.sheet, loc.cell
    if mapping_type == "Cell":
        if not sheet or not cell:
            raise ValueError("Cell mapping requires Worksheet + Cell")
        return sheet, cell
    raise ValueError(f"Unknown MappingType: {mapping_type}")


def _read_value_or_formula(
    path: Path, mapping_type: str, sheet: str | None, cell: str | None, named_range: str | None
) -> Any:
    # cached values
    wb_val = openpyxl.load_workbook(path, data_only=True)
    wb_for = openpyxl.load_workbook(path, data_only=False)
    try:
        s, c = _get_cell(wb_val, mapping_type, sheet, cell, named_range)
        v = wb_val[s][c].value
        if v is not None:
            return v
        # fallback to formula text
        sf, cf = _get_cell(wb_for, mapping_type, sheet, cell, named_range)
        f = wb_for[sf][cf].value
        return f if f is not None else None
    finally:
        wb_val.close()
        wb_for.close()


def write_diff(
    plan: dict[str, Any], out_csv_path: Path, new_model_path: Path | None = None
) -> Path:
    out_dir = Path(plan.get("outputs", {}).get("output_dir", "output"))
    ensure_dir(str(out_dir / "audit"))

    model = plan.get("inputs", {}).get("model", {})
    old_path = Path(model.get("prior_model_xlsx"))
    driver_reg_path = model.get("driver_registry_csv")
    out_reg_path = model.get("output_registry_csv")

    if new_model_path is None:
        # pick most recent model in output/model
        model_dir = out_dir / "model"
        if model_dir.exists():
            candidates = sorted(
                model_dir.glob("*.xls*"), key=lambda p: p.stat().st_mtime, reverse=True
            )
            if candidates:
                new_model_path = candidates[0]
    if new_model_path is None:
        raise ValueError("Could not determine new model path; pass new_model_path explicitly")

    if not old_path.exists():
        raise FileNotFoundError(f"Old model not found: {old_path}")
    if not new_model_path.exists():
        raise FileNotFoundError(f"New model not found: {new_model_path}")
    if is_missing(driver_reg_path):
        raise ValueError("inputs.model.driver_registry_csv is required for diff")

    driver_reg = _read_csv(driver_reg_path)
    out_reg = (
        _read_csv(out_reg_path)
        if out_reg_path and str(out_reg_path).upper() != "MISSING" and Path(out_reg_path).exists()
        else pd.DataFrame()
    )

    # Driver updates source tags (best-effort)
    norm = plan.get("inputs", {}).get("normalized", {})
    driver_updates_path = norm.get("driver_updates_csv")
    source_by_driver = {}
    if driver_updates_path and Path(driver_updates_path).exists():
        du = _read_csv(driver_updates_path)
        for _, r in du.iterrows():
            did = str(r.get("DriverID") or "").strip()
            if did:
                source_by_driver[did] = r.get("SourceTag")

    items: list[dict[str, Any]] = []

    # Drivers
    for _, r in driver_reg.iterrows():
        did = str(r.get("DriverID") or "").strip()
        if not did:
            continue
        mapping_type = str(r.get("MappingType") or "NamedRange").strip() or "NamedRange"
        ws = str(r.get("Worksheet") or "").strip() or None
        cell = str(r.get("Cell") or "").strip() or None
        nr = str(r.get("NamedRange") or "").strip() or None
        units = str(r.get("Units") or "").strip()

        old = _read_value_or_formula(old_path, mapping_type, ws, cell, nr)
        new = _read_value_or_formula(new_model_path, mapping_type, ws, cell, nr)

        old_f = as_float_or_none(old)
        new_f = as_float_or_none(new)
        delta = None
        if old_f is not None and new_f is not None:
            delta = new_f - old_f

        items.append(
            {
                "Category": "Driver",
                "Item": did,
                "Old": old,
                "New": new,
                "Delta": delta,
                "Units": units,
                "PrimaryImpact": "MISSING",
                "SourceTag": source_by_driver.get(did, "MISSING"),
                "Notes": f"{mapping_type}:{nr or ''}{ws or ''}{cell or ''}",
            }
        )

    # Outputs
    if not out_reg.empty:
        for _, r in out_reg.iterrows():
            oid = str(r.get("OutputID") or "").strip()
            if not oid:
                continue
            mapping_type = str(r.get("MappingType") or "NamedRange").strip() or "NamedRange"
            ws = str(r.get("Worksheet") or "").strip() or None
            cell = str(r.get("Cell") or "").strip() or None
            nr = str(r.get("NamedRange") or "").strip() or None
            units = str(r.get("Units") or "").strip()

            old = _read_value_or_formula(old_path, mapping_type, ws, cell, nr)
            new = _read_value_or_formula(new_model_path, mapping_type, ws, cell, nr)

            old_f = as_float_or_none(old)
            new_f = as_float_or_none(new)
            delta = None
            if old_f is not None and new_f is not None:
                delta = new_f - old_f

            items.append(
                {
                    "Category": "Output",
                    "Item": oid,
                    "Old": old,
                    "New": new,
                    "Delta": delta,
                    "Units": units,
                    "PrimaryImpact": oid,
                    "SourceTag": "MISSING",
                    "Notes": "Output value may be cached; recalc in Excel",
                }
            )

    # Rank by absolute delta (numeric), then category, then item
    def _abs_delta(x):
        d = x.get("Delta")
        if d is None:
            return -1
        try:
            return abs(float(d))
        except Exception:
            return -1

    items_sorted = sorted(
        items, key=lambda x: (_abs_delta(x), x["Category"], x["Item"]), reverse=True
    )

    out_rows = []
    for idx, it in enumerate(items_sorted, start=1):
        out_rows.append(
            {
                "Rank": idx,
                "Category": it["Category"],
                "Item": it["Item"],
                "Old": it["Old"],
                "New": it["New"],
                "Delta": it["Delta"],
                "Units": it["Units"],
                "PrimaryImpact": it["PrimaryImpact"],
                "SourceTag": it["SourceTag"],
                "Notes": it["Notes"],
            }
        )

    df_out = pd.DataFrame(
        out_rows,
        columns=[
            "Rank",
            "Category",
            "Item",
            "Old",
            "New",
            "Delta",
            "Units",
            "PrimaryImpact",
            "SourceTag",
            "Notes",
        ],
    )
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_csv_path, index=False)
    return out_csv_path


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: python scripts/model_diff.py plan.json output/audit/WhatChanged_Diff.csv [new_model_path]"
        )
        return 1

    plan = read_json(sys.argv[1])
    out_path = Path(sys.argv[2])
    new_model = Path(sys.argv[3]) if len(sys.argv) >= 4 else None
    write_diff(plan, out_path, new_model)
    print(f"Wrote diff: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
