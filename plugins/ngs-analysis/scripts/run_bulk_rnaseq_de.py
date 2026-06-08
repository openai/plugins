#!/usr/bin/env python3
"""Run bulk RNA-seq differential expression with validation and audited artifacts."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
import os
import shlex
import shutil
from pathlib import Path
from typing import Any

from ngs_run_utils import (
    build_artifact_index,
    command_path,
    run_cmd,
    slug_timestamp,
    software_versions,
    tool_preflight,
    write_json,
    write_standard_manifest,
    write_text,
)
from ngs_visualization_utils import (
    artifact_entry,
    launch_marimo_review_app,
    write_marimo_review_notebook,
    write_visualization_index,
)

SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = SCRIPT_PATH.parents[1]
WORKFLOW_ROOT = PLUGIN_ROOT / "workflows" / "bulk_rnaseq_differential_expression"
WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "bulk_rnaseq_de"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle, delimiter="\t")
        ]


def r_package_available(package: str) -> bool:
    if not command_path("Rscript"):
        return False
    result = run_cmd(
        ["Rscript", "-e", f"cat(requireNamespace('{package}', quietly=TRUE))"],
        Path.cwd(),
        timeout=60,
    )
    return result.get("ok") and "TRUE" in str(result.get("stdout_tail", ""))


def parse_count_matrix(path: Path) -> tuple[list[str], list[dict[str, str]], dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        columns = reader.fieldnames or []
        if "gene_id" not in columns:
            raise ValueError("count matrix must include a gene_id column")
        sample_cols = [column for column in columns if column not in {"gene_id", "gene_name"}]
        rows = list(reader)
    errors = []
    integer_like = True
    finite_values = True
    min_value = math.inf
    max_value = -math.inf
    for row_index, row in enumerate(rows, start=2):
        for sample in sample_cols:
            try:
                value = float(row[sample])
            except ValueError:
                errors.append(f"row {row_index} sample {sample}: non-numeric expression value")
                continue
            if not math.isfinite(value):
                finite_values = False
                errors.append(f"row {row_index} sample {sample}: non-finite expression value")
            if abs(value - round(value)) > 1e-8:
                integer_like = False
            min_value = min(min_value, value)
            max_value = max(max_value, value)
    return (
        sample_cols,
        rows,
        {
            "errors": errors,
            "integer_like": integer_like,
            "finite_values": finite_values,
            "gene_count": len(rows),
            "min_value": None if min_value == math.inf else min_value,
            "max_value": None if max_value == -math.inf else max_value,
        },
    )


def infer_input_mode(
    requested: str, matrix_status: dict[str, Any], warnings: list[str], errors: list[str]
) -> str:
    integer_like = bool(matrix_status.get("integer_like"))
    min_value = matrix_status.get("min_value")
    if requested != "auto":
        if requested == "raw_counts" and not integer_like:
            errors.append("raw_counts input mode requires an integer-like matrix")
        return requested
    if integer_like:
        return "raw_counts"
    if min_value is not None and min_value < 0:
        warnings.append(
            "Auto-detected input_mode=log_expression because the matrix contains negative values. "
            "Override with --input-mode if the matrix scale is known explicitly."
        )
        return "log_expression"
    warnings.append(
        "Auto-detected input_mode=normalized_expression for a non-integer, non-negative matrix. "
        "Override with --input-mode if the input is already log-transformed."
    )
    return "normalized_expression"


def build_fit_formula(metadata_rows: list[dict[str, str]], selected_method: str) -> str:
    batch_values = [row.get("batch", "") for row in metadata_rows if row.get("batch", "")]
    has_batch = len(set(batch_values)) > 1
    if selected_method in {"limma_log2", "edgeR"}:
        return "~ 0 + condition + batch" if has_batch else "~ 0 + condition"
    return "~ batch + condition" if has_batch else "~ condition"


def build_outputs_map(input_mode: str) -> dict[str, str]:
    outputs = {
        "contrast_status": "manifest/contrast_status.tsv",
        "qc_plots": "qc/*.png",
        "de_tables": "results/*.tsv",
        "contrast_plots": "plots/*.png",
        "design_diagnostics": "qc/design_diagnostics.tsv",
        "outlier_metrics": "qc/sample_outlier_metrics.tsv",
        "statistical_summary": "qc/statistical_summary.tsv",
        "statistical_warnings": "qc/statistical_warnings.tsv",
    }
    if input_mode == "raw_counts":
        outputs.update(
            {
                "raw_counts": "results/raw_counts.tsv",
                "normalized_expression": "results/normalized_expression_matrix.tsv",
                "log_expression": "results/log2_expression_matrix.tsv",
            }
        )
    elif input_mode == "normalized_expression":
        outputs.update(
            {
                "input_normalized_expression": "results/input_normalized_expression_matrix.tsv",
                "log_expression": "results/log2_expression_matrix.tsv",
            }
        )
    else:
        outputs.update(
            {
                "input_log_expression": "results/input_log_expression_matrix.tsv",
                "modeling_expression": "results/modeling_expression_matrix.tsv",
            }
        )
    return outputs


def validate_inputs(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    count_matrix = args.count_matrix.expanduser().resolve()
    sample_metadata = args.sample_metadata.expanduser().resolve()
    contrasts = args.contrasts.expanduser().resolve()
    errors = []
    warnings = []
    for label, path in [
        ("count_matrix", count_matrix),
        ("sample_metadata", sample_metadata),
        ("contrasts", contrasts),
    ]:
        if not path.exists():
            errors.append(f"{label} does not exist: {path}")
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}, {}

    sample_cols, _, matrix_status = parse_count_matrix(count_matrix)
    errors.extend(matrix_status["errors"])
    metadata_rows = read_tsv(sample_metadata)
    contrast_rows = read_tsv(contrasts)

    metadata_samples = [row.get("sample_id", "") for row in metadata_rows]
    if len(metadata_samples) != len(set(metadata_samples)):
        errors.append("sample metadata contains duplicate sample_id values")
    if set(sample_cols) != set(metadata_samples):
        errors.append("count matrix sample columns and metadata sample_id values do not match")
    if "condition" not in (metadata_rows[0].keys() if metadata_rows else []):
        errors.append("sample metadata must include a condition column")

    condition_counts: dict[str, int] = {}
    for row in metadata_rows:
        condition = row.get("condition", "")
        if not condition:
            errors.append(f"sample {row.get('sample_id', '<missing>')} has no condition")
        condition_counts[condition] = condition_counts.get(condition, 0) + 1

    contrast_status = []
    required_contrast_cols = {"contrast", "numerator_condition", "denominator_condition"}
    if contrast_rows and not required_contrast_cols.issubset(contrast_rows[0].keys()):
        errors.append(
            "contrasts file must include contrast, numerator_condition, and denominator_condition columns"
        )
    for row in contrast_rows:
        numerator = row.get("numerator_condition", "")
        denominator = row.get("denominator_condition", "")
        numerator_n = condition_counts.get(numerator, 0)
        denominator_n = condition_counts.get(denominator, 0)
        status = "valid" if numerator_n >= 2 and denominator_n >= 2 else "insufficient_replicates"
        if status == "valid" and numerator_n == 2 and denominator_n == 2:
            warnings.append(
                f"Contrast {row.get('contrast', '')} is minimally powered (2 vs 2 replicates); treat p-values and effect sizes as exploratory and review QC plots carefully."
            )
        contrast_status.append(
            {
                "contrast": row.get("contrast", ""),
                "numerator_condition": numerator,
                "denominator_condition": denominator,
                "numerator_replicates": numerator_n,
                "denominator_replicates": denominator_n,
                "status": status,
                "expected_status": row.get("expected_status", ""),
                "notes": row.get("notes", ""),
            }
        )
    if not contrast_status:
        errors.append("no contrasts were provided")

    package_status = {
        package: r_package_available(package) for package in ["DESeq2", "edgeR", "limma"]
    }
    input_mode = infer_input_mode(args.input_mode, matrix_status, warnings, errors)
    selected_method = select_method(args.method, input_mode, package_status, errors)
    if selected_method == "limma_log2" and not package_status["limma"]:
        errors.append("limma is required for limma_log2 execution but is not installed")
    fit_formula = build_fit_formula(metadata_rows, selected_method)

    method_decision = {
        "requested_method": args.method,
        "selected_method": selected_method,
        "requested_input_mode": args.input_mode,
        "input_mode": input_mode,
        "matrix_integer_like": matrix_status["integer_like"],
        "r_packages": package_status,
        "condition_counts": condition_counts,
        "contrast_status": contrast_status,
        "fit_formula": fit_formula,
    }
    validation = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "count_matrix": str(count_matrix),
        "sample_metadata": str(sample_metadata),
        "contrasts": str(contrasts),
        "sample_count": len(sample_cols),
        "gene_count": matrix_status["gene_count"],
        "matrix_integer_like": matrix_status["integer_like"],
        "contrast_status": contrast_status,
        "method_decision": method_decision,
    }
    return validation, method_decision


def select_method(
    requested: str, input_mode: str, packages: dict[str, bool], errors: list[str]
) -> str:
    if requested != "auto":
        if requested in {"DESeq2", "edgeR"} and input_mode != "raw_counts":
            errors.append(
                f"{requested} requires raw integer-like counts; input_mode={input_mode} is not compatible"
            )
        if requested != "limma_log2" and not packages.get(requested, False):
            errors.append(f"{requested} was requested but the R package is not installed")
        return requested
    if input_mode == "raw_counts" and packages.get("DESeq2", False):
        return "DESeq2"
    if input_mode == "raw_counts" and packages.get("edgeR", False):
        return "edgeR"
    return "limma_log2"


def write_workflow(run_dir: Path) -> None:
    scripts_dir = run_dir / "workflow" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(WORKFLOW_ROOT / "run_bulk_de.R", scripts_dir / "run_bulk_de.R")


def r_command(args: argparse.Namespace, run_dir: Path, method: dict[str, Any]) -> list[str]:
    return [
        "Rscript",
        "workflow/scripts/run_bulk_de.R",
        str(args.count_matrix.expanduser().resolve()),
        str(args.sample_metadata.expanduser().resolve()),
        str(args.contrasts.expanduser().resolve()),
        str(method.get("selected_method", "limma_log2")),
        str(method.get("input_mode", "normalized_expression")),
        str(method.get("fit_formula", "~ 0 + condition")),
        str(run_dir),
    ]


def write_commands(run_dir: Path, cmd: list[str]) -> None:
    write_text(
        run_dir / "commands.sh", "#!/usr/bin/env bash\nset -euo pipefail\n" + shlex.join(cmd) + "\n"
    )


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    method: dict[str, Any],
    review_app_info: dict[str, Any] | None = None,
) -> None:
    outputs = build_outputs_map(str(method.get("input_mode", "normalized_expression")))
    lines = [
        "# Bulk RNA-seq Differential Expression Run Summary",
        "",
        f"Status: `{status}`",
        f"Selected method: `{method.get('selected_method')}`",
        f"Input mode: `{method.get('input_mode')}`",
        f"Matrix integer-like: `{method.get('matrix_integer_like')}`",
        f"Fit formula: `{method.get('fit_formula')}`",
        f"Review app URL: `{review_app_info.get('url') if review_app_info and review_app_info.get('ok') else 'not started'}`",
        "",
        "## Contrast Status",
        "",
    ]
    for contrast in validation.get("contrast_status", []):
        lines.append(
            f"- `{contrast['contrast']}`: {contrast['status']} "
            f"({contrast['numerator_condition']} n={contrast['numerator_replicates']} vs "
            f"{contrast['denominator_condition']} n={contrast['denominator_replicates']})"
        )
    lines.extend(
        [
            "",
            "## Key Artifacts",
            "",
            "- `manifest/contrast_status.tsv`",
        ]
    )
    for artifact in [
        outputs.get("raw_counts"),
        outputs.get("input_normalized_expression"),
        outputs.get("normalized_expression"),
        outputs.get("input_log_expression"),
        outputs.get("modeling_expression"),
        outputs.get("log_expression"),
    ]:
        if artifact:
            lines.append(f"- `{artifact}`")
    lines.extend(
        [
            "- `qc/pca.png`",
            "- `qc/sample_distance_heatmap.png`",
            "- `qc/design_diagnostics.tsv`",
            "- `qc/sample_outlier_metrics.tsv`",
            "- `qc/statistical_warnings.tsv`",
            "- `plots/*_volcano.png` and `plots/*_ma.png` for executed limma contrasts",
            "- `notebooks/marimo_server.json`",
            "- `visualizations/index.html`",
            "- `artifact_index.json`",
            "",
        ]
    )
    if validation.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in validation["warnings"])
        lines.append("")
    if validation.get("errors"):
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {error}" for error in validation["errors"])
        lines.append("")
    write_text(run_dir / "summary.md", "\n".join(lines))


def generate_visualizations(
    run_dir: Path,
    validation: dict[str, Any],
    review_app_info: dict[str, Any] | None = None,
) -> dict[str, str]:
    entries: list[dict[str, Any]] = []
    notes = [
        "artifact_index.json includes per-file SHA256 and modification timestamps for provenance.",
        "Use qc/statistical_warnings.tsv and manifest/contrast_status.tsv together when deciding whether a contrast is interpretable.",
    ]
    if validation.get("warnings"):
        notes.extend(str(warning) for warning in validation["warnings"])

    for artifact_id, title, rel_path, kind, description in [
        (
            "pca_plot",
            "PCA Plot",
            "qc/pca.png",
            "plot",
            "PCA on the modeling matrix with variance explained and condition colors.",
        ),
        (
            "sample_distance_heatmap",
            "Sample Distance Heatmap",
            "qc/sample_distance_heatmap.png",
            "plot",
            "Clustered sample-to-sample Euclidean distances.",
        ),
        (
            "mean_variance_trend",
            "Mean-Variance Trend",
            "qc/mean_variance_trend.png",
            "plot",
            "Method-specific mean-variance diagnostic.",
        ),
        (
            "library_sizes",
            "Library Sizes",
            "qc/library_sizes.png",
            "plot",
            "Per-sample total expression values from the supplied matrix.",
        ),
        (
            "contrast_status",
            "Contrast Status",
            "manifest/contrast_status.tsv",
            "table",
            "Executed and blocked contrasts with replicate counts.",
        ),
        (
            "design_diagnostics",
            "Design Diagnostics",
            "qc/design_diagnostics.tsv",
            "table",
            "Design rank and model structure checks.",
        ),
        (
            "statistical_warnings",
            "Statistical Warnings",
            "qc/statistical_warnings.tsv",
            "table",
            "Human-readable statistical UX warnings emitted by the runner.",
        ),
        (
            "sample_outliers",
            "Sample Outlier Metrics",
            "qc/sample_outlier_metrics.tsv",
            "table",
            "Mean distance and z-score outlier screen.",
        ),
    ]:
        path = run_dir / rel_path
        entries.append(
            artifact_entry(
                artifact_id=artifact_id,
                title=title,
                path=rel_path if path.exists() else None,
                kind=kind,
                status="created" if path.exists() else "not_available",
                description=description,
            )
        )
    for result_path in sorted((run_dir / "results").glob("*.tsv")):
        rel_path = str(result_path.relative_to(run_dir))
        entries.append(
            artifact_entry(
                artifact_id=f"table_{result_path.stem}",
                title=f"Result Table: {result_path.stem}",
                path=rel_path,
                kind="table",
                status="created",
                description="Differential expression table or blocked-contrast stub emitted by the selected method.",
            )
        )
    for plot_path in sorted((run_dir / "plots").glob("*.png")):
        rel_path = str(plot_path.relative_to(run_dir))
        entries.append(
            artifact_entry(
                artifact_id=f"plot_{plot_path.stem}",
                title=f"Contrast Plot: {plot_path.stem}",
                path=rel_path,
                kind="plot",
                status="created",
                description="Per-contrast volcano or MA plot for an executed comparison.",
            )
        )
    notebook_path = write_marimo_review_notebook(
        run_dir / "notebooks" / "bulk_rnaseq_de_review.marimo.py",
        title="Bulk RNA-seq Differential Expression Review",
        run_dir=run_dir,
        image_items=[
            ("PCA", "qc/pca.png"),
            ("Sample Distance Heatmap", "qc/sample_distance_heatmap.png"),
            ("Mean-Variance Trend", "qc/mean_variance_trend.png"),
            ("Library Sizes", "qc/library_sizes.png"),
        ]
        + [
            (f"Contrast Plot: {path.stem}", str(path.relative_to(run_dir)))
            for path in sorted((run_dir / "plots").glob("*.png"))
        ],
        table_items=[
            ("Contrast Status", "manifest/contrast_status.tsv"),
            ("Design Diagnostics", "qc/design_diagnostics.tsv"),
            ("Statistical Warnings", "qc/statistical_warnings.tsv"),
            ("Sample Outlier Metrics", "qc/sample_outlier_metrics.tsv"),
        ]
        + [
            (f"Result Table: {path.stem}", str(path.relative_to(run_dir)))
            for path in sorted((run_dir / "results").glob("*.tsv"))
        ],
    )
    entries.append(
        artifact_entry(
            artifact_id="de_review_notebook",
            title="DE Review Notebook",
            path=notebook_path.relative_to(run_dir),
            kind="notebook",
            status="created",
            description="Marimo review notebook over the key DE plots, diagnostics, and result tables.",
        )
    )
    if review_app_info:
        entries.append(
            artifact_entry(
                artifact_id="de_review_launch",
                title="DE Review App",
                path=review_app_info.get("url"),
                kind="localhost_app",
                status="created" if review_app_info.get("ok") else "blocked",
                description="Auto-launched localhost Marimo review app for the generated DE notebook.",
                source="notebooks/marimo_server.json",
            )
        )
        if review_app_info.get("ok"):
            notes.append(f"Review app auto-launched at {review_app_info['url']}.")
        else:
            notes.append(
                "Review app auto-launch did not become ready. See notebooks/marimo_server.json and logs/marimo_server.log."
            )
    index = write_visualization_index(
        run_dir,
        title="Bulk RNA-seq Differential Expression Review Bundle",
        description="Human-readable review surface for the DE lane, with an auto-launched Marimo review app and explicit statistical context.",
        entries=entries,
        notes=notes,
    )
    return {
        "visualization_index": str(index.relative_to(run_dir)),
        "visualization_manifest": "visualizations/visualization_manifest.json",
        "review_notebook": str(notebook_path.relative_to(run_dir)),
    }


def maybe_launch_review_app(
    args: argparse.Namespace, run_dir: Path, notebook_path: Path
) -> dict[str, Any]:
    info_path = run_dir / "notebooks" / "marimo_server.json"
    if not args.launch_review_app:
        info = {"ok": False, "error": "Review app auto-launch disabled by CLI flag."}
        write_json(info_path, info)
        return info
    if not importlib.util.find_spec("marimo"):
        info = {"ok": False, "error": "marimo is not installed in the current Python environment."}
        write_json(info_path, info)
        return info
    try:
        info = launch_marimo_review_app(
            notebook_path=notebook_path,
            run_dir=run_dir,
            start_port=args.review_app_port,
            python_executable=os.environ.get("PYTHON_EXECUTABLE_OVERRIDE"),
        )
    except Exception as exc:  # noqa: BLE001
        info = {"ok": False, "error": str(exc)}
    write_json(info_path, info)
    return info


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count-matrix", type=Path, required=True)
    parser.add_argument("--sample-metadata", type=Path, required=True)
    parser.add_argument("--contrasts", type=Path, required=True)
    parser.add_argument(
        "--input-mode",
        choices=["auto", "raw_counts", "normalized_expression", "log_expression"],
        default="auto",
        help="Explicit matrix scale. Auto infers from integer-likeness and sign.",
    )
    parser.add_argument(
        "--method", choices=["auto", "DESeq2", "edgeR", "limma_log2"], default="auto"
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        help="Run directory. Defaults to ngs_runs/bulk_rnaseq_de/<timestamp>.",
    )
    parser.add_argument("--run-id", default=slug_timestamp("bulk-rnaseq-de"))
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--launch-review-app",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-launch the generated Marimo review app on localhost and record its URL in the run envelope.",
    )
    parser.add_argument(
        "--review-app-port",
        type=int,
        default=2718,
        help="Starting port to use when auto-launching the Marimo review app.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    validation, method_decision = validate_inputs(args)
    tool_status = tool_preflight(["Rscript"], optional=[])
    write_json(
        run_dir / "config.json",
        {
            "method": method_decision,
            "inputs": {
                "count_matrix": str(args.count_matrix.expanduser().resolve()),
                "sample_metadata": str(args.sample_metadata.expanduser().resolve()),
                "contrasts": str(args.contrasts.expanduser().resolve()),
            },
        },
    )
    write_json(run_dir / "validation" / "input_summary.json", {"inputs": validation})
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions({"Rscript": ["Rscript", "--version"]}),
    )
    write_workflow(run_dir)

    cmd = r_command(args, run_dir, method_decision)
    write_commands(run_dir, cmd)
    dry_run = {
        "ok": validation.get("ok") and tool_status.get("ok"),
        "detail": "input/method validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    write_text(run_dir / "logs" / "validation_dry_run.log", dry_run["detail"] + "\n")
    execution: dict[str, Any] | None = None
    status = "blocked" if not dry_run["ok"] else "validated"
    if args.execute and dry_run["ok"]:
        execution = run_cmd(cmd, run_dir, timeout=86400)
        write_json(run_dir / "logs" / "rscript_execute.json", execution)
        write_text(run_dir / "logs" / "rscript_execute.log", execution.get("stdout_tail", ""))
        status = "completed" if execution.get("ok") else "failed"

    outputs = build_outputs_map(str(method_decision.get("input_mode", "normalized_expression")))
    review_bundle = generate_visualizations(run_dir, validation)
    review_notebook_path = run_dir / review_bundle["review_notebook"]
    review_app_info = (
        maybe_launch_review_app(args, run_dir, review_notebook_path)
        if args.execute and status == "completed" and review_notebook_path.exists()
        else None
    )
    review_bundle = generate_visualizations(run_dir, validation, review_app_info=review_app_info)
    outputs["review_app_record"] = "notebooks/marimo_server.json"
    outputs.update(review_bundle)
    write_summary(run_dir, status, validation, method_decision, review_app_info=review_app_info)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="bulk_rnaseq_differential_expression",
        workflow="r_bioconductor_bulk_de",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "count_matrix": str(args.count_matrix.expanduser().resolve()),
            "sample_metadata": str(args.sample_metadata.expanduser().resolve()),
            "contrasts": str(args.contrasts.expanduser().resolve()),
        },
        outputs=outputs,
        method=method_decision,
        review_bundle={**review_bundle, "review_app": review_app_info},
    )
    write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))

    print(run_dir)
    if status in {"blocked", "failed"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
