#!/usr/bin/env python3
"""Run or plan shotgun metagenomics Kraken2/Bracken/HUMAnN backend artifacts."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Any

import ngs_reference_manager
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
DEFAULT_RUN_ROOT = WORKSPACE_ROOT / "ngs_runs" / "shotgun_metagenomics_backend"


def parse_float(value: Any) -> float:
    text = str(value).strip().replace(",", "")
    if not text or text.lower() in {"-", "na", "nan", "none"}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def humann_database_paths(root: Path) -> tuple[Path, Path]:
    chocophlan = root / "chocophlan"
    uniref = root / "uniref"
    if chocophlan.is_dir() and uniref.is_dir():
        return chocophlan, uniref
    return root, root


def resolve_bracken_read_length(
    bracken_db: Path, requested_read_length: int
) -> tuple[int, str | None]:
    requested_path = bracken_db / f"database{requested_read_length}mers.kmer_distrib"
    if requested_path.exists():
        return requested_read_length, None
    available_lengths = sorted(
        int(match.group(1))
        for path in bracken_db.glob("database*mers.kmer_distrib")
        if (match := re.match(r"database(\d+)mers\.kmer_distrib$", path.name))
    )
    if not available_lengths:
        return requested_read_length, None
    selected = min(available_lengths, key=lambda value: abs(value - requested_read_length))
    if selected == requested_read_length:
        return selected, None
    return (
        selected,
        f"Bracken database lacks database{requested_read_length}mers.kmer_distrib; using available read length {selected} instead.",
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
    kraken_db = args.kraken_db.expanduser().resolve() if args.kraken_db else None
    if not kraken_db:
        errors.append("--kraken-db is required for taxonomic classification")
    elif not kraken_db.exists():
        errors.append(f"Kraken2 database does not exist: {kraken_db}")
    bracken_db = args.bracken_db.expanduser().resolve() if args.bracken_db else kraken_db
    if args.run_bracken and bracken_db and not bracken_db.exists():
        errors.append(f"Bracken database path does not exist: {bracken_db}")
    humann_db = args.humann_db.expanduser().resolve() if args.humann_db else None
    if args.run_humann and not humann_db:
        errors.append("--run-humann requires --humann-db")
    if humann_db and not humann_db.exists():
        errors.append(f"HUMAnN database root does not exist: {humann_db}")
    if humann_db and humann_db.exists() and args.run_humann:
        nucleotide_db, protein_db = humann_database_paths(humann_db)
        if nucleotide_db == humann_db and protein_db == humann_db:
            warnings.append(
                "HUMAnN database root does not expose chocophlan/uniref subdirectories; runner will pass the root directly."
            )
    host_reference = args.host_reference.expanduser().resolve() if args.host_reference else None
    if host_reference and not host_reference.exists():
        errors.append(f"host reference does not exist: {host_reference}")
    if not args.metadata:
        warnings.append(
            "no metadata table was supplied; diversity and differential-abundance interpretation will be limited"
        )
    for row_index, row in enumerate(rows, start=2):
        sample = normalize_sample_name(
            row.get("sample") or row.get("sample_id"), f"row_{row_index}"
        )
        r1 = resolve_path(row.get("r1") or row.get("fastq_1"), sample_sheet.parent)
        r2 = resolve_path(row.get("r2") or row.get("fastq_2"), sample_sheet.parent)
        if not r1:
            errors.append(f"row {row_index}: r1/fastq_1 is required")
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
        errors.append("no usable shotgun samples found")
    validation = {
        "ok": not errors,
        "sample_sheet": str(sample_sheet),
        "metadata": str(args.metadata.expanduser().resolve()) if args.metadata else None,
        "sample_count": len(samples),
        "kraken_db": str(kraken_db) if kraken_db else None,
        "bracken_db": str(bracken_db) if bracken_db else None,
        "humann_db": str(humann_db) if humann_db else None,
        "host_reference": str(host_reference) if host_reference else None,
        "columns": columns,
        "errors": errors,
        "warnings": warnings,
    }
    return validation, samples


def _missing_required_resources(resources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "kind": item["kind"],
            "bundle": item["bundle"],
            "root": item["root"],
            "missing": item["check"].get("missing", []),
            "error": item["check"].get("error"),
        }
        for item in resources
        if item.get("blocking")
    ]


def promote_requested_database_steps(
    plan: dict[str, Any], args: argparse.Namespace
) -> dict[str, Any]:
    requested = {
        "bracken_standard": args.run_bracken,
        "humann_uniref90": args.run_humann,
    }
    if not any(requested.values()):
        return plan
    updated = dict(plan)
    resources: list[dict[str, Any]] = []
    for resource in plan.get("resources", []):
        item = dict(resource)
        if requested.get(str(item.get("bundle"))):
            item["required"] = True
            item["blocking"] = not bool(item.get("ok"))
        resources.append(item)
    updated["resources"] = resources
    updated["missing_required"] = _missing_required_resources(resources)
    updated["ok"] = not updated["missing_required"]
    return updated


def resource_blockers(resource_plan: dict[str, Any] | None) -> list[str]:
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
    roots = {"kraken2_standard": args.kraken_db.expanduser().resolve()}
    if args.run_bracken or args.bracken_db:
        roots["bracken_standard"] = (args.bracken_db or args.kraken_db).expanduser().resolve()
    if args.run_humann and args.humann_db:
        roots["humann_uniref90"] = args.humann_db.expanduser().resolve()
    plan = ngs_reference_manager.plan_pipeline_resources(
        "shotgun_metagenomics",
        bundle_roots=roots,
        include_optional=args.include_optional_resources or args.run_bracken or args.run_humann,
        include_checksums=args.resource_checksums,
    )
    plan = promote_requested_database_steps(plan, args)
    run_root = run_dir.resolve()
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
            "resource readiness plan was skipped; database roots were not checked against the registry contract"
        )
    else:
        merged["resource_plan_ok"] = bool(resource_plan.get("ok"))
        merged["resource_plan_skipped"] = False
        merged["resource_plan_path"] = resource_plan.get("outputs", {}).get("resource_plan")
        merged["missing_required_resources"] = resource_plan.get("missing_required", [])
        errors.extend(resource_blockers(resource_plan))
    merged["errors"] = errors
    merged["warnings"] = warnings
    merged["ok"] = bool(validation.get("ok")) and (
        resource_plan is None or bool(resource_plan.get("ok"))
    )
    return merged


def build_plan(args: argparse.Namespace, samples: list[dict[str, str]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    kraken_db = args.kraken_db.expanduser().resolve() if args.kraken_db else "MISSING_KRAKEN_DB"
    bracken_db = args.bracken_db.expanduser().resolve() if args.bracken_db else kraken_db
    bracken_read_length, _ = (
        resolve_bracken_read_length(bracken_db, args.read_length)
        if isinstance(bracken_db, Path)
        else (args.read_length, None)
    )
    humann_nucleotide_db, humann_protein_db = (
        humann_database_paths(args.humann_db.expanduser().resolve())
        if args.humann_db
        else (Path("MISSING_HUMANN_DB"), Path("MISSING_HUMANN_DB"))
    )
    for sample in samples:
        name = sample["sample"]
        current_r1 = sample["r1"]
        current_r2 = sample["r2"]
        if args.host_reference:
            clean_r1, clean_r2 = host_depleted_paths(sample)
            plan.append(build_host_depletion_step(args, sample, clean_r1, clean_r2))
            current_r1 = clean_r1
            current_r2 = clean_r2
        kraken_cmd: list[str | Path] = [
            "kraken2",
            "--db",
            kraken_db,
            "--threads",
            str(args.threads),
            "--report",
            f"taxonomic_classification/{name}.kraken.report",
            "--output",
            f"taxonomic_classification/{name}.kraken.output",
        ]
        if current_r2:
            kraken_cmd.extend(["--paired", current_r1, current_r2])
        else:
            kraken_cmd.append(current_r1)
        plan.append(
            command_plan_entry(
                f"{name}: kraken2 classify",
                kraken_cmd,
                outputs=[
                    f"taxonomic_classification/{name}.kraken.report",
                    f"taxonomic_classification/{name}.kraken.output",
                ],
            )
        )
        if args.run_bracken:
            plan.append(
                command_plan_entry(
                    f"{name}: bracken abundance",
                    [
                        "bracken",
                        "-d",
                        bracken_db,
                        "-i",
                        f"taxonomic_classification/{name}.kraken.report",
                        "-o",
                        f"taxonomic_classification/{name}.bracken.tsv",
                        "-r",
                        str(bracken_read_length),
                        "-l",
                        args.bracken_level,
                    ],
                    outputs=[f"taxonomic_classification/{name}.bracken.tsv"],
                )
            )
        if args.run_humann:
            humann_input = current_r1 if not current_r2 else f"workflow/{name}.paired.fastq"
            if current_r2:
                plan.append(
                    command_plan_entry(
                        f"{name}: concatenate paired reads for HUMAnN",
                        f"zcat -f {shell_join([current_r1])} {shell_join([current_r2])} > {shell_join([humann_input])}",
                        outputs=[humann_input],
                    )
                )
            plan.append(
                command_plan_entry(
                    f"{name}: HUMAnN functional profile",
                    [
                        "humann",
                        "--input",
                        humann_input,
                        "--output",
                        f"functional_profile/{name}",
                        "--threads",
                        str(args.threads),
                        "--nucleotide-database",
                        humann_nucleotide_db,
                        "--protein-database",
                        humann_protein_db,
                    ],
                    outputs=[f"functional_profile/{name}"],
                )
            )
    return plan


def host_depleted_paths(sample: dict[str, str]) -> tuple[str, str]:
    name = sample["sample"]
    if sample.get("r2"):
        return f"host_depletion/{name}.clean_R1.fastq", f"host_depletion/{name}.clean_R2.fastq"
    return f"host_depletion/{name}.clean.fastq", ""


def build_host_depletion_step(
    args: argparse.Namespace, sample: dict[str, str], clean_r1: str, clean_r2: str
) -> dict[str, Any]:
    name = sample["sample"]
    out_dir = f"host_depletion/{name}"
    reference = args.host_reference.expanduser().resolve()
    if sample.get("r2"):
        kneaddata_cmd = [
            "kneaddata",
            "--input1",
            sample["r1"],
            "--input2",
            sample["r2"],
            "--reference-db",
            reference,
            "--output",
            out_dir,
            "--output-prefix",
            name,
            "--threads",
            str(args.threads),
        ]
        command = " && ".join(
            [
                f"mkdir -p {shell_join([out_dir])}",
                shell_join(kneaddata_cmd),
                f"clean_r1=$(find {shell_join([out_dir])} -type f \\( -name '*paired_1.fastq' -o -name '*paired_1.fastq.gz' -o -name '*clean_R1.fastq' -o -name '*clean_R1.fastq.gz' \\) | head -n 1)",
                f"clean_r2=$(find {shell_join([out_dir])} -type f \\( -name '*paired_2.fastq' -o -name '*paired_2.fastq.gz' -o -name '*clean_R2.fastq' -o -name '*clean_R2.fastq.gz' \\) | head -n 1)",
                'test -n "$clean_r1"',
                'test -n "$clean_r2"',
                f'ln -sf "$PWD/$clean_r1" {shell_join([clean_r1])}',
                f'ln -sf "$PWD/$clean_r2" {shell_join([clean_r2])}',
            ]
        )
        return command_plan_entry(
            f"{name}: KneadData host depletion", command, outputs=[clean_r1, clean_r2, out_dir]
        )
    kneaddata_cmd = [
        "kneaddata",
        "--input",
        sample["r1"],
        "--reference-db",
        reference,
        "--output",
        out_dir,
        "--output-prefix",
        name,
        "--threads",
        str(args.threads),
    ]
    command = " && ".join(
        [
            f"mkdir -p {shell_join([out_dir])}",
            shell_join(kneaddata_cmd),
            f"clean=$(find {shell_join([out_dir])} -type f \\( -name '*kneaddata.fastq' -o -name '*kneaddata.fastq.gz' -o -name '*clean.fastq' -o -name '*clean.fastq.gz' \\) | head -n 1)",
            'test -n "$clean"',
            f'ln -sf "$PWD/$clean" {shell_join([clean_r1])}',
        ]
    )
    return command_plan_entry(
        f"{name}: KneadData host depletion", command, outputs=[clean_r1, out_dir]
    )


def parse_bracken_table(path: Path, sample: str | None = None) -> list[dict[str, Any]]:
    rows, columns = read_table(path)
    sample_name = sample or path.name.replace(".bracken", "").replace(".tsv", "").replace(
        ".txt", ""
    )
    if not columns:
        return []
    lower_columns = {column.lower(): column for column in columns}
    name_col = (
        lower_columns.get("name")
        or lower_columns.get("taxonomy")
        or lower_columns.get("taxon")
        or columns[0]
    )
    taxid_col = (
        lower_columns.get("taxonomy_id")
        or lower_columns.get("taxid")
        or lower_columns.get("taxon_id")
        or ""
    )
    rank_col = (
        lower_columns.get("taxonomy_lvl")
        or lower_columns.get("rank")
        or lower_columns.get("level")
        or ""
    )
    reads_col = (
        lower_columns.get("new_est_reads")
        or lower_columns.get("reads")
        or lower_columns.get("kraken_assigned_reads")
        or ""
    )
    fraction_col = (
        lower_columns.get("fraction_total_reads")
        or lower_columns.get("fraction")
        or lower_columns.get("relative_abundance")
        or ""
    )
    parsed = []
    for row in rows:
        taxon = (row.get(name_col) or "").strip()
        if not taxon:
            continue
        parsed.append(
            {
                "sample": sample_name,
                "taxon": taxon,
                "taxonomy_id": (row.get(taxid_col) or "").strip() if taxid_col else "",
                "taxonomy_lvl": (row.get(rank_col) or "").strip() if rank_col else "",
                "est_reads": parse_float(row.get(reads_col, "")) if reads_col else 0.0,
                "fraction_total_reads": parse_float(row.get(fraction_col, ""))
                if fraction_col
                else 0.0,
            }
        )
    return parsed


def write_matrix(
    path: Path,
    matrix: dict[tuple[str, str, str], dict[str, float]],
    samples: list[str],
    value_label: str,
) -> int:
    rows = []
    for key, values in sorted(matrix.items(), key=lambda item: sum(item[1].values()), reverse=True):
        taxon, taxid, rank = key
        row: dict[str, Any] = {"taxon": taxon, "taxonomy_id": taxid, "taxonomy_lvl": rank}
        for sample in samples:
            value = values.get(sample, 0.0)
            row[sample] = f"{value:.8g}"
        rows.append(row)
    if rows:
        write_tsv(path, rows, ["taxon", "taxonomy_id", "taxonomy_lvl", *samples])
    return len(rows)


def merge_bracken_outputs(run_dir: Path, samples: list[dict[str, str]]) -> dict[str, Any]:
    sample_names = [row["sample"] for row in samples]
    observed: list[dict[str, Any]] = []
    for sample in sample_names:
        for candidate in [
            run_dir / "taxonomic_classification" / f"{sample}.bracken.tsv",
            run_dir / "taxonomic_classification" / f"{sample}.bracken.txt",
        ]:
            if candidate.exists():
                observed.extend(parse_bracken_table(candidate, sample=sample))
                break
    if not observed:
        summary = {
            "status": "not_available",
            "input_tables": [],
            "taxa": 0,
            "samples": sample_names,
            "outputs": {},
            "note": "No Bracken tables were found under taxonomic_classification/*.bracken.tsv.",
        }
        write_json(run_dir / "tables" / "bracken_summary.json", summary)
        return summary

    read_matrix: dict[tuple[str, str, str], dict[str, float]] = {}
    fraction_matrix: dict[tuple[str, str, str], dict[str, float]] = {}
    input_tables = sorted(
        {
            str(run_dir / "taxonomic_classification" / f"{row['sample']}.bracken.tsv")
            for row in observed
        }
    )
    for row in observed:
        key = (row["taxon"], row["taxonomy_id"], row["taxonomy_lvl"])
        read_matrix.setdefault(key, {})[row["sample"]] = read_matrix.setdefault(key, {}).get(
            row["sample"], 0.0
        ) + float(row["est_reads"])
        fraction_matrix.setdefault(key, {})[row["sample"]] = fraction_matrix.setdefault(
            key, {}
        ).get(row["sample"], 0.0) + float(row["fraction_total_reads"])

    read_count = write_matrix(
        run_dir / "tables" / "bracken_est_reads_matrix.tsv", read_matrix, sample_names, "est_reads"
    )
    fraction_count = write_matrix(
        run_dir / "tables" / "bracken_relative_abundance_matrix.tsv",
        fraction_matrix,
        sample_names,
        "fraction_total_reads",
    )
    summary = {
        "status": "created",
        "input_tables": input_tables,
        "taxa": max(read_count, fraction_count),
        "samples": sample_names,
        "outputs": {
            "est_reads_matrix": "tables/bracken_est_reads_matrix.tsv",
            "relative_abundance_matrix": "tables/bracken_relative_abundance_matrix.tsv",
        },
    }
    write_json(run_dir / "tables" / "bracken_summary.json", summary)
    return summary


def infer_humann_sample(path: Path, sample_names: list[str]) -> str:
    for part in [path.parent.name, path.stem]:
        for sample in sample_names:
            if part == sample or part.startswith(sample):
                return sample
    stem = path.stem
    for suffix in ["_pathabundance", "_genefamilies", "_abundance"]:
        stem = stem.replace(suffix, "")
    return stem or path.parent.name


def parse_humann_table(path: Path, sample_hint: str) -> dict[str, dict[str, float]]:
    lines = [
        line
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line and (not line.startswith("#") or "\t" in line)
    ]
    if not lines:
        return {}
    header = lines[0].lstrip("#").split("\t")
    value_columns = header[1:] or [sample_hint]
    if len(value_columns) == 1:
        value_columns = [sample_hint]
    matrix: dict[str, dict[str, float]] = {}
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        feature = parts[0].strip()
        if not feature:
            continue
        for sample, value in zip(value_columns, parts[1:], strict=False):
            matrix.setdefault(feature, {})[sample] = matrix.setdefault(feature, {}).get(
                sample, 0.0
            ) + parse_float(value)
    return matrix


def find_humann_tables(run_dir: Path, label: str) -> list[Path]:
    root = run_dir / "functional_profile"
    if not root.exists():
        return []
    patterns = {
        "pathabundance": ["*pathabundance*.tsv", "*path_abundance*.tsv"],
        "genefamilies": ["*genefamilies*.tsv", "*gene_families*.tsv"],
    }[label]
    seen: set[Path] = set()
    tables: list[Path] = []
    for pattern in patterns:
        for path in root.rglob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                tables.append(path)
    return sorted(tables)


def write_humann_matrix(path: Path, matrix: dict[str, dict[str, float]], samples: list[str]) -> int:
    observed_samples = sorted({sample for values in matrix.values() for sample in values})
    columns = samples or observed_samples
    for sample in observed_samples:
        if sample not in columns:
            columns.append(sample)
    rows = []
    for feature, values in sorted(
        matrix.items(), key=lambda item: sum(item[1].values()), reverse=True
    ):
        row: dict[str, Any] = {"feature": feature}
        for sample in columns:
            row[sample] = f"{values.get(sample, 0.0):.8g}"
        rows.append(row)
    if rows:
        write_tsv(path, rows, ["feature", *columns])
    return len(rows)


def merge_humann_outputs(run_dir: Path, samples: list[dict[str, str]]) -> dict[str, Any]:
    sample_names = [row["sample"] for row in samples]
    summary: dict[str, Any] = {"status": "not_available", "samples": sample_names, "outputs": {}}
    any_created = False
    for label, output_name in [
        ("pathabundance", "humann_pathabundance_matrix.tsv"),
        ("genefamilies", "humann_genefamilies_matrix.tsv"),
    ]:
        tables = find_humann_tables(run_dir, label)
        combined: dict[str, dict[str, float]] = {}
        for table in tables:
            sample_hint = infer_humann_sample(table, sample_names)
            parsed = parse_humann_table(table, sample_hint)
            for feature, values in parsed.items():
                for sample, value in values.items():
                    combined.setdefault(feature, {})[sample] = (
                        combined.setdefault(feature, {}).get(sample, 0.0) + value
                    )
        feature_count = write_humann_matrix(
            run_dir / "tables" / output_name, combined, sample_names
        )
        summary[label] = {"input_tables": [str(path) for path in tables], "features": feature_count}
        if feature_count:
            summary["outputs"][label] = f"tables/{output_name}"
            any_created = True
    summary["status"] = "created" if any_created else "not_available"
    if not any_created:
        summary["note"] = (
            "No HUMAnN pathabundance or genefamilies tables were found under functional_profile/."
        )
    write_json(run_dir / "tables" / "humann_summary.json", summary)
    return summary


def summarize_backend_outputs(run_dir: Path, samples: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "bracken": merge_bracken_outputs(run_dir, samples),
        "humann": merge_humann_outputs(run_dir, samples),
    }


def read_abundance_matrix(
    path: Path, feature_column: str = "feature"
) -> tuple[list[str], list[dict[str, Any]]]:
    if not path.exists():
        return [], []
    rows, columns = read_table(path)
    if not columns:
        return [], []
    first_col = columns[0]
    sample_columns = [
        column for column in columns[1:] if column not in {"taxonomy_id", "taxonomy_lvl"}
    ]
    parsed: list[dict[str, Any]] = []
    for row in rows:
        feature = row.get(first_col, "").strip()
        if not feature:
            continue
        values = {sample: parse_float(row.get(sample, "")) for sample in sample_columns}
        parsed.append(
            {
                feature_column: feature,
                "taxonomy_id": row.get("taxonomy_id", ""),
                "taxonomy_lvl": row.get("taxonomy_lvl", ""),
                "total_abundance": sum(values.values()),
                **values,
            }
        )
    return sample_columns, parsed


def write_top_rows(
    path: Path, rows: list[dict[str, Any]], key: str, sample_columns: list[str], *, limit: int = 25
) -> int:
    top = sorted(rows, key=lambda row: float(row.get("total_abundance", 0.0)), reverse=True)[:limit]
    if top:
        fieldnames = [
            key,
            "total_abundance",
            *(
                [
                    column
                    for column in ["taxonomy_id", "taxonomy_lvl"]
                    if any(row.get(column) for row in top)
                ]
            ),
            *sample_columns,
        ]
        write_tsv(path, top, fieldnames)
    return len(top)


def write_backend_bar_svg(
    path: Path, title: str, rows: list[dict[str, Any]], key: str, *, empty_message: str
) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    values = [
        (str(row.get(key, "")), float(row.get("total_abundance", 0.0)))
        for row in rows[:15]
        if float(row.get("total_abundance", 0.0)) > 0
    ]
    if not values:
        body = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" role="img" aria-label="{html.escape(title)}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="32" y="48" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#202124">{html.escape(title)}</text>
  <text x="32" y="92" font-family="Arial, sans-serif" font-size="15" fill="#5f6368">{html.escape(empty_message)}</text>
</svg>
"""
        path.write_text(body, encoding="utf-8")
        return str(path)
    width = 980
    row_height = 38
    height = 92 + row_height * len(values)
    max_value = max(value for _, value in values) or 1.0
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img" aria-label="{html.escape(title)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="42" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#202124">{html.escape(title)}</text>',
    ]
    for index, (label, value) in enumerate(values):
        y = 78 + index * row_height
        width_value = max(2.0, min(470.0, value / max_value * 470.0))
        short_label = label if len(label) < 44 else label[:41] + "..."
        lines.extend(
            [
                f'<text x="32" y="{y + 14}" font-family="Arial, sans-serif" font-size="12" fill="#202124">{html.escape(short_label)}</text>',
                f'<rect x="330" y="{y}" width="470" height="17" fill="#eef2f7"/>',
                f'<rect x="330" y="{y}" width="{width_value:.1f}" height="17" fill="#34a853"/>',
                f'<text x="812" y="{y + 13}" font-family="Arial, sans-serif" font-size="12" fill="#202124">{value:.5g}</text>',
            ]
        )
    lines.append("</svg>\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def write_shotgun_review_outputs(run_dir: Path) -> dict[str, Any]:
    outputs: dict[str, str] = {}
    notes: list[str] = []
    status = "not_available"

    def add_output(label: str, rel_path: str) -> None:
        if (run_dir / rel_path).exists():
            outputs[label] = rel_path

    # Surface staged backend-like inputs and normalized matrices so the dashboard
    # does not hide Kraken/Bracken/HUMAnN layers when they were supplied rather
    # than executed in this environment.
    for path in sorted((run_dir / "taxonomic_classification").glob("*.kraken.report")):
        outputs[f"kraken_report:{path.stem}"] = str(path.relative_to(run_dir))
    for path in sorted((run_dir / "taxonomic_classification").glob("*.bracken.tsv")):
        outputs[f"bracken_table:{path.stem}"] = str(path.relative_to(run_dir))
    for path in sorted((run_dir / "functional_profile").rglob("*pathabundance*.tsv")):
        outputs[f"humann_pathabundance:{path.parent.name}"] = str(path.relative_to(run_dir))
    for path in sorted((run_dir / "functional_profile").rglob("*genefamilies*.tsv")):
        outputs[f"humann_genefamilies:{path.parent.name}"] = str(path.relative_to(run_dir))

    add_output("kraken_top_taxa_table", "tables/kraken_top_taxa.tsv")
    add_output("kraken_top_taxa_plot", "visualizations/kraken_top_taxa_barplot.png")
    add_output("bracken_summary", "tables/bracken_summary.json")
    add_output("bracken_est_reads_matrix", "tables/bracken_est_reads_matrix.tsv")
    add_output("bracken_relative_abundance_matrix", "tables/bracken_relative_abundance_matrix.tsv")
    add_output("humann_summary", "tables/humann_summary.json")
    add_output("humann_pathabundance_matrix", "tables/humann_pathabundance_matrix.tsv")
    add_output("humann_genefamilies_matrix", "tables/humann_genefamilies_matrix.tsv")

    bracken_samples, bracken_rows = read_abundance_matrix(
        run_dir / "tables" / "bracken_relative_abundance_matrix.tsv", feature_column="taxon"
    )
    if bracken_rows:
        status = "created"
        write_top_rows(
            run_dir / "tables" / "top_bracken_taxa.tsv", bracken_rows, "taxon", bracken_samples
        )
        write_backend_bar_svg(
            run_dir / "visualizations" / "shotgun_top_taxa.svg",
            "Shotgun Top Bracken Taxa",
            sorted(
                bracken_rows, key=lambda row: float(row.get("total_abundance", 0.0)), reverse=True
            ),
            "taxon",
            empty_message="Bracken abundance matrix is not available.",
        )
        outputs["top_bracken_taxa"] = "tables/top_bracken_taxa.tsv"
        outputs["top_taxa_plot"] = "visualizations/shotgun_top_taxa.svg"
    else:
        notes.append(
            "Bracken relative-abundance matrix is not available; top taxa plot remains unavailable."
        )

    pathway_samples, pathway_rows = read_abundance_matrix(
        run_dir / "tables" / "humann_pathabundance_matrix.tsv", feature_column="feature"
    )
    if pathway_rows:
        status = "created"
        write_top_rows(
            run_dir / "tables" / "top_humann_pathways.tsv", pathway_rows, "feature", pathway_samples
        )
        write_backend_bar_svg(
            run_dir / "visualizations" / "shotgun_top_pathways.svg",
            "Shotgun Top HUMAnN Pathways",
            sorted(
                pathway_rows, key=lambda row: float(row.get("total_abundance", 0.0)), reverse=True
            ),
            "feature",
            empty_message="HUMAnN pathway matrix is not available.",
        )
        outputs["top_humann_pathways"] = "tables/top_humann_pathways.tsv"
        outputs["top_pathways_plot"] = "visualizations/shotgun_top_pathways.svg"
    else:
        notes.append("HUMAnN pathway matrix is not available.")

    gene_samples, gene_rows = read_abundance_matrix(
        run_dir / "tables" / "humann_genefamilies_matrix.tsv", feature_column="feature"
    )
    if gene_rows:
        status = "created"
        write_top_rows(
            run_dir / "tables" / "top_humann_gene_families.tsv", gene_rows, "feature", gene_samples
        )
        write_backend_bar_svg(
            run_dir / "visualizations" / "shotgun_top_gene_families.svg",
            "Shotgun Top HUMAnN Gene Families",
            sorted(gene_rows, key=lambda row: float(row.get("total_abundance", 0.0)), reverse=True),
            "feature",
            empty_message="HUMAnN gene-family matrix is not available.",
        )
        outputs["top_humann_gene_families"] = "tables/top_humann_gene_families.tsv"
        outputs["top_gene_families_plot"] = "visualizations/shotgun_top_gene_families.svg"
    else:
        notes.append("HUMAnN gene-family matrix is not available.")

    if any(
        label.startswith(
            ("kraken_report:", "bracken_table:", "humann_pathabundance:", "humann_genefamilies:")
        )
        for label in outputs
    ):
        notes.append(
            "Dashboard rows include staged support inputs when Kraken/Bracken/HUMAnN outputs were supplied rather than executed locally."
        )

    dashboard_rows = []
    for label, rel_path in outputs.items():
        href = (
            rel_path.replace("visualizations/", "", 1)
            if rel_path.startswith("visualizations/")
            else f"../{rel_path}"
        )
        dashboard_rows.append(
            f'<tr><td>{html.escape(label)}</td><td><a href="{html.escape(href)}">{html.escape(rel_path)}</a></td></tr>'
        )
    if not dashboard_rows:
        dashboard_rows.append(
            '<tr><td colspan="2">No database-derived shotgun review outputs are available yet.</td></tr>'
        )
    dashboard = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Shotgun Metagenomics Backend Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 28px; color: #202124; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f6f8fa; }}
  </style>
</head>
<body>
  <h1>Shotgun Metagenomics Backend Dashboard</h1>
  <p>Native review of Kraken, Bracken, and HUMAnN inputs plus normalized downstream outputs. When local backends are unavailable, supplied support tables are surfaced alongside the derived matrices and plots.</p>
  <table><thead><tr><th>Artifact</th><th>Path</th></tr></thead><tbody>{"".join(dashboard_rows)}</tbody></table>
  <h2>Notes</h2>
  <ul>{"".join(f"<li>{html.escape(note)}</li>" for note in notes)}</ul>
</body>
</html>
"""
    dashboard_path = run_dir / "visualizations" / "shotgun_backend_dashboard.html"
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(dashboard, encoding="utf-8")
    outputs["dashboard"] = "visualizations/shotgun_backend_dashboard.html"
    summary = {
        "status": status,
        "outputs": outputs,
        "notes": notes,
        "bracken_taxa": len(bracken_rows),
        "humann_pathways": len(pathway_rows),
        "humann_gene_families": len(gene_rows),
    }
    write_json(run_dir / "tables" / "metagenomics_backend_review.json", summary)
    return summary


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
    write_json(run_dir / "workflow" / "shotgun_backend_command_plan.json", {"commands": plan})
    write_command_script(run_dir / "commands.sh", [item["command"] for item in plan])
    write_json(
        run_dir / "qc" / "metagenomics_database_status.json",
        {
            "kraken_db": validation.get("kraken_db"),
            "bracken_db": validation.get("bracken_db"),
            "humann_db": validation.get("humann_db"),
            "host_reference": validation.get("host_reference"),
            "warnings": validation.get("warnings", []),
        },
    )
    summarize_backend_outputs(run_dir, samples)
    write_shotgun_review_outputs(run_dir)


def execute_plan(run_dir: Path, plan: list[dict[str, Any]]) -> dict[str, Any]:
    for dirname in ["taxonomic_classification", "functional_profile", "tables", "logs", "workflow"]:
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
            title="Shotgun Samples",
            path="validation/samples.normalized.tsv",
            kind="table",
            status="created",
            description="Normalized shotgun sample FASTQ manifest.",
        ),
        artifact_entry(
            artifact_id="command_plan",
            title="Backend Command Plan",
            path="workflow/shotgun_backend_command_plan.json",
            kind="json",
            status="created",
            description="Kraken2, Bracken, and HUMAnN execution commands.",
        ),
        artifact_entry(
            artifact_id="database_status",
            title="Database Status",
            path="qc/metagenomics_database_status.json",
            kind="json",
            status="created",
            description="Resolved database and host-reference paths.",
        ),
        artifact_entry(
            artifact_id="host_depletion",
            title="Host Depletion Outputs",
            path="host_depletion",
            kind="directory",
            status="created" if (run_dir / "host_depletion").exists() else "not_available",
            description="KneadData cleaned reads when a host reference is supplied.",
        ),
        artifact_entry(
            artifact_id="kraken_reports",
            title="Kraken Reports",
            path="taxonomic_classification",
            kind="directory",
            status="created"
            if (run_dir / "taxonomic_classification").exists()
            else "not_available",
            description="Taxonomic classification outputs after execution.",
        ),
        artifact_entry(
            artifact_id="bracken_matrix",
            title="Bracken Relative Abundance Matrix",
            path="tables/bracken_relative_abundance_matrix.tsv",
            kind="table",
            status="created"
            if (run_dir / "tables" / "bracken_relative_abundance_matrix.tsv").exists()
            else "not_available",
            description="Merged Bracken relative abundance by taxon and sample.",
        ),
        artifact_entry(
            artifact_id="humann_pathabundance",
            title="HUMAnN Pathway Matrix",
            path="tables/humann_pathabundance_matrix.tsv",
            kind="table",
            status="created"
            if (run_dir / "tables" / "humann_pathabundance_matrix.tsv").exists()
            else "not_available",
            description="Merged HUMAnN pathway abundance by feature and sample.",
        ),
        artifact_entry(
            artifact_id="humann_genefamilies",
            title="HUMAnN Gene Family Matrix",
            path="tables/humann_genefamilies_matrix.tsv",
            kind="table",
            status="created"
            if (run_dir / "tables" / "humann_genefamilies_matrix.tsv").exists()
            else "not_available",
            description="Merged HUMAnN gene-family abundance by feature and sample.",
        ),
        artifact_entry(
            artifact_id="backend_summaries",
            title="Backend Output Summaries",
            path="tables",
            kind="directory",
            status="created",
            description="JSON summaries documenting which Bracken/HUMAnN backend artifacts were found and normalized.",
        ),
        artifact_entry(
            artifact_id="backend_review",
            title="Backend Review Summary",
            path="tables/metagenomics_backend_review.json",
            kind="json",
            status="created",
            description="Native review summary for normalized Bracken/HUMAnN tables and plots.",
        ),
        artifact_entry(
            artifact_id="backend_dashboard",
            title="Backend Dashboard",
            path="visualizations/shotgun_backend_dashboard.html",
            kind="html",
            status="created",
            description="Native dashboard for taxonomic and functional backend outputs.",
        ),
        artifact_entry(
            artifact_id="top_taxa_plot",
            title="Top Taxa Plot",
            path="visualizations/shotgun_top_taxa.svg",
            kind="svg",
            status="created"
            if (run_dir / "visualizations" / "shotgun_top_taxa.svg").exists()
            else "not_available",
            description="Top Bracken taxa plot from normalized relative abundance matrix.",
        ),
        artifact_entry(
            artifact_id="top_pathways_plot",
            title="Top Pathways Plot",
            path="visualizations/shotgun_top_pathways.svg",
            kind="svg",
            status="created"
            if (run_dir / "visualizations" / "shotgun_top_pathways.svg").exists()
            else "not_available",
            description="Top HUMAnN pathway plot from normalized pathabundance matrix.",
        ),
        artifact_entry(
            artifact_id="top_gene_families_plot",
            title="Top Gene Families Plot",
            path="visualizations/shotgun_top_gene_families.svg",
            kind="svg",
            status="created"
            if (run_dir / "visualizations" / "shotgun_top_gene_families.svg").exists()
            else "not_available",
            description="Top HUMAnN gene-family plot from normalized genefamilies matrix.",
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
                    description="Database readiness gate for Kraken2, Bracken, and HUMAnN bundles.",
                ),
                artifact_entry(
                    artifact_id="resource_manifest",
                    title="Resource Manifest",
                    path="resources/resource_manifest.tsv",
                    kind="table",
                    status="created",
                    description="Resolved database roots, expected files, and missing-file counts.",
                ),
                artifact_entry(
                    artifact_id="resource_plan",
                    title="Resource Plan",
                    path="resources/resource_plan.json",
                    kind="json",
                    status="created",
                    description="Structured database readiness plan used to gate this run.",
                ),
                artifact_entry(
                    artifact_id="resource_setup_plan",
                    title="Resource Setup Plan",
                    path="resources/resource_setup_plan.md",
                    kind="markdown",
                    status="created",
                    description="Actionable setup checklist for missing Kraken2, Bracken, and HUMAnN bundles.",
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
    index = write_visualization_index(
        run_dir,
        title="Shotgun Metagenomics Backend Review",
        description="Review surface for taxonomic classification, Bracken abundance, HUMAnN functional profiles, and database provenance.",
        entries=entries,
        notes=[*validation.get("warnings", []), *resource_blockers(resource_plan)],
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
        "# Shotgun Metagenomics Backend Run Summary",
        "",
        f"Status: `{status}`",
        f"Samples parsed: `{validation.get('sample_count', 0)}`",
        "",
        "## Key Artifacts",
        "",
        "- `workflow/shotgun_backend_command_plan.json`",
        "- `qc/metagenomics_database_status.json`",
        "- `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts",
        "- `host_depletion/` cleaned FASTQs when `--host-reference` is supplied",
        "- `taxonomic_classification/*.kraken.report` and `*.bracken.tsv` when executed",
        "- `tables/bracken_*_matrix.tsv` when Bracken outputs are available",
        "- `tables/humann_*_matrix.tsv` when HUMAnN outputs are available",
        "- `tables/metagenomics_backend_review.json`, `tables/top_*`, and `visualizations/shotgun_*` native backend review files",
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
        lines.append(
            f"Setup plan: `{resource_plan.get('outputs', {}).get('resource_setup_summary', 'resources/resource_setup_plan.md')}`"
        )
        for item in resource_plan.get("resources", []):
            state = "ready" if item.get("ok") else "missing"
            required = "required" if item.get("required") else "optional"
            lines.append(f"- `{item.get('bundle')}` ({required}): {state}")
        lines.append("")
    if validation.get("errors"):
        lines.extend(["## Blockers", ""])
        lines.extend(f"- {item}" for item in validation["errors"])
    write_text(run_dir / "summary.md", "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-sheet", type=Path, required=True)
    parser.add_argument("--kraken-db", type=Path, required=True)
    parser.add_argument("--bracken-db", type=Path)
    parser.add_argument("--run-bracken", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--bracken-level", default="S")
    parser.add_argument("--read-length", type=int, default=150)
    parser.add_argument("--run-humann", action="store_true")
    parser.add_argument("--humann-db", type=Path)
    parser.add_argument("--host-reference", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument(
        "--include-optional-resources",
        action="store_true",
        help="Include optional database bundles in readiness output even if their analysis steps are not requested.",
    )
    parser.add_argument(
        "--resource-checksums",
        action="store_true",
        help="Compute checksums for database files below the reference-manager checksum threshold.",
    )
    parser.add_argument(
        "--skip-resource-plan",
        action="store_true",
        help="Skip registry-level database readiness checks and rely only on path/tool validation.",
    )
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--run-id", default=slug_timestamp("shotgun-metagenomics-backend"))
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
    if args.run_bracken and args.bracken_db:
        effective_read_length, read_length_warning = resolve_bracken_read_length(
            args.bracken_db.expanduser().resolve(), args.read_length
        )
        if read_length_warning:
            input_validation.setdefault("warnings", []).append(read_length_warning)
        args.read_length = effective_read_length
    resource_plan = write_resource_plan(args, run_dir)
    validation = merge_resource_status(input_validation, resource_plan)
    required = (
        ["kraken2"]
        + (["bracken"] if args.run_bracken else [])
        + (["humann"] if args.run_humann else [])
        + (["kneaddata"] if args.host_reference else [])
    )
    optional = ["metaphlan", "multiqc"] + ([] if args.host_reference else ["kneaddata"])
    tool_status = tool_preflight(required, optional=optional)
    plan = build_plan(args, samples)
    write_json(run_dir / "config.json", {**serializable_args(args), "run_dir": str(run_dir)})
    write_json(run_dir / "validation" / "input_validation_summary.json", input_validation)
    write_json(run_dir / "validation" / "validation_summary.json", validation)
    write_json(run_dir / "validation" / "tool_preflight.json", tool_status)
    write_json(
        run_dir / "versions" / "software_versions.json",
        software_versions(
            {
                "kraken2": ["kraken2", "--version"],
                "bracken": ["bracken", "-v"],
                "humann": ["humann", "--version"],
            }
        ),
    )
    write_outputs(run_dir, validation, samples, plan)
    dry_run = {
        "ok": validation["ok"] and tool_status["ok"],
        "detail": "shotgun sample, database, and tool validation completed",
    }
    write_json(run_dir / "logs" / "validation_dry_run.json", dry_run)
    status = "blocked" if not dry_run["ok"] else "validated"
    execution = None
    if args.execute and dry_run["ok"]:
        execution = execute_plan(run_dir, plan)
        status = "completed" if execution.get("ok") else "failed"
        summarize_backend_outputs(run_dir, samples)
        write_shotgun_review_outputs(run_dir)
    visuals = write_visuals(run_dir, status, validation, resource_plan)
    resource_outputs = resource_plan.get("outputs", {}) if resource_plan else {}
    write_standard_manifest(
        run_dir,
        run_id=args.run_id,
        lane="shotgun_metagenomics",
        workflow="backend_kraken2_bracken_humann",
        status=status,
        execute_requested=args.execute,
        validation=validation,
        tool_preflight_result=tool_status,
        dry_run=dry_run,
        execution=execution,
        inputs={
            "sample_sheet": str(args.sample_sheet.expanduser().resolve()),
            "kraken_db": str(args.kraken_db.expanduser().resolve()),
            "bracken_db": str(args.bracken_db.expanduser().resolve()) if args.bracken_db else None,
            "humann_db": str(args.humann_db.expanduser().resolve()) if args.humann_db else None,
            "metadata": str(args.metadata.expanduser().resolve()) if args.metadata else None,
            **(
                {"resource_plan": resource_outputs.get("resource_plan")} if resource_outputs else {}
            ),
        },
        outputs={
            "sample_table": "validation/samples.normalized.tsv",
            "command_plan": "workflow/shotgun_backend_command_plan.json",
            "database_status": "qc/metagenomics_database_status.json",
            "host_depletion": "host_depletion/" if args.host_reference else None,
            "kraken_reports": "taxonomic_classification/*.kraken.report",
            "bracken_tables": "taxonomic_classification/*.bracken.tsv",
            "bracken_est_reads_matrix": "tables/bracken_est_reads_matrix.tsv",
            "bracken_relative_abundance_matrix": "tables/bracken_relative_abundance_matrix.tsv",
            "humann_pathabundance_matrix": "tables/humann_pathabundance_matrix.tsv",
            "humann_genefamilies_matrix": "tables/humann_genefamilies_matrix.tsv",
            "backend_summaries": ["tables/bracken_summary.json", "tables/humann_summary.json"],
            "backend_review": "tables/metagenomics_backend_review.json",
            "top_bracken_taxa": "tables/top_bracken_taxa.tsv",
            "top_humann_pathways": "tables/top_humann_pathways.tsv",
            "top_humann_gene_families": "tables/top_humann_gene_families.tsv",
            "backend_dashboard": "visualizations/shotgun_backend_dashboard.html",
            "top_taxa_plot": "visualizations/shotgun_top_taxa.svg",
            "top_pathways_plot": "visualizations/shotgun_top_pathways.svg",
            "top_gene_families_plot": "visualizations/shotgun_top_gene_families.svg",
            **resource_outputs,
            **visuals,
        },
        method={
            "taxonomic_classifier": "Kraken2",
            "host_depletion": "KneadData" if args.host_reference else None,
            "host_reference": str(args.host_reference.expanduser().resolve())
            if args.host_reference
            else None,
            "abundance_estimator": "Bracken" if args.run_bracken else None,
            "functional_profiler": "HUMAnN" if args.run_humann else None,
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
