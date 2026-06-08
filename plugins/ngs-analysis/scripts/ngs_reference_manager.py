#!/usr/bin/env python3
"""Inspect and verify local NGS reference and database bundles."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from ngs_run_utils import now_iso, sha256_file, write_json

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE_REGISTRY = PLUGIN_ROOT / "references" / "reference-registry.json"
DEFAULT_DATABASE_REGISTRY = PLUGIN_ROOT / "references" / "database-registry.json"
MAX_CHECKSUM_BYTES = 512 * 1024 * 1024
PIPELINE_RESOURCE_REQUIREMENTS: dict[str, list[dict[str, Any]]] = {
    "bulk_rnaseq_counts_qc": [
        {
            "kind": "reference",
            "selector": "genome_core",
            "required": True,
            "purpose": "genome FASTA, annotation GTF, and aligner/quantification indexes",
        }
    ],
    "scrnaseq_fastq_to_count": [
        {
            "kind": "reference",
            "selector": "genome_core",
            "required": True,
            "purpose": "single-cell count-generation reference FASTA and annotation",
        }
    ],
    "dna_variant_calling": [
        {
            "kind": "reference",
            "selector": "genome_core",
            "required": True,
            "purpose": "reference FASTA, sequence dictionary, indexes, and known-sites resources",
        }
    ],
    "dna_germline_variants": [
        {
            "kind": "reference",
            "selector": "genome_core",
            "required": True,
            "purpose": "GATK/DeepVariant germline reference and known-sites resources",
        }
    ],
    "dna_somatic_variants": [
        {
            "kind": "reference",
            "selector": "genome_core",
            "required": True,
            "purpose": "Mutect2 reference, indexes, blacklist, and optional cancer resources",
        }
    ],
    "dna_umi_panel_variants": [
        {
            "kind": "reference",
            "selector": "genome_core",
            "required": True,
            "purpose": "panel reference FASTA/indexes and target-coverage context",
        }
    ],
    "atacseq_peaks_qc": [
        {
            "kind": "reference",
            "selector": "genome_core",
            "required": True,
            "purpose": "alignment FASTA/indexes, blacklist, TSS annotation, and genome-build context",
        }
    ],
    "chip_cutrun_peaks_qc": [
        {
            "kind": "reference",
            "selector": "genome_core",
            "required": True,
            "purpose": "alignment FASTA/indexes, blacklist, and genome-build context",
        }
    ],
    "amplicon_microbiome": [
        {
            "kind": "database",
            "bundle": "silva_138_amplicon",
            "required": True,
            "purpose": "marker-gene taxonomy assignment",
        },
        {
            "kind": "database",
            "bundle": "gtdb_release",
            "required": False,
            "purpose": "optional alternate taxonomy database",
        },
    ],
    "shotgun_metagenomics": [
        {
            "kind": "database",
            "bundle": "kraken2_standard",
            "required": True,
            "purpose": "Kraken2 taxonomic classification",
        },
        {
            "kind": "database",
            "bundle": "bracken_standard",
            "required": False,
            "purpose": "Bracken abundance estimation paired to the Kraken2 database",
        },
        {
            "kind": "database",
            "bundle": "humann_uniref90",
            "required": False,
            "purpose": "HUMAnN functional profiling",
        },
    ],
}
PIPELINE_ALIASES = {
    "bulk_rnaseq": "bulk_rnaseq_counts_qc",
    "rnaseq": "bulk_rnaseq_counts_qc",
    "scrna": "scrnaseq_fastq_to_count",
    "scrnaseq": "scrnaseq_fastq_to_count",
    "scrnaseq_fastq": "scrnaseq_fastq_to_count",
    "sarek": "dna_variant_calling",
    "germline": "dna_germline_variants",
    "somatic": "dna_somatic_variants",
    "umi": "dna_umi_panel_variants",
    "atacseq": "atacseq_peaks_qc",
    "chipseq": "chip_cutrun_peaks_qc",
    "cutandrun": "chip_cutrun_peaks_qc",
    "cutandtag": "chip_cutrun_peaks_qc",
    "ampliseq": "amplicon_microbiome",
    "taxprofiler": "shotgun_metagenomics",
}
GENOME_BUILD_TO_REFERENCE = {
    "grch38": "grch38_core",
    "hg38": "grch38_core",
    "human": "grch38_core",
    "grcm39": "grcm39_core",
    "mm39": "grcm39_core",
    "mouse": "grcm39_core",
    "reduced": "reduced_micro_genome",
    "reduced_local": "reduced_micro_genome",
    "synthetic": "reduced_micro_genome",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expand_root(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(os.path.expandvars(value)).expanduser().resolve()


def load_registries(
    reference_registry: Path = DEFAULT_REFERENCE_REGISTRY,
    database_registry: Path = DEFAULT_DATABASE_REGISTRY,
) -> dict[str, Any]:
    references = read_json(reference_registry)
    databases = read_json(database_registry)
    return {
        "schema_version": {
            "references": references.get("schema_version"),
            "databases": databases.get("schema_version"),
        },
        "references": references.get("references", {}),
        "databases": databases.get("databases", {}),
    }


def bundle_root(bundle: dict[str, Any], override_root: Path | None = None) -> Path | None:
    if override_root:
        return override_root.expanduser().resolve()
    for key in ("root", "root_env"):
        value = bundle.get(key)
        if key == "root_env" and value:
            expanded = expand_root(os.environ.get(str(value)))
        else:
            expanded = expand_root(value)
        if expanded:
            return expanded
    return None


def env_assignment(bundle: dict[str, Any], root: str | None) -> dict[str, Any] | None:
    root_env = bundle.get("root_env")
    if not root_env:
        return None
    return {"name": str(root_env), "value": root}


def check_expected_files(
    *,
    bundle_name: str,
    bundle: dict[str, Any],
    override_root: Path | None = None,
    include_checksums: bool = False,
) -> dict[str, Any]:
    root = bundle_root(bundle, override_root)
    expected = bundle.get("required_files", [])
    records: list[dict[str, Any]] = []
    missing: list[str] = []
    for item in expected:
        rel_path = str(item)
        resolved = (root / rel_path).resolve() if root else None
        exists = bool(resolved and resolved.exists())
        record: dict[str, Any] = {
            "path": rel_path,
            "resolved_path": str(resolved) if resolved else None,
            "exists": exists,
            "bytes": resolved.stat().st_size
            if exists and resolved and resolved.is_file()
            else None,
            "sha256": None,
        }
        if not exists:
            missing.append(rel_path)
        elif include_checksums and resolved and resolved.is_file():
            size = resolved.stat().st_size
            if size <= MAX_CHECKSUM_BYTES:
                record["sha256"] = sha256_file(resolved)
            else:
                record["sha256_skipped_reason"] = (
                    f"file exceeds {MAX_CHECKSUM_BYTES} byte checksum threshold"
                )
        records.append(record)
    return {
        "bundle": bundle_name,
        "display_name": bundle.get("display_name", bundle_name),
        "kind": bundle.get("kind"),
        "root": str(root) if root else None,
        "ok": not missing and root is not None,
        "missing": missing,
        "files": records,
        "metadata": {
            "genome_build": bundle.get("genome_build"),
            "database_family": bundle.get("database_family"),
            "version": bundle.get("version"),
            "source": bundle.get("source"),
            "license_note": bundle.get("license_note"),
        },
    }


def check_named_bundle(
    name: str,
    *,
    kind: str = "reference",
    root: Path | None = None,
    include_checksums: bool = False,
    registries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registries = registries or load_registries()
    collection_name = "references" if kind == "reference" else "databases"
    collection = registries.get(collection_name, {})
    if name not in collection:
        return {
            "bundle": name,
            "kind": kind,
            "ok": False,
            "missing": [],
            "error": f"unknown {kind} bundle: {name}",
            "available": sorted(collection),
        }
    return check_expected_files(
        bundle_name=name,
        bundle=collection[name],
        override_root=root,
        include_checksums=include_checksums,
    )


def normalize_pipeline_name(value: str) -> str:
    key = value.strip().lower().replace("-", "_").replace("/", "_")
    return PIPELINE_ALIASES.get(key, key)


def reference_bundle_for_genome(genome_build: str | None) -> str:
    if not genome_build:
        return "grch38_core"
    return GENOME_BUILD_TO_REFERENCE.get(genome_build.strip().lower(), genome_build)


def parse_bundle_roots(values: list[str] | None) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for raw in values or []:
        if "=" not in raw:
            raise SystemExit(f"--bundle-root must be formatted as bundle=/path, got: {raw}")
        name, value = raw.split("=", 1)
        name = name.strip()
        if not name:
            raise SystemExit(f"--bundle-root is missing bundle name: {raw}")
        roots[name] = Path(value).expanduser().resolve()
    return roots


def resource_requirements_for_pipeline(
    pipeline: str,
    *,
    genome_build: str | None = None,
    include_optional: bool = False,
) -> tuple[str, list[dict[str, Any]]]:
    normalized = normalize_pipeline_name(pipeline)
    if normalized not in PIPELINE_RESOURCE_REQUIREMENTS:
        raise SystemExit(
            f"Unknown pipeline resource contract: {pipeline}. "
            f"Known pipelines: {', '.join(sorted(PIPELINE_RESOURCE_REQUIREMENTS))}"
        )
    resolved: list[dict[str, Any]] = []
    for requirement in PIPELINE_RESOURCE_REQUIREMENTS[normalized]:
        if not requirement.get("required", True) and not include_optional:
            continue
        item = dict(requirement)
        if item.get("selector") == "genome_core":
            item["bundle"] = reference_bundle_for_genome(genome_build)
            item.pop("selector", None)
        resolved.append(item)
    return normalized, resolved


def plan_pipeline_resources(
    pipeline: str,
    *,
    genome_build: str | None = None,
    bundle_roots: dict[str, Path] | None = None,
    include_optional: bool = False,
    include_checksums: bool = False,
    registries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registries = registries or load_registries()
    bundle_roots = bundle_roots or {}
    normalized, requirements = resource_requirements_for_pipeline(
        pipeline,
        genome_build=genome_build,
        include_optional=include_optional,
    )
    resources = []
    for requirement in requirements:
        bundle = requirement["bundle"]
        kind = requirement["kind"]
        root = bundle_roots.get(bundle)
        check = check_named_bundle(
            bundle,
            kind=kind,
            root=root,
            include_checksums=include_checksums,
            registries=registries,
        )
        collection_name = "references" if kind == "reference" else "databases"
        bundle_payload = registries.get(collection_name, {}).get(bundle, {})
        resources.append(
            {
                "kind": kind,
                "bundle": bundle,
                "required": bool(requirement.get("required", True)),
                "purpose": requirement.get("purpose"),
                "ok": bool(check.get("ok")),
                "blocking": bool(requirement.get("required", True)) and not bool(check.get("ok")),
                "root": check.get("root"),
                "env": env_assignment(bundle_payload, check.get("root")),
                "check": check,
                "setup": {
                    "source": bundle_payload.get("source"),
                    "license_note": bundle_payload.get("license_note"),
                    "suggested_setup": bundle_payload.get("suggested_setup", []),
                    "estimated_size": bundle_payload.get("estimated_size"),
                },
            }
        )
    missing_required = [
        {
            "kind": item["kind"],
            "bundle": item["bundle"],
            "root": item["root"],
            "missing": item["check"].get("missing", []),
            "error": item["check"].get("error"),
        }
        for item in resources
        if item["blocking"]
    ]
    return {
        "created_at": now_iso(),
        "pipeline": normalized,
        "requested_pipeline": pipeline,
        "genome_build": genome_build,
        "include_optional": include_optional,
        "ok": not missing_required,
        "missing_required": missing_required,
        "resources": resources,
    }


def resource_manifest_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in plan.get("resources", []):
        check = item.get("check", {})
        metadata = check.get("metadata", {})
        env = item.get("env") or {}
        rows.append(
            {
                "pipeline": plan.get("pipeline", ""),
                "kind": item.get("kind", ""),
                "bundle": item.get("bundle", ""),
                "required": str(item.get("required", False)).lower(),
                "ok": str(item.get("ok", False)).lower(),
                "blocking": str(item.get("blocking", False)).lower(),
                "root": item.get("root") or "",
                "env_var": env.get("name", ""),
                "purpose": item.get("purpose") or "",
                "missing_count": len(check.get("missing", [])),
                "missing_files": ";".join(check.get("missing", [])),
                "source": metadata.get("source") or "",
                "license_note": metadata.get("license_note") or "",
            }
        )
    return rows


def write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\t".join(fieldnames) + "\n")
        for row in rows:
            handle.write(
                "\t".join(str(row.get(field, "")).replace("\n", " ") for field in fieldnames) + "\n"
            )


def validation_command_for_resource(action: dict[str, Any]) -> str:
    root = action.get("root")
    root_env = action.get("root_env")
    if root:
        root_arg = json.dumps(str(root))
    elif root_env:
        root_arg = f'"${{{root_env}:-/path/to/{action.get("bundle")}}}"'
    else:
        root_arg = f'"/path/to/{action.get("bundle")}"'
    return (
        "python plugins/ngs-analysis/scripts/ngs_reference_manager.py check "
        f"--kind {action.get('kind')} --bundle {action.get('bundle')} --root {root_arg}"
    )


def resource_setup_action(plan: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    check = item.get("check", {})
    env = item.get("env") or {}
    setup = item.get("setup") or {}
    missing_files = list(check.get("missing", []))
    root = item.get("root") or check.get("root")
    action = {
        "pipeline": plan.get("pipeline"),
        "requested_pipeline": plan.get("requested_pipeline"),
        "genome_build": plan.get("genome_build"),
        "kind": item.get("kind"),
        "bundle": item.get("bundle"),
        "display_name": check.get("display_name") or item.get("bundle"),
        "required": bool(item.get("required")),
        "blocking": bool(item.get("blocking")),
        "ok": bool(item.get("ok")),
        "root": root,
        "root_env": env.get("name", ""),
        "purpose": item.get("purpose") or "",
        "missing_files": missing_files,
        "missing_count": len(missing_files),
        "error": check.get("error"),
        "source": setup.get("source"),
        "license_note": setup.get("license_note"),
        "estimated_size": setup.get("estimated_size"),
        "suggested_setup": list(setup.get("suggested_setup") or []),
    }
    next_actions: list[str] = []
    if not root:
        if action["root_env"]:
            next_actions.append(
                f"Choose or create a local bundle root and export {action['root_env']}=/path/to/{action['bundle']}."
            )
        else:
            next_actions.append(
                f"Choose or create a local bundle root for {action['bundle']} and pass it with --bundle-root."
            )
    elif missing_files:
        next_actions.append(
            f"Complete the bundle under {root} by adding the missing contract files."
        )
    if action.get("error"):
        next_actions.append(str(action["error"]))
    if missing_files:
        next_actions.append("Missing files: " + ", ".join(missing_files))
    if action["suggested_setup"]:
        next_actions.append(
            "Review and adapt the registry setup hints before downloading or generating large resources."
        )
    action["validation_command"] = validation_command_for_resource(action)
    next_actions.append("Re-run the validation command after setup.")
    action["next_actions"] = next_actions
    action["ready_after"] = {
        "root_configured": "yes" if root else "pending",
        "missing_files": "none" if not missing_files else "all missing files present",
        "validation_command": action["validation_command"],
    }
    return action


def setup_plan_from_resource_plan(
    plan: dict[str, Any], *, include_ready: bool = False
) -> dict[str, Any]:
    actions = [
        resource_setup_action(plan, item)
        for item in plan.get("resources", [])
        if include_ready or not item.get("ok")
    ]
    return {
        "schema_version": "ngs_resource_setup_plan/v0.1",
        "created_at": now_iso(),
        "pipeline": plan.get("pipeline"),
        "requested_pipeline": plan.get("requested_pipeline"),
        "genome_build": plan.get("genome_build"),
        "include_optional": bool(plan.get("include_optional")),
        "include_ready": include_ready,
        "resource_plan_ok": bool(plan.get("ok")),
        "ok": not any(action.get("blocking") for action in actions),
        "action_count": len(actions),
        "blocking_count": sum(1 for action in actions if action.get("blocking")),
        "actions": actions,
    }


def resource_setup_plan_rows(setup_plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for action in setup_plan.get("actions", []):
        rows.append(
            {
                "pipeline": setup_plan.get("pipeline", ""),
                "kind": action.get("kind", ""),
                "bundle": action.get("bundle", ""),
                "display_name": action.get("display_name", ""),
                "required": str(action.get("required", False)).lower(),
                "blocking": str(action.get("blocking", False)).lower(),
                "ok": str(action.get("ok", False)).lower(),
                "root": action.get("root") or "",
                "root_env": action.get("root_env") or "",
                "purpose": action.get("purpose") or "",
                "missing_count": action.get("missing_count", 0),
                "missing_files": ";".join(action.get("missing_files", [])),
                "estimated_size": action.get("estimated_size") or "",
                "source": action.get("source") or "",
                "license_note": action.get("license_note") or "",
                "suggested_setup": "; ".join(
                    str(item) for item in action.get("suggested_setup", [])
                ),
                "validation_command": action.get("validation_command") or "",
            }
        )
    return rows


def write_resource_setup_markdown(setup_plan: dict[str, Any], path: Path) -> None:
    lines = [
        "# NGS Resource Setup Plan",
        "",
        f"Created: `{setup_plan.get('created_at')}`",
        f"Pipeline: `{setup_plan.get('pipeline')}`",
        f"Resource plan ready: `{str(setup_plan.get('resource_plan_ok')).lower()}`",
        f"Setup actions: `{setup_plan.get('action_count')}`",
        f"Blocking setup actions: `{setup_plan.get('blocking_count')}`",
        "",
        "This file is a setup checklist. Review license, size, and source notes before downloading or generating large references/databases.",
        "",
    ]
    actions = setup_plan.get("actions", [])
    if not actions:
        lines.append("No missing resources were selected for setup planning.")
    for action in actions:
        required = "required" if action.get("required") else "optional"
        state = "ready" if action.get("ok") else "missing"
        lines.extend(
            [
                f"## `{action.get('bundle')}`",
                "",
                f"Display name: {action.get('display_name')}",
                f"Kind: `{action.get('kind')}`",
                f"State: `{state}`",
                f"Requirement: `{required}`",
                f"Blocking: `{str(action.get('blocking')).lower()}`",
                f"Purpose: {action.get('purpose') or 'not specified'}",
                f"Root: `{action.get('root') or 'not configured'}`",
                f"Env var: `{action.get('root_env') or 'none'}`",
            ]
        )
        if action.get("estimated_size"):
            lines.append(f"Estimated size: {action['estimated_size']}")
        if action.get("source"):
            lines.append(f"Source: {action['source']}")
        if action.get("license_note"):
            lines.append(f"License/source note: {action['license_note']}")
        if action.get("missing_files"):
            lines.extend(["", "Missing files:"])
            lines.extend(f"- `{item}`" for item in action["missing_files"])
        if action.get("next_actions"):
            lines.extend(["", "Next actions:"])
            lines.extend(f"- {item}" for item in action["next_actions"])
        if action.get("suggested_setup"):
            lines.extend(["", "Suggested setup hints:", "", "```bash"])
            lines.extend(str(command) for command in action["suggested_setup"])
            lines.append("```")
        lines.extend(
            [
                "",
                "Validation command:",
                "",
                "```bash",
                str(action.get("validation_command")),
                "```",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_resource_setup_commands(setup_plan: dict[str, Any], path: Path) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Review and edit placeholder paths before running.",
        "# Large reference/database setup may require license, quota, and disk-space review.",
        "# Registry setup hints are commented by default to avoid accidental large downloads.",
        "",
    ]
    actions = setup_plan.get("actions", [])
    if not actions:
        lines.append("# No setup actions selected.")
    for action in actions:
        lines.extend(
            [
                f"# === {action.get('bundle')} ({action.get('kind')}) ===",
                f"# Purpose: {action.get('purpose') or 'not specified'}",
                f"# Required: {str(action.get('required')).lower()}",
                f"# Blocking: {str(action.get('blocking')).lower()}",
                f"# Root: {action.get('root') or 'not configured'}",
            ]
        )
        if action.get("root_env"):
            root_value = action.get("root") or f"/path/to/{action.get('bundle')}"
            lines.append(f"# export {action['root_env']}={json.dumps(str(root_value))}")
        if action.get("estimated_size"):
            lines.append(f"# Estimated size: {action['estimated_size']}")
        if action.get("license_note"):
            lines.append(f"# License/source note: {action['license_note']}")
        if action.get("missing_files"):
            lines.append("# Missing files:")
            lines.extend(f"# - {item}" for item in action["missing_files"])
        if action.get("suggested_setup"):
            lines.append("# Suggested setup hints:")
            lines.extend(f"# {command}" for command in action["suggested_setup"])
        lines.append(f"# Validate after setup: {action.get('validation_command')}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_resource_setup_plan_outputs(setup_plan: dict[str, Any], outdir: Path) -> dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir / "resource_setup_plan.json", setup_plan)
    fieldnames = [
        "pipeline",
        "kind",
        "bundle",
        "display_name",
        "required",
        "blocking",
        "ok",
        "root",
        "root_env",
        "purpose",
        "missing_count",
        "missing_files",
        "estimated_size",
        "source",
        "license_note",
        "suggested_setup",
        "validation_command",
    ]
    write_tsv(outdir / "resource_setup_plan.tsv", resource_setup_plan_rows(setup_plan), fieldnames)
    write_resource_setup_commands(setup_plan, outdir / "resource_setup_commands.sh")
    write_resource_setup_markdown(setup_plan, outdir / "resource_setup_plan.md")
    return {
        "resource_setup_plan": str(outdir / "resource_setup_plan.json"),
        "resource_setup_plan_tsv": str(outdir / "resource_setup_plan.tsv"),
        "resource_setup_commands": str(outdir / "resource_setup_commands.sh"),
        "resource_setup_summary": str(outdir / "resource_setup_plan.md"),
    }


def write_resource_plan_outputs(plan: dict[str, Any], outdir: Path) -> dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir / "resource_plan.json", plan)
    fieldnames = [
        "pipeline",
        "kind",
        "bundle",
        "required",
        "ok",
        "blocking",
        "root",
        "env_var",
        "purpose",
        "missing_count",
        "missing_files",
        "source",
        "license_note",
    ]
    write_tsv(outdir / "resource_manifest.tsv", resource_manifest_rows(plan), fieldnames)
    env_lines = [
        "#!/usr/bin/env bash",
        "# Source this file after editing placeholder paths, then rerun resource checks.",
    ]
    for item in plan.get("resources", []):
        env = item.get("env")
        if not env:
            continue
        name = env["name"]
        value = env.get("value")
        if value:
            env_lines.append(f"export {name}={json.dumps(value)}")
        else:
            env_lines.append(f"# export {name}=/path/to/{item['bundle']}")
    (outdir / "resource_env.sh").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    missing_lines = [
        "# NGS Resource Readiness",
        "",
        f"Pipeline: `{plan.get('pipeline')}`",
        f"Ready: `{str(plan.get('ok')).lower()}`",
        "",
    ]
    for item in plan.get("missing_required", []):
        missing_lines.append(f"## Missing {item['kind']} `{item['bundle']}`")
        missing_lines.append("")
        missing_lines.append(f"Root: `{item.get('root') or 'not configured'}`")
        if item.get("error"):
            missing_lines.append(f"Error: {item['error']}")
        for missing in item.get("missing", []):
            missing_lines.append(f"- `{missing}`")
        missing_lines.append("")
    if not plan.get("missing_required"):
        missing_lines.append("All required bundles are present.")
    (outdir / "resource_readiness.md").write_text(
        "\n".join(missing_lines).rstrip() + "\n", encoding="utf-8"
    )
    setup_outputs = write_resource_setup_plan_outputs(setup_plan_from_resource_plan(plan), outdir)
    return {
        "resource_plan": str(outdir / "resource_plan.json"),
        "resource_manifest": str(outdir / "resource_manifest.tsv"),
        "resource_env": str(outdir / "resource_env.sh"),
        "resource_readiness": str(outdir / "resource_readiness.md"),
        **setup_outputs,
    }


def check_all_bundles(
    *,
    kind: str = "all",
    bundle_roots: dict[str, Path] | None = None,
    include_checksums: bool = False,
    registries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registries = registries or load_registries()
    bundle_roots = bundle_roots or {}
    checks = []
    if kind in {"all", "reference"}:
        for name in sorted(registries.get("references", {})):
            checks.append(
                check_named_bundle(
                    name,
                    kind="reference",
                    root=bundle_roots.get(name),
                    include_checksums=include_checksums,
                    registries=registries,
                )
            )
    if kind in {"all", "database"}:
        for name in sorted(registries.get("databases", {})):
            checks.append(
                check_named_bundle(
                    name,
                    kind="database",
                    root=bundle_roots.get(name),
                    include_checksums=include_checksums,
                    registries=registries,
                )
            )
    missing = [item for item in checks if not item.get("ok")]
    return {
        "created_at": now_iso(),
        "kind": kind,
        "ok": not missing,
        "checked_count": len(checks),
        "ready_count": len(checks) - len(missing),
        "missing_count": len(missing),
        "checks": checks,
    }


def pipeline_usage_by_bundle(registries: dict[str, Any]) -> dict[str, dict[str, list[str]]]:
    usage: dict[str, dict[str, set[str]]] = {}
    all_bundles = set(registries.get("references", {})) | set(registries.get("databases", {}))
    for bundle in all_bundles:
        usage[bundle] = {"required": set(), "optional": set()}
    reference_bundles = set(registries.get("references", {}))
    for pipeline, requirements in PIPELINE_RESOURCE_REQUIREMENTS.items():
        for requirement in requirements:
            slot = "required" if requirement.get("required", True) else "optional"
            if requirement.get("bundle"):
                usage.setdefault(
                    str(requirement["bundle"]), {"required": set(), "optional": set()}
                )[slot].add(pipeline)
            elif requirement.get("selector") == "genome_core":
                for bundle in reference_bundles:
                    usage.setdefault(bundle, {"required": set(), "optional": set()})[slot].add(
                        f"{pipeline}:genome_core"
                    )
    return {
        bundle: {
            "required": sorted(values["required"]),
            "optional": sorted(values["optional"]),
        }
        for bundle, values in sorted(usage.items())
    }


def iter_bundle_payloads(registries: dict[str, Any], kind: str = "all"):
    if kind in {"all", "reference"}:
        for name, payload in sorted(registries.get("references", {}).items()):
            yield "reference", name, payload
    if kind in {"all", "database"}:
        for name, payload in sorted(registries.get("databases", {}).items()):
            yield "database", name, payload


def inventory_resources(
    *,
    kind: str = "all",
    bundle_roots: dict[str, Path] | None = None,
    include_checksums: bool = False,
    registries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registries = registries or load_registries()
    bundle_roots = bundle_roots or {}
    usage = pipeline_usage_by_bundle(registries)
    bundles: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for item_kind, name, payload in iter_bundle_payloads(registries, kind=kind):
        check = check_named_bundle(
            name,
            kind=item_kind,
            root=bundle_roots.get(name),
            include_checksums=include_checksums,
            registries=registries,
        )
        bundle_usage = usage.get(name, {"required": [], "optional": []})
        missing = check.get("missing", [])
        env = env_assignment(payload, check.get("root"))
        configured_root = str(bundle_roots[name]) if name in bundle_roots else check.get("root")
        record = {
            "kind": item_kind,
            "bundle": name,
            "display_name": payload.get("display_name", name),
            "ok": bool(check.get("ok")),
            "root": configured_root,
            "root_env": payload.get("root_env"),
            "env": env,
            "required_file_count": len(payload.get("required_files", [])),
            "missing_count": len(missing),
            "missing": missing,
            "estimated_size": payload.get("estimated_size"),
            "source": payload.get("source"),
            "license_note": payload.get("license_note"),
            "suggested_setup": payload.get("suggested_setup", []),
            "pipelines_required": bundle_usage.get("required", []),
            "pipelines_optional": bundle_usage.get("optional", []),
            "check": check,
        }
        bundles.append(record)
        rows.append(
            {
                "kind": item_kind,
                "bundle": name,
                "display_name": record["display_name"],
                "ok": str(record["ok"]).lower(),
                "root": record["root"] or "",
                "root_env": record["root_env"] or "",
                "required_file_count": record["required_file_count"],
                "missing_count": record["missing_count"],
                "missing_files": ";".join(missing),
                "pipelines_required": ";".join(record["pipelines_required"]),
                "pipelines_optional": ";".join(record["pipelines_optional"]),
                "estimated_size": record["estimated_size"] or "",
                "source": record["source"] or "",
                "license_note": record["license_note"] or "",
            }
        )
    missing_bundles = [item for item in bundles if not item["ok"]]
    return {
        "created_at": now_iso(),
        "kind": kind,
        "ok": not missing_bundles,
        "bundle_count": len(bundles),
        "ready_count": len(bundles) - len(missing_bundles),
        "missing_count": len(missing_bundles),
        "bundles": bundles,
        "rows": rows,
    }


def inventory_manifest_rows(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    return list(inventory.get("rows", []))


def write_resource_inventory_outputs(inventory: dict[str, Any], outdir: Path) -> dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir / "resource_inventory.json", inventory)
    fieldnames = [
        "kind",
        "bundle",
        "display_name",
        "ok",
        "root",
        "root_env",
        "required_file_count",
        "missing_count",
        "missing_files",
        "pipelines_required",
        "pipelines_optional",
        "estimated_size",
        "source",
        "license_note",
    ]
    write_tsv(outdir / "resource_inventory.tsv", inventory_manifest_rows(inventory), fieldnames)
    env_lines = [
        "#!/usr/bin/env bash",
        "# Source this file after editing placeholder paths, then rerun ngs_reference_manager.py inventory.",
    ]
    for item in inventory.get("bundles", []):
        env = item.get("env")
        root_env = item.get("root_env")
        if env and env.get("value"):
            env_lines.append(f"export {env['name']}={json.dumps(env['value'])}")
        elif root_env:
            env_lines.append(f"# export {root_env}=/path/to/{item['bundle']}")
    (outdir / "resource_env.sh").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    write_resource_dashboard(inventory, outdir / "resource_dashboard.md")
    return {
        "resource_inventory": str(outdir / "resource_inventory.json"),
        "resource_inventory_tsv": str(outdir / "resource_inventory.tsv"),
        "resource_env": str(outdir / "resource_env.sh"),
        "resource_dashboard": str(outdir / "resource_dashboard.md"),
    }


def write_resource_dashboard(inventory: dict[str, Any], path: Path) -> None:
    lines = [
        "# NGS Resource Inventory",
        "",
        f"Created: `{inventory.get('created_at')}`",
        f"Ready bundles: `{inventory.get('ready_count')}/{inventory.get('bundle_count')}`",
        f"All ready: `{str(inventory.get('ok')).lower()}`",
        "",
        "## Bundle Readiness",
        "",
        "| Kind | Bundle | Display Name | Ready | Root | Missing | Required By | Optional For |",
        "|---|---|---|---:|---|---:|---|---|",
    ]
    for item in inventory.get("bundles", []):
        lines.append(
            "| {kind} | `{bundle}` | {display_name} | `{ok}` | `{root}` | {missing_count} | {required} | {optional} |".format(
                kind=item.get("kind", ""),
                bundle=item.get("bundle", ""),
                display_name=item.get("display_name", ""),
                ok=str(item.get("ok", False)).lower(),
                root=item.get("root") or "not configured",
                missing_count=item.get("missing_count", 0),
                required=", ".join(item.get("pipelines_required", [])) or "",
                optional=", ".join(item.get("pipelines_optional", [])) or "",
            )
        )
    missing_items = [item for item in inventory.get("bundles", []) if not item.get("ok")]
    if missing_items:
        lines.extend(["", "## Missing Bundle Details", ""])
        for item in missing_items:
            lines.extend(
                [
                    f"### `{item.get('bundle')}`",
                    "",
                    f"Root: `{item.get('root') or 'not configured'}`",
                    f"Env var: `{item.get('root_env') or 'none'}`",
                ]
            )
            missing = item.get("missing", [])
            if missing:
                lines.append("Missing files:")
                lines.extend(f"- `{entry}`" for entry in missing)
            else:
                lines.append("Missing files: root not configured or bundle contract unavailable.")
            if item.get("license_note"):
                lines.append(f"License/source note: {item['license_note']}")
            setup = item.get("suggested_setup", [])
            if setup:
                lines.extend(["", "Suggested setup:", "", "```bash"])
                lines.extend(str(command) for command in setup)
                lines.append("```")
            lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def resource_lock_from_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    bundles: list[dict[str, Any]] = []
    for item in inventory.get("bundles", []):
        check = item.get("check", {})
        bundles.append(
            {
                "kind": item.get("kind"),
                "bundle": item.get("bundle"),
                "display_name": item.get("display_name"),
                "ok": bool(item.get("ok")),
                "root": item.get("root"),
                "root_env": item.get("root_env"),
                "required_file_count": item.get("required_file_count", 0),
                "missing": list(item.get("missing", [])),
                "files": list(check.get("files", [])),
                "metadata": check.get("metadata", {}),
                "source": item.get("source"),
                "license_note": item.get("license_note"),
                "estimated_size": item.get("estimated_size"),
                "pipelines_required": list(item.get("pipelines_required", [])),
                "pipelines_optional": list(item.get("pipelines_optional", [])),
            }
        )
    return {
        "schema_version": "ngs_resource_lock/v0.1",
        "created_at": now_iso(),
        "inventory_created_at": inventory.get("created_at"),
        "kind": inventory.get("kind", "all"),
        "ok": bool(inventory.get("ok")),
        "bundle_count": inventory.get("bundle_count", len(bundles)),
        "ready_count": inventory.get("ready_count", sum(1 for item in bundles if item.get("ok"))),
        "missing_count": inventory.get(
            "missing_count", sum(1 for item in bundles if not item.get("ok"))
        ),
        "bundles": bundles,
    }


def resource_lock_rows(lock: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bundle in lock.get("bundles", []):
        for file_record in bundle.get("files", []):
            rows.append(
                {
                    "kind": bundle.get("kind", ""),
                    "bundle": bundle.get("bundle", ""),
                    "display_name": bundle.get("display_name", ""),
                    "bundle_ok": str(bundle.get("ok", False)).lower(),
                    "root": bundle.get("root") or "",
                    "path": file_record.get("path", ""),
                    "resolved_path": file_record.get("resolved_path") or "",
                    "exists": str(file_record.get("exists", False)).lower(),
                    "bytes": file_record.get("bytes") or "",
                    "sha256": file_record.get("sha256") or "",
                    "sha256_skipped_reason": file_record.get("sha256_skipped_reason") or "",
                    "pipelines_required": ";".join(bundle.get("pipelines_required", [])),
                    "pipelines_optional": ";".join(bundle.get("pipelines_optional", [])),
                }
            )
    return rows


def write_resource_lock_outputs(lock: dict[str, Any], outdir: Path) -> dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir / "resource_lock.json", lock)
    fieldnames = [
        "kind",
        "bundle",
        "display_name",
        "bundle_ok",
        "root",
        "path",
        "resolved_path",
        "exists",
        "bytes",
        "sha256",
        "sha256_skipped_reason",
        "pipelines_required",
        "pipelines_optional",
    ]
    write_tsv(outdir / "resource_lock.tsv", resource_lock_rows(lock), fieldnames)
    write_resource_lock_summary(lock, outdir / "resource_lock.md")
    return {
        "resource_lock": str(outdir / "resource_lock.json"),
        "resource_lock_tsv": str(outdir / "resource_lock.tsv"),
        "resource_lock_summary": str(outdir / "resource_lock.md"),
    }


def write_resource_lock_summary(lock: dict[str, Any], path: Path) -> None:
    lines = [
        "# NGS Resource Lockfile",
        "",
        f"Created: `{lock.get('created_at')}`",
        f"Schema: `{lock.get('schema_version')}`",
        f"Ready bundles: `{lock.get('ready_count')}/{lock.get('bundle_count')}`",
        f"All ready at lock time: `{str(lock.get('ok')).lower()}`",
        "",
        "| Kind | Bundle | Ready | Root | Files | Missing | Checksummed |",
        "|---|---|---:|---|---:|---:|---:|",
    ]
    for bundle in lock.get("bundles", []):
        files = bundle.get("files", [])
        checksummed = sum(1 for item in files if item.get("sha256"))
        missing = len(bundle.get("missing", []))
        lines.append(
            "| {kind} | `{bundle}` | `{ok}` | `{root}` | {files} | {missing} | {checksummed} |".format(
                kind=bundle.get("kind", ""),
                bundle=bundle.get("bundle", ""),
                ok=str(bundle.get("ok", False)).lower(),
                root=bundle.get("root") or "not configured",
                files=len(files),
                missing=missing,
                checksummed=checksummed,
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def locked_file_path(
    bundle: dict[str, Any], file_record: dict[str, Any], bundle_roots: dict[str, Path]
) -> Path | None:
    bundle_name = str(bundle.get("bundle") or "")
    if bundle_name in bundle_roots:
        return (bundle_roots[bundle_name] / str(file_record.get("path", ""))).expanduser().resolve()
    resolved = file_record.get("resolved_path")
    if resolved:
        return Path(str(resolved)).expanduser().resolve()
    root = bundle.get("root")
    if root:
        return (Path(str(root)).expanduser() / str(file_record.get("path", ""))).resolve()
    return None


def verify_resource_lock(
    lock: dict[str, Any],
    *,
    bundle_roots: dict[str, Path] | None = None,
    verify_checksums: bool = True,
) -> dict[str, Any]:
    bundle_roots = bundle_roots or {}
    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    for bundle in lock.get("bundles", []):
        bundle_name = str(bundle.get("bundle") or "")
        for file_record in bundle.get("files", []):
            path = locked_file_path(bundle, file_record, bundle_roots)
            current_exists = bool(path and path.exists())
            expected_exists = bool(file_record.get("exists"))
            current_bytes = (
                path.stat().st_size if current_exists and path and path.is_file() else None
            )
            expected_bytes = file_record.get("bytes")
            current_sha = None
            expected_sha = file_record.get("sha256")
            status = "matched"
            issue = ""
            if expected_exists and not current_exists:
                status = "mismatch"
                issue = "missing_now"
            elif not expected_exists and current_exists:
                status = "mismatch"
                issue = "was_missing_now_present"
            elif (
                expected_exists
                and current_exists
                and expected_bytes is not None
                and current_bytes != expected_bytes
            ):
                status = "mismatch"
                issue = "bytes_changed"
            elif (
                expected_exists
                and current_exists
                and expected_sha
                and verify_checksums
                and path
                and path.is_file()
            ):
                current_sha = sha256_file(path)
                if current_sha != expected_sha:
                    status = "mismatch"
                    issue = "sha256_changed"
            row = {
                "bundle": bundle_name,
                "kind": bundle.get("kind", ""),
                "path": file_record.get("path", ""),
                "resolved_path": str(path) if path else "",
                "expected_exists": str(expected_exists).lower(),
                "current_exists": str(current_exists).lower(),
                "expected_bytes": expected_bytes if expected_bytes is not None else "",
                "current_bytes": current_bytes if current_bytes is not None else "",
                "expected_sha256": expected_sha or "",
                "current_sha256": current_sha or "",
                "status": status,
                "issue": issue,
            }
            rows.append(row)
            if status != "matched":
                mismatches.append(row)
    original_ok = bool(lock.get("ok"))
    return {
        "created_at": now_iso(),
        "schema_version": "ngs_resource_lock_verification/v0.1",
        "lock_created_at": lock.get("created_at"),
        "lock_schema_version": lock.get("schema_version"),
        "original_lock_ok": original_ok,
        "ok": original_ok and not mismatches,
        "verified_file_count": len(rows),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "rows": rows,
    }


def write_resource_lock_verification_outputs(
    verification: dict[str, Any], outdir: Path
) -> dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir / "resource_lock_verification.json", verification)
    fieldnames = [
        "bundle",
        "kind",
        "path",
        "resolved_path",
        "expected_exists",
        "current_exists",
        "expected_bytes",
        "current_bytes",
        "expected_sha256",
        "current_sha256",
        "status",
        "issue",
    ]
    write_tsv(
        outdir / "resource_lock_verification.tsv", list(verification.get("rows", [])), fieldnames
    )
    write_resource_lock_verification_summary(verification, outdir / "resource_lock_verification.md")
    return {
        "resource_lock_verification": str(outdir / "resource_lock_verification.json"),
        "resource_lock_verification_tsv": str(outdir / "resource_lock_verification.tsv"),
        "resource_lock_verification_summary": str(outdir / "resource_lock_verification.md"),
    }


def write_resource_lock_verification_summary(verification: dict[str, Any], path: Path) -> None:
    lines = [
        "# NGS Resource Lock Verification",
        "",
        f"Created: `{verification.get('created_at')}`",
        f"Lock created: `{verification.get('lock_created_at')}`",
        f"Original lock ready: `{str(verification.get('original_lock_ok')).lower()}`",
        f"Verification ready: `{str(verification.get('ok')).lower()}`",
        f"Files checked: `{verification.get('verified_file_count')}`",
        f"Mismatches: `{verification.get('mismatch_count')}`",
        "",
    ]
    if verification.get("mismatches"):
        lines.extend(
            ["## Mismatches", "", "| Bundle | Path | Issue | Current Path |", "|---|---|---|---|"]
        )
        for item in verification["mismatches"]:
            lines.append(
                f"| `{item.get('bundle')}` | `{item.get('path')}` | `{item.get('issue')}` | `{item.get('resolved_path')}` |"
            )
    else:
        lines.append("All locked files match the lockfile state.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def list_bundles(registries: dict[str, Any]) -> dict[str, Any]:
    return {
        "created_at": now_iso(),
        "references": {
            name: {
                "display_name": payload.get("display_name", name),
                "genome_build": payload.get("genome_build"),
                "root": payload.get("root") or f"${payload.get('root_env')}"
                if payload.get("root_env")
                else payload.get("root"),
                "required_files": payload.get("required_files", []),
            }
            for name, payload in sorted(registries.get("references", {}).items())
        },
        "databases": {
            name: {
                "display_name": payload.get("display_name", name),
                "database_family": payload.get("database_family"),
                "version": payload.get("version"),
                "root": payload.get("root") or f"${payload.get('root_env')}"
                if payload.get("root_env")
                else payload.get("root"),
                "required_files": payload.get("required_files", []),
            }
            for name, payload in sorted(registries.get("databases", {}).items())
        },
    }


def explain_missing(check: dict[str, Any]) -> str:
    if check.get("ok"):
        return f"{check['bundle']} is present under {check.get('root')}."
    lines = [
        f"{check.get('bundle')} is not ready.",
        f"Root: {check.get('root') or 'not configured'}",
    ]
    if check.get("error"):
        lines.append(f"Error: {check['error']}")
    if check.get("missing"):
        lines.append("Missing files:")
        lines.extend(f"- {item}" for item in check["missing"])
    license_note = check.get("metadata", {}).get("license_note")
    if license_note:
        lines.append(f"License/source note: {license_note}")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-registry", type=Path, default=DEFAULT_REFERENCE_REGISTRY)
    parser.add_argument("--database-registry", type=Path, default=DEFAULT_DATABASE_REGISTRY)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List known reference and database bundle contracts.")

    check = sub.add_parser("check", help="Check one named bundle.")
    check.add_argument("--kind", choices=["reference", "database"], required=True)
    check.add_argument("--bundle", required=True)
    check.add_argument("--root", type=Path)
    check.add_argument("--include-checksums", action="store_true")
    check.add_argument("--output", type=Path)

    explain = sub.add_parser(
        "explain-missing", help="Print a human-readable missing-resource explanation."
    )
    explain.add_argument("--kind", choices=["reference", "database"], required=True)
    explain.add_argument("--bundle", required=True)
    explain.add_argument("--root", type=Path)

    plan = sub.add_parser("plan", help="Create a pipeline-aware reference/database readiness plan.")
    plan.add_argument("--pipeline", required=True)
    plan.add_argument(
        "--genome-build",
        help="Genome build or alias for genome-backed pipelines, e.g. GRCh38, hg38, GRCm39, mm39, or a configured local alias.",
    )
    plan.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Override a bundle root as bundle=/path. May be repeated.",
    )
    plan.add_argument(
        "--include-optional",
        action="store_true",
        help="Include optional databases such as Bracken/HUMAnN or alternate taxonomy bundles.",
    )
    plan.add_argument("--include-checksums", action="store_true")
    plan.add_argument(
        "--outdir",
        type=Path,
        help="Write resource_plan.json, resource_manifest.tsv, resource_env.sh, resource_readiness.md, and setup-plan artifacts.",
    )

    setup_plan = sub.add_parser(
        "setup-plan", help="Create an actionable setup checklist for missing pipeline resources."
    )
    setup_plan.add_argument("--pipeline", required=True)
    setup_plan.add_argument(
        "--genome-build",
        help="Genome build or alias for genome-backed pipelines, e.g. GRCh38, hg38, GRCm39, mm39, or a configured local alias.",
    )
    setup_plan.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Override a bundle root as bundle=/path. May be repeated.",
    )
    setup_plan.add_argument(
        "--include-optional",
        action="store_true",
        help="Include optional databases such as Bracken/HUMAnN or alternate taxonomy bundles.",
    )
    setup_plan.add_argument("--include-checksums", action="store_true")
    setup_plan.add_argument(
        "--include-ready",
        action="store_true",
        help="Include already-ready bundles in the setup plan for documentation.",
    )
    setup_plan.add_argument(
        "--outdir",
        type=Path,
        required=True,
        help="Write resource_setup_plan.json, .tsv, .md, and resource_setup_commands.sh.",
    )
    setup_plan.add_argument(
        "--fail-on-blocking",
        action="store_true",
        help="Exit non-zero when required resources need setup.",
    )

    check_all = sub.add_parser("check-all", help="Check every known bundle contract.")
    check_all.add_argument("--kind", choices=["all", "reference", "database"], default="all")
    check_all.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Override a bundle root as bundle=/path. May be repeated.",
    )
    check_all.add_argument("--include-checksums", action="store_true")
    check_all.add_argument("--output", type=Path)

    inventory = sub.add_parser(
        "inventory", help="Write a project-level reference/database inventory dashboard."
    )
    inventory.add_argument("--kind", choices=["all", "reference", "database"], default="all")
    inventory.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Override a bundle root as bundle=/path. May be repeated.",
    )
    inventory.add_argument("--include-checksums", action="store_true")
    inventory.add_argument(
        "--outdir",
        type=Path,
        help="Write resource_inventory.json, resource_inventory.tsv, resource_env.sh, and resource_dashboard.md.",
    )
    inventory.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit non-zero when any inventoried bundle is incomplete.",
    )

    lock = sub.add_parser(
        "lock", help="Create a reproducible resource lockfile from the current inventory."
    )
    lock.add_argument("--kind", choices=["all", "reference", "database"], default="all")
    lock.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Override a bundle root as bundle=/path. May be repeated.",
    )
    lock.add_argument(
        "--include-checksums",
        action="store_true",
        help="Record SHA256 checksums for files below the checksum threshold.",
    )
    lock.add_argument(
        "--outdir",
        type=Path,
        required=True,
        help="Write resource_lock.json, resource_lock.tsv, and resource_lock.md.",
    )
    lock.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit non-zero when the lock captures incomplete bundles.",
    )

    verify_lock = sub.add_parser(
        "verify-lock", help="Verify a resource lockfile against the current filesystem."
    )
    verify_lock.add_argument("--lockfile", type=Path, required=True)
    verify_lock.add_argument(
        "--bundle-root",
        action="append",
        default=[],
        help="Override a locked bundle root as bundle=/path. May be repeated.",
    )
    verify_lock.add_argument(
        "--skip-checksums",
        action="store_true",
        help="Skip SHA256 comparison even when the lockfile contains checksums.",
    )
    verify_lock.add_argument(
        "--outdir", type=Path, help="Write resource_lock_verification.json, .tsv, and .md."
    )
    verify_lock.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit non-zero when the lock is incomplete or files no longer match.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registries = load_registries(args.reference_registry, args.database_registry)
    if args.command == "list":
        print(json.dumps(list_bundles(registries), indent=2, sort_keys=True))
        return 0
    if args.command == "check":
        result = check_named_bundle(
            args.bundle,
            kind=args.kind,
            root=args.root,
            include_checksums=args.include_checksums,
            registries=registries,
        )
        if args.output:
            write_json(args.output, result)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("ok") else 1
    if args.command == "explain-missing":
        result = check_named_bundle(
            args.bundle, kind=args.kind, root=args.root, registries=registries
        )
        print(explain_missing(result), end="")
        return 0 if result.get("ok") else 1
    if args.command == "plan":
        result = plan_pipeline_resources(
            args.pipeline,
            genome_build=args.genome_build,
            bundle_roots=parse_bundle_roots(args.bundle_root),
            include_optional=args.include_optional,
            include_checksums=args.include_checksums,
            registries=registries,
        )
        if args.outdir:
            result["outputs"] = write_resource_plan_outputs(
                result, args.outdir.expanduser().resolve()
            )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("ok") else 1
    if args.command == "setup-plan":
        resource_plan = plan_pipeline_resources(
            args.pipeline,
            genome_build=args.genome_build,
            bundle_roots=parse_bundle_roots(args.bundle_root),
            include_optional=args.include_optional,
            include_checksums=args.include_checksums,
            registries=registries,
        )
        result = setup_plan_from_resource_plan(resource_plan, include_ready=args.include_ready)
        result["resource_plan"] = resource_plan
        result["outputs"] = write_resource_setup_plan_outputs(
            result, args.outdir.expanduser().resolve()
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if args.fail_on_blocking and result.get("blocking_count") else 0
    if args.command == "check-all":
        result = check_all_bundles(
            kind=args.kind,
            bundle_roots=parse_bundle_roots(args.bundle_root),
            include_checksums=args.include_checksums,
            registries=registries,
        )
        if args.output:
            write_json(args.output, result)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("ok") else 1
    if args.command == "inventory":
        result = inventory_resources(
            kind=args.kind,
            bundle_roots=parse_bundle_roots(args.bundle_root),
            include_checksums=args.include_checksums,
            registries=registries,
        )
        if args.outdir:
            result["outputs"] = write_resource_inventory_outputs(
                result, args.outdir.expanduser().resolve()
            )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if args.fail_on_missing and not result.get("ok") else 0
    if args.command == "lock":
        inventory = inventory_resources(
            kind=args.kind,
            bundle_roots=parse_bundle_roots(args.bundle_root),
            include_checksums=args.include_checksums,
            registries=registries,
        )
        result = resource_lock_from_inventory(inventory)
        result["outputs"] = write_resource_lock_outputs(result, args.outdir.expanduser().resolve())
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if args.fail_on_missing and not result.get("ok") else 0
    if args.command == "verify-lock":
        lock_payload = read_json(args.lockfile.expanduser().resolve())
        result = verify_resource_lock(
            lock_payload,
            bundle_roots=parse_bundle_roots(args.bundle_root),
            verify_checksums=not args.skip_checksums,
        )
        if args.outdir:
            result["outputs"] = write_resource_lock_verification_outputs(
                result, args.outdir.expanduser().resolve()
            )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if args.fail_on_mismatch and not result.get("ok") else 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
