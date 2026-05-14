#!/usr/bin/env python3
"""Audit a Codex plugin scaffold before publishing or sharing it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAX_PLUGIN_NAME_LENGTH = 64
VALID_INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
VALID_AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}
SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
TEXT_SUFFIXES = {
    ".app.json",
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_FILE_NAMES = {"SKILL.md", "openai.yaml", "plugin.json", ".app.json", ".mcp.json"}
IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "references",
    "vendor",
}
ERROR_PLACEHOLDER_PATTERNS = [
    (re.compile(r"\[TODO(?::|\])", re.IGNORECASE), "scaffold [TODO] marker"),
    (re.compile(r"\b(?:TODO|FIXME|TBD)\b", re.IGNORECASE), "unfinished work marker"),
    (
        re.compile(r"\b(?:author@example\.com|docs\.example\.com|example\.com)\b", re.IGNORECASE),
        "example domain or email",
    ),
    (
        re.compile(
            r"\b(?:"
            r"Plugin Display Name|Brief plugin description|Short description for subtitle|"
            r"Long description for details page|Marketplace Display Name|marketplace-name|"
            r"keyword1|keyword2"
            r")\b",
            re.IGNORECASE,
        ),
        "scaffold sample text",
    ),
]
WARN_PLACEHOLDER_PATTERNS = [
    (re.compile(r"\blorem ipsum\b", re.IGNORECASE), "filler copy"),
    (re.compile(r"\bchange me\b", re.IGNORECASE), "unfinished change-me text"),
]
SCAFFOLD_DEFAULT_PROMPTS = {
    "Summarize my inbox and draft replies for me.",
    "Find open bugs and turn them into tickets.",
    "Review today's meetings and flag gaps.",
}
SCAFFOLD_BRAND_COLOR = "#3B82F6"
REQUIRED_TOP_LEVEL_STRINGS = [
    "name",
    "version",
    "description",
    "license",
]
REQUIRED_INTERFACE_STRINGS = [
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
]
RECOMMENDED_INTERFACE_STRINGS = [
    "privacyPolicyURL",
    "termsOfServiceURL",
]
OPTIONAL_PATH_FIELDS = {
    "skills": "directory",
    "hooks": "file",
    "mcpServers": "file",
    "apps": "file",
}


@dataclass(frozen=True)
class Issue:
    severity: str
    path: Path | None
    message: str


def add_issue(issues: list[Issue], severity: str, path: Path | None, message: str) -> None:
    issues.append(Issue(severity, path, message))


def rel_path(path: Path | None, base: Path) -> str:
    if path is None:
        return "-"
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def normalize_plugin_name(plugin_name: str) -> str:
    normalized = plugin_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def has_error_placeholder(text: str) -> tuple[str, str] | None:
    for pattern, label in ERROR_PLACEHOLDER_PATTERNS:
        match = pattern.search(text)
        if match:
            return label, match.group(0)
    return None


def has_warn_placeholder(text: str) -> tuple[str, str] | None:
    for pattern, label in WARN_PLACEHOLDER_PATTERNS:
        match = pattern.search(text)
        if match:
            return label, match.group(0)
    return None


def strip_scaffold_todo(value: str) -> str:
    stripped = value.strip()
    match = re.fullmatch(r"\[TODO:\s*(.*?)\s*\]", stripped, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return stripped


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_plugin_relative_path(value: str) -> bool:
    return value.startswith("./") and not Path(value).is_absolute() and ".." not in Path(value).parts


def path_is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
    except ValueError:
        return False
    return True


def load_json(path: Path, issues: list[Issue]) -> Any | None:
    try:
        with path.open() as handle:
            return json.load(handle)
    except FileNotFoundError:
        add_issue(issues, "ERROR", path, "File does not exist.")
    except json.JSONDecodeError as exc:
        add_issue(issues, "ERROR", path, f"Invalid JSON: {exc.msg} at line {exc.lineno}.")
    return None


def find_plugin_root(input_path: Path) -> Path:
    path = input_path.expanduser().resolve()
    if path.is_file() and path.name == "plugin.json" and path.parent.name == ".codex-plugin":
        return path.parent.parent
    if path.is_dir() and (path / ".codex-plugin" / "plugin.json").exists():
        return path
    raise ValueError(
        f"{input_path} is not a plugin root and is not a .codex-plugin/plugin.json file."
    )


def resolve_plugin_path(plugin_root: Path, value: str) -> Path:
    return (plugin_root / value).resolve()


def check_string_field(
    payload: dict[str, Any],
    field: str,
    issues: list[Issue],
    manifest_path: Path,
    context: str,
) -> None:
    value = payload.get(field)
    if not is_non_empty_string(value):
        add_issue(issues, "ERROR", manifest_path, f"{context}.{field} must be a non-empty string.")
        return
    placeholder = has_error_placeholder(value)
    if placeholder:
        label, match = placeholder
        add_issue(
            issues,
            "ERROR",
            manifest_path,
            f"{context}.{field} contains {label}: {match!r}.",
        )


def check_url_field(
    payload: dict[str, Any],
    field: str,
    issues: list[Issue],
    manifest_path: Path,
    context: str,
    required: bool,
) -> None:
    value = payload.get(field)
    if value is None and not required:
        add_issue(issues, "WARN", manifest_path, f"{context}.{field} is recommended.")
        return
    check_string_field(payload, field, issues, manifest_path, context)
    if not is_non_empty_string(value):
        return
    if has_error_placeholder(value):
        return
    if not re.match(r"^https?://", value):
        add_issue(issues, "ERROR", manifest_path, f"{context}.{field} must be an http(s) URL.")


def check_asset_path(
    plugin_root: Path,
    value: Any,
    label: str,
    issues: list[Issue],
    manifest_path: Path,
    supported_suffixes: set[str] | None = None,
) -> None:
    supported_suffixes = supported_suffixes or SUPPORTED_IMAGE_SUFFIXES
    if not is_non_empty_string(value):
        add_issue(issues, "ERROR", manifest_path, f"interface.{label} must be a relative asset path.")
        return
    placeholder = has_error_placeholder(value)
    if placeholder:
        label_text, match = placeholder
        add_issue(
            issues,
            "ERROR",
            manifest_path,
            f"interface.{label} contains {label_text}: {match!r}.",
        )
        return
    if not is_plugin_relative_path(value):
        add_issue(
            issues,
            "ERROR",
            manifest_path,
            f"interface.{label} must be a relative plugin path starting with './'.",
        )
        return
    asset_path = resolve_plugin_path(plugin_root, value)
    if asset_path.suffix.lower() not in supported_suffixes:
        asset_kind = "PNG image file" if supported_suffixes == {".png"} else "supported image file"
        add_issue(
            issues,
            "ERROR",
            manifest_path,
            f"interface.{label} must point to a {asset_kind}.",
        )
    if not asset_path.exists():
        add_issue(issues, "ERROR", asset_path, f"Missing interface.{label} asset.")
    elif asset_path.is_file() and asset_path.stat().st_size == 0:
        add_issue(issues, "ERROR", asset_path, f"interface.{label} asset is empty.")


def check_prompt_list(prompts: Any, issues: list[Issue], manifest_path: Path) -> None:
    if not isinstance(prompts, list) or not prompts:
        add_issue(issues, "ERROR", manifest_path, "interface.defaultPrompt must be a non-empty array.")
        return
    if len(prompts) > 3:
        add_issue(issues, "ERROR", manifest_path, "interface.defaultPrompt must contain at most 3 prompts.")

    seen: set[str] = set()
    for index, prompt in enumerate(prompts, start=1):
        if not is_non_empty_string(prompt):
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"interface.defaultPrompt[{index}] must be a non-empty string.",
            )
            continue
        cleaned_prompt = strip_scaffold_todo(prompt)
        placeholder = has_error_placeholder(prompt)
        if placeholder:
            label, match = placeholder
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"interface.defaultPrompt[{index}] contains {label}: {match!r}.",
            )
            continue
        if cleaned_prompt in SCAFFOLD_DEFAULT_PROMPTS:
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"interface.defaultPrompt[{index}] still matches a scaffold sample prompt.",
            )
        if len(prompt) > 128:
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"interface.defaultPrompt[{index}] is {len(prompt)} characters; max is 128.",
            )
        normalized = " ".join(cleaned_prompt.lower().split())
        if normalized in seen:
            add_issue(
                issues,
                "WARN",
                manifest_path,
                f"interface.defaultPrompt[{index}] duplicates another starter prompt.",
            )
        seen.add(normalized)


def check_plugin_json(plugin_root: Path, issues: list[Issue]) -> dict[str, Any] | None:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path, issues)
    if manifest is None:
        return None
    if not isinstance(manifest, dict):
        add_issue(issues, "ERROR", manifest_path, "plugin.json must contain a JSON object.")
        return None

    for field in REQUIRED_TOP_LEVEL_STRINGS:
        check_string_field(manifest, field, issues, manifest_path, "plugin")

    plugin_name = manifest.get("name")
    if is_non_empty_string(plugin_name):
        if normalize_plugin_name(plugin_name) != plugin_name:
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                "plugin.name must be lower-case hyphen-case.",
            )
        if len(plugin_name) > MAX_PLUGIN_NAME_LENGTH:
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"plugin.name must be {MAX_PLUGIN_NAME_LENGTH} characters or fewer.",
            )
        if plugin_root.name != plugin_name:
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"plugin.name must match the plugin folder name '{plugin_root.name}'.",
            )

    version = manifest.get("version")
    if (
        is_non_empty_string(version)
        and not has_error_placeholder(version)
        and not re.match(
            r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$",
            version,
        )
    ):
        add_issue(issues, "ERROR", manifest_path, "plugin.version must be a semantic version.")

    author = manifest.get("author")
    if not isinstance(author, dict):
        add_issue(issues, "ERROR", manifest_path, "plugin.author must be an object.")
    else:
        for field in ["name", "email"]:
            check_string_field(author, field, issues, manifest_path, "plugin.author")
        email = author.get("email")
        if is_non_empty_string(email) and "@" not in email:
            add_issue(issues, "ERROR", manifest_path, "plugin.author.email must be an email address.")
        check_url_field(author, "url", issues, manifest_path, "plugin.author", required=True)

    for field in ["homepage", "repository"]:
        check_url_field(manifest, field, issues, manifest_path, "plugin", required=True)

    keywords = manifest.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        add_issue(issues, "ERROR", manifest_path, "plugin.keywords must be a non-empty array.")
    else:
        for index, keyword in enumerate(keywords, start=1):
            if not is_non_empty_string(keyword):
                add_issue(
                    issues,
                    "ERROR",
                    manifest_path,
                    f"plugin.keywords[{index}] must be a non-empty string.",
                )
            elif has_error_placeholder(keyword):
                add_issue(
                    issues,
                    "ERROR",
                    manifest_path,
                    f"plugin.keywords[{index}] contains placeholder text.",
                )

    for field, expected_type in OPTIONAL_PATH_FIELDS.items():
        value = manifest.get(field)
        if value is None:
            continue
        if not is_non_empty_string(value):
            add_issue(issues, "ERROR", manifest_path, f"plugin.{field} must be a relative path string.")
            continue
        placeholder = has_error_placeholder(value)
        if placeholder:
            label, match = placeholder
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"plugin.{field} contains {label}: {match!r}.",
            )
            continue
        if not is_plugin_relative_path(value):
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"plugin.{field} must be a relative plugin path starting with './'.",
            )
            continue
        resolved = resolve_plugin_path(plugin_root, value)
        if not resolved.exists():
            add_issue(issues, "ERROR", resolved, f"plugin.{field} points to a missing path.")
        elif expected_type == "directory" and not resolved.is_dir():
            add_issue(issues, "ERROR", resolved, f"plugin.{field} must point to a directory.")
        elif expected_type == "file" and not resolved.is_file():
            add_issue(issues, "ERROR", resolved, f"plugin.{field} must point to a file.")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        add_issue(issues, "ERROR", manifest_path, "plugin.interface must be an object.")
        return manifest

    for field in REQUIRED_INTERFACE_STRINGS:
        check_string_field(interface, field, issues, manifest_path, "interface")
    check_url_field(interface, "websiteURL", issues, manifest_path, "interface", required=True)
    for field in RECOMMENDED_INTERFACE_STRINGS:
        check_url_field(interface, field, issues, manifest_path, "interface", required=False)

    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        add_issue(issues, "ERROR", manifest_path, "interface.capabilities must be a non-empty array.")
    else:
        for capability in capabilities:
            if not is_non_empty_string(capability):
                add_issue(issues, "ERROR", manifest_path, "interface.capabilities must contain strings.")

    brand_color = interface.get("brandColor")
    if not is_non_empty_string(brand_color):
        add_issue(issues, "ERROR", manifest_path, "interface.brandColor must be a non-empty string.")
    else:
        placeholder = has_error_placeholder(brand_color)
        if placeholder:
            label, match = placeholder
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                f"interface.brandColor contains {label}: {match!r}.",
            )
        elif not re.match(r"^#[0-9A-Fa-f]{6}$", brand_color):
            add_issue(
                issues,
                "ERROR",
                manifest_path,
                "interface.brandColor must be a 6-digit hex color like #3B82F6.",
            )
        elif brand_color.upper() == SCAFFOLD_BRAND_COLOR:
            add_issue(
                issues,
                "WARN",
                manifest_path,
                "interface.brandColor is the scaffold default; confirm it is intentional.",
            )

    check_prompt_list(interface.get("defaultPrompt"), issues, manifest_path)
    check_asset_path(plugin_root, interface.get("composerIcon"), "composerIcon", issues, manifest_path)
    check_asset_path(plugin_root, interface.get("logo"), "logo", issues, manifest_path)

    screenshots = interface.get("screenshots")
    if screenshots is None:
        pass
    elif not isinstance(screenshots, list):
        add_issue(issues, "ERROR", manifest_path, "interface.screenshots must be an array.")
    else:
        for index, screenshot in enumerate(screenshots, start=1):
            check_asset_path(
                plugin_root,
                screenshot,
                f"screenshots[{index}]",
                issues,
                manifest_path,
                supported_suffixes={".png"},
            )

    developer_name = interface.get("developerName")
    if developer_name != "OpenAI" and not (
        isinstance(developer_name, str) and has_error_placeholder(developer_name)
    ):
        for field in ["privacyPolicyURL", "termsOfServiceURL"]:
            value = interface.get(field)
            if is_non_empty_string(value) and "openai.com" in value:
                add_issue(
                    issues,
                    "WARN",
                    manifest_path,
                    f"interface.{field} points to OpenAI while developerName is {developer_name!r}.",
                )

    return manifest


def check_json_component_file(
    plugin_root: Path,
    manifest: dict[str, Any],
    manifest_field: str,
    required_key: str,
    issues: list[Issue],
) -> None:
    value = manifest.get(manifest_field)
    if not is_non_empty_string(value) or not is_plugin_relative_path(value):
        return
    path = resolve_plugin_path(plugin_root, value)
    if not path.exists():
        return
    payload = load_json(path, issues)
    if payload is None:
        return
    if not isinstance(payload, dict):
        add_issue(issues, "ERROR", path, f"{path.name} must contain a JSON object.")
        return
    section = payload.get(required_key)
    if not isinstance(section, dict):
        add_issue(issues, "ERROR", path, f"{path.name} must contain a '{required_key}' object.")
    elif not section:
        add_issue(
            issues,
            "ERROR",
            path,
            f"{path.name} has an empty '{required_key}' object; fill it or remove plugin.{manifest_field}.",
        )


def parse_skill_frontmatter(path: Path) -> dict[str, str] | None:
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("\"'")
    return None


def parse_openai_interface(path: Path) -> dict[str, str] | None:
    text = path.read_text(errors="replace")
    in_interface = False
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^interface:\s*$", line):
            in_interface = True
            continue
        if in_interface and not line.startswith((" ", "\t")):
            break
        if in_interface:
            match = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
            if match:
                value = match.group(2).strip().strip("\"'")
                fields[match.group(1)] = value
    return fields if in_interface else None


def validate_openai_yaml(
    openai_path: Path,
    base_path: Path,
    issues: list[Issue],
    default_prompt_required: bool,
) -> None:
    interface = parse_openai_interface(openai_path)
    if interface is None:
        add_issue(issues, "ERROR", openai_path, "openai.yaml must contain an interface block.")
        return

    for field in ["display_name", "short_description"]:
        if not is_non_empty_string(interface.get(field)):
            add_issue(issues, "ERROR", openai_path, f"interface.{field} must be set.")
    default_prompt = interface.get("default_prompt")
    if not is_non_empty_string(default_prompt):
        severity = "ERROR" if default_prompt_required else "WARN"
        add_issue(issues, severity, openai_path, "interface.default_prompt should be set.")

    for icon_field in ["icon_small", "icon_large"]:
        icon_value = interface.get(icon_field)
        if not is_non_empty_string(icon_value):
            add_issue(issues, "WARN", openai_path, f"interface.{icon_field} is recommended.")
            continue
        if not is_plugin_relative_path(icon_value):
            add_issue(
                issues,
                "ERROR",
                openai_path,
                f"interface.{icon_field} must be a relative path starting with './'.",
            )
            continue
        icon_path = (base_path / icon_value).resolve()
        if not icon_path.exists():
            add_issue(issues, "ERROR", icon_path, f"Missing openai.yaml {icon_field} asset.")
        elif icon_path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            add_issue(issues, "ERROR", icon_path, f"openai.yaml {icon_field} is not a supported image.")


def find_skill_dirs(plugin_root: Path, manifest: dict[str, Any] | None) -> list[Path]:
    skills_root = plugin_root / "skills"
    if manifest and is_non_empty_string(manifest.get("skills")) and is_plugin_relative_path(manifest["skills"]):
        skills_root = resolve_plugin_path(plugin_root, manifest["skills"])
    if not skills_root.is_dir():
        return []
    return sorted({path.parent for path in skills_root.rglob("SKILL.md")})


def check_skills_and_openai_yaml(
    plugin_root: Path,
    manifest: dict[str, Any] | None,
    issues: list[Issue],
    allow_missing_skill_openai: bool,
) -> None:
    checked_openai_paths: set[Path] = set()
    skill_dirs = find_skill_dirs(plugin_root, manifest)

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        frontmatter = parse_skill_frontmatter(skill_md)
        if frontmatter is None:
            add_issue(issues, "ERROR", skill_md, "SKILL.md must start with YAML frontmatter.")
        else:
            for field in ["name", "description"]:
                if not is_non_empty_string(frontmatter.get(field)):
                    add_issue(issues, "ERROR", skill_md, f"frontmatter.{field} must be set.")
            skill_name = frontmatter.get("name")
            if is_non_empty_string(skill_name) and normalize_plugin_name(skill_name) != skill_dir.name:
                add_issue(
                    issues,
                    "WARN",
                    skill_md,
                    f"frontmatter.name {skill_name!r} does not match folder name {skill_dir.name!r}.",
                )

        openai_path = skill_dir / "agents" / "openai.yaml"
        if not openai_path.exists():
            severity = "WARN" if allow_missing_skill_openai else "ERROR"
            add_issue(
                issues,
                severity,
                openai_path,
                "Each skill should have agents/openai.yaml UI metadata.",
            )
        else:
            validate_openai_yaml(
                openai_path,
                skill_dir,
                issues,
                default_prompt_required=False,
            )
            checked_openai_paths.add(openai_path.resolve())

    for openai_path in sorted(plugin_root.rglob("agents/openai.yaml")):
        if openai_path.resolve() in checked_openai_paths:
            continue
        base_path = openai_path.parent.parent
        validate_openai_yaml(
            openai_path,
            base_path,
            issues,
            default_prompt_required=True,
        )

    if not skill_dirs and not (plugin_root / "agents" / "openai.yaml").exists():
        add_issue(
            issues,
            "WARN",
            plugin_root,
            "No skills or root agents/openai.yaml found; confirm the plugin exposes a usable entrypoint.",
        )


def iter_text_files(plugin_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in plugin_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.stat().st_size > 512_000:
            continue
        if path.name in TEXT_FILE_NAMES or path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return files


def check_placeholders(plugin_root: Path, issues: list[Issue]) -> None:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    for path in iter_text_files(plugin_root):
        if path == manifest_path:
            continue
        text = path.read_text(errors="replace")
        error_placeholder = has_error_placeholder(text)
        if error_placeholder:
            label, match = error_placeholder
            add_issue(issues, "ERROR", path, f"Contains {label}: {match!r}.")
            continue
        warn_placeholder = has_warn_placeholder(text)
        if warn_placeholder:
            label, match = warn_placeholder
            add_issue(issues, "WARN", path, f"Contains possible {label}: {match!r}.")


def discover_repo_plugin_marketplace(plugin_root: Path) -> Path | None:
    for parent in plugin_root.parents:
        candidate = parent / ".agents" / "plugins" / "marketplace.json"
        plugins_dir = parent / "plugins"
        if candidate.exists() and path_is_relative_to(plugin_root, plugins_dir):
            return candidate
    return None


def check_marketplace(
    marketplace_path: Path,
    plugin_name: str,
    issues: list[Issue],
) -> None:
    payload = load_json(marketplace_path, issues)
    if payload is None:
        return
    if not isinstance(payload, dict):
        add_issue(issues, "ERROR", marketplace_path, "marketplace.json must contain a JSON object.")
        return
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        add_issue(issues, "ERROR", marketplace_path, "marketplace.json plugins must be an array.")
        return

    entry = next(
        (item for item in plugins if isinstance(item, dict) and item.get("name") == plugin_name),
        None,
    )
    if entry is None:
        add_issue(issues, "ERROR", marketplace_path, f"No marketplace entry found for {plugin_name!r}.")
        return

    source = entry.get("source")
    if not isinstance(source, dict):
        add_issue(issues, "ERROR", marketplace_path, f"Marketplace entry {plugin_name!r} needs source.")
    else:
        if source.get("source") != "local":
            add_issue(
                issues,
                "ERROR",
                marketplace_path,
                f"Marketplace entry {plugin_name!r} source.source must be 'local'.",
            )
        expected_path = f"./plugins/{plugin_name}"
        if source.get("path") != expected_path:
            add_issue(
                issues,
                "ERROR",
                marketplace_path,
                f"Marketplace entry {plugin_name!r} source.path must be {expected_path!r}.",
            )

    policy = entry.get("policy")
    if not isinstance(policy, dict):
        add_issue(issues, "ERROR", marketplace_path, f"Marketplace entry {plugin_name!r} needs policy.")
    else:
        if policy.get("installation") not in VALID_INSTALL_POLICIES:
            add_issue(
                issues,
                "ERROR",
                marketplace_path,
                f"Marketplace entry {plugin_name!r} has invalid policy.installation.",
            )
        if policy.get("authentication") not in VALID_AUTH_POLICIES:
            add_issue(
                issues,
                "ERROR",
                marketplace_path,
                f"Marketplace entry {plugin_name!r} has invalid policy.authentication.",
            )
    if not is_non_empty_string(entry.get("category")):
        add_issue(issues, "ERROR", marketplace_path, f"Marketplace entry {plugin_name!r} needs category.")


def print_report(plugin_root: Path, issues: list[Issue]) -> None:
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    warnings = [issue for issue in issues if issue.severity == "WARN"]

    print(f"Plugin readiness report: {plugin_root}")
    if not issues:
        print("OK: no blockers or warnings found.")
        return

    for severity in ["ERROR", "WARN"]:
        matching = [issue for issue in issues if issue.severity == severity]
        if not matching:
            continue
        print(f"\n{severity}S ({len(matching)}):")
        for issue in matching:
            print(f"- {rel_path(issue.path, plugin_root)}: {issue.message}")

    print(f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether a Codex plugin is ready to publish or share."
    )
    parser.add_argument("plugin_path", help="Plugin root or .codex-plugin/plugin.json path")
    parser.add_argument(
        "--marketplace-path",
        help=(
            "Optional marketplace.json path to validate against this plugin. "
            "Repo plugins under <repo>/plugins are checked against <repo>/.agents/plugins/marketplace.json automatically."
        ),
    )
    parser.add_argument(
        "--allow-missing-skill-openai",
        "--allow-missing-openai-yaml",
        dest="allow_missing_skill_openai",
        action="store_true",
        help="Warn instead of failing when a skill lacks agents/openai.yaml.",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Exit non-zero when warnings are present.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    issues: list[Issue] = []
    try:
        plugin_root = find_plugin_root(Path(args.plugin_path))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    manifest = check_plugin_json(plugin_root, issues)
    if manifest is not None:
        check_json_component_file(plugin_root, manifest, "apps", "apps", issues)
        check_json_component_file(plugin_root, manifest, "mcpServers", "mcpServers", issues)

    check_skills_and_openai_yaml(
        plugin_root,
        manifest,
        issues,
        allow_missing_skill_openai=args.allow_missing_skill_openai,
    )
    check_placeholders(plugin_root, issues)

    plugin_name = manifest.get("name") if isinstance(manifest, dict) else None
    if is_non_empty_string(plugin_name):
        if args.marketplace_path:
            marketplace_path = Path(args.marketplace_path).expanduser().resolve()
            check_marketplace(marketplace_path, plugin_name, issues)
        else:
            marketplace_path = discover_repo_plugin_marketplace(plugin_root)
            if marketplace_path is not None:
                check_marketplace(
                    marketplace_path,
                    plugin_name,
                    issues,
                )

    print_report(plugin_root, issues)
    has_errors = any(issue.severity == "ERROR" for issue in issues)
    has_warnings = any(issue.severity == "WARN" for issue in issues)
    return 1 if has_errors or (args.strict_warnings and has_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
