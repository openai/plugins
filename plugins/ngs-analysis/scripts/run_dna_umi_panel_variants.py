#!/usr/bin/env python3
"""Run or plan UMI-aware targeted panel variant calling from consensus or raw BAMs."""

from __future__ import annotations

import argparse
import csv
import shutil
import statistics
import subprocess
from pathlib import Path
from typing import Any

import ngs_resource_gate
from ngs_planner_utils import (
    command_plan_entry,
    normalize_sample_name,
    read_table,
    resolve_path,
    shell_join,
    write_command_script,
    write_tsv,
)
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
    add_vcf_review_notebook_entry,
    artifact_entry,
    write_visualization_index,
)

WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "dna_umi_panel_variants"
UMI_POSTRUN_FIELDS = [
    "sample",
    "consensus_state",
    "consensus_bam",
    "consensus_bam_exists",
    "total_consensus_reads",
    "mapped_consensus_reads",
    "mean_target_depth",
    "target_bases_covered",
    "variant_records",
    "snp_count",
    "indel_count",
    "median_family_size",
    "duplex_fraction",
    "status",
    "notes",
]
UMI_EVIDENCE_FIELDS = [
    "sample",
    "umi_mode",
    "consensus_state",
    "min_af",
    "min_reads_per_molecule",
    "consensus_bam",
    "consensus_bam_exists",
    "family_metrics_path",
    "family_metrics_exists",
    "variant_vcf",
    "variant_vcf_exists",
    "variant_stats_path",
    "variant_stats_exists",
    "hotspot_vcf",
    "hotspot_review",
    "duplex_review",
    "low_af_review_status",
    "notes",
]
UMI_SAMPLE_FIELDS = [
    "sample",
    "raw_alignment",
    "consensus_alignment",
    "consensus_state",
    "fgbio_readiness",
    "raw_umi_tag_status",
    "mate_tag_status",
    "row_index",
]


def maybe_path(raw: str | None, base: Path) -> Path | None:
    return resolve_path(raw, base) if raw else None


def inspect_alignment_tags(
    path: Path, required_tags: tuple[str, ...] = ("RX", "MQ"), max_records: int = 200
) -> dict[str, Any]:
    """Inspect a BAM/CRAM for required per-read tags using the first few alignments."""
    status = {
        "inspectable": False,
        "reason": "",
        "records_inspected": 0,
        "tags": {tag: False for tag in required_tags},
        "all_present": False,
    }
    samtools = shutil.which("samtools")
    if samtools is None:
        status["reason"] = "samtools_not_available"
        return status
    if path.suffix.lower() not in {".bam", ".cram"}:
        status["reason"] = "unsupported_alignment_extension"
        return status

    proc = subprocess.Popen(
        [samtools, "view", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stderr = ""
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            status["records_inspected"] += 1
            fields = line.rstrip("\n").split("\t")
            for item in fields[11:]:
                tag = item.split(":", 1)[0]
                if tag in status["tags"]:
                    status["tags"][tag] = True
            if all(status["tags"].values()) or status["records_inspected"] >= max_records:
                break
    finally:
        if proc.stdout is not None:
            proc.stdout.close()
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
        if proc.stderr is not None:
            stderr = proc.stderr.read().strip()
            proc.stderr.close()

    status["inspectable"] = status["records_inspected"] > 0
    status["all_present"] = status["inspectable"] and all(status["tags"].values())
    if not status["inspectable"]:
        status["reason"] = stderr.splitlines()[0] if stderr else "no_alignment_records_observed"
    return status


def validate_inputs(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, str]]]:
    sample_sheet = args.sample_sheet.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, str]] = []
    columns: list[str] = []
    samples: list[dict[str, str]] = []
    if not sample_sheet.exists():
        errors.append(f"sample sheet does not exist: {sample_sheet}")
    else:
        rows, columns = read_table(sample_sheet)

    reference = args.reference_fasta.expanduser().resolve()
    if not reference.exists():
        errors.append(f"reference FASTA does not exist: {reference}")
    if not Path(str(reference) + ".fai").exists():
        warnings.append(
            f"reference FASTA index is missing and may be created by samtools faidx: {reference}.fai"
        )
    target_bed = args.target_bed.expanduser().resolve() if args.target_bed else None
    if target_bed and not target_bed.exists():
        errors.append(f"target BED does not exist: {target_bed}")
    hotspot_vcf = args.hotspot_vcf.expanduser().resolve() if args.hotspot_vcf else None
    if hotspot_vcf and not hotspot_vcf.exists():
        warnings.append(f"hotspot VCF does not exist: {hotspot_vcf}")

    for row_index, row in enumerate(rows, start=2):
        sample = normalize_sample_name(
            row.get("sample") or row.get("sample_id"), f"row_{row_index}"
        )
        raw_bam = maybe_path(
            row.get("bam") or row.get("raw_bam") or row.get("cram"), sample_sheet.parent
        )
        consensus_bam = maybe_path(
            row.get("consensus_bam") or row.get("duplex_bam") or row.get("simplex_bam"),
            sample_sheet.parent,
        )
        tag_status = {
            "inspectable": False,
            "reason": "",
            "tags": {"RX": False, "MQ": False},
            "all_present": False,
        }
        if not raw_bam and not consensus_bam:
            errors.append(f"row {row_index}: provide bam/raw_bam/cram or consensus_bam")
            continue
        if raw_bam and not raw_bam.exists():
            errors.append(f"row {row_index}: raw alignment does not exist: {raw_bam}")
        elif raw_bam:
            tag_status = inspect_alignment_tags(raw_bam)
        if consensus_bam and not consensus_bam.exists():
            warnings.append(f"row {row_index}: consensus BAM does not exist yet: {consensus_bam}")
        if not consensus_bam and not raw_bam:
            errors.append(f"row {row_index}: no usable alignment path")
        if not consensus_bam and not args.umi_tag:
            warnings.append(
                f"row {row_index}: no consensus BAM and no --umi-tag was supplied; consensus generation is not fully specified"
            )
        raw_umi_tag_status = "unknown"
        mate_tag_status = "unknown"
        fgbio_readiness = "not_applicable"
        if raw_bam:
            if tag_status["inspectable"]:
                raw_umi_tag_status = "present" if tag_status["tags"].get("RX") else "missing"
                mate_tag_status = "present" if tag_status["tags"].get("MQ") else "missing"
                fgbio_readiness = "ready" if tag_status["all_present"] else "review_contract_only"
                if fgbio_readiness == "review_contract_only" and not consensus_bam:
                    missing = [tag for tag, present in tag_status["tags"].items() if not present]
                    warnings.append(
                        f"row {row_index}: raw alignment lacks required UMI tags ({','.join(missing)}); "
                        "treat as a review-contract input unless a consensus BAM is already provided"
                    )
            else:
                fgbio_readiness = "unknown"
                warnings.append(
                    f"row {row_index}: could not verify RX/MQ tags on raw alignment; "
                    "end-to-end fgbio readiness remains unconfirmed"
                )
        consensus_state = (
            "provided"
            if consensus_bam
            else (
                "review_contract_only"
                if fgbio_readiness == "review_contract_only"
                else "needs_generation"
            )
        )
        samples.append(
            {
                "sample": sample,
                "raw_alignment": str(raw_bam) if raw_bam else "",
                "consensus_alignment": str(consensus_bam) if consensus_bam else "",
                "consensus_state": consensus_state,
                "fgbio_readiness": fgbio_readiness,
                "raw_umi_tag_status": raw_umi_tag_status,
                "mate_tag_status": mate_tag_status,
                "row_index": str(row_index),
            }
        )
    if not samples:
        errors.append("no usable UMI panel samples found")
    if args.min_af < 0 or args.min_af > 1:
        errors.append("--min-af must be between 0 and 1")
    validation = {
        "ok": not errors,
        "sample_sheet": str(sample_sheet),
        "reference_fasta": str(reference),
        "target_bed": str(target_bed) if target_bed else None,
        "hotspot_vcf": str(hotspot_vcf) if hotspot_vcf else None,
        "columns": columns,
        "sample_count": len(samples),
        "umi_mode": args.umi_mode,
        "umi_tag": args.umi_tag,
        "min_af": args.min_af,
        "errors": errors,
        "warnings": warnings,
    }
    return validation, samples


def build_plan(args: argparse.Namespace, samples: list[dict[str, str]]) -> list[dict[str, Any]]:
    reference = args.reference_fasta.expanduser().resolve()
    plan: list[dict[str, Any]] = []
    for sample in samples:
        name = sample["sample"]
        raw = sample["raw_alignment"]
        consensus = sample["consensus_alignment"] or f"consensus/{name}.consensus.bam"
        can_generate_consensus = (
            sample["consensus_state"] == "needs_generation"
            and bool(raw)
            and sample.get("fgbio_readiness") != "review_contract_only"
        )
        consensus_available_for_plan = (
            sample["consensus_state"] == "provided" or can_generate_consensus
        )
        if can_generate_consensus:
            grouped = f"consensus/{name}.grouped.bam"
            plan.append(
                command_plan_entry(
                    f"{name}: group reads by UMI",
                    [
                        "fgbio",
                        "GroupReadsByUmi",
                        "-i",
                        raw,
                        "-o",
                        grouped,
                        "-s",
                        args.grouping_strategy,
                        "--edits",
                        str(args.umi_edits),
                        "-t",
                        args.umi_tag or "RX",
                    ],
                    outputs=[grouped],
                )
            )
            plan.append(
                command_plan_entry(
                    f"{name}: call molecular consensus reads",
                    [
                        "fgbio",
                        "CallMolecularConsensusReads",
                        "-i",
                        grouped,
                        "-o",
                        consensus,
                        "-M",
                        str(args.min_reads_per_molecule),
                    ],
                    outputs=[consensus],
                )
            )
        if not consensus_available_for_plan:
            continue
        plan.append(
            command_plan_entry(
                f"{name}: consensus flagstat",
                f"{shell_join(['samtools', 'flagstat', consensus])} > {shell_join([f'qc/{name}.consensus.flagstat.txt'])}",
                outputs=[f"qc/{name}.consensus.flagstat.txt"],
            )
        )
        if args.target_bed:
            plan.append(
                command_plan_entry(
                    f"{name}: target coverage",
                    f"{shell_join(['samtools', 'coverage', '-b', args.target_bed.expanduser().resolve(), consensus])} > {shell_join([f'qc/{name}.target_coverage.tsv'])}",
                    outputs=[f"qc/{name}.target_coverage.tsv"],
                )
            )
        mpileup = ["bcftools", "mpileup", "-Ou", "-f", reference]
        if args.target_bed:
            mpileup.extend(["-R", args.target_bed.expanduser().resolve()])
        mpileup.append(consensus)
        call = ["bcftools", "call", "-mv", "-Oz", "-o", f"variants/{name}.consensus.vcf.gz"]
        plan.append(
            command_plan_entry(
                f"{name}: consensus variant calling",
                f"{shell_join(mpileup)} | {shell_join(call)}",
                outputs=[f"variants/{name}.consensus.vcf.gz"],
            )
        )
        plan.append(
            command_plan_entry(
                f"{name}: index consensus VCF",
                ["bcftools", "index", "-t", f"variants/{name}.consensus.vcf.gz"],
            )
        )
        plan.append(
            command_plan_entry(
                f"{name}: variant stats",
                f"{shell_join(['bcftools', 'stats', f'variants/{name}.consensus.vcf.gz'])} > {shell_join([f'variants/{name}.bcftools_stats.txt'])}",
                outputs=[f"variants/{name}.bcftools_stats.txt"],
            )
        )
    return plan


def parse_first_int(value: str) -> int | None:
    try:
        return int(str(value).strip().split()[0])
    except (ValueError, IndexError):
        return None


def parse_flagstat(path: Path) -> dict[str, int | None]:
    metrics: dict[str, int | None] = {"total_reads": None, "mapped_reads": None}
    if not path.exists():
        return metrics
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if " in total " in line:
            metrics["total_reads"] = parse_first_int(line)
        elif " mapped (" in line and " mate mapped" not in line:
            metrics["mapped_reads"] = parse_first_int(line)
    return metrics


def parse_coverage(path: Path) -> dict[str, float | int | None]:
    metrics: dict[str, float | int | None] = {
        "mean_target_depth": None,
        "target_bases_covered": None,
    }
    if not path.exists():
        return metrics
    covered = 0
    depths: list[float] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            covbases = row.get("covbases") or row.get("coverage") or row.get("cov_bases")
            depth = row.get("meandepth") or row.get("mean_depth")
            try:
                if covbases is not None:
                    covered += int(float(covbases))
            except ValueError:
                pass
            try:
                if depth is not None:
                    depths.append(float(depth))
            except ValueError:
                pass
    metrics["target_bases_covered"] = covered if covered else None
    metrics["mean_target_depth"] = round(sum(depths) / len(depths), 3) if depths else None
    return metrics


def parse_bcftools_stats(path: Path) -> dict[str, int | None]:
    metrics: dict[str, int | None] = {
        "variant_records": None,
        "snp_count": None,
        "indel_count": None,
    }
    if not path.exists():
        return metrics
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("SN\t0\t"):
            continue
        fields = line.split("\t")
        if len(fields) < 4:
            continue
        label = fields[2]
        value = parse_first_int(fields[3])
        if label == "number of records:":
            metrics["variant_records"] = value
        elif label == "number of SNPs:":
            metrics["snp_count"] = value
        elif label == "number of indels:":
            metrics["indel_count"] = value
    return metrics


def parse_family_metrics(path: Path) -> dict[str, float | None]:
    metrics: dict[str, float | None] = {"median_family_size": None, "duplex_fraction": None}
    if not path.exists():
        return metrics
    sizes: list[float] = []
    duplex_total = 0.0
    total = 0.0
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            size_value = row.get("family_size") or row.get("size") or row.get("umi_family_size")
            count_value = row.get("count") or row.get("families") or row.get("n")
            family_type = (
                row.get("family_type") or row.get("type") or row.get("strand") or ""
            ).lower()
            try:
                size = float(size_value) if size_value not in {None, ""} else None
                count = float(count_value) if count_value not in {None, ""} else 1.0
            except ValueError:
                continue
            if size is not None:
                sizes.extend([size] * max(1, min(int(count), 10000)))
            total += count
            if "duplex" in family_type:
                duplex_total += count
    metrics["median_family_size"] = round(float(statistics.median(sizes)), 3) if sizes else None
    metrics["duplex_fraction"] = round(duplex_total / total, 4) if total else None
    return metrics


def summarize_postrun_artifacts(
    run_dir: Path, samples: list[dict[str, str]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sample in samples:
        name = sample["sample"]
        consensus_bam = sample["consensus_alignment"] or f"consensus/{name}.consensus.bam"
        consensus_path = Path(consensus_bam)
        if not consensus_path.is_absolute():
            consensus_path = run_dir / consensus_path
        flagstat = parse_flagstat(run_dir / "qc" / f"{name}.consensus.flagstat.txt")
        coverage = parse_coverage(run_dir / "qc" / f"{name}.target_coverage.tsv")
        stats = parse_bcftools_stats(run_dir / "variants" / f"{name}.bcftools_stats.txt")
        family_metrics = {"median_family_size": None, "duplex_fraction": None}
        for candidate in [
            run_dir / "qc" / f"{name}.family_size.tsv",
            run_dir / "qc" / f"{name}.umi_family_size.tsv",
            run_dir / "consensus" / f"{name}.family_size.tsv",
        ]:
            if candidate.exists():
                family_metrics = parse_family_metrics(candidate)
                break
        observed_files = [
            consensus_path.exists(),
            (run_dir / "qc" / f"{name}.consensus.flagstat.txt").exists(),
            (run_dir / "qc" / f"{name}.target_coverage.tsv").exists(),
            (run_dir / "variants" / f"{name}.bcftools_stats.txt").exists(),
        ]
        status = (
            "created"
            if all(observed_files[:2])
            else ("partial" if any(observed_files) else "not_executed")
        )
        notes = []
        if family_metrics["median_family_size"] is None:
            notes.append("family-size metrics not found")
        if coverage["mean_target_depth"] is None:
            notes.append("target coverage not found")
        if stats["variant_records"] is None:
            notes.append("variant stats not found")
        rows.append(
            {
                "sample": name,
                "consensus_state": sample["consensus_state"],
                "consensus_bam": str(consensus_path),
                "consensus_bam_exists": str(consensus_path.exists()).lower(),
                "total_consensus_reads": flagstat["total_reads"]
                if flagstat["total_reads"] is not None
                else "",
                "mapped_consensus_reads": flagstat["mapped_reads"]
                if flagstat["mapped_reads"] is not None
                else "",
                "mean_target_depth": coverage["mean_target_depth"]
                if coverage["mean_target_depth"] is not None
                else "",
                "target_bases_covered": coverage["target_bases_covered"]
                if coverage["target_bases_covered"] is not None
                else "",
                "variant_records": stats["variant_records"]
                if stats["variant_records"] is not None
                else "",
                "snp_count": stats["snp_count"] if stats["snp_count"] is not None else "",
                "indel_count": stats["indel_count"] if stats["indel_count"] is not None else "",
                "median_family_size": family_metrics["median_family_size"]
                if family_metrics["median_family_size"] is not None
                else "",
                "duplex_fraction": family_metrics["duplex_fraction"]
                if family_metrics["duplex_fraction"] is not None
                else "",
                "status": status,
                "notes": "; ".join(notes),
            }
        )
    write_tsv(run_dir / "qc" / "umi_postrun_summary.tsv", rows, UMI_POSTRUN_FIELDS)
    write_json(
        run_dir / "qc" / "umi_postrun_summary.json",
        {
            "samples": rows,
            "samples_with_consensus_bam": sum(
                1 for row in rows if row["consensus_bam_exists"] == "true"
            ),
            "samples_with_variant_stats": sum(1 for row in rows if row["variant_records"] != ""),
            "samples_with_family_metrics": sum(
                1 for row in rows if row["median_family_size"] != ""
            ),
        },
    )
    return rows


def first_existing_family_metrics(run_dir: Path, sample: str) -> Path:
    for candidate in [
        run_dir / "qc" / f"{sample}.family_size.tsv",
        run_dir / "qc" / f"{sample}.umi_family_size.tsv",
        run_dir / "consensus" / f"{sample}.family_size.tsv",
    ]:
        if candidate.exists():
            return candidate
    return run_dir / "qc" / f"{sample}.family_size.tsv"


def write_molecular_evidence_contract(
    run_dir: Path,
    validation: dict[str, Any],
    samples: list[dict[str, str]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sample in samples:
        name = sample["sample"]
        consensus_bam = sample["consensus_alignment"] or f"consensus/{name}.consensus.bam"
        consensus_path = Path(consensus_bam)
        if not consensus_path.is_absolute():
            consensus_path = run_dir / consensus_path
        family_metrics = first_existing_family_metrics(run_dir, name)
        variant_vcf = run_dir / "variants" / f"{name}.consensus.vcf.gz"
        variant_stats = run_dir / "variants" / f"{name}.bcftools_stats.txt"
        hotspot_vcf = str(validation.get("hotspot_vcf") or "")
        notes: list[str] = []
        if sample["consensus_state"] == "needs_generation":
            notes.append("consensus BAM must be generated before variant evidence review")
        elif sample["consensus_state"] == "review_contract_only":
            notes.append(
                "raw BAM lacks RX/MQ tags; treat as a review-contract input or start from raw UMI FASTQs before evidence review"
            )
        if not family_metrics.exists():
            notes.append("family-size or molecule-support metrics not found")
        if not variant_stats.exists():
            notes.append("variant stats not found")
        if args.umi_mode == "duplex" and not family_metrics.exists():
            notes.append("duplex fraction cannot be reviewed without family metrics")
        if not hotspot_vcf:
            notes.append("hotspot VCF not provided")
        evidence_ready = (
            consensus_path.exists()
            and family_metrics.exists()
            and variant_vcf.exists()
            and variant_stats.exists()
        )
        rows.append(
            {
                "sample": name,
                "umi_mode": validation.get("umi_mode"),
                "consensus_state": sample["consensus_state"],
                "min_af": validation.get("min_af"),
                "min_reads_per_molecule": args.min_reads_per_molecule,
                "consensus_bam": str(consensus_path),
                "consensus_bam_exists": str(consensus_path.exists()).lower(),
                "family_metrics_path": str(family_metrics),
                "family_metrics_exists": str(family_metrics.exists()).lower(),
                "variant_vcf": str(variant_vcf),
                "variant_vcf_exists": str(variant_vcf.exists()).lower(),
                "variant_stats_path": str(variant_stats),
                "variant_stats_exists": str(variant_stats.exists()).lower(),
                "hotspot_vcf": hotspot_vcf,
                "hotspot_review": "available" if hotspot_vcf else "not_configured",
                "duplex_review": "required" if args.umi_mode == "duplex" else "optional",
                "low_af_review_status": "ready_for_review" if evidence_ready else "planned",
                "notes": "; ".join(notes),
            }
        )
    write_tsv(run_dir / "qc" / "umi_molecular_evidence_contract.tsv", rows, UMI_EVIDENCE_FIELDS)
    write_json(
        run_dir / "qc" / "umi_molecular_evidence_contract.json",
        {
            "samples": rows,
            "sample_count": len(rows),
            "ready_for_review_count": sum(
                1 for row in rows if row["low_af_review_status"] == "ready_for_review"
            ),
            "duplex_review_required_count": sum(
                1 for row in rows if row["duplex_review"] == "required"
            ),
            "hotspot_review_available_count": sum(
                1 for row in rows if row["hotspot_review"] == "available"
            ),
        },
    )
    return rows


def write_outputs(
    run_dir: Path,
    validation: dict[str, Any],
    samples: list[dict[str, str]],
    plan: list[dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    write_tsv(run_dir / "validation" / "samples.normalized.tsv", samples, UMI_SAMPLE_FIELDS)
    write_json(
        run_dir / "qc" / "umi_consensus_plan.json",
        {
            "umi_mode": validation.get("umi_mode"),
            "umi_tag": validation.get("umi_tag"),
            "min_af": validation.get("min_af"),
            "samples_needing_consensus": [
                row["sample"] for row in samples if row["consensus_state"] == "needs_generation"
            ],
            "review_contract_only_samples": [
                row["sample"]
                for row in samples
                if row.get("fgbio_readiness") == "review_contract_only"
            ],
            "fgbio_ready_samples": [
                row["sample"] for row in samples if row.get("fgbio_readiness") == "ready"
            ],
            "warnings": validation.get("warnings", []),
        },
    )
    summarize_postrun_artifacts(run_dir, samples)
    write_molecular_evidence_contract(run_dir, validation, samples, args)
    write_json(run_dir / "workflow" / "umi_panel_command_plan.json", {"commands": plan})
    write_command_script(run_dir / "commands.sh", [item["command"] for item in plan])


def execute_plan(run_dir: Path, plan: list[dict[str, Any]]) -> dict[str, Any]:
    for dirname in ["variants", "qc", "logs", "consensus"]:
        (run_dir / dirname).mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"ok": True, "steps": []}
    for index, item in enumerate(plan, start=1):
        step = run_cmd(["bash", "-c", item["command"]], run_dir, timeout=7200)
        safe = item["name"].replace(":", "").replace(" ", "_").replace("/", "_")
        write_json(run_dir / "logs" / f"{index:02d}_{safe}.json", step)
        result["steps"].append({"name": item["name"], "ok": step.get("ok")})
        result["ok"] = bool(result["ok"] and step.get("ok"))
        if not step.get("ok"):
            break
    return result


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# UMI Panel Variant Run Summary",
        "",
        f"Status: `{status}`",
        f"Samples parsed: `{validation.get('sample_count', 0)}`",
        f"UMI mode: `{validation.get('umi_mode')}`",
        f"Minimum allele fraction goal: `{validation.get('min_af')}`",
        "",
        "## Key Artifacts",
        "",
        "- `validation/samples.normalized.tsv`",
        "- `workflow/umi_panel_command_plan.json`",
        "- `qc/umi_consensus_plan.json`",
        "- `qc/umi_postrun_summary.tsv` and `qc/umi_postrun_summary.json`",
        "- `qc/umi_molecular_evidence_contract.tsv` and `qc/umi_molecular_evidence_contract.json`",
        "- `consensus/*.bam` and `variants/*.consensus.vcf.gz` when executed",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `visualizations/index.html` and `visualizations/visualization_manifest.json`",
        "- `notebooks/vcf_review.marimo.py` when output VCF/gVCF artifacts are present",
        "- `run_manifest.json` and `artifact_index.json`",
        "",
        "## Guardrails",
        "",
        "- Generic recalibrated BAMs without RX and MQ tags are review-contract fixtures; do not treat them as end-to-end fgbio inputs.",
        "- Raw read depth, consensus depth, and unique molecular depth must be interpreted separately.",
        "- Low-AF calls require molecule-count, strand/duplex, and hotspot/artifact review before biological interpretation.",
        "",
    ]
    if validation.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {item}" for item in validation["warnings"])
        lines.append("")
    lines.extend(ngs_resource_gate.resource_summary_lines(resource_plan))
    if validation.get("errors"):
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {item}" for item in validation["errors"])
    write_text(run_dir / "summary.md", "\n".join(lines) + "\n")


def write_visuals(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> dict[str, str]:
    entries = [
        artifact_entry(
            artifact_id="samples",
            title="UMI Panel Samples",
            path="validation/samples.normalized.tsv",
            kind="table",
            status="created",
            description="Normalized sample table with raw/consensus alignment state.",
        ),
        artifact_entry(
            artifact_id="consensus_plan",
            title="Consensus Plan",
            path="qc/umi_consensus_plan.json",
            kind="json",
            status="created",
            description="UMI grouping, consensus, and low-frequency calling settings.",
        ),
        artifact_entry(
            artifact_id="postrun_summary",
            title="UMI Post-run Summary",
            path="qc/umi_postrun_summary.tsv",
            kind="table",
            status="created",
            description="Consensus-read, target-coverage, variant-count, and family-size summary parsed from run artifacts.",
        ),
        artifact_entry(
            artifact_id="molecular_evidence_contract",
            title="Molecular Evidence Contract",
            path="qc/umi_molecular_evidence_contract.tsv",
            kind="table",
            status="created",
            description="Per-sample evidence requirements for low-AF review: consensus BAM, family metrics, variant stats, hotspot review, and duplex review.",
        ),
        artifact_entry(
            artifact_id="command_plan",
            title="UMI Panel Command Plan",
            path="workflow/umi_panel_command_plan.json",
            kind="json",
            status="created",
            description="Executable consensus and consensus-BAM variant-calling commands.",
        ),
    ]
    review_outputs = add_vcf_review_notebook_entry(
        run_dir,
        entries,
        title="UMI Panel VCF Review",
        table_items=[
            ("Resolved Sample Table", "validation/samples.normalized.tsv"),
            ("UMI Post-run Summary", "qc/umi_postrun_summary.tsv"),
            ("Molecular Evidence Contract", "qc/umi_molecular_evidence_contract.tsv"),
        ],
        object_items=[("Run Summary", "summary.md")],
    )
    entries.extend(ngs_resource_gate.resource_visual_entries(resource_plan))
    index = write_visualization_index(
        run_dir,
        title="UMI Panel Variant Review",
        description="Review surface for molecular consensus, panel coverage, and low-frequency variant calling artifacts.",
        entries=entries,
        notes=[
            *validation.get("warnings", []),
            *ngs_resource_gate.resource_messages(resource_plan),
        ],
        analysis_intent="real_analysis" if status != "blocked" else "blocked_preflight",
        provenance_summary={
            "status": status,
            "sample_count": validation.get("sample_count", 0),
            "resource_plan_ok": validation.get("resource_plan_ok"),
        },
    )
    return {
        "visualization_index": str(index.relative_to(run_dir)),
        "visualization_manifest": "visualizations/visualization_manifest.json",
        **review_outputs,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-sheet", type=Path, required=True)
    parser.add_argument("--reference-fasta", type=Path, required=True)
    parser.add_argument("--target-bed", type=Path)
    parser.add_argument("--hotspot-vcf", type=Path)
    parser.add_argument("--umi-mode", default="single", choices=["single", "duplex", "unknown"])
    parser.add_argument("--umi-tag", default="RX")
    parser.add_argument(
        "--grouping-strategy",
        default="adjacency",
        choices=["identity", "edit", "adjacency", "paired"],
    )
    parser.add_argument("--umi-edits", type=int, default=1)
    parser.add_argument("--min-reads-per-molecule", type=int, default=2)
    parser.add_argument("--min-af", type=float, default=0.005)
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
        help="Treat missing registered reference bundles as blocking for this direct runner.",
    )
    parser.add_argument(
        "--skip-resource-plan",
        action="store_true",
        help="Skip registered reference bundle readiness checks.",
    )
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--run-id", default=slug_timestamp("dna-umi-panel-variants"))
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def serializable_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()
    }


def main() -> int:
    args = parse_args()
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    input_validation, samples = validate_inputs(args)
    resource_plan = ngs_resource_gate.write_pipeline_resource_plan(
        run_dir=run_dir,
        pipeline="dna_umi_panel_variants",
        genome_build=args.genome_build,
        bundle_roots=args.bundle_root,
        include_optional=args.include_optional_resources,
        include_checksums=args.resource_checksums,
        skip=args.skip_resource_plan,
        required=args.require_resource_plan,
    )
    validation = ngs_resource_gate.merge_resource_status(
        input_validation, resource_plan, required=args.require_resource_plan
    )
    needs_consensus = any(row["consensus_state"] == "needs_generation" for row in samples)
    required_tools = (
        (["samtools", "bcftools"] + (["fgbio"] if needs_consensus else [])) if args.execute else []
    )
    optional_tools = [
        name for name in ["samtools", "bcftools", "fgbio", "gatk"] if name not in required_tools
    ]
    tool_status = tool_preflight(required_tools, optional=optional_tools)
    plan = build_plan(args, samples)
    write_json(run_dir / "config.json", {**serializable_args(args), "run_dir": str(run_dir)})
    write_json(run_dir / "validation" / "input_validation_summary.json", input_validation)
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions(
            {
                "fgbio": ["fgbio", "--version"],
                "samtools": ["samtools", "--version"],
                "bcftools": ["bcftools", "--version"],
            }
        ),
    )
    write_outputs(run_dir, validation, samples, plan, args)
    dry_run = {
        "ok": validation["ok"] and (tool_status["ok"] if args.execute else True),
        "detail": "input, UMI, target, and tool validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    status = "blocked" if not dry_run["ok"] else "validated"
    execution = None
    if args.execute and dry_run["ok"]:
        execution = execute_plan(run_dir, plan)
        status = "completed" if execution.get("ok") else "failed"
        summarize_postrun_artifacts(run_dir, samples)
        write_molecular_evidence_contract(run_dir, validation, samples, args)
    visuals = write_visuals(run_dir, status, validation, resource_plan)
    resource_outputs = ngs_resource_gate.resource_output_paths(resource_plan)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="dna_umi_panel_variants",
        workflow="local_light_umi_consensus_panel",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "reference_fasta": str(args.reference_fasta.expanduser().resolve()),
            "target_bed": str(args.target_bed.expanduser().resolve()) if args.target_bed else None,
            "hotspot_vcf": str(args.hotspot_vcf.expanduser().resolve())
            if args.hotspot_vcf
            else None,
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "sample_table": "validation/samples.normalized.tsv",
            "command_plan": "workflow/umi_panel_command_plan.json",
            "consensus_plan": "qc/umi_consensus_plan.json",
            "postrun_summary": "qc/umi_postrun_summary.tsv",
            "postrun_summary_json": "qc/umi_postrun_summary.json",
            "molecular_evidence_contract": "qc/umi_molecular_evidence_contract.tsv",
            "molecular_evidence_contract_json": "qc/umi_molecular_evidence_contract.json",
            "consensus_bam_glob": "consensus/*.bam",
            "vcf_glob": "variants/*.consensus.vcf.gz",
            **resource_outputs,
            **visuals,
        },
        method={
            "umi_mode": args.umi_mode,
            "umi_tag": args.umi_tag,
            "grouping_strategy": args.grouping_strategy,
            "min_reads_per_molecule": args.min_reads_per_molecule,
            "min_af": args.min_af,
            "resource_plan": resource_plan,
        },
        audit={"resource_readiness": resource_plan} if resource_plan else None,
        review_bundle=visuals,
    )
    write_summary(run_dir, status, validation, resource_plan)
    write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))
    print(run_dir)
    return 1 if status in {"blocked", "failed"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
