#!/usr/bin/env python3
"""Run BAM-to-VCF DNA variant calling with samtools and bcftools."""

from __future__ import annotations

import argparse
import csv
import json
import shlex
import statistics
from pathlib import Path
from typing import Any

import ngs_resource_gate
from ngs_run_utils import (
    build_artifact_index,
    run_cmd,
    run_cmd_stdout_to_file,
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
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "dna_variant_calling"
MQ_INFO_INTEGER_HEADER = (
    '##INFO=<ID=MQ,Number=1,Type=Integer,Description="Average mapping quality">'
)
MQ_INFO_FLOAT_HEADER = '##INFO=<ID=MQ,Number=1,Type=Float,Description="Average mapping quality">'
DEFAULT_ANNOTATION_INFO_TAGS = ["AF", "AC", "AN"]
DEFAULT_CALLABLE_MIN_DEPTH = 10


def detect_delimiter(path: Path) -> str:
    if path.suffix.lower() in {".tsv", ".tab"}:
        return "\t"
    return ","


def read_samples(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=detect_delimiter(path))
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
        return rows, list(reader.fieldnames or [])


def load_reference_contigs(reference: Path) -> dict[str, int]:
    contigs: dict[str, int] = {}
    fai = Path(str(reference) + ".fai")
    if not fai.exists():
        return contigs
    with fai.open("r", encoding="utf-8") as handle:
        for line in handle:
            fields = line.rstrip().split("\t")
            if len(fields) >= 2:
                contigs[fields[0]] = int(fields[1])
    return contigs


def parse_region(region: str) -> tuple[str, int, int]:
    if ":" not in region:
        raise ValueError(f"region must use contig:start-end syntax, got: {region}")
    contig, coords = region.split(":", 1)
    if "-" in coords:
        start_s, end_s = coords.split("-", 1)
    else:
        start_s = coords
        end_s = coords
    start = int(start_s.replace(",", ""))
    end = int(end_s.replace(",", ""))
    if start < 1 or end < 1 or end < start:
        raise ValueError(f"region has invalid coordinates: {region}")
    return contig, start, end


def alt_contig_name(contig: str, available: dict[str, int]) -> str | None:
    candidates = [f"chr{contig}", contig.removeprefix("chr")]
    for item in candidates:
        if item != contig and item in available:
            return item
    return None


def normalize_region(region: str | None, reference_contigs: dict[str, int]) -> dict[str, Any]:
    if not region:
        return {"requested": None, "normalized": None, "errors": [], "warnings": []}
    errors: list[str] = []
    warnings: list[str] = []
    try:
        contig, start, end = parse_region(region)
    except ValueError as exc:
        return {"requested": region, "normalized": None, "errors": [str(exc)], "warnings": []}
    if contig not in reference_contigs:
        suggestion = alt_contig_name(contig, reference_contigs)
        if suggestion:
            errors.append(
                f"region contig '{contig}' was not found in the reference; did you mean '{suggestion}:{start}-{end}'?"
            )
        else:
            errors.append(f"region contig '{contig}' was not found in the reference")
        return {"requested": region, "normalized": None, "errors": errors, "warnings": warnings}
    contig_length = reference_contigs[contig]
    if start > contig_length:
        errors.append(f"region start {start} exceeds contig length {contig_length} for {contig}")
    if end > contig_length:
        warnings.append(
            f"region end {end} exceeds contig length {contig_length} for {contig}; clipping to {contig_length}"
        )
        end = contig_length
    normalized = f"{contig}:{start}-{end}" if not errors else None
    return {
        "requested": region,
        "normalized": normalized,
        "contig": contig,
        "start": start,
        "end": end,
        "contig_length": contig_length,
        "errors": errors,
        "warnings": warnings,
    }


def validate_inputs(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, str]]]:
    sample_sheet = args.sample_sheet.expanduser().resolve()
    reference = args.reference_fasta.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    normalized: list[dict[str, str]] = []
    columns: list[str] = []

    if not sample_sheet.exists():
        errors.append(f"sample sheet does not exist: {sample_sheet}")
        rows: list[dict[str, str]] = []
    else:
        try:
            rows, columns = read_samples(sample_sheet)
        except Exception as exc:  # pragma: no cover - defensive parse guard
            rows = []
            errors.append(f"failed to parse sample sheet {sample_sheet}: {exc}")

    if not reference.exists():
        errors.append(f"reference FASTA does not exist: {reference}")
    reference_contigs = load_reference_contigs(reference)
    if not reference_contigs:
        warnings.append(
            f"reference FASTA index is missing and may be created by samtools faidx: {reference}.fai"
        )
    region_summary = (
        normalize_region(args.region, reference_contigs)
        if reference.exists()
        else {"requested": args.region, "normalized": None, "errors": [], "warnings": []}
    )
    errors.extend(region_summary.get("errors", []))
    warnings.extend(region_summary.get("warnings", []))
    if args.annotation_vcf:
        annotation_vcf = args.annotation_vcf.expanduser().resolve()
        if not annotation_vcf.exists():
            errors.append(f"annotation VCF does not exist: {annotation_vcf}")
        if (
            not (Path(str(annotation_vcf) + ".tbi")).exists()
            and not (Path(str(annotation_vcf) + ".csi")).exists()
        ):
            warnings.append(
                f"annotation VCF index is missing and may be required by bcftools annotate: {annotation_vcf}.tbi"
            )
    sample_names: set[str] = set()
    duplicate_names: set[str] = set()
    for row_index, row in enumerate(rows, start=2):
        sample = row.get("sample") or row.get("sample_id") or f"row_{row_index}"
        bam_raw = row.get("bam") or row.get("cram") or ""
        if sample in sample_names:
            duplicate_names.add(sample)
        sample_names.add(sample)
        if not bam_raw:
            errors.append(f"row {row_index}: bam or cram column is required")
            continue
        bam = Path(bam_raw).expanduser()
        if not bam.is_absolute():
            bam = sample_sheet.parent / bam
        bam = bam.resolve()
        if not bam.exists():
            errors.append(f"row {row_index}: alignment file does not exist: {bam}")
        if bam.suffix == ".bam" and not (Path(str(bam) + ".bai")).exists():
            warnings.append(
                f"row {row_index}: BAM index is missing and may be created by samtools index: {bam}.bai"
            )
        normalized.append({"sample": sample, "alignment": str(bam), "row_index": str(row_index)})

    if not normalized:
        errors.append("no usable alignment rows found")
    if duplicate_names:
        warnings.append(
            f"duplicate sample names detected in sample sheet: {', '.join(sorted(duplicate_names))}"
        )
    validation = {
        "ok": not errors,
        "sample_sheet": str(sample_sheet),
        "reference_fasta": str(reference),
        "region": region_summary.get("normalized") or args.region,
        "region_requested": args.region,
        "region_summary": region_summary,
        "columns": columns,
        "sample_count": len(normalized),
        "run_class": "targeted_region_check"
        if region_summary.get("normalized")
        else "alignment_wide_local_light",
        "errors": errors,
        "warnings": warnings,
    }
    return validation, normalized


def write_normalized_samples(run_dir: Path, rows: list[dict[str, str]]) -> None:
    path = run_dir / "validation" / "samples.normalized.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["sample", "alignment", "row_index"], delimiter="\t"
        )
        writer.writeheader()
        writer.writerows(rows)


def bcftools_call_command(
    reference: Path, alignment: Path, output: Path, region: str | None
) -> str:
    mpileup = ["bcftools", "mpileup", "-Ou", "-f", str(reference)]
    if region:
        mpileup.extend(["-r", region])
    mpileup.append(str(alignment))
    call = ["bcftools", "call", "-mv", "-Oz", "-o", str(output)]
    return f"{shlex.join(mpileup)} | {shlex.join(call)}"


def detect_annotation_columns(run_dir: Path, annotation_vcf: Path, requested: str | None) -> str:
    if requested:
        return requested
    tags_to_probe = "|".join(DEFAULT_ANNOTATION_INFO_TAGS)
    probe = run_cmd(
        [
            "bash",
            "-lc",
            f"bcftools view -h {shlex.quote(str(annotation_vcf))} | rg '^##INFO=<ID=({tags_to_probe}),'",
        ],
        run_dir,
        timeout=600,
    )
    if not probe.get("ok"):
        return "ID"
    available_tags = set()
    for line in str(probe.get("stdout_tail", "")).splitlines():
        if line.startswith("##INFO=<ID="):
            tag = line.split("##INFO=<ID=", 1)[1].split(",", 1)[0]
            available_tags.add(tag)
    selected = ["ID"]
    selected.extend(f"INFO/{tag}" for tag in DEFAULT_ANNOTATION_INFO_TAGS if tag in available_tags)
    return ",".join(selected)


def annotate_vcf(
    run_dir: Path,
    sample: str,
    input_vcf: Path,
    annotation_vcf: Path | None,
    annotation_columns: str | None,
) -> tuple[Path, dict[str, Any]]:
    if not annotation_vcf:
        return input_vcf, {"ok": True, "changed": False, "reason": "annotation not requested"}
    columns = detect_annotation_columns(run_dir, annotation_vcf, annotation_columns)
    output_vcf = input_vcf.parent / f"{input_vcf.name.removesuffix('.vcf.gz')}.annotated.vcf.gz"
    annotate = run_cmd(
        [
            "bcftools",
            "annotate",
            "-a",
            str(annotation_vcf),
            "-c",
            columns,
            "--pair-logic",
            "exact",
            "-O",
            "z",
            "-o",
            str(output_vcf),
            str(input_vcf),
        ],
        run_dir,
        timeout=3600,
    )
    result: dict[str, Any] = {
        "ok": bool(annotate.get("ok")),
        "changed": bool(annotate.get("ok")),
        "reason": "annotated from resource VCF"
        if annotate.get("ok")
        else "bcftools annotate failed",
        "annotation_vcf": str(annotation_vcf),
        "annotation_columns": columns,
        "annotate": annotate,
    }
    return (output_vcf if annotate.get("ok") else input_vcf), result


def normalize_mq_header(run_dir: Path, sample: str, vcf: Path) -> dict[str, Any]:
    """Rewrite INFO/MQ as Float so bcftools stats does not warn on the emitted header."""
    header = run_cmd(["bcftools", "view", "-h", str(vcf)], run_dir, timeout=600)
    result: dict[str, Any] = {"ok": bool(header.get("ok")), "changed": False}
    if not header.get("ok"):
        result["reason"] = "failed to read VCF header"
        return result

    header_lines = [
        line
        for line in str(header.get("stdout_tail", "")).splitlines()
        if line.startswith(("##", "#CHROM"))
    ]
    header_text = "\n".join(header_lines) + ("\n" if header_lines else "")
    if MQ_INFO_INTEGER_HEADER not in header_text:
        result["reason"] = "no MQ Integer header present"
        return result

    normalized_header = header_text.replace(MQ_INFO_INTEGER_HEADER, MQ_INFO_FLOAT_HEADER)
    header_path = run_dir / "logs" / f"{sample}.mq_header.normalized.hdr"
    temp_vcf = vcf.parent / f"{vcf.name.removesuffix('.vcf.gz')}.reheader.vcf.gz"
    write_text(header_path, normalized_header)
    reheader = run_cmd(
        ["bcftools", "reheader", "-h", str(header_path), "-o", str(temp_vcf), str(vcf)],
        run_dir,
        timeout=600,
    )
    result["reheader"] = reheader
    if not reheader.get("ok"):
        result["ok"] = False
        result["reason"] = "bcftools reheader failed"
        return result

    temp_vcf.replace(vcf)
    result["changed"] = True
    result["reason"] = "rewrote INFO/MQ header to Float"
    return result


def summarize_depth_file(depth_path: Path, callable_min_depth: int) -> dict[str, Any]:
    positions = 0
    callable_positions = 0
    zero_depth_positions = 0
    depth_values: list[int] = []
    for line in depth_path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        depth = int(fields[2])
        positions += 1
        depth_values.append(depth)
        if depth >= callable_min_depth:
            callable_positions += 1
        if depth == 0:
            zero_depth_positions += 1
    mean_depth = sum(depth_values) / positions if positions else 0.0
    median_depth = statistics.median(depth_values) if depth_values else 0.0
    return {
        "positions": positions,
        "callable_min_depth": callable_min_depth,
        "callable_positions": callable_positions,
        "callable_fraction": (callable_positions / positions) if positions else 0.0,
        "zero_depth_positions": zero_depth_positions,
        "mean_depth": round(mean_depth, 3),
        "median_depth": round(float(median_depth), 3),
        "max_depth": max(depth_values) if depth_values else 0,
    }


def parse_variant_stats(stats_text: str) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "record_count": None,
        "snp_count": None,
        "indel_count": None,
        "interpretation": "variant stats unavailable",
    }
    for line in stats_text.splitlines():
        if not line.startswith("SN\t0\t"):
            continue
        _, _, key, value = line.split("\t", 3)
        value_int = int(value)
        if key == "number of records:":
            summary["record_count"] = value_int
        elif key == "number of SNPs:":
            summary["snp_count"] = value_int
        elif key == "number of indels:":
            summary["indel_count"] = value_int
    record_count = summary.get("record_count")
    if record_count == 0:
        summary["interpretation"] = "no variant records were emitted in the queried region"
    elif isinstance(record_count, int) and record_count > 0:
        summary["interpretation"] = "variant records were emitted in the queried region"
    return summary


def run_region_qc(
    run_dir: Path,
    sample: str,
    alignment: Path,
    region: str | None,
    callable_min_depth: int,
) -> dict[str, Any]:
    qc_dir = run_dir / "qc"
    coverage_path = qc_dir / f"{sample}.coverage.tsv"
    coverage_cmd = ["samtools", "coverage"]
    if region:
        coverage_cmd.extend(["-r", region])
    coverage_cmd.append(str(alignment))
    coverage = run_cmd_stdout_to_file(coverage_cmd, run_dir, coverage_path, timeout=600)

    depth_summary: dict[str, Any] = {
        "positions": 0,
        "callable_min_depth": callable_min_depth,
        "callable_positions": 0,
        "callable_fraction": 0.0,
        "zero_depth_positions": 0,
        "mean_depth": 0.0,
        "median_depth": 0.0,
        "max_depth": 0,
        "note": "per-base depth was omitted because no region was provided",
    }
    depth_log: dict[str, Any] = {"ok": True, "skipped": True, "reason": depth_summary["note"]}
    if region:
        depth_path = qc_dir / f"{sample}.depth.tsv"
        depth_cmd = ["samtools", "depth", "-aa", "-r", region, str(alignment)]
        depth_log = run_cmd_stdout_to_file(depth_cmd, run_dir, depth_path, timeout=600)
        if depth_log.get("ok"):
            depth_summary = summarize_depth_file(depth_path, callable_min_depth)

    return {"coverage": coverage, "depth": depth_log, "callability": depth_summary}


def filter_vcf(
    run_dir: Path,
    input_vcf: Path,
    min_qual: float | None,
    min_site_dp: int | None,
) -> tuple[Path, dict[str, Any]]:
    expressions: list[str] = []
    if min_qual is not None:
        expressions.append(f"QUAL<{min_qual}")
    if min_site_dp is not None:
        expressions.append(f"INFO/DP<{min_site_dp}")
    if not expressions:
        return input_vcf, {"ok": True, "changed": False, "reason": "filtering not requested"}
    output_vcf = input_vcf.parent / f"{input_vcf.name.removesuffix('.vcf.gz')}.filtered.vcf.gz"
    expr = " || ".join(expressions)
    result = run_cmd(
        [
            "bcftools",
            "filter",
            "-s",
            "LOW_SUPPORT",
            "-e",
            expr,
            "-O",
            "z",
            "-o",
            str(output_vcf),
            str(input_vcf),
        ],
        run_dir,
        timeout=3600,
    )
    payload = {
        "ok": bool(result.get("ok")),
        "changed": bool(result.get("ok")),
        "reason": "soft-filtered VCF emitted" if result.get("ok") else "bcftools filter failed",
        "expression": expr,
        "filter": result,
    }
    return (output_vcf if result.get("ok") else input_vcf), payload


def write_commands(run_dir: Path, args: argparse.Namespace, rows: list[dict[str, str]]) -> None:
    reference = args.reference_fasta.expanduser().resolve()
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        shlex.join(["samtools", "faidx", str(reference)]),
    ]
    for row in rows:
        sample = row["sample"]
        alignment = Path(row["alignment"])
        lines.append(shlex.join(["samtools", "quickcheck", "-v", str(alignment)]))
        lines.append(
            shlex.join(["samtools", "flagstat", str(alignment)]) + f" > qc/{sample}.flagstat.txt"
        )
        lines.append(
            shlex.join(["samtools", "idxstats", str(alignment)]) + f" > qc/{sample}.idxstats.tsv"
        )
        lines.append(
            shlex.join(["samtools", "coverage", "-r", args.region, str(alignment)])
            + f" > qc/{sample}.coverage.tsv"
            if args.region
            else shlex.join(["samtools", "coverage", str(alignment)])
            + f" > qc/{sample}.coverage.tsv"
        )
        if args.region:
            lines.append(
                shlex.join(["samtools", "depth", "-aa", "-r", args.region, str(alignment)])
                + f" > qc/{sample}.depth.tsv"
            )
        lines.append(
            bcftools_call_command(
                reference, alignment, Path("variants") / f"{sample}.vcf.gz", args.region
            )
        )
        lines.append(
            f"# The runner may normalize INFO/MQ in variants/{sample}.vcf.gz before bcftools stats."
        )
        if args.annotation_vcf:
            annotation_vcf = args.annotation_vcf.expanduser().resolve()
            columns = detect_annotation_columns(run_dir, annotation_vcf, args.annotation_columns)
            lines.append(shlex.join(["bcftools", "index", "-t", f"variants/{sample}.vcf.gz"]))
            lines.append(
                shlex.join(
                    [
                        "bcftools",
                        "annotate",
                        "-a",
                        str(annotation_vcf),
                        "-c",
                        columns,
                        "--pair-logic",
                        "exact",
                        "-O",
                        "z",
                        "-o",
                        f"variants/{sample}.annotated.vcf.gz",
                        f"variants/{sample}.vcf.gz",
                    ]
                )
            )
            lines.append(
                shlex.join(["bcftools", "index", "-t", f"variants/{sample}.annotated.vcf.gz"])
            )
            if args.filter_min_qual is not None or args.filter_min_site_dp is not None:
                expr = " || ".join(
                    [
                        item
                        for item in [
                            f"QUAL<{args.filter_min_qual}"
                            if args.filter_min_qual is not None
                            else None,
                            f"INFO/DP<{args.filter_min_site_dp}"
                            if args.filter_min_site_dp is not None
                            else None,
                        ]
                        if item
                    ]
                )
                lines.append(
                    shlex.join(
                        [
                            "bcftools",
                            "filter",
                            "-s",
                            "LOW_SUPPORT",
                            "-e",
                            expr,
                            "-O",
                            "z",
                            "-o",
                            f"variants/{sample}.annotated.filtered.vcf.gz",
                            f"variants/{sample}.annotated.vcf.gz",
                        ]
                    )
                )
                lines.append(
                    shlex.join(
                        ["bcftools", "index", "-t", f"variants/{sample}.annotated.filtered.vcf.gz"]
                    )
                )
                lines.append(
                    shlex.join(
                        ["bcftools", "stats", f"variants/{sample}.annotated.filtered.vcf.gz"]
                    )
                    + f" > variants/{sample}.filtered.bcftools_stats.txt"
                )
            else:
                lines.append(
                    shlex.join(["bcftools", "stats", f"variants/{sample}.annotated.vcf.gz"])
                    + f" > variants/{sample}.bcftools_stats.txt"
                )
        else:
            lines.append(shlex.join(["bcftools", "index", "-t", f"variants/{sample}.vcf.gz"]))
            if args.filter_min_qual is not None or args.filter_min_site_dp is not None:
                expr = " || ".join(
                    [
                        item
                        for item in [
                            f"QUAL<{args.filter_min_qual}"
                            if args.filter_min_qual is not None
                            else None,
                            f"INFO/DP<{args.filter_min_site_dp}"
                            if args.filter_min_site_dp is not None
                            else None,
                        ]
                        if item
                    ]
                )
                lines.append(
                    shlex.join(
                        [
                            "bcftools",
                            "filter",
                            "-s",
                            "LOW_SUPPORT",
                            "-e",
                            expr,
                            "-O",
                            "z",
                            "-o",
                            f"variants/{sample}.filtered.vcf.gz",
                            f"variants/{sample}.vcf.gz",
                        ]
                    )
                )
                lines.append(
                    shlex.join(["bcftools", "index", "-t", f"variants/{sample}.filtered.vcf.gz"])
                )
                lines.append(
                    shlex.join(["bcftools", "stats", f"variants/{sample}.filtered.vcf.gz"])
                    + f" > variants/{sample}.filtered.bcftools_stats.txt"
                )
            else:
                lines.append(
                    shlex.join(["bcftools", "stats", f"variants/{sample}.vcf.gz"])
                    + f" > variants/{sample}.bcftools_stats.txt"
                )
    write_text(run_dir / "commands.sh", "\n".join(lines) + "\n")


def execute(run_dir: Path, args: argparse.Namespace, rows: list[dict[str, str]]) -> dict[str, Any]:
    reference = args.reference_fasta.expanduser().resolve()
    annotation_vcf = args.annotation_vcf.expanduser().resolve() if args.annotation_vcf else None
    results: dict[str, Any] = {"ok": True, "steps": []}
    (run_dir / "qc").mkdir(parents=True, exist_ok=True)
    (run_dir / "variants").mkdir(parents=True, exist_ok=True)
    if not (Path(str(reference) + ".fai")).exists():
        faidx = run_cmd(["samtools", "faidx", str(reference)], run_dir, timeout=600)
        write_json(run_dir / "logs" / "samtools_faidx.json", faidx)
        results["steps"].append({"name": "samtools_faidx", "ok": faidx.get("ok")})
        results["ok"] = bool(results["ok"] and faidx.get("ok"))

    for row in rows:
        sample = row["sample"]
        alignment = Path(row["alignment"])
        quickcheck = run_cmd(["samtools", "quickcheck", "-v", str(alignment)], run_dir, timeout=300)
        write_json(run_dir / "logs" / f"{sample}.quickcheck.json", quickcheck)
        flagstat = run_cmd(["samtools", "flagstat", str(alignment)], run_dir, timeout=600)
        write_json(run_dir / "logs" / f"{sample}.flagstat.json", flagstat)
        write_text(run_dir / "qc" / f"{sample}.flagstat.txt", flagstat.get("stdout_tail", ""))
        idxstats = run_cmd(["samtools", "idxstats", str(alignment)], run_dir, timeout=600)
        write_json(run_dir / "logs" / f"{sample}.idxstats.json", idxstats)
        write_text(run_dir / "qc" / f"{sample}.idxstats.tsv", idxstats.get("stdout_tail", ""))
        region_qc = run_region_qc(run_dir, sample, alignment, args.region, args.callable_min_depth)
        write_json(run_dir / "logs" / f"{sample}.coverage.json", region_qc["coverage"])
        write_json(run_dir / "logs" / f"{sample}.depth.json", region_qc["depth"])
        write_json(run_dir / "qc" / f"{sample}.callability.json", region_qc["callability"])
        vcf = run_dir / "variants" / f"{sample}.vcf.gz"
        call = run_cmd(
            ["bash", "-c", bcftools_call_command(reference, alignment, vcf, args.region)],
            run_dir,
            timeout=3600,
        )
        write_json(run_dir / "logs" / f"{sample}.bcftools_call.json", call)
        write_text(run_dir / "logs" / f"{sample}.bcftools_call.log", call.get("stdout_tail", ""))
        mq_header_fix = (
            normalize_mq_header(run_dir, sample, vcf)
            if call.get("ok")
            else {"ok": False, "skipped": True}
        )
        write_json(run_dir / "logs" / f"{sample}.mq_header_fix.json", mq_header_fix)
        pre_annotation_index = (
            run_cmd(["bcftools", "index", "-t", str(vcf)], run_dir, timeout=600)
            if call.get("ok") and mq_header_fix.get("ok")
            else {"ok": False, "skipped": True}
        )
        write_json(run_dir / "logs" / f"{sample}.pre_annotation_index.json", pre_annotation_index)
        final_vcf, annotation_result = (
            annotate_vcf(run_dir, sample, vcf, annotation_vcf, args.annotation_columns)
            if pre_annotation_index.get("ok")
            else (vcf, {"ok": False, "skipped": True})
        )
        write_json(run_dir / "logs" / f"{sample}.annotation.json", annotation_result)
        filtered_vcf, filter_result = (
            filter_vcf(run_dir, final_vcf, args.filter_min_qual, args.filter_min_site_dp)
            if call.get("ok") and mq_header_fix.get("ok") and annotation_result.get("ok")
            else (final_vcf, {"ok": False, "skipped": True})
        )
        write_json(run_dir / "logs" / f"{sample}.filter.json", filter_result)
        if call.get("ok") and mq_header_fix.get("ok") and annotation_result.get("ok"):
            if filtered_vcf == vcf and pre_annotation_index.get("ok"):
                index = {
                    **pre_annotation_index,
                    "reused": True,
                    "reason": "reused pre-annotation index for unannotated VCF",
                }
            else:
                index = run_cmd(
                    ["bcftools", "index", "-t", str(filtered_vcf)], run_dir, timeout=600
                )
        else:
            index = {"ok": False, "skipped": True}
        write_json(run_dir / "logs" / f"{sample}.bcftools_index.json", index)
        stats = (
            run_cmd(["bcftools", "stats", str(filtered_vcf)], run_dir, timeout=600)
            if call.get("ok")
            and mq_header_fix.get("ok")
            and annotation_result.get("ok")
            and filter_result.get("ok")
            else {"ok": False, "skipped": True}
        )
        write_json(run_dir / "logs" / f"{sample}.bcftools_stats.json", stats)
        write_text(
            run_dir / "variants" / f"{sample}.bcftools_stats.txt", stats.get("stdout_tail", "")
        )
        write_json(
            run_dir / "qc" / f"{sample}.variant_summary.json",
            parse_variant_stats(str(stats.get("stdout_tail", ""))),
        )
        sample_ok = bool(
            quickcheck.get("ok")
            and flagstat.get("ok")
            and idxstats.get("ok")
            and region_qc["coverage"].get("ok")
            and region_qc["depth"].get("ok")
            and call.get("ok")
            and mq_header_fix.get("ok")
            and annotation_result.get("ok")
            and filter_result.get("ok")
            and index.get("ok")
            and stats.get("ok")
        )
        results["steps"].append({"name": sample, "ok": sample_ok})
        results["ok"] = bool(results["ok"] and sample_ok)
    return results


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    annotation_enabled: bool,
    filtering_enabled: bool,
    resource_plan: dict[str, Any] | None = None,
) -> None:
    sample_name = next(iter((run_dir / "qc").glob("*.variant_summary.json")), None)
    variant_summary = {}
    if sample_name:
        variant_summary = json.loads(sample_name.read_text(encoding="utf-8"))
    lines = [
        "# DNA Variant Calling Run Summary",
        "",
        f"Status: `{status}`",
        f"Samples parsed: `{validation.get('sample_count', 0)}`",
        f"Region: `{validation.get('region') or 'whole input alignment'}`",
        f"Run class: `{validation.get('run_class')}`",
        "",
        "## Key Artifacts",
        "",
        "- `qc/*.flagstat.txt`",
        "- `qc/*.idxstats.tsv`",
        "- `qc/*.coverage.tsv`",
        "- `qc/*.depth.tsv` when `--region` is provided",
        "- `qc/*.callability.json` and `qc/*.variant_summary.json`",
        "- `variants/*.vcf.gz`",
        "- `variants/*.annotated.vcf.gz`" if annotation_enabled else None,
        "- `variants/*.filtered.vcf.gz`" if filtering_enabled else None,
        "- `variants/*.bcftools_stats.txt`",
        "- `visualizations/index.html` and `visualizations/visualization_manifest.json`",
        "- `notebooks/vcf_review.marimo.py` when output VCF/gVCF artifacts are present",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `run_manifest.json` and `artifact_index.json`",
        "",
    ]
    lines = [line for line in lines if line is not None]
    if variant_summary:
        lines.extend(
            [
                "## Interpretation",
                "",
                f"- Record count: `{variant_summary.get('record_count')}`",
                f"- SNP count: `{variant_summary.get('snp_count')}`",
                f"- Indel count: `{variant_summary.get('indel_count')}`",
                f"- Interpretation: {variant_summary.get('interpretation')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Guardrails",
            "",
            "- This local lane is a targeted verification and audit envelope; use subtype lanes for full germline or somatic workflow requirements.",
            "- When no annotation VCF or filter thresholds are provided, interpretation is limited to raw bcftools calls in the queried region.",
            "- Use the germline/somatic subtype lanes for BQSR, cohort logic, or richer annotation/reporting.",
            "",
        ]
    )
    if validation.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in validation["warnings"])
        lines.append("")
    lines.extend(ngs_resource_gate.resource_summary_lines(resource_plan))
    if validation.get("errors"):
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {error}" for error in validation["errors"])
    write_text(run_dir / "summary.md", "\n".join(lines) + "\n")


def write_visuals(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> dict[str, str]:
    first_variant_summary = next(
        iter(sorted((run_dir / "qc").glob("*.variant_summary.json"))), None
    )
    entries = [
        artifact_entry(
            artifact_id="sample_table",
            title="Resolved Sample Table",
            path="validation/samples.normalized.tsv",
            kind="table",
            status="created",
            description="Resolved sample table with absolute BAM/CRAM alignment paths.",
        ),
        artifact_entry(
            artifact_id="variant_summary",
            title="Variant Summary",
            path=str(first_variant_summary.relative_to(run_dir)) if first_variant_summary else None,
            kind="json",
            status="created" if first_variant_summary else "not_available",
            description="Per-sample variant counts parsed from bcftools stats.",
        ),
    ]
    review_outputs = add_vcf_review_notebook_entry(
        run_dir,
        entries,
        title="DNA Variant VCF Review",
        table_items=[("Resolved Sample Table", "validation/samples.normalized.tsv")],
        object_items=[("Run Summary", "summary.md"), ("Artifact Index", "artifact_index.json")],
    )
    entries.extend(ngs_resource_gate.resource_visual_entries(resource_plan))
    index = write_visualization_index(
        run_dir,
        title="DNA Variant Review Bundle",
        description="Review surface for the local DNA variant lane, including VCF/gVCF notebook previews when variant artifacts are present.",
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
    parser.add_argument("--region")
    parser.add_argument(
        "--annotation-vcf",
        type=Path,
        help="Optional bgzip/tabix-indexed VCF used to annotate called variants.",
    )
    parser.add_argument(
        "--annotation-columns",
        help="Optional bcftools annotate -c column list. Defaults to ID plus available AF/AC/AN tags from the resource VCF.",
    )
    parser.add_argument(
        "--filter-min-qual",
        type=float,
        help="Optional QUAL threshold for soft-filtering emitted variants.",
    )
    parser.add_argument(
        "--filter-min-site-dp",
        type=int,
        help="Optional INFO/DP threshold for soft-filtering emitted variants.",
    )
    parser.add_argument(
        "--callable-min-depth",
        type=int,
        default=DEFAULT_CALLABLE_MIN_DEPTH,
        help="Minimum depth used to mark a locus callable in region-level depth summaries.",
    )
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
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--run-id", default=slug_timestamp("dna-variant-calling"))
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    input_validation, rows = validate_inputs(args)
    resource_plan = ngs_resource_gate.write_pipeline_resource_plan(
        run_dir=run_dir,
        pipeline="dna_variant_calling",
        genome_build=args.genome_build,
        bundle_roots=args.bundle_root,
        include_optional=args.include_optional_resources,
        include_checksums=args.resource_checksums,
        skip=args.skip_resource_plan,
        required=args.require_resource_plan,
    )
    validation = ngs_resource_gate.merge_resource_status(
        input_validation,
        resource_plan,
        required=args.require_resource_plan,
    )
    tool_status = tool_preflight(["samtools", "bcftools"], optional=[])
    write_json(
        run_dir / "config.json",
        {
            "reference_fasta": str(args.reference_fasta.expanduser().resolve()),
            "region": validation.get("region"),
            "region_requested": args.region,
            "filter_min_qual": args.filter_min_qual,
            "filter_min_site_dp": args.filter_min_site_dp,
            "callable_min_depth": args.callable_min_depth,
            "run_class": validation.get("run_class"),
        },
    )
    write_json(run_dir / "validation" / "input_summary.json", {"samples": rows})
    write_json(run_dir / "validation" / "input_validation_summary.json", input_validation)
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_normalized_samples(run_dir, rows)
    write_commands(run_dir, args, rows)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions(
            {"samtools": ["samtools", "--version"], "bcftools": ["bcftools", "--version"]}
        ),
    )

    dry_run = {
        "ok": validation["ok"] and tool_status["ok"],
        "detail": "input and tool validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    execution = None
    status = "blocked" if not dry_run["ok"] else "validated"
    if args.execute and dry_run["ok"]:
        execution = execute(run_dir, args, rows)
        status = "completed" if execution.get("ok") else "failed"

    visuals = write_visuals(run_dir, status, validation, resource_plan)
    resource_outputs = ngs_resource_gate.resource_output_paths(resource_plan)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="dna_variant_calling",
        workflow="local_light_samtools_bcftools",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "reference_fasta": str(args.reference_fasta.expanduser().resolve()),
            "annotation_vcf": str(args.annotation_vcf.expanduser().resolve())
            if args.annotation_vcf
            else None,
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "vcf_glob": "variants/*.vcf.gz",
            "annotated_vcf_glob": "variants/*.annotated.vcf.gz" if args.annotation_vcf else None,
            "filtered_vcf_glob": "variants/*.filtered.vcf.gz"
            if args.filter_min_qual is not None or args.filter_min_site_dp is not None
            else None,
            "flagstat_glob": "qc/*.flagstat.txt",
            "idxstats_glob": "qc/*.idxstats.tsv",
            "coverage_glob": "qc/*.coverage.tsv",
            "depth_glob": "qc/*.depth.tsv" if validation.get("region") else None,
            "callability_glob": "qc/*.callability.json",
            **resource_outputs,
            **visuals,
        },
        method={
            "caller": "bcftools mpileup/call",
            "region": validation.get("region"),
            "annotation_columns": args.annotation_columns,
            "filter_min_qual": args.filter_min_qual,
            "filter_min_site_dp": args.filter_min_site_dp,
            "callable_min_depth": args.callable_min_depth,
            "run_class": validation.get("run_class"),
            "resource_plan": resource_plan,
        },
        audit={"resource_readiness": resource_plan} if resource_plan else None,
        review_bundle=visuals,
    )
    write_summary(
        run_dir,
        status,
        validation,
        bool(args.annotation_vcf),
        bool(args.filter_min_qual is not None or args.filter_min_site_dp is not None),
        resource_plan,
    )
    write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))
    print(run_dir)
    return 1 if status in {"blocked", "failed"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
