#!/usr/bin/env python3
"""Create a local adaptive logo explorer app from a JSON spec."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[3]
TEMPLATE = ROOT / "assets" / "logo-explorer-app"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "logo-route"


def normalize_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def first_text(*values: object) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def validate_spec(spec: dict) -> None:
    meta = spec.setdefault("meta", {})
    meta.setdefault("title", "Logo Explorer")
    meta.setdefault("stage", "Logo exploration")
    meta.setdefault("anchor", meta.get("brand_name") or meta.get("title", "Logo anchor"))
    meta.setdefault("summary", "Compare identity concepts and select one for final production.")

    constraints = spec.setdefault("constraints", {})
    constraints["preserve"] = normalize_list(constraints.get("preserve"))
    constraints["avoid"] = normalize_list(constraints.get("avoid"))

    routes = spec.get("routes") or spec.get("families") or spec.get("items")
    if not isinstance(routes, list) or not routes:
        raise ValueError("Spec must include a non-empty routes array.")

    normalized_routes = []
    for index, route in enumerate(routes, start=1):
        if not isinstance(route, dict):
            raise ValueError(f"Route {index} must be an object.")
        label = (
            route.get("label") or route.get("title") or route.get("id") or f"Logo concept {index}"
        )
        route["id"] = route.get("id") or slugify(label)
        route["label"] = label
        route.setdefault("family", route.get("tone") or "logo")
        route.setdefault("rationale", route.get("caption") or "")
        route["best_for"] = first_text(
            route.get("best_for"),
            route.get("bestFor"),
            route.get("usage_note"),
        )
        route["decision_advice"] = first_text(
            route.get("decision_advice"),
            route.get("decisionAdvice"),
            route.get("advice"),
            route.get("recommendation"),
            route.get("rationale"),
        )
        route["watch_out"] = first_text(
            route.get("watch_out"),
            route.get("watchOut"),
            route.get("caveat"),
        )
        route["next_step"] = first_text(
            route.get("next_step"),
            route.get("nextStep"),
            route.get("next"),
        )
        route.setdefault(
            "final_owner",
            spec.get("handoff", {}).get("default_owner", "external-production-identity"),
        )
        route["next_prompt_hints"] = normalize_list(route.get("next_prompt_hints"))
        route["usage_contexts"] = normalize_list(route.get("usage_contexts"))
        if not route.get("prompt"):
            raise ValueError(f"Route {index} ({route['id']}) is missing prompt.")
        normalized_routes.append(route)

    spec["routes"] = normalized_routes
    spec.setdefault("handoff", {})
    spec["handoff"].setdefault("default_owner", "external-production-identity")
    spec["handoff"]["next_prompt_hints"] = normalize_list(spec["handoff"].get("next_prompt_hints"))


def copy_base_asset(spec: dict, output: Path) -> None:
    meta = spec.get("meta", {})
    base_asset = meta.get("base_asset") or meta.get("base_asset_path")
    if not base_asset:
        return

    source = Path(base_asset).expanduser()
    if not source.is_absolute():
        source = Path.cwd() / source
    if not source.exists():
        raise FileNotFoundError(f"Base asset not found: {source}")

    suffix = source.suffix.lower() or ".png"
    target = output / "data" / f"base_asset{suffix}"
    shutil.copy2(source, target)
    meta["base_asset"] = str(source)
    meta["base_asset_url"] = f"/data/{target.name}"


def plugin_version_label() -> str:
    manifest_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return f"{manifest['name']}@{manifest['version']}"


def write_runtime_config(output: Path) -> None:
    (output / "data" / "runtime-config.json").write_text(
        json.dumps(
            {
                "createdByPluginVersion": plugin_version_label(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        required=True,
        type=Path,
        help="JSON file with meta, constraints, and routes.",
    )
    parser.add_argument("--output", required=True, type=Path, help="Output app directory.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace output directory if it already exists.",
    )
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    validate_spec(spec)

    if args.output.exists():
        if not args.force:
            raise FileExistsError(f"{args.output} already exists. Use --force to replace it.")
        shutil.rmtree(args.output)

    shutil.copytree(TEMPLATE, args.output)
    data_dir = args.output / "data"
    data_dir.mkdir(exist_ok=True)
    (args.output / "generated").mkdir(exist_ok=True)
    copy_base_asset(spec, args.output)
    write_runtime_config(args.output)

    (data_dir / "logo-spec.json").write_text(
        json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "output": str(args.output),
                "routes": len(spec["routes"]),
                "handoff_json": str(data_dir / "selected-logo-route.json"),
                "handoff_markdown": str(data_dir / "handoff.md"),
                "reviewSurface": "creative_production_board",
                "handoff": (
                    "Use the inline MCP mood-board review surface for generated logo imagery. "
                    "Use the local HTML/server surface only for debug or inspection requests."
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
