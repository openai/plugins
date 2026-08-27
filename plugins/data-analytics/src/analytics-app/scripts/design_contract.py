#!/usr/bin/env python3
"""Shared DESIGN.md contract checks for generated analytics app packages."""

from __future__ import annotations

import re
from pathlib import Path

from package_utils import ContractError

CANONICAL_DESIGN_SECTIONS = [
    "Overview",
    "Colors",
    "Typography",
    "Layout",
    "Elevation & Depth",
    "Shapes",
    "Components",
    "Do's and Don'ts",
]
REQUIRED_FRONTMATTER_KEYS = (
    "name",
    "description",
    "colors",
    "typography",
    "spacing",
    "rounded",
    "surfaces",
    "components",
    "implementation",
)
REQUIRED_DESIGN_TOKENS = (
    "bg/primary",
    "bg/secondary",
    "bg/tertiary",
    "border/light",
    "border/default",
    "text/primary",
    "text/secondary",
    "text/tertiary",
    "icon/accent",
    "space-12",
    "space-24",
    "corner-radius/cr-24",
    "elevation/01",
    "blue/500",
    "green/700",
    "purple/500",
)
REQUIRED_TYPE_TOKENS = (
    "System Sans Variable",
    "text/xs/normal",
    "text/xs/semibold",
    "text/sm/normal",
    "text/sm/medium",
    "heading/md/medium",
    "heading/2xl",
)
REQUIRED_SURFACE_MEASUREMENTS = (
    "1140px",
    "800px",
    "48px",
    "24px",
)
REQUIRED_COMPONENT_NAMES = (
    "top-bar",
    "metric-card",
    "report-block",
    "chart-block",
    "table-list",
    "popover-menu",
)


def split_design_file(markdown: str, path: Path) -> tuple[str, str]:
    if not markdown.startswith("---\n"):
        raise ContractError(f"{path.name} must start with YAML front matter")
    try:
        _opening, frontmatter, body = markdown.split("---\n", 2)
    except ValueError as exc:
        raise ContractError(f"{path.name} must contain closed YAML front matter") from exc
    if not frontmatter.strip():
        raise ContractError(f"{path.name} front matter must not be empty")
    if not body.strip():
        raise ContractError(f"{path.name} body must not be empty")
    return frontmatter, body


def require_frontmatter_key(frontmatter: str, key: str, path: Path) -> None:
    if not re.search(rf"^{re.escape(key)}\s*:", frontmatter, flags=re.MULTILINE):
        raise ContractError(f"{path.name} front matter must define {key}")


def require_text_anchor(markdown: str, anchor: str, path: Path, group: str) -> None:
    if anchor not in markdown:
        raise ContractError(f"{path.name} must include {group} anchor: {anchor}")


def section_positions(body: str) -> dict[str, int]:
    positions: dict[str, int] = {}
    for match in re.finditer(r"^##\s+(.+?)\s*$", body, flags=re.MULTILINE):
        title = match.group(1).strip()
        if title in CANONICAL_DESIGN_SECTIONS:
            positions[title] = match.start()
    return positions


def validate_design_contract(root: Path) -> None:
    path = root / "DESIGN.md"
    if not path.exists():
        raise ContractError("analytics app package must include DESIGN.md")

    markdown = path.read_text(encoding="utf-8")
    frontmatter, body = split_design_file(markdown, path)

    for key in REQUIRED_FRONTMATTER_KEYS:
        require_frontmatter_key(frontmatter, key, path)

    for token in REQUIRED_DESIGN_TOKENS:
        require_text_anchor(markdown, token, path, "design token")
    for token in REQUIRED_TYPE_TOKENS:
        require_text_anchor(markdown, token, path, "typography token")
    for measurement in REQUIRED_SURFACE_MEASUREMENTS:
        require_text_anchor(markdown, measurement, path, "surface measurement")
    for component in REQUIRED_COMPONENT_NAMES:
        require_text_anchor(frontmatter, component, path, "component recipe")

    positions = section_positions(body)
    missing_sections = [
        section for section in CANONICAL_DESIGN_SECTIONS if section not in positions
    ]
    if missing_sections:
        raise ContractError(f"{path.name} is missing sections: {missing_sections}")
    ordered_positions = [positions[section] for section in CANONICAL_DESIGN_SECTIONS]
    if ordered_positions != sorted(ordered_positions):
        raise ContractError(f"{path.name} sections must follow the canonical DESIGN.md order")

    lower_body = body.lower()
    if "decorative orb" in lower_body or "bokeh" in lower_body:
        raise ContractError(f"{path.name} must not encourage decorative effects")
    if "customiz" not in lower_body and "customis" not in lower_body:
        raise ContractError(f"{path.name} must explain how users can customize outputs")
