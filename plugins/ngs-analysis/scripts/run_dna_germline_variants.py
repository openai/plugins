#!/usr/bin/env python3
"""Run germline DNA variant calling with optional BQSR, gVCF, and joint genotyping."""

from __future__ import annotations

import argparse
import csv
import shlex
from pathlib import Path
from typing import Any

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
    add_vcf_review_notebook_entry,
    artifact_entry,
    write_visualization_index,
)

WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "dna_germline_variants"


def detect_delimiter(path: Path) -> str:
    if path.suffix.lower() in {".tsv", ".tab"}:
        return "\t"
    return ","


def read_samples(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=detect_delimiter(path))
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
        return rows, list(reader.fieldnames or [])


def bqsr_enabled(args: argparse.Namespace) -> bool:
    if args.bqsr_mode == "off":
        return False
    if args.bqsr_mode == "force":
        return True
    return bool(args.known_sites)


def use_gvcf(args: argparse.Namespace, sample_count: int) -> bool:
    return bool(args.emit_gvcf or args.joint_call or sample_count > 1)


def validate_inputs(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, str]]]:
    sample_sheet = args.sample_sheet.expanduser().resolve()
    reference = args.reference_fasta.expanduser().resolve()
    target_bed = args.target_bed.expanduser().resolve() if args.target_bed else None
    rows, columns = read_samples(sample_sheet)
    errors: list[str] = []
    warnings: list[str] = []
    normalized: list[dict[str, str]] = []

    if not reference.exists():
        errors.append(f"reference FASTA does not exist: {reference}")
    if not (Path(str(reference) + ".fai")).exists():
        warnings.append(
            f"reference FASTA index is missing and may be created by samtools faidx: {reference}.fai"
        )
    if not (reference.with_suffix(".dict")).exists():
        warnings.append(
            f"reference sequence dictionary is missing and may be created by GATK: {reference.with_suffix('.dict')}"
        )
    if target_bed and not target_bed.exists():
        errors.append(f"target BED does not exist: {target_bed}")
    if args.bqsr_mode == "force" and not args.known_sites:
        errors.append("BQSR was forced but no --known-sites VCFs were provided")

    known_sites: list[str] = []
    for item in args.known_sites:
        resource = item.expanduser().resolve()
        known_sites.append(str(resource))
        if not resource.exists():
            errors.append(f"known-sites VCF does not exist: {resource}")
        if (
            not (Path(str(resource) + ".tbi")).exists()
            and not (Path(str(resource) + ".csi")).exists()
        ):
            warnings.append(
                f"known-sites VCF index is missing and may be required by GATK: {resource}.tbi"
            )

    for row_index, row in enumerate(rows, start=2):
        sample = row.get("sample") or row.get("sample_id") or f"row_{row_index}"
        bam_raw = row.get("bam") or row.get("cram") or ""
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
    if args.joint_call and len(normalized) < 2:
        warnings.append(
            "joint calling was requested with fewer than two samples; GenotypeGVCFs can still run, but a cohort VCF may not add value"
        )

    validation = {
        "ok": not errors,
        "sample_sheet": str(sample_sheet),
        "reference_fasta": str(reference),
        "target_bed": str(target_bed) if target_bed else None,
        "known_sites": known_sites,
        "columns": columns,
        "sample_count": len(normalized),
        "sample_model": args.sample_model,
        "bqsr_enabled": bqsr_enabled(args),
        "emit_gvcf": use_gvcf(args, len(normalized)),
        "joint_call": args.joint_call,
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


def write_commands(run_dir: Path, args: argparse.Namespace, rows: list[dict[str, str]]) -> None:
    reference = args.reference_fasta.expanduser().resolve()
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        shlex.join(["samtools", "faidx", str(reference)]),
    ]
    if bqsr_enabled(args):
        for row in rows:
            sample = row["sample"]
            known_sites_args = []
            for resource in args.known_sites:
                known_sites_args.extend(["--known-sites", str(resource.expanduser().resolve())])
            lines.append(
                shlex.join(
                    [
                        "gatk",
                        "BaseRecalibrator",
                        "-R",
                        str(reference),
                        "-I",
                        row["alignment"],
                        *known_sites_args,
                        "-O",
                        f"recal/{sample}.recal.table",
                    ]
                )
            )
            lines.append(
                shlex.join(
                    [
                        "gatk",
                        "ApplyBQSR",
                        "-R",
                        str(reference),
                        "-I",
                        row["alignment"],
                        "--bqsr-recal-file",
                        f"recal/{sample}.recal.table",
                        "-O",
                        f"recal/{sample}.recal.bam",
                    ]
                )
            )
    for row in rows:
        sample = row["sample"]
        input_bam = (
            Path(f"recal/{sample}.recal.bam") if bqsr_enabled(args) else Path(row["alignment"])
        )
        lines.append(
            shlex.join(["samtools", "flagstat", str(input_bam)]) + f" > qc/{sample}.flagstat.txt"
        )
        lines.append(
            shlex.join(["samtools", "idxstats", str(input_bam)]) + f" > qc/{sample}.idxstats.tsv"
        )
        hc_cmd = ["gatk", "HaplotypeCaller", "-R", str(reference), "-I", str(input_bam)]
        if args.target_bed:
            hc_cmd.extend(["-L", str(args.target_bed.expanduser().resolve())])
        if use_gvcf(args, len(rows)):
            hc_cmd.extend(["-ERC", "GVCF", "-O", f"gvcf/{sample}.g.vcf.gz"])
        else:
            hc_cmd.extend(["-O", f"variants/{sample}.vcf.gz"])
        lines.append(shlex.join(hc_cmd))
    if args.joint_call:
        combine_cmd = ["gatk", "CombineGVCFs", "-R", str(reference)]
        for row in rows:
            combine_cmd.extend(["-V", f"gvcf/{row['sample']}.g.vcf.gz"])
        combine_cmd.extend(["-O", "joint/cohort.combined.g.vcf.gz"])
        lines.append(shlex.join(combine_cmd))
        lines.append(
            shlex.join(
                [
                    "gatk",
                    "GenotypeGVCFs",
                    "-R",
                    str(reference),
                    "-V",
                    "joint/cohort.combined.g.vcf.gz",
                    "-O",
                    "joint/cohort.joint.vcf.gz",
                ]
            )
        )
    write_text(run_dir / "commands.sh", "\n".join(lines) + "\n")


def execute(run_dir: Path, args: argparse.Namespace, rows: list[dict[str, str]]) -> dict[str, Any]:
    reference = args.reference_fasta.expanduser().resolve()
    results: dict[str, Any] = {"ok": True, "steps": []}
    (run_dir / "qc").mkdir(parents=True, exist_ok=True)
    (run_dir / "recal").mkdir(parents=True, exist_ok=True)
    (run_dir / "gvcf").mkdir(parents=True, exist_ok=True)
    (run_dir / "variants").mkdir(parents=True, exist_ok=True)
    (run_dir / "joint").mkdir(parents=True, exist_ok=True)

    if not (Path(str(reference) + ".fai")).exists():
        faidx = run_cmd(["samtools", "faidx", str(reference)], run_dir, timeout=600)
        write_json(run_dir / "logs" / "samtools_faidx.json", faidx)
        results["steps"].append({"name": "samtools_faidx", "ok": faidx.get("ok")})
        results["ok"] = bool(results["ok"] and faidx.get("ok"))

    reference_dict = reference.with_suffix(".dict")
    if not reference_dict.exists():
        create_dict = run_cmd(
            ["gatk", "CreateSequenceDictionary", "-R", str(reference), "-O", str(reference_dict)],
            run_dir,
            timeout=600,
        )
        write_json(run_dir / "logs" / "gatk_create_dict.json", create_dict)
        results["steps"].append({"name": "gatk_create_dict", "ok": create_dict.get("ok")})
        results["ok"] = bool(results["ok"] and create_dict.get("ok"))

    gvcfs: list[Path] = []
    for row in rows:
        sample = row["sample"]
        input_bam = Path(row["alignment"])
        if bqsr_enabled(args):
            known_sites_args = []
            for resource in args.known_sites:
                known_sites_args.extend(["--known-sites", str(resource.expanduser().resolve())])
            recal_table = run_dir / "recal" / f"{sample}.recal.table"
            recal = run_cmd(
                [
                    "gatk",
                    "BaseRecalibrator",
                    "-R",
                    str(reference),
                    "-I",
                    str(input_bam),
                    *known_sites_args,
                    "-O",
                    str(recal_table),
                ],
                run_dir,
                timeout=3600,
            )
            write_json(run_dir / "logs" / f"{sample}.base_recalibrator.json", recal)
            apply_bqsr = run_cmd(
                [
                    "gatk",
                    "ApplyBQSR",
                    "-R",
                    str(reference),
                    "-I",
                    str(input_bam),
                    "--bqsr-recal-file",
                    str(recal_table),
                    "-O",
                    str(run_dir / "recal" / f"{sample}.recal.bam"),
                ],
                run_dir,
                timeout=3600,
            )
            write_json(run_dir / "logs" / f"{sample}.apply_bqsr.json", apply_bqsr)
            input_bam = run_dir / "recal" / f"{sample}.recal.bam"
            bam_index = run_cmd(["samtools", "index", str(input_bam)], run_dir, timeout=600)
            write_json(run_dir / "logs" / f"{sample}.recal_index.json", bam_index)
        quickcheck = run_cmd(["samtools", "quickcheck", "-v", str(input_bam)], run_dir, timeout=300)
        write_json(run_dir / "logs" / f"{sample}.quickcheck.json", quickcheck)
        flagstat = run_cmd(["samtools", "flagstat", str(input_bam)], run_dir, timeout=600)
        write_json(run_dir / "logs" / f"{sample}.flagstat.json", flagstat)
        write_text(run_dir / "qc" / f"{sample}.flagstat.txt", flagstat.get("stdout_tail", ""))
        idxstats = run_cmd(["samtools", "idxstats", str(input_bam)], run_dir, timeout=600)
        write_json(run_dir / "logs" / f"{sample}.idxstats.json", idxstats)
        write_text(run_dir / "qc" / f"{sample}.idxstats.tsv", idxstats.get("stdout_tail", ""))

        output_vcf = (
            run_dir
            / ("gvcf" if use_gvcf(args, len(rows)) else "variants")
            / (f"{sample}.g.vcf.gz" if use_gvcf(args, len(rows)) else f"{sample}.vcf.gz")
        )
        haplotype_caller_cmd = [
            "gatk",
            "HaplotypeCaller",
            "-R",
            str(reference),
            "-I",
            str(input_bam),
        ]
        if args.target_bed:
            haplotype_caller_cmd.extend(["-L", str(args.target_bed.expanduser().resolve())])
        if use_gvcf(args, len(rows)):
            haplotype_caller_cmd.extend(["-ERC", "GVCF"])
        haplotype_caller_cmd.extend(["-O", str(output_vcf)])
        hc = run_cmd(haplotype_caller_cmd, run_dir, timeout=7200)
        write_json(run_dir / "logs" / f"{sample}.haplotypecaller.json", hc)
        sample_ok = bool(
            quickcheck.get("ok") and flagstat.get("ok") and idxstats.get("ok") and hc.get("ok")
        )
        results["steps"].append({"name": sample, "ok": sample_ok})
        results["ok"] = bool(results["ok"] and sample_ok)
        if use_gvcf(args, len(rows)):
            gvcfs.append(output_vcf)

    if args.joint_call and gvcfs:
        combine_cmd = ["gatk", "CombineGVCFs", "-R", str(reference)]
        for item in gvcfs:
            combine_cmd.extend(["-V", str(item)])
        combined_gvcf = run_dir / "joint" / "cohort.combined.g.vcf.gz"
        combine_cmd.extend(["-O", str(combined_gvcf)])
        combine = run_cmd(combine_cmd, run_dir, timeout=7200)
        write_json(run_dir / "logs" / "cohort.combine_gvcfs.json", combine)
        genotype = run_cmd(
            [
                "gatk",
                "GenotypeGVCFs",
                "-R",
                str(reference),
                "-V",
                str(combined_gvcf),
                "-O",
                str(run_dir / "joint" / "cohort.joint.vcf.gz"),
            ],
            run_dir,
            timeout=7200,
        )
        write_json(run_dir / "logs" / "cohort.genotype_gvcfs.json", genotype)
        joint_ok = bool(combine.get("ok") and genotype.get("ok"))
        results["steps"].append({"name": "joint_call", "ok": joint_ok})
        results["ok"] = bool(results["ok"] and joint_ok)
    return results


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# Germline DNA Variant Calling Run Summary",
        "",
        f"Status: `{status}`",
        f"Sample model: `{validation.get('sample_model')}`",
        f"BQSR enabled: `{validation.get('bqsr_enabled')}`",
        f"Emit gVCF: `{validation.get('emit_gvcf')}`",
        f"Joint call: `{validation.get('joint_call')}`",
        "",
        "## Key Artifacts",
        "",
        "- `qc/*.flagstat.txt`",
        "- `qc/*.idxstats.tsv`",
        "- `recal/*.recal.table` and `recal/*.recal.bam` when BQSR runs",
        "- `gvcf/*.g.vcf.gz` for per-sample GVCFs",
        "- `joint/cohort.joint.vcf.gz` for joint genotyping",
        "- `visualizations/index.html` and `visualizations/visualization_manifest.json`",
        "- `notebooks/vcf_review.marimo.py` when output VCF/gVCF artifacts are present",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `run_manifest.json` and `artifact_index.json`",
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
        lines.append("")
    write_text(run_dir / "summary.md", "\n".join(lines))


def write_visuals(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> dict[str, str]:
    entries = [
        artifact_entry(
            artifact_id="sample_table",
            title="Resolved Sample Table",
            path="validation/samples.normalized.tsv",
            kind="table",
            status="created",
            description="Resolved sample table with absolute alignment paths used by the germline runner.",
        ),
    ]
    review_outputs = add_vcf_review_notebook_entry(
        run_dir,
        entries,
        title="Germline DNA VCF Review",
        table_items=[("Resolved Sample Table", "validation/samples.normalized.tsv")],
        object_items=[("Run Summary", "summary.md"), ("Artifact Index", "artifact_index.json")],
    )
    entries.extend(ngs_resource_gate.resource_visual_entries(resource_plan))
    index = write_visualization_index(
        run_dir,
        title="Germline DNA Review Bundle",
        description="Review surface for the GATK germline lane, including generic VCF/gVCF notebook previews when variant artifacts are present.",
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
    parser.add_argument(
        "--known-sites",
        type=Path,
        action="append",
        default=[],
        help="Repeat for each known-sites VCF used by BaseRecalibrator.",
    )
    parser.add_argument("--target-bed", type=Path)
    parser.add_argument(
        "--sample-model",
        choices=["singleton", "cohort", "duo", "trio", "family"],
        default="singleton",
    )
    parser.add_argument("--bqsr-mode", choices=["auto", "off", "force"], default="auto")
    parser.add_argument(
        "--emit-gvcf",
        action="store_true",
        help="Emit per-sample gVCFs even without joint genotyping.",
    )
    parser.add_argument(
        "--joint-call", action="store_true", help="Combine per-sample gVCFs and run GenotypeGVCFs."
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
    parser.add_argument("--run-id", default=slug_timestamp("dna-germline-variants"))
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
        pipeline="dna_germline_variants",
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
    required_tools = ["samtools", "gatk"] if args.execute else []
    optional_tools = [
        name
        for name in ["samtools", "gatk", "bcftools", "deepvariant"]
        if name not in required_tools
    ]
    tool_status = tool_preflight(required_tools, optional=optional_tools)
    write_json(
        run_dir / "config.json",
        {
            "reference_fasta": str(args.reference_fasta.expanduser().resolve()),
            "known_sites": [str(item.expanduser().resolve()) for item in args.known_sites],
            "target_bed": str(args.target_bed.expanduser().resolve()) if args.target_bed else None,
            "sample_model": args.sample_model,
            "bqsr_mode": args.bqsr_mode,
            "emit_gvcf": args.emit_gvcf,
            "joint_call": args.joint_call,
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
            {
                "samtools": ["samtools", "--version"],
                "gatk": ["gatk", "--version"],
                "bcftools": ["bcftools", "--version"],
            }
        ),
    )

    dry_run_ok = validation["ok"] and (tool_status["ok"] if args.execute else True)
    dry_run = {"ok": dry_run_ok, "detail": "input, resource, and tool validation completed"}
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
        lane="dna_germline_variants",
        workflow="gatk_bqsr_haplotypecaller_joint_genotyping",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "reference_fasta": str(args.reference_fasta.expanduser().resolve()),
            "known_sites": [str(item.expanduser().resolve()) for item in args.known_sites],
            "target_bed": str(args.target_bed.expanduser().resolve()) if args.target_bed else None,
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "flagstat_glob": "qc/*.flagstat.txt",
            "idxstats_glob": "qc/*.idxstats.tsv",
            "recal_table_glob": "recal/*.recal.table",
            "recal_bam_glob": "recal/*.recal.bam",
            "gvcf_glob": "gvcf/*.g.vcf.gz",
            "joint_vcf_glob": "joint/cohort.joint.vcf.gz" if args.joint_call else None,
            **resource_outputs,
            **visuals,
        },
        method={
            "sample_model": args.sample_model,
            "bqsr_mode": args.bqsr_mode,
            "emit_gvcf": use_gvcf(args, len(rows)),
            "joint_call": args.joint_call,
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
