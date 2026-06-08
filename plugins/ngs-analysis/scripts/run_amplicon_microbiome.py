#!/usr/bin/env python3
"""Run or plan amplicon ASV, taxonomy, diversity, and visualization backends."""

from __future__ import annotations

import argparse
import html
import math
import subprocess
from pathlib import Path
from typing import Any

import ngs_resource_gate
from ngs_planner_utils import (
    command_plan_entry,
    normalize_sample_name,
    read_table,
    resolve_path,
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
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "amplicon_microbiome_backend"
DADA2_BACKEND_SCRIPT = PLUGIN_ROOT / "workflows" / "amplicon_microbiome" / "run_dada2_backend.R"


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
    if not args.primer_forward or not args.primer_reverse:
        errors.append(
            "both --primer-forward and --primer-reverse are required for full amplicon backend execution"
        )
    if args.taxonomy_classifier:
        classifier = args.taxonomy_classifier.expanduser().resolve()
        if not classifier.exists():
            errors.append(f"taxonomy classifier/database does not exist: {classifier}")
    else:
        warnings.append(
            "no --taxonomy-classifier was provided; ASV generation can be planned but taxonomy assignment is blocked"
        )
    if args.metadata:
        metadata = args.metadata.expanduser().resolve()
        if not metadata.exists():
            errors.append(f"metadata file does not exist: {metadata}")
    else:
        warnings.append(
            "no sample metadata was provided; PERMANOVA and metadata-colored diversity plots will be limited"
        )
    for row_index, row in enumerate(rows, start=2):
        sample = normalize_sample_name(
            first_present(row, ["sample", "sample_id", "sampleID"]), f"row_{row_index}"
        )
        r1 = resolve_path(
            first_present(row, ["r1", "fastq_1", "forwardReads", "read1"]), sample_sheet.parent
        )
        r2 = resolve_path(
            first_present(row, ["r2", "fastq_2", "reverseReads", "read2"]), sample_sheet.parent
        )
        if not r1:
            errors.append(f"row {row_index}: r1/fastq_1/forwardReads is required")
            continue
        if not r1.exists():
            errors.append(f"row {row_index}: R1 FASTQ does not exist: {r1}")
        if r2 and not r2.exists():
            errors.append(f"row {row_index}: R2 FASTQ does not exist: {r2}")
        samples.append(
            {
                "sample": sample,
                "r1": str(r1),
                "r2": str(r2) if r2 else "",
                "row_index": str(row_index),
            }
        )
    if not samples:
        errors.append("no usable amplicon samples found")
    validation = {
        "ok": not errors,
        "sample_sheet": str(sample_sheet),
        "metadata": str(args.metadata.expanduser().resolve()) if args.metadata else None,
        "taxonomy_classifier": str(args.taxonomy_classifier.expanduser().resolve())
        if args.taxonomy_classifier
        else None,
        "backend": args.backend,
        "marker": args.marker,
        "primer_forward": args.primer_forward,
        "primer_reverse": args.primer_reverse,
        "sample_count": len(samples),
        "columns": columns,
        "errors": errors,
        "warnings": warnings,
    }
    return validation, samples


def first_present(row: dict[str, str], names: list[str]) -> str | None:
    for name in names:
        value = row.get(name)
        if value:
            return value
    return None


def build_qiime2_plan(
    args: argparse.Namespace, samples: list[dict[str, str]]
) -> list[dict[str, Any]]:
    paired = any(row["r2"] for row in samples)
    manifest = "workflow/qiime2_manifest.tsv"
    plan = [
        command_plan_entry(
            "import FASTQs",
            [
                "qiime",
                "tools",
                "import",
                "--type",
                "SampleData[PairedEndSequencesWithQuality]"
                if paired
                else "SampleData[SequencesWithQuality]",
                "--input-path",
                manifest,
                "--output-path",
                "qiime2/demux.qza",
                "--input-format",
                "PairedEndFastqManifestPhred33V2" if paired else "SingleEndFastqManifestPhred33V2",
            ],
            outputs=["qiime2/demux.qza"],
        ),
        command_plan_entry(
            "trim primers",
            [
                "qiime",
                "cutadapt",
                "trim-paired" if paired else "trim-single",
                "--i-demultiplexed-sequences",
                "qiime2/demux.qza",
                "--p-front-f",
                args.primer_forward,
                "--p-front-r",
                args.primer_reverse,
                "--o-trimmed-sequences",
                "qiime2/trimmed.qza",
            ],
            outputs=["qiime2/trimmed.qza"],
        ),
        command_plan_entry(
            "DADA2 denoise",
            [
                "qiime",
                "dada2",
                "denoise-paired" if paired else "denoise-single",
                "--i-demultiplexed-seqs",
                "qiime2/trimmed.qza",
                "--p-trunc-len-f",
                str(args.trunc_len_f or 0),
                "--p-trunc-len-r",
                str(args.trunc_len_r or 0),
                "--o-table",
                "qiime2/table.qza",
                "--o-representative-sequences",
                "qiime2/rep-seqs.qza",
                "--o-denoising-stats",
                "qiime2/denoising-stats.qza",
            ],
            outputs=["qiime2/table.qza", "qiime2/rep-seqs.qza"],
        ),
    ]
    if args.taxonomy_classifier:
        plan.append(
            command_plan_entry(
                "assign taxonomy",
                [
                    "qiime",
                    "feature-classifier",
                    "classify-sklearn",
                    "--i-classifier",
                    args.taxonomy_classifier.expanduser().resolve(),
                    "--i-reads",
                    "qiime2/rep-seqs.qza",
                    "--o-classification",
                    "qiime2/taxonomy.qza",
                ],
                outputs=["qiime2/taxonomy.qza"],
            )
        )
    if args.metadata:
        plan.append(
            command_plan_entry(
                "core diversity metrics",
                [
                    "qiime",
                    "diversity",
                    "core-metrics",
                    "--i-table",
                    "qiime2/table.qza",
                    "--p-sampling-depth",
                    str(args.sampling_depth),
                    "--m-metadata-file",
                    args.metadata.expanduser().resolve(),
                    "--output-dir",
                    "qiime2/core-metrics",
                ],
                outputs=["qiime2/core-metrics"],
            )
        )
    plan.append(
        command_plan_entry(
            "export feature table",
            [
                "qiime",
                "tools",
                "export",
                "--input-path",
                "qiime2/table.qza",
                "--output-path",
                "tables/asv_table_export",
            ],
            outputs=["tables/asv_table_export"],
        )
    )
    if args.taxonomy_classifier:
        plan.append(
            command_plan_entry(
                "export taxonomy",
                [
                    "qiime",
                    "tools",
                    "export",
                    "--input-path",
                    "qiime2/taxonomy.qza",
                    "--output-path",
                    "tables/taxonomy_export",
                ],
                outputs=["tables/taxonomy_export"],
            )
        )
    plan.append(
        command_plan_entry(
            "export denoising stats",
            [
                "qiime",
                "tools",
                "export",
                "--input-path",
                "qiime2/denoising-stats.qza",
                "--output-path",
                "tables/denoising_stats_export",
            ],
            outputs=["tables/denoising_stats_export"],
        )
    )
    return plan


def build_nfcore_plan(args: argparse.Namespace) -> list[dict[str, Any]]:
    cmd = [
        "python",
        "plugins/ngs-analysis/scripts/run_nfcore_pipeline.py",
        "--pipeline",
        "ampliseq",
        "--sample-sheet",
        args.sample_sheet.expanduser().resolve(),
        "--extra-param",
        f"FW_primer={args.primer_forward}",
        "--extra-param",
        f"RV_primer={args.primer_reverse}",
    ]
    if args.profile:
        cmd.extend(["--profile", args.profile])
    if args.execute:
        cmd.append("--execute")
    return [command_plan_entry("nf-core/ampliseq handoff", cmd, outputs=["nfcore/ampliseq"])]


def build_plan(args: argparse.Namespace, samples: list[dict[str, str]]) -> list[dict[str, Any]]:
    if args.backend == "qiime2":
        return build_qiime2_plan(args, samples)
    if args.backend == "nf-core/ampliseq":
        return build_nfcore_plan(args)
    cmd: list[str | Path] = [
        "Rscript",
        DADA2_BACKEND_SCRIPT,
        "--sample-sheet",
        args.sample_sheet.expanduser().resolve(),
        "--outdir",
        ".",
        "--primer-forward",
        args.primer_forward,
        "--primer-reverse",
        args.primer_reverse,
        "--threads",
        str(args.threads),
    ]
    if args.trunc_len_f is not None:
        cmd.extend(["--trunc-len-f", str(args.trunc_len_f)])
    if args.trunc_len_r is not None:
        cmd.extend(["--trunc-len-r", str(args.trunc_len_r)])
    if args.taxonomy_classifier:
        cmd.extend(["--taxonomy-classifier", args.taxonomy_classifier.expanduser().resolve()])
    return [
        command_plan_entry(
            "DADA2 R backend",
            cmd,
            outputs=[
                "tables/asv_table.tsv",
                "tables/taxonomy.tsv",
                "tables/read_retention.tsv",
                "tables/representative_sequences.fasta",
            ],
        )
    ]


def r_package_preflight(packages: list[str]) -> dict[str, Any]:
    if not packages:
        return {"checked": [], "missing": [], "ok": True}
    if not any(item["present"] for item in tool_preflight(["Rscript"]).get("checked", [])):
        return {
            "checked": [
                {"package": package, "present": False, "reason": "Rscript missing"}
                for package in packages
            ],
            "missing": packages,
            "ok": False,
        }
    expression = (
        "cat(paste(%s, as.integer(vapply(%s, requireNamespace, logical(1), quietly=TRUE)), sep='\\t'), sep='\\n')"
        % (
            "c(%s)" % ",".join(repr(package) for package in packages),
            "c(%s)" % ",".join(repr(package) for package in packages),
        )
    )
    result = subprocess.run(
        ["Rscript", "-e", expression],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    present: dict[str, bool] = {}
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            present[parts[0]] = parts[1] == "1"
    checked = [{"package": package, "present": bool(present.get(package))} for package in packages]
    missing = [item["package"] for item in checked if not item["present"]]
    return {
        "checked": checked,
        "missing": missing,
        "ok": result.returncode == 0 and not missing,
        "stderr_tail": result.stderr.splitlines()[-5:],
    }


def merge_tool_status(
    tool_status: dict[str, Any], extra_status: dict[str, Any] | None
) -> dict[str, Any]:
    if not extra_status:
        return tool_status
    merged = dict(tool_status)
    runtime_missing = list(merged.get("runtime_missing", []))
    for package in extra_status.get("missing", []):
        runtime_missing.append(f"R package:{package}")
    merged["runtime_missing"] = runtime_missing
    merged["r_packages"] = extra_status
    merged["ok"] = bool(merged.get("ok")) and bool(extra_status.get("ok"))
    return merged


def write_outputs(
    run_dir: Path,
    validation: dict[str, Any],
    samples: list[dict[str, str]],
    plan: list[dict[str, Any]],
) -> None:
    write_tsv(
        run_dir / "validation" / "samples.normalized.tsv",
        samples,
        ["sample", "r1", "r2", "row_index"],
    )
    write_json(run_dir / "workflow" / "amplicon_backend_command_plan.json", {"commands": plan})
    write_command_script(run_dir / "commands.sh", [item["command"] for item in plan])
    write_json(
        run_dir / "methods" / "amplicon_backend_methods.json",
        {
            "backend": validation.get("backend"),
            "marker": validation.get("marker"),
            "primer_forward": validation.get("primer_forward"),
            "primer_reverse": validation.get("primer_reverse"),
            "taxonomy_classifier": validation.get("taxonomy_classifier"),
            "outputs_expected": [
                "ASV table",
                "representative sequences",
                "taxonomy table",
                "alpha diversity",
                "beta diversity",
                "PCoA",
                "read-retention summary",
            ],
        },
    )
    normalize_backend_exports(run_dir)
    write_amplicon_review_outputs(run_dir)


def _data_lines(path: Path) -> list[str]:
    lines = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        if line.startswith("#") and "\t" not in line:
            continue
        lines.append(line[1:] if line.startswith("#") else line)
    return lines


def normalize_generic_tsv(
    source: Path, destination: Path, first_column: str, header_aliases: dict[str, str] | None = None
) -> int:
    lines = _data_lines(source)
    if not lines:
        return 0
    header_aliases = header_aliases or {}
    header = [part.strip() for part in lines[0].split("\t")]
    header[0] = first_column
    header = [header_aliases.get(item.lower(), item) for item in header]
    output = ["\t".join(header)]
    row_count = 0
    for line in lines[1:]:
        parts = line.split("\t")
        if not parts or not parts[0].strip():
            continue
        output.append("\t".join(parts))
        row_count += 1
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(output) + "\n", encoding="utf-8")
    return row_count


def first_existing(paths: list[Path]) -> Path | None:
    return next((path for path in paths if path.exists()), None)


def normalize_backend_exports(run_dir: Path) -> dict[str, Any]:
    tables_dir = run_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "status": "not_available",
        "outputs": {},
        "inputs": {},
        "notes": [],
        "conversion_commands": [],
    }

    asv_output = tables_dir / "asv_table.tsv"
    asv_source = first_existing(
        [
            asv_output,
            tables_dir / "asv_table_export" / "feature-table.tsv",
            tables_dir / "asv_table_export" / "feature-table.txt",
            tables_dir / "asv_table_export" / "biom.tsv",
        ]
    )
    biom_source = tables_dir / "asv_table_export" / "feature-table.biom"
    if asv_source:
        summary["inputs"]["asv_table"] = str(asv_source)
        if asv_source != asv_output:
            rows = normalize_generic_tsv(
                asv_source,
                asv_output,
                "feature_id",
                {"#otu id": "feature_id", "otu id": "feature_id"},
            )
            summary["notes"].append(f"normalized {rows} ASV/features from exported TSV")
        summary["outputs"]["asv_table"] = "tables/asv_table.tsv"
    elif biom_source.exists():
        summary["inputs"]["asv_biom"] = str(biom_source)
        summary["notes"].append(
            "QIIME2 exported a BIOM feature table; convert it to TSV before native visualization."
        )
        summary["conversion_commands"].append(
            "biom convert -i tables/asv_table_export/feature-table.biom -o tables/asv_table_export/feature-table.tsv --to-tsv"
        )

    taxonomy_output = tables_dir / "taxonomy.tsv"
    taxonomy_source = first_existing(
        [
            taxonomy_output,
            tables_dir / "taxonomy_export" / "taxonomy.tsv",
            tables_dir / "taxonomy_export" / "taxonomy.txt",
        ]
    )
    if taxonomy_source:
        summary["inputs"]["taxonomy"] = str(taxonomy_source)
        if taxonomy_source != taxonomy_output:
            rows = normalize_generic_tsv(
                taxonomy_source,
                taxonomy_output,
                "feature_id",
                {"feature id": "feature_id", "taxon": "taxonomy", "confidence": "confidence"},
            )
            summary["notes"].append(f"normalized {rows} taxonomy rows from QIIME2 export")
        summary["outputs"]["taxonomy_table"] = "tables/taxonomy.tsv"

    retention_output = tables_dir / "read_retention.tsv"
    retention_source = first_existing(
        [
            retention_output,
            tables_dir / "denoising_stats_export" / "stats.tsv",
            tables_dir / "denoising_stats_export" / "stats.txt",
        ]
    )
    if retention_source:
        summary["inputs"]["read_retention"] = str(retention_source)
        if retention_source != retention_output:
            rows = normalize_generic_tsv(
                retention_source,
                retention_output,
                "sample",
                {"sample id": "sample", "sample-id": "sample"},
            )
            summary["notes"].append(
                f"normalized {rows} denoising/read-retention rows from QIIME2 export"
            )
        summary["outputs"]["read_retention"] = "tables/read_retention.tsv"

    diversity_dir = run_dir / "qiime2" / "core-metrics"
    if diversity_dir.exists():
        summary["inputs"]["core_metrics"] = str(diversity_dir)
        summary["outputs"]["core_metrics_dir"] = "qiime2/core-metrics"

    summary["status"] = "created" if summary["outputs"] else "not_available"
    if not summary["outputs"]:
        summary["notes"].append(
            "No ASV, taxonomy, denoising, or QIIME2 core-metrics exports were found yet."
        )
    write_json(tables_dir / "amplicon_backend_summary.json", summary)
    return summary


def parse_numeric(value: Any) -> float:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


def read_feature_matrix(path: Path) -> tuple[list[str], dict[str, dict[str, float]]]:
    if not path.exists():
        return [], {}
    rows, columns = read_table(path)
    if len(columns) < 2:
        return [], {}
    feature_col = columns[0]
    samples = columns[1:]
    matrix: dict[str, dict[str, float]] = {}
    for row in rows:
        feature = row.get(feature_col, "").strip()
        if not feature:
            continue
        matrix[feature] = {sample: parse_numeric(row.get(sample, "")) for sample in samples}
    return samples, matrix


def taxonomy_label_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    rows, columns = read_table(path)
    if not columns:
        return {}
    feature_col = columns[0]
    lower = {column.lower(): column for column in columns}
    taxonomy_col = lower.get("taxonomy") or lower.get("taxon") or lower.get("classification")
    labels: dict[str, str] = {}
    for row in rows:
        feature = row.get(feature_col, "").strip()
        taxonomy = row.get(taxonomy_col, "").strip() if taxonomy_col else ""
        if not feature or not taxonomy:
            continue
        parts = [part.strip() for part in taxonomy.split(";") if part.strip()]
        labels[feature] = parts[-1] if parts else taxonomy
    return labels


def write_bar_svg(path: Path, title: str, values: list[tuple[str, float]], *, subtitle: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not values:
        body = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" role="img" aria-label="{html.escape(title)}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="32" y="48" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#202124">{html.escape(title)}</text>
  <text x="32" y="92" font-family="Arial, sans-serif" font-size="15" fill="#5f6368">{html.escape(subtitle)}</text>
</svg>
"""
        path.write_text(body, encoding="utf-8")
        return str(path)
    width = 980
    row_height = 38
    height = 92 + len(values) * row_height
    max_value = max(value for _, value in values) or 1.0
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img" aria-label="{html.escape(title)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="38" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#202124">{html.escape(title)}</text>',
        f'<text x="32" y="62" font-family="Arial, sans-serif" font-size="13" fill="#5f6368">{html.escape(subtitle)}</text>',
    ]
    for index, (label, value) in enumerate(values):
        y = 84 + index * row_height
        bar_width = max(2.0, min(460.0, value / max_value * 460.0))
        short_label = label if len(label) < 42 else label[:39] + "..."
        lines.extend(
            [
                f'<text x="32" y="{y + 14}" font-family="Arial, sans-serif" font-size="12" fill="#202124">{html.escape(short_label)}</text>',
                f'<rect x="310" y="{y}" width="460" height="17" fill="#eef2f7"/>',
                f'<rect x="310" y="{y}" width="{bar_width:.1f}" height="17" fill="#2f80ed"/>',
                f'<text x="782" y="{y + 13}" font-family="Arial, sans-serif" font-size="12" fill="#202124">{value:.5g}</text>',
            ]
        )
    lines.append("</svg>\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def write_amplicon_review_outputs(run_dir: Path) -> dict[str, Any]:
    samples, matrix = read_feature_matrix(run_dir / "tables" / "asv_table.tsv")
    taxonomy = taxonomy_label_map(run_dir / "tables" / "taxonomy.tsv")
    outputs: dict[str, str] = {}
    status = "not_available"
    notes: list[str] = []

    if not matrix:
        notes.append(
            "ASV table is not available; backend-derived diversity and taxa plots were not generated from real tables."
        )
    else:
        status = "created"
        alpha_rows: list[dict[str, Any]] = []
        for sample in samples:
            values = [feature_values.get(sample, 0.0) for feature_values in matrix.values()]
            total = sum(values)
            observed = sum(1 for value in values if value > 0)
            shannon = 0.0
            if total:
                for value in values:
                    if value > 0:
                        proportion = value / total
                        shannon -= proportion * math.log(proportion)
            alpha_rows.append(
                {
                    "sample": sample,
                    "total_reads": round(total, 6),
                    "observed_features": observed,
                    "shannon": round(shannon, 6),
                }
            )
        write_tsv(
            run_dir / "tables" / "alpha_diversity.tsv",
            alpha_rows,
            ["sample", "total_reads", "observed_features", "shannon"],
        )
        outputs["alpha_diversity"] = "tables/alpha_diversity.tsv"

        distance_rows = []
        for left in samples:
            row: dict[str, Any] = {"sample": left}
            for right in samples:
                numerator = sum(
                    abs(values.get(left, 0.0) - values.get(right, 0.0))
                    for values in matrix.values()
                )
                denominator = sum(
                    values.get(left, 0.0) + values.get(right, 0.0) for values in matrix.values()
                )
                row[right] = f"{(numerator / denominator if denominator else 0.0):.8g}"
            distance_rows.append(row)
        write_tsv(
            run_dir / "tables" / "bray_curtis_distance.tsv", distance_rows, ["sample", *samples]
        )
        outputs["bray_curtis_distance"] = "tables/bray_curtis_distance.tsv"

        grouped: dict[str, dict[str, float]] = {}
        for feature, values in matrix.items():
            label = taxonomy.get(feature, feature)
            grouped.setdefault(label, {sample: 0.0 for sample in samples})
            for sample in samples:
                grouped[label][sample] += values.get(sample, 0.0)
        taxa_rows = []
        for label, values in sorted(
            grouped.items(), key=lambda item: sum(item[1].values()), reverse=True
        ):
            row: dict[str, Any] = {
                "taxon_or_feature": label,
                "total_abundance": round(sum(values.values()), 6),
            }
            row.update({sample: round(values.get(sample, 0.0), 6) for sample in samples})
            taxa_rows.append(row)
        write_tsv(
            run_dir / "tables" / "top_taxa_or_features.tsv",
            taxa_rows[:25],
            ["taxon_or_feature", "total_abundance", *samples],
        )
        outputs["top_taxa_or_features"] = "tables/top_taxa_or_features.tsv"

        write_bar_svg(
            run_dir / "visualizations" / "amplicon_sample_depth.svg",
            "Amplicon Sample Depth",
            [(row["sample"], float(row["total_reads"])) for row in alpha_rows],
            subtitle="Total feature-table counts per sample.",
        )
        write_bar_svg(
            run_dir / "visualizations" / "amplicon_alpha_diversity.svg",
            "Amplicon Alpha Diversity",
            [(row["sample"], float(row["shannon"])) for row in alpha_rows],
            subtitle="Shannon diversity computed from the normalized ASV/feature table.",
        )
        write_bar_svg(
            run_dir / "visualizations" / "amplicon_top_taxa.svg",
            "Amplicon Top Taxa Or Features",
            [(row["taxon_or_feature"], float(row["total_abundance"])) for row in taxa_rows[:15]],
            subtitle="Aggregated abundance across samples; taxonomy labels are used when available.",
        )
        outputs.update(
            {
                "sample_depth_plot": "visualizations/amplicon_sample_depth.svg",
                "alpha_diversity_plot": "visualizations/amplicon_alpha_diversity.svg",
                "top_taxa_plot": "visualizations/amplicon_top_taxa.svg",
            }
        )
        if not taxonomy:
            notes.append("Taxonomy table is not available; top-taxa plot uses feature IDs.")

    dashboard_rows = []
    for output_label, output_path in outputs.items():
        href = (
            output_path.replace("visualizations/", "", 1)
            if output_path.startswith("visualizations/")
            else f"../{output_path}"
        )
        dashboard_rows.append(
            f'<tr><td>{html.escape(output_label)}</td><td><a href="{html.escape(href)}">{html.escape(output_path)}</a></td></tr>'
        )
    if not dashboard_rows:
        dashboard_rows.append(
            '<tr><td colspan="2">No backend-derived amplicon review outputs are available yet.</td></tr>'
        )
    dashboard = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Amplicon Backend Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 28px; color: #202124; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f6f8fa; }}
  </style>
</head>
<body>
  <h1>Amplicon Backend Dashboard</h1>
  <p>Native review of normalized backend ASV, diversity, taxonomy, and read-retention artifacts. Outputs remain absent until real backend tables are present.</p>
  <table><thead><tr><th>Artifact</th><th>Path</th></tr></thead><tbody>{"".join(dashboard_rows)}</tbody></table>
  <h2>Notes</h2>
  <ul>{"".join(f"<li>{html.escape(note)}</li>" for note in notes)}</ul>
</body>
</html>
"""
    dashboard_path = run_dir / "visualizations" / "amplicon_backend_dashboard.html"
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(dashboard, encoding="utf-8")
    outputs["dashboard"] = "visualizations/amplicon_backend_dashboard.html"
    summary = {
        "status": status,
        "outputs": outputs,
        "notes": notes,
        "sample_count": len(samples),
        "feature_count": len(matrix),
    }
    write_json(run_dir / "tables" / "amplicon_diversity_summary.json", summary)
    return summary


def write_qiime2_manifest(run_dir: Path, samples: list[dict[str, str]]) -> None:
    paired = any(row["r2"] for row in samples)
    fieldnames = (
        ["sample-id", "forward-absolute-filepath", "reverse-absolute-filepath"]
        if paired
        else ["sample-id", "absolute-filepath"]
    )
    rows = []
    for row in samples:
        if paired:
            rows.append(
                {
                    "sample-id": row["sample"],
                    "forward-absolute-filepath": row["r1"],
                    "reverse-absolute-filepath": row["r2"],
                }
            )
        else:
            rows.append({"sample-id": row["sample"], "absolute-filepath": row["r1"]})
    write_tsv(run_dir / "workflow" / "qiime2_manifest.tsv", rows, fieldnames)


def execute_plan(run_dir: Path, plan: list[dict[str, Any]]) -> dict[str, Any]:
    for dirname in ["qiime2", "tables", "logs", "workflow"]:
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
            title="Amplicon Samples",
            path="validation/samples.normalized.tsv",
            kind="table",
            status="created",
            description="Normalized sample FASTQ manifest.",
        ),
        artifact_entry(
            artifact_id="command_plan",
            title="Backend Command Plan",
            path="workflow/amplicon_backend_command_plan.json",
            kind="json",
            status="created",
            description="QIIME2, DADA2, or nf-core/ampliseq command contract.",
        ),
        artifact_entry(
            artifact_id="methods",
            title="Backend Methods",
            path="methods/amplicon_backend_methods.json",
            kind="json",
            status="created",
            description="Primer, marker, taxonomy, and diversity method contract.",
        ),
        artifact_entry(
            artifact_id="backend_summary",
            title="Backend Export Summary",
            path="tables/amplicon_backend_summary.json",
            kind="json",
            status="created",
            description="Records which QIIME2/DADA2/nf-core exported tables were normalized for review.",
        ),
        artifact_entry(
            artifact_id="diversity_summary",
            title="Diversity Summary",
            path="tables/amplicon_diversity_summary.json",
            kind="json",
            status="created",
            description="Backend-derived alpha diversity, Bray-Curtis, and taxa-plot availability summary.",
        ),
        artifact_entry(
            artifact_id="backend_dashboard",
            title="Backend Dashboard",
            path="visualizations/amplicon_backend_dashboard.html",
            kind="html",
            status="created",
            description="Native review dashboard for ASV depth, alpha diversity, taxa/features, and backend caveats.",
        ),
        artifact_entry(
            artifact_id="sample_depth_plot",
            title="Sample Depth Plot",
            path="visualizations/amplicon_sample_depth.svg",
            kind="svg",
            status="created"
            if (run_dir / "visualizations" / "amplicon_sample_depth.svg").exists()
            else "not_available",
            description="Per-sample feature-table count plot.",
        ),
        artifact_entry(
            artifact_id="alpha_diversity_plot",
            title="Alpha Diversity Plot",
            path="visualizations/amplicon_alpha_diversity.svg",
            kind="svg",
            status="created"
            if (run_dir / "visualizations" / "amplicon_alpha_diversity.svg").exists()
            else "not_available",
            description="Shannon diversity plot computed from the normalized ASV/feature table.",
        ),
        artifact_entry(
            artifact_id="top_taxa_plot",
            title="Top Taxa Or Features Plot",
            path="visualizations/amplicon_top_taxa.svg",
            kind="svg",
            status="created"
            if (run_dir / "visualizations" / "amplicon_top_taxa.svg").exists()
            else "not_available",
            description="Top taxa/features aggregated across samples.",
        ),
        artifact_entry(
            artifact_id="asv_table",
            title="ASV Table",
            path="tables/asv_table.tsv",
            kind="table",
            status="created"
            if (run_dir / "tables" / "asv_table.tsv").exists()
            else "not_available",
            description="ASV/feature table after backend execution or export.",
        ),
        artifact_entry(
            artifact_id="taxonomy_table",
            title="Taxonomy Table",
            path="tables/taxonomy.tsv",
            kind="table",
            status="created" if (run_dir / "tables" / "taxonomy.tsv").exists() else "not_available",
            description="Feature taxonomy table normalized from backend output.",
        ),
        artifact_entry(
            artifact_id="alpha_diversity",
            title="Alpha Diversity Table",
            path="tables/alpha_diversity.tsv",
            kind="table",
            status="created"
            if (run_dir / "tables" / "alpha_diversity.tsv").exists()
            else "not_available",
            description="Observed features, total reads, and Shannon diversity per sample.",
        ),
        artifact_entry(
            artifact_id="bray_curtis",
            title="Bray-Curtis Distance Matrix",
            path="tables/bray_curtis_distance.tsv",
            kind="table",
            status="created"
            if (run_dir / "tables" / "bray_curtis_distance.tsv").exists()
            else "not_available",
            description="Pairwise Bray-Curtis distances computed from normalized feature counts.",
        ),
        artifact_entry(
            artifact_id="read_retention",
            title="Read Retention",
            path="tables/read_retention.tsv",
            kind="table",
            status="created"
            if (run_dir / "tables" / "read_retention.tsv").exists()
            else "not_available",
            description="Denoising or read-retention summary normalized from backend output.",
        ),
    ]
    entries.extend(ngs_resource_gate.resource_visual_entries(resource_plan))
    index = write_visualization_index(
        run_dir,
        title="Amplicon Microbiome Backend Review",
        description="Review surface for ASV, taxonomy, diversity, and backend provenance artifacts.",
        entries=entries,
        notes=[
            *validation.get("warnings", []),
            *ngs_resource_gate.resource_messages(resource_plan),
        ],
        analysis_intent="real_analysis" if status != "blocked" else "blocked_preflight",
        provenance_summary={
            "status": status,
            "backend": validation.get("backend"),
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
    tool_status: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# Amplicon Microbiome Backend Run Summary",
        "",
        f"Status: `{status}`",
        f"Backend: `{validation.get('backend')}`",
        f"Samples parsed: `{validation.get('sample_count', 0)}`",
        "",
        "## Key Artifacts",
        "",
        "- `workflow/amplicon_backend_command_plan.json`",
        "- `workflow/qiime2_manifest.tsv` for QIIME2 runs",
        "- `methods/amplicon_backend_methods.json`",
        "- `tables/` ASV, taxonomy, and diversity outputs when executed/exported",
        "- `tables/amplicon_backend_summary.json`",
        "- `tables/amplicon_diversity_summary.json`, `tables/alpha_diversity.tsv`, and `tables/bray_curtis_distance.tsv` when ASV tables are available",
        "- `visualizations/amplicon_backend_dashboard.html` and backend-derived SVG plots",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `visualizations/index.html`",
        "- `run_manifest.json` and `artifact_index.json`",
        "",
    ]
    if validation.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {item}" for item in validation["warnings"])
        lines.append("")
    if tool_status and not tool_status.get("ok"):
        lines.extend(["## Runtime Blockers", ""])
        for item in tool_status.get("missing_required", []):
            lines.append(f"- missing executable: `{item}`")
        for item in tool_status.get("runtime_missing", []):
            lines.append(f"- missing runtime dependency: `{item}`")
        lines.append("")
    lines.extend(ngs_resource_gate.resource_summary_lines(resource_plan))
    if validation.get("errors"):
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {item}" for item in validation["errors"])
    write_text(run_dir / "summary.md", "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-sheet", type=Path, required=True)
    parser.add_argument(
        "--backend", choices=["qiime2", "dada2", "nf-core/ampliseq"], default="qiime2"
    )
    parser.add_argument("--marker", default="16S")
    parser.add_argument("--primer-forward", required=True)
    parser.add_argument("--primer-reverse", required=True)
    parser.add_argument("--taxonomy-classifier", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--trunc-len-f", type=int)
    parser.add_argument("--trunc-len-r", type=int)
    parser.add_argument("--sampling-depth", type=int, default=1000)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--profile")
    parser.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Resource bundle override formatted as bundle=/path. May be repeated.",
    )
    parser.add_argument(
        "--include-optional-resources",
        action="store_true",
        help="Include optional taxonomy databases such as GTDB in readiness checks.",
    )
    parser.add_argument("--resource-checksums", action="store_true")
    parser.add_argument(
        "--require-resource-plan",
        action="store_true",
        help="Treat missing registered taxonomy/reference bundles as blocking for this direct runner.",
    )
    parser.add_argument(
        "--skip-resource-plan",
        action="store_true",
        help="Skip registered taxonomy database readiness checks.",
    )
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--run-id", default=slug_timestamp("amplicon-microbiome-backend"))
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
        pipeline="amplicon_microbiome",
        bundle_roots=args.bundle_root,
        include_optional=args.include_optional_resources,
        include_checksums=args.resource_checksums,
        skip=args.skip_resource_plan,
        required=args.require_resource_plan,
    )
    validation = ngs_resource_gate.merge_resource_status(
        input_validation, resource_plan, required=args.require_resource_plan
    )
    required = {"qiime2": ["qiime"], "dada2": ["Rscript"], "nf-core/ampliseq": ["nextflow"]}[
        args.backend
    ]
    tool_status = tool_preflight(required, optional=["cutadapt", "multiqc"])
    if args.backend == "dada2":
        package_status = r_package_preflight(["dada2"])
        tool_status = merge_tool_status(tool_status, package_status)
    plan = build_plan(args, samples)
    write_qiime2_manifest(run_dir, samples)
    write_json(run_dir / "config.json", {**serializable_args(args), "run_dir": str(run_dir)})
    write_json(run_dir / "validation" / "input_validation_summary.json", input_validation)
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions(
            {
                "qiime": ["qiime", "--version"],
                "Rscript": ["Rscript", "--version"],
                "nextflow": ["nextflow", "-version"],
            }
        ),
    )
    write_outputs(run_dir, validation, samples, plan)
    dry_run = {
        "ok": validation["ok"] and tool_status["ok"],
        "detail": "amplicon backend inputs, primers, taxonomy resources, and tools validated",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    status = "blocked" if not dry_run["ok"] else "validated"
    execution = None
    if args.execute and dry_run["ok"]:
        execution = execute_plan(run_dir, plan)
        status = "completed" if execution.get("ok") else "failed"
        normalize_backend_exports(run_dir)
        write_amplicon_review_outputs(run_dir)
    visuals = write_visuals(run_dir, status, validation, resource_plan)
    resource_outputs = ngs_resource_gate.resource_output_paths(resource_plan)
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="amplicon_microbiome",
        workflow=f"backend_{args.backend}",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "metadata": str(args.metadata.expanduser().resolve()) if args.metadata else None,
            "taxonomy_classifier": str(args.taxonomy_classifier.expanduser().resolve())
            if args.taxonomy_classifier
            else None,
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "sample_table": "validation/samples.normalized.tsv",
            "command_plan": "workflow/amplicon_backend_command_plan.json",
            "methods": "methods/amplicon_backend_methods.json",
            "backend_summary": "tables/amplicon_backend_summary.json",
            "diversity_summary": "tables/amplicon_diversity_summary.json",
            "asv_table": "tables/asv_table.tsv",
            "taxonomy_table": "tables/taxonomy.tsv",
            "alpha_diversity": "tables/alpha_diversity.tsv",
            "bray_curtis_distance": "tables/bray_curtis_distance.tsv",
            "top_taxa_or_features": "tables/top_taxa_or_features.tsv",
            "read_retention": "tables/read_retention.tsv",
            "backend_dashboard": "visualizations/amplicon_backend_dashboard.html",
            "sample_depth_plot": "visualizations/amplicon_sample_depth.svg",
            "alpha_diversity_plot": "visualizations/amplicon_alpha_diversity.svg",
            "top_taxa_plot": "visualizations/amplicon_top_taxa.svg",
            **resource_outputs,
            **visuals,
        },
        method={
            "backend": args.backend,
            "marker": args.marker,
            "primer_forward": args.primer_forward,
            "primer_reverse": args.primer_reverse,
            "resource_plan": resource_plan,
        },
        audit={"resource_readiness": resource_plan} if resource_plan else None,
        review_bundle=visuals,
    )
    write_summary(run_dir, status, validation, resource_plan, tool_status)
    write_json(run_dir / "artifact_index.json", build_artifact_index(run_dir))
    print(run_dir)
    return 1 if status in {"blocked", "failed"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
