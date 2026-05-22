#!/usr/bin/env python3
"""Run local bulk RNA-seq counts/QC with Salmon, FastQC, MultiQC, and matrices."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
import shlex
import shutil
import statistics
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import ngs_resource_gate
from ngs_run_utils import (
    build_artifact_index,
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
    reachable_localhost_url_for_path,
    write_localhost_launch_hint,
    write_marimo_review_notebook,
    write_multiqc_browser_helper,
    write_visualization_index,
)

SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = SCRIPT_PATH.parents[1]
WORKFLOW_ROOT = PLUGIN_ROOT / "workflows" / "bulk_rnaseq_counts_qc"
WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "bulk_rnaseq_counts_qc"
SAMPLE_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
FASTQ_EXTENSIONS = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
QC_THRESHOLDS = {
    "mapping_rate_warn": 70.0,
    "mapping_rate_fail": 50.0,
    "duplication_warn": 60.0,
    "duplication_fail": 80.0,
    "strand_bias_warn": 0.10,
    "outlier_delta_warn": 10.0,
}


def load_yaml_module() -> Any | None:
    try:
        import yaml as yaml_module  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        if exc.name == "yaml":
            return None
        raise
    return yaml_module


def yaml_dependency_status() -> dict[str, Any]:
    yaml_module = load_yaml_module()
    if yaml_module is None:
        return {
            "ok": False,
            "python_modules": {"yaml": {"present": False, "package": "PyYAML"}},
            "errors": ["Python package PyYAML is required to write config.yaml."],
        }
    return {
        "ok": True,
        "python_modules": {
            "yaml": {
                "present": True,
                "package": "PyYAML",
                "version": getattr(yaml_module, "__version__", None),
            }
        },
        "errors": [],
    }


def salmon_libtype(layout: str, strandedness: str) -> tuple[str, str]:
    normalized = strandedness.lower().strip()
    if normalized in {"auto", "unknown"}:
        return "A", "infer_from_salmon"
    if layout == "PE":
        return {
            "forward": ("ISF", "from_input"),
            "reverse": ("ISR", "from_input"),
            "unstranded": ("IU", "from_input"),
        }.get(normalized, ("A", "infer_from_salmon"))
    return {
        "forward": ("SF", "from_input"),
        "reverse": ("SR", "from_input"),
        "unstranded": ("U", "from_input"),
    }.get(normalized, ("A", "infer_from_salmon"))


def filename_from_uri(value: str) -> str:
    if value.startswith(("http://", "https://", "s3://", "gs://")):
        return Path(urlparse(value).path).name
    return Path(value).name


def resolve_existing_path(raw: str, base: Path, roots: list[Path]) -> Path | None:
    if not raw:
        return None
    if raw.startswith(("http://", "https://", "s3://", "gs://")):
        basename = filename_from_uri(raw)
    else:
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = base / candidate
        if candidate.exists():
            return candidate.resolve()
        basename = candidate.name

    matches: list[Path] = []
    for root in roots:
        direct = root / basename
        if direct.exists():
            matches.append(direct.resolve())
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise FileExistsError(f"ambiguous FASTQ basename {basename}: {matches}")
    return None


def open_fastq_text(path: Path):
    if path.name.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("rt", encoding="utf-8", errors="replace")


def check_fastq(path: Path, quick: bool, max_records: int) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "readable": False,
        "records_checked": 0,
        "record_count": None,
        "errors": [],
    }
    if not path.exists():
        result["errors"].append("file does not exist")
        return result
    if not path.is_file():
        result["errors"].append("path is not a file")
        return result
    if not path.name.endswith(FASTQ_EXTENSIONS):
        result["errors"].append("file extension is not a recognized FASTQ extension")
    result["readable"] = True
    try:
        with open_fastq_text(path) as handle:
            record_count = 0
            while True:
                header = handle.readline()
                if not header:
                    break
                sequence = handle.readline()
                plus = handle.readline()
                quality = handle.readline()
                if not quality:
                    result["errors"].append(f"incomplete FASTQ record after record {record_count}")
                    break
                record_count += 1
                if not header.startswith("@"):
                    result["errors"].append(f"record {record_count} header does not start with @")
                if not plus.startswith("+"):
                    result["errors"].append(
                        f"record {record_count} separator does not start with +"
                    )
                if len(sequence.rstrip("\n\r")) != len(quality.rstrip("\n\r")):
                    result["errors"].append(
                        f"record {record_count} sequence and quality lengths differ"
                    )
                if quick and record_count >= max_records:
                    break
        result["records_checked"] = record_count
        result["record_count"] = None if quick else record_count
    except OSError as exc:
        result["errors"].append(f"read failed: {exc}")
    return result


def read_samplesheet(
    path: Path, fastq_roots: list[Path], quick: bool, max_records: int
) -> tuple[dict[str, Any], list[dict[str, str]], dict[str, Any]]:
    rows: list[dict[str, str]] = []
    grouped: dict[str, dict[str, Any]] = {}
    fastq_files: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    warnings: list[str] = []
    fastq_checks: list[dict[str, Any]] = []
    required = {"sample", "fastq_1", "strandedness"}

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        observed = set(reader.fieldnames or [])
        missing = sorted(required - observed)
        if missing:
            raise ValueError(f"sample sheet missing required columns: {', '.join(missing)}")
        for row_index, row in enumerate(reader, start=2):
            sample = (row.get("sample") or "").strip()
            fastq_1_raw = (row.get("fastq_1") or "").strip()
            fastq_2_raw = (row.get("fastq_2") or "").strip()
            strandedness = (row.get("strandedness") or "").strip().lower()
            if not sample or not fastq_1_raw:
                errors.append(f"row {row_index}: sample and fastq_1 are required")
                continue
            if not SAMPLE_RE.match(sample):
                errors.append(f"row {row_index}: sample contains unsupported characters: {sample}")
            if strandedness not in {"forward", "reverse", "unstranded", "auto", "unknown"}:
                errors.append(f"row {row_index}: unsupported strandedness value: {strandedness}")

            r1 = resolve_existing_path(fastq_1_raw, path.parent, fastq_roots)
            r2 = (
                resolve_existing_path(fastq_2_raw, path.parent, fastq_roots)
                if fastq_2_raw
                else None
            )
            if not r1:
                errors.append(f"row {row_index}: could not resolve fastq_1 path {fastq_1_raw}")
                continue
            if fastq_2_raw and not r2:
                errors.append(f"row {row_index}: could not resolve fastq_2 path {fastq_2_raw}")
                continue

            layout = "PE" if r2 else "SE"
            libtype, libtype_source = salmon_libtype(layout, strandedness)
            grouped.setdefault(
                sample,
                {
                    "sample": sample,
                    "layout": layout,
                    "strandedness": strandedness,
                    "salmon_libtype": libtype,
                    "salmon_libtype_source": libtype_source,
                    "r1": [],
                    "r2": [],
                    "row_indices": [],
                },
            )
            entry = grouped[sample]
            if entry["layout"] != layout:
                errors.append(f"sample {sample} mixes PE and SE rows")
            if entry["strandedness"] != strandedness:
                errors.append(f"sample {sample} mixes strandedness values")
            if entry["salmon_libtype"] != libtype:
                errors.append(f"sample {sample} mixes Salmon library types")
            entry["r1"].append(str(r1))
            if r2:
                entry["r2"].append(str(r2))
            entry["row_indices"].append(row_index)

            for read_label, read_path in [("r1", r1), ("r2", r2)]:
                if read_path is None:
                    continue
                unit = f"{sample}__row{row_index}__{read_label}"
                fastq_files[unit] = {"sample": sample, "read": read_label, "path": str(read_path)}
                stats = check_fastq(read_path, quick=quick, max_records=max_records)
                stats["unit"] = unit
                fastq_checks.append(stats)
                if stats["errors"]:
                    errors.extend(f"{unit}: {error}" for error in stats["errors"])

            rows.append(
                {
                    "sample": sample,
                    "row_index": str(row_index),
                    "fastq_1": fastq_1_raw,
                    "fastq_2": fastq_2_raw,
                    "resolved_fastq_1": str(r1),
                    "resolved_fastq_2": str(r2) if r2 else "",
                    "layout": layout,
                    "strandedness": strandedness,
                    "salmon_libtype": libtype,
                }
            )

    if not grouped:
        errors.append("no valid samples found in sample sheet")
    return (
        {
            "ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "fastq_checks": fastq_checks,
            "sample_count": len(grouped),
        },
        rows,
        {"rnaseq_salmon_samples": grouped, "fastq_files": fastq_files},
    )


def write_normalized_samplesheet(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sample",
        "row_index",
        "fastq_1",
        "fastq_2",
        "resolved_fastq_1",
        "resolved_fastq_2",
        "layout",
        "strandedness",
        "salmon_libtype",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def validate_references(args: argparse.Namespace) -> dict[str, Any]:
    references = {
        "transcriptome_fasta": args.transcriptome_fasta.expanduser().resolve()
        if args.transcriptome_fasta
        else None,
        "genome_fasta": args.genome_fasta.expanduser().resolve() if args.genome_fasta else None,
        "annotation_gtf": args.annotation_gtf.expanduser().resolve()
        if args.annotation_gtf
        else None,
    }
    errors = []
    warnings = []
    if not references["transcriptome_fasta"]:
        errors.append("--transcriptome-fasta is required for Salmon quantification")
    for key, path in references.items():
        if path and not path.exists():
            errors.append(f"{key} does not exist: {path}")
    if not references["genome_fasta"]:
        warnings.append(
            "genome FASTA not provided; alignment-aware STAR path is not executed by this Salmon local runner"
        )
    if not references["annotation_gtf"]:
        warnings.append(
            "annotation GTF not provided; gene-level summarization is not emitted by this transcript-level runner"
        )
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "references": {key: str(path) if path else None for key, path in references.items()},
    }


def read_tsv_table(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def fastqc_sample_to_group(sample_name: str, fastq_files: dict[str, dict[str, str]]) -> str | None:
    for details in fastq_files.values():
        basename = Path(details["path"]).name
        for suffix in FASTQ_EXTENSIONS:
            if basename.endswith(suffix):
                basename = basename[: -len(suffix)]
                break
        if basename == sample_name:
            return details["sample"]
    return None


def compute_qc_verdict(run_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    fastq_stats = read_tsv_table(
        run_dir / "fastqc" / "multiqc" / "multiqc_data" / "multiqc_general_stats.txt"
    )
    salmon_stats = read_tsv_table(
        run_dir / "rnaseq_salmon" / "multiqc" / "multiqc_data" / "multiqc_general_stats.txt"
    )
    samples = config.get("rnaseq_salmon_samples", {})
    fastq_files = config.get("fastq_files", {})
    per_sample_duplication: dict[str, list[float]] = {}
    for row in fastq_stats:
        sample_name = row.get("Sample", "")
        grouped = fastqc_sample_to_group(sample_name, fastq_files)
        if not grouped:
            continue
        try:
            duplication = float(row.get("fastqc-percent_duplicates", ""))
        except ValueError:
            continue
        per_sample_duplication.setdefault(grouped, []).append(duplication)

    sample_rows: list[dict[str, Any]] = []
    mapping_rates: list[float] = []
    for row in salmon_stats:
        sample = row.get("Sample", "")
        if sample not in samples:
            continue
        try:
            mapping_rate = float(row.get("salmon-percent_mapped", "nan"))
        except ValueError:
            mapping_rate = math.nan
        if math.isfinite(mapping_rate):
            mapping_rates.append(mapping_rate)
        expected_libtype = samples[sample].get("salmon_libtype", "A")
        lib_format_path = run_dir / "rnaseq_salmon" / "quant" / sample / "lib_format_counts.json"
        observed_format = None
        strand_bias = None
        if lib_format_path.exists():
            payload = json.loads(lib_format_path.read_text(encoding="utf-8"))
            observed_format = payload.get("expected_format")
            strand_bias = payload.get("strand_mapping_bias")
        duplication_values = per_sample_duplication.get(sample, [])
        duplication = statistics.mean(duplication_values) if duplication_values else None
        mapping_status = "pass"
        if mapping_rate < QC_THRESHOLDS["mapping_rate_fail"]:
            mapping_status = "fail"
        elif mapping_rate < QC_THRESHOLDS["mapping_rate_warn"]:
            mapping_status = "warn"
        duplication_status = "pass"
        if duplication is not None:
            if duplication > QC_THRESHOLDS["duplication_fail"]:
                duplication_status = "fail"
            elif duplication > QC_THRESHOLDS["duplication_warn"]:
                duplication_status = "warn"
        libtype_status = "pass"
        if expected_libtype != "A" and observed_format and observed_format != expected_libtype:
            libtype_status = "fail"
        strand_bias_status = "pass"
        if strand_bias is not None and strand_bias > QC_THRESHOLDS["strand_bias_warn"]:
            strand_bias_status = "warn"
        sample_rows.append(
            {
                "sample": sample,
                "mapping_rate_percent": mapping_rate,
                "duplication_percent": duplication,
                "configured_libtype": expected_libtype,
                "observed_libtype": observed_format,
                "strand_bias": strand_bias,
                "mapping_rate_status": mapping_status,
                "duplication_status": duplication_status,
                "libtype_status": libtype_status,
                "strand_bias_status": strand_bias_status,
            }
        )
    median_mapping = statistics.median(mapping_rates) if mapping_rates else None
    outlier_samples: list[str] = []
    if median_mapping is not None:
        for row in sample_rows:
            if row["mapping_rate_percent"] <= median_mapping - QC_THRESHOLDS["outlier_delta_warn"]:
                outlier_samples.append(row["sample"])
                if row["mapping_rate_status"] == "pass":
                    row["mapping_rate_status"] = "warn"

    overall = "pass"
    for row in sample_rows:
        statuses = [
            row["mapping_rate_status"],
            row["duplication_status"],
            row["libtype_status"],
            row["strand_bias_status"],
        ]
        if "fail" in statuses:
            overall = "fail"
            break
        if "warn" in statuses:
            overall = "warn"
    return {
        "overall_status": overall,
        "thresholds": QC_THRESHOLDS,
        "outlier_samples": outlier_samples,
        "samples": sample_rows,
        "de_readiness": {
            "status": "caution",
            "reason": "Gene-level expected counts are derived from transcript-level Salmon quantification and are suitable for QC and exploratory review, but downstream DE should validate assumptions and metadata before model fitting.",
            "gene_level_counts": "rnaseq_salmon/matrices/gene_num_reads.tsv",
            "tx2gene_provenance": "rnaseq_salmon/matrices/tx2gene.tsv",
        },
    }


def write_workflow(run_dir: Path) -> None:
    workflow_dir = run_dir / "workflow"
    scripts_dir = workflow_dir / "scripts"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(WORKFLOW_ROOT / "Snakefile.smk", workflow_dir / "Snakefile")
    shutil.copy2(
        WORKFLOW_ROOT / "aggregate_salmon_quant.py", scripts_dir / "aggregate_salmon_quant.py"
    )


def snakemake_cmd(run_dir: Path, cores: int, dry_run: bool) -> list[str]:
    cmd = [
        "env",
        f"XDG_CACHE_HOME={run_dir / '.cache'}",
        "snakemake",
        "--snakefile",
        "workflow/Snakefile",
        "--configfile",
        "config.json",
        "--cores",
        str(cores),
        "--shared-fs-usage",
        "input-output",
        "persistence",
        "software-deployment",
        "software-deployment-cache",
        "sources",
        "storage-local-copies",
    ]
    if dry_run:
        cmd.append("--dry-run")
    return cmd


def write_commands(run_dir: Path, cores: int) -> None:
    write_text(
        run_dir / "commands.sh",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                shlex.join(snakemake_cmd(run_dir, cores, dry_run=True)),
                shlex.join(snakemake_cmd(run_dir, cores, dry_run=False)),
                "",
            ]
        ),
    )


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    reference_validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# Bulk RNA-seq Counts/QC Run Summary",
        "",
        f"Status: `{status}`",
        "",
        f"Samples parsed: `{validation.get('sample_count', 0)}`",
        "",
        "## Key Artifacts",
        "",
        "- `rnaseq_salmon/quant/*/quant.sf`",
        "- `rnaseq_salmon/matrices/tpm.tsv`",
        "- `rnaseq_salmon/matrices/num_reads.tsv`",
        "- `rnaseq_salmon/matrices/effective_length.tsv`",
        "- `rnaseq_salmon/matrices/gene_num_reads.tsv`",
        "- `rnaseq_salmon/matrices/tx2gene.tsv`",
        "- `qc/qc_verdict.json`",
        "- `visualizations/localhost_launch_hint.txt` for the preferred localhost MultiQC links",
        "- `fastqc/multiqc/multiqc_browser_helper.html`",
        "- `rnaseq_salmon/multiqc/multiqc_browser_helper.html`",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `artifact_index.json`",
        "",
    ]
    issues = validation.get("errors", []) + reference_validation.get("errors", [])
    if issues:
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
    lines.extend(ngs_resource_gate.resource_summary_lines(resource_plan))
    lines.append("Raw FASTQs and reference files were read-only inputs and were not modified.")
    lines.append("")
    write_text(run_dir / "summary.md", "\n".join(lines))


def generate_visualizations(
    run_dir: Path,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> dict[str, str]:
    entries: list[dict[str, Any]] = []
    notes = [
        "artifact_index.json now includes per-file SHA256 and modification timestamps for provenance.",
        "Use the MultiQC browser helpers when the raw MultiQC HTML stalls under file:// in the Codex browser.",
        "Serve the run directory over localhost and open the browser helpers for a stable in-app review path.",
    ]
    if validation.get("warnings"):
        notes.extend(str(warning) for warning in validation["warnings"])
    multiqc_specs = [
        (
            "fastqc_multiqc_localhost",
            "FastQC MultiQC Localhost URL",
            reachable_localhost_url_for_path("fastqc/multiqc/multiqc_report.html"),
            "fastqc/multiqc/multiqc_report.html",
            "Live localhost URL for the full FastQC MultiQC report when the run directory is already being served.",
            "localhost_app",
        ),
        (
            "fastqc_multiqc_helper",
            "FastQC MultiQC Browser Helper",
            "fastqc/multiqc/multiqc_browser_helper.html",
            "fastqc/multiqc/multiqc_browser_helper.html",
            "Browser-safe review page for the FastQC MultiQC report.",
            "html_report",
        ),
        (
            "salmon_multiqc_localhost",
            "Salmon MultiQC Localhost URL",
            reachable_localhost_url_for_path("rnaseq_salmon/multiqc/multiqc_report.html"),
            "rnaseq_salmon/multiqc/multiqc_report.html",
            "Live localhost URL for the full Salmon MultiQC report when the run directory is already being served.",
            "localhost_app",
        ),
        (
            "salmon_multiqc_helper",
            "Salmon MultiQC Browser Helper",
            "rnaseq_salmon/multiqc/multiqc_browser_helper.html",
            "rnaseq_salmon/multiqc/multiqc_browser_helper.html",
            "Browser-safe review page for the Salmon MultiQC report.",
            "html_report",
        ),
    ]
    for artifact_id, title, entry_path, source_rel_path, description, kind in multiqc_specs:
        source_path = run_dir / source_rel_path
        available = bool(entry_path) if kind == "localhost_app" else source_path.exists()
        entries.append(
            artifact_entry(
                artifact_id=artifact_id,
                title=title,
                path=entry_path if available else None,
                kind=kind,
                status="created" if available else "not_available",
                description=description,
            )
        )
    for artifact_id, title, rel_path, description in [
        (
            "sample_table",
            "Resolved Sample Table",
            "rnaseq_salmon/matrices/samples.tsv",
            "Grouped samples with layout, strandedness, and row provenance.",
        ),
        (
            "tpm_matrix",
            "TPM Matrix",
            "rnaseq_salmon/matrices/tpm.tsv",
            "Transcript-by-sample TPM matrix from Salmon quantification.",
        ),
        (
            "num_reads_matrix",
            "Num Reads Matrix",
            "rnaseq_salmon/matrices/num_reads.tsv",
            "Transcript-by-sample expected fragment counts.",
        ),
        (
            "effective_length_matrix",
            "Effective Length Matrix",
            "rnaseq_salmon/matrices/effective_length.tsv",
            "Transcript-by-sample effective lengths.",
        ),
        (
            "gene_num_reads_matrix",
            "Gene Num Reads Matrix",
            "rnaseq_salmon/matrices/gene_num_reads.tsv",
            "Gene-by-sample expected counts aggregated from Salmon transcripts.",
        ),
        (
            "gene_tpm_matrix",
            "Gene TPM Matrix",
            "rnaseq_salmon/matrices/gene_tpm.tsv",
            "Gene-by-sample TPM values aggregated from Salmon transcripts.",
        ),
        (
            "tx2gene_map",
            "Transcript-to-Gene Map",
            "rnaseq_salmon/matrices/tx2gene.tsv",
            "tx2gene provenance derived from the provided GTF.",
        ),
        (
            "qc_verdict",
            "QC Verdict",
            "qc/qc_verdict.json",
            "Compact pass/warn/fail summary over mapping rate, duplication, library-type agreement, and outliers.",
        ),
        (
            "normalized_samplesheet",
            "Normalized Sample Sheet",
            "validation/samplesheet.normalized.csv",
            "Resolved FASTQ paths and grouped sample layout.",
        ),
    ]:
        path = run_dir / rel_path
        entries.append(
            artifact_entry(
                artifact_id=artifact_id,
                title=title,
                path=rel_path if path.exists() else None,
                kind="table",
                status="created" if path.exists() else "not_available",
                description=description,
            )
        )
    notebook_path = write_marimo_review_notebook(
        run_dir / "notebooks" / "bulk_rnaseq_counts_qc_review.marimo.py",
        title="Bulk RNA-seq Counts/QC Review",
        run_dir=run_dir,
        image_items=[],
        table_items=[
            ("Resolved Sample Table", "rnaseq_salmon/matrices/samples.tsv"),
            ("TPM Matrix", "rnaseq_salmon/matrices/tpm.tsv"),
            ("Num Reads Matrix", "rnaseq_salmon/matrices/num_reads.tsv"),
            ("Effective Length Matrix", "rnaseq_salmon/matrices/effective_length.tsv"),
        ],
        object_items=[
            ("FastQC MultiQC Browser Helper", "fastqc/multiqc/multiqc_browser_helper.html"),
            ("Salmon MultiQC Browser Helper", "rnaseq_salmon/multiqc/multiqc_browser_helper.html"),
            ("QC Verdict", "qc/qc_verdict.json"),
            ("Localhost Launch Hint", "visualizations/localhost_launch_hint.txt"),
        ],
    )
    entries.append(
        artifact_entry(
            artifact_id="counts_qc_review_notebook",
            title="Counts/QC Review Notebook",
            path=notebook_path.relative_to(run_dir),
            kind="notebook",
            status="created",
            description="Marimo review notebook over the key counts/QC tables and report helpers.",
        )
    )
    launch_hint = write_localhost_launch_hint(
        run_dir,
        report_entries=[
            ("FastQC MultiQC", "fastqc/multiqc/multiqc_report.html"),
            ("Salmon MultiQC", "rnaseq_salmon/multiqc/multiqc_report.html"),
        ],
    )
    entries.append(
        artifact_entry(
            artifact_id="localhost_launch_hint",
            title="Localhost Launch Hint",
            path=launch_hint.relative_to(run_dir),
            kind="text",
            status="created",
            description="Command and URLs for serving the run directory over localhost and opening browser-safe report helpers.",
        )
    )
    entries.extend(ngs_resource_gate.resource_visual_entries(resource_plan))
    index = write_visualization_index(
        run_dir,
        title="Bulk RNA-seq Counts/QC Review Bundle",
        description="Human-readable review surface for the counts/QC lane, with links to the key reports and matrices.",
        entries=entries,
        notes=[*notes, *ngs_resource_gate.resource_messages(resource_plan)],
    )
    return {
        "visualization_index": str(index.relative_to(run_dir)),
        "visualization_manifest": "visualizations/visualization_manifest.json",
        "review_notebook": str(notebook_path.relative_to(run_dir)),
        "localhost_launch_hint": str(launch_hint.relative_to(run_dir)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-sheet", type=Path, required=True)
    parser.add_argument("--transcriptome-fasta", type=Path, required=True)
    parser.add_argument("--genome-fasta", type=Path)
    parser.add_argument("--annotation-gtf", type=Path)
    parser.add_argument(
        "--fastq-root",
        type=Path,
        action="append",
        default=[],
        help="Directory to search by FASTQ basename.",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        help="Run directory. Defaults to ngs_runs/bulk_rnaseq_counts_qc/<timestamp>.",
    )
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--run-id", default=slug_timestamp("bulk-rnaseq-counts-qc"))
    parser.add_argument("--kmer", type=int, default=31)
    parser.add_argument(
        "--genome-build",
        help="Genome build or registry alias for resource readiness, e.g. GRCh38, mm39, or a configured local alias.",
    )
    parser.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Resource bundle override formatted as bundle=/path. May be repeated.",
    )
    parser.add_argument("--include-optional-resources", action="store_true")
    parser.add_argument("--resource-checksums", action="store_true")
    parser.add_argument(
        "--require-resource-plan",
        action="store_true",
        help="Treat missing registered reference bundles as blocking for this local runner.",
    )
    parser.add_argument(
        "--skip-resource-plan",
        action="store_true",
        help="Skip registered reference bundle readiness checks.",
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--no-dry-run", action="store_true")
    parser.add_argument("--quick-validation", action="store_true")
    parser.add_argument("--fastq-record-check", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    yaml_module = load_yaml_module()
    if yaml_module is None:
        yaml_status = yaml_dependency_status()
        write_json(run_dir / "validation" / "tool_preflight.json", yaml_status)
        write_text(
            run_dir / "summary.md",
            "Python dependency preflight failed: PyYAML is required to write config.yaml.\n",
        )
        write_standard_manifest(
            run_dir,
            run_id=args.run_id,
            lane="bulk_rnaseq_counts_qc",
            workflow="local_light_snakemake_salmon",
            status="blocked",
            execute_requested=args.execute,
            validation={"ok": True, "errors": [], "warnings": []},
            tool_preflight_result=yaml_status,
            dry_run={"ok": False, "detail": "Python dependency preflight failed"},
            execution={"ok": False, "detail": "execution not attempted"},
            inputs={},
            outputs={
                "summary": "summary.md",
                "tool_preflight": "validation/tool_preflight.json",
            },
            method={"quantifier": "salmon"},
        )
        write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))
        print(run_dir)
        return 1

    sample_sheet = args.sample_sheet.expanduser().resolve()
    fastq_roots = [root.expanduser().resolve() for root in args.fastq_root]
    fastq_roots.extend([sample_sheet.parent, Path.cwd()])
    if not sample_sheet.exists():
        raise FileNotFoundError(f"sample sheet does not exist: {sample_sheet}")

    validation, normalized_rows, config_parts = read_samplesheet(
        sample_sheet, fastq_roots, args.quick_validation, args.fastq_record_check
    )
    reference_validation = validate_references(args)
    combined_validation = {
        "ok": validation["ok"] and reference_validation["ok"],
        "sample_sheet": str(sample_sheet),
        "errors": validation.get("errors", []) + reference_validation.get("errors", []),
        "warnings": validation.get("warnings", []) + reference_validation.get("warnings", []),
        "sample_count": validation.get("sample_count", 0),
        "fastq_checks": validation.get("fastq_checks", []),
        "reference_validation": reference_validation,
    }
    resource_plan = ngs_resource_gate.write_pipeline_resource_plan(
        run_dir=run_dir,
        pipeline="bulk_rnaseq_counts_qc",
        genome_build=args.genome_build,
        bundle_roots=args.bundle_root,
        include_optional=args.include_optional_resources,
        include_checksums=args.resource_checksums,
        skip=args.skip_resource_plan,
        required=args.require_resource_plan,
    )
    combined_validation = ngs_resource_gate.merge_resource_status(
        combined_validation,
        resource_plan,
        required=args.require_resource_plan,
    )
    tool_status = tool_preflight(["snakemake", "fastqc", "multiqc", "salmon"], optional=[])

    config = {
        "threads": args.threads,
        "references": reference_validation["references"],
        "salmon": {"kmer": args.kmer},
        **config_parts,
    }
    write_json(run_dir / "config.json", config)
    write_text(run_dir / "config.yaml", yaml_module.safe_dump(config, sort_keys=True))
    write_normalized_samplesheet(
        run_dir / "validation" / "samplesheet.normalized.csv", normalized_rows
    )
    write_json(
        run_dir / "validation" / "input_summary.json",
        {"sample_sheet": str(sample_sheet), **config_parts},
    )
    write_json(run_dir / "validation" / "validation_summary.json", combined_validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_workflow(run_dir)
    write_commands(run_dir, args.threads)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions(
            {
                "snakemake": ["snakemake", "--version"],
                "fastqc": ["fastqc", "--version"],
                "multiqc": ["multiqc", "--version"],
                "salmon": ["salmon", "--no-version-check", "--version"],
            }
        ),
    )

    dry_run: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    blocked = not combined_validation["ok"] or not tool_status["ok"]
    status = "blocked" if blocked else "prepared"
    if not blocked and not args.no_dry_run:
        dry_run = run_cmd(snakemake_cmd(run_dir, args.threads, dry_run=True), run_dir, timeout=600)
        write_json(run_dir / "logs" / "snakemake_dry_run.json", dry_run)
        write_text(run_dir / "logs" / "snakemake_dry_run.log", dry_run.get("stdout_tail", ""))
        if not dry_run.get("ok"):
            blocked = True
            status = "failed"
    elif not blocked:
        write_json(
            run_dir / "logs" / "snakemake_dry_run_skipped.json",
            {"ok": True, "reason": "--no-dry-run was requested"},
        )
    if args.execute and not blocked:
        execution = run_cmd(
            snakemake_cmd(run_dir, args.threads, dry_run=False), run_dir, timeout=86400
        )
        write_json(run_dir / "logs" / "snakemake_execute.json", execution)
        write_text(run_dir / "logs" / "snakemake_execute.log", execution.get("stdout_tail", ""))
        status = "completed" if execution.get("ok") else "failed"
    elif not args.execute and status == "prepared":
        status = "validated"

    write_multiqc_browser_helper(
        run_dir,
        report_path="fastqc/multiqc/multiqc_report.html",
        title="FastQC MultiQC Browser Helper",
    )
    write_multiqc_browser_helper(
        run_dir,
        report_path="rnaseq_salmon/multiqc/multiqc_report.html",
        title="Salmon MultiQC Browser Helper",
    )
    qc_verdict = (
        compute_qc_verdict(run_dir, config)
        if args.execute and status == "completed"
        else {
            "overall_status": "not_available",
            "thresholds": QC_THRESHOLDS,
            "outlier_samples": [],
            "samples": [],
            "de_readiness": {
                "status": "not_available",
                "reason": "Execution did not complete, so QC verdict and DE-readiness assessment were not computed.",
            },
        }
    )
    write_json(run_dir / "qc" / "qc_verdict.json", qc_verdict)
    review_bundle = generate_visualizations(run_dir, combined_validation, resource_plan)
    review_bundle.update(
        {
            "suggested_localhost_port": 8765,
            "localhost_report_examples": {
                "fastqc_report": reachable_localhost_url_for_path(
                    "fastqc/multiqc/multiqc_report.html"
                ),
                "salmon_report": reachable_localhost_url_for_path(
                    "rnaseq_salmon/multiqc/multiqc_report.html"
                ),
            },
        }
    )

    outputs = {
        "quant_glob": "rnaseq_salmon/quant/*/quant.sf",
        "tpm_matrix": "rnaseq_salmon/matrices/tpm.tsv",
        "num_reads_matrix": "rnaseq_salmon/matrices/num_reads.tsv",
        "effective_length_matrix": "rnaseq_salmon/matrices/effective_length.tsv",
        "gene_num_reads_matrix": "rnaseq_salmon/matrices/gene_num_reads.tsv",
        "gene_tpm_matrix": "rnaseq_salmon/matrices/gene_tpm.tsv",
        "tx2gene_map": "rnaseq_salmon/matrices/tx2gene.tsv",
        "sample_table": "rnaseq_salmon/matrices/samples.tsv",
        "qc_verdict": "qc/qc_verdict.json",
        "fastq_multiqc_localhost": reachable_localhost_url_for_path(
            "fastqc/multiqc/multiqc_report.html"
        )
        if (run_dir / "fastqc/multiqc/multiqc_report.html").exists()
        else None,
        "fastq_multiqc_helper": "fastqc/multiqc/multiqc_browser_helper.html",
        "salmon_multiqc_localhost": reachable_localhost_url_for_path(
            "rnaseq_salmon/multiqc/multiqc_report.html"
        )
        if (run_dir / "rnaseq_salmon/multiqc/multiqc_report.html").exists()
        else None,
        "salmon_multiqc_helper": "rnaseq_salmon/multiqc/multiqc_browser_helper.html",
        "visualization_index": review_bundle["visualization_index"],
        "visualization_manifest": review_bundle["visualization_manifest"],
        "review_notebook": review_bundle["review_notebook"],
        "localhost_launch_hint": review_bundle["localhost_launch_hint"],
    }
    resource_outputs = ngs_resource_gate.resource_output_paths(resource_plan)
    outputs.update(resource_outputs)
    write_summary(run_dir, status, combined_validation, reference_validation, resource_plan)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="bulk_rnaseq_counts_qc",
        workflow="local_light_snakemake_salmon",
        status=status,
        execute_requested=args.execute,
        validation=combined_validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(sample_sheet),
            "references": reference_validation["references"],
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs=outputs,
        method={
            "quantifier": "salmon",
            "alignment": "transcriptome_pseudoalignment",
            "gene_level_counts": "salmon_tx_aggregation_with_tx2gene",
            "strandedness_policy": "respect_input_or_infer_when_unknown",
            "resource_plan": resource_plan,
        },
        audit={
            "qc_verdict_path": "qc/qc_verdict.json",
            **({"resource_readiness": resource_plan} if resource_plan else {}),
        },
        review_bundle=review_bundle,
    )
    write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))
    write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))

    print(run_dir)
    if status in {"blocked", "failed"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
