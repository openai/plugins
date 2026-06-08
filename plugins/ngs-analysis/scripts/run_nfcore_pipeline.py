#!/usr/bin/env python3
"""Generate and optionally execute a standardized nf-core pipeline run envelope."""

from __future__ import annotations

import argparse
import shlex
from pathlib import Path
from typing import Any

import ngs_reference_manager
from ngs_planner_utils import shell_join, write_command_script
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
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "nfcore"

NFCORE_PIPELINES: dict[str, dict[str, Any]] = {
    "rnaseq": {
        "workflow": "nf-core/rnaseq",
        "description": "Bulk RNA-seq FASTQ to QC, alignment/pseudoalignment, quantification, and MultiQC.",
        "resource_pipeline": "bulk_rnaseq_counts_qc",
    },
    "scrnaseq": {
        "workflow": "nf-core/scrnaseq",
        "description": "Single-cell or single-nucleus RNA-seq FASTQ to count matrices and QC outputs.",
        "resource_pipeline": "scrnaseq_fastq_to_count",
    },
    "sarek": {
        "workflow": "nf-core/sarek",
        "description": "DNA germline/somatic variant analysis using nf-core/sarek.",
        "resource_pipeline": "dna_variant_calling",
    },
    "atacseq": {
        "workflow": "nf-core/atacseq",
        "description": "ATAC-seq alignment, QC, peak calling, consensus peaks, and signal outputs.",
        "resource_pipeline": "atacseq_peaks_qc",
    },
    "chipseq": {
        "workflow": "nf-core/chipseq",
        "description": "ChIP-seq alignment, QC, peak calling, consensus peaks, and signal outputs.",
        "resource_pipeline": "chip_cutrun_peaks_qc",
    },
    "cutandrun": {
        "workflow": "nf-core/cutandrun",
        "description": "CUT&RUN/CUT&Tag alignment, QC, peak calling, and reporting.",
        "resource_pipeline": "chip_cutrun_peaks_qc",
    },
    "ampliseq": {
        "workflow": "nf-core/ampliseq",
        "description": "Marker-gene amplicon denoising, taxonomy, diversity, and reporting.",
        "resource_pipeline": "amplicon_microbiome",
    },
    "taxprofiler": {
        "workflow": "nf-core/taxprofiler",
        "description": "Shotgun metagenomics taxonomic and optional functional profiling.",
        "resource_pipeline": "shotgun_metagenomics",
    },
}


def validate_inputs(args: argparse.Namespace) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    sample_sheet = args.sample_sheet.expanduser().resolve()
    if not sample_sheet.exists():
        errors.append(f"sample sheet does not exist: {sample_sheet}")
    params_file = args.params_file.expanduser().resolve() if args.params_file else None
    if params_file and not params_file.exists():
        errors.append(f"params file does not exist: {params_file}")
    if args.pipeline not in NFCORE_PIPELINES:
        errors.append(f"unsupported nf-core pipeline: {args.pipeline}")
    if not args.profile:
        warnings.append(
            "no Nextflow profile was provided; nf-core usually needs docker, singularity, conda, or institutional profiles"
        )
    return {
        "ok": not errors,
        "input_ok": not errors,
        "pipeline": args.pipeline,
        "workflow": NFCORE_PIPELINES.get(args.pipeline, {}).get("workflow"),
        "sample_sheet": str(sample_sheet),
        "params_file": str(params_file) if params_file else None,
        "profile": args.profile,
        "revision": args.revision,
        "errors": errors,
        "warnings": warnings,
    }


def resource_genome_build(args: argparse.Namespace) -> str | None:
    return args.genome_build or args.genome


def summarize_resource_blockers(resource_plan: dict[str, Any] | None) -> list[str]:
    if resource_plan is None or resource_plan.get("ok"):
        return []
    blockers = []
    for item in resource_plan.get("missing_required", []):
        detail = item.get("error") or ", ".join(item.get("missing", [])) or "root not configured"
        blockers.append(
            f"required {item.get('kind')} bundle `{item.get('bundle')}` is not ready: {detail}"
        )
    return blockers


def write_resource_plan(args: argparse.Namespace, run_dir: Path) -> dict[str, Any] | None:
    if args.skip_resource_plan:
        return None
    run_root = run_dir.resolve()
    pipeline = NFCORE_PIPELINES[args.pipeline]["resource_pipeline"]
    plan = ngs_reference_manager.plan_pipeline_resources(
        pipeline,
        genome_build=resource_genome_build(args),
        bundle_roots=ngs_reference_manager.parse_bundle_roots(args.bundle_root),
        include_optional=args.include_optional_resources,
        include_checksums=args.resource_checksums,
    )
    outputs = ngs_reference_manager.write_resource_plan_outputs(plan, run_root / "resources")
    plan["outputs"] = {
        key: str(Path(value).resolve().relative_to(run_root)) for key, value in outputs.items()
    }
    return plan


def merge_resource_status(
    validation: dict[str, Any], resource_plan: dict[str, Any] | None
) -> dict[str, Any]:
    merged = dict(validation)
    errors = list(merged.get("errors", []))
    warnings = list(merged.get("warnings", []))
    if resource_plan is None:
        merged["resource_plan_ok"] = None
        merged["resource_plan_skipped"] = True
        warnings.append(
            "resource readiness plan was skipped; perform a separate reference/database check before marking the run ready"
        )
    else:
        merged["resource_plan_skipped"] = False
        merged["resource_plan_ok"] = bool(resource_plan.get("ok"))
        merged["resource_plan_pipeline"] = resource_plan.get("pipeline")
        merged["resource_plan_path"] = resource_plan.get("outputs", {}).get("resource_plan")
        merged["missing_required_resources"] = resource_plan.get("missing_required", [])
        errors.extend(summarize_resource_blockers(resource_plan))
    merged["errors"] = errors
    merged["warnings"] = warnings
    merged["ok"] = bool(validation.get("ok")) and (
        resource_plan is None or bool(resource_plan.get("ok"))
    )
    return merged


def generated_params(args: argparse.Namespace, run_dir: Path) -> dict[str, Any]:
    params: dict[str, Any] = {
        "input": str(args.sample_sheet.expanduser().resolve()),
        "outdir": str((run_dir / "results").resolve()),
    }
    if args.genome:
        params["genome"] = args.genome
    if args.fasta:
        params["fasta"] = str(args.fasta.expanduser().resolve())
    if args.gtf:
        params["gtf"] = str(args.gtf.expanduser().resolve())
    if args.extra_param:
        for item in args.extra_param:
            if "=" not in item:
                raise ValueError(f"--extra-param must use key=value syntax, got: {item}")
            key, value = item.split("=", 1)
            params[key] = value
    return params


def build_command(args: argparse.Namespace, run_dir: Path, params_path: Path) -> str:
    workflow = NFCORE_PIPELINES[args.pipeline]["workflow"]
    cmd: list[str | Path] = [
        "nextflow",
        "run",
        workflow,
        "-params-file",
        params_path,
        "-work-dir",
        run_dir / "work",
        "-with-report",
        run_dir / "workflow" / "nextflow_report.html",
        "-with-timeline",
        run_dir / "workflow" / "timeline.html",
        "-with-trace",
        run_dir / "workflow" / "trace.txt",
        "-with-dag",
        run_dir / "workflow" / "dag.html",
    ]
    if args.revision:
        cmd.extend(["-r", args.revision])
    if args.profile:
        cmd.extend(["-profile", args.profile])
    base = shell_join(cmd)
    if args.nextflow_arg:
        base = " ".join([base, *args.nextflow_arg])
    return base


def execute_command(run_dir: Path, command: str) -> dict[str, Any]:
    return run_cmd(["bash", "-c", command], run_dir, timeout=None)


def write_summary(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None,
) -> None:
    lines = [
        "# nf-core Pipeline Run Summary",
        "",
        f"Status: `{status}`",
        f"Pipeline: `{validation.get('workflow')}`",
        f"Profile: `{validation.get('profile') or 'not provided'}`",
        "",
        "## Key Artifacts",
        "",
        "- `workflow/params.generated.json`",
        "- `workflow/nfcore_command.json`",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `commands.sh`",
        "- `workflow/nextflow_report.html`, `timeline.html`, `trace.txt`, and `dag.html` when executed",
        "- `results/` published outputs when execution completes",
        "- `visualizations/index.html`",
        "- `run_manifest.json` and `artifact_index.json`",
        "",
    ]
    if validation.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {item}" for item in validation["warnings"])
        lines.append("")
    if resource_plan is not None:
        lines.extend(["## Resource Readiness", ""])
        lines.append(f"Ready: `{str(resource_plan.get('ok')).lower()}`")
        lines.append(f"Resource contract: `{resource_plan.get('pipeline')}`")
        lines.append(
            f"Setup plan: `{resource_plan.get('outputs', {}).get('resource_setup_summary', 'resources/resource_setup_plan.md')}`"
        )
        for item in resource_plan.get("resources", []):
            state = "ready" if item.get("ok") else "missing"
            required = "required" if item.get("required") else "optional"
            lines.append(f"- `{item.get('bundle')}` ({item.get('kind')}, {required}): {state}")
        lines.append("")
    if validation.get("errors"):
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {item}" for item in validation["errors"])
    write_text(run_dir / "summary.md", "\n".join(lines) + "\n")


def write_visuals(
    run_dir: Path,
    status: str,
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None,
) -> dict[str, str]:
    entries = [
        artifact_entry(
            artifact_id="params",
            title="Generated Params",
            path="workflow/params.generated.json",
            kind="json",
            status="created",
            description="Nextflow params generated by the plugin adapter.",
        ),
        artifact_entry(
            artifact_id="command",
            title="Nextflow Command",
            path="workflow/nfcore_command.json",
            kind="json",
            status="created",
            description="Exact command used or ready to run.",
        ),
        artifact_entry(
            artifact_id="nextflow_report",
            title="Nextflow Report",
            path="workflow/nextflow_report.html",
            kind="html",
            status="created"
            if (run_dir / "workflow" / "nextflow_report.html").exists()
            else "not_available",
            description="Nextflow execution report, emitted after a successful or partially successful run.",
        ),
    ]
    if resource_plan is not None:
        entries.extend(
            [
                artifact_entry(
                    artifact_id="resource_readiness",
                    title="Resource Readiness",
                    path="resources/resource_readiness.md",
                    kind="markdown",
                    status="created",
                    description="Human-readable reference/database readiness gate for this nf-core run.",
                ),
                artifact_entry(
                    artifact_id="resource_manifest",
                    title="Resource Manifest",
                    path="resources/resource_manifest.tsv",
                    kind="table",
                    status="created",
                    description="Pipeline resource bundles, roots, env vars, and missing-file counts.",
                ),
                artifact_entry(
                    artifact_id="resource_plan",
                    title="Resource Plan",
                    path="resources/resource_plan.json",
                    kind="json",
                    status="created",
                    description="Structured resource readiness plan used to gate this run.",
                ),
                artifact_entry(
                    artifact_id="resource_setup_plan",
                    title="Resource Setup Plan",
                    path="resources/resource_setup_plan.md",
                    kind="markdown",
                    status="created",
                    description="Actionable setup checklist for missing reference/database bundles.",
                ),
                artifact_entry(
                    artifact_id="resource_setup_commands",
                    title="Resource Setup Commands",
                    path="resources/resource_setup_commands.sh",
                    kind="script",
                    status="created",
                    description="Reviewed shell skeleton with commented setup hints and validation commands.",
                ),
            ]
        )
    review_outputs = add_vcf_review_notebook_entry(
        run_dir,
        entries,
        title="nf-core VCF Review",
        object_items=[
            ("Nextflow Report", "workflow/nextflow_report.html"),
            ("Run Summary", "summary.md"),
        ],
    )
    index = write_visualization_index(
        run_dir,
        title="nf-core Execution Review",
        description="Standard review surface for nf-core execution.",
        entries=entries,
        notes=[*validation.get("warnings", []), *summarize_resource_blockers(resource_plan)],
        analysis_intent="real_analysis" if status != "blocked" else "blocked_preflight",
        provenance_summary={
            "pipeline": validation.get("workflow"),
            "status": status,
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
    parser.add_argument("--pipeline", choices=sorted(NFCORE_PIPELINES), required=True)
    parser.add_argument("--sample-sheet", type=Path, required=True)
    parser.add_argument("--params-file", type=Path)
    parser.add_argument(
        "--profile", help="Nextflow profile, e.g. docker, singularity, conda, or a site profile."
    )
    parser.add_argument("--revision", help="Pinned nf-core revision/tag/commit.")
    parser.add_argument("--genome")
    parser.add_argument(
        "--genome-build",
        help="Genome build/alias for the reference resource plan. Defaults to --genome when omitted.",
    )
    parser.add_argument("--fasta", type=Path)
    parser.add_argument("--gtf", type=Path)
    parser.add_argument(
        "--extra-param",
        action="append",
        default=[],
        help="Additional generated params as key=value. May be repeated.",
    )
    parser.add_argument(
        "--nextflow-arg",
        action="append",
        default=[],
        help="Raw extra Nextflow argument appended to the command. May be repeated.",
    )
    parser.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Resource bundle override formatted as bundle=/path. May be repeated.",
    )
    parser.add_argument(
        "--include-optional-resources",
        action="store_true",
        help="Include optional resource bundles such as Bracken/HUMAnN in readiness checks.",
    )
    parser.add_argument(
        "--resource-checksums",
        action="store_true",
        help="Compute checksums for resource files below the reference-manager checksum threshold.",
    )
    parser.add_argument(
        "--skip-resource-plan",
        action="store_true",
        help="Generate the nf-core run envelope without gating on reference/database bundle readiness.",
    )
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def serializable_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()
    }


def main() -> int:
    args = parse_args()
    run_id = args.run_id or slug_timestamp(f"nfcore-{args.pipeline}")
    run_dir = (args.outdir or (DEFAULT_RUN_ROOT / args.pipeline / run_id)).expanduser().resolve()
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "workflow").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    input_validation = validate_inputs(args)
    resource_plan = write_resource_plan(args, run_dir)
    validation = merge_resource_status(input_validation, resource_plan)
    tool_status = tool_preflight(["nextflow"], optional=[])
    params = generated_params(args, run_dir)
    generated_params_path = run_dir / "workflow" / "params.generated.json"
    write_json(generated_params_path, params)
    command = build_command(args, run_dir, generated_params_path)
    write_json(
        run_dir / "workflow" / "nfcore_command.json",
        {"command": command, "argv_preview": shlex.split(command)},
    )
    write_command_script(run_dir / "commands.sh", [command])
    write_json(run_dir / "config.json", {**serializable_args(args), "run_dir": str(run_dir)})
    write_json(run_dir / "validation" / "input_validation_summary.json", input_validation)
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions({"nextflow": ["nextflow", "-version"]}),
    )
    dry_run = {
        "ok": validation["ok"] and tool_status["ok"],
        "detail": "nf-core inputs, params, and Nextflow runtime validated",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    status = "blocked" if not dry_run["ok"] else "validated"
    execution = None
    if args.execute and dry_run["ok"]:
        execution = execute_command(run_dir, command)
        write_json(run_dir / "logs" / "nextflow_execute.json", execution)
        write_text(run_dir / "logs" / "nextflow_execute.log", str(execution.get("stdout_tail", "")))
        status = "completed" if execution.get("ok") else "failed"
    visuals = write_visuals(run_dir, status, validation, resource_plan)
    resource_outputs = resource_plan.get("outputs", {}) if resource_plan else {}
    write_standard_manifest(
        run_dir,
        run_id=run_id,
        lane=f"nfcore_{args.pipeline}",
        workflow=NFCORE_PIPELINES[args.pipeline]["workflow"],
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "params_file": str(args.params_file.expanduser().resolve())
            if args.params_file
            else None,
            "generated_params": "workflow/params.generated.json",
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "published_results": "results/",
            "nextflow_report": "workflow/nextflow_report.html",
            "timeline": "workflow/timeline.html",
            "trace": "workflow/trace.txt",
            "dag": "workflow/dag.html",
            **resource_outputs,
            **visuals,
        },
        method={
            "adapter": "nf-core",
            "pipeline": NFCORE_PIPELINES[args.pipeline],
            "resource_plan": resource_plan,
        },
        audit={"resource_readiness": resource_plan} if resource_plan else None,
        review_bundle=visuals,
    )
    write_summary(run_dir, status, validation, resource_plan)
    write_json(
        run_dir / "artifact_index.json",
        build_artifact_index(run_dir, patterns=None, extra_roots={"results": run_dir / "results"}),
    )
    print(run_dir)
    return 1 if status in {"blocked", "failed"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
