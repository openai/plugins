#!/usr/bin/env python3
"""Run matrix-level scRNA post-count QC with raw-count preservation and auditable artifacts."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = SCRIPT_PATH.parents[1]
WORKSPACE_ROOT = Path.cwd()


def configure_runtime_environment() -> dict[str, str]:
    runtime_root = (
        Path(os.environ.get("NGS_ANALYSIS_RUNTIME_ROOT", tempfile.gettempdir()))
        / "ngs-analysis-runtime"
        / "scrnaseq-post-count"
    )
    dirs = {
        "runtime_root": runtime_root,
        "mplconfig": runtime_root / "matplotlib",
        "xdg_cache": runtime_root / "xdg_cache",
        "xdg_state": runtime_root / "xdg_state",
        "numba_cache": runtime_root / "numba",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(dirs["mplconfig"]))
    os.environ.setdefault("XDG_CACHE_HOME", str(dirs["xdg_cache"]))
    os.environ.setdefault("XDG_STATE_HOME", str(dirs["xdg_state"]))
    os.environ.setdefault("NUMBA_CACHE_DIR", str(dirs["numba_cache"]))
    os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 1))
    return {key: str(value) for key, value in dirs.items()}


RUNTIME_ENV = configure_runtime_environment()


def patch_numba_cache_decorators() -> None:
    try:
        import numba  # type: ignore
    except ImportError:
        return

    def wrap_strip_cache(fn: Any) -> Any:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            kwargs.pop("cache", None)
            return fn(*args, **kwargs)

        return wrapped

    for name in ("jit", "njit", "vectorize", "guvectorize", "cfunc"):
        if hasattr(numba, name):
            setattr(numba, name, wrap_strip_cache(getattr(numba, name)))


patch_numba_cache_decorators()

from ngs_run_utils import build_artifact_index, write_standard_manifest  # noqa: E402
from ngs_visualization_utils import (  # noqa: E402
    artifact_entry,
    copy_visual_asset,
    launch_marimo_review_app,
    write_marimo_review_notebook,
    write_visualization_index,
)

PYTHON_ANALYSIS_MODULES = {
    "anndata": "anndata",
    "matplotlib": "matplotlib",
    "numpy": "numpy",
    "pandas": "pandas",
    "scanpy": "scanpy",
}
REQUIRED_R_PACKAGES = ("DropletUtils", "scDblFinder", "SoupX")

ad: Any = None
matplotlib: Any = None
plt: Any = None
np: Any = None
pd: Any = None
sc: Any = None


def python_dependency_status() -> dict[str, Any]:
    modules = {}
    missing = []
    for module_name, package_name in PYTHON_ANALYSIS_MODULES.items():
        try:
            present = importlib.util.find_spec(module_name) is not None
        except (ImportError, AttributeError, ValueError):
            present = False
        modules[module_name] = {"present": present, "package": package_name}
        if not present:
            missing.append(module_name)
    return {
        "ok": not missing,
        "python_modules": modules,
        "missing": missing,
        "errors": ["Missing Python analysis packages: " + ", ".join(missing)] if missing else [],
    }


def installed_package_version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def load_analysis_modules() -> dict[str, Any]:
    status = python_dependency_status()
    if not status["ok"]:
        return status

    global ad, matplotlib, np, pd, plt, sc

    import anndata as ad_module  # type: ignore[import-not-found]
    import matplotlib as matplotlib_module  # type: ignore[import-not-found]
    import numpy as np_module
    import pandas as pd_module
    import scanpy as sc_module  # type: ignore[import-not-found]

    matplotlib_module.use("Agg")
    import matplotlib.pyplot as plt_module  # type: ignore[import-not-found]

    ad = ad_module
    matplotlib = matplotlib_module
    np = np_module
    pd = pd_module
    plt = plt_module
    sc = sc_module
    for module_name, loaded_module in {
        "anndata": ad,
        "matplotlib": matplotlib,
        "numpy": np,
        "pandas": pd,
        "scanpy": sc,
    }.items():
        package_name = PYTHON_ANALYSIS_MODULES[module_name]
        status["python_modules"][module_name]["version"] = installed_package_version(
            package_name
        ) or getattr(loaded_module, "__version__", None)
    return status


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slug_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S-scrnaseq-post-count-qc")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def command_path(name: str) -> str | None:
    return shutil.which(name)


def run_cmd(cmd: list[str], cwd: Path, timeout: int | None) -> dict[str, Any]:
    started = now_iso()
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        output = result.stdout or ""
        return {
            "cmd": cmd,
            "cwd": str(cwd),
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": result.returncode,
            "ok": result.returncode == 0,
            "stdout_tail": output[-12000:],
        }
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout if isinstance(exc.stdout, str) else ""
        return {
            "cmd": cmd,
            "cwd": str(cwd),
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": None,
            "ok": False,
            "error": f"TimeoutExpired: exceeded {timeout}s",
            "stdout_tail": output[-12000:],
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing matrix/, manifest.tsv, dataset_metadata.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Where to write QC artifacts. Defaults to <input-dir>/output/<timestamp>/",
    )
    parser.add_argument(
        "--matrix-dir",
        type=Path,
        help="Optional explicit matrix directory with matrix.mtx, barcodes.tsv, genes.tsv.",
    )
    parser.add_argument(
        "--raw-matrix-dir",
        type=Path,
        help="Optional raw droplet matrix directory for emptyDrops-style cell calling.",
    )
    parser.add_argument(
        "--dataset-metadata", type=Path, help="Optional explicit metadata JSON path."
    )
    parser.add_argument(
        "--resolution",
        type=float,
        default=0.5,
        help="Leiden resolution for plot subset clustering.",
    )
    parser.add_argument(
        "--timeout-seconds", type=int, default=1800, help="Timeout for the R doublet step."
    )
    parser.add_argument(
        "--rscript", type=Path, help="Optional explicit Rscript path for the scDblFinder step."
    )
    parser.add_argument(
        "--launch-review-app",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-launch the generated Marimo review app on localhost and record its URL in the run envelope.",
    )
    parser.add_argument(
        "--review-app-port",
        type=int,
        default=2719,
        help="Starting port to use when auto-launching the Marimo review app.",
    )
    return parser.parse_args()


def matrix_paths(args: argparse.Namespace) -> tuple[Path, Path, Path | None, Path, Path]:
    input_dir = args.input_dir.expanduser().resolve()
    matrix_dir = (args.matrix_dir or input_dir / "matrix").expanduser().resolve()
    raw_matrix_dir = args.raw_matrix_dir.expanduser().resolve() if args.raw_matrix_dir else None
    metadata = (args.dataset_metadata or input_dir / "dataset_metadata.json").expanduser().resolve()
    return input_dir, matrix_dir, raw_matrix_dir, metadata, input_dir / "manifest.tsv"


def validate_inputs(
    matrix_dir: Path, raw_matrix_dir: Path | None, metadata: Path, manifest: Path
) -> dict[str, Any]:
    files = {
        "matrix": matrix_dir / "matrix.mtx",
        "barcodes": matrix_dir / "barcodes.tsv",
        "genes": matrix_dir / "genes.tsv",
        "metadata": metadata,
        "manifest": manifest,
    }
    if raw_matrix_dir:
        files["raw_matrix"] = raw_matrix_dir / "matrix.mtx"
        files["raw_barcodes"] = raw_matrix_dir / "barcodes.tsv"
        files["raw_genes"] = raw_matrix_dir / "genes.tsv"
    summary: dict[str, Any] = {"files": {}, "errors": []}
    for name, path in files.items():
        exists = path.exists()
        summary["files"][name] = {
            "path": str(path),
            "exists": exists,
            "size": path.stat().st_size if exists else None,
        }
        if not exists and name != "manifest":
            summary["errors"].append(f"required file missing: {path}")
    if summary["errors"]:
        return summary
    with (matrix_dir / "matrix.mtx").open("rt", encoding="utf-8", errors="replace") as handle:
        first = handle.readline().strip()
    if not first.startswith("%%MatrixMarket"):
        summary["errors"].append("matrix.mtx does not start with MatrixMarket header")
    return summary


def r_dependency_status(rscript: Path | None) -> dict[str, Any]:
    rscript_cmd = str(rscript) if rscript else command_path("Rscript")
    status: dict[str, Any] = {
        "rscript": rscript_cmd,
        "packages": {},
        "required_packages": list(REQUIRED_R_PACKAGES),
        "missing": [],
        "ok": False,
    }
    if not rscript_cmd:
        status["missing"] = ["Rscript", *REQUIRED_R_PACKAGES]
        return status
    probe = run_cmd(
        [
            rscript_cmd,
            "-e",
            'pkgs<-c("DropletUtils","scDblFinder","SoupX");'
            "st<-sapply(pkgs, requireNamespace, quietly=TRUE);"
            'cat(paste(names(st), st, sep="=", collapse=";"))',
        ],
        WORKSPACE_ROOT,
        timeout=60,
    )
    status["probe"] = probe
    if probe.get("ok"):
        parsed = {}
        for item in str(probe.get("stdout_tail", "")).strip().split(";"):
            if "=" in item:
                key, value = item.split("=", 1)
                parsed[key] = value == "TRUE"
        status["packages"] = parsed
        status["missing"] = [pkg for pkg in REQUIRED_R_PACKAGES if not parsed.get(pkg, False)]
        status["ok"] = not status["missing"]
    else:
        status["missing"] = list(REQUIRED_R_PACKAGES)
    return status


def combined_tool_preflight_status(
    python_dep_status: dict[str, Any], r_dep_status: dict[str, Any]
) -> dict[str, Any]:
    return {
        "ok": bool(python_dep_status.get("ok") and r_dep_status.get("ok")),
        "python_dependencies": python_dep_status,
        "r_dependencies": r_dep_status,
    }


def matrix_nonzero_entries(matrix: Any) -> int:
    if hasattr(matrix, "nnz"):
        return int(matrix.nnz)
    return int(np.count_nonzero(np.asarray(matrix)))


def scdbfinder_readiness(adata: ad.AnnData) -> dict[str, Any]:
    informative_mask = np.asarray(adata.obs["total_counts"] > 0, dtype=bool)
    informative_cells = int(np.count_nonzero(informative_mask))
    nonzero_entries = matrix_nonzero_entries(adata.layers.get("counts", adata.X))
    if informative_cells < 2:
        return {
            "ok": False,
            "reason": "too_few_informative_cells",
            "detail": (
                "scDblFinder requires at least 2 informative cells with non-zero counts. "
                f"Observed {informative_cells} informative cells across {adata.n_obs} barcodes "
                f"and {nonzero_entries} non-zero matrix entries."
            ),
            "informative_cells": informative_cells,
            "barcodes": int(adata.n_obs),
            "nonzero_entries": nonzero_entries,
        }
    return {
        "ok": True,
        "informative_cells": informative_cells,
        "barcodes": int(adata.n_obs),
        "nonzero_entries": nonzero_entries,
    }


def scdbfinder_blocker_reason(dbl_result: dict[str, Any]) -> str:
    reason = dbl_result.get("reason")
    if reason == "too_few_informative_cells":
        return "scDblFinder was skipped because the matrix has too few informative cells for doublet modeling."
    if reason == "missing_r_dependencies":
        return "scDblFinder was skipped because required R/Bioconductor packages were unavailable."
    if reason == "rscript_missing":
        return "scDblFinder was skipped because Rscript was not available."
    return "scDblFinder could not run; final cell set is not doublet-complete."


def robust_lower(values: np.ndarray, use_log: bool = True, z: float = 3.0) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if arr.size == 0:
        return 0.0
    work = np.log10(arr + 1.0) if use_log else arr
    median = float(np.median(work))
    mad = float(np.median(np.abs(work - median)))
    if mad == 0:
        return float(np.min(arr))
    bound = median - z * mad
    return float(max(0.0, 10**bound - 1.0)) if use_log else float(max(0.0, bound))


def robust_upper(values: np.ndarray, use_log: bool = True, z: float = 3.0) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if arr.size == 0:
        return float("nan")
    work = np.log10(arr + 1.0) if use_log else arr
    median = float(np.median(work))
    mad = float(np.median(np.abs(work - median)))
    if mad == 0:
        return float(np.max(arr))
    bound = median + z * mad
    return float(10**bound - 1.0) if use_log else float(bound)


def threshold_dict(adata: ad.AnnData) -> dict[str, Any]:
    lower_genes = robust_lower(adata.obs["n_genes_by_counts"].to_numpy(), use_log=True, z=3.0)
    lower_counts = robust_lower(adata.obs["total_counts"].to_numpy(), use_log=True, z=3.0)
    upper_mito = robust_upper(adata.obs["pct_counts_mt"].to_numpy(), use_log=False, z=3.0)
    upper_genes = robust_upper(adata.obs["n_genes_by_counts"].to_numpy(), use_log=True, z=3.0)
    upper_counts = robust_upper(adata.obs["total_counts"].to_numpy(), use_log=True, z=3.0)
    return {
        "n_genes_by_counts": {
            "lower": lower_genes,
            "upper_review": upper_genes,
            "method": "log10 median +/- 3 MAD",
        },
        "total_counts": {
            "lower": lower_counts,
            "upper_review": upper_counts,
            "method": "log10 median +/- 3 MAD",
        },
        "pct_counts_mt": {
            "upper": None if not np.isfinite(upper_mito) else upper_mito,
            "method": "median + 3 MAD; disabled when no mitochondrial signal is present",
        },
    }


def plot_thresholds(adata: ad.AnnData, thresholds: dict[str, Any], out_path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    items = [
        (
            "total_counts",
            "Total counts",
            thresholds["total_counts"]["lower"],
            thresholds["total_counts"]["upper_review"],
        ),
        (
            "n_genes_by_counts",
            "Detected genes",
            thresholds["n_genes_by_counts"]["lower"],
            thresholds["n_genes_by_counts"]["upper_review"],
        ),
        ("pct_counts_mt", "Mito %", None, thresholds["pct_counts_mt"]["upper"]),
    ]
    for ax, (column, title, lower, upper) in zip(axes, items, strict=True):
        values = adata.obs[column].to_numpy()
        ax.hist(values, bins=60, color="#4f7d4a", alpha=0.85)
        if lower is not None:
            ax.axvline(lower, color="#b22222", linestyle="--", linewidth=1.5)
        if upper is not None:
            ax.axvline(upper, color="#204a87", linestyle=":", linewidth=1.5)
        ax.set_title(title)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=fieldnames).to_csv(path, sep="\t", index=False)


def plot_count_summary(rows: list[dict[str, Any]], out_path: Path, *, title: str) -> None:
    labels = [str(row["metric"]) for row in rows]
    values = [float(row["cells"]) for row in rows]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.bar(labels, values, color="#3b6ea8")
    ax.set_title(title)
    ax.set_ylabel("Cells")
    ax.tick_params(axis="x", rotation=35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_simple_embedding(
    coords: np.ndarray, labels: pd.Series, out_path: Path, *, title: str
) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ax.scatter(coords[:, 0], coords[:, 1], s=65, c="#3b6ea8", alpha=0.9)
    for idx, label in enumerate(labels.astype(str).tolist()):
        ax.text(coords[idx, 0] + 0.03, coords[idx, 1] + 0.03, label, fontsize=8)
    ax.set_title(title)
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def write_scrna_visual_bundle(
    output_root: Path, review_app_info: dict[str, Any] | None
) -> dict[str, str]:
    entries: list[dict[str, Any]] = []
    notes = [
        "The Marimo notebook is a review surface over generated artifacts; the PNG/CSV/H5AD files remain the portable source of truth.",
        "Marker labels are conservative PBMC fallback labels unless a matched reference was provided upstream.",
    ]
    visualizations = output_root / "visualizations"
    visualizations.mkdir(parents=True, exist_ok=True)
    (output_root / "tables").mkdir(parents=True, exist_ok=True)
    (output_root / "notebooks").mkdir(parents=True, exist_ok=True)

    copy_specs = [
        (
            "threshold_justification",
            "QC Threshold Justification",
            "qc/threshold_justification.png",
            "visualizations/threshold_justification.png",
            "Threshold histograms with selected review/filter cutoffs.",
        ),
        (
            "umap_global",
            "UMAP by Coarse Label",
            "plots/umap_global.png",
            "visualizations/umap_by_coarse_label.png",
            "Global UMAP colored by conservative coarse labels.",
        ),
        (
            "umap_by_cluster",
            "UMAP by Leiden Cluster",
            "plots/umap_by_coarse_label.png",
            "visualizations/umap_by_cluster.png",
            "Global UMAP colored by Leiden cluster.",
        ),
        (
            "qc_pass_fail_counts",
            "QC Pass/Fail Counts",
            "qc/qc_pass_fail_counts.png",
            "visualizations/qc_pass_fail_counts.png",
            "Cell counts for major QC inclusion states.",
        ),
    ]
    for artifact_id, title, source_rel, dest_rel, description in copy_specs:
        dest = copy_visual_asset(output_root / source_rel, output_root / dest_rel)
        entries.append(
            artifact_entry(
                artifact_id=artifact_id,
                title=title,
                path=dest.relative_to(output_root) if dest else None,
                kind="plot",
                status="created" if dest else "not_available",
                description=description,
            )
        )

    table_specs = [
        (
            "cell_qc_summary",
            "Cell QC Summary",
            "tables/cell_qc_summary.tsv",
            "Aggregate cell counts for major QC states.",
        ),
        (
            "cell_qc_metrics",
            "Cell QC Metrics",
            "qc/cell_qc_metrics.csv",
            "Per-cell QC metrics and filter flags.",
        ),
        (
            "cell_labels",
            "Cell Labels",
            "annotation/cell_labels.csv",
            "Per-cell labels, marker scores, and annotation confidence.",
        ),
        (
            "umap_coords",
            "UMAP Coordinates",
            "embeddings/umap_coords.csv",
            "UMAP coordinates for downstream plotting.",
        ),
    ]
    for artifact_id, title, rel_path, description in table_specs:
        exists = (output_root / rel_path).exists()
        entries.append(
            artifact_entry(
                artifact_id=artifact_id,
                title=title,
                path=rel_path if exists else None,
                kind="table",
                status="created" if exists else "not_available",
                description=description,
            )
        )

    notebook_path = write_marimo_review_notebook(
        output_root / "notebooks" / "scrna_qc_review.marimo.py",
        title="scRNA QC Review",
        run_dir=output_root,
        image_items=[
            ("QC Threshold Justification", "visualizations/threshold_justification.png"),
            ("QC Pass/Fail Counts", "visualizations/qc_pass_fail_counts.png"),
            ("UMAP by Coarse Label", "visualizations/umap_by_coarse_label.png"),
            ("UMAP by Leiden Cluster", "visualizations/umap_by_cluster.png"),
        ],
        table_items=[
            ("Cell QC Summary", "tables/cell_qc_summary.tsv"),
            ("Cell QC Metrics", "qc/cell_qc_metrics.csv"),
            ("Cell Labels", "annotation/cell_labels.csv"),
            ("UMAP Coordinates", "embeddings/umap_coords.csv"),
        ],
        object_items=[
            ("Analysis with flags", "analysis_with_flags.h5ad"),
            ("Filtered review object", "filtered_view.h5ad"),
        ],
    )
    entries.append(
        artifact_entry(
            artifact_id="scrna_qc_review_notebook",
            title="scRNA QC Review Notebook",
            path=notebook_path.relative_to(output_root),
            kind="marimo_notebook",
            status="created",
            description="Interactive review notebook over the generated QC, UMAP, and annotation artifacts.",
        )
    )
    if review_app_info:
        entries.append(
            artifact_entry(
                artifact_id="scrna_qc_review_launch",
                title="scRNA QC Review App",
                path=review_app_info.get("url"),
                kind="localhost_app",
                status="created" if review_app_info.get("ok") else "blocked",
                description="Auto-launched localhost Marimo review app for the generated notebook.",
                source="notebooks/marimo_server.json",
            )
        )
        if review_app_info.get("ok"):
            notes.append(f"Review app auto-launched at {review_app_info['url']}.")
        else:
            notes.append(
                "Review app auto-launch did not become ready. See notebooks/marimo_server.json and logs/marimo_server.log."
            )

    index_path = write_visualization_index(
        output_root,
        title="scRNA Post-count QC Visualizations",
        description="Portable scRNA QC artifact bundle with an auto-launched Marimo review app and a notebook backup.",
        entries=entries,
        notes=notes,
    )
    return {
        "visualization_index": str(index_path.relative_to(output_root)),
        "visualization_manifest": "visualizations/visualization_manifest.json",
        "review_notebook": str(notebook_path.relative_to(output_root)),
    }


def run_scdbfinder(
    matrix_dir: Path, out_csv: Path, timeout: int, rscript: Path | None
) -> dict[str, Any]:
    rscript_cmd = str(rscript) if rscript else command_path("Rscript")
    if not rscript_cmd:
        return {"ok": False, "error": "Rscript not found"}
    r_script = dedent(
        f"""
        suppressPackageStartupMessages({{
          library(DropletUtils)
          library(scDblFinder)
        }})
        sce <- read10xCounts("{matrix_dir.as_posix()}", col.names=TRUE)
        sce <- scDblFinder(sce)
        out <- data.frame(
          barcode=colnames(sce),
          scDblFinder_score=colData(sce)$scDblFinder.score,
          scDblFinder_class=colData(sce)$scDblFinder.class,
          row.names=NULL
        )
        write.csv(out, "{out_csv.as_posix()}", row.names=FALSE)
        """
    ).strip()
    with tempfile.NamedTemporaryFile("w", suffix=".R", delete=False, encoding="utf-8") as handle:
        handle.write(r_script)
        temp_script = Path(handle.name)
    try:
        result = run_cmd([rscript_cmd, str(temp_script)], WORKSPACE_ROOT, timeout=timeout)
    finally:
        temp_script.unlink(missing_ok=True)
    return result


def run_emptydrops(
    matrix_dir: Path, out_csv: Path, timeout: int, rscript: Path | None
) -> dict[str, Any]:
    rscript_cmd = str(rscript) if rscript else command_path("Rscript")
    if not rscript_cmd:
        return {"ok": False, "error": "Rscript not found"}
    r_script = dedent(
        f"""
        suppressPackageStartupMessages({{
          library(DropletUtils)
        }})
        sce <- read10xCounts("{matrix_dir.as_posix()}", col.names=TRUE)
        ed <- emptyDrops(counts(sce))
        out <- data.frame(
          barcode=rownames(ed),
          FDR=ed$FDR,
          LogProb=ed$LogProb,
          Limited=ed$Limited,
          row.names=NULL
        )
        write.csv(out, "{out_csv.as_posix()}", row.names=FALSE)
        """
    ).strip()
    with tempfile.NamedTemporaryFile("w", suffix=".R", delete=False, encoding="utf-8") as handle:
        handle.write(r_script)
        temp_script = Path(handle.name)
    try:
        result = run_cmd([rscript_cmd, str(temp_script)], WORKSPACE_ROOT, timeout=timeout)
    finally:
        temp_script.unlink(missing_ok=True)
    return result


def add_marker_scores(adata: ad.AnnData) -> list[str]:
    marker_sets = {
        "T_cell": ["IL7R", "LTB", "MALAT1", "IL32", "LTB"],
        "NK_cell": ["NKG7", "GNLY", "PRF1", "CCL5", "GZMB"],
        "B_cell": ["MS4A1", "CD79A", "CD79B", "HLA-DRA", "CD74"],
        "CD14_mono": ["LST1", "S100A8", "S100A9", "FCN1", "LGALS3"],
        "FCGR3A_mono": ["FCGR3A", "MS4A7", "LST1", "IFITM3", "SAT1"],
        "DC": ["FCER1A", "CST3", "HLA-DRA", "CLEC10A", "FCER1G"],
        "Platelet": ["PPBP", "PF4", "SDPR", "NRGN", "GNG11"],
    }
    created: list[str] = []
    for label, genes in marker_sets.items():
        present = [gene for gene in genes if gene in adata.var_names]
        if not present:
            continue
        score_name = f"{label}_score"
        sc.tl.score_genes(adata, gene_list=present, score_name=score_name, use_raw=False)
        created.append(score_name)
    return created


def assign_labels(adata: ad.AnnData, score_columns: list[str]) -> pd.DataFrame:
    if not score_columns:
        result = pd.DataFrame(index=adata.obs_names)
        result["coarse_label"] = "unknown"
        result["label_confidence"] = 0.0
        return result
    scores = adata.obs[score_columns].copy()
    top_label = scores.idxmax(axis=1).str.replace("_score", "", regex=False)
    top_score = scores.max(axis=1)
    runner_up = scores.apply(
        lambda row: row.nlargest(2).iloc[-1] if row.notna().sum() >= 2 else 0.0, axis=1
    )
    delta = top_score - runner_up
    label = np.where((top_score > 0.1) & (delta > 0.02), top_label, "ambiguous")
    confidence = delta.clip(lower=0.0)
    return pd.DataFrame(
        {"coarse_label": label, "label_confidence": confidence}, index=adata.obs_names
    )


def package_versions() -> dict[str, str]:
    import importlib.metadata

    packages = [
        "scanpy",
        "anndata",
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "igraph",
        "leidenalg",
        "marimo",
    ]
    versions: dict[str, str] = {}
    for pkg in packages:
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "missing"
    return versions


def build_analysis_status(
    *,
    dataset_metadata: dict[str, Any],
    dbl_result: dict[str, Any],
    review_app_info: dict[str, Any] | None,
) -> dict[str, Any]:
    blocking_issues: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not dbl_result.get("ok"):
        blocking_issues.append(
            {
                "component": "doublet_detection",
                "reason": scdbfinder_blocker_reason(dbl_result),
                "detail": dbl_result.get("stdout_tail") or dbl_result.get("error"),
            }
        )
    if dataset_metadata.get("batch_count", 0) <= 1:
        warnings.append(
            "No cell-level batch or channel metadata were provided, so QC and doublet logic could not be partition-aware."
        )
    warnings.append(
        "Ambient RNA modeling was skipped because the bundle contains a filtered matrix without raw droplets."
    )
    warnings.append(
        "Annotation used a conservative PBMC marker fallback because no matched reference atlas was provided."
    )
    if review_app_info and not review_app_info.get("ok"):
        warnings.append(
            "The Marimo review app was generated but did not become ready before timeout; reopen it from the recorded localhost URL if needed."
        )
    return {
        "completion_state": "complete" if not blocking_issues else "partial",
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }


def write_summary_md(
    output_root: Path,
    *,
    dataset_metadata: dict[str, Any],
    thresholds: dict[str, Any],
    qc_summary_rows: list[dict[str, Any]],
    analysis_status: dict[str, Any],
    review_app_info: dict[str, Any] | None,
) -> None:
    metric_map = {row["metric"]: row["cells"] for row in qc_summary_rows}
    lines = [
        "# scRNA Post-count QC Summary",
        "",
        f"- Dataset ID: `{dataset_metadata.get('dataset_id', 'unknown')}`",
        f"- Organism / assay: `{dataset_metadata.get('organism', 'unknown')}` / `{dataset_metadata.get('assay', 'unknown')}`",
        f"- Completion state: `{analysis_status['completion_state']}`",
        f"- Input cells: `{metric_map.get('input_cells', 'n/a')}`",
        f"- QC-passing cells: `{metric_map.get('passes_qc', 'n/a')}`",
        f"- Plot-included cells: `{metric_map.get('plot_include', 'n/a')}`",
        f"- Doublet detection complete: `{not bool(analysis_status['blocking_issues'])}`",
        f"- Review app URL: `{review_app_info.get('url') if review_app_info else 'not started'}`",
        "",
        "## Thresholds",
        f"- Detected genes lower bound: `{thresholds['n_genes_by_counts']['lower']:.2f}`",
        f"- Total counts lower bound: `{thresholds['total_counts']['lower']:.2f}`",
        f"- Mitochondrial fraction upper bound: `{thresholds['pct_counts_mt']['upper']}`",
        "",
        "## Notes",
    ]
    for warning in analysis_status["warnings"]:
        lines.append(f"- {warning}")
    if analysis_status["blocking_issues"]:
        lines.extend(["", "## Blocking Issues"])
        for issue in analysis_status["blocking_issues"]:
            lines.append(f"- {issue['component']}: {issue['reason']}")
    write_text(output_root / "summary.md", "\n".join(lines) + "\n")


def maybe_launch_review_app(
    args: argparse.Namespace, output_root: Path, notebook_path: Path
) -> dict[str, Any]:
    info_path = output_root / "notebooks" / "marimo_server.json"
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
            run_dir=output_root,
            start_port=args.review_app_port,
            python_executable=os.environ.get("PYTHON_EXECUTABLE_OVERRIDE"),
        )
    except Exception as exc:  # noqa: BLE001
        info = {"ok": False, "error": str(exc)}
    write_json(info_path, info)
    return info


def run_pipeline(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    started_at = now_iso()
    input_dir, matrix_dir, raw_matrix_dir, metadata_path, manifest_path = matrix_paths(args)
    output_root = (
        args.output_dir.expanduser().resolve()
        if args.output_dir
        else input_dir / "output" / slug_timestamp()
    )
    output_root.mkdir(parents=True, exist_ok=True)
    for child in [
        "validation",
        "qc",
        "annotation",
        "embeddings",
        "plots",
        "provenance",
        "tables",
        "visualizations",
        "notebooks",
        "logs",
        "manifest",
        "versions",
    ]:
        (output_root / child).mkdir(parents=True, exist_ok=True)

    validation = validate_inputs(matrix_dir, raw_matrix_dir, metadata_path, manifest_path)
    write_json(output_root / "validation" / "input_summary.json", validation)
    dep_status = r_dependency_status(args.rscript)
    write_json(output_root / "validation" / "tool_preflight.json", dep_status)
    if validation["errors"]:
        write_text(
            output_root / "summary.md",
            "Input validation failed. See validation/input_summary.json for details.\n",
        )
        write_standard_manifest(
            output_root,
            run_id=output_root.name,
            lane="scrnaseq_post_count_qc",
            workflow="local_light_scanpy_qc",
            status="blocked",
            execute_requested=True,
            validation={"ok": False, **validation},
            tool_preflight_result={"ok": dep_status.get("ok", False), **dep_status},
            dry_run={"ok": False, "detail": "input validation failed"},
            execution={"ok": False, "detail": "execution not attempted"},
            inputs={
                "input_dir": str(input_dir),
                "matrix_dir": str(matrix_dir),
                "raw_matrix_dir": str(raw_matrix_dir) if raw_matrix_dir else None,
                "dataset_metadata": str(metadata_path),
                "manifest": str(manifest_path),
            },
            outputs={"summary": "summary.md", "validation": "validation/input_summary.json"},
            method={"resolution": args.resolution},
        )
        write_json(output_root / "artifact_index.json", build_artifact_index(output_root))
        raise SystemExit("Input validation failed. See validation/input_summary.json for details.")

    python_dep_status = load_analysis_modules()
    write_json(output_root / "validation" / "python_dependency_preflight.json", python_dep_status)
    if not python_dep_status["ok"]:
        write_text(
            output_root / "summary.md",
            "Python dependency preflight failed. See validation/python_dependency_preflight.json for details.\n",
        )
        write_standard_manifest(
            output_root,
            run_id=output_root.name,
            lane="scrnaseq_post_count_qc",
            workflow="local_light_scanpy_qc",
            status="blocked",
            execute_requested=True,
            validation={"ok": True, **validation},
            tool_preflight_result=combined_tool_preflight_status(python_dep_status, dep_status),
            dry_run={"ok": False, "detail": "Python dependency preflight failed"},
            execution={"ok": False, "detail": "execution not attempted"},
            inputs={
                "input_dir": str(input_dir),
                "matrix_dir": str(matrix_dir),
                "raw_matrix_dir": str(raw_matrix_dir) if raw_matrix_dir else None,
                "dataset_metadata": str(metadata_path),
                "manifest": str(manifest_path),
            },
            outputs={
                "summary": "summary.md",
                "python_dependency_preflight": "validation/python_dependency_preflight.json",
                "r_dependency_preflight": "validation/tool_preflight.json",
            },
            method={"resolution": args.resolution},
        )
        write_json(output_root / "artifact_index.json", build_artifact_index(output_root))
        raise SystemExit(
            "Python dependency preflight failed. See validation/python_dependency_preflight.json for details."
        )

    dataset_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    adata = sc.read_10x_mtx(matrix_dir, var_names="gene_symbols", cache=False)
    adata.var_names_make_unique()
    adata.layers["counts"] = adata.X.copy()
    adata.uns["input_metadata"] = dataset_metadata
    adata.uns["runtime_environment"] = RUNTIME_ENV
    adata.obs["barcode"] = adata.obs_names.to_numpy()
    adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)

    thresholds = threshold_dict(adata)
    mito_upper = thresholds["pct_counts_mt"]["upper"]
    mito_mask = True if mito_upper is None else adata.obs["pct_counts_mt"] <= mito_upper
    adata.obs["passes_qc"] = (
        (adata.obs["n_genes_by_counts"] >= thresholds["n_genes_by_counts"]["lower"])
        & (adata.obs["total_counts"] >= thresholds["total_counts"]["lower"])
        & mito_mask
    )
    adata.obs["high_gene_outlier"] = (
        adata.obs["n_genes_by_counts"] > thresholds["n_genes_by_counts"]["upper_review"]
    )
    adata.obs["high_count_outlier"] = (
        adata.obs["total_counts"] > thresholds["total_counts"]["upper_review"]
    )
    plot_thresholds(adata, thresholds, output_root / "qc" / "threshold_justification.png")
    write_json(output_root / "qc" / "thresholds.json", thresholds)

    dbl_out = output_root / "qc" / "doublet_calls.csv"
    dbl_readiness = scdbfinder_readiness(adata)
    if not dep_status.get("packages", {}).get("scDblFinder", False) or not dep_status.get(
        "packages", {}
    ).get("DropletUtils", False):
        dbl_result = {
            "ok": False,
            "reason": "missing_r_dependencies",
            "error": "scDblFinder and DropletUtils must both be available in the selected R runtime.",
        }
    elif not args.rscript and not command_path("Rscript"):
        dbl_result = {"ok": False, "reason": "rscript_missing", "error": "Rscript not found"}
    elif not dbl_readiness["ok"]:
        dbl_result = {
            "ok": False,
            "reason": dbl_readiness["reason"],
            "error": dbl_readiness["detail"],
            "readiness": dbl_readiness,
        }
    else:
        dbl_result = run_scdbfinder(
            matrix_dir, dbl_out, timeout=args.timeout_seconds, rscript=args.rscript
        )
    if dbl_result["ok"] and dbl_out.exists():
        dbl_df = pd.read_csv(dbl_out)
        dbl_df = dbl_df.set_index("barcode").reindex(adata.obs_names)
        adata.obs["doublet_score"] = dbl_df["scDblFinder_score"].to_numpy()
        adata.obs["doublet_class"] = dbl_df["scDblFinder_class"].fillna("unknown").to_numpy()
    else:
        adata.obs["doublet_score"] = np.nan
        adata.obs["doublet_class"] = "blocked"
        write_text(
            output_root / "qc" / "doublet_blocker.txt",
            f"{scdbfinder_blocker_reason(dbl_result)}\n"
            f"Command status: {json.dumps(dbl_result, indent=2, sort_keys=True)}\n",
        )

    emptydrops_result = {"ok": False, "reason": "raw droplet matrix not provided"}
    if raw_matrix_dir is None:
        write_text(
            output_root / "qc" / "emptydrops_skip.txt",
            "emptyDrops skipped: no raw droplet matrix directory was provided.\n",
        )
    elif not dep_status.get("packages", {}).get("DropletUtils", False):
        write_text(
            output_root / "qc" / "emptydrops_skip.txt",
            "emptyDrops skipped: DropletUtils is not available in the current R runtime.\n",
        )
        emptydrops_result = {"ok": False, "reason": "DropletUtils unavailable"}
    else:
        emptydrops_out = output_root / "qc" / "emptydrops_calls.csv"
        emptydrops_result = run_emptydrops(
            raw_matrix_dir, emptydrops_out, timeout=args.timeout_seconds, rscript=args.rscript
        )
        if emptydrops_result.get("ok") and emptydrops_out.exists():
            ed_df = pd.read_csv(emptydrops_out)
            ed_df = ed_df.set_index("barcode").reindex(adata.obs_names)
            adata.obs["emptydrops_fdr"] = ed_df["FDR"].to_numpy()
        else:
            write_text(
                output_root / "qc" / "emptydrops_skip.txt",
                "emptyDrops attempted but did not complete successfully.\n"
                f"Command status: {json.dumps(emptydrops_result, indent=2, sort_keys=True)}\n",
            )

    ambient_note = (
        "Ambient RNA estimation was not executed. A raw droplet matrix plus a supported ambient backend are required for robust modeling; "
        "ambient-derived hard filters were not applied in this run."
    )
    adata.obs["ambient_flag"] = False
    write_text(output_root / "qc" / "ambient_limitations.md", ambient_note + "\n")

    adata.obs["plot_include"] = adata.obs["passes_qc"] & adata.obs["doublet_class"].ne("doublet")
    qc_metrics = adata.obs[
        [
            "barcode",
            "total_counts",
            "n_genes_by_counts",
            "pct_counts_mt",
            "passes_qc",
            "high_gene_outlier",
            "high_count_outlier",
            "doublet_score",
            "doublet_class",
            "ambient_flag",
            "plot_include",
        ]
    ].copy()
    qc_metrics.to_csv(output_root / "qc" / "cell_qc_metrics.csv", index=False)
    qc_summary_rows = [
        {"metric": "input_cells", "cells": int(adata.n_obs)},
        {"metric": "passes_qc", "cells": int(adata.obs["passes_qc"].sum())},
        {"metric": "plot_include", "cells": int(adata.obs["plot_include"].sum())},
        {"metric": "high_gene_outlier", "cells": int(adata.obs["high_gene_outlier"].sum())},
        {"metric": "high_count_outlier", "cells": int(adata.obs["high_count_outlier"].sum())},
        {
            "metric": "doublet_blocked_or_called",
            "cells": int(adata.obs["doublet_class"].ne("unknown").sum()),
        },
    ]
    write_tsv(output_root / "tables" / "cell_qc_summary.tsv", qc_summary_rows, ["metric", "cells"])
    plot_count_summary(
        qc_summary_rows,
        output_root / "qc" / "qc_pass_fail_counts.png",
        title="scRNA QC Cell Counts",
    )

    plot_view = adata[adata.obs["plot_include"].to_numpy()].copy()
    fallback_note = None
    if plot_view.n_obs == 0:
        nonzero_mask = adata.obs["total_counts"].to_numpy() > 0
        if int(nonzero_mask.sum()) > 0:
            plot_view = adata[nonzero_mask].copy()
            fallback_note = (
                "No cells passed the default QC mask. Nonzero-count cells were used for visualization-only outputs so the "
                "artifact bundle remains reviewable."
            )
        else:
            plot_view = adata[:1].copy()
            fallback_note = "No nonzero-count cells were available. A one-cell placeholder view was used for visualization-only outputs."
    if fallback_note:
        write_text(output_root / "qc" / "plot_view_fallback.txt", fallback_note + "\n")

    if plot_view.n_obs >= 3:
        sc.pp.normalize_total(plot_view, target_sum=1e4)
        sc.pp.log1p(plot_view)
        sc.pp.highly_variable_genes(plot_view, n_top_genes=2000, flavor="seurat", subset=False)
        sc.tl.pca(plot_view, use_highly_variable=True, svd_solver="arpack")
        sc.pp.neighbors(plot_view, n_neighbors=15, n_pcs=30)
        sc.tl.umap(plot_view)
        sc.tl.leiden(plot_view, resolution=args.resolution, key_added="leiden")
        score_columns = add_marker_scores(plot_view)
        labels = assign_labels(plot_view, score_columns)
        plot_view.obs["coarse_label"] = labels["coarse_label"].to_numpy()
        plot_view.obs["label_confidence"] = labels["label_confidence"].to_numpy()
        marker_summary = []
        if score_columns:
            for score_name in score_columns:
                marker_summary.append(
                    {
                        "score_name": score_name,
                        "n_cells_positive": int((plot_view.obs[score_name] > 0).sum()),
                    }
                )
        reference_manifest = {
            "mode": "marker_based_fallback",
            "reason": "No matched reference atlas was provided in the input bundle; conservative PBMC marker scoring was used.",
            "score_columns": score_columns,
        }

        fig, ax = plt.subplots(figsize=(7.5, 6.5))
        sc.pl.umap(
            plot_view,
            color="coarse_label",
            ax=ax,
            show=False,
            frameon=False,
            legend_loc="right margin",
        )
        fig.tight_layout()
        fig.savefig(output_root / "plots" / "umap_global.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7.5, 6.5))
        sc.pl.umap(
            plot_view, color="leiden", ax=ax, show=False, frameon=False, legend_loc="on data"
        )
        fig.tight_layout()
        fig.savefig(output_root / "plots" / "umap_by_coarse_label.png", dpi=160)
        plt.close(fig)
    else:
        score_columns = []
        plot_view.obs["leiden"] = [str(i) for i in range(plot_view.n_obs)]
        plot_view.obs["coarse_label"] = "unknown"
        plot_view.obs["label_confidence"] = 0.0
        coords = np.zeros((plot_view.n_obs, 2), dtype=float)
        if plot_view.n_obs > 1:
            coords[:, 0] = np.arange(plot_view.n_obs, dtype=float)
        plot_view.obsm["X_umap"] = coords
        marker_summary = []
        reference_manifest = {
            "mode": "tiny_dataset_fallback",
            "reason": "Fewer than 3 cells were available for embedding; simple coordinates were emitted so the portable review bundle stays intact.",
            "score_columns": score_columns,
        }
        plot_simple_embedding(
            coords,
            plot_view.obs["coarse_label"],
            output_root / "plots" / "umap_global.png",
            title="UMAP by Coarse Label",
        )
        plot_simple_embedding(
            coords,
            plot_view.obs["leiden"],
            output_root / "plots" / "umap_by_coarse_label.png",
            title="UMAP by Leiden Cluster",
        )

    plot_view.obs.to_csv(output_root / "annotation" / "cell_labels.csv")
    umap_coords = pd.DataFrame(
        plot_view.obsm["X_umap"], index=plot_view.obs_names, columns=["UMAP1", "UMAP2"]
    )
    umap_coords.to_csv(output_root / "embeddings" / "umap_coords.csv")
    pd.DataFrame(marker_summary).to_csv(
        output_root / "annotation" / "marker_summary.csv", index=False
    )
    write_json(output_root / "annotation" / "reference_manifest.json", reference_manifest)

    adata.write_h5ad(output_root / "analysis_with_flags.h5ad", compression="gzip")
    plot_view.write_h5ad(output_root / "filtered_view.h5ad", compression="gzip")

    visualization_outputs = write_scrna_visual_bundle(output_root, None)
    review_notebook_path = output_root / visualization_outputs["review_notebook"]
    review_app_info = (
        maybe_launch_review_app(args, output_root, review_notebook_path)
        if review_notebook_path.exists()
        else None
    )
    analysis_status = build_analysis_status(
        dataset_metadata=dataset_metadata, dbl_result=dbl_result, review_app_info=review_app_info
    )
    write_json(output_root / "provenance" / "analysis_status.json", analysis_status)

    versions = package_versions()
    write_json(output_root / "versions" / "software_versions.json", versions)
    write_json(output_root / "provenance" / "package_versions.json", versions)
    write_json(
        output_root / "provenance" / "run_manifest.json",
        {
            "started_at": started_at,
            "finished_at": now_iso(),
            "input_dir": str(input_dir),
            "matrix_dir": str(matrix_dir),
            "raw_matrix_dir": str(raw_matrix_dir) if raw_matrix_dir else None,
            "metadata_path": str(metadata_path),
            "thresholds": thresholds,
            "resolution": args.resolution,
            "doublet_result": dbl_result,
            "emptydrops_result": emptydrops_result,
            "analysis_status": analysis_status,
            "runtime_environment": RUNTIME_ENV,
            "review_app": review_app_info,
        },
    )

    visualization_outputs = write_scrna_visual_bundle(output_root, review_app_info)
    write_summary_md(
        output_root,
        dataset_metadata=dataset_metadata,
        thresholds=thresholds,
        qc_summary_rows=qc_summary_rows,
        analysis_status=analysis_status,
        review_app_info=review_app_info,
    )
    write_standard_manifest(
        output_root,
        run_id=output_root.name,
        lane="scrnaseq_post_count_qc",
        workflow="local_light_scanpy_qc",
        status="completed",
        execute_requested=True,
        validation={"ok": True, "errors": [], "warnings": [], **validation},
        tool_preflight_result=combined_tool_preflight_status(python_dep_status, dep_status),
        dry_run={"ok": True, "detail": "matrix and metadata validation completed"},
        execution={"ok": True, "detail": "post-count QC completed"},
        inputs={
            "input_dir": str(input_dir),
            "matrix_dir": str(matrix_dir),
            "raw_matrix_dir": str(raw_matrix_dir) if raw_matrix_dir else None,
            "dataset_metadata": str(metadata_path),
            "manifest": str(manifest_path),
        },
        outputs={
            "analysis_h5ad": "analysis_with_flags.h5ad",
            "filtered_h5ad": "filtered_view.h5ad",
            "qc_summary": "tables/cell_qc_summary.tsv",
            "labels": "annotation/cell_labels.csv",
            "visualization_manifest": "visualizations/visualization_manifest.json",
            "versions": "versions/software_versions.json",
        },
        method={
            "thresholds": thresholds,
            "resolution": args.resolution,
            "doublet_method": "scDblFinder",
            "emptydrops_enabled": raw_matrix_dir is not None,
            "ambient_step": "explicit_skip_unless_raw_and_backend_available",
        },
        review_bundle=visualization_outputs,
    )
    write_json(output_root / "artifact_index.json", build_artifact_index(output_root))
    return output_root, {
        "cells_input": int(adata.n_obs),
        "cells_plot_include": int(plot_view.n_obs),
        "doublet_ok": dbl_result["ok"],
        "emptydrops_ok": emptydrops_result.get("ok", False),
        "review_app_url": review_app_info.get("url") if review_app_info else None,
    }


def main() -> int:
    args = parse_args()
    out_dir, summary = run_pipeline(args)
    print(json.dumps({"output_dir": str(out_dir), "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
