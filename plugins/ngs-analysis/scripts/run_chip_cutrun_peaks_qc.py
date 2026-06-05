#!/usr/bin/env python3
"""Run or plan local ChIP-seq, CUT&RUN, or CUT&Tag peak/QC artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import ngs_resource_gate
from ngs_epigenomics_utils import summarize_epigenomics_outputs
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
from ngs_visualization_utils import artifact_entry, write_visualization_index

WORKSPACE_ROOT = Path.cwd()
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "chip_cutrun_peaks_qc"


def is_control_row(target: str | None, condition: str | None, sample: str | None) -> bool:
    labels = {
        str(target or "").strip().lower(),
        str(condition or "").strip().lower(),
        str(sample or "").strip().lower(),
    }
    return any(
        label in {"input", "igg", "control", "no_antibody", "no-antibody"} for label in labels
    )


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
    if not args.bam_only and not args.bowtie2_index:
        warnings.append(
            "no --bowtie2-index was provided; FASTQ rows can only be planned, not aligned"
        )
    if not args.genome_size:
        errors.append("--genome-size is required for MACS2 peak calling")
    blacklist = args.blacklist_bed.expanduser().resolve() if args.blacklist_bed else None
    if blacklist and not blacklist.exists():
        errors.append(f"blacklist BED does not exist: {blacklist}")
    if getattr(args, "run_motifs", False) and not getattr(args, "motif_genome", None):
        errors.append(
            "--run-motifs requires --motif-genome, for example hg38, mm10, or a HOMER genome identifier"
        )
    for row_index, row in enumerate(rows, start=2):
        sample = normalize_sample_name(
            row.get("sample") or row.get("sample_id"), f"row_{row_index}"
        )
        condition = row.get("condition", "")
        target = row.get("target") or args.target_class
        control_sample = (
            normalize_sample_name(
                row.get("control") or row.get("control_sample") or row.get("negative_control"), ""
            )
            or ""
        )
        bam = resolve_path(row.get("bam") or row.get("alignment"), sample_sheet.parent)
        r1 = resolve_path(row.get("r1") or row.get("fastq_1"), sample_sheet.parent)
        r2 = resolve_path(row.get("r2") or row.get("fastq_2"), sample_sheet.parent)
        control_bam = resolve_path(
            row.get("control_bam") or row.get("input_bam") or row.get("igg_bam"),
            sample_sheet.parent,
        )
        if bam:
            if not bam.exists():
                errors.append(f"row {row_index}: BAM does not exist: {bam}")
            layout = "bam"
        elif r1:
            if not r1.exists():
                errors.append(f"row {row_index}: R1 FASTQ does not exist: {r1}")
            if r2 and not r2.exists():
                errors.append(f"row {row_index}: R2 FASTQ does not exist: {r2}")
            layout = "fastq_pe" if r2 else "fastq_se"
        else:
            errors.append(f"row {row_index}: provide bam/alignment or r1/fastq_1")
            continue
        if control_bam and not control_bam.exists():
            warnings.append(f"row {row_index}: control BAM does not exist: {control_bam}")
        samples.append(
            {
                "sample": sample,
                "condition": condition,
                "replicate": row.get("replicate", ""),
                "target": target,
                "layout": layout,
                "bam": str(bam) if bam else "",
                "r1": str(r1) if r1 else "",
                "r2": str(r2) if r2 else "",
                "control_bam": str(control_bam) if control_bam else "",
                "control_sample": control_sample,
                "is_control": str(is_control_row(target, condition, sample)).lower(),
                "row_index": str(row_index),
            }
        )
    sample_names = {sample["sample"] for sample in samples}
    for sample in samples:
        control_sample = sample.get("control_sample", "")
        if control_sample and control_sample not in sample_names:
            errors.append(
                f"sample {sample['sample']}: referenced control sample does not exist in sample sheet: {control_sample}"
            )
        if (
            args.assay == "chipseq"
            and sample["is_control"] != "true"
            and not control_sample
            and not sample["control_bam"]
        ):
            warnings.append(
                f"row {sample['row_index']}: ChIP-seq usually needs input/IgG control for robust peak calling"
            )
    if not samples:
        errors.append("no usable ChIP/CUT&RUN samples found")
    validation = {
        "ok": not errors,
        "sample_sheet": str(sample_sheet),
        "assay": args.assay,
        "columns": columns,
        "sample_count": len(samples),
        "blacklist_bed": str(blacklist) if blacklist else None,
        "genome_size": args.genome_size,
        "peak_mode": args.peak_mode,
        "run_motifs": getattr(args, "run_motifs", False),
        "motif_genome": getattr(args, "motif_genome", None),
        "motif_size": getattr(args, "motif_size", None),
        "errors": errors,
        "warnings": warnings,
    }
    return validation, samples


def aligned_bam(sample: dict[str, str]) -> str:
    return (
        sample["bam"] if sample["layout"] == "bam" else f"alignment/{sample['sample']}.sorted.bam"
    )


def build_plan(args: argparse.Namespace, samples: list[dict[str, str]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    samples_by_name = {sample["sample"]: sample for sample in samples}

    for sample in samples:
        name = sample["sample"]
        bam = aligned_bam(sample)
        filtered_bam = f"alignment/{name}.filtered.bam"
        if sample["layout"].startswith("fastq"):
            bowtie = [
                "bowtie2",
                "-x",
                args.bowtie2_index or "MISSING_BOWTIE2_INDEX",
                "-p",
                str(args.threads),
            ]
            if sample["r2"]:
                bowtie.extend(["-1", sample["r1"], "-2", sample["r2"]])
            else:
                bowtie.extend(["-U", sample["r1"]])
            plan.append(
                command_plan_entry(
                    f"{name}: align and sort",
                    f"{shell_join(bowtie)} | {shell_join(['samtools', 'sort', '-@', str(args.threads), '-o', bam, '-'])}",
                    outputs=[bam],
                )
            )
            plan.append(
                command_plan_entry(f"{name}: index aligned BAM", ["samtools", "index", bam])
            )
        plan.append(
            command_plan_entry(
                f"{name}: filter alignment",
                [
                    "samtools",
                    "view",
                    "-b",
                    "-q",
                    str(args.min_mapq),
                    "-F",
                    "1804",
                    "-o",
                    filtered_bam,
                    bam,
                ],
                outputs=[filtered_bam],
            )
        )
        plan.append(
            command_plan_entry(f"{name}: index filtered BAM", ["samtools", "index", filtered_bam])
        )
        plan.append(
            command_plan_entry(
                f"{name}: flagstat",
                f"{shell_join(['samtools', 'flagstat', filtered_bam])} > {shell_join([f'qc/{name}.flagstat.txt'])}",
                outputs=[f"qc/{name}.flagstat.txt"],
            )
        )
        plan.append(
            command_plan_entry(
                f"{name}: insert sizes",
                f"{shell_join(['samtools', 'view', '-f', '2', filtered_bam])} | awk '{{t=$9; if (t<0) t=-t; if (t>0) print t}}' > {shell_join([f'qc/{name}.insert_sizes.txt'])}",
                outputs=[f"qc/{name}.insert_sizes.txt"],
            )
        )
        plan.append(
            command_plan_entry(
                f"{name}: total filtered reads",
                f"{shell_join(['samtools', 'view', '-c', filtered_bam])} > {shell_join([f'qc/{name}.filtered_reads.txt'])}",
                outputs=[f"qc/{name}.filtered_reads.txt"],
            )
        )
        plan.append(
            command_plan_entry(
                f"{name}: bigWig signal",
                [
                    "bamCoverage",
                    "-b",
                    filtered_bam,
                    "-o",
                    f"tracks/{name}.bw",
                    "--numberOfProcessors",
                    str(args.threads),
                ],
                outputs=[f"tracks/{name}.bw"],
            )
        )

    for sample in samples:
        if sample.get("is_control") == "true":
            continue

        name = sample["sample"]
        filtered_bam = f"alignment/{name}.filtered.bam"
        peak_name = name
        peak_cmd: list[str | Path] = [
            "macs2",
            "callpeak",
            "-t",
            filtered_bam,
            "-f",
            "BAMPE",
            "-g",
            args.genome_size,
            "-n",
            peak_name,
            "--outdir",
            "peaks",
        ]
        control_bam = sample["control_bam"]
        if not control_bam and sample.get("control_sample"):
            control_sample = samples_by_name.get(sample["control_sample"])
            if control_sample:
                control_bam = f"alignment/{control_sample['sample']}.filtered.bam"
        if control_bam:
            peak_cmd.extend(["-c", control_bam])
        if args.peak_mode == "broad":
            peak_cmd.extend(["--broad"])
        plan.append(
            command_plan_entry(
                f"{name}: MACS2 peaks",
                peak_cmd,
                outputs=[
                    f"peaks/{name}_peaks.narrowPeak"
                    if args.peak_mode == "narrow"
                    else f"peaks/{name}_peaks.broadPeak"
                ],
            )
        )
        peak_path = (
            f"peaks/{name}_peaks.narrowPeak"
            if args.peak_mode == "narrow"
            else f"peaks/{name}_peaks.broadPeak"
        )
        if args.blacklist_bed:
            plan.append(
                command_plan_entry(
                    f"{name}: blacklist-filter peaks",
                    f"{shell_join(['bedtools', 'intersect', '-v', '-a', peak_path, '-b', args.blacklist_bed.expanduser().resolve()])} > {shell_join([f'peaks/{name}.blacklist_filtered.{args.peak_mode}Peak'])}",
                    outputs=[f"peaks/{name}.blacklist_filtered.{args.peak_mode}Peak"],
                )
            )
        plan.append(
            command_plan_entry(
                f"{name}: FRiP numerator",
                f"{shell_join(['bedtools', 'intersect', '-u', '-abam', filtered_bam, '-b', peak_path])} | {shell_join(['samtools', 'view', '-c', '-'])} > {shell_join([f'qc/{name}.frip_reads.txt'])}",
                outputs=[f"qc/{name}.frip_reads.txt"],
            )
        )
        if getattr(args, "run_motifs", False):
            motif_genome = getattr(args, "motif_genome", None) or "MISSING_MOTIF_GENOME"
            motif_size = str(getattr(args, "motif_size", "given"))
            motif_peak = (
                f"peaks/{name}.blacklist_filtered.{args.peak_mode}Peak"
                if args.blacklist_bed
                else peak_path
            )
            plan.append(
                command_plan_entry(
                    f"{name}: motif enrichment",
                    [
                        "findMotifsGenome.pl",
                        motif_peak,
                        motif_genome,
                        f"motifs/{name}",
                        "-size",
                        motif_size,
                    ],
                    outputs=[f"motifs/{name}/knownResults.txt", f"motifs/{name}/homerResults.html"],
                )
            )
    plan.append(
        command_plan_entry(
            "consensus peak merge",
            f"cat peaks/*_peaks.{'broadPeak' if args.peak_mode == 'broad' else 'narrowPeak'} 2>/dev/null | sort -k1,1 -k2,2n | {shell_join(['bedtools', 'merge', '-i', '-'])} > peaks/consensus_peaks.bed",
            outputs=["peaks/consensus_peaks.bed"],
        )
    )
    return plan


def write_outputs(
    run_dir: Path,
    validation: dict[str, Any],
    samples: list[dict[str, str]],
    plan: list[dict[str, Any]],
) -> None:
    write_tsv(
        run_dir / "validation" / "samples.normalized.tsv",
        samples,
        [
            "sample",
            "condition",
            "replicate",
            "target",
            "layout",
            "bam",
            "r1",
            "r2",
            "control_bam",
            "control_sample",
            "is_control",
            "row_index",
        ],
    )
    write_json(run_dir / "workflow" / "chip_cutrun_command_plan.json", {"commands": plan})
    write_command_script(run_dir / "commands.sh", [item["command"] for item in plan])
    write_json(
        run_dir / "qc" / "chip_cutrun_qc_contract.json",
        {
            "required_review_metrics": [
                "alignment_rate",
                "duplicate_rate",
                "FRiP",
                "peak_count",
                "blacklist_overlap",
                "control_use",
                "replicate_concordance",
                "signal_tracks",
                "motif_enrichment_if_requested",
            ],
            "available_after_execution": [
                "qc/*.flagstat.txt",
                "qc/*.insert_sizes.txt",
                "qc/*.frip_reads.txt",
                "qc/*.filtered_reads.txt",
                "peaks/*Peak",
                "tracks/*.bw",
                "tracks/browser_tracks.tsv",
                "motifs/motif_summary.tsv",
            ],
            "warnings": validation.get("warnings", []),
        },
    )
    write_json(
        run_dir / "motifs" / "motif_enrichment_plan.json",
        {
            "status": "planned",
            "note": "Motif enrichment requires a motif backend such as HOMER, MEME, or chromVAR and a genome/motif database selected by the user.",
            "enabled": validation.get("run_motifs", False),
            "motif_genome": validation.get("motif_genome"),
            "motif_size": validation.get("motif_size"),
            "input_peak_glob": "peaks/*Peak",
        },
    )
    summarize_epigenomics_outputs(
        run_dir,
        samples,
        peak_mode=validation.get("peak_mode", "narrow"),
        output_prefix="chip_cutrun_qc",
        title="ChIP/CUT&RUN",
    )


def execute_plan(run_dir: Path, plan: list[dict[str, Any]]) -> dict[str, Any]:
    for dirname in ["alignment", "qc", "peaks", "tracks", "logs", "motifs"]:
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


def write_visuals(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> dict[str, str]:
    entries = [
        artifact_entry(
            artifact_id="samples",
            title="ChIP/CUT&RUN Samples",
            path="validation/samples.normalized.tsv",
            kind="table",
            status="created",
            description="Normalized antibody/enrichment sample table.",
        ),
        artifact_entry(
            artifact_id="command_plan",
            title="Peak Calling Command Plan",
            path="workflow/chip_cutrun_command_plan.json",
            kind="json",
            status="created",
            description="Alignment, control-aware peak calling, FRiP, and signal-track commands.",
        ),
        artifact_entry(
            artifact_id="qc_contract",
            title="QC Contract",
            path="qc/chip_cutrun_qc_contract.json",
            kind="json",
            status="created",
            description="Metrics required before interpreting enrichment peaks.",
        ),
        artifact_entry(
            artifact_id="qc_summary",
            title="Epigenomics QC Summary",
            path="qc/chip_cutrun_qc_summary.tsv",
            kind="table",
            status="created",
            description="Parsed per-sample alignment, insert-size, FRiP, peak, motif, and track state.",
        ),
        artifact_entry(
            artifact_id="qc_dashboard",
            title="Epigenomics QC Dashboard",
            path="qc/chip_cutrun_qc_dashboard.html",
            kind="html",
            status="created",
            description="Native dashboard summarizing FRiP, peak counts, insert sizes, track state, control caveats, and motifs.",
        ),
        artifact_entry(
            artifact_id="frip_peak_overview",
            title="FRiP And Peak Plot",
            path="qc/chip_cutrun_qc_frip_peak_overview.svg",
            kind="svg",
            status="created",
            description="Compact FRiP and peak-count plot generated from parsed run artifacts.",
        ),
        artifact_entry(
            artifact_id="insert_size_distribution",
            title="Insert-Size Plot",
            path="qc/chip_cutrun_qc_insert_size_distribution.svg",
            kind="svg",
            status="created",
            description="Native insert-size distribution plot generated from parsed fragment sizes.",
        ),
        artifact_entry(
            artifact_id="browser_tracks",
            title="Browser Track Manifest",
            path="tracks/browser_tracks.tsv",
            kind="table",
            status="created",
            description="bigWig track lines and IGV/UCSC browser handoff metadata.",
        ),
        artifact_entry(
            artifact_id="browser_track_preview",
            title="Browser Track Preview",
            path="tracks/browser_track_preview.html",
            kind="html",
            status="created",
            description="HTML preview of bigWig track paths and UCSC track lines.",
        ),
        artifact_entry(
            artifact_id="motif_plan",
            title="Motif Enrichment Plan",
            path="motifs/motif_enrichment_plan.json",
            kind="json",
            status="created",
            description="Motif backend handoff contract.",
        ),
        artifact_entry(
            artifact_id="motif_summary",
            title="Motif Summary",
            path="motifs/motif_summary.tsv",
            kind="table",
            status="created",
            description="Motif-enrichment output summary when motif backend outputs are present.",
        ),
    ]
    entries.extend(ngs_resource_gate.resource_visual_entries(resource_plan))
    index = write_visualization_index(
        run_dir,
        title="ChIP/CUT&RUN Peaks QC Review",
        description="Review surface for control-aware peak calling, FRiP, signal tracks, and motif handoff.",
        entries=entries,
        notes=[
            *validation.get("warnings", []),
            *ngs_resource_gate.resource_messages(resource_plan),
        ],
        analysis_intent="real_analysis" if status != "blocked" else "blocked_preflight",
        provenance_summary={
            "status": status,
            "assay": validation.get("assay"),
            "sample_count": validation.get("sample_count", 0),
            "resource_plan_ok": validation.get("resource_plan_ok"),
        },
    )
    return {
        "visualization_index": str(index.relative_to(run_dir)),
        "visualization_manifest": "visualizations/visualization_manifest.json",
    }


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# ChIP/CUT&RUN Peaks QC Run Summary",
        "",
        f"Status: `{status}`",
        f"Assay: `{validation.get('assay')}`",
        f"Samples parsed: `{validation.get('sample_count', 0)}`",
        "",
        "## Key Artifacts",
        "",
        "- `workflow/chip_cutrun_command_plan.json`",
        "- `qc/chip_cutrun_qc_contract.json`",
        "- `qc/chip_cutrun_qc_summary.tsv` and `qc/chip_cutrun_qc_summary.json`",
        "- `qc/chip_cutrun_qc_dashboard.html`, `qc/chip_cutrun_qc_frip_peak_overview.svg`, and `qc/chip_cutrun_qc_insert_size_distribution.svg`",
        "- `peaks/*Peak`, `peaks/consensus_peaks.bed`, and `tracks/*.bw` when executed",
        "- `tracks/browser_tracks.tsv`, `tracks/browser_track_preview.html`, `tracks/ucsc_track_lines.txt`, and `tracks/igv_session.xml`",
        "- `motifs/motif_enrichment_plan.json`",
        "- `motifs/motif_summary.tsv` when motif outputs are generated",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `visualizations/index.html`",
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
    write_text(run_dir / "summary.md", "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-sheet", type=Path, required=True)
    parser.add_argument("--assay", choices=["chipseq", "cutandrun", "cutandtag"], default="chipseq")
    parser.add_argument(
        "--target-class", default="tf", choices=["tf", "histone", "chromatin_regulator", "custom"]
    )
    parser.add_argument("--peak-mode", choices=["narrow", "broad"], default="narrow")
    parser.add_argument("--bowtie2-index")
    parser.add_argument("--bam-only", action="store_true")
    parser.add_argument("--genome-size", required=True)
    parser.add_argument("--blacklist-bed", type=Path)
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
    parser.add_argument("--run-motifs", action="store_true")
    parser.add_argument("--motif-genome")
    parser.add_argument("--motif-size", default="given")
    parser.add_argument("--min-mapq", type=int, default=30)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--run-id", default=slug_timestamp("chip-cutrun-peaks-qc"))
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
        pipeline="chip_cutrun_peaks_qc",
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
    needs_alignment = any(row["layout"].startswith("fastq") for row in samples)
    required_tools = (
        ["samtools", "macs2", "bedtools", "bamCoverage"] + (["bowtie2"] if needs_alignment else [])
        if args.execute
        else []
    )
    if args.execute and args.run_motifs:
        required_tools.append("findMotifsGenome.pl")
    optional_tools = [
        name
        for name in [
            "samtools",
            "macs2",
            "bedtools",
            "bamCoverage",
            "bowtie2",
            "findMotifsGenome.pl",
            "multiqc",
        ]
        if name not in required_tools
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
                "samtools": ["samtools", "--version"],
                "macs2": ["macs2", "--version"],
                "bedtools": ["bedtools", "--version"],
                "bowtie2": ["bowtie2", "--version"],
                "bamCoverage": ["bamCoverage", "--version"],
            }
        ),
    )
    write_outputs(run_dir, validation, samples, plan)
    dry_run = {
        "ok": validation["ok"] and (tool_status["ok"] if args.execute else True),
        "detail": "ChIP/CUT&RUN sample, control, metadata, and backend tool validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    status = "blocked" if not dry_run["ok"] else "validated"
    execution = None
    if args.execute and dry_run["ok"]:
        execution = execute_plan(run_dir, plan)
        status = "completed" if execution.get("ok") else "failed"
        summarize_epigenomics_outputs(
            run_dir,
            samples,
            peak_mode=args.peak_mode,
            output_prefix="chip_cutrun_qc",
            title="ChIP/CUT&RUN",
        )
    visuals = write_visuals(run_dir, status, validation, resource_plan)
    resource_outputs = ngs_resource_gate.resource_output_paths(resource_plan)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="chip_cutrun_peaks_qc",
        workflow="local_light_chip_cutrun_alignment_peaks_qc",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "blacklist_bed": str(args.blacklist_bed.expanduser().resolve())
            if args.blacklist_bed
            else None,
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "sample_table": "validation/samples.normalized.tsv",
            "command_plan": "workflow/chip_cutrun_command_plan.json",
            "qc_contract": "qc/chip_cutrun_qc_contract.json",
            "qc_summary": "qc/chip_cutrun_qc_summary.tsv",
            "qc_summary_json": "qc/chip_cutrun_qc_summary.json",
            "qc_dashboard": "qc/chip_cutrun_qc_dashboard.html",
            "frip_peak_overview": "qc/chip_cutrun_qc_frip_peak_overview.svg",
            "insert_size_distribution": "qc/chip_cutrun_qc_insert_size_distribution.svg",
            "peaks": "peaks/*Peak",
            "consensus_peaks": "peaks/consensus_peaks.bed",
            "tracks": "tracks/*.bw",
            "browser_tracks": "tracks/browser_tracks.tsv",
            "browser_track_preview": "tracks/browser_track_preview.html",
            "igv_session": "tracks/igv_session.xml",
            "motif_plan": "motifs/motif_enrichment_plan.json",
            "motif_summary": "motifs/motif_summary.tsv",
            **resource_outputs,
            **visuals,
        },
        method={
            "assay": args.assay,
            "peak_caller": "MACS2",
            "peak_mode": args.peak_mode,
            "frip": "bedtools intersect + samtools count",
            "motif_enrichment": "HOMER findMotifsGenome.pl when --run-motifs is supplied",
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
