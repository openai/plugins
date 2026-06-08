#!/usr/bin/env python3
"""Shared reference/database readiness gates for NGS run envelopes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import ngs_reference_manager
from ngs_visualization_utils import artifact_entry


def relative_outputs(outputs: dict[str, str], run_dir: Path) -> dict[str, str]:
    run_root = run_dir.resolve()
    return {key: str(Path(value).resolve().relative_to(run_root)) for key, value in outputs.items()}


def write_pipeline_resource_plan(
    *,
    run_dir: Path,
    pipeline: str,
    genome_build: str | None = None,
    bundle_roots: list[str] | None = None,
    include_optional: bool = False,
    include_checksums: bool = False,
    skip: bool = False,
    required: bool = False,
) -> dict[str, Any] | None:
    if skip:
        return None
    plan = ngs_reference_manager.plan_pipeline_resources(
        pipeline,
        genome_build=genome_build,
        bundle_roots=ngs_reference_manager.parse_bundle_roots(bundle_roots or []),
        include_optional=include_optional,
        include_checksums=include_checksums,
    )
    plan["gate_mode"] = "required" if required else "advisory"
    plan["blocking_for_run"] = bool(required and not plan.get("ok"))
    outputs = ngs_reference_manager.write_resource_plan_outputs(
        plan, run_dir.resolve() / "resources"
    )
    plan["outputs"] = relative_outputs(outputs, run_dir)
    return plan


def resource_messages(resource_plan: dict[str, Any] | None) -> list[str]:
    if resource_plan is None or resource_plan.get("ok"):
        return []
    messages = []
    for item in resource_plan.get("missing_required", []):
        detail = item.get("error") or ", ".join(item.get("missing", [])) or "root not configured"
        messages.append(
            f"required {item.get('kind')} bundle `{item.get('bundle')}` is not ready: {detail}"
        )
    return messages


def merge_resource_status(
    validation: dict[str, Any],
    resource_plan: dict[str, Any] | None,
    *,
    required: bool = False,
) -> dict[str, Any]:
    merged = dict(validation)
    errors = list(merged.get("errors", []))
    warnings = list(merged.get("warnings", []))
    if resource_plan is None:
        merged["resource_plan_ok"] = None
        merged["resource_plan_skipped"] = True
        warnings.append(
            "resource readiness plan was skipped; reference/database bundle contents were not checked"
        )
    else:
        messages = resource_messages(resource_plan)
        merged["resource_plan_ok"] = bool(resource_plan.get("ok"))
        merged["resource_plan_skipped"] = False
        merged["resource_plan_mode"] = resource_plan.get(
            "gate_mode", "required" if required else "advisory"
        )
        merged["resource_plan_path"] = resource_plan.get("outputs", {}).get("resource_plan")
        merged["missing_required_resources"] = resource_plan.get("missing_required", [])
        if messages and required:
            errors.extend(messages)
        elif messages:
            warnings.extend([f"advisory resource check: {message}" for message in messages])
    merged["errors"] = errors
    merged["warnings"] = warnings
    merged["ok"] = bool(validation.get("ok")) and (
        resource_plan is None or not required or bool(resource_plan.get("ok"))
    )
    return merged


def resource_output_paths(resource_plan: dict[str, Any] | None) -> dict[str, str]:
    return resource_plan.get("outputs", {}) if resource_plan else {}


def resource_visual_entries(resource_plan: dict[str, Any] | None) -> list[dict[str, Any]]:
    if resource_plan is None:
        return []
    return [
        artifact_entry(
            artifact_id="resource_readiness",
            title="Resource Readiness",
            path="resources/resource_readiness.md",
            kind="markdown",
            status="created",
            description="Human-readable reference/database readiness gate for this run.",
        ),
        artifact_entry(
            artifact_id="resource_manifest",
            title="Resource Manifest",
            path="resources/resource_manifest.tsv",
            kind="table",
            status="created",
            description="Resolved resource bundles, roots, env vars, and missing-file counts.",
        ),
        artifact_entry(
            artifact_id="resource_plan",
            title="Resource Plan",
            path="resources/resource_plan.json",
            kind="json",
            status="created",
            description="Structured reference/database readiness plan used by this run.",
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


def resource_summary_lines(resource_plan: dict[str, Any] | None) -> list[str]:
    if resource_plan is None:
        return []
    lines = [
        "## Resource Readiness",
        "",
        f"Mode: `{resource_plan.get('gate_mode', 'required')}`",
        f"Ready: `{str(resource_plan.get('ok')).lower()}`",
        f"Resource contract: `{resource_plan.get('pipeline')}`",
        f"Setup plan: `{resource_plan.get('outputs', {}).get('resource_setup_summary', 'resources/resource_setup_plan.md')}`",
    ]
    for item in resource_plan.get("resources", []):
        state = "ready" if item.get("ok") else "missing"
        required = "required" if item.get("required") else "optional"
        lines.append(f"- `{item.get('bundle')}` ({item.get('kind')}, {required}): {state}")
    lines.append("")
    return lines
