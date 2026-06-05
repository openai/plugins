#!/usr/bin/env python3
"""Run or plan local ATAC-seq alignment, QC, peak, signal, and FRiP artifacts."""

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
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "atacseq_peaks_qc"


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
        errors.append(
            "--genome-size is required for MACS2 peak calling, e.g. hs, mm, or an effective genome size"
        )
    blacklist = args.blacklist_bed.expanduser().resolve() if args.blacklist_bed else None
    if blacklist and not blacklist.exists():
        errors.append(f"blacklist BED does not exist: {blacklist}")
    tss_bed = args.tss_bed.expanduser().resolve() if args.tss_bed else None
    if tss_bed and not tss_bed.exists():
        warnings.append(
            f"TSS BED does not exist; TSS enrichment commands will be skipped: {tss_bed}"
        )
    if getattr(args, "run_motifs", False) and not getattr(args, "motif_genome", None):
        errors.append(
            "--run-motifs requires --motif-genome, for example hg38, mm10, or a HOMER genome identifier"
        )

    for row_index, row in enumerate(rows, start=2):
        sample = normalize_sample_name(
            row.get("sample") or row.get("sample_id"), f"row_{row_index}"
        )
        bam = resolve_path(row.get("bam") or row.get("alignment"), sample_sheet.parent)
        r1 = resolve_path(row.get("r1") or row.get("fastq_1"), sample_sheet.parent)
        r2 = resolve_path(row.get("r2") or row.get("fastq_2"), sample_sheet.parent)
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
        samples.append(
            {
                "sample": sample,
                "condition": row.get("condition", ""),
                "replicate": row.get("replicate", ""),
                "layout": layout,
                "bam": str(bam) if bam else "",
                "r1": str(r1) if r1 else "",
                "r2": str(r2) if r2 else "",
                "row_index": str(row_index),
            }
        )
    if not samples:
        errors.append("no usable ATAC-seq samples found")
    validation = {
        "ok": not errors,
        "sample_sheet": str(sample_sheet),
        "columns": columns,
        "sample_count": len(samples),
        "blacklist_bed": str(blacklist) if blacklist else None,
        "tss_bed": str(tss_bed) if tss_bed else None,
        "genome_size": args.genome_size,
        "run_motifs": getattr(args, "run_motifs", False),
        "motif_genome": getattr(args, "motif_genome", None),
        "motif_size": getattr(args, "motif_size", None),
        "errors": errors,
        "warnings": warnings,
    }
    return validation, samples


def sample_bam_path(sample: dict[str, str]) -> str:
    return (
        sample["bam"] if sample["layout"] == "bam" else f"alignment/{sample['sample']}.sorted.bam"
    )


def build_plan(args: argparse.Namespace, samples: list[dict[str, str]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    for sample in samples:
        name = sample["sample"]
        bam = sample_bam_path(sample)
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
            name,
            "--outdir",
            "peaks",
            "--keep-dup",
            "all",
        ]
        plan.append(
            command_plan_entry(
                f"{name}: MACS2 peaks", peak_cmd, outputs=[f"peaks/{name}_peaks.narrowPeak"]
            )
        )
        if args.blacklist_bed:
            plan.append(
                command_plan_entry(
                    f"{name}: blacklist-filter peaks",
                    f"{shell_join(['bedtools', 'intersect', '-v', '-a', f'peaks/{name}_peaks.narrowPeak', '-b', args.blacklist_bed.expanduser().resolve()])} > {shell_join([f'peaks/{name}.blacklist_filtered.narrowPeak'])}",
                    outputs=[f"peaks/{name}.blacklist_filtered.narrowPeak"],
                )
            )
        plan.append(
            command_plan_entry(
                f"{name}: FRiP numerator",
                f"{shell_join(['bedtools', 'intersect', '-u', '-abam', filtered_bam, '-b', f'peaks/{name}_peaks.narrowPeak'])} | {shell_join(['samtools', 'view', '-c', '-'])} > {shell_join([f'qc/{name}.frip_reads.txt'])}",
                outputs=[f"qc/{name}.frip_reads.txt"],
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
        if args.tss_bed:
            plan.append(
                command_plan_entry(
                    f"{name}: TSS enrichment matrix",
                    [
                        "computeMatrix",
                        "reference-point",
                        "-S",
                        f"tracks/{name}.bw",
                        "-R",
                        args.tss_bed.expanduser().resolve(),
                        "--referencePoint",
                        "TSS",
                        "-b",
                        "2000",
                        "-a",
                        "2000",
                        "-o",
                        f"qc/{name}.tss_matrix.gz",
                    ],
                    outputs=[f"qc/{name}.tss_matrix.gz"],
                )
            )
            plan.append(
                command_plan_entry(
                    f"{name}: TSS enrichment profile",
                    [
                        "plotProfile",
                        "-m",
                        f"qc/{name}.tss_matrix.gz",
                        "-out",
                        f"qc/{name}.tss_profile.png",
                        "--plotTitle",
                        f"{name} TSS enrichment",
                    ],
                    outputs=[f"qc/{name}.tss_profile.png"],
                )
            )
            plan.append(
                command_plan_entry(
                    f"{name}: TSS enrichment heatmap",
                    [
                        "plotHeatmap",
                        "-m",
                        f"qc/{name}.tss_matrix.gz",
                        "-out",
                        f"qc/{name}.tss_heatmap.png",
                        "--plotTitle",
                        f"{name} TSS enrichment",
                    ],
                    outputs=[f"qc/{name}.tss_heatmap.png"],
                )
            )
        if getattr(args, "run_motifs", False):
            motif_genome = getattr(args, "motif_genome", None) or "MISSING_MOTIF_GENOME"
            motif_size = str(getattr(args, "motif_size", "given"))
            motif_peak = (
                f"peaks/{name}.blacklist_filtered.narrowPeak"
                if args.blacklist_bed
                else f"peaks/{name}_peaks.narrowPeak"
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
            f"cat peaks/*_peaks.narrowPeak 2>/dev/null | sort -k1,1 -k2,2n | {shell_join(['bedtools', 'merge', '-i', '-'])} > peaks/consensus_peaks.bed",
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
        ["sample", "condition", "replicate", "layout", "bam", "r1", "r2", "row_index"],
    )
    write_json(run_dir / "workflow" / "atacseq_command_plan.json", {"commands": plan})
    write_command_script(run_dir / "commands.sh", [item["command"] for item in plan])
    write_json(
        run_dir / "qc" / "atac_qc_contract.json",
        {
            "required_review_metrics": [
                "alignment_rate",
                "duplicate_rate",
                "mitochondrial_fraction",
                "insert_size_periodicity",
                "TSS_enrichment",
                "FRiP",
                "blacklist_overlap",
                "replicate_concordance",
            ],
            "available_after_execution": [
                "qc/*.flagstat.txt",
                "qc/*.insert_sizes.txt",
                "qc/*.frip_reads.txt",
                "qc/*.filtered_reads.txt",
                "peaks/*.narrowPeak",
                "tracks/*.bw",
            ],
            "warnings": validation.get("warnings", []),
        },
    )
    summarize_epigenomics_outputs(
        run_dir, samples, peak_mode="narrow", output_prefix="atacseq_qc", title="ATAC-seq"
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
            title="ATAC Samples",
            path="validation/samples.normalized.tsv",
            kind="table",
            status="created",
            description="Normalized ATAC sample table.",
        ),
        artifact_entry(
            artifact_id="command_plan",
            title="ATAC Command Plan",
            path="workflow/atacseq_command_plan.json",
            kind="json",
            status="created",
            description="Alignment, filtering, peak, FRiP, signal, and TSS command plan.",
        ),
        artifact_entry(
            artifact_id="qc_contract",
            title="ATAC QC Contract",
            path="qc/atac_qc_contract.json",
            kind="json",
            status="created",
            description="Metrics required for interpretation and artifacts expected after execution.",
        ),
        artifact_entry(
            artifact_id="qc_summary",
            title="ATAC QC Summary",
            path="qc/atacseq_qc_summary.tsv",
            kind="table",
            status="created",
            description="Parsed per-sample alignment, insert-size, FRiP, peak, TSS, motif, and track state.",
        ),
        artifact_entry(
            artifact_id="qc_dashboard",
            title="ATAC QC Dashboard",
            path="qc/atacseq_qc_dashboard.html",
            kind="html",
            status="created",
            description="Native dashboard summarizing FRiP, peak counts, insert sizes, track state, and caveats.",
        ),
        artifact_entry(
            artifact_id="frip_peak_overview",
            title="FRiP And Peak Plot",
            path="qc/atacseq_qc_frip_peak_overview.svg",
            kind="svg",
            status="created",
            description="Compact FRiP and peak-count plot generated from parsed run artifacts.",
        ),
        artifact_entry(
            artifact_id="insert_size_distribution",
            title="Insert-Size Plot",
            path="qc/atacseq_qc_insert_size_distribution.svg",
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
            artifact_id="consensus_peaks",
            title="Consensus Peaks",
            path="peaks/consensus_peaks.bed",
            kind="bed",
            status="created"
            if (run_dir / "peaks" / "consensus_peaks.bed").exists()
            else "not_available",
            description="Merged consensus peak set after execution.",
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
        title="ATAC-seq Peaks QC Review",
        description="Review surface for ATAC-seq alignment, peak, FRiP, TSS, and track outputs.",
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
    }


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# ATAC-seq Peaks QC Run Summary",
        "",
        f"Status: `{status}`",
        f"Samples parsed: `{validation.get('sample_count', 0)}`",
        "",
        "## Key Artifacts",
        "",
        "- `workflow/atacseq_command_plan.json`",
        "- `qc/atac_qc_contract.json`",
        "- `qc/atacseq_qc_summary.tsv` and `qc/atacseq_qc_summary.json`",
        "- `qc/atacseq_qc_dashboard.html`, `qc/atacseq_qc_frip_peak_overview.svg`, and `qc/atacseq_qc_insert_size_distribution.svg`",
        "- `peaks/*.narrowPeak`, `peaks/consensus_peaks.bed`, and `tracks/*.bw` when executed",
        "- `tracks/browser_tracks.tsv`, `tracks/browser_track_preview.html`, `tracks/ucsc_track_lines.txt`, and `tracks/igv_session.xml`",
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
    parser.add_argument("--bowtie2-index")
    parser.add_argument("--bam-only", action="store_true")
    parser.add_argument("--genome-size", required=True)
    parser.add_argument("--blacklist-bed", type=Path)
    parser.add_argument("--tss-bed", type=Path)
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
    parser.add_argument("--run-id", default=slug_timestamp("atacseq-peaks-qc"))
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
        pipeline="atacseq_peaks_qc",
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
    if args.execute and args.tss_bed:
        required_tools.extend(["computeMatrix", "plotProfile", "plotHeatmap"])
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
            "computeMatrix",
            "plotProfile",
            "plotHeatmap",
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
        "detail": "ATAC sample, metadata, and backend tool validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    status = "blocked" if not dry_run["ok"] else "validated"
    execution = None
    if args.execute and dry_run["ok"]:
        execution = execute_plan(run_dir, plan)
        status = "completed" if execution.get("ok") else "failed"
        summarize_epigenomics_outputs(
            run_dir, samples, peak_mode="narrow", output_prefix="atacseq_qc", title="ATAC-seq"
        )
    visuals = write_visuals(run_dir, status, validation, resource_plan)
    resource_outputs = ngs_resource_gate.resource_output_paths(resource_plan)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="atacseq_peaks_qc",
        workflow="local_light_atacseq_alignment_peaks_qc",
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
            "tss_bed": str(args.tss_bed.expanduser().resolve()) if args.tss_bed else None,
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "sample_table": "validation/samples.normalized.tsv",
            "command_plan": "workflow/atacseq_command_plan.json",
            "qc_contract": "qc/atac_qc_contract.json",
            "qc_summary": "qc/atacseq_qc_summary.tsv",
            "qc_summary_json": "qc/atacseq_qc_summary.json",
            "qc_dashboard": "qc/atacseq_qc_dashboard.html",
            "frip_peak_overview": "qc/atacseq_qc_frip_peak_overview.svg",
            "insert_size_distribution": "qc/atacseq_qc_insert_size_distribution.svg",
            "peaks": "peaks/*.narrowPeak",
            "consensus_peaks": "peaks/consensus_peaks.bed",
            "tracks": "tracks/*.bw",
            "browser_tracks": "tracks/browser_tracks.tsv",
            "browser_track_preview": "tracks/browser_track_preview.html",
            "igv_session": "tracks/igv_session.xml",
            "motif_summary": "motifs/motif_summary.tsv",
            **resource_outputs,
            **visuals,
        },
        method={
            "peak_caller": "MACS2",
            "frip": "bedtools intersect + samtools count",
            "tss_enrichment": "deepTools computeMatrix/plotProfile/plotHeatmap when --tss-bed is supplied",
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
