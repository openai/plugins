#!/usr/bin/env python3
"""Transparent CLI helper for portfolio-risk-management sizing JSON inputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from position_sizing_core import (  # noqa: E402
    exposure_rows,
    liquidity_rows,
    monitoring_rows,
    scenario_rows,
    sizing_rows,
)
from position_sizing_outputs import (  # noqa: E402
    output_paths,
    source_basis,
    summarize_console,
    write_output_bundle,
)

from shared.artifacts import build_run_log, output_manifest, write_run_log_bundle  # noqa: E402

FILENAMES = {
    "position_summary": "position_summary.csv",
    "sizing_cases": "sizing_cases.csv",
    "scenario_pnl": "scenario_pnl.csv",
    "exposure_impact": "exposure_impact.csv",
    "liquidity_exit": "liquidity_exit.csv",
    "monitoring_rules": "monitoring_rules.csv",
    "support_note": "support_note.md",
    "run_log": "run_log.json",
    "manifest": "manifest.json",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize portfolio-risk-management sizing support outputs from JSON input."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default="risk_position_sizing_outputs")
    return parser.parse_args(argv)


def build_failure_run_log(
    out: Path, args: argparse.Namespace, paths: dict[str, str], message: str
) -> dict[str, Any]:
    return build_run_log(
        hard_failures=[message],
        warnings=[],
        outputs=paths,
        output_manifest_rows=output_manifest(
            paths,
            written={"run_log", "manifest"},
            artifact_roles={
                "support_note": "narrative_support",
                "run_log": "machine_support",
                "manifest": "machine_support",
            },
            hidden_unless_requested=set(paths),
        ),
        checks={"validation_errors": [message]},
        model_status="not-decision-ready",
        workbook_mode="csv_support_note_export",
        extra={
            "input_path": str(args.input),
            "primary_human_deliverable": None,
            "support_artifacts": [paths[key] for key in paths if key in {"run_log", "manifest"}],
        },
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    paths = output_paths(out)

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        sizing, summary = sizing_rows(data)
        scenarios = scenario_rows(data, summary)
        exposures = exposure_rows(data, summary)
        liquidity = liquidity_rows(data, summary)
        monitoring = monitoring_rows(data)
    except Exception as exc:
        write_run_log_bundle(out, build_failure_run_log(out, args, paths, str(exc)))
        print(f"ERROR: {exc}")
        return 1

    try:
        write_output_bundle(out, summary, sizing, scenarios, exposures, liquidity, monitoring)
    except Exception as exc:
        message = f"could not write output: {exc}"
        write_run_log_bundle(out, build_failure_run_log(out, args, paths, message))
        print(f"ERROR: {message}")
        return 1

    written = set(FILENAMES)
    run_log = build_run_log(
        hard_failures=[],
        warnings=[
            "Validate live prices, volatility, beta, liquidity, borrow, Greeks, limits, and correlations before trading."
        ],
        outputs=paths,
        output_manifest_rows=output_manifest(
            paths,
            written=written,
            artifact_roles={
                "support_note": "narrative_support",
                "run_log": "machine_support",
                "manifest": "machine_support",
            },
            hidden_unless_requested=set(paths),
        ),
        source_basis=source_basis(data),
        workbook_mode="csv_support_note_export",
        extra={
            "input_path": str(args.input),
            "primary_human_deliverable": None,
            "support_artifacts": [paths[key] for key in paths if key in written],
        },
    )
    write_run_log_bundle(out, run_log)

    print(f"Wrote outputs to {out}")
    for line in summarize_console(summary):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
