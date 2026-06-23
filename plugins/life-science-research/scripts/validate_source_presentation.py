#!/usr/bin/env python3
"""Validate source-link coverage and provenance contracts for this plugin."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from urllib.parse import urlsplit

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = PLUGIN_ROOT / "skills"
REGISTRY_PATH = PLUGIN_ROOT / "references" / "source-links.json"
CONTRACT_PATH = PLUGIN_ROOT / "references" / "source-presentation.md"
CONTRACT_MARKER = "<!-- source-presentation-contract:v2 -->"


def _is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parts = urlsplit(value)
    return parts.scheme == "https" and bool(parts.netloc)


def validate() -> list[str]:
    errors: list[str] = []
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read source registry: {exc}"]

    try:
        contract_text = CONTRACT_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"Could not read source presentation contract: {exc}")
        contract_text = ""

    contract_normalized = " ".join(contract_text.split())
    for required_phrase in (
        "every substantive externally sourced claim should remain traceable",
        "Connectivity or schema check",
        "Empty result or failed request",
        "Router or planner",
        "Local synthesis or derived analysis",
        "queried but returned no relevant evidence",
    ):
        if required_phrase not in contract_normalized:
            errors.append(f"source-presentation.md: missing rule: {required_phrase}")

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    skill_names = {path.name for path in skill_dirs}
    registry_skills = registry.get("skills")
    if not isinstance(registry_skills, dict):
        return errors + ["source-links.json must contain a `skills` object"]

    registry_names = set(registry_skills)
    for missing in sorted(skill_names - registry_names):
        errors.append(f"Registry is missing skill: {missing}")
    for unknown in sorted(registry_names - skill_names):
        errors.append(f"Registry contains unknown skill: {unknown}")

    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        skill_path = skill_dir / "SKILL.md"
        try:
            skill_text = skill_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"Could not read {skill_path}: {exc}")
            continue

        if CONTRACT_MARKER not in skill_text:
            errors.append(f"{skill_name}: missing source presentation marker")
        for required_phrase in (
            "only for substantive external claims supported by the response",
            "Do not force evidence links for connectivity or schema checks",
        ):
            if required_phrase not in skill_text:
                errors.append(
                    f"{skill_name}: missing conditional rule: {required_phrase}"
                )
        expected_registry_line = (
            f"Use the `{skill_name}` entry in `../../references/source-links.json`"
        )
        if expected_registry_line not in skill_text:
            errors.append(f"{skill_name}: missing or incorrect registry key")

        entry = registry_skills.get(skill_name)
        if not isinstance(entry, dict):
            continue
        if (
            not isinstance(entry.get("source_name"), str)
            or not entry["source_name"].strip()
        ):
            errors.append(f"{skill_name}: source_name must be a non-empty string")
        homepage = entry.get("homepage_url")
        if homepage is not None and not _is_https_url(homepage):
            errors.append(f"{skill_name}: homepage_url must be HTTPS or null")
        templates = entry.get("record_url_templates")
        if not isinstance(templates, list):
            errors.append(f"{skill_name}: record_url_templates must be a list")
        else:
            for index, template_entry in enumerate(templates):
                if not isinstance(template_entry, dict):
                    errors.append(f"{skill_name}: template {index} must be an object")
                    continue
                identifier_type = template_entry.get("identifier_type")
                template = template_entry.get("template")
                if not isinstance(identifier_type, str) or not identifier_type.strip():
                    errors.append(
                        f"{skill_name}: template {index} lacks identifier_type"
                    )
                if not _is_https_url(template) or "{id}" not in str(template):
                    errors.append(
                        f"{skill_name}: template {index} must be HTTPS and contain {{id}}"
                    )
                transform = template_entry.get("transform")
                if transform is not None and (
                    not isinstance(transform, str) or not transform.strip()
                ):
                    errors.append(
                        f"{skill_name}: template {index} transform must be a non-empty string"
                    )

        scripts_dir = skill_dir / "scripts"
        if scripts_dir.is_dir():
            script_files = sorted(scripts_dir.glob("*.py"))
            runtime_files = [
                path for path in script_files if not path.name.startswith("test_")
            ]
            combined_runtime_text = "\n".join(
                path.read_text(encoding="utf-8") for path in runtime_files
            )
            if (
                '"sources"' not in combined_runtime_text
                and "_attach_sources" not in combined_runtime_text
            ):
                errors.append(f"{skill_name}: script outputs lack provenance support")
            if "def _sanitize_request_url" in combined_runtime_text:
                for required_phrase in (
                    'parts.netloc.rsplit("@", 1)[-1]',
                    'urlencode(query), ""',
                    '"credential"',
                    '"sig"',
                ):
                    if required_phrase not in combined_runtime_text:
                        errors.append(
                            f"{skill_name}: URL sanitizer missing: {required_phrase}"
                        )
            for script_path in script_files:
                try:
                    ast.parse(
                        script_path.read_text(encoding="utf-8"),
                        filename=str(script_path),
                    )
                except (OSError, SyntaxError) as exc:
                    errors.append(
                        f"{skill_name}: invalid Python in {script_path.name}: {exc}"
                    )

    router_text = (SKILLS_DIR / "research-router-skill" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    router_normalized = " ".join(router_text.split())
    for required_phrase in (
        "retain the downstream skill's `sources` entries",
        "Do not seed the router with example citations",
        "only performs a connectivity or schema check, returns no evidence, or fails",
        "supplements rather than replaces applicable claim-adjacent links",
        "the structured `sources` entries returned by those skills",
    ):
        if required_phrase not in router_normalized:
            errors.append(f"research-router-skill: missing rule: {required_phrase}")

    mapper_text = (SKILLS_DIR / "locus-to-gene-mapper-skill" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    mapper_normalized = " ".join(mapper_text.split())
    for required_phrase in (
        "Distinguish evidence-contributing sources",
        "queried sources that returned no mapping evidence",
        "queried-but-empty sources in methods, provenance, or limitations",
    ):
        if required_phrase not in mapper_normalized:
            errors.append(
                f"locus-to-gene-mapper-skill: missing rule: {required_phrase}"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1
    skill_count = len([path for path in SKILLS_DIR.iterdir() if path.is_dir()])
    script_skill_count = len(
        [path for path in SKILLS_DIR.iterdir() if (path / "scripts").is_dir()]
    )
    print(
        f"Source presentation validation passed: {skill_count} skills, "
        f"{script_skill_count} script-backed skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
