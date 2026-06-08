#!/usr/bin/env python3
"""Run local FASTQ QC with validation, Snakemake execution, and artifacts."""

from __future__ import annotations

import argparse
import csv
import gzip
import importlib.util
import json
import re
import shlex
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from ngs_visualization_utils import (
    artifact_entry,
    reachable_localhost_url_for_path,
    write_localhost_launch_hint,
    write_multiqc_browser_helper,
    write_visualization_index,
)

SCRIPT_PATH = Path(__file__).resolve()
PLUGIN_ROOT = SCRIPT_PATH.parents[1]
WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "fastq_qc"
SAMPLE_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
FASTQ_EXTENSIONS = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
READ_NAME_PREVIEW_LIMIT = 25
FASTQ_ASSAY_CHOICES = ("generic", "rna_seq", "amplicon", "small_rna", "targeted")


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slug_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S-fastq-qc")


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
    if name == "multiqc" and module_present("multiqc"):
        return f"{sys.executable} -m multiqc"
    if name == "cutadapt" and module_present("cutadapt"):
        return f"{sys.executable} -m cutadapt"
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
                if not header.startswith("@"):
                    stats["errors"].append(f"record {record_count} header does not start with @")
                if not plus.startswith("+"):
                    stats["errors"].append(f"record {record_count} separator does not start with +")
                if len(sequence.rstrip("\n\r")) != len(quality.rstrip("\n\r")):
                    stats["errors"].append(
                        f"record {record_count} sequence and quality lengths differ"
                    )
                if len(stats["first_read_names"]) < min(pair_check_reads, READ_NAME_PREVIEW_LIMIT):
                    stats["first_read_names"].append(normalize_read_name(header))
                if quick and record_count >= pair_check_reads:
                    break
        stats["record_count"] = None if quick else record_count
        stats["records_checked"] = record_count
        stats["gzip_ok"] = True if path.name.endswith(".gz") else None
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
            sample_col = (
                "sample" if "sample" in columns else "sample_id" if "sample_id" in columns else None
            )
            r1_col = "fastq_1" if "fastq_1" in columns else "r1" if "r1" in columns else None
            r2_col = "fastq_2" if "fastq_2" in columns else "r2" if "r2" in columns else None
            if not sample_col or not r1_col:
                return [], ["sample sheet must include sample/sample_id and fastq_1/r1 columns"]
            for index, row in enumerate(reader, start=2):
                sample = (row.get(sample_col) or "").strip()
                r1 = (row.get(r1_col) or "").strip()
                r2 = (row.get(r2_col) or "").strip() if r2_col else ""
                if not sample or not r1:
                    errors.append(f"row {index}: sample and fastq_1 are required")
                    continue
                if is_remote_uri(r1) or (r2 and is_remote_uri(r2)):
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
                        "r1": str(resolve_path(r1, sheet.parent)),
                        "r2": str(resolve_path(r2, sheet.parent)) if r2 else None,
                        "layout": "paired" if r2 else "single",
                    }
                )
    elif args.r1:
        sample = args.sample or Path(args.r1).name.split(".")[0]
        samples.append(
            {
                "sample": sample,
                "original_sample": sample,
                "r1": str(Path(args.r1).expanduser().resolve()),
                "r2": str(Path(args.r2).expanduser().resolve()) if args.r2 else None,
                "layout": "paired" if args.r2 else "single",
            }
        )
    else:
        errors.append("provide --sample-sheet or --r1")

    seen: set[str] = set()
    for sample in samples:
        name = sample["sample"]
        if not SAMPLE_RE.match(name):
            errors.append(f"sample name {name!r} must match {SAMPLE_RE.pattern}")
        seen.add(name)
    return samples, errors


def validate_samples(
    samples: list[dict[str, Any]], pair_check_reads: int, quick: bool
) -> dict[str, Any]:
    sample_summaries = []
    errors: list[str] = []
    warnings: list[str] = []
    for sample in samples:
        r1_stats = fastq_stats(Path(sample["r1"]), pair_check_reads, quick)
        r2_stats = (
            fastq_stats(Path(sample["r2"]), pair_check_reads, quick) if sample.get("r2") else None
        )
        pair_summary = {"checked": False, "mismatches": [], "record_count_match": None}
        if r2_stats:
            pair_summary["checked"] = True
            r1_names = r1_stats.get("first_read_names", [])
            r2_names = r2_stats.get("first_read_names", [])
            mismatch_count = 0
            for index, (r1_name, r2_name) in enumerate(zip(r1_names, r2_names), start=1):
                if r1_name != r2_name:
                    mismatch_count += 1
                    if len(pair_summary["mismatches"]) < 10:
                        pair_summary["mismatches"].append(
                            {"record": index, "r1": r1_name, "r2": r2_name}
                        )
            if mismatch_count:
                errors.append(f"{sample['sample']}: first read names do not match between R1/R2")
            if (
                r1_stats.get("record_count") is not None
                and r2_stats.get("record_count") is not None
            ):
                pair_summary["record_count_match"] = (
                    r1_stats["record_count"] == r2_stats["record_count"]
                )
                if not pair_summary["record_count_match"]:
                    errors.append(f"{sample['sample']}: R1/R2 record counts differ")
            else:
                warnings.append(
                    f"{sample['sample']}: quick validation skipped full R1/R2 count parity"
                )
        for label, stats in [("R1", r1_stats), ("R2", r2_stats)]:
            if not stats:
                continue
            for error in stats.get("errors", []):
                errors.append(f"{sample['sample']} {label}: {error}")
        sample_summaries.append(
            {
                "sample": sample["sample"],
                "layout": sample["layout"],
                "r1": r1_stats,
                "r2": r2_stats,
                "pairing": pair_summary,
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


def tool_preflight(trim_mode: str) -> dict[str, Any]:
    required = ["snakemake", "fastqc", "multiqc"]
    if trim_mode == "fastp":
        required.append("fastp")
    if trim_mode == "cutadapt":
        required.append("cutadapt")
    tools = {name: shell_tool_command(name) for name in sorted(set(required + ["seqkit"]))}
    missing = [name for name in required if not tools.get(name)]
    return {
        "created_at": now_iso(),
        "required": required,
        "tools": tools,
        "missing": missing,
        "ok": not missing,
    }


def render_snakefile(trim_mode: str) -> str:
    trim_enabled = trim_mode != "none"
    base = f'''"""Plugin-owned local FASTQ QC workflow."""

SAMPLES = config["samples"]
THREADS = int(config.get("threads", 4))
TRIM_MODE = config.get("trim_mode", "none")
TRIM_ENABLED = {str(trim_enabled)}
MULTIQC = config.get("commands", {{}}).get("multiqc", "multiqc")
CUTADAPT = config.get("commands", {{}}).get("cutadapt", "cutadapt")
PAIRED = [sample for sample, meta in SAMPLES.items() if meta.get("r2")]
SINGLE = [sample for sample, meta in SAMPLES.items() if not meta.get("r2")]


def raw_targets():
    targets = ["multiqc/raw/multiqc_report.html"]
    if TRIM_ENABLED:
        targets.append("multiqc/trimmed/multiqc_report.html")
    return targets


rule all:
    input:
        raw_targets()


rule fastqc_raw:
    input:
        lambda wildcards: [SAMPLES[wildcards.sample]["r1"]] + ([SAMPLES[wildcards.sample]["r2"]] if SAMPLES[wildcards.sample].get("r2") else [])
    output:
        touch("fastqc/raw/{{sample}}.done")
    threads: THREADS
    shell:
        "mkdir -p fastqc/raw && fastqc -t {{threads}} -o fastqc/raw {{input}}"


rule multiqc_raw:
    input:
        expand("fastqc/raw/{{sample}}.done", sample=SAMPLES.keys())
    output:
        "multiqc/raw/multiqc_report.html"
    shell:
        "mkdir -p multiqc/raw && {{MULTIQC}} --force --no-version-check --no-megaqc-upload fastqc/raw -o multiqc/raw"
'''

    if not trim_enabled:
        return base

    if trim_mode == "fastp":
        trim_rules = """


rule fastp_paired:
    input:
        r1=lambda wildcards: SAMPLES[wildcards.sample]["r1"],
        r2=lambda wildcards: SAMPLES[wildcards.sample]["r2"],
    output:
        r1="trimmed/{{sample}}/{{sample}}_R1.fastq.gz",
        r2="trimmed/{{sample}}/{{sample}}_R2.fastq.gz",
        html="trimmed/{{sample}}/{{sample}}.fastp.html",
        json="trimmed/{{sample}}/{{sample}}.fastp.json",
    threads: THREADS
    shell:
        "mkdir -p trimmed/{{wildcards.sample}} && "
        "fastp -i {{input.r1}} -I {{input.r2}} -o {{output.r1}} -O {{output.r2}} "
        "--html {{output.html}} --json {{output.json}} --thread {{threads}}"


rule fastp_single:
    input:
        r1=lambda wildcards: SAMPLES[wildcards.sample]["r1"],
    output:
        r1="trimmed/{{sample}}/{{sample}}.fastq.gz",
        html="trimmed/{{sample}}/{{sample}}.fastp.html",
        json="trimmed/{{sample}}/{{sample}}.fastp.json",
    threads: THREADS
    shell:
        "mkdir -p trimmed/{{wildcards.sample}} && "
        "fastp -i {{input.r1}} -o {{output.r1}} --html {{output.html}} "
        "--json {{output.json}} --thread {{threads}}"
"""
    elif trim_mode == "cutadapt":
        trim_rules = """


rule cutadapt_paired:
    input:
        r1=lambda wildcards: SAMPLES[wildcards.sample]["r1"],
        r2=lambda wildcards: SAMPLES[wildcards.sample]["r2"],
    output:
        r1="trimmed/{{sample}}/{{sample}}_R1.fastq.gz",
        r2="trimmed/{{sample}}/{{sample}}_R2.fastq.gz",
        log="trimmed/{{sample}}/{{sample}}.cutadapt.log",
    params:
        a=lambda wildcards: config.get("adapter_r1", ""),
        A=lambda wildcards: config.get("adapter_r2", ""),
    shell:
        "mkdir -p trimmed/{{wildcards.sample}} && "
        "{{CUTADAPT}} -a {{params.a}} -A {{params.A}} -o {{output.r1}} -p {{output.r2}} "
        "{{input.r1}} {{input.r2}} > {{output.log}}"


rule cutadapt_single:
    input:
        r1=lambda wildcards: SAMPLES[wildcards.sample]["r1"],
    output:
        r1="trimmed/{{sample}}/{{sample}}.fastq.gz",
        log="trimmed/{{sample}}/{{sample}}.cutadapt.log",
    params:
        a=lambda wildcards: config.get("adapter_r1", ""),
    shell:
        "mkdir -p trimmed/{{wildcards.sample}} && "
        "{{CUTADAPT}} -a {{params.a}} -o {{output.r1}} {{input.r1}} > {{output.log}}"
"""
    else:
        raise ValueError(f"unsupported trim mode: {trim_mode}")

    trim_qc_rules = """


rule fastqc_trimmed_paired:
    input:
        r1="trimmed/{{sample}}/{{sample}}_R1.fastq.gz",
        r2="trimmed/{{sample}}/{{sample}}_R2.fastq.gz",
    output:
        touch("fastqc/trimmed/paired/{{sample}}.done")
    threads: THREADS
    shell:
        "mkdir -p fastqc/trimmed && fastqc -t {{threads}} -o fastqc/trimmed {{input.r1}} {{input.r2}}"


rule fastqc_trimmed_single:
    input:
        r1="trimmed/{{sample}}/{{sample}}.fastq.gz",
    output:
        touch("fastqc/trimmed/single/{{sample}}.done")
    threads: THREADS
    shell:
        "mkdir -p fastqc/trimmed && fastqc -t {{threads}} -o fastqc/trimmed {{input.r1}}"


rule multiqc_trimmed:
    input:
        expand("fastqc/trimmed/paired/{{sample}}.done", sample=PAIRED),
        expand("fastqc/trimmed/single/{{sample}}.done", sample=SINGLE)
    output:
        "multiqc/trimmed/multiqc_report.html"
    shell:
        "mkdir -p multiqc/trimmed && {{MULTIQC}} --force --no-version-check --no-megaqc-upload fastqc/trimmed trimmed -o multiqc/trimmed"
"""
    trim_rules = trim_rules.replace("{{", "{").replace("}}", "}")
    trim_qc_rules = trim_qc_rules.replace("{{", "{").replace("}}", "}")
    return base + trim_rules + trim_qc_rules


def write_workflow(run_dir: Path, trim_mode: str) -> None:
    workflow_dir = run_dir / "workflow"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    snakefile = render_snakefile(trim_mode)
    (workflow_dir / "Snakefile").write_text(snakefile, encoding="utf-8")


def write_commands(run_dir: Path, cores: int) -> None:
    commands = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"cd {json.dumps(str(run_dir))}",
        shlex.join(snakemake_cmd(run_dir, cores, dry_run=True)),
        shlex.join(snakemake_cmd(run_dir, cores, dry_run=False)),
        "",
    ]
    path = run_dir / "commands.sh"
    path.write_text("\n".join(commands), encoding="utf-8")
    path.chmod(0o755)


def snakemake_cmd(run_dir: Path, cores: int, dry_run: bool) -> list[str]:
    snakemake = shell_tool_command("snakemake") or "snakemake"
    cmd = [
        "env",
        f"XDG_CACHE_HOME={run_dir / '.cache'}",
        *shlex.split(snakemake),
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


def _safe_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _poly_n_fraction(sequence: str) -> float:
    if not sequence:
        return 0.0
    n_count = sum(1 for base in sequence.upper() if base == "N")
    return n_count / len(sequence)


def _extract_fastqc_metrics(data_text: str) -> tuple[dict[str, str], dict[str, Any]]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    for line in data_text.splitlines():
        if line.startswith(">>END_MODULE"):
            current_section = None
            continue
        if line.startswith(">>"):
            parts = line[2:].split("\t")
            current_section = parts[0]
            sections[current_section] = []
            continue
        if current_section is not None:
            sections[current_section].append(line)

    basic_stats: dict[str, str] = {}
    metrics: dict[str, Any] = {
        "total_sequences": None,
        "sequence_length": None,
        "gc_percent": None,
        "deduplicated_percent": None,
        "duplicate_percent": None,
        "overrepresented_top_percent": 0.0,
        "overrepresented_adapter_like_percent": 0.0,
        "overrepresented_no_hit_percent": 0.0,
        "overrepresented_poly_n_percent": 0.0,
        "adapter_content_max_percent": 0.0,
    }

    for line in sections.get("Basic Statistics", []):
        if not line or line.startswith("#"):
            continue
        key, value = line.split("\t", 1)
        basic_stats[key] = value
    metrics["total_sequences"] = _safe_int(basic_stats.get("Total Sequences"))
    metrics["sequence_length"] = basic_stats.get("Sequence length")
    metrics["gc_percent"] = _safe_float(basic_stats.get("%GC"))

    for line in sections.get("Sequence Duplication Levels", []):
        if line.startswith("#Total Deduplicated Percentage"):
            _, value = line.split("\t", 1)
            metrics["deduplicated_percent"] = _safe_float(value)
            if metrics["deduplicated_percent"] is not None:
                metrics["duplicate_percent"] = round(100.0 - metrics["deduplicated_percent"], 3)
            break

    for line in sections.get("Overrepresented sequences", []):
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) < 4:
            continue
        sequence, _count, percent_raw, source = fields[:4]
        percent = _safe_float(percent_raw) or 0.0
        metrics["overrepresented_top_percent"] = max(
            metrics["overrepresented_top_percent"], percent
        )
        if source != "No Hit":
            metrics["overrepresented_adapter_like_percent"] += percent
        else:
            metrics["overrepresented_no_hit_percent"] += percent
        if _poly_n_fraction(sequence) >= 0.5:
            metrics["overrepresented_poly_n_percent"] += percent

    adapter_rows = [
        line for line in sections.get("Adapter Content", []) if line and not line.startswith("#")
    ]
    if adapter_rows:
        header = sections["Adapter Content"][0].split("\t")
        for line in adapter_rows:
            fields = line.split("\t")
            for value in fields[1 : len(header)]:
                metrics["adapter_content_max_percent"] = max(
                    metrics["adapter_content_max_percent"], _safe_float(value) or 0.0
                )

    return basic_stats, metrics


def fastqc_zip_summaries(root: Path) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for zip_path in sorted(root.glob("*_fastqc.zip")):
        modules = []
        basic_stats: dict[str, str] = {}
        metrics: dict[str, Any] = {}
        try:
            with zipfile.ZipFile(zip_path) as archive:
                summary_name = next(
                    name for name in archive.namelist() if name.endswith("/summary.txt")
                )
                for line in (
                    archive.read(summary_name).decode("utf-8", errors="replace").splitlines()
                ):
                    status, module, filename = line.split("\t")[:3]
                    modules.append({"status": status, "module": module, "file": filename})
                data_name = next(
                    name for name in archive.namelist() if name.endswith("/fastqc_data.txt")
                )
                data_text = archive.read(data_name).decode("utf-8", errors="replace")
                basic_stats, metrics = _extract_fastqc_metrics(data_text)
        except Exception as exc:  # noqa: BLE001
            modules.append({"status": "ERROR", "module": "FastQC zip parsing", "detail": str(exc)})
        summaries[zip_path.name] = {
            "modules": modules,
            "basic_statistics": basic_stats,
            "metrics": metrics,
        }
    return summaries


def interpret_qc(
    raw_summaries: dict[str, Any], trimmed_summaries: dict[str, Any] | None, assay_type: str
) -> dict[str, Any]:
    module_statuses: dict[str, dict[str, int]] = {}
    sample_metrics: dict[str, Any] = {}
    recommendation_reasons: list[str] = []
    context_warnings: list[str] = []
    quality_issue = False
    adapter_issue = False
    poly_n_issue = False
    for sample_name, summary in raw_summaries.items():
        sample_metrics[sample_name] = summary.get("metrics", {})
        for module in summary.get("modules", []):
            name = module.get("module", "unknown")
            status = module.get("status", "unknown")
            module_statuses.setdefault(name, {}).setdefault(status, 0)
            module_statuses[name][status] += 1
        metrics = summary.get("metrics", {})
        if (metrics.get("adapter_content_max_percent") or 0.0) >= 5.0 or (
            metrics.get("overrepresented_adapter_like_percent") or 0.0
        ) >= 1.0:
            adapter_issue = True
        if (metrics.get("overrepresented_poly_n_percent") or 0.0) >= 1.0:
            poly_n_issue = True
    for module_name in ["Per base sequence quality", "Per sequence quality scores"]:
        counts = module_statuses.get(module_name, {})
        if counts.get("WARN") or counts.get("FAIL"):
            quality_issue = True

    if quality_issue:
        recommendation_reasons.append(
            "Per-base or per-sequence quality modules showed WARN/FAIL, which can justify end trimming or closer review."
        )
    if adapter_issue:
        recommendation_reasons.append(
            "Adapter-like signal reached an actionable fraction in raw FastQC metrics."
        )
    if poly_n_issue:
        recommendation_reasons.append(
            "Poly-N overrepresented sequences reached an actionable fraction in raw FastQC metrics."
        )

    if not recommendation_reasons:
        recommendation = "no_trimming_by_default"
        recommendation_reasons.append(
            "Raw FastQC metrics did not show trimming-level adapter or quality degradation."
        )
    elif quality_issue:
        recommendation = "quality_trim_or_investigate"
    elif adapter_issue:
        recommendation = "trim_adapters_or_primers"
    else:
        recommendation = "investigate_low_complexity_or_n_content"

    duplication = module_statuses.get("Sequence Duplication Levels", {})
    if duplication.get("WARN") or duplication.get("FAIL"):
        if assay_type in {"rna_seq", "amplicon", "small_rna"}:
            context_warnings.append(
                f"Sequence duplication is elevated, but that can be expected for {assay_type.replace('_', '-')} libraries and is not sufficient on its own to trigger trimming."
            )
        else:
            context_warnings.append(
                "Sequence duplication is elevated; interpret it as a library-complexity signal before filtering."
            )
    base_content = module_statuses.get("Per base sequence content", {})
    if base_content.get("WARN") or base_content.get("FAIL"):
        if assay_type in {"rna_seq", "amplicon", "small_rna"}:
            context_warnings.append(
                f"Per-base sequence content is WARN/FAIL, which often reflects composition bias in {assay_type.replace('_', '-')} rather than removable adapter sequence."
            )
        else:
            context_warnings.append(
                "Per-base sequence content is WARN/FAIL and should be interpreted in assay context rather than treated as an automatic trimming trigger."
            )

    return {
        "created_at": now_iso(),
        "assay_type": assay_type,
        "raw_fastqc_files": raw_summaries,
        "trimmed_fastqc_files": trimmed_summaries or {},
        "module_status_counts": module_statuses,
        "sample_metrics": sample_metrics,
        "recommendation": recommendation,
        "recommendation_reasons": recommendation_reasons,
        "context_warnings": context_warnings,
        "notes": [
            "Do not trim solely because a FastQC module warns; weight the affected fraction, assay context, and downstream requirements.",
            "Preserve raw FastQC and MultiQC outputs even when a trimming branch is executed.",
        ],
    }


def artifact_index(run_dir: Path) -> dict[str, Any]:
    patterns = [
        "fastqc/**/*.html",
        "fastqc/**/*.zip",
        "multiqc/**/*.html",
        "multiqc/**/*",
        "trimmed/**/*",
        "visualizations/**/*",
        "qc_interpretation.json",
        "validation/*.json",
        "logs/*.json",
        "logs/*.log",
        "workflow/Snakefile",
        "commands.sh",
        "config.json",
        "run_manifest.json",
        "summary.md",
    ]
    artifacts = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in run_dir.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                artifacts.append(
                    {
                        "path": str(path.relative_to(run_dir)),
                        "bytes": path.stat().st_size,
                    }
                )
    return {"created_at": now_iso(), "artifacts": sorted(artifacts, key=lambda item: item["path"])}


def write_summary(
    run_dir: Path,
    status: str,
    interpretation: dict[str, Any] | None,
    review_outputs: dict[str, str | None],
) -> None:
    lines = [
        "# FASTQ QC Run Summary",
        "",
        f"Status: `{status}`",
        "",
    ]
    if interpretation:
        lines.extend(
            [
                f"Recommendation: `{interpretation['recommendation']}`",
                "",
                "## Reasons",
                "",
            ]
        )
        reasons = interpretation.get("recommendation_reasons") or [
            "No trimming signal was detected in raw FastQC summaries."
        ]
        lines.extend(f"- {reason}" for reason in reasons)
        lines.append("")
        warnings = interpretation.get("context_warnings") or []
        if warnings:
            lines.extend(
                [
                    "## Context Warnings",
                    "",
                ]
            )
            lines.extend(f"- {warning}" for warning in warnings)
            lines.append("")
    lines.extend(
        [
            "## Key Artifacts",
            "",
        ]
    )
    key_artifacts = [
        review_outputs.get("visualization_index"),
        review_outputs.get("multiqc_raw_helper"),
        review_outputs.get("localhost_launch_hint"),
        review_outputs.get("multiqc_raw_localhost"),
        review_outputs.get("multiqc_trimmed_helper"),
        review_outputs.get("multiqc_trimmed_localhost"),
        "qc_interpretation.json" if interpretation else None,
        "validation/input_summary.json",
        "validation/validation_summary.json",
        "artifact_index.json",
    ]
    for path in key_artifacts:
        if not path:
            continue
        if path.startswith(("http://", "https://")) or (run_dir / path).exists():
            lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "Raw FASTQs were read-only inputs and were not modified.",
            "",
        ]
    )
    (run_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def build_review_bundle(
    run_dir: Path, interpretation: dict[str, Any] | None, trim_mode: str
) -> dict[str, str | None]:
    notes = [
        "Use the browser helper or visualization index first when the raw MultiQC HTML struggles under file:// in the in-app browser.",
        "Recommendation logic combines FastQC status modules with parsed fractions from raw FastQC tables, rather than treating every WARN as trimming-worthy.",
    ]
    entries: list[dict[str, Any]] = []
    localhost_reports = [("Raw MultiQC", "multiqc/raw/multiqc_report.html")]
    helper_specs = [
        (
            "multiqc_raw_helper",
            "Raw MultiQC Browser Helper",
            "multiqc/raw/multiqc_browser_helper.html",
            "Browser-safe view over the raw FastQC MultiQC report.",
        ),
    ]
    if trim_mode != "none":
        localhost_reports.append(("Trimmed MultiQC", "multiqc/trimmed/multiqc_report.html"))
        helper_specs.extend(
            [
                (
                    "multiqc_trimmed_helper",
                    "Trimmed MultiQC Browser Helper",
                    "multiqc/trimmed/multiqc_browser_helper.html",
                    "Browser-safe view over the trimmed FastQC MultiQC report.",
                ),
            ]
        )
    launch_hint = write_localhost_launch_hint(run_dir, report_entries=localhost_reports)
    for label, rel_path in localhost_reports:
        path = run_dir / rel_path
        path_parts = Path(rel_path).parts
        link_key = path_parts[1] if len(path_parts) > 1 else Path(rel_path).stem
        live_url = reachable_localhost_url_for_path(rel_path)
        entries.append(
            artifact_entry(
                artifact_id=f"{link_key}_localhost",
                title=f"{label} Localhost URL",
                path=live_url,
                kind="localhost_app",
                status="created" if live_url else "not_available",
                description=f"Live localhost review URL for the full {label.lower()} interactive report when the run directory is already being served.",
            )
        )
    for artifact_id, title, rel_path, description in helper_specs:
        path = run_dir / rel_path
        entries.append(
            artifact_entry(
                artifact_id=artifact_id,
                title=title,
                path=rel_path if path.exists() else None,
                kind="html_report",
                status="created" if path.exists() else "not_available",
                description=description,
            )
        )
    entries.append(
        artifact_entry(
            artifact_id="localhost_launch_hint",
            title="Localhost Launch Hint",
            path=str(launch_hint.relative_to(run_dir)),
            kind="text",
            status="created",
            description="Command and localhost URLs for serving the run directory and opening the full MultiQC reports.",
        )
    )
    for zip_name in sorted((interpretation or {}).get("raw_fastqc_files", {})):
        sample_prefix = zip_name.replace("_fastqc.zip", "")
        for suffix, kind in [("_fastqc.html", "html_report"), ("_fastqc.zip", "archive")]:
            rel_path = f"fastqc/raw/{sample_prefix}{suffix}"
            path = run_dir / rel_path
            entries.append(
                artifact_entry(
                    artifact_id=f"{sample_prefix}{suffix}".replace(".", "_"),
                    title=f"{sample_prefix} {suffix.removeprefix('_').replace('_', ' ')}",
                    path=rel_path if path.exists() else None,
                    kind=kind,
                    status="created" if path.exists() else "not_available",
                    description=f"Raw FastQC {suffix.removeprefix('_')} for {sample_prefix}.",
                )
            )
    for artifact_id, title, rel_path, kind, description in [
        (
            "qc_interpretation",
            "QC Interpretation JSON",
            "qc_interpretation.json",
            "json",
            "Machine-readable QC interpretation with recommendation, metrics, and context warnings.",
        ),
        (
            "summary",
            "Run Summary",
            "summary.md",
            "markdown",
            "Concise run summary for human review.",
        ),
        (
            "manifest",
            "Run Manifest",
            "run_manifest.json",
            "json",
            "Run-level manifest with inputs, outputs, and execution status.",
        ),
        (
            "commands",
            "Execution Commands",
            "commands.sh",
            "text",
            "Recorded validation and execute commands for reproducibility.",
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
    index = write_visualization_index(
        run_dir,
        title="FASTQ QC Review Bundle",
        description="Human-readable review surface for raw FASTQ QC, with links to the key reports, command envelope, and machine-readable interpretation.",
        entries=entries,
        notes=notes,
    )
    return {
        "visualization_index": str(index.relative_to(run_dir)),
        "visualization_manifest": "visualizations/visualization_manifest.json",
        "multiqc_raw_helper": "multiqc/raw/multiqc_browser_helper.html"
        if (run_dir / "multiqc/raw/multiqc_browser_helper.html").exists()
        else None,
        "localhost_launch_hint": str(launch_hint.relative_to(run_dir)),
        "multiqc_raw_localhost": reachable_localhost_url_for_path("multiqc/raw/multiqc_report.html")
        if (run_dir / "multiqc/raw/multiqc_report.html").exists()
        else None,
        "multiqc_trimmed_helper": "multiqc/trimmed/multiqc_browser_helper.html"
        if (run_dir / "multiqc/trimmed/multiqc_browser_helper.html").exists()
        else None,
        "multiqc_trimmed_localhost": reachable_localhost_url_for_path(
            "multiqc/trimmed/multiqc_report.html"
        )
        if (run_dir / "multiqc/trimmed/multiqc_report.html").exists()
        else None,
    }


def build_config(samples: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    return {
        "samples": {
            sample["sample"]: {
                "original_sample": sample.get("original_sample", sample["sample"]),
                "r1": sample["r1"],
                "r2": sample.get("r2"),
                "layout": sample["layout"],
            }
            for sample in samples
        },
        "threads": args.threads,
        "assay_type": args.assay_type,
        "trim_mode": args.trim_mode,
        "adapter_r1": args.adapter_r1 or "",
        "adapter_r2": args.adapter_r2 or args.adapter_r1 or "",
        "commands": {
            "multiqc": shell_tool_command("multiqc") or "multiqc",
            "cutadapt": shell_tool_command("cutadapt") or "cutadapt",
        },
    }


def validate_trim_args(args: argparse.Namespace, samples: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if args.trim_mode == "cutadapt" and not args.adapter_r1:
        errors.append("--trim-mode cutadapt requires --adapter-r1")
    if args.trim_mode != "none" and not samples:
        errors.append("trimming requested but no samples were parsed")
    return errors


def write_manifest(
    run_dir: Path,
    run_id: str,
    args: argparse.Namespace,
    status: str,
    config: dict[str, Any],
    validation: dict[str, Any],
    tool_status: dict[str, Any],
    dry_run: dict[str, Any] | None,
    execution: dict[str, Any] | None,
    interpretation: dict[str, Any] | None,
    review_outputs: dict[str, str | None],
) -> None:
    manifest = {
        "run_id": run_id,
        "created_at": now_iso(),
        "status": status,
        "workflow": "fastq_qc_local_snakemake",
        "run_dir": str(run_dir),
        "execute_requested": args.execute,
        "dry_run_performed": dry_run is not None,
        "assay_type": args.assay_type,
        "trim_mode": args.trim_mode,
        "sample_count": len(config["samples"]),
        "samples": sorted(config["samples"]),
        "validation_ok": validation.get("ok"),
        "ready_to_execute": validation.get("ok") and tool_status.get("ok"),
        "tool_preflight_ok": tool_status.get("ok"),
        "dry_run_ok": dry_run.get("ok") if dry_run else None,
        "execution_ok": execution.get("ok") if execution else None,
        "recommendation": interpretation.get("recommendation") if interpretation else None,
        "inputs": config["samples"],
        "outputs": {
            **review_outputs,
            "qc_interpretation": "qc_interpretation.json" if interpretation else None,
        },
    }
    write_json(run_dir / "run_manifest.json", manifest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-sheet", help="CSV with sample, fastq_1, and optional fastq_2 columns."
    )
    parser.add_argument("--sample", help="Sample name for --r1/--r2 single-sample mode.")
    parser.add_argument("--r1", help="FASTQ R1 or single-end FASTQ for single-sample mode.")
    parser.add_argument("--r2", help="FASTQ R2 for single-sample paired mode.")
    parser.add_argument(
        "--outdir", type=Path, help="Run directory. Defaults to ngs_runs/fastq_qc/<timestamp>."
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
    parser.add_argument("--pair-check-reads", type=int, default=10000)
    parser.add_argument("--assay-type", choices=list(FASTQ_ASSAY_CHOICES), default="generic")
    parser.add_argument("--trim-mode", choices=["none", "fastp", "cutadapt"], default="none")
    parser.add_argument("--adapter-r1")
    parser.add_argument("--adapter-r2")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    samples, parse_errors = parse_samples(args)
    trim_errors = validate_trim_args(args, samples)
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
    validation["errors"] = parse_errors + trim_errors + validation.get("errors", [])
    validation["ok"] = not validation["errors"]
    tool_status = tool_preflight(args.trim_mode)
    config = build_config(samples, args)

    write_json(run_dir / "config.json", config)
    write_json(run_dir / "validation" / "input_summary.json", {"samples": config["samples"]})
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_workflow(run_dir, args.trim_mode)
    write_commands(run_dir, args.threads)

    dry_run: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    interpretation: dict[str, Any] | None = None
    review_outputs: dict[str, str | None] = {}
    status = "prepared"
    blocked = not validation["ok"] or not tool_status["ok"]
    if blocked:
        status = "blocked"
    elif not args.no_dry_run:
        dry_run = run_cmd(snakemake_cmd(run_dir, args.threads, dry_run=True), run_dir, timeout=600)
        write_json(run_dir / "logs" / "snakemake_dry_run.json", dry_run)
        (run_dir / "logs" / "snakemake_dry_run.log").write_text(
            dry_run.get("stdout_tail", ""), encoding="utf-8"
        )
        if not dry_run.get("ok"):
            status = "failed"
            blocked = True
    if args.execute and not blocked:
        execution = run_cmd(
            snakemake_cmd(run_dir, args.threads, dry_run=False), run_dir, timeout=86400
        )
        write_json(run_dir / "logs" / "snakemake_execute.json", execution)
        (run_dir / "logs" / "snakemake_execute.log").write_text(
            execution.get("stdout_tail", ""), encoding="utf-8"
        )
        status = "completed" if execution.get("ok") else "failed"
        if execution.get("ok"):
            raw_summaries = fastqc_zip_summaries(run_dir / "fastqc" / "raw")
            trimmed_summaries = (
                fastqc_zip_summaries(run_dir / "fastqc" / "trimmed")
                if (run_dir / "fastqc" / "trimmed").exists()
                else None
            )
            interpretation = interpret_qc(raw_summaries, trimmed_summaries, args.assay_type)
            write_json(run_dir / "qc_interpretation.json", interpretation)
    elif not args.execute and status == "prepared":
        status = "validated"

    write_multiqc_browser_helper(
        run_dir,
        report_path="multiqc/raw/multiqc_report.html",
        title="FASTQ QC Raw MultiQC Browser Helper",
    )
    if args.trim_mode != "none":
        write_multiqc_browser_helper(
            run_dir,
            report_path="multiqc/trimmed/multiqc_report.html",
            title="FASTQ QC Trimmed MultiQC Browser Helper",
        )

    review_outputs = {
        "multiqc_raw_helper": "multiqc/raw/multiqc_browser_helper.html"
        if (run_dir / "multiqc/raw/multiqc_browser_helper.html").exists()
        else None,
        "multiqc_raw_localhost": reachable_localhost_url_for_path("multiqc/raw/multiqc_report.html")
        if (run_dir / "multiqc/raw/multiqc_report.html").exists()
        else None,
        "localhost_launch_hint": str(
            write_localhost_launch_hint(
                run_dir, report_entries=[("Raw MultiQC", "multiqc/raw/multiqc_report.html")]
            ).relative_to(run_dir)
        ),
        "visualization_index": None,
        "visualization_manifest": None,
    }
    write_summary(run_dir, status, interpretation, review_outputs)
    write_manifest(
        run_dir,
        args.run_id,
        args,
        status,
        config,
        validation,
        tool_status,
        dry_run,
        execution,
        interpretation,
        review_outputs,
    )
    review_outputs = build_review_bundle(run_dir, interpretation, args.trim_mode)
    write_summary(run_dir, status, interpretation, review_outputs)
    write_manifest(
        run_dir,
        args.run_id,
        args,
        status,
        config,
        validation,
        tool_status,
        dry_run,
        execution,
        interpretation,
        review_outputs,
    )
    write_json(run_dir / "artifact_index.json", artifact_index(run_dir))

    print(run_dir)
    if status in {"blocked", "failed"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
