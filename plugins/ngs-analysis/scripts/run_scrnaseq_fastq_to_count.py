#!/usr/bin/env python3
"""Run local scRNA FASTQ-to-count processing with validation, Snakemake execution, and artifacts."""

from __future__ import annotations

import argparse
import csv
import gzip
import importlib.util
import json
import platform
import re
import shlex
import shutil
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import ngs_resource_gate
from ngs_run_utils import (
    build_artifact_index,
    software_versions,
    write_standard_manifest,
    write_text,
)

SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = SCRIPT_PATH.parents[1]
WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "scrnaseq_fastq_to_count"
WORKFLOW_TEMPLATE = PLUGIN_ROOT / "workflows" / "scrnaseq_fastq_to_count" / "Snakefile.smk"
WORKFLOW_DIR = WORKFLOW_TEMPLATE.parent
DEFAULT_STAR_IMAGE = (
    "josousa/star@sha256:2683d370b9c91a2e497d776d9b0dff2ddcc01dfec5029103ffa66b2a8da7b0c2"
)
DEFAULT_STAR_IMAGE_TAG = "josousa/star:2.7.11b"
PINNED_SNAKEMAKE_VERSION = "9.19.0"
PINNED_STAR_VERSION = "2.7.11b"
SAMPLE_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
FASTQ_EXTENSIONS = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
READ_NAME_PREVIEW_LIMIT = 25


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slug_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S-scrnaseq-fastq-to-count")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def command_path(name: str) -> str | None:
    return shutil.which(name)


def module_present(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def shell_tool_command(name: str) -> str | None:
    resolved = command_path(name)
    if resolved:
        return name
    if name == "snakemake" and module_present("snakemake"):
        return f"{sys.executable} -m snakemake"
    return None


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


def resolve_path(value: str, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def is_remote_uri(value: str) -> bool:
    return value.startswith(("http://", "https://", "s3://", "gs://"))


def normalize_read_name(header: str) -> str:
    name = header.strip()
    if name.startswith("@"):
        name = name[1:]
    name = name.split()[0]
    if name.endswith(("/1", "/2")):
        name = name[:-2]
    return name


def open_fastq_text(path: Path):
    if path.name.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("rt", encoding="utf-8", errors="replace")


def fastq_stats(path: Path, pair_check_reads: int, quick: bool) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "readable": False,
        "gzip_ok": None,
        "record_count": None,
        "records_checked": 0,
        "first_read_names": [],
        "read_lengths_preview": [],
        "errors": [],
    }
    if not path.exists():
        stats["errors"].append("file does not exist")
        return stats
    if not path.is_file():
        stats["errors"].append("path is not a file")
        return stats
    if not path.name.endswith(FASTQ_EXTENSIONS):
        stats["errors"].append("file extension is not a recognized FASTQ extension")
    stats["readable"] = True

    try:
        record_count = 0
        with open_fastq_text(path) as handle:
            while True:
                header = handle.readline()
                if not header:
                    break
                sequence = handle.readline()
                plus = handle.readline()
                quality = handle.readline()
                if not quality:
                    stats["errors"].append(f"incomplete FASTQ record after record {record_count}")
                    break
                record_count += 1
                sequence_len = len(sequence.rstrip("\n\r"))
                if not header.startswith("@"):
                    stats["errors"].append(f"record {record_count} header does not start with @")
                if not plus.startswith("+"):
                    stats["errors"].append(f"record {record_count} separator does not start with +")
                if sequence_len != len(quality.rstrip("\n\r")):
                    stats["errors"].append(
                        f"record {record_count} sequence and quality lengths differ"
                    )
                if len(stats["first_read_names"]) < min(pair_check_reads, READ_NAME_PREVIEW_LIMIT):
                    stats["first_read_names"].append(normalize_read_name(header))
                if len(stats["read_lengths_preview"]) < pair_check_reads:
                    stats["read_lengths_preview"].append(sequence_len)
                if quick and record_count >= pair_check_reads:
                    break
        stats["record_count"] = None if quick else record_count
        stats["records_checked"] = record_count
        stats["gzip_ok"] = True if path.name.endswith(".gz") else None
        if stats["read_lengths_preview"]:
            stats["median_read_length"] = statistics.median(stats["read_lengths_preview"])
    except gzip.BadGzipFile:
        stats["gzip_ok"] = False
        stats["errors"].append("gzip stream is invalid")
    except OSError as exc:
        stats["errors"].append(f"read failed: {exc}")
    return stats


def parse_samples(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    samples: list[dict[str, Any]] = []
    if args.sample_sheet:
        sheet = Path(args.sample_sheet).expanduser().resolve()
        if not sheet.exists():
            return [], [f"sample sheet does not exist: {sheet}"]
        sample_counts: dict[str, int] = {}
        with sheet.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            legacy_mode = {"group", "replicate", "fastq_1", "fastq_2"}.issubset(columns)
            sample_col = "group" if legacy_mode else "sample" if "sample" in columns else None
            r1_col = "fastq_1" if "fastq_1" in columns else None
            r2_col = "fastq_2" if "fastq_2" in columns else None
            if not sample_col or not r1_col or not r2_col:
                return [], ["sample sheet must include group/sample and fastq_1/fastq_2 columns"]
            for index, row in enumerate(reader, start=2):
                sample = (row.get(sample_col) or "").strip()
                r1 = (row.get(r1_col) or "").strip()
                r2 = (row.get(r2_col) or "").strip()
                if not sample or not r1 or not r2:
                    errors.append(f"row {index}: group/sample, fastq_1, and fastq_2 are required")
                    continue
                if is_remote_uri(r1) or is_remote_uri(r2):
                    errors.append(
                        f"row {index}: remote FASTQ URLs are not supported by local execution; download or stage files first"
                    )
                    continue
                sample_counts[sample] = sample_counts.get(sample, 0) + 1
                unit = sample if sample_counts[sample] == 1 else f"{sample}__row{index}"
                samples.append(
                    {
                        "sample": unit,
                        "original_sample": sample,
                        "barcode_fastq": str(resolve_path(r1, sheet.parent)),
                        "cdna_fastq": str(resolve_path(r2, sheet.parent)),
                        "expected_cells": (row.get("expected_cells") or "").strip(),
                        "replicate": (row.get("replicate") or "").strip(),
                    }
                )
    elif args.barcode_fastq and args.cdna_fastq:
        sample = args.sample or Path(args.barcode_fastq).name.split(".")[0]
        samples.append(
            {
                "sample": sample,
                "original_sample": sample,
                "barcode_fastq": str(Path(args.barcode_fastq).expanduser().resolve()),
                "cdna_fastq": str(Path(args.cdna_fastq).expanduser().resolve()),
                "expected_cells": args.expected_cells or "",
                "replicate": "",
            }
        )
    else:
        errors.append("provide --sample-sheet or --barcode-fastq with --cdna-fastq")

    for sample in samples:
        if not SAMPLE_RE.match(sample["sample"]):
            errors.append(f"sample name {sample['sample']!r} must match {SAMPLE_RE.pattern}")
    return samples, errors


def validate_samples(
    samples: list[dict[str, Any]], pair_check_reads: int, quick: bool
) -> dict[str, Any]:
    sample_summaries = []
    errors: list[str] = []
    warnings: list[str] = []
    for sample in samples:
        barcode_stats = fastq_stats(Path(sample["barcode_fastq"]), pair_check_reads, quick)
        cdna_stats = fastq_stats(Path(sample["cdna_fastq"]), pair_check_reads, quick)
        pairing = {"checked": True, "mismatches": [], "record_count_match": None}
        barcode_names = barcode_stats.get("first_read_names", [])
        cdna_names = cdna_stats.get("first_read_names", [])
        for index, (barcode_name, cdna_name) in enumerate(zip(barcode_names, cdna_names), start=1):
            if barcode_name != cdna_name and len(pairing["mismatches"]) < 10:
                pairing["mismatches"].append(
                    {"record": index, "barcode": barcode_name, "cdna": cdna_name}
                )
        if pairing["mismatches"]:
            errors.append(f"{sample['sample']}: barcode and cDNA read names do not match")
        if (
            barcode_stats.get("record_count") is not None
            and cdna_stats.get("record_count") is not None
        ):
            pairing["record_count_match"] = (
                barcode_stats["record_count"] == cdna_stats["record_count"]
            )
            if not pairing["record_count_match"]:
                errors.append(f"{sample['sample']}: barcode and cDNA FASTQ record counts differ")
        else:
            warnings.append(
                f"{sample['sample']}: quick validation skipped full barcode/cDNA count parity"
            )
        for label, stats in [("barcode", barcode_stats), ("cdna", cdna_stats)]:
            for error in stats.get("errors", []):
                errors.append(f"{sample['sample']} {label}: {error}")
        barcode_len = barcode_stats.get("median_read_length")
        if barcode_len and barcode_len < 20:
            warnings.append(
                f"{sample['sample']}: barcode read length {barcode_len} is shorter than expected for 10x chemistry"
            )
        sample_summaries.append(
            {
                "sample": sample["sample"],
                "barcode_fastq": barcode_stats,
                "cdna_fastq": cdna_stats,
                "pairing": pairing,
                "expected_cells": sample.get("expected_cells", ""),
            }
        )
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "samples": sample_summaries,
        "quick_validation": quick,
        "pair_check_reads": pair_check_reads,
    }


def whitelist_stats(path: Path) -> dict[str, Any]:
    lengths: dict[int, int] = {}
    total = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            barcode = line.strip()
            if not barcode:
                continue
            total += 1
            lengths[len(barcode)] = lengths.get(len(barcode), 0) + 1
    return {
        "path": str(path),
        "count": total,
        "length_histogram": lengths,
        "dominant_length": max(lengths, key=lengths.get) if lengths else None,
    }


def chemistry_evidence(samples: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    read_lengths = []
    for sample in samples:
        stats = fastq_stats(Path(sample["barcode_fastq"]), args.pair_check_reads, quick=True)
        if stats.get("median_read_length"):
            read_lengths.append(float(stats["median_read_length"]))
    whitelist = whitelist_stats(Path(args.cb_whitelist).expanduser().resolve())
    dominant_whitelist_len = whitelist.get("dominant_length")
    observed_barcode_read_len = statistics.median(read_lengths) if read_lengths else None
    predicted = None
    confidence = "low"
    reasons: list[str] = []
    if (
        dominant_whitelist_len == 16
        and observed_barcode_read_len
        and observed_barcode_read_len >= 26
    ):
        predicted = "10x_v2"
        confidence = "high" if int(observed_barcode_read_len) == 26 else "medium"
        reasons.append(
            "Whitelist length is 16 and median barcode read length is consistent with 16bp CB + 10bp UMI."
        )
    elif dominant_whitelist_len == 16:
        predicted = "10x_like_16bp_cb"
        confidence = "medium"
        reasons.append(
            "Whitelist length suggests a 10x-style 16bp cell barcode, but barcode read length is not fully diagnostic."
        )
    else:
        reasons.append(
            "Whitelist length/read structure did not uniquely identify a known chemistry."
        )
    selected = args.chemistry
    compatible = selected == predicted if predicted else None
    if compatible:
        reasons.append("Selected chemistry matches the detected chemistry signature.")
    elif predicted and selected != predicted:
        reasons.append(
            "Selected chemistry does not match the detected chemistry signature; review override or barcode layout."
        )
    return {
        "selected": selected,
        "predicted": predicted,
        "compatible": compatible,
        "confidence": confidence,
        "observed_barcode_read_length_median": observed_barcode_read_len,
        "whitelist": whitelist,
        "reasons": reasons,
    }


def tool_preflight() -> dict[str, Any]:
    required = ["snakemake"]
    if platform.system() == "Darwin":
        required.append("docker")
    else:
        required.append("STAR")
    tools = {name: shell_tool_command(name) for name in required}
    missing = [name for name in required if not tools.get(name)]
    docker_daemon = None
    if "docker" in required and not missing:
        docker_probe = run_cmd(["docker", "info"], WORKSPACE_ROOT, timeout=30)
        docker_daemon = docker_probe.get("ok", False)
        if not docker_daemon:
            missing.append("docker_daemon")
    return {
        "created_at": now_iso(),
        "required": required,
        "tools": tools,
        "missing": missing,
        "docker_daemon": docker_daemon,
        "ok": not missing,
    }


def runtime_version_snapshot() -> dict[str, Any]:
    versions = software_versions(
        {
            "snakemake": ["snakemake", "--version"],
            "docker": ["docker", "version"],
            "star_native": ["STAR", "--version"],
        }
    )
    image_digest = None
    if command_path("docker"):
        inspect = run_cmd(
            [
                "docker",
                "image",
                "inspect",
                DEFAULT_STAR_IMAGE_TAG,
                "--format",
                "{{json .RepoDigests}}",
            ],
            WORKSPACE_ROOT,
            timeout=30,
        )
        if inspect.get("ok") and inspect.get("stdout_tail"):
            try:
                digests = json.loads(str(inspect["stdout_tail"]).splitlines()[-1].strip())
                image_digest = digests[0] if digests else None
            except json.JSONDecodeError:
                image_digest = None
    mismatches = []
    if versions.get("snakemake") and PINNED_SNAKEMAKE_VERSION not in versions["snakemake"]:
        mismatches.append(
            f"snakemake version differs from pinned version {PINNED_SNAKEMAKE_VERSION}"
        )
    if versions.get("star_native") and PINNED_STAR_VERSION not in versions["star_native"]:
        mismatches.append(f"STAR native version differs from pinned version {PINNED_STAR_VERSION}")
    if image_digest and image_digest != DEFAULT_STAR_IMAGE:
        mismatches.append("Docker STAR image digest differs from the pinned plugin default.")
    return {
        "software_versions": versions,
        "pinned_versions": {
            "snakemake": PINNED_SNAKEMAKE_VERSION,
            "star": PINNED_STAR_VERSION,
            "star_image": DEFAULT_STAR_IMAGE,
            "star_image_tag": DEFAULT_STAR_IMAGE_TAG,
        },
        "resolved_star_image_digest": image_digest,
        "mismatch_warnings": mismatches,
    }


def build_config(samples: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    star_runner = "docker" if platform.system() == "Darwin" else "native"
    chemistry = chemistry_evidence(samples, args)
    return {
        "samples": {
            sample["sample"]: {
                "original_sample": sample.get("original_sample", sample["sample"]),
                "barcode_fastq": sample["barcode_fastq"],
                "cdna_fastq": sample["cdna_fastq"],
                "expected_cells": sample.get("expected_cells", ""),
                "read_files_command": "zcat" if sample["barcode_fastq"].endswith(".gz") else "cat",
            }
            for sample in samples
        },
        "threads": args.threads,
        "execution": {
            "star_runner": star_runner,
            "star_image": DEFAULT_STAR_IMAGE,
            "star_image_tag": DEFAULT_STAR_IMAGE_TAG,
        },
        "references": {
            "genome_fasta": str(Path(args.genome_fasta).expanduser().resolve()),
            "annotation_gtf": str(Path(args.annotation_gtf).expanduser().resolve()),
            "cb_whitelist": str(Path(args.cb_whitelist).expanduser().resolve()),
        },
        "chemistry": {
            "name": args.chemistry,
            "cb_start": args.cb_start,
            "cb_len": args.cb_len,
            "umi_start": args.umi_start,
            "umi_len": args.umi_len,
            "sjdb_overhang": args.sjdb_overhang,
            "solo_type": "CB_UMI_Simple",
            "solo_cell_filter": "CellRanger2.2 3000 0.99 10",
            "features_mode": "Gene",
        },
        "chemistry_detection": chemistry,
        "runtime_pins": {
            "snakemake": PINNED_SNAKEMAKE_VERSION,
            "star": PINNED_STAR_VERSION,
            "star_image": DEFAULT_STAR_IMAGE,
            "star_image_tag": DEFAULT_STAR_IMAGE_TAG,
        },
    }


def write_workflow(run_dir: Path) -> None:
    workflow_dir = run_dir / "workflow"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    for source in WORKFLOW_DIR.iterdir():
        if source.is_file():
            target_name = "Snakefile" if source == WORKFLOW_TEMPLATE else source.name
            shutil.copy2(source, workflow_dir / target_name)


def runtime_source_cache_path(run_dir: Path) -> Path:
    cache_dir = run_dir / ".snakemake" / "runtime-source-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def write_working_sample_sheet(run_dir: Path, samples: list[dict[str, Any]]) -> Path:
    manifest_dir = run_dir / "manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / "working_samplesheet.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sample",
                "original_sample",
                "fastq_1",
                "fastq_2",
                "expected_cells",
                "replicate",
            ],
        )
        writer.writeheader()
        for sample in samples:
            writer.writerow(
                {
                    "sample": sample["sample"],
                    "original_sample": sample.get("original_sample", sample["sample"]),
                    "fastq_1": sample["barcode_fastq"],
                    "fastq_2": sample["cdna_fastq"],
                    "expected_cells": sample.get("expected_cells", ""),
                    "replicate": sample.get("replicate", ""),
                }
            )
    return path


def write_inputs_manifest(
    run_dir: Path, args: argparse.Namespace, samples: list[dict[str, Any]]
) -> Path:
    manifest_dir = run_dir / "manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / "inputs_manifest.tsv"
    rows = [
        (
            "sample_sheet",
            str(Path(args.sample_sheet).expanduser().resolve()) if args.sample_sheet else "",
            "user_input",
        ),
        ("genome_fasta", str(Path(args.genome_fasta).expanduser().resolve()), "reference"),
        ("annotation_gtf", str(Path(args.annotation_gtf).expanduser().resolve()), "reference"),
        ("cb_whitelist", str(Path(args.cb_whitelist).expanduser().resolve()), "reference"),
    ]
    for sample in samples:
        rows.append((f"{sample['sample']}.fastq_1", sample["barcode_fastq"], "fastq"))
        rows.append((f"{sample['sample']}.fastq_2", sample["cdna_fastq"], "fastq"))
    lines = ["logical_name\tpath\trole"]
    for logical_name, file_path, role in rows:
        lines.append(f"{logical_name}\t{file_path}\t{role}")
    write_text(path, "\n".join(lines) + "\n")
    return path


def write_commands(run_dir: Path, cores: int, runtime_cache_path: Path) -> None:
    commands = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"cd {json.dumps(str(run_dir))}",
        "snakemake --snakefile workflow/Snakefile --configfile config.json "
        f"--runtime-source-cache-path {shlex.quote(str(runtime_cache_path))} "
        f"--cores {cores} --dry-run",
        "snakemake --snakefile workflow/Snakefile --configfile config.json "
        f"--runtime-source-cache-path {shlex.quote(str(runtime_cache_path))} "
        f"--cores {cores}",
        "",
    ]
    path = run_dir / "commands.sh"
    path.write_text("\n".join(commands), encoding="utf-8")
    path.chmod(0o755)


def snakemake_cmd(cores: int, dry_run: bool, runtime_cache_path: Path) -> list[str]:
    snakemake = shell_tool_command("snakemake") or "snakemake"
    cmd = [
        *shlex.split(snakemake),
        "--snakefile",
        "workflow/Snakefile",
        "--configfile",
        "config.json",
        "--runtime-source-cache-path",
        str(runtime_cache_path),
        "--cores",
        str(cores),
    ]
    if dry_run:
        cmd.append("--dry-run")
    return cmd


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# scRNA FASTQ-to-count Run Summary",
        "",
        f"Status: `{status}`",
        "",
        "## Key Artifacts",
        "",
        "- `counts/<sample>/Solo.out/Gene/raw/matrix.mtx`",
        "- `counts/<sample>/Solo.out/Gene/raw/barcodes.tsv`",
        "- `counts/<sample>/Solo.out/Gene/raw/features.tsv`",
        "- `validation/input_summary.json`",
        "- `validation/validation_summary.json`",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `artifact_index.json`",
        "",
    ]
    if validation.get("warnings"):
        lines.extend(["## Validation Warnings", ""])
        lines.extend(f"- {warning}" for warning in validation["warnings"])
        lines.append("")
    lines.extend(ngs_resource_gate.resource_summary_lines(resource_plan))
    lines.append("Raw FASTQs were read-only inputs and were not modified.")
    lines.append("")
    (run_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-sheet", help="CSV with group/sample, fastq_1, and fastq_2 columns."
    )
    parser.add_argument("--sample", help="Sample name for single-sample mode.")
    parser.add_argument("--barcode-fastq", help="R1 barcode/UMI FASTQ for single-sample mode.")
    parser.add_argument("--cdna-fastq", help="R2 cDNA FASTQ for single-sample mode.")
    parser.add_argument("--genome-fasta", required=True)
    parser.add_argument("--annotation-gtf", required=True)
    parser.add_argument("--cb-whitelist", required=True)
    parser.add_argument("--expected-cells")
    parser.add_argument(
        "--outdir",
        type=Path,
        help="Run directory. Defaults to ngs_runs/scrnaseq_fastq_to_count/<timestamp>.",
    )
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--run-id", default=slug_timestamp())
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run Snakemake after validation and workflow validation.",
    )
    parser.add_argument(
        "--no-dry-run", action="store_true", help="Skip Snakemake workflow validation."
    )
    parser.add_argument(
        "--quick-validation", action="store_true", help="Check only the first N records per FASTQ."
    )
    parser.add_argument("--pair-check-reads", type=int, default=1000)
    parser.add_argument("--chemistry", default="10x_v2")
    parser.add_argument("--cb-start", type=int, default=1)
    parser.add_argument("--cb-len", type=int, default=16)
    parser.add_argument("--umi-start", type=int, default=17)
    parser.add_argument("--umi-len", type=int, default=10)
    parser.add_argument("--sjdb-overhang", type=int, default=99)
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    config: dict[str, Any] = {}
    validation: dict[str, Any] = {"ok": False, "errors": [], "warnings": [], "samples": []}
    tool_status: dict[str, Any] = {"ok": False}
    dry_run: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    status = "failed"
    samples, parse_errors = parse_samples(args)
    validation = (
        validate_samples(samples, args.pair_check_reads, args.quick_validation)
        if samples
        else {
            "ok": False,
            "errors": [],
            "warnings": [],
            "samples": [],
            "quick_validation": args.quick_validation,
            "pair_check_reads": args.pair_check_reads,
        }
    )
    validation["errors"] = parse_errors + validation.get("errors", [])
    validation["ok"] = not validation["errors"]
    tool_status = tool_preflight()
    config = build_config(samples, args) if samples else {}
    input_validation = dict(validation)
    resource_plan = ngs_resource_gate.write_pipeline_resource_plan(
        run_dir=run_dir,
        pipeline="scrnaseq",
        genome_build=args.genome_build,
        bundle_roots=args.bundle_root,
        include_optional=args.include_optional_resources,
        include_checksums=args.resource_checksums,
        skip=args.skip_resource_plan,
        required=args.require_resource_plan,
    )
    validation = ngs_resource_gate.merge_resource_status(
        validation,
        resource_plan,
        required=args.require_resource_plan,
    )

    if config:
        write_json(run_dir / "config.json", config)
    write_json(
        run_dir / "validation" / "input_summary.json", {"samples": config.get("samples", {})}
    )
    write_json(run_dir / "validation" / "input_validation_summary.json", input_validation)
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_json(run_dir / "versions" / "software_versions.json", runtime_version_snapshot())
    working_samplesheet = write_working_sample_sheet(run_dir, samples)
    inputs_manifest = write_inputs_manifest(run_dir, args, samples)
    source_cache_path = runtime_source_cache_path(run_dir)
    write_workflow(run_dir)
    write_commands(run_dir, args.threads, source_cache_path)

    try:
        status = "prepared"
        blocked = not validation["ok"] or not tool_status["ok"]
        if blocked:
            status = "blocked"
        elif not args.no_dry_run:
            dry_run = run_cmd(
                snakemake_cmd(args.threads, dry_run=True, runtime_cache_path=source_cache_path),
                run_dir,
                timeout=600,
            )
            write_json(run_dir / "logs" / "snakemake_dry_run.json", dry_run)
            write_text(run_dir / "logs" / "snakemake_dry_run.log", dry_run.get("stdout_tail", ""))
            if not dry_run.get("ok"):
                status = "failed"
                blocked = True
        if args.execute and not blocked:
            execution = run_cmd(
                snakemake_cmd(args.threads, dry_run=False, runtime_cache_path=source_cache_path),
                run_dir,
                timeout=86400,
            )
            write_json(run_dir / "logs" / "snakemake_execute.json", execution)
            write_text(run_dir / "logs" / "snakemake_execute.log", execution.get("stdout_tail", ""))
            status = "completed" if execution.get("ok") else "failed"
        elif not args.execute and status == "prepared":
            status = "validated"
    except Exception as exc:  # pragma: no cover - defensive manifest completion
        write_text(run_dir / "logs" / "runner_exception.txt", f"{type(exc).__name__}: {exc}\n")
        execution = execution or {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        status = "failed"

    write_summary(run_dir, status, validation, resource_plan)
    resource_outputs = ngs_resource_gate.resource_output_paths(resource_plan)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="scrnaseq_fastq_to_count",
        workflow="local_snakemake_starsolo",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(Path(args.sample_sheet).expanduser().resolve())
            if args.sample_sheet
            else None,
            "working_sample_sheet": str(working_samplesheet),
            "inputs_manifest": str(inputs_manifest),
            "references": config.get("references", {}),
            "samples": config.get("samples", {}),
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "raw_matrix_glob": "counts/*/Solo.out/Gene/raw/*.tsv",
            "raw_matrix_mtx_glob": "counts/*/Solo.out/Gene/raw/*.mtx",
            "filtered_matrix_glob": "counts/*/Solo.out/Gene/filtered/*",
            "star_logs_glob": "counts/*/Log*",
            "versions": "versions/software_versions.json",
            "manifest_glob": "manifest/*",
            **resource_outputs,
        },
        method={
            "runner": "STARsolo",
            "chemistry": config.get("chemistry"),
            "chemistry_detection": config.get("chemistry_detection"),
            "runtime_pins": config.get("runtime_pins"),
            "resource_plan": resource_plan,
        },
        audit={"resource_readiness": resource_plan} if resource_plan else None,
    )
    write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))

    print(run_dir)
    if status in {"blocked", "failed"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
