#!/usr/bin/env python3
"""Run FASTQ-based assay packages for epigenomics, amplicon, and metagenomics lanes."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import shlex
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional plotting dependencies
    plt = None
    np = None

from ngs_run_utils import (
    build_artifact_index,
    command_path,
    now_iso,
    run_cmd,
    sha256_file,
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
    write_multiqc_browser_helper,
    write_visualization_index,
)

WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "fastq_assay_package"
FASTQ_EXTENSIONS = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
LANES = {
    "epigenomics_peaks": {
        "display": "Epigenomics peaks/QC",
        "required": ["seqkit"],
        "optional": ["fastqc", "multiqc", "cutadapt", "macs2"],
    },
    "amplicon_microbiome": {
        "display": "Amplicon microbiome QC",
        "required": ["seqkit"],
        "optional": ["fastqc", "multiqc", "cutadapt"],
    },
    "shotgun_metagenomics": {
        "display": "Shotgun metagenomics QC",
        "required": ["seqkit"],
        "optional": ["fastqc", "multiqc", "kraken2", "bracken", "metaphlan", "humann"],
    },
}
LANE_THRESHOLDS = {
    "epigenomics_peaks": {
        "min_reads_for_qc": 1_000_000,
        "recommended_replicates": 2,
        "short_read_max_avg_len": 300,
        "expected_layout": "PE",
    },
    "amplicon_microbiome": {
        "min_reads_for_qc": 10_000,
        "recommended_replicates": 1,
        "short_read_max_avg_len": 350,
        "expected_layout": "PE_or_SE",
    },
    "shotgun_metagenomics": {
        "min_reads_for_qc": 1_000_000,
        "recommended_replicates": 1,
        "short_read_max_avg_len": 350,
        "expected_layout": "PE_or_SE",
    },
}
SYNTHETIC_MARKERS = ("synthetic", "simulated", "reduced")


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

    matches = []
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


def detect_delimiter(path: Path) -> str:
    if path.suffix.lower() in {".tsv", ".tab"}:
        return "\t"
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            first_line = handle.readline()
        if "\t" in first_line and "," not in first_line:
            return "\t"
    except OSError:
        pass
    return ","


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=detect_delimiter(path))
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
        return rows, list(reader.fieldnames or [])


def first_present(row: dict[str, str], names: list[str]) -> str:
    for name in names:
        if row.get(name):
            return row[name]
    return ""


def check_fastq(path: Path, max_records: int) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "records_checked": 0,
        "errors": [],
    }
    if not path.exists():
        result["errors"].append("file does not exist")
        return result
    if not path.name.endswith(FASTQ_EXTENSIONS):
        result["errors"].append("file extension is not a recognized FASTQ extension")
    try:
        with open_fastq_text(path) as handle:
            for index in range(max_records):
                header = handle.readline()
                if not header:
                    break
                sequence = handle.readline()
                plus = handle.readline()
                quality = handle.readline()
                if not quality:
                    result["errors"].append(f"incomplete FASTQ record after record {index}")
                    break
                result["records_checked"] += 1
                if not header.startswith("@"):
                    result["errors"].append(f"record {index + 1} header does not start with @")
                if not plus.startswith("+"):
                    result["errors"].append(f"record {index + 1} separator does not start with +")
                if len(sequence.rstrip()) != len(quality.rstrip()):
                    result["errors"].append(
                        f"record {index + 1} sequence and quality lengths differ"
                    )
    except OSError as exc:
        result["errors"].append(f"read failed: {exc}")
    return result


def truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "negative", "blank", "control"}


def summarize_input_context(args: argparse.Namespace, rows: list[dict[str, str]]) -> dict[str, Any]:
    assays = sorted({row.get("assay", "").strip() for row in rows if row.get("assay", "").strip()})
    platforms = sorted(
        {
            row.get("instrument_platform", "").strip()
            for row in rows
            if row.get("instrument_platform", "").strip()
        }
    )
    layouts = sorted(
        {row.get("layout", "").strip() for row in rows if row.get("layout", "").strip()}
    )
    host_present = any(row.get("host_organism", "").strip() for row in rows)
    host_depletion_present = any(row.get("host_depletion", "").strip() for row in rows)
    negative_controls_present = any(truthy(row.get("control", "")) for row in rows)
    control_metadata_present = any(row.get("control", "").strip() for row in rows)
    batches_present = any(row.get("batch", "").strip() for row in rows)
    replicate_metadata_present = any(row.get("replicate", "").strip() for row in rows)
    markers_present = sorted(
        {row.get("marker", "").strip() for row in rows if row.get("marker", "").strip()}
    )
    genome_build_present = any(row.get("genome_build", "").strip() for row in rows)
    blacklist_present = any(row.get("blacklist", "").strip() for row in rows)
    peak_type_present = any(row.get("peak_type", "").strip() for row in rows)
    primer_forward_present = any(row.get("primer_forward", "").strip() for row in rows)
    primer_reverse_present = any(row.get("primer_reverse", "").strip() for row in rows)
    primer_orientation_present = any(row.get("primer_orientation", "").strip() for row in rows)
    merge_strategy_present = any(row.get("merge_reads", "").strip() for row in rows)
    taxonomy_database_present = any(row.get("taxonomy_database", "").strip() for row in rows)
    taxonomy_database_version_present = any(
        row.get("taxonomy_database_version", "").strip() for row in rows
    )
    sample_metadata_present = any(row.get("sample_metadata", "").strip() for row in rows)
    return {
        "assays": assays,
        "instrument_platforms": platforms,
        "layouts": layouts,
        "host_organism_present": host_present,
        "host_depletion_present": host_depletion_present,
        "negative_controls_present": negative_controls_present,
        "control_metadata_present": control_metadata_present,
        "batch_metadata_present": batches_present,
        "replicate_metadata_present": replicate_metadata_present,
        "markers_present": markers_present,
        "genome_build_present": genome_build_present,
        "blacklist_present": blacklist_present,
        "peak_type_present": peak_type_present,
        "primer_forward_present": primer_forward_present,
        "primer_reverse_present": primer_reverse_present,
        "primer_sequences_present": primer_forward_present and primer_reverse_present,
        "primer_orientation_present": primer_orientation_present,
        "merge_strategy_present": merge_strategy_present,
        "taxonomy_database_present": taxonomy_database_present,
        "taxonomy_database_version_present": taxonomy_database_version_present,
        "sample_metadata_present": sample_metadata_present,
        "mixed_layouts": len(layouts) > 1,
        "likely_short_read_platform": any(
            platform.upper().startswith("ILLUMINA") for platform in platforms
        ),
    }


def metadata_warnings(args: argparse.Namespace, rows: list[dict[str, str]]) -> list[str]:
    context = summarize_input_context(args, rows)
    warnings: list[str] = []
    if context["mixed_layouts"]:
        warnings.append(
            "Input sample sheet mixes SE and PE layouts; downstream comparisons should verify that this is intentional."
        )
    if args.lane == "shotgun_metagenomics":
        if not context["host_organism_present"]:
            warnings.append(
                "Host organism is not declared in the sample sheet, so host-depletion decisions and privacy review remain unresolved."
            )
        if not context["host_depletion_present"]:
            warnings.append(
                "Host-depletion intent is not declared in the sample sheet, so this run should be treated as readiness-only rather than analysis-ready."
            )
        if not context["negative_controls_present"]:
            warnings.append(
                "No negative controls are flagged in the sample sheet, which weakens contamination interpretation for metagenomics."
            )
    if args.lane == "epigenomics_peaks":
        if not any(row.get("replicate", "").strip() for row in rows):
            warnings.append(
                "Replicate metadata are missing, so peak-level statistical comparisons cannot be validated from the sample sheet alone."
            )
        if not context["host_organism_present"]:
            warnings.append(
                "Organism metadata are missing, so genome-build selection and blacklist choice are not yet audit-ready."
            )
        if not context["genome_build_present"]:
            warnings.append(
                "Genome build is missing from the sample sheet, so alignment, TSS enrichment, FRiP, and track generation remain metadata-blocked."
            )
        if not context["blacklist_present"]:
            warnings.append(
                "Blacklist BED/path is not declared, so blacklist-overlap QC and final peak filtering are not yet reproducible."
            )
        if not context["control_metadata_present"]:
            warnings.append(
                "Control/input pairing is not declared, so ChIP/CUT&RUN-style background handling remains ambiguous even though FASTQ QC can still run."
            )
        if not context["peak_type_present"]:
            warnings.append(
                "Peak type is not declared, so downstream peak-caller settings remain ambiguous."
            )
    if args.lane == "amplicon_microbiome" and not any(
        row.get("marker", "").strip() for row in rows
    ):
        warnings.append(
            "Amplicon marker/region is missing from the sample sheet, which weakens primer and taxonomy interpretation."
        )
    if args.lane == "amplicon_microbiome":
        if not context["primer_sequences_present"]:
            warnings.append(
                "Primer sequences are not declared in the sample sheet, so full ASV inference remains blocked even if read-level QC passes."
            )
        if not context["primer_orientation_present"]:
            warnings.append(
                "Primer orientation is not declared in the sample sheet, so trimming and read-merging settings remain ambiguous."
            )
        if (
            not context["taxonomy_database_present"]
            or not context["taxonomy_database_version_present"]
        ):
            warnings.append(
                "Taxonomy database and version are not fully declared in the sample sheet, so taxa-level interpretation is not yet audit-ready."
            )
        if not context["sample_metadata_present"]:
            warnings.append(
                "Sample metadata are not declared in the sample sheet, so diversity and differential-abundance interpretation would be incomplete."
            )
    return warnings


def normalize_samples(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[dict[str, str]], list[Path]]:
    sample_sheet = args.sample_sheet.expanduser().resolve()
    rows, columns = read_table(sample_sheet)
    roots = [root.expanduser().resolve() for root in args.fastq_root]
    roots.extend([sample_sheet.parent, Path.cwd()])
    normalized: list[dict[str, str]] = []
    fastq_paths: list[Path] = []
    errors: list[str] = []
    warnings: list[str] = []
    fastq_checks = []

    for row_index, row in enumerate(rows, start=2):
        sample = (
            first_present(row, ["sample", "sample_id", "sampleID", "run_accession"])
            or f"row_{row_index}"
        )
        r1_raw = first_present(row, ["fastq_1", "forwardReads", "r1", "read1"])
        r2_raw = first_present(row, ["fastq_2", "reverseReads", "r2", "read2"])
        fasta_raw = first_present(row, ["fasta"])
        if not r1_raw and not fasta_raw:
            errors.append(f"row {row_index}: fastq_1/forwardReads or fasta is required")
            continue
        r1 = resolve_existing_path(r1_raw, sample_sheet.parent, roots) if r1_raw else None
        r2 = resolve_existing_path(r2_raw, sample_sheet.parent, roots) if r2_raw else None
        fasta = resolve_existing_path(fasta_raw, sample_sheet.parent, roots) if fasta_raw else None
        if r1_raw and not r1:
            errors.append(f"row {row_index}: could not resolve read 1 path {r1_raw}")
        if r2_raw and not r2:
            errors.append(f"row {row_index}: could not resolve read 2 path {r2_raw}")
        if fasta_raw and not fasta:
            errors.append(f"row {row_index}: could not resolve fasta path {fasta_raw}")
        for read_label, read_path in [("r1", r1), ("r2", r2)]:
            if read_path is None:
                continue
            fastq_paths.append(read_path)
            check = check_fastq(read_path, args.fastq_record_check)
            check["sample"] = sample
            check["read"] = read_label
            fastq_checks.append(check)
            if check["errors"]:
                errors.extend(f"{sample} {read_label}: {error}" for error in check["errors"])
        normalized.append(
            {
                "sample": sample,
                "row_index": str(row_index),
                "fastq_1": str(r1) if r1 else "",
                "fastq_2": str(r2) if r2 else "",
                "fasta": str(fasta) if fasta else "",
                "layout": "PE" if r2 else ("SE" if r1 else "FASTA"),
                "marker": first_present(row, ["marker", "target", "region"]),
                "assay": first_present(row, ["assay", "library_strategy"]) or args.lane,
                "instrument_platform": first_present(row, ["instrument_platform", "platform"]),
                "host_organism": first_present(
                    row, ["host_organism", "host", "host_species", "organism"]
                ),
                "genome_build": first_present(
                    row, ["genome_build", "genome", "assembly", "reference", "reference_genome"]
                ),
                "blacklist": first_present(row, ["blacklist", "blacklist_bed", "blacklist_file"]),
                "peak_type": first_present(row, ["peak_type", "peak_style", "peak_calling_mode"]),
                "host_depletion": first_present(
                    row, ["host_depletion", "host_depletion_applied", "host_removal", "hostremoval"]
                ),
                "primer_forward": first_present(
                    row, ["primer_forward", "forward_primer", "fw_primer", "fwd_primer"]
                ),
                "primer_reverse": first_present(
                    row, ["primer_reverse", "reverse_primer", "rv_primer", "rev_primer"]
                ),
                "primer_orientation": first_present(row, ["primer_orientation", "orientation"]),
                "merge_reads": first_present(row, ["merge_reads", "read_merge", "merge_policy"]),
                "taxonomy_database": first_present(
                    row, ["taxonomy_database", "taxonomy_db", "classifier_db"]
                ),
                "taxonomy_database_version": first_present(
                    row,
                    ["taxonomy_database_version", "taxonomy_db_version", "classifier_db_version"],
                ),
                "sample_metadata": first_present(
                    row, ["sample_metadata", "metadata", "sample_metadata_file", "metadata_file"]
                ),
                "batch": first_present(row, ["batch", "batch_id"]),
                "replicate": first_present(row, ["replicate", "replicate_id"]),
                "control": first_present(row, ["control", "control_sample", "negative_control"]),
            }
        )
    if not normalized:
        errors.append("no usable rows found in sample sheet")
    warnings.extend(metadata_warnings(args, normalized))
    validation = {
        "ok": not errors,
        "lane": args.lane,
        "sample_sheet": str(sample_sheet),
        "columns": columns,
        "sample_count": len({row["sample"] for row in normalized}),
        "row_count": len(normalized),
        "fastq_count": len(fastq_paths),
        "errors": errors,
        "warnings": warnings,
        "fastq_checks": fastq_checks,
        "input_context": summarize_input_context(args, normalized),
    }
    return validation, normalized, fastq_paths


def write_normalized_samples(run_dir: Path, rows: list[dict[str, str]]) -> None:
    path = run_dir / "validation" / "samples.normalized.tsv"
    if not rows:
        write_text(path, "")
        return
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_resolved_sample_sheet(
    run_dir: Path, source_path: Path, rows: list[dict[str, str]]
) -> Path:
    destination = run_dir / "inputs" / "sample_sheet" / f"{source_path.stem}.resolved.tsv"
    if not rows:
        write_text(destination, "")
        return destination
    write_tsv(destination, rows, list(rows[0].keys()))
    return destination


def _supplemental_sample_name(
    sample_names: list[str], item_count: int, index: int, fallback: str
) -> str:
    if len(sample_names) == 1:
        return sample_names[0]
    if len(sample_names) == item_count and index < len(sample_names):
        return sample_names[index]
    return fallback


def _copy_input(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)
    return destination


def _rewrite_humann_headers(source: Path, destination: Path, sample_names: list[str]) -> Path:
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line and not line.startswith("#")), None
    )
    if header_index is None:
        return _copy_input(source, destination)
    header = lines[header_index].split("\t")
    provided = header[1:]
    if len(sample_names) == 1 and len(provided) == 1:
        header[1] = sample_names[0]
    elif len(sample_names) == len(provided):
        header[1:] = sample_names
    lines[header_index] = "\t".join(header)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def stage_analysis_inputs(
    run_dir: Path, args: argparse.Namespace, rows: list[dict[str, str]]
) -> dict[str, Any]:
    sample_names = [row["sample"] for row in rows if row.get("sample")]
    sample_sheet_path = args.sample_sheet.expanduser().resolve()
    sample_sheet_copy = _copy_input(
        sample_sheet_path, run_dir / "inputs" / "sample_sheet" / sample_sheet_path.name
    )
    resolved_sheet = write_resolved_sample_sheet(run_dir, sample_sheet_path, rows)
    provenance: dict[str, Any] = {
        "analysis_intent": "real_analysis",
        "sample_sheet": {
            "original_path": str(sample_sheet_path),
            "copied_path": str(sample_sheet_copy.relative_to(run_dir)),
            "resolved_path": str(resolved_sheet.relative_to(run_dir)),
            "sha256": sha256_file(sample_sheet_copy),
        },
        "supplemental_inputs": {
            "kraken_reports": [],
            "bracken_tables": [],
            "humann_pathabundance": None,
            "humann_genefamilies": None,
        },
    }

    staged_kraken: list[Path] = []
    for index, source in enumerate(args.kraken_report):
        source_path = source.expanduser().resolve()
        sample_name = _supplemental_sample_name(
            sample_names, len(args.kraken_report), index, sample_stem(source_path.name)
        )
        destination = _copy_input(
            source_path, run_dir / "inputs" / "kraken_reports" / f"{sample_name}.report.txt"
        )
        staged_kraken.append(destination)
        provenance["supplemental_inputs"]["kraken_reports"].append(
            {
                "original_path": str(source_path),
                "staged_path": str(destination.relative_to(run_dir)),
                "sha256": sha256_file(destination),
            }
        )
    args.kraken_report = staged_kraken

    staged_bracken: list[Path] = []
    for index, source in enumerate(args.bracken_table):
        source_path = source.expanduser().resolve()
        sample_name = _supplemental_sample_name(
            sample_names, len(args.bracken_table), index, sample_stem(source_path.name)
        )
        destination = _copy_input(
            source_path, run_dir / "inputs" / "bracken_tables" / f"{sample_name}.bracken.tsv"
        )
        staged_bracken.append(destination)
        provenance["supplemental_inputs"]["bracken_tables"].append(
            {
                "original_path": str(source_path),
                "staged_path": str(destination.relative_to(run_dir)),
                "sha256": sha256_file(destination),
            }
        )
    args.bracken_table = staged_bracken

    if args.humann_pathabundance:
        source_path = args.humann_pathabundance.expanduser().resolve()
        sample_name = _supplemental_sample_name(sample_names, 1, 0, sample_stem(source_path.name))
        destination = _rewrite_humann_headers(
            source_path,
            run_dir / "inputs" / "humann" / f"{sample_name}.pathabundance.tsv",
            sample_names,
        )
        args.humann_pathabundance = destination
        provenance["supplemental_inputs"]["humann_pathabundance"] = {
            "original_path": str(source_path),
            "staged_path": str(destination.relative_to(run_dir)),
            "sha256": sha256_file(destination),
        }

    if args.humann_genefamilies:
        source_path = args.humann_genefamilies.expanduser().resolve()
        sample_name = _supplemental_sample_name(sample_names, 1, 0, sample_stem(source_path.name))
        destination = _rewrite_humann_headers(
            source_path,
            run_dir / "inputs" / "humann" / f"{sample_name}.genefamilies.tsv",
            sample_names,
        )
        args.humann_genefamilies = destination
        provenance["supplemental_inputs"]["humann_genefamilies"] = {
            "original_path": str(source_path),
            "staged_path": str(destination.relative_to(run_dir)),
            "sha256": sha256_file(destination),
        }
    return provenance


def build_replay_command(args: argparse.Namespace, sample_sheet_path: Path) -> list[str]:
    command = [
        "python",
        str(Path(__file__).resolve()),
        "--lane",
        args.lane,
        "--sample-sheet",
        str(sample_sheet_path),
        "--threads",
        str(args.threads),
        "--fastq-record-check",
        str(args.fastq_record_check),
    ]
    if args.execute:
        command.append("--execute")
    if args.kraken_db:
        command.extend(["--kraken-db", str(args.kraken_db.expanduser().resolve())])
    if args.asv_table:
        command.extend(["--asv-table", str(args.asv_table.expanduser().resolve())])
    if args.taxonomy_table:
        command.extend(["--taxonomy-table", str(args.taxonomy_table.expanduser().resolve())])
    if args.synthetic_downstream_inputs:
        command.append("--synthetic-downstream-inputs")
    if args.allow_synthetic_diversity:
        command.append("--allow-synthetic-diversity")
    for path in args.kraken_report:
        command.extend(["--kraken-report", str(path)])
    for path in args.bracken_table:
        command.extend(["--bracken-table", str(path)])
    if args.humann_pathabundance:
        command.extend(["--humann-pathabundance", str(args.humann_pathabundance)])
    if args.humann_genefamilies:
        command.extend(["--humann-genefamilies", str(args.humann_genefamilies)])
    return command


def write_commands(
    run_dir: Path, args: argparse.Namespace, fastq_paths: list[Path], sample_sheet_path: Path
) -> None:
    lines = ["#!/usr/bin/env bash", "set -euo pipefail"]
    lines.append("# Full runner invocation for this bundle:")
    lines.append(f"# {shlex.join(build_replay_command(args, sample_sheet_path))}")
    if fastq_paths:
        lines.append(
            shlex.join(["seqkit", "stats", "-T", *map(str, fastq_paths)]) + " > qc/seqkit_stats.tsv"
        )
    if fastq_paths:
        lines.append(
            shlex.join(
                ["fastqc", "-t", str(args.threads), "-o", "fastqc/raw", *map(str, fastq_paths)]
            )
        )
        lines.append(
            shlex.join(["multiqc", "--no-version-check", "fastqc/raw", "-o", "fastqc/multiqc"])
        )
    write_text(run_dir / "commands.sh", "\n".join(lines) + "\n")


def parse_float(value: str) -> float:
    text = str(value).strip().replace(",", "")
    if not text or text in {"-", "NA", "nan"}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def path_has_synthetic_marker(path: Path | None) -> bool:
    if path is None:
        return False
    name = path.name.lower()
    return any(marker in name for marker in SYNTHETIC_MARKERS)


def fig_caption(fig: Any, caption: str | None) -> None:
    if caption:
        fig.text(0.99, 0.01, caption, ha="right", va="bottom", fontsize=8, color="#666666")


def read_seqkit_stats_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows, _ = read_table(path)
    parsed = []
    for row in rows:
        raw_file = row.get("file", "").strip()
        if not raw_file:
            continue
        file_path = Path(raw_file)
        if not file_path.exists():
            continue
        parsed.append(
            {
                "file": raw_file,
                "num_seqs": parse_float(row.get("num_seqs", "")),
                "sum_len": parse_float(row.get("sum_len", "")),
                "min_len": parse_float(row.get("min_len", "")),
                "avg_len": parse_float(row.get("avg_len", "")),
                "max_len": parse_float(row.get("max_len", "")),
            }
        )
    return parsed


def read_multiqc_table(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows, _ = read_table(path)
    return rows


def infer_read_technology(stats_rows: list[dict[str, Any]]) -> str:
    avg_len = max((float(row.get("avg_len", 0.0)) for row in stats_rows), default=0.0)
    max_len = max((float(row.get("max_len", 0.0)) for row in stats_rows), default=0.0)
    if avg_len >= 1000 or max_len >= 5000:
        return "long_read_like"
    if avg_len >= 350 or max_len >= 1500:
        return "mixed_or_long_insert"
    return "short_read_like"


def sample_stem(text: str) -> str:
    name = Path(text).name
    for suffix in [".fastq.gz", ".fq.gz", ".fastq", ".fq", ".report.txt", ".report"]:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def summarize_fastqc_modules(multiqc_rows: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    excluded = {
        "Sample",
        "Filename",
        "File type",
        "Encoding",
        "Total Sequences",
        "Total Bases",
        "Sequences flagged as poor quality",
        "Sequence length",
        "%GC",
        "total_deduplicated_percentage",
        "avg_sequence_length",
        "median_sequence_length",
    }
    module_summary: dict[str, dict[str, int]] = {}
    for row in multiqc_rows:
        for column, value in row.items():
            if column in excluded:
                continue
            status = value.strip().lower()
            if status not in {"pass", "warn", "fail"}:
                continue
            counts = module_summary.setdefault(column, {"pass": 0, "warn": 0, "fail": 0})
            counts[status] += 1
    return dict(
        sorted(
            module_summary.items(), key=lambda item: (-item[1]["fail"], -item[1]["warn"], item[0])
        )
    )


def build_fastq_assay_qc_verdict(
    run_dir: Path, args: argparse.Namespace, validation: dict[str, Any]
) -> dict[str, Any]:
    context = validation.get("input_context", {})
    thresholds = LANE_THRESHOLDS[args.lane]
    seqkit_rows = read_seqkit_stats_file(run_dir / "qc" / "seqkit_stats.tsv")
    multiqc_rows = read_multiqc_table(
        run_dir / "fastqc" / "multiqc" / "multiqc_data" / "multiqc_fastqc.txt"
    )
    general_stats_rows = read_multiqc_table(
        run_dir / "fastqc" / "multiqc" / "multiqc_data" / "multiqc_general_stats.txt"
    )
    module_summary = summarize_fastqc_modules(multiqc_rows)
    warnings: list[str] = list(validation.get("warnings", []))
    reason_codes: list[str] = []
    recommendations: list[str] = []
    per_sample: list[dict[str, Any]] = []

    technology = infer_read_technology(seqkit_rows)
    sample_count = int(validation.get("sample_count", 0) or 0)
    replicate_count = sample_count if context.get("replicate_metadata_present") else 0

    # Collect per-sample metrics and heuristic flags.
    min_reads_observed = None
    max_percent_fails = 0.0
    for row in seqkit_rows:
        file_key = sample_stem(str(row.get("file", "")))
        sample_fastqc = next(
            (item for item in multiqc_rows if sample_stem(item.get("Filename", "")) == file_key), {}
        )
        sample_general = next(
            (
                item
                for item in general_stats_rows
                if sample_stem(item.get("Sample", "")) == file_key
            ),
            {},
        )
        num_seqs = int(row.get("num_seqs", 0) or 0)
        min_reads_observed = (
            num_seqs if min_reads_observed is None else min(min_reads_observed, num_seqs)
        )
        percent_fails = parse_float(sample_general.get("fastqc-percent_fails", ""))
        max_percent_fails = max(max_percent_fails, percent_fails)
        per_sample.append(
            {
                "file": file_key,
                "num_reads": num_seqs,
                "avg_read_length": float(row.get("avg_len", 0.0) or 0.0),
                "max_read_length": float(row.get("max_len", 0.0) or 0.0),
                "fastqc_percent_fails": percent_fails,
                "fastqc_duplication_percent": parse_float(
                    sample_general.get("fastqc-percent_duplicates", "")
                ),
            }
        )

    if min_reads_observed is not None and min_reads_observed < thresholds["min_reads_for_qc"]:
        reason_codes.append("read_depth_below_recommended_minimum")
        recommendations.append(
            f"Observed read depth is below the lane heuristic minimum of {thresholds['min_reads_for_qc']:,} reads; treat this run as QC/readiness rather than interpretation-ready."
        )
    if context.get("likely_short_read_platform") and technology != "short_read_like":
        reason_codes.append("platform_read_length_mismatch")
        warnings.append(
            "Read-length statistics do not match the declared short-read platform, so FastQC module pass/fail calls should be interpreted cautiously."
        )
        recommendations.append(
            "Confirm instrument metadata and, if needed, apply technology-specific QC rather than relying on short-read FastQC expectations."
        )
    if max_percent_fails >= 30.0:
        reason_codes.append("fastqc_failure_rate_high")
        recommendations.append(
            "Inspect the highest-failing FastQC modules before advancing to downstream interpretation; a high module fail rate should block interpretation until reviewed."
        )

    if args.lane == "epigenomics_peaks":
        per_base_fail_count = module_summary.get("per_base_sequence_content", {}).get("fail", 0)
        adapter_fail_count = module_summary.get("adapter_content", {}).get("fail", 0)
        max_duplication = max(
            (sample.get("fastqc_duplication_percent", 0.0) for sample in per_sample), default=0.0
        )
        if any(layout != "PE" for layout in context.get("layouts", [])):
            reason_codes.append("paired_end_layout_expected")
            recommendations.append(
                "ATAC/epigenomics inputs are usually paired-end for robust fragment metrics; confirm that SE layout is intentional."
            )
        if sample_count < thresholds["recommended_replicates"]:
            reason_codes.append("replicate_count_below_recommended_minimum")
            recommendations.append(
                "Provide at least two biological replicates before using this plugin surface to justify peak-level statistical comparisons."
            )
        if not context.get("host_organism_present"):
            reason_codes.append("organism_metadata_missing")
            recommendations.append(
                "Add organism metadata so the downstream assay-specific workflow can pin the correct reference bundle and TSS annotation."
            )
        if not context.get("genome_build_present"):
            reason_codes.append("genome_build_missing")
            recommendations.append(
                "Record the genome build in the sample sheet before aligning reads or generating tracks, FRiP, and TSS enrichment metrics."
            )
        if not context.get("blacklist_present"):
            reason_codes.append("blacklist_missing")
            recommendations.append(
                "Provide a blacklist BED path before treating blacklist overlap and final peaks as reproducible."
            )
        if not context.get("control_metadata_present"):
            reason_codes.append("control_metadata_missing")
            recommendations.append(
                "Declare control/input metadata so background-aware peak calling is auditable for ChIP, CUT&RUN, or CUT&Tag studies."
            )
        if not context.get("peak_type_present"):
            reason_codes.append("peak_type_missing")
            recommendations.append(
                "Declare whether downstream peaks are narrow, broad, or accessibility-style to keep peak-caller parameters explicit."
            )
        if command_path("macs2") is None:
            reason_codes.append("peak_caller_backend_missing")
            recommendations.append(
                "Install MACS2 or run a full nf-core backend before expecting peak-calling outputs from this lane."
            )
        if per_base_fail_count:
            warnings.append(
                "FastQC flagged per-base sequence content; for ATAC/CUT&RUN/CUT&Tag libraries this can be assay-expected and should not be treated as an automatic trimming failure."
            )
        if adapter_fail_count:
            warnings.append(
                "FastQC flagged adapter content; confirm trimming policy before alignment, but do not infer failed peak calling from this flag alone."
            )
        if max_duplication >= 25.0:
            warnings.append(
                f"Duplicate estimates reach {max_duplication:.1f}% in the current MultiQC summary. For epigenomics libraries this is not necessarily fatal, but library complexity should be reassessed after alignment with mitochondrial fraction, FRiP, and TSS enrichment."
            )
        recommendations.append(
            "Compute mitochondrial fraction, insert-size periodicity, TSS enrichment, FRiP, blacklist overlap, and replicate concordance after alignment before making biological claims."
        )
    elif args.lane == "amplicon_microbiome":
        if not context.get("markers_present"):
            reason_codes.append("marker_metadata_missing")
            recommendations.append(
                "Declare the marker region and primer pair in the sample sheet so trimming and taxonomy interpretation are auditable."
            )
        if not context.get("primer_sequences_present"):
            reason_codes.append("primer_sequences_missing")
            recommendations.append(
                "Provide forward and reverse primer sequences before treating this lane as a full amplicon analysis rather than QC/readiness."
            )
        if not context.get("primer_orientation_present"):
            reason_codes.append("primer_orientation_missing")
            recommendations.append(
                "Declare primer orientation so trimming and merging settings are reproducible."
            )
        if not context.get("taxonomy_database_present"):
            reason_codes.append("taxonomy_database_missing")
            recommendations.append(
                "Choose a taxonomy database before expecting taxa-level plots or assignments."
            )
        if not context.get("taxonomy_database_version_present"):
            reason_codes.append("taxonomy_database_version_missing")
            recommendations.append(
                "Record the taxonomy database version so taxa-level interpretation is audit-ready."
            )
        if not context.get("sample_metadata_present"):
            reason_codes.append("sample_metadata_missing")
            recommendations.append(
                "Provide sample metadata before treating diversity or differential-abundance outputs as interpretable."
            )
        if command_path("cutadapt") is None:
            reason_codes.append("primer_trimming_backend_missing")
            recommendations.append(
                "Install cutadapt before treating this lane as primer-trimming-ready."
            )
        reason_codes.append("taxonomy_backend_required")
        recommendations.append(
            "Provide an ASV table and taxonomy resource or a QIIME2/DADA2 backend before treating the run as analysis-complete."
        )
    elif args.lane == "shotgun_metagenomics":
        classification_status = {}
        status_path = run_dir / "taxonomic_classification_status.json"
        if status_path.exists():
            classification_status = json.loads(status_path.read_text(encoding="utf-8"))
        if not context.get("host_organism_present"):
            reason_codes.append("host_metadata_missing")
            recommendations.append(
                "Add host organism and host-depletion intent to the sample sheet before treating metagenomics outputs as interpretation-ready."
            )
        if not context.get("negative_controls_present"):
            reason_codes.append("negative_controls_not_flagged")
            recommendations.append(
                "Flag negative controls explicitly in the sample sheet to make contamination interpretation auditable."
            )
        if not classification_status.get("executed"):
            reason_codes.append("classification_backend_not_executed")
            recommendations.append(
                "Provide a Kraken2 database or precomputed Kraken/Bracken/HUMAnN tables to emit taxonomic/functional interpretation artifacts."
            )

    verdict = "pass_with_caveats" if not reason_codes else "analysis_not_ready"
    readiness = {
        "epigenomics_peaks": "ready_for_alignment_handoff"
        if verdict == "pass_with_caveats"
        else "readiness_only",
        "amplicon_microbiome": "ready_for_primer_trimming_handoff"
        if verdict == "pass_with_caveats"
        else "readiness_only",
        "shotgun_metagenomics": "ready_for_taxonomic_profiling"
        if verdict == "pass_with_caveats"
        else "readiness_only",
    }[args.lane]
    result = {
        "created_at": now_iso(),
        "lane": args.lane,
        "verdict": verdict,
        "analysis_readiness": readiness,
        "reason_codes": sorted(dict.fromkeys(reason_codes)),
        "warnings": list(dict.fromkeys(warnings)),
        "recommendations": list(dict.fromkeys(recommendations)),
        "thresholds": thresholds,
        "metadata_context": context,
        "technology_inference": technology,
        "fastqc_module_summary": module_summary,
        "metrics_summary": {
            "sample_count": sample_count,
            "replicate_count": replicate_count,
            "min_reads_observed": min_reads_observed,
            "max_fastqc_percent_fails": max_percent_fails,
        },
        "samples": per_sample,
    }
    if args.lane == "epigenomics_peaks":
        result["follow_on_commands"] = build_epigenomics_follow_on_commands(args, run_dir, context)
    if args.lane == "amplicon_microbiome":
        result["follow_on_commands"] = build_amplicon_follow_on_commands(args, run_dir)
    return result


def select_epigenomics_backend(context: dict[str, Any]) -> str:
    assay_text = " ".join(context.get("assays", [])).lower()
    if "atac" in assay_text:
        return "nf-core/atacseq"
    if (
        "cut&run" in assay_text
        or "cutrun" in assay_text
        or "cut&tag" in assay_text
        or "cuttag" in assay_text
    ):
        return "nf-core/cutandrun"
    if "chip" in assay_text:
        return "nf-core/chipseq"
    return "nf-core/atacseq"


def build_epigenomics_follow_on_commands(
    args: argparse.Namespace, run_dir: Path, context: dict[str, Any]
) -> list[dict[str, str]]:
    sample_sheet = str(args.sample_sheet.expanduser().resolve())
    backend = select_epigenomics_backend(context)
    backend_outdir = str((run_dir / "backend" / backend.replace("/", "_")).resolve())
    return [
        {
            "id": "epigenomics_backend_alignment_and_peaks",
            "description": "Run the assay-specific backend with explicit genome, blacklist, and control metadata to generate aligned BAMs, tracks, and peaks.",
            "command": (
                f"nextflow run {backend} "
                f"-profile docker --input {shlex.quote(sample_sheet)} "
                "--genome <GENOME_BUILD> --blacklist <BLACKLIST_BED> "
                f"--outdir {shlex.quote(backend_outdir)}"
            ),
        },
        {
            "id": "render_epigenomics_qc_after_alignment",
            "description": "Re-run the local lane after alignment/peak calling artifacts exist so the review bundle can include final readiness metrics and track links.",
            "command": (
                "python plugins/ngs-analysis/scripts/run_fastq_assay_package.py "
                f"--lane epigenomics_peaks --sample-sheet {shlex.quote(sample_sheet)} "
                "--execute"
            ),
        },
    ]


def build_epigenomics_readiness(
    run_dir: Path,
    args: argparse.Namespace,
    validation: dict[str, Any],
    interpretation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = validation.get("input_context", {})
    missing_metadata: list[str] = []
    if not context.get("host_organism_present"):
        missing_metadata.append("organism")
    if not context.get("genome_build_present"):
        missing_metadata.append("genome_build")
    if not context.get("blacklist_present"):
        missing_metadata.append("blacklist_bed")
    if not context.get("control_metadata_present"):
        missing_metadata.append("control_or_input")
    if not context.get("replicate_metadata_present"):
        missing_metadata.append("replicate_ids")
    if not context.get("peak_type_present"):
        missing_metadata.append("peak_type")

    alignment_missing = [
        field
        for field in missing_metadata
        if field in {"organism", "genome_build", "blacklist_bed"}
    ]
    peak_missing = [
        field
        for field in missing_metadata
        if field in {"control_or_input", "replicate_ids", "peak_type"}
    ]

    checklist = [
        {
            "id": "alignment",
            "status": "ready" if not alignment_missing else "missing_metadata",
            "requires_alignment": True,
            "required_inputs": ["FASTQs", "genome_build", "aligner", "blacklist_bed"],
            "missing_metadata": alignment_missing,
            "note": "Coordinate-sorted, filtered BAMs are the prerequisite for all downstream epigenomics metrics.",
        },
        {
            "id": "mitochondrial_fraction",
            "status": "requires_alignment",
            "requires_alignment": True,
            "required_inputs": ["filtered BAM", "genome_build"],
            "missing_metadata": alignment_missing,
            "note": "Mitochondrial fraction is measured on aligned reads and cannot be inferred from FASTQ QC alone.",
        },
        {
            "id": "fragment_periodicity",
            "status": "requires_alignment",
            "requires_alignment": True,
            "required_inputs": ["paired-end BAM"],
            "missing_metadata": [field for field in missing_metadata if field == "genome_build"],
            "note": "Insert-size periodicity is an alignment-derived ATAC-seq quality metric.",
        },
        {
            "id": "tss_enrichment",
            "status": "requires_alignment",
            "requires_alignment": True,
            "required_inputs": ["filtered BAM", "TSS annotation BED/GTF", "genome_build"],
            "missing_metadata": [
                field for field in missing_metadata if field in {"organism", "genome_build"}
            ],
            "note": "TSS enrichment depends on aligned read pileups around annotated TSS loci.",
        },
        {
            "id": "frip",
            "status": "requires_alignment_and_peaks",
            "requires_alignment": True,
            "required_inputs": ["filtered BAM", "called peaks"],
            "missing_metadata": peak_missing,
            "note": "FRiP is computed after peak calling and should be interpreted together with duplication and mitochondrial fraction.",
        },
        {
            "id": "blacklist_overlap",
            "status": "requires_alignment",
            "requires_alignment": True,
            "required_inputs": ["filtered BAM", "blacklist_bed"],
            "missing_metadata": [field for field in missing_metadata if field == "blacklist_bed"],
            "note": "Blacklist overlap requires the chosen genome build and blacklist resource.",
        },
        {
            "id": "peaks",
            "status": "requires_alignment_and_backend",
            "requires_alignment": True,
            "required_inputs": [
                "filtered BAM",
                "peak_caller",
                "peak_type",
                "controls (if applicable)",
            ],
            "missing_metadata": peak_missing,
            "note": "Peak calling needs aligned BAMs plus an explicit backend such as MACS2 or nf-core.",
        },
        {
            "id": "tracks",
            "status": "requires_alignment",
            "requires_alignment": True,
            "required_inputs": ["filtered BAM", "genome_sizes", "normalization choice"],
            "missing_metadata": [field for field in missing_metadata if field == "genome_build"],
            "note": "Browser tracks are derived from aligned reads and require explicit normalization settings.",
        },
    ]
    payload = {
        "schema_version": "2.0",
        "created_at": now_iso(),
        "lane": args.lane,
        "review_surface_ok": (
            run_dir / "fastqc" / "multiqc" / "multiqc_browser_helper.html"
        ).exists(),
        "ready_for_alignment_handoff": not alignment_missing,
        "macs2_present": command_path("macs2") is not None,
        "alignment_required": True,
        "missing_metadata": missing_metadata,
        "metadata_context": context,
        "checklist": checklist,
        "note": "This package validates and summarizes epigenomics FASTQs. Downstream TSS enrichment, FRiP, peaks, and tracks require aligned BAMs plus assay-specific metadata and backends.",
    }
    if interpretation:
        payload["verdict"] = interpretation.get("verdict")
        payload["analysis_readiness"] = interpretation.get("analysis_readiness")
        payload["reason_codes"] = interpretation.get("reason_codes", [])
        payload["recommendations"] = interpretation.get("recommendations", [])
        payload["follow_on_commands"] = interpretation.get("follow_on_commands", [])
    return payload


def build_amplicon_follow_on_commands(
    args: argparse.Namespace, run_dir: Path
) -> list[dict[str, str]]:
    sample_sheet = str(args.sample_sheet.expanduser().resolve())
    backend_outdir = str((run_dir / "backend" / "ampliseq").resolve())
    asv_table = str((run_dir / "backend" / "ampliseq" / "feature-table.tsv").resolve())
    taxonomy_table = str((run_dir / "backend" / "ampliseq" / "taxonomy.tsv").resolve())
    return [
        {
            "id": "nfcore_ampliseq_backend",
            "description": "Generate ASV and taxonomy tables from the same sample sheet once primer sequences, orientation, and taxonomy DB are chosen.",
            "command": (
                "nextflow run nf-core/ampliseq "
                f"-profile docker --input {shlex.quote(sample_sheet)} "
                "--FW_primer <FORWARD_PRIMER> --RV_primer <REVERSE_PRIMER> "
                "--database <TAXONOMY_DB> "
                f"--outdir {shlex.quote(backend_outdir)}"
            ),
        },
        {
            "id": "render_amplicon_visuals",
            "description": "Re-render plugin-native diversity and taxa plots after the backend emits ASV and taxonomy tables.",
            "command": (
                "python plugins/ngs-analysis/scripts/run_fastq_assay_package.py "
                f"--lane amplicon_microbiome --sample-sheet {shlex.quote(sample_sheet)} "
                f"--asv-table {shlex.quote(asv_table)} "
                f"--taxonomy-table {shlex.quote(taxonomy_table)} "
                "--execute"
            ),
        },
    ]


def build_shotgun_qc_interpretation(
    run_dir: Path, args: argparse.Namespace, validation: dict[str, Any]
) -> dict[str, Any]:
    context = validation.get("input_context", {})
    seqkit_rows = read_seqkit_stats_file(run_dir / "qc" / "seqkit_stats.tsv")
    multiqc_rows = read_multiqc_table(
        run_dir / "fastqc" / "multiqc" / "multiqc_data" / "multiqc_fastqc.txt"
    )
    general_stats_rows = read_multiqc_table(
        run_dir / "fastqc" / "multiqc" / "multiqc_data" / "multiqc_general_stats.txt"
    )
    classification_status = {}
    status_path = run_dir / "taxonomic_classification_status.json"
    if status_path.exists():
        classification_status = json.loads(status_path.read_text(encoding="utf-8"))

    technology = infer_read_technology(seqkit_rows)
    conclusions: list[str] = []
    warnings: list[str] = list(validation.get("warnings", []))
    recommendations: list[str] = []
    if not context.get("host_organism_present") or not context.get("host_depletion_present"):
        conclusions.append("host_depletion_context_missing")
        recommendations.append(
            "Add host organism and host-depletion intent/reference metadata before treating the run as analysis-ready."
        )
    if not classification_status.get("executed"):
        conclusions.append("classification_blocked")
        recommendations.append(
            "Provide Kraken/Bracken/HUMAnN inputs or a Kraken2 database before expecting taxonomic or functional interpretation artifacts."
        )
    if context.get("likely_short_read_platform") and technology != "short_read_like":
        conclusions.append("technology_mismatch")
        warnings.append(
            "Read-length statistics look long-read-like while the sample metadata declares a short-read platform; FastQC modules are less interpretable under this mismatch."
        )
        recommendations.append(
            "Confirm the sequencing platform and consider long-read-aware QC before relying on FastQC module pass/fail calls."
        )
    elif technology != "short_read_like":
        warnings.append(
            "Read lengths are long-read-like, so FastQC module pass/fail calls should be interpreted cautiously."
        )
        recommendations.append(
            "Supplement FastQC with technology-aware QC if this dataset is truly long-read or mixed-read."
        )

    percent_fails = max(
        (parse_float(row.get("fastqc-percent_fails", "")) for row in general_stats_rows),
        default=0.0,
    )
    if percent_fails >= 20.0:
        warnings.append(
            f"FastQC modules show a high fail rate ({percent_fails:.1f}%), which should be interpreted in the context of read length and platform."
        )

    readiness = "analysis_ready_for_taxonomic_profiling"
    if conclusions:
        readiness = "readiness_only"

    per_sample = []
    for row in seqkit_rows:
        name = Path(str(row.get("file", ""))).name
        sample_fastqc = next(
            (
                item
                for item in multiqc_rows
                if item.get("Filename", "").startswith(
                    name.replace(".fastq.gz", "").replace(".fq.gz", "")
                )
            ),
            {},
        )
        sample_general = next(
            (
                item
                for item in general_stats_rows
                if item.get("Sample", "").startswith(
                    name.replace(".fastq.gz", "").replace(".fq.gz", "")
                )
            ),
            {},
        )
        per_sample.append(
            {
                "file": name,
                "num_seqs": int(row.get("num_seqs", 0) or 0),
                "avg_len": float(row.get("avg_len", 0.0) or 0.0),
                "max_len": float(row.get("max_len", 0.0) or 0.0),
                "fastqc_percent_fails": parse_float(sample_general.get("fastqc-percent_fails", "")),
                "fastqc_sequence_length_distribution": sample_fastqc.get(
                    "sequence_length_distribution", ""
                ),
            }
        )
    return {
        "analysis_readiness": readiness,
        "conclusions": conclusions,
        "warnings": warnings,
        "recommendations": recommendations,
        "technology_inference": technology,
        "metadata_context": context,
        "classification_status": classification_status,
        "samples": per_sample,
    }


def save_barplot(
    labels: list[str],
    values: list[float],
    out_path: Path,
    *,
    title: str,
    ylabel: str,
    caption: str | None = None,
) -> bool:
    if plt is None or not labels:
        return False
    width = max(7, min(16, len(labels) * 0.65 + 3))
    fig, ax = plt.subplots(figsize=(width, 5.2))
    ax.bar(range(len(labels)), values, color="#3b6ea8")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig_caption(fig, caption)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return True


def save_stacked_barplot(
    samples: list[str],
    categories: list[str],
    values_by_category: dict[str, list[float]],
    out_path: Path,
    *,
    title: str,
    ylabel: str,
    caption: str | None = None,
) -> bool:
    if plt is None or np is None or not samples or not categories:
        return False
    width = max(8, min(18, len(samples) * 0.7 + 4))
    fig, ax = plt.subplots(figsize=(width, 5.8))
    bottom = np.zeros(len(samples))
    cmap = plt.get_cmap("tab20")
    for index, category in enumerate(categories):
        values = np.asarray(values_by_category.get(category, [0.0] * len(samples)), dtype=float)
        ax.bar(samples, values, bottom=bottom, label=category, color=cmap(index % 20))
        bottom = bottom + values
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig_caption(fig, caption)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return True


def save_heatmap(
    matrix: Any,
    row_labels: list[str],
    col_labels: list[str],
    out_path: Path,
    *,
    title: str,
    colorbar_label: str,
    caption: str | None = None,
) -> bool:
    if plt is None or np is None or not row_labels or not col_labels:
        return False
    data = np.asarray(matrix, dtype=float)
    height = max(5, min(18, len(row_labels) * 0.35 + 2))
    width = max(7, min(18, len(col_labels) * 0.55 + 4))
    fig, ax = plt.subplots(figsize=(width, height))
    image = ax.imshow(data, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, rotation=45, ha="right")
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels)
    ax.set_title(title)
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label(colorbar_label)
    fig_caption(fig, caption)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return True


def save_scatter(
    x_values: list[float],
    y_values: list[float],
    labels: list[str],
    out_path: Path,
    *,
    title: str,
    caption: str | None = None,
) -> bool:
    if plt is None or not labels:
        return False
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    ax.scatter(x_values, y_values, color="#4f7d4a", s=55)
    for label, x_value, y_value in zip(labels, x_values, y_values, strict=True):
        ax.text(x_value, y_value, label, fontsize=8, ha="left", va="bottom")
    ax.axhline(0, color="#ddd", linewidth=0.8)
    ax.axvline(0, color="#ddd", linewidth=0.8)
    ax.set_xlabel("PCoA1")
    ax.set_ylabel("PCoA2")
    ax.set_title(title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig_caption(fig, caption)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return True


def read_feature_count_table(path: Path) -> tuple[list[str], list[str], Any]:
    if np is None:
        raise RuntimeError("numpy is required for feature-table visualizations")
    rows, columns = read_table(path)
    if not rows or not columns:
        raise ValueError(f"feature table is empty: {path}")
    feature_col = columns[0]
    excluded = {feature_col, "taxonomy", "taxon", "confidence", "sequence"}
    sample_columns = [column for column in columns[1:] if column not in excluded]
    numeric_sample_columns = []
    for column in sample_columns:
        if any(parse_float(row.get(column, "")) > 0 for row in rows):
            numeric_sample_columns.append(column)
    if not numeric_sample_columns:
        raise ValueError(f"no numeric sample columns found in feature table: {path}")
    features = [row.get(feature_col, f"feature_{index}") for index, row in enumerate(rows, start=1)]
    matrix = np.asarray(
        [[parse_float(row.get(sample, "")) for sample in numeric_sample_columns] for row in rows],
        dtype=float,
    )
    return features, numeric_sample_columns, matrix


def read_asv_sample_columns(path: Path | None) -> list[str]:
    if path is None:
        return []
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        return []
    try:
        _, samples, _ = read_feature_count_table(resolved)
        return samples
    except Exception:
        return []


def shannon(counts: Any) -> float:
    if np is None:
        return 0.0
    total = float(np.asarray(counts, dtype=float).sum())
    if total <= 0:
        return 0.0
    proportions = np.asarray(counts, dtype=float) / total
    proportions = proportions[proportions > 0]
    return float(-(proportions * np.log(proportions)).sum())


def bray_curtis(sample_by_feature: Any) -> Any:
    if np is None:
        raise RuntimeError("numpy is required for beta-diversity visualizations")
    sample_by_feature = np.asarray(sample_by_feature, dtype=float)
    n_samples = sample_by_feature.shape[0]
    matrix = np.zeros((n_samples, n_samples), dtype=float)
    for i in range(n_samples):
        for j in range(n_samples):
            denominator = float(sample_by_feature[i].sum() + sample_by_feature[j].sum())
            matrix[i, j] = (
                0.0
                if denominator == 0
                else float(np.abs(sample_by_feature[i] - sample_by_feature[j]).sum() / denominator)
            )
    return matrix


def pcoa(distance_matrix: Any) -> tuple[Any, list[float]]:
    if np is None:
        raise RuntimeError("numpy is required for PCoA visualizations")
    distances = np.asarray(distance_matrix, dtype=float)
    n_samples = distances.shape[0]
    if n_samples < 2:
        return np.zeros((n_samples, 2)), [0.0, 0.0]
    centering = np.eye(n_samples) - np.ones((n_samples, n_samples)) / n_samples
    gram = -0.5 * centering @ (distances**2) @ centering
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    positive = np.maximum(eigenvalues[:2], 0.0)
    coords = eigenvectors[:, :2] * np.sqrt(positive)
    total_positive = float(np.maximum(eigenvalues, 0.0).sum())
    variance = [float(value / total_positive) if total_positive else 0.0 for value in positive]
    return coords, variance


def expected_rarefied_features(counts: Any, depth: int) -> float:
    counts = [int(value) for value in counts if int(value) > 0]
    total = sum(counts)
    if depth <= 0 or total <= 0:
        return 0.0
    depth = min(depth, total)

    def log_choose(n: int, k: int) -> float:
        if k < 0 or k > n:
            return float("-inf")
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

    denominator = log_choose(total, depth)
    expected = 0.0
    for count in counts:
        if total - count < depth:
            expected += 1.0
            continue
        missing_probability = math.exp(log_choose(total - count, depth) - denominator)
        expected += 1.0 - missing_probability
    return expected


def taxonomy_label(raw_taxonomy: str, rank: str) -> str:
    text = raw_taxonomy.strip()
    if not text:
        return "Unassigned"
    rank_prefix = {"phylum": "p__", "genus": "g__", "species": "s__"}.get(rank, "")
    parts = [part.strip() for part in text.replace("|", ";").split(";")]
    if rank_prefix:
        for part in parts:
            if part.lower().startswith(rank_prefix):
                label = part[len(rank_prefix) :].strip()
                return label or "Unassigned"
    rank_offsets = {"phylum": 1, "genus": 5, "species": 6}
    offset = rank_offsets.get(rank)
    if offset is not None and offset < len(parts):
        label = parts[offset].split("__")[-1].strip()
        return label or "Unassigned"
    return parts[-1].split("__")[-1].strip() or "Unassigned"


def read_taxonomy_map(path: Path, rank: str) -> dict[str, str]:
    rows, columns = read_table(path)
    if not rows or not columns:
        return {}
    feature_col = columns[0]
    taxonomy_col = next(
        (column for column in columns if column.lower() in {"taxonomy", "taxon", "lineage"}),
        columns[-1],
    )
    return {
        row.get(feature_col, ""): taxonomy_label(row.get(taxonomy_col, ""), rank) for row in rows
    }


def build_amplicon_downstream_context(
    args: argparse.Namespace,
    rows: list[dict[str, str]],
    asv_samples: list[str] | None = None,
) -> dict[str, Any]:
    real_samples = sorted(
        {row.get("sample", "").strip() for row in rows if row.get("sample", "").strip()}
    )
    asv_samples = [sample for sample in (asv_samples or []) if sample]
    extra_table_samples = sorted({sample for sample in asv_samples if sample not in real_samples})
    synthetic_reasons: list[str] = []
    if args.synthetic_downstream_inputs:
        synthetic_reasons.append("synthetic_downstream_inputs flag was supplied explicitly.")
    if path_has_synthetic_marker(args.asv_table.expanduser().resolve() if args.asv_table else None):
        synthetic_reasons.append("ASV table filename contains a synthetic or reduced-data marker.")
    if path_has_synthetic_marker(
        args.taxonomy_table.expanduser().resolve() if args.taxonomy_table else None
    ):
        synthetic_reasons.append(
            "Taxonomy table filename contains a synthetic or reduced-data marker."
        )
    if extra_table_samples:
        synthetic_reasons.append(
            "ASV table contains sample columns not present in the sample sheet: "
            + ", ".join(extra_table_samples)
        )
    synthetic_detected = bool(synthetic_reasons)
    beta_diversity_allowed = len(real_samples) >= 2 and not synthetic_detected
    return {
        "real_samples": real_samples,
        "real_sample_count": len(real_samples),
        "asv_samples": asv_samples,
        "asv_sample_count": len(asv_samples),
        "extra_table_samples": extra_table_samples,
        "synthetic_downstream_inputs": synthetic_detected,
        "synthetic_reasons": synthetic_reasons,
        "beta_diversity_allowed": beta_diversity_allowed,
        "review_only": synthetic_detected,
    }


def build_amplicon_methods_manifest(
    run_dir: Path,
    args: argparse.Namespace,
    rows: list[dict[str, str]],
    downstream_context: dict[str, Any],
) -> tuple[dict[str, Any], Path]:
    marker_values = sorted(
        {row.get("marker", "").strip() for row in rows if row.get("marker", "").strip()}
    )
    methods = {
        "created_at": now_iso(),
        "lane": args.lane,
        "marker_regions": marker_values,
        "sample_count": len(rows),
        "real_samples": downstream_context["real_samples"],
        "read_processing": {
            "merge_reads": args.merge_reads,
            "trunc_len_f": args.trunc_len_f,
            "trunc_len_r": args.trunc_len_r,
            "primer_forward": args.primer_forward,
            "primer_reverse": args.primer_reverse,
            "primer_orientation": args.primer_orientation,
            "denoiser": args.denoiser,
        },
        "normalization": {
            "strategy": args.normalization,
            "rarefaction_depth": args.rarefaction_depth,
        },
        "taxonomy": {
            "database": args.taxonomy_database,
            "database_version": args.taxonomy_database_version,
            "rank": args.taxonomy_rank,
        },
        "downstream_inputs": {
            "asv_table": str(args.asv_table.expanduser().resolve()) if args.asv_table else None,
            "taxonomy_table": str(args.taxonomy_table.expanduser().resolve())
            if args.taxonomy_table
            else None,
            "synthetic_detected": downstream_context["synthetic_downstream_inputs"],
            "synthetic_reasons": downstream_context["synthetic_reasons"],
            "beta_diversity_allowed": downstream_context["beta_diversity_allowed"],
        },
    }
    methods_path = run_dir / "methods" / "amplicon_methods.json"
    write_json(methods_path, methods)
    return methods, methods_path


def write_amplicon_backend_bundle(
    run_dir: Path,
    args: argparse.Namespace,
    methods_manifest_path: Path,
) -> dict[str, Any]:
    missing_required: list[str] = []
    if not args.primer_forward:
        missing_required.append("primer_forward")
    if not args.primer_reverse:
        missing_required.append("primer_reverse")
    if not args.taxonomy_database:
        missing_required.append("taxonomy_database")
    if not args.taxonomy_database_version:
        missing_required.append("taxonomy_database_version")
    backend_dir = run_dir / "workflow"
    backend_dir.mkdir(parents=True, exist_ok=True)
    result_dir = backend_dir / "ampliseq_results"
    command = [
        "nextflow",
        "run",
        "nf-core/ampliseq",
        "-profile",
        "docker",
        "--input",
        str(args.sample_sheet.expanduser().resolve()),
        "--outdir",
        str(result_dir),
    ]
    if args.primer_forward:
        command.extend(["--FW_primer", args.primer_forward])
    if args.primer_reverse:
        command.extend(["--RV_primer", args.primer_reverse])
    if args.trunc_len_f is not None:
        command.extend(["--trunclenf", str(args.trunc_len_f)])
    if args.trunc_len_r is not None:
        command.extend(["--trunclenr", str(args.trunc_len_r)])
    command_path_file = backend_dir / "amplicon_backend_command.sh"
    command_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "# Review the command below against your nf-core/ampliseq release before execution.",
        shlex.join(command),
    ]
    write_text(command_path_file, "\n".join(command_lines) + "\n")
    backend_status = {
        "created_at": now_iso(),
        "workflow": args.amplicon_backend,
        "ready_to_run": not missing_required,
        "missing_required_inputs": missing_required,
        "command_path": str(command_path_file.relative_to(run_dir)),
        "methods_manifest_path": str(methods_manifest_path.relative_to(run_dir)),
        "notes": [
            "This bundle captures a concrete backend handoff for real ASV/taxonomy generation.",
            "Review primer and truncation parameters against the target nf-core/ampliseq release before execution.",
        ],
    }
    write_json(backend_dir / "amplicon_backend_status.json", backend_status)
    write_json(
        backend_dir / "amplicon_backend_plan.json",
        {
            "workflow": args.amplicon_backend,
            "command": command,
            "missing_required_inputs": missing_required,
            "result_dir": str(result_dir.relative_to(run_dir)),
        },
    )
    return backend_status


def add_amplicon_visualizations(
    run_dir: Path,
    args: argparse.Namespace,
    entries: list[dict[str, Any]],
    notes: list[str],
    rows: list[dict[str, str]],
) -> None:
    if not args.asv_table:
        entries.append(
            artifact_entry(
                artifact_id="amplicon_diversity",
                title="Amplicon Diversity Plots",
                path=None,
                kind="plot_bundle",
                status="not_available",
                description="Provide --asv-table to generate alpha diversity, beta diversity, and rarefaction plots.",
            )
        )
        return
    asv_table = args.asv_table.expanduser().resolve()
    if not asv_table.exists():
        entries.append(
            artifact_entry(
                artifact_id="amplicon_diversity",
                title="Amplicon Diversity Plots",
                path=None,
                kind="plot_bundle",
                status="blocked",
                description=f"ASV table was requested but does not exist: {asv_table}",
            )
        )
        return

    try:
        features, samples, feature_by_sample = read_feature_count_table(asv_table)
    except Exception as exc:
        entries.append(
            artifact_entry(
                artifact_id="amplicon_diversity",
                title="Amplicon Diversity Plots",
                path=None,
                kind="plot_bundle",
                status="blocked",
                description=f"Could not parse ASV table: {exc}",
            )
        )
        return

    downstream_context = build_amplicon_downstream_context(args, rows, asv_samples=samples)
    if downstream_context["synthetic_downstream_inputs"]:
        notes.append(
            "Review-only downstream inputs were detected; generated amplicon tables and plots are for runner verification and should not be used for biological interpretation."
        )
        notes.extend(downstream_context["synthetic_reasons"])

    sample_by_feature = feature_by_sample.T
    review_caption = (
        "REVIEW ONLY - synthetic downstream inputs detected"
        if downstream_context["review_only"]
        else None
    )
    alpha_rows = []
    for sample, counts in zip(samples, sample_by_feature, strict=True):
        alpha_rows.append(
            {
                "sample": sample,
                "total_reads": int(counts.sum()),
                "observed_features": int((counts > 0).sum()),
                "shannon": f"{shannon(counts):.6g}",
            }
        )
    alpha_path = run_dir / "tables" / "alpha_diversity.tsv"
    write_tsv(alpha_path, alpha_rows, ["sample", "total_reads", "observed_features", "shannon"])
    entries.append(
        artifact_entry(
            artifact_id="alpha_diversity_table",
            title="Alpha Diversity Table",
            path=alpha_path.relative_to(run_dir),
            kind="table",
            status="created",
            description="Observed feature counts and Shannon diversity per sample.",
            source=str(asv_table),
        )
    )

    shannon_plot = run_dir / "visualizations" / "alpha_diversity_shannon.png"
    observed_plot = run_dir / "visualizations" / "alpha_diversity_observed_features.png"
    if save_barplot(
        samples,
        [parse_float(row["shannon"]) for row in alpha_rows],
        shannon_plot,
        title="Shannon Diversity",
        ylabel="Shannon index",
        caption=review_caption,
    ):
        entries.append(
            artifact_entry(
                artifact_id="alpha_shannon_plot",
                title="Alpha Diversity: Shannon",
                path=shannon_plot.relative_to(run_dir),
                kind="plot",
                status="created",
                description="Per-sample Shannon diversity from the provided ASV table.",
            )
        )
    if save_barplot(
        samples,
        [parse_float(row["observed_features"]) for row in alpha_rows],
        observed_plot,
        title="Observed Features",
        ylabel="Observed features",
        caption=review_caption,
    ):
        entries.append(
            artifact_entry(
                artifact_id="alpha_observed_plot",
                title="Alpha Diversity: Observed Features",
                path=observed_plot.relative_to(run_dir),
                kind="plot",
                status="created",
                description="Per-sample observed ASV/feature counts.",
            )
        )

    beta_diversity_allowed = (
        downstream_context["beta_diversity_allowed"] or args.allow_synthetic_diversity
    )
    if len(samples) >= 2 and beta_diversity_allowed:
        distance = bray_curtis(sample_by_feature)
        distance_rows = []
        for sample, values in zip(samples, distance, strict=True):
            row = {"sample": sample}
            row.update(
                {other: f"{float(value):.6g}" for other, value in zip(samples, values, strict=True)}
            )
            distance_rows.append(row)
        distance_path = run_dir / "tables" / "beta_bray_curtis_distance.tsv"
        write_tsv(distance_path, distance_rows, ["sample", *samples])
        coords, variance = pcoa(distance)
        pcoa_rows = [
            {"sample": sample, "PCoA1": f"{float(coord[0]):.6g}", "PCoA2": f"{float(coord[1]):.6g}"}
            for sample, coord in zip(samples, coords, strict=True)
        ]
        pcoa_path = run_dir / "tables" / "beta_pcoa.tsv"
        write_tsv(pcoa_path, pcoa_rows, ["sample", "PCoA1", "PCoA2"])
        pcoa_plot = run_dir / "visualizations" / "beta_diversity_pcoa_bray_curtis.png"
        if save_scatter(
            [float(row["PCoA1"]) for row in pcoa_rows],
            [float(row["PCoA2"]) for row in pcoa_rows],
            samples,
            pcoa_plot,
            title=f"Bray-Curtis PCoA ({variance[0]:.1%}, {variance[1]:.1%})",
            caption=review_caption,
        ):
            entries.append(
                artifact_entry(
                    artifact_id="beta_pcoa_plot",
                    title="Beta Diversity: Bray-Curtis PCoA",
                    path=pcoa_plot.relative_to(run_dir),
                    kind="plot",
                    status="created",
                    description="PCoA from Bray-Curtis distances computed from the provided ASV table.",
                )
            )
        entries.append(
            artifact_entry(
                artifact_id="beta_distance_table",
                title="Beta Diversity Distance Matrix",
                path=distance_path.relative_to(run_dir),
                kind="table",
                status="created",
                description="Bray-Curtis distance matrix.",
            )
        )
    elif len(samples) < 2:
        notes.append("Beta diversity PCoA requires at least two samples.")
    else:
        entries.append(
            artifact_entry(
                artifact_id="beta_pcoa_plot",
                title="Beta Diversity: Bray-Curtis PCoA",
                path=None,
                kind="plot",
                status="blocked",
                description="Beta-diversity and PCoA are blocked because downstream inputs are marked synthetic or review-only. Pass --allow-synthetic-diversity to override for visualization-only review runs.",
            )
        )
        notes.append(
            "Beta-diversity and PCoA were blocked because downstream inputs were marked synthetic or review-only. Pass --allow-synthetic-diversity to override for visualization-only review runs."
        )

    rarefaction_rows: list[dict[str, Any]] = []
    max_depth = int(max((counts.sum() for counts in sample_by_feature), default=0))
    if max_depth > 0:
        depths = sorted({max(1, int(max_depth * fraction / 10)) for fraction in range(1, 11)})
        for sample, counts in zip(samples, sample_by_feature, strict=True):
            for depth in depths:
                rarefaction_rows.append(
                    {
                        "sample": sample,
                        "depth": depth,
                        "expected_observed_features": f"{expected_rarefied_features(counts, depth):.6g}",
                    }
                )
    rarefaction_path = run_dir / "tables" / "rarefaction.tsv"
    write_tsv(rarefaction_path, rarefaction_rows, ["sample", "depth", "expected_observed_features"])
    if plt is not None and rarefaction_rows:
        fig, ax = plt.subplots(figsize=(7.8, 5.5))
        for sample in samples:
            sample_rows = [row for row in rarefaction_rows if row["sample"] == sample]
            ax.plot(
                [int(row["depth"]) for row in sample_rows],
                [float(row["expected_observed_features"]) for row in sample_rows],
                marker="o",
                label=sample,
            )
        ax.set_title("Rarefaction Curves")
        ax.set_xlabel("Subsampled reads")
        ax.set_ylabel("Expected observed features")
        ax.legend(frameon=False, fontsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig_caption(fig, review_caption)
        fig.tight_layout()
        rarefaction_plot = run_dir / "visualizations" / "rarefaction_curves.png"
        fig.savefig(rarefaction_plot, dpi=160)
        plt.close(fig)
        entries.append(
            artifact_entry(
                artifact_id="rarefaction_plot",
                title="Rarefaction Curves",
                path=rarefaction_plot.relative_to(run_dir),
                kind="plot",
                status="created",
                description="Expected observed features across subsampling depths.",
            )
        )

    if args.taxonomy_table:
        taxonomy_path = args.taxonomy_table.expanduser().resolve()
        taxonomy_map = (
            read_taxonomy_map(taxonomy_path, args.taxonomy_rank) if taxonomy_path.exists() else {}
        )
        if taxonomy_map:
            taxa = sorted({taxonomy_map.get(feature, "Unassigned") for feature in features})
            abundance = {sample: {taxon: 0.0 for taxon in taxa} for sample in samples}
            for feature, counts in zip(features, feature_by_sample, strict=True):
                taxon = taxonomy_map.get(feature, "Unassigned")
                for sample, count in zip(samples, counts, strict=True):
                    abundance[sample][taxon] += float(count)
            totals_by_taxon = {
                taxon: sum(abundance[sample][taxon] for sample in samples) for taxon in taxa
            }
            top_taxa = [
                taxon
                for taxon, _ in sorted(
                    totals_by_taxon.items(), key=lambda item: item[1], reverse=True
                )[: args.top_n_taxa]
            ]
            if len(taxa) > len(top_taxa):
                top_taxa.append("Other")
            rows = []
            values_by_taxon = {taxon: [] for taxon in top_taxa}
            for sample in samples:
                sample_total = sum(abundance[sample].values()) or 1.0
                other = 0.0
                for taxon in taxa:
                    value = abundance[sample][taxon] / sample_total
                    if taxon in values_by_taxon:
                        values_by_taxon[taxon].append(value)
                        rows.append(
                            {"sample": sample, "taxon": taxon, "relative_abundance": f"{value:.6g}"}
                        )
                    else:
                        other += value
                if "Other" in values_by_taxon:
                    values_by_taxon["Other"].append(other)
                    rows.append(
                        {"sample": sample, "taxon": "Other", "relative_abundance": f"{other:.6g}"}
                    )
            taxa_table = run_dir / "tables" / f"taxa_abundance_{args.taxonomy_rank}.tsv"
            write_tsv(taxa_table, rows, ["sample", "taxon", "relative_abundance"])
            taxa_plot = run_dir / "visualizations" / f"taxa_barplot_{args.taxonomy_rank}.png"
            if save_stacked_barplot(
                samples,
                top_taxa,
                values_by_taxon,
                taxa_plot,
                title=f"Taxa Barplot ({args.taxonomy_rank})",
                ylabel="Relative abundance",
                caption=review_caption,
            ):
                entries.append(
                    artifact_entry(
                        artifact_id="taxa_barplot",
                        title=f"Taxa Barplot ({args.taxonomy_rank})",
                        path=taxa_plot.relative_to(run_dir),
                        kind="plot",
                        status="created",
                        description="Stacked relative abundance by sample from the provided taxonomy table.",
                        source=str(taxonomy_path),
                    )
                )
        else:
            notes.append(
                "Taxonomy table was provided but could not be parsed into feature-to-taxon labels."
            )
    else:
        entries.append(
            artifact_entry(
                artifact_id="taxa_barplot",
                title="Taxa Barplot",
                path=None,
                kind="plot",
                status="not_available",
                description="Provide --taxonomy-table with --asv-table to generate taxa barplots.",
            )
        )


def parse_kraken_report(path: Path, rank_filter: set[str]) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.strip().split(maxsplit=5)
        if len(parts) < 6:
            continue
        percent, clade_reads, taxon_reads, rank, taxid, name = parts
        if rank_filter and rank not in rank_filter:
            continue
        rows.append(
            {
                "sample": path.name.replace(".report.txt", "").replace(".report", ""),
                "percent": parse_float(percent),
                "clade_reads": parse_float(clade_reads),
                "taxon_reads": parse_float(taxon_reads),
                "rank": rank,
                "taxid": taxid,
                "name": name.strip(),
            }
        )
    return rows


def read_bracken_table(path: Path) -> list[dict[str, Any]]:
    rows, columns = read_table(path)
    sample = path.name.replace(".bracken", "").replace(".tsv", "").replace(".txt", "")
    name_col = next(
        (column for column in columns if column.lower() in {"name", "taxonomy", "taxon"}),
        columns[0] if columns else "name",
    )
    reads_col = next(
        (
            column
            for column in columns
            if column.lower() in {"new_est_reads", "fraction_total_reads", "reads"}
        ),
        "",
    )
    fraction_col = next(
        (column for column in columns if column.lower() == "fraction_total_reads"), ""
    )
    parsed = []
    for row in rows:
        parsed.append(
            {
                "sample": sample,
                "name": row.get(name_col, ""),
                "reads": parse_float(row.get(reads_col, "")),
                "fraction": parse_float(row.get(fraction_col, "")) if fraction_col else 0.0,
            }
        )
    return parsed


def read_humann_table(path: Path) -> tuple[list[str], list[str], Any]:
    if np is None:
        raise RuntimeError("numpy is required for HUMAnN visualizations")
    lines = [
        line
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line and not line.startswith("#")
    ]
    if not lines:
        raise ValueError(f"HUMAnN table is empty: {path}")
    header = lines[0].split("\t")
    sample_names = header[1:]
    features = []
    values = []
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        features.append(parts[0])
        values.append([parse_float(value) for value in parts[1 : len(sample_names) + 1]])
    return features, sample_names, np.asarray(values, dtype=float)


def add_shotgun_visualizations(
    run_dir: Path, args: argparse.Namespace, entries: list[dict[str, Any]], notes: list[str]
) -> None:
    kraken_reports = [path.expanduser().resolve() for path in args.kraken_report]
    kraken_reports.extend(sorted((run_dir / "taxonomic_classification").glob("*.report.txt")))
    kraken_reports = [
        path
        for index, path in enumerate(kraken_reports)
        if path.exists() and path not in kraken_reports[:index]
    ]
    if kraken_reports:
        rank_filter = set(args.kraken_rank)
        kraken_rows = []
        for path in kraken_reports:
            kraken_rows.extend(parse_kraken_report(path, rank_filter))
        if kraken_rows:
            kraken_table = run_dir / "tables" / "kraken_top_taxa.tsv"
            top_rows = sorted(kraken_rows, key=lambda row: row["clade_reads"], reverse=True)[
                : args.top_n_taxa * max(1, len(kraken_reports))
            ]
            write_tsv(
                kraken_table,
                top_rows,
                ["sample", "percent", "clade_reads", "taxon_reads", "rank", "taxid", "name"],
            )
            samples = sorted({row["sample"] for row in top_rows})
            taxa = [
                taxon
                for taxon, _ in sorted(
                    {
                        row["name"]: sum(r["percent"] for r in top_rows if r["name"] == row["name"])
                        for row in top_rows
                    }.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )[: args.top_n_taxa]
            ]
            values_by_taxon = {taxon: [] for taxon in taxa}
            for sample in samples:
                total = sum(row["percent"] for row in top_rows if row["sample"] == sample) or 1.0
                for taxon in taxa:
                    values_by_taxon[taxon].append(
                        sum(
                            row["percent"]
                            for row in top_rows
                            if row["sample"] == sample and row["name"] == taxon
                        )
                        / total
                    )
            kraken_plot = run_dir / "visualizations" / "kraken_top_taxa_barplot.png"
            if save_stacked_barplot(
                samples,
                taxa,
                values_by_taxon,
                kraken_plot,
                title="Kraken Top Taxa",
                ylabel="Relative share of displayed taxa",
            ):
                entries.append(
                    artifact_entry(
                        artifact_id="kraken_top_taxa",
                        title="Kraken Top Taxa",
                        path=kraken_plot.relative_to(run_dir),
                        kind="plot",
                        status="created",
                        description="Stacked barplot from Kraken report files.",
                    )
                )
            entries.append(
                artifact_entry(
                    artifact_id="kraken_top_taxa_table",
                    title="Kraken Top Taxa Table",
                    path=kraken_table.relative_to(run_dir),
                    kind="table",
                    status="created",
                    description="Parsed top Kraken report rows.",
                )
            )
    else:
        entries.append(
            artifact_entry(
                artifact_id="kraken_top_taxa",
                title="Kraken Top Taxa",
                path=None,
                kind="plot",
                status="not_available",
                description="Provide --kraken-report or run Kraken2 with --kraken-db to generate taxonomic plots.",
            )
        )

    bracken_rows = []
    for path in [item.expanduser().resolve() for item in args.bracken_table]:
        if path.exists():
            bracken_rows.extend(read_bracken_table(path))
    if bracken_rows:
        bracken_table = run_dir / "tables" / "bracken_relative_abundance.tsv"
        write_tsv(bracken_table, bracken_rows, ["sample", "name", "reads", "fraction"])
        samples = sorted({row["sample"] for row in bracken_rows})
        top_taxa = [
            taxon
            for taxon, _ in sorted(
                {
                    row["name"]: sum(
                        r["fraction"] or r["reads"]
                        for r in bracken_rows
                        if r["name"] == row["name"]
                    )
                    for row in bracken_rows
                }.items(),
                key=lambda item: item[1],
                reverse=True,
            )[: args.top_n_taxa]
        ]
        matrix = []
        for taxon in top_taxa:
            matrix.append(
                [
                    sum(
                        row["fraction"] or row["reads"]
                        for row in bracken_rows
                        if row["sample"] == sample and row["name"] == taxon
                    )
                    for sample in samples
                ]
            )
        bracken_heatmap = run_dir / "visualizations" / "bracken_relative_abundance_heatmap.png"
        if save_heatmap(
            matrix,
            top_taxa,
            samples,
            bracken_heatmap,
            title="Bracken Relative Abundance",
            colorbar_label="Fraction or reads",
        ):
            entries.append(
                artifact_entry(
                    artifact_id="bracken_heatmap",
                    title="Bracken Relative Abundance Heatmap",
                    path=bracken_heatmap.relative_to(run_dir),
                    kind="plot",
                    status="created",
                    description="Top Bracken taxa across samples.",
                )
            )
    else:
        entries.append(
            artifact_entry(
                artifact_id="bracken_heatmap",
                title="Bracken Relative Abundance Heatmap",
                path=None,
                kind="plot",
                status="not_available",
                description="Provide --bracken-table to generate Bracken relative-abundance plots.",
            )
        )

    humann_inputs = [
        ("pathway", args.humann_pathabundance, "--humann-pathabundance"),
        ("gene_family", args.humann_genefamilies, "--humann-genefamilies"),
    ]
    for label, path, option_name in humann_inputs:
        if not path:
            entries.append(
                artifact_entry(
                    artifact_id=f"humann_{label}_heatmap",
                    title=f"HUMAnN {label.replace('_', ' ').title()} Heatmap",
                    path=None,
                    kind="plot",
                    status="not_available",
                    description=f"Provide {option_name} to generate this HUMAnN visual layer.",
                )
            )
            continue
        resolved = path.expanduser().resolve()
        if not resolved.exists():
            notes.append(f"HUMAnN {label} table was provided but does not exist: {resolved}")
            continue
        try:
            features, samples, matrix = read_humann_table(resolved)
        except Exception as exc:
            notes.append(f"Could not parse HUMAnN {label} table: {exc}")
            continue
        totals = matrix.sum(axis=1)
        order = list(np.argsort(totals)[::-1][: args.top_n_taxa]) if np is not None else []
        top_features = [features[index] for index in order]
        top_matrix = matrix[order, :] if np is not None and order else []
        table_rows = []
        for feature_index in order:
            row = {"feature": features[feature_index]}
            row.update(
                {
                    sample: f"{float(value):.6g}"
                    for sample, value in zip(samples, matrix[feature_index, :], strict=True)
                }
            )
            table_rows.append(row)
        humann_table = run_dir / "tables" / f"humann_{label}_top_features.tsv"
        write_tsv(humann_table, table_rows, ["feature", *samples])
        humann_heatmap = run_dir / "visualizations" / f"humann_{label}_heatmap.png"
        if save_heatmap(
            top_matrix,
            top_features,
            samples,
            humann_heatmap,
            title=f"HUMAnN {label.replace('_', ' ').title()}",
            colorbar_label="Abundance",
        ):
            entries.append(
                artifact_entry(
                    artifact_id=f"humann_{label}_heatmap",
                    title=f"HUMAnN {label.replace('_', ' ').title()} Heatmap",
                    path=humann_heatmap.relative_to(run_dir),
                    kind="plot",
                    status="created",
                    description=f"Top HUMAnN {label.replace('_', ' ')} features across samples.",
                    source=str(resolved),
                )
            )


def add_read_qc_visualizations(
    run_dir: Path, entries: list[dict[str, Any]], notes: list[str]
) -> None:
    seqkit_stats = run_dir / "qc" / "seqkit_stats.tsv"
    if not seqkit_stats.exists() or seqkit_stats.stat().st_size == 0:
        entries.append(
            artifact_entry(
                artifact_id="read_count_plot",
                title="Read Counts",
                path=None,
                kind="plot",
                status="not_available",
                description="Run with --execute and seqkit available to generate read-count plots.",
            )
        )
        return
    rows, columns = read_table(seqkit_stats)
    if not rows:
        notes.append("seqkit stats file exists but no rows could be parsed.")
        return
    file_col = "file" if "file" in columns else columns[0]
    count_col = (
        "num_seqs"
        if "num_seqs" in columns
        else next((column for column in columns if "seq" in column.lower()), "")
    )
    avg_len_col = (
        "avg_len"
        if "avg_len" in columns
        else next(
            (column for column in columns if "avg" in column.lower() and "len" in column.lower()),
            "",
        )
    )
    labels = [
        Path(row.get(file_col, f"read_{index}")).name for index, row in enumerate(rows, start=1)
    ]
    if count_col:
        count_plot = run_dir / "visualizations" / "read_counts.png"
        if save_barplot(
            labels,
            [parse_float(row.get(count_col, "")) for row in rows],
            count_plot,
            title="Read Counts",
            ylabel="Reads",
        ):
            entries.append(
                artifact_entry(
                    artifact_id="read_count_plot",
                    title="Read Counts",
                    path=count_plot.relative_to(run_dir),
                    kind="plot",
                    status="created",
                    description="Read counts parsed from seqkit stats.",
                )
            )
    if avg_len_col:
        length_plot = run_dir / "visualizations" / "average_read_lengths.png"
        if save_barplot(
            labels,
            [parse_float(row.get(avg_len_col, "")) for row in rows],
            length_plot,
            title="Average Read Lengths",
            ylabel="Bases",
        ):
            entries.append(
                artifact_entry(
                    artifact_id="average_read_length_plot",
                    title="Average Read Lengths",
                    path=length_plot.relative_to(run_dir),
                    kind="plot",
                    status="created",
                    description="Average read lengths parsed from seqkit stats.",
                )
            )


def generate_visualizations(
    run_dir: Path,
    args: argparse.Namespace,
    validation: dict[str, Any],
    rows: list[dict[str, str]],
    input_provenance: dict[str, Any],
    interpretation: dict[str, Any] | None = None,
) -> dict[str, str]:
    entries: list[dict[str, Any]] = []
    notes: list[str] = []
    (run_dir / "visualizations").mkdir(parents=True, exist_ok=True)
    (run_dir / "tables").mkdir(parents=True, exist_ok=True)
    multiqc_report_exists = (run_dir / "fastqc" / "multiqc" / "multiqc_report.html").exists()
    localhost_report = reachable_localhost_url_for_path("fastqc/multiqc/multiqc_report.html")
    multiqc_helper = write_multiqc_browser_helper(
        run_dir,
        report_path="fastqc/multiqc/multiqc_report.html",
        title="FastQC MultiQC Browser Helper",
    )
    launch_hint = write_localhost_launch_hint(
        run_dir,
        report_entries=[("FastQC MultiQC", "fastqc/multiqc/multiqc_report.html")],
    )

    entries.append(
        artifact_entry(
            artifact_id="multiqc_localhost",
            title="FastQC MultiQC Localhost URL",
            path=localhost_report if localhost_report else None,
            kind="localhost_app",
            status="created" if localhost_report else "not_available",
            description="Live review surface for the full interactive MultiQC report when the run directory is already being served over localhost.",
        )
    )
    entries.append(
        artifact_entry(
            artifact_id="multiqc_browser_helper",
            title="FastQC MultiQC Browser Helper",
            path=str(multiqc_helper.relative_to(run_dir)) if multiqc_helper else None,
            kind="html_report",
            status="created" if multiqc_helper else "not_available",
            description="Browser-safe MultiQC helper with embedded tables and localhost instructions for the full interactive report.",
        )
    )
    entries.append(
        artifact_entry(
            artifact_id="localhost_launch_hint",
            title="Localhost Launch Hint",
            path=str(launch_hint.relative_to(run_dir)),
            kind="text",
            status="created",
            description="Command and localhost URL for serving the run directory and opening the full MultiQC report.",
        )
    )
    entries.append(
        artifact_entry(
            artifact_id="qc_verdict",
            title="QC Verdict",
            path="qc_verdict.json" if (run_dir / "qc_verdict.json").exists() else None,
            kind="json",
            status="created" if (run_dir / "qc_verdict.json").exists() else "not_available",
            description="Machine-readable QC/readiness verdict with thresholds, reason codes, and next-step recommendations.",
        )
    )
    entries.append(
        artifact_entry(
            artifact_id="qc_interpretation",
            title="QC Interpretation",
            path="qc_interpretation.json"
            if (run_dir / "qc_interpretation.json").exists()
            else None,
            kind="json",
            status="created" if (run_dir / "qc_interpretation.json").exists() else "not_available",
            description="Lane-specific interpretation alias for user-facing review surfaces that expect a stable qc_interpretation.json path.",
        )
    )
    add_read_qc_visualizations(run_dir, entries, notes)
    if args.lane == "amplicon_microbiome":
        add_amplicon_visualizations(run_dir, args, entries, notes, rows)
    elif args.lane == "shotgun_metagenomics":
        add_shotgun_visualizations(run_dir, args, entries, notes)
    elif args.lane == "epigenomics_peaks":
        entries.append(
            artifact_entry(
                artifact_id="peak_calling_readiness",
                title="Peak Calling Readiness",
                path="peak_calling_readiness.json"
                if (run_dir / "peak_calling_readiness.json").exists()
                else None,
                kind="json",
                status="created"
                if (run_dir / "peak_calling_readiness.json").exists()
                else "not_available",
                description="FASTQ-stage readiness record for the alignment and peak-calling handoff.",
            )
        )
    if validation.get("warnings"):
        notes.extend(validation["warnings"])
    if validation.get("errors"):
        notes.extend(validation["errors"])
    if interpretation and interpretation.get("warnings"):
        notes.extend(interpretation["warnings"])
    notes = list(dict.fromkeys(notes))
    analysis_intent = "real_analysis"
    provenance_summary: dict[str, Any] = {
        "sample_sheet_resolved": input_provenance.get("sample_sheet", {}).get("resolved_path"),
        "supplemental_input_count": sum(
            len(value) if isinstance(value, list) else int(bool(value))
            for value in input_provenance.get("supplemental_inputs", {}).values()
        ),
    }
    if args.lane == "amplicon_microbiome":
        downstream_context = build_amplicon_downstream_context(
            args, rows, asv_samples=read_asv_sample_columns(args.asv_table)
        )
        provenance_summary.update(
            {
                "synthetic_downstream_inputs": downstream_context["synthetic_downstream_inputs"],
                "synthetic_reasons": downstream_context["synthetic_reasons"],
                "real_sample_count": downstream_context["real_sample_count"],
                "asv_sample_count": downstream_context["asv_sample_count"],
            }
        )
    if provenance_summary.get("supplemental_input_count"):
        notes.append(
            "Supplemental taxonomy/function inputs were copied under inputs/ and checksummed in run_manifest audit."
        )
    notes = list(dict.fromkeys(notes))
    index = write_visualization_index(
        run_dir,
        title=f"{LANES[args.lane]['display']} Visualizations",
        description="Native artifact bundle generated by the Life Sciences NGS Analysis plugin for Codex review and handoff.",
        entries=entries,
        notes=notes,
        analysis_intent=analysis_intent,
        provenance_summary=provenance_summary,
    )
    return {
        "visualization_index": str(index.relative_to(run_dir)),
        "visualization_manifest": "visualizations/visualization_manifest.json",
        "localhost_launch_hint": str(launch_hint.relative_to(run_dir)),
        "fastqc_multiqc_localhost": localhost_report if multiqc_report_exists else None,
    }


def execute_package(
    run_dir: Path,
    args: argparse.Namespace,
    fastq_paths: list[Path],
    tool_status: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    results: dict[str, Any] = {"ok": True, "steps": []}
    if not fastq_paths:
        return results
    (run_dir / "qc").mkdir(parents=True, exist_ok=True)

    seqkit = run_cmd(["seqkit", "stats", "-T", *map(str, fastq_paths)], run_dir, timeout=600)
    write_json(run_dir / "logs" / "seqkit_stats.json", seqkit)
    write_text(run_dir / "qc" / "seqkit_stats.tsv", seqkit.get("stdout_tail", ""))
    results["steps"].append({"name": "seqkit_stats", "ok": seqkit.get("ok")})
    results["ok"] = bool(results["ok"] and seqkit.get("ok"))

    if command_path("fastqc") and command_path("multiqc"):
        (run_dir / "fastqc" / "raw").mkdir(parents=True, exist_ok=True)
        fastqc = run_cmd(
            ["fastqc", "-t", str(args.threads), "-o", "fastqc/raw", *map(str, fastq_paths)],
            run_dir,
            timeout=3600,
        )
        write_json(run_dir / "logs" / "fastqc.json", fastqc)
        write_text(run_dir / "logs" / "fastqc.log", fastqc.get("stdout_tail", ""))
        multiqc = run_cmd(
            ["multiqc", "--no-version-check", "fastqc/raw", "-o", "fastqc/multiqc"],
            run_dir,
            timeout=600,
        )
        write_json(run_dir / "logs" / "multiqc.json", multiqc)
        write_text(run_dir / "logs" / "multiqc.log", multiqc.get("stdout_tail", ""))
        results["steps"].extend(
            [
                {"name": "fastqc", "ok": fastqc.get("ok")},
                {"name": "multiqc", "ok": multiqc.get("ok")},
            ]
        )
        results["ok"] = bool(results["ok"] and fastqc.get("ok") and multiqc.get("ok"))

    if args.lane == "shotgun_metagenomics":
        status = {
            "analysis_intent": "real_analysis",
            "requested_local_backend": bool(args.kraken_db),
            "executed": False,
            "reason": None,
            "supplemental_reports_present": bool(args.kraken_report),
        }
        if args.kraken_db and command_path("kraken2"):
            kraken_dir = run_dir / "taxonomic_classification"
            kraken_dir.mkdir(parents=True, exist_ok=True)
            for fastq in fastq_paths:
                out = (
                    kraken_dir
                    / f"{fastq.stem.replace('.fastq', '').replace('.fq', '')}.kraken2.txt"
                )
                report = (
                    kraken_dir / f"{fastq.stem.replace('.fastq', '').replace('.fq', '')}.report.txt"
                )
                kraken = run_cmd(
                    ["kraken2", "--db", str(args.kraken_db), "--report", str(report), str(fastq)],
                    run_dir,
                    timeout=3600,
                )
                write_text(out, kraken.get("stdout_tail", ""))
                status["executed"] = bool(status["executed"] or kraken.get("ok"))
        elif args.kraken_db:
            status["reason"] = "kraken2 is not installed"
        elif args.kraken_report:
            status["reason"] = (
                "local Kraken2 classification was not run; supplied Kraken reports were used for downstream visualization."
            )
        else:
            status["reason"] = "no Kraken2 database was provided"
        write_json(run_dir / "taxonomic_classification_status.json", status)

    if args.lane == "epigenomics_peaks":
        write_json(
            run_dir / "peak_calling_readiness.json",
            build_epigenomics_readiness(run_dir, args, validation),
        )
    if args.lane == "amplicon_microbiome":
        downstream_context = build_amplicon_downstream_context(args, [])
        write_json(
            run_dir / "amplicon_analysis_status.json",
            {
                "primer_trimming_ready": command_path("cutadapt") is not None,
                "taxonomy_backend_required": True,
                "synthetic_downstream_inputs_detected": downstream_context[
                    "synthetic_downstream_inputs"
                ],
                "beta_diversity_allowed": downstream_context["beta_diversity_allowed"]
                or args.allow_synthetic_diversity,
                "backend_status_path": "workflow/amplicon_backend_status.json",
                "note": "This package validates amplicon reads and summarizes read content; ASV/taxonomy assignment remains database/backend gated.",
            },
        )
    return results


def write_summary(
    run_dir: Path,
    args: argparse.Namespace,
    status: str,
    validation: dict[str, Any],
    interpretation: dict[str, Any] | None = None,
) -> None:
    lines = [
        f"# {LANES[args.lane]['display']} Run Summary",
        "",
        f"Status: `{status}`",
        f"Rows parsed: `{validation.get('row_count', 0)}`",
        f"FASTQs parsed: `{validation.get('fastq_count', 0)}`",
        "",
        "## Key Artifacts",
        "",
        "- `validation/samples.normalized.tsv`",
        "- `qc/seqkit_stats.tsv`",
        "- `visualizations/localhost_launch_hint.txt` for the preferred localhost MultiQC link",
        "- `fastqc/multiqc/multiqc_browser_helper.html` when FastQC/MultiQC execute",
        "- `visualizations/index.html` and `visualizations/visualization_manifest.json`",
        "- `methods/amplicon_methods.json` and `workflow/amplicon_backend_status.json` for amplicon provenance/handoff",
        "- `tables/` for optional ASV, taxonomy, Kraken, Bracken, or HUMAnN-derived summaries",
        "- lane-specific readiness/status JSON",
        "- `run_manifest.json` and `artifact_index.json`",
        "",
    ]
    if validation.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in validation["warnings"])
        lines.append("")
    if interpretation:
        lines.extend(["## Interpretation", ""])
        lines.append(f"- Verdict: `{interpretation.get('verdict', 'unknown')}`")
        lines.append(
            f"- Analysis readiness: `{interpretation.get('analysis_readiness', 'unknown')}`"
        )
        for reason in interpretation.get("reason_codes", []):
            lines.append(f"- Reason code: `{reason}`")
        for recommendation in interpretation.get("recommendations", []):
            lines.append(f"- Recommendation: {recommendation}")
        for follow_on in interpretation.get("follow_on_commands", []):
            lines.append(
                f"- Follow-on command ({follow_on.get('id', 'next')}): `{follow_on.get('command', '')}`"
            )
        lines.append("")
    if args.lane == "epigenomics_peaks":
        readiness_path = run_dir / "peak_calling_readiness.json"
        if readiness_path.exists():
            readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
            lines.extend(["## Epigenomics Readiness", ""])
            lines.append(f"- Review surface OK: `{readiness.get('review_surface_ok')}`")
            lines.append(
                f"- Alignment handoff ready: `{readiness.get('ready_for_alignment_handoff')}`"
            )
            for missing in readiness.get("missing_metadata", []):
                lines.append(f"- Missing metadata: `{missing}`")
            for item in readiness.get("checklist", []):
                lines.append(f"- {item.get('id')}: `{item.get('status')}`")
            lines.append("")
    methods_path = run_dir / "methods" / "amplicon_methods.json"
    if methods_path.exists():
        methods_payload = json.loads(methods_path.read_text(encoding="utf-8"))
        if methods_payload.get("downstream_inputs", {}).get("synthetic_detected"):
            lines.extend(["## Review Guardrail", ""])
            lines.append(
                "- Downstream ASV/taxonomy inputs were flagged as synthetic or review-only; diversity plots are emitted for runner verification, not biological interpretation."
            )
            lines.append("")
    if validation.get("errors"):
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {error}" for error in validation["errors"])
    write_text(run_dir / "summary.md", "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=sorted(LANES), required=True)
    parser.add_argument("--sample-sheet", type=Path, required=True)
    parser.add_argument("--fastq-root", type=Path, action="append", default=[])
    parser.add_argument("--kraken-db", type=Path)
    parser.add_argument(
        "--asv-table",
        type=Path,
        help="Optional amplicon feature/ASV count table for diversity visualizations.",
    )
    parser.add_argument(
        "--taxonomy-table", type=Path, help="Optional feature taxonomy table paired to --asv-table."
    )
    parser.add_argument("--taxonomy-rank", default="genus", choices=["phylum", "genus", "species"])
    parser.add_argument(
        "--synthetic-downstream-inputs",
        action="store_true",
        help="Mark ASV/taxonomy inputs as synthetic or review-only so downstream interpretation is blocked or labeled.",
    )
    parser.add_argument(
        "--allow-synthetic-diversity",
        dest="allow_synthetic_diversity",
        action="store_true",
        help="Allow beta-diversity/PCoA even when downstream inputs are synthetic or review-only.",
    )
    parser.add_argument(
        "--primer-forward",
        default=None,
        help="Forward primer sequence for backend handoff and methods manifest.",
    )
    parser.add_argument(
        "--primer-reverse",
        default=None,
        help="Reverse primer sequence for backend handoff and methods manifest.",
    )
    parser.add_argument(
        "--primer-orientation",
        default=None,
        help="Primer orientation for backend handoff and methods manifest.",
    )
    parser.add_argument(
        "--merge-reads",
        default="auto",
        choices=["auto", "yes", "no"],
        help="Read-merging policy recorded in the methods manifest.",
    )
    parser.add_argument(
        "--trunc-len-f",
        type=int,
        default=None,
        help="Forward read truncation length for backend handoff.",
    )
    parser.add_argument(
        "--trunc-len-r",
        type=int,
        default=None,
        help="Reverse read truncation length for backend handoff.",
    )
    parser.add_argument(
        "--denoiser",
        default="dada2",
        choices=["dada2", "qiime2-dada2", "deblur"],
        help="Denoiser recorded in the methods manifest.",
    )
    parser.add_argument(
        "--taxonomy-database",
        default=None,
        help="Taxonomy database name for methods manifest and backend handoff.",
    )
    parser.add_argument(
        "--taxonomy-database-version",
        default=None,
        help="Taxonomy database version for methods manifest and backend handoff.",
    )
    parser.add_argument(
        "--normalization",
        default="relative_abundance",
        choices=["relative_abundance", "rarefy", "none"],
        help="Normalization policy recorded in the methods manifest.",
    )
    parser.add_argument(
        "--rarefaction-depth",
        type=int,
        default=None,
        help="Rarefaction depth recorded in the methods manifest.",
    )
    parser.add_argument(
        "--amplicon-backend",
        default="nf-core/ampliseq",
        choices=["nf-core/ampliseq", "qiime2", "dada2"],
        help="Backend workflow captured in the amplicon handoff bundle.",
    )
    parser.add_argument(
        "--kraken-report",
        type=Path,
        action="append",
        default=[],
        help="Optional Kraken report file; may be repeated.",
    )
    parser.add_argument(
        "--kraken-rank",
        action="append",
        default=["S"],
        help="Kraken rank code to plot, e.g. S, G, P. May be repeated.",
    )
    parser.add_argument(
        "--bracken-table",
        type=Path,
        action="append",
        default=[],
        help="Optional Bracken abundance table; may be repeated.",
    )
    parser.add_argument(
        "--humann-pathabundance", type=Path, help="Optional HUMAnN pathabundance table."
    )
    parser.add_argument(
        "--humann-genefamilies", type=Path, help="Optional HUMAnN genefamilies table."
    )
    parser.add_argument(
        "--top-n-taxa",
        type=int,
        default=12,
        help="Maximum taxa/features shown in stacked bars and heatmaps.",
    )
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--fastq-record-check", type=int, default=200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_id = args.run_id or slug_timestamp(args.lane.replace("_", "-"))
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.lane / run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    validation, rows, fastq_paths = normalize_samples(args)
    input_provenance = stage_analysis_inputs(run_dir, args, rows)
    replay_sample_sheet = run_dir / input_provenance["sample_sheet"]["resolved_path"]
    tool_status = tool_preflight(
        LANES[args.lane]["required"], optional=LANES[args.lane]["optional"]
    )
    write_json(
        run_dir / "config.json",
        {
            "lane": args.lane,
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "resolved_sample_sheet": str(replay_sample_sheet),
            "kraken_db": str(args.kraken_db) if args.kraken_db else None,
            "asv_table": str(args.asv_table.expanduser().resolve()) if args.asv_table else None,
            "taxonomy_table": str(args.taxonomy_table.expanduser().resolve())
            if args.taxonomy_table
            else None,
            "synthetic_downstream_inputs": args.synthetic_downstream_inputs,
            "allow_synthetic_diversity": args.allow_synthetic_diversity,
            "primer_forward": args.primer_forward,
            "primer_reverse": args.primer_reverse,
            "primer_orientation": args.primer_orientation,
            "merge_reads": args.merge_reads,
            "trunc_len_f": args.trunc_len_f,
            "trunc_len_r": args.trunc_len_r,
            "denoiser": args.denoiser,
            "taxonomy_database": args.taxonomy_database,
            "taxonomy_database_version": args.taxonomy_database_version,
            "normalization": args.normalization,
            "rarefaction_depth": args.rarefaction_depth,
            "amplicon_backend": args.amplicon_backend,
            "kraken_reports": [str(path.expanduser().resolve()) for path in args.kraken_report],
            "bracken_tables": [str(path.expanduser().resolve()) for path in args.bracken_table],
            "humann_pathabundance": str(args.humann_pathabundance.expanduser().resolve())
            if args.humann_pathabundance
            else None,
            "humann_genefamilies": str(args.humann_genefamilies.expanduser().resolve())
            if args.humann_genefamilies
            else None,
        },
    )
    write_json(run_dir / "validation" / "input_summary.json", {"samples": rows})
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_normalized_samples(run_dir, rows)
    write_json(run_dir / "inputs" / "input_provenance.json", input_provenance)
    write_commands(run_dir, args, fastq_paths, replay_sample_sheet)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions(
            {
                "seqkit": ["seqkit", "version"],
                "fastqc": ["fastqc", "--version"],
                "multiqc": ["multiqc", "--version"],
                "cutadapt": ["cutadapt", "--version"],
                "macs2": ["macs2", "--version"],
                "kraken2": ["kraken2", "--version"],
            }
        ),
    )

    dry_run = {
        "ok": validation["ok"] and tool_status["ok"],
        "detail": "input and tool validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    execution = None
    interpretation: dict[str, Any] | None = None
    methods_manifest: dict[str, Any] | None = None
    methods_manifest_path: Path | None = None
    backend_status: dict[str, Any] | None = None
    if args.lane == "amplicon_microbiome":
        downstream_context = build_amplicon_downstream_context(
            args, rows, asv_samples=read_asv_sample_columns(args.asv_table)
        )
        methods_manifest, methods_manifest_path = build_amplicon_methods_manifest(
            run_dir, args, rows, downstream_context
        )
        backend_status = write_amplicon_backend_bundle(run_dir, args, methods_manifest_path)
    status = "blocked" if not dry_run["ok"] else "validated"
    if args.execute and dry_run["ok"]:
        execution = execute_package(run_dir, args, fastq_paths, tool_status, validation)
        status = "completed" if execution.get("ok") else "failed"
        if (
            args.lane == "amplicon_microbiome"
            and (run_dir / "amplicon_analysis_status.json").exists()
        ):
            status_payload = json.loads(
                (run_dir / "amplicon_analysis_status.json").read_text(encoding="utf-8")
            )
            status_payload.update(
                {
                    "synthetic_downstream_inputs_detected": bool(
                        methods_manifest
                        and methods_manifest.get("downstream_inputs", {}).get("synthetic_detected")
                    ),
                    "beta_diversity_allowed": bool(
                        methods_manifest
                        and methods_manifest.get("downstream_inputs", {}).get(
                            "beta_diversity_allowed"
                        )
                    )
                    or args.allow_synthetic_diversity,
                    "backend_ready_to_run": bool(
                        backend_status and backend_status.get("ready_to_run")
                    ),
                }
            )
            write_json(run_dir / "amplicon_analysis_status.json", status_payload)
        if execution.get("ok"):
            interpretation = build_fastq_assay_qc_verdict(run_dir, args, validation)
            write_json(run_dir / "qc_verdict.json", interpretation)
            if args.lane in {"shotgun_metagenomics", "amplicon_microbiome", "epigenomics_peaks"}:
                write_json(run_dir / "qc_interpretation.json", interpretation)
            if args.lane == "epigenomics_peaks":
                write_json(
                    run_dir / "peak_calling_readiness.json",
                    build_epigenomics_readiness(run_dir, args, validation, interpretation),
                )
            if args.lane == "amplicon_microbiome":
                status_payload = json.loads(
                    (run_dir / "amplicon_analysis_status.json").read_text(encoding="utf-8")
                )
                status_payload.update(
                    {
                        "analysis_readiness": interpretation.get("analysis_readiness"),
                        "verdict": interpretation.get("verdict"),
                        "missing_analysis_context": [
                            code
                            for code in interpretation.get("reason_codes", [])
                            if code.endswith("_missing")
                        ],
                        "follow_on_commands": interpretation.get("follow_on_commands", []),
                        "synthetic_downstream_inputs_detected": bool(
                            methods_manifest
                            and methods_manifest.get("downstream_inputs", {}).get(
                                "synthetic_detected"
                            )
                        ),
                        "beta_diversity_allowed": bool(
                            methods_manifest
                            and methods_manifest.get("downstream_inputs", {}).get(
                                "beta_diversity_allowed"
                            )
                        )
                        or args.allow_synthetic_diversity,
                        "backend_ready_to_run": bool(
                            backend_status and backend_status.get("ready_to_run")
                        ),
                    }
                )
                write_json(run_dir / "amplicon_analysis_status.json", status_payload)

    visualization_outputs = generate_visualizations(
        run_dir, args, validation, rows, input_provenance, interpretation
    )
    if args.lane == "epigenomics_peaks" and args.execute and dry_run["ok"]:
        write_json(
            run_dir / "peak_calling_readiness.json",
            build_epigenomics_readiness(run_dir, args, validation, interpretation),
        )
    review_bundle = {**visualization_outputs}
    outputs = {
        "sample_table": "validation/samples.normalized.tsv",
        "seqkit_stats": "qc/seqkit_stats.tsv",
        "fastqc_multiqc_helper": "fastqc/multiqc/multiqc_browser_helper.html",
        **visualization_outputs,
    }
    if methods_manifest_path:
        outputs["amplicon_methods_manifest"] = str(methods_manifest_path.relative_to(run_dir))
        outputs["amplicon_backend_status"] = "workflow/amplicon_backend_status.json"
        outputs["amplicon_backend_plan"] = "workflow/amplicon_backend_plan.json"
        outputs["amplicon_backend_command"] = "workflow/amplicon_backend_command.sh"
    if interpretation:
        outputs["qc_verdict"] = "qc_verdict.json"
        if args.lane in {"shotgun_metagenomics", "amplicon_microbiome", "epigenomics_peaks"}:
            outputs["qc_interpretation"] = "qc_interpretation.json"
        review_bundle["verdict"] = interpretation.get("verdict")
    helper_path = run_dir / outputs["fastqc_multiqc_helper"]
    review_bundle["review_surface_ok"] = helper_path.exists()
    review_bundle["preferred_review_surface"] = (
        outputs["fastqc_multiqc_localhost"]
        if helper_path.exists()
        else outputs.get("visualization_index")
    )
    write_standard_manifest(
        run_dir,
        run_id=run_id,
        lane=args.lane,
        analysis_intent="real_analysis",
        workflow="local_light_fastq_assay_package",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "resolved_sample_sheet": str(replay_sample_sheet),
            "input_provenance_path": "inputs/input_provenance.json",
            "kraken_reports": [str(path) for path in args.kraken_report],
            "bracken_tables": [str(path) for path in args.bracken_table],
            "humann_pathabundance": str(args.humann_pathabundance)
            if args.humann_pathabundance
            else None,
            "humann_genefamilies": str(args.humann_genefamilies)
            if args.humann_genefamilies
            else None,
        },
        outputs=outputs,
        method=methods_manifest
        if methods_manifest
        else {
            "package": LANES[args.lane]["display"],
            "taxonomy_database": args.taxonomy_database
            if args.lane == "amplicon_microbiome"
            else (str(args.kraken_db) if args.kraken_db else None),
        },
        audit={
            "resolved_executables": tool_status.get("checked", []),
            "software_versions_path": "versions/software_versions.json",
            "review_only": False,
            "backend_status": backend_status,
            "input_provenance_path": "inputs/input_provenance.json",
        },
        review_bundle=review_bundle,
    )
    write_summary(run_dir, args, status, validation, interpretation)
    write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))
    print(run_dir)
    return 1 if status in {"blocked", "failed"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
