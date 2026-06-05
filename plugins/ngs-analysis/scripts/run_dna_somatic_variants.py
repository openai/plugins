#!/usr/bin/env python3
"""Run or plan local somatic SNV/indel calling with GATK Mutect2."""

from __future__ import annotations

import argparse
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
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "dna_somatic_variants"
SOMATIC_PAIR_REVIEW_FIELDS = [
    "pair_id",
    "design",
    "tumor_sample",
    "normal_sample",
    "filtered_vcf",
    "filtered_vcf_exists",
    "bcftools_stats",
    "variant_records",
    "snp_count",
    "indel_count",
    "contamination_table",
    "contamination_table_exists",
    "panel_of_normals_ready",
    "germline_resource_ready",
    "orientation_bias_model_requested",
    "status",
    "notes",
]


def parse_first_int(value: str) -> int | None:
    try:
        return int(str(value).strip().split()[0])
    except (ValueError, IndexError):
        return None


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
        value = parse_first_int(fields[3])
        if fields[2] == "number of records:":
            metrics["variant_records"] = value
        elif fields[2] == "number of SNPs:":
            metrics["snp_count"] = value
        elif fields[2] == "number of indels:":
            metrics["indel_count"] = value
    return metrics


def optional_existing_path(
    raw: str | None,
    base: Path,
    errors: list[str],
    warnings: list[str],
    label: str,
    *,
    required: bool = False,
) -> Path | None:
    path = resolve_path(raw, base)
    if path is None:
        if required:
            errors.append(f"{label} is required")
        return None
    if not path.exists():
        message = f"{label} does not exist: {path}"
        if required:
            errors.append(message)
        else:
            warnings.append(message)
    return path


def validate_inputs(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, str]]]:
    sample_sheet = args.sample_sheet.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    pairs: list[dict[str, str]] = []
    rows: list[dict[str, str]] = []
    columns: list[str] = []
    if not sample_sheet.exists():
        errors.append(f"sample sheet does not exist: {sample_sheet}")
    else:
        try:
            rows, columns = read_table(sample_sheet)
        except Exception as exc:  # pragma: no cover - defensive parser guard
            errors.append(f"failed to parse sample sheet {sample_sheet}: {exc}")

    reference = optional_existing_path(
        str(args.reference_fasta),
        sample_sheet.parent,
        errors,
        warnings,
        "reference FASTA",
        required=True,
    )
    if reference:
        if not Path(str(reference) + ".fai").exists():
            warnings.append(
                f"reference FASTA index is missing and may be created by samtools faidx: {reference}.fai"
            )
        if not reference.with_suffix(".dict").exists():
            warnings.append(
                f"reference sequence dictionary is missing and may be created by GATK: {reference.with_suffix('.dict')}"
            )
    target_bed = optional_existing_path(
        str(args.target_bed) if args.target_bed else None,
        sample_sheet.parent,
        errors,
        warnings,
        "target BED",
    )
    panel_of_normals = optional_existing_path(
        str(args.panel_of_normals) if args.panel_of_normals else None,
        sample_sheet.parent,
        errors,
        warnings,
        "panel-of-normals VCF",
    )
    germline_resource = optional_existing_path(
        str(args.germline_resource) if args.germline_resource else None,
        sample_sheet.parent,
        errors,
        warnings,
        "germline resource VCF",
    )
    annotation_vcf = optional_existing_path(
        str(args.annotation_vcf) if args.annotation_vcf else None,
        sample_sheet.parent,
        errors,
        warnings,
        "annotation VCF",
    )

    for row_index, row in enumerate(rows, start=2):
        pair_id = normalize_sample_name(
            row.get("pair_id")
            or row.get("case_id")
            or row.get("sample")
            or row.get("tumor_sample"),
            f"row_{row_index}",
        )
        tumor_sample = normalize_sample_name(
            row.get("tumor_sample") or row.get("sample") or pair_id, f"{pair_id}_tumor"
        )
        normal_sample = (
            normalize_sample_name(row.get("normal_sample"), f"{pair_id}_normal")
            if row.get("normal_sample")
            else ""
        )
        tumor_bam = optional_existing_path(
            row.get("tumor_bam") or row.get("tumor_cram") or row.get("bam") or row.get("cram"),
            sample_sheet.parent,
            errors,
            warnings,
            f"row {row_index} tumor BAM/CRAM",
            required=True,
        )
        normal_bam = optional_existing_path(
            row.get("normal_bam") or row.get("normal_cram"),
            sample_sheet.parent,
            errors,
            warnings,
            f"row {row_index} normal BAM/CRAM",
        )
        if tumor_bam and tumor_bam.suffix == ".bam" and not Path(str(tumor_bam) + ".bai").exists():
            warnings.append(
                f"row {row_index}: tumor BAM index is missing and may be created by samtools index: {tumor_bam}.bai"
            )
        if (
            normal_bam
            and normal_bam.suffix == ".bam"
            and not Path(str(normal_bam) + ".bai").exists()
        ):
            warnings.append(
                f"row {row_index}: normal BAM index is missing and may be created by samtools index: {normal_bam}.bai"
            )
        if tumor_bam:
            design = "tumor_normal" if normal_bam else "tumor_only"
            if design == "tumor_only":
                warnings.append(
                    f"row {row_index}: tumor-only somatic calling requires stronger germline filtering caveats"
                )
            pairs.append(
                {
                    "pair_id": pair_id,
                    "design": design,
                    "tumor_sample": tumor_sample,
                    "tumor_alignment": str(tumor_bam),
                    "normal_sample": normal_sample,
                    "normal_alignment": str(normal_bam) if normal_bam else "",
                    "row_index": str(row_index),
                }
            )
    if not pairs:
        errors.append("no usable tumor rows found")
    if any(pair["design"] == "tumor_only" for pair in pairs) and not germline_resource:
        warnings.append(
            "tumor-only runs should provide --germline-resource to reduce germline false positives"
        )
    if not panel_of_normals:
        warnings.append(
            "no panel-of-normals was provided; recurrent technical artifacts may be harder to filter"
        )
    validation = {
        "ok": not errors,
        "sample_sheet": str(sample_sheet),
        "reference_fasta": str(reference) if reference else str(args.reference_fasta),
        "target_bed": str(target_bed) if target_bed else None,
        "panel_of_normals": str(panel_of_normals) if panel_of_normals else None,
        "germline_resource": str(germline_resource) if germline_resource else None,
        "annotation_vcf": str(annotation_vcf) if annotation_vcf else None,
        "columns": columns,
        "pair_count": len(pairs),
        "designs": sorted({pair["design"] for pair in pairs}),
        "errors": errors,
        "warnings": warnings,
    }
    return validation, pairs


def mutect2_plan(args: argparse.Namespace, pairs: list[dict[str, str]]) -> list[dict[str, Any]]:
    reference = args.reference_fasta.expanduser().resolve()
    commands: list[dict[str, Any]] = []
    for pair in pairs:
        pair_id = pair["pair_id"]
        tumor_bam = Path(pair["tumor_alignment"])
        unfiltered = f"variants/{pair_id}.unfiltered.vcf.gz"
        filtered = f"variants/{pair_id}.filtered.vcf.gz"
        cmd: list[str | Path] = [
            "gatk",
            "Mutect2",
            "-R",
            reference,
            "-I",
            tumor_bam,
            "-tumor",
            pair["tumor_sample"],
        ]
        if pair["normal_alignment"]:
            cmd.extend(["-I", Path(pair["normal_alignment"]), "-normal", pair["normal_sample"]])
        if args.germline_resource:
            cmd.extend(["--germline-resource", args.germline_resource.expanduser().resolve()])
        if args.panel_of_normals:
            cmd.extend(["-pon", args.panel_of_normals.expanduser().resolve()])
        if args.target_bed:
            cmd.extend(["-L", args.target_bed.expanduser().resolve()])
        if args.f1r2_orientation_model:
            cmd.extend(["--f1r2-tar-gz", f"f1r2/{pair_id}.f1r2.tar.gz"])
        cmd.extend(["-O", unfiltered])
        commands.append(command_plan_entry(f"{pair_id}: mutect2", cmd, outputs=[unfiltered]))
        if args.f1r2_orientation_model:
            commands.append(
                command_plan_entry(
                    f"{pair_id}: learn read orientation model",
                    [
                        "gatk",
                        "LearnReadOrientationModel",
                        "-I",
                        f"f1r2/{pair_id}.f1r2.tar.gz",
                        "-O",
                        f"f1r2/{pair_id}.read-orientation-model.tar.gz",
                    ],
                    outputs=[f"f1r2/{pair_id}.read-orientation-model.tar.gz"],
                )
            )
        contamination_args: list[str | Path] = []
        if args.germline_resource:
            pileup_intervals = (
                args.target_bed.expanduser().resolve()
                if args.target_bed
                else args.germline_resource.expanduser().resolve()
            )
            tumor_pileups = f"qc/{pair_id}.tumor.pileups.table"
            commands.append(
                command_plan_entry(
                    f"{pair_id}: tumor pileup summaries",
                    [
                        "gatk",
                        "GetPileupSummaries",
                        "-I",
                        tumor_bam,
                        "-V",
                        args.germline_resource.expanduser().resolve(),
                        "-L",
                        pileup_intervals,
                        "-O",
                        tumor_pileups,
                    ],
                    outputs=[tumor_pileups],
                )
            )
            contamination_args.extend(
                ["--contamination-table", f"qc/{pair_id}.contamination.table"]
            )
            if pair["normal_alignment"]:
                normal_pileups = f"qc/{pair_id}.normal.pileups.table"
                commands.append(
                    command_plan_entry(
                        f"{pair_id}: normal pileup summaries",
                        [
                            "gatk",
                            "GetPileupSummaries",
                            "-I",
                            Path(pair["normal_alignment"]),
                            "-V",
                            args.germline_resource.expanduser().resolve(),
                            "-L",
                            pileup_intervals,
                            "-O",
                            normal_pileups,
                        ],
                        outputs=[normal_pileups],
                    )
                )
                commands.append(
                    command_plan_entry(
                        f"{pair_id}: contamination estimate",
                        [
                            "gatk",
                            "CalculateContamination",
                            "-I",
                            tumor_pileups,
                            "-matched",
                            normal_pileups,
                            "-O",
                            f"qc/{pair_id}.contamination.table",
                        ],
                        outputs=[f"qc/{pair_id}.contamination.table"],
                    )
                )
            else:
                commands.append(
                    command_plan_entry(
                        f"{pair_id}: contamination estimate",
                        [
                            "gatk",
                            "CalculateContamination",
                            "-I",
                            tumor_pileups,
                            "-O",
                            f"qc/{pair_id}.contamination.table",
                        ],
                        outputs=[f"qc/{pair_id}.contamination.table"],
                    )
                )
        filter_cmd: list[str | Path] = [
            "gatk",
            "FilterMutectCalls",
            "-R",
            reference,
            "-V",
            unfiltered,
            "-O",
            filtered,
        ]
        filter_cmd.extend(contamination_args)
        if args.f1r2_orientation_model:
            filter_cmd.extend(["--ob-priors", f"f1r2/{pair_id}.read-orientation-model.tar.gz"])
        commands.append(
            command_plan_entry(f"{pair_id}: filter mutect calls", filter_cmd, outputs=[filtered])
        )
        if args.annotation_vcf:
            annotated = f"variants/{pair_id}.filtered.annotated.vcf.gz"
            commands.append(
                command_plan_entry(
                    f"{pair_id}: annotate filtered VCF",
                    [
                        "bcftools",
                        "annotate",
                        "-a",
                        args.annotation_vcf.expanduser().resolve(),
                        "-c",
                        "ID,INFO/AF",
                        "-O",
                        "z",
                        "-o",
                        annotated,
                        filtered,
                    ],
                    outputs=[annotated],
                )
            )
        commands.append(
            command_plan_entry(
                f"{pair_id}: bcftools stats",
                f"{shell_join(['bcftools', 'stats', filtered])} > {shell_join([f'variants/{pair_id}.bcftools_stats.txt'])}",
                outputs=[f"variants/{pair_id}.bcftools_stats.txt"],
            )
        )
    return commands


def summarize_somatic_artifacts(
    run_dir: Path,
    validation: dict[str, Any],
    pairs: list[dict[str, str]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair in pairs:
        pair_id = pair["pair_id"]
        filtered_vcf = run_dir / "variants" / f"{pair_id}.filtered.vcf.gz"
        stats_path = run_dir / "variants" / f"{pair_id}.bcftools_stats.txt"
        contamination_path = run_dir / "qc" / f"{pair_id}.contamination.table"
        stats = parse_bcftools_stats(stats_path)
        observed = [filtered_vcf.exists(), stats_path.exists(), contamination_path.exists()]
        status = "created" if all(observed[:2]) else ("partial" if any(observed) else "planned")
        notes: list[str] = []
        if pair["design"] == "tumor_only":
            notes.append("tumor-only design; matched-normal evidence unavailable")
        if not validation.get("germline_resource"):
            notes.append("germline resource not provided")
        if not validation.get("panel_of_normals"):
            notes.append("panel-of-normals not provided")
        if not args.f1r2_orientation_model:
            notes.append("orientation-bias model not requested")
        if stats["variant_records"] is None:
            notes.append("variant stats not found")
        rows.append(
            {
                "pair_id": pair_id,
                "design": pair["design"],
                "tumor_sample": pair["tumor_sample"],
                "normal_sample": pair["normal_sample"],
                "filtered_vcf": str(filtered_vcf),
                "filtered_vcf_exists": str(filtered_vcf.exists()).lower(),
                "bcftools_stats": str(stats_path),
                "variant_records": stats["variant_records"]
                if stats["variant_records"] is not None
                else "",
                "snp_count": stats["snp_count"] if stats["snp_count"] is not None else "",
                "indel_count": stats["indel_count"] if stats["indel_count"] is not None else "",
                "contamination_table": str(contamination_path),
                "contamination_table_exists": str(contamination_path.exists()).lower(),
                "panel_of_normals_ready": str(bool(validation.get("panel_of_normals"))).lower(),
                "germline_resource_ready": str(bool(validation.get("germline_resource"))).lower(),
                "orientation_bias_model_requested": str(bool(args.f1r2_orientation_model)).lower(),
                "status": status,
                "notes": "; ".join(notes),
            }
        )
    write_tsv(run_dir / "qc" / "somatic_pair_review.tsv", rows, SOMATIC_PAIR_REVIEW_FIELDS)
    write_json(
        run_dir / "qc" / "somatic_pair_review.json",
        {
            "pairs": rows,
            "pair_count": len(rows),
            "tumor_only_count": sum(1 for row in rows if row["design"] == "tumor_only"),
            "pairs_with_filtered_vcf": sum(
                1 for row in rows if row["filtered_vcf_exists"] == "true"
            ),
            "pairs_with_variant_stats": sum(1 for row in rows if row["variant_records"] != ""),
            "pairs_with_contamination_table": sum(
                1 for row in rows if row["contamination_table_exists"] == "true"
            ),
        },
    )
    return rows


def write_outputs(
    run_dir: Path,
    validation: dict[str, Any],
    pairs: list[dict[str, str]],
    plan: list[dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    write_tsv(
        run_dir / "validation" / "pairs.normalized.tsv",
        pairs,
        [
            "pair_id",
            "design",
            "tumor_sample",
            "tumor_alignment",
            "normal_sample",
            "normal_alignment",
            "row_index",
        ],
    )
    write_json(
        run_dir / "qc" / "somatic_qc_summary.json",
        {
            "pair_count": validation.get("pair_count", 0),
            "designs": validation.get("designs", []),
            "tumor_only_pair_ids": [
                pair["pair_id"] for pair in pairs if pair["design"] == "tumor_only"
            ],
            "resource_status": {
                "germline_resource": bool(validation.get("germline_resource")),
                "panel_of_normals": bool(validation.get("panel_of_normals")),
                "target_bed": bool(validation.get("target_bed")),
            },
            "warnings": validation.get("warnings", []),
        },
    )
    write_tsv(
        run_dir / "qc" / "somatic_filter_reasons.tsv",
        [
            {
                "pair_id": pair["pair_id"],
                "status": "not_executed",
                "note": "Filter annotations are populated after Mutect2 execution.",
            }
            for pair in pairs
        ],
        ["pair_id", "status", "note"],
    )
    summarize_somatic_artifacts(run_dir, validation, pairs, args)
    write_json(run_dir / "workflow" / "somatic_command_plan.json", {"commands": plan})
    write_command_script(run_dir / "commands.sh", [item["command"] for item in plan])


def execute_plan(run_dir: Path, plan: list[dict[str, Any]]) -> dict[str, Any]:
    for dirname in ["variants", "qc", "logs", "f1r2"]:
        (run_dir / dirname).mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"ok": True, "steps": []}
    for index, item in enumerate(plan, start=1):
        step = run_cmd(["bash", "-c", item["command"]], run_dir, timeout=7200)
        safe_name = item["name"].replace(":", "").replace(" ", "_").replace("/", "_")
        write_json(run_dir / "logs" / f"{index:02d}_{safe_name}.json", step)
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
        "# Somatic DNA Variant Run Summary",
        "",
        f"Status: `{status}`",
        f"Pairs parsed: `{validation.get('pair_count', 0)}`",
        f"Designs: `{', '.join(validation.get('designs', [])) or 'none'}`",
        "",
        "## Key Artifacts",
        "",
        "- `validation/pairs.normalized.tsv`",
        "- `workflow/somatic_command_plan.json`",
        "- `qc/somatic_qc_summary.json`",
        "- `qc/somatic_pair_review.tsv` and `qc/somatic_pair_review.json`",
        "- `qc/somatic_filter_reasons.tsv`",
        "- `variants/*.unfiltered.vcf.gz` and `variants/*.filtered.vcf.gz` when executed",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `visualizations/index.html` and `visualizations/visualization_manifest.json`",
        "- `notebooks/vcf_review.marimo.py` when output VCF/gVCF artifacts are present",
        "- `run_manifest.json` and `artifact_index.json`",
        "",
        "## Guardrails",
        "",
        "- Tumor-only calls are not confirmed somatic without matched-normal or strong germline-resource filtering.",
        "- Panel-of-normals and orientation-bias filtering should match the capture kit, library prep, and reference build.",
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
            artifact_id="pairing_table",
            title="Tumor/Normal Pairing Table",
            path="validation/pairs.normalized.tsv",
            kind="table",
            status="created",
            description="Normalized tumor-normal or tumor-only sample design used by the runner.",
        ),
        artifact_entry(
            artifact_id="command_plan",
            title="Somatic Command Plan",
            path="workflow/somatic_command_plan.json",
            kind="json",
            status="created",
            description="Executable Mutect2, contamination, filtering, and optional annotation commands.",
        ),
        artifact_entry(
            artifact_id="somatic_qc_summary",
            title="Somatic QC Summary",
            path="qc/somatic_qc_summary.json",
            kind="json",
            status="created",
            description="Pairing, resource, and tumor-only caveat summary.",
        ),
        artifact_entry(
            artifact_id="somatic_pair_review",
            title="Somatic Pair Review",
            path="qc/somatic_pair_review.tsv",
            kind="table",
            status="created",
            description="Per-pair review of design, matched-normal state, resource caveats, filtered VCF status, contamination table, and variant stats.",
        ),
    ]
    review_outputs = add_vcf_review_notebook_entry(
        run_dir,
        entries,
        title="Somatic DNA VCF Review",
        table_items=[
            ("Tumor/Normal Pairing Table", "validation/pairs.normalized.tsv"),
            ("Somatic Pair Review", "qc/somatic_pair_review.tsv"),
        ],
        object_items=[
            ("Somatic QC Summary", "qc/somatic_qc_summary.json"),
            ("Run Summary", "summary.md"),
        ],
    )
    entries.extend(ngs_resource_gate.resource_visual_entries(resource_plan))
    index = write_visualization_index(
        run_dir,
        title="Somatic DNA Variant Review",
        description="Review surface for tumor-normal/tumor-only Mutect2 planning and execution artifacts.",
        entries=entries,
        notes=[
            *validation.get("warnings", []),
            *ngs_resource_gate.resource_messages(resource_plan),
        ],
        analysis_intent="real_analysis" if status != "blocked" else "blocked_preflight",
        provenance_summary={
            "status": status,
            "pair_count": validation.get("pair_count", 0),
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
    parser.add_argument("--panel-of-normals", type=Path)
    parser.add_argument("--germline-resource", type=Path)
    parser.add_argument("--annotation-vcf", type=Path)
    parser.add_argument("--f1r2-orientation-model", action="store_true")
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
    parser.add_argument("--run-id", default=slug_timestamp("dna-somatic-variants"))
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

    input_validation, pairs = validate_inputs(args)
    resource_plan = ngs_resource_gate.write_pipeline_resource_plan(
        run_dir=run_dir,
        pipeline="dna_somatic_variants",
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
    required_tools = ["gatk", "samtools", "bcftools"] if args.execute else []
    optional_tools = [
        name for name in ["gatk", "samtools", "bcftools"] if name not in required_tools
    ]
    tool_status = tool_preflight(required_tools, optional=optional_tools)
    plan = mutect2_plan(args, pairs)
    write_json(run_dir / "config.json", {**serializable_args(args), "run_dir": str(run_dir)})
    write_json(run_dir / "validation" / "input_validation_summary.json", input_validation)
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions(
            {
                "gatk": ["gatk", "--version"],
                "samtools": ["samtools", "--version"],
                "bcftools": ["bcftools", "--version"],
            }
        ),
    )
    write_outputs(run_dir, validation, pairs, plan, args)
    dry_run = {
        "ok": validation["ok"] and (tool_status["ok"] if args.execute else True),
        "detail": "input, pairing, resource, and tool validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    status = "blocked" if not dry_run["ok"] else "validated"
    execution = None
    if args.execute and dry_run["ok"]:
        execution = execute_plan(run_dir, plan)
        status = "completed" if execution.get("ok") else "failed"
        summarize_somatic_artifacts(run_dir, validation, pairs, args)
    visuals = write_visuals(run_dir, status, validation, resource_plan)
    resource_outputs = ngs_resource_gate.resource_output_paths(resource_plan)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="dna_somatic_variants",
        workflow="local_light_gatk_mutect2",
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
            "panel_of_normals": str(args.panel_of_normals.expanduser().resolve())
            if args.panel_of_normals
            else None,
            "germline_resource": str(args.germline_resource.expanduser().resolve())
            if args.germline_resource
            else None,
            "annotation_vcf": str(args.annotation_vcf.expanduser().resolve())
            if args.annotation_vcf
            else None,
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "pairing_table": "validation/pairs.normalized.tsv",
            "command_plan": "workflow/somatic_command_plan.json",
            "qc_summary": "qc/somatic_qc_summary.json",
            "pair_review": "qc/somatic_pair_review.tsv",
            "pair_review_json": "qc/somatic_pair_review.json",
            "filter_reasons": "qc/somatic_filter_reasons.tsv",
            "filtered_vcf_glob": "variants/*.filtered.vcf.gz",
            **resource_outputs,
            **visuals,
        },
        method={
            "caller": "GATK Mutect2",
            "filter": "GATK FilterMutectCalls",
            "tumor_normal_designs": validation.get("designs", []),
            "orientation_bias_model_requested": args.f1r2_orientation_model,
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
