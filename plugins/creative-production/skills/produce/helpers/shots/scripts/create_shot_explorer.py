#!/usr/bin/env python3
"""Build a Creative Production Shot Explorer batch and shared review page."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PLUGIN_ROOT = SCRIPT_DIR.parents[4]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from scripts import review_renderer  # noqa: E402

DEFAULT_IMAGE_GENERATION_RUNNER = None


VALID_GROUPS = {"angle", "crop", "detail"}


DEFAULT_SHOTS: list[dict[str, str]] = [
    {
        "id": "overhead",
        "label": "overhead",
        "group": "angle",
        "prompt": "Using the uploaded image as the source reference, create a clean overhead product photograph from directly above. Preserve the subject identity, proportions, colors, materials, logo placement, and visible surface details. Use controlled commercial light and a simple background. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "side-profile",
        "label": "side profile",
        "group": "angle",
        "prompt": "Using the uploaded image as the source reference, create a precise side-profile product photograph. Preserve the subject identity, proportions, colors, materials, logo placement, and important markings. Use simple studio lighting and realistic shadow. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "three-quarter-front",
        "label": "three-quarter front",
        "group": "angle",
        "prompt": "Using the uploaded image as the source reference, create a three-quarter front product photograph that shows depth and shape while keeping the product recognizable. Preserve silhouette, materials, colors, visible logos, and key construction details. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "low-hero",
        "label": "low hero angle",
        "group": "angle",
        "prompt": "Using the uploaded image as the source reference, create a low hero-angle commercial product photograph with a slightly upward camera position. Preserve subject identity, proportions, colors, materials, logo placement, and surface details. Keep the background simple and product-led. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "back",
        "label": "back view",
        "group": "angle",
        "prompt": "Using the uploaded image as the source reference, create a plausible rear or back-view product photograph. Preserve construction logic, materials, colors, brand placement rules, and category. Infer only the hidden reverse angle needed for a commercial shot. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "pan-left",
        "label": "pan left",
        "group": "crop",
        "prompt": "Using the uploaded image as the source reference, recompose the shot as if the camera panned left. Preserve product identity, scale logic, materials, colors, and visible markings. Add clean breathing room on the left while keeping the subject commercially framed. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "pan-right",
        "label": "pan right",
        "group": "crop",
        "prompt": "Using the uploaded image as the source reference, recompose the shot as if the camera panned right. Preserve product identity, scale logic, materials, colors, and visible markings. Add clean breathing room on the right while keeping the subject commercially framed. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "zoom-in",
        "label": "zoom in",
        "group": "crop",
        "prompt": "Using the uploaded image as the source reference, create a tighter close-up crop of the subject. Preserve identity, materials, colors, logo placement, and important construction details. Make the frame feel like a professional close product photograph. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "wide-context",
        "label": "wide context",
        "group": "crop",
        "prompt": "Using the uploaded image as the source reference, create a wider commercial product shot with more clean space around the subject. Preserve identity, materials, colors, logo placement, and important details. Add only simple studio breathing room, not a new ad layout. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "macro-detail",
        "label": "macro detail",
        "group": "detail",
        "prompt": "Using the uploaded image as the source reference, create an extreme macro detail product photograph. Preserve the source subject identity, materials, colors, surface texture, visible logo placement where applicable, and category. Focus on tactile texture, stitching, finish, and craftsmanship. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "material-edge",
        "label": "material edge",
        "group": "detail",
        "prompt": "Using the uploaded image as the source reference, create a close detail photograph of an edge, seam, material transition, or construction junction. Preserve the product identity, colors, materials, texture, and category. Keep the image commercial and inspectable. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "surface-texture",
        "label": "surface texture",
        "group": "detail",
        "prompt": "Using the uploaded image as the source reference, create a detail photograph centered on surface texture and material finish. Preserve the product identity, palette, material cues, construction, and category. Use clean commercial lighting. No new readable text, claims, labels, or logos.",
    },
    {
        "id": "surprise-angle",
        "label": "surprise commercial angle",
        "group": "detail",
        "prompt": "Using the uploaded image as the source reference, create one unexpected but commercially useful camera angle. Preserve subject identity, materials, colors, logo placement, and important details. The result should feel like a strong exploratory product shot, not an ad layout. No new readable text, claims, labels, or logos.",
    },
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "shot-route"


def normalize_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def default_spec() -> dict[str, Any]:
    return {
        "meta": {
            "title": "Shot Explorer",
            "stage": "Shot exploration",
            "anchor": "Uploaded image",
            "summary": "Select shot directions, generate the chosen angles, and review them in the shared Creative Production gallery.",
        },
        "constraints": {
            "preserve": [
                "subject identity",
                "silhouette and proportions",
                "materials, colors, visible logos, and surface details",
            ],
            "avoid": [
                "new claims",
                "fake endorsements",
                "competitor marks",
                "new readable labels unless requested",
            ],
        },
        "shots": DEFAULT_SHOTS,
        "review": {
            "layout": "wall",
            "title": "Shot Explorer",
            "showCaptions": False,
            "showPrompts": False,
            "note": "Image-led review wall. Captions and prompt details stay in the manifest, not under the tiles.",
            "emptyMessage": "Images pending. Generate the selected shots to populate this review wall.",
            "contactSheetColumns": 4,
            "contactSheetOutput": "shot-contact-sheet.png",
        },
        "handoff": {
            "default_owner": "produce",
        },
    }


def normalize_group(group: object) -> str:
    candidate = str(group or "").strip().lower()
    return candidate if candidate in VALID_GROUPS else "detail"


def validate_spec(spec: dict[str, Any]) -> None:
    meta = spec.setdefault("meta", {})
    meta.setdefault("title", "Shot Explorer")
    meta.setdefault("stage", "Shot exploration")
    meta.setdefault("anchor", meta.get("title", "Uploaded image"))
    meta.setdefault("summary", "Select shot directions and generate camera variants.")

    constraints = spec.setdefault("constraints", {})
    constraints["preserve"] = normalize_list(constraints.get("preserve"))
    constraints["avoid"] = normalize_list(constraints.get("avoid"))

    shots = spec.get("shots") or spec.get("routes") or spec.get("items") or DEFAULT_SHOTS
    if not isinstance(shots, list) or not shots:
        raise ValueError(
            "Spec must include a non-empty shots array, or omit shots to use defaults."
        )

    normalized_shots = []
    seen = set()
    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            raise ValueError(f"Shot {index} must be an object.")
        label = str(shot.get("label") or shot.get("title") or shot.get("id") or f"Shot {index}")
        shot_id = str(shot.get("id") or slugify(label))
        if shot_id in seen:
            raise ValueError(f"Duplicate shot id: {shot_id}")
        seen.add(shot_id)
        normalized = {
            **shot,
            "id": shot_id,
            "label": label,
            "group": normalize_group(shot.get("group")),
        }
        if not normalized.get("prompt"):
            raise ValueError(f"Shot {index} ({shot_id}) is missing prompt.")
        normalized_shots.append(normalized)

    spec["shots"] = normalized_shots
    review = spec.setdefault("review", {})
    if not review.get("preset") and not review.get("layout"):
        review["layout"] = "wall"
    if review.get("preset") == "shot-wall":
        review.pop("preset")
        review["layout"] = "wall"
    spec["review"].setdefault("title", f"{meta['title']} Review")
    spec["review"].setdefault("showCaptions", False)
    spec["review"].setdefault("showPrompts", False)
    spec.setdefault("handoff", {})
    spec["handoff"].setdefault("default_owner", "produce")


def parse_selected(values: list[str] | None) -> list[str]:
    selected: list[str] = []
    for value in values or []:
        selected.extend(part.strip() for part in value.split(",") if part.strip())
    return selected


def choose_shots(spec: dict[str, Any], selected: list[str] | None) -> list[dict[str, Any]]:
    shots = spec["shots"]
    requested = parse_selected(selected)
    if not requested:
        requested = normalize_list(spec.get("selected_shots") or spec.get("selected"))
    if not requested:
        return shots

    by_key: dict[str, dict[str, Any]] = {}
    for shot in shots:
        by_key[shot["id"]] = shot
        by_key[slugify(shot["label"])] = shot
        by_key[str(shot["label"]).strip().lower()] = shot

    chosen = []
    missing = []
    for item in requested:
        key = slugify(item)
        shot = by_key.get(item) or by_key.get(item.lower()) or by_key.get(key)
        if shot:
            if shot not in chosen:
                chosen.append(shot)
        else:
            missing.append(item)
    if missing:
        available = ", ".join(shot["id"] for shot in shots)
        raise ValueError(f"Unknown selected shot(s): {', '.join(missing)}. Available: {available}")
    return chosen


def resolve_source(source_value: str | Path | None) -> Path | None:
    if not source_value:
        return None
    source = Path(source_value).expanduser()
    if not source.is_absolute():
        source = Path.cwd() / source
    if not source.exists():
        raise FileNotFoundError(f"Base asset not found: {source}")
    return source


def copy_base_asset(
    spec: dict[str, Any], output: Path, base_asset: Path | None
) -> dict[str, Any] | None:
    meta = spec.get("meta", {})
    source = resolve_source(base_asset or meta.get("base_asset") or meta.get("base_asset_path"))
    if not source:
        existing = output / "data" / "source-image.json"
        if existing.exists():
            return json.loads(existing.read_text(encoding="utf-8"))
        return None

    content = source.read_bytes()
    source_id = hashlib.sha256(content).hexdigest()[:32]
    mime_type = mimetypes.guess_type(source.name)[0] or "image/png"
    suffix = source.suffix.lower() or ".png"
    target_name = f"source-{source_id}{suffix}"
    target = output / "uploads" / target_name
    target.write_bytes(content)

    source_meta = {
        "id": source_id,
        "name": source.name,
        "mimeType": mime_type,
        "fileName": target_name,
        "path": f"uploads/{target_name}",
        "filePath": str(target),
        "url": f"uploads/{target_name}",
        "uploadedAt": "seeded-by-create-shot-explorer",
    }
    (output / "data" / "source-image.json").write_text(
        json.dumps(source_meta, indent=2) + "\n",
        encoding="utf-8",
    )
    meta["base_asset"] = str(source)
    meta["base_asset_url"] = source_meta["url"]
    meta["base_asset_name"] = source.name
    return source_meta


def output_name(index: int, total: int, shot: dict[str, Any]) -> str:
    width = 3 if total >= 100 else 2
    return f"{index:0{width}d}-{shot['id']}.png"


def prompt_for_shot(
    shot: dict[str, Any],
    *,
    mode: str,
    preserve: list[str],
    avoid: list[str],
) -> str:
    mode_instruction = (
        "Use a production-quality render with stronger source preservation and careful commercial lighting."
        if mode == "pro"
        else "Use a fast exploratory render suitable for comparing shot direction."
    )
    lines = [
        str(shot["prompt"]),
        mode_instruction,
        "Keep the source subject visibly central, recognizable, and inspectable.",
    ]
    if preserve:
        lines.append(f"Preserve: {', '.join(preserve)}.")
    if avoid:
        lines.append(f"Avoid: {', '.join(avoid)}.")
    lines.append(
        "Avoid invented claims, fake labels, extra brand marks, watermarks, captions, contact sheets, UI chrome, split panels, or collage layouts."
    )
    return "\n\n".join(lines)


def build_manifest(
    shots: list[dict[str, Any]],
    *,
    mode: str,
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    total = len(shots)
    preserve = spec.get("constraints", {}).get("preserve") or []
    avoid = spec.get("constraints", {}).get("avoid") or []
    manifest = []
    for index, shot in enumerate(shots, start=1):
        prompt = prompt_for_shot(shot, mode=mode, preserve=preserve, avoid=avoid)
        manifest.append(
            {
                "index": index,
                "id": shot["id"],
                "title": shot["label"],
                "label": shot["label"],
                "group": shot["group"],
                "routeName": shot["group"],
                "output": output_name(index, total, shot),
                "prompt": prompt,
            }
        )
    return manifest


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_batch(
    out_dir: Path,
    spec: dict[str, Any],
    source: dict[str, Any] | None,
    manifest: list[dict[str, Any]],
) -> tuple[Path, Path, Path]:
    data_dir = out_dir / "data"
    data_dir.mkdir(exist_ok=True)
    manifest_file = data_dir / "prompts-manifest.json"
    job_file = data_dir / "jobs.jsonl"
    spec_file = data_dir / "shot-spec.json"
    write_json(spec_file, spec)
    write_json(manifest_file, manifest)
    job_lines = []
    for item in manifest:
        job_lines.append(
            json.dumps(
                {
                    "id": item["id"],
                    "shot_id": item["id"],
                    "title": item["title"],
                    "group": item["group"],
                    "output": item["output"],
                    "prompt": item["prompt"],
                    "source": source,
                }
            )
        )
    job_file.write_text("\n".join(job_lines) + ("\n" if job_lines else ""), encoding="utf-8")
    return job_file, manifest_file, spec_file


def generate_images(
    args: argparse.Namespace,
    job_file: Path,
    *,
    total: int,
) -> int:
    if args.image_generation_runner is None:
        raise SystemExit(
            "Image generation is chat-managed in this plugin. Run without --generate "
            "and let the Creative Production coordinator generate and ingest the images."
        )
    cmd = [
        sys.executable,
        str(args.image_generation_runner),
        "--input",
        str(job_file),
        "--out-dir",
        str(args.output),
        "--workspace",
        str(args.workspace),
        "--max-concurrency",
        str(args.max_concurrency),
        "--max-attempts",
        str(args.max_attempts),
        "--timeout-seconds",
        str(args.timeout_seconds),
    ]
    subprocess.run(cmd, check=True)
    return sum(1 for item in review_renderer.image_files(args.output) if item.is_file()) or total


def write_handoff(
    out_dir: Path,
    spec: dict[str, Any],
    source: dict[str, Any] | None,
    manifest: list[dict[str, Any]],
    review_file: Path,
    contact_sheet: Path | None,
    *,
    mode: str,
) -> tuple[Path, Path]:
    data_dir = out_dir / "data"
    generated = [
        {
            **item,
            "fileName": item["output"],
            "url": item["output"] if (out_dir / item["output"]).exists() else None,
        }
        for item in manifest
    ]
    handoff = {
        "meta": spec.get("meta", {}),
        "source": source,
        "selected_shot_route": None,
        "generated_shots": generated,
        "constraints": spec.get("constraints", {}),
        "settings": {
            "mode": mode,
            "generator": "codex-exec-imagegen",
            "source_preservation": "Source file metadata is included in worker context; generation is prompt-driven through native image generation.",
            "review_html": str(review_file),
            "contact_sheet": str(contact_sheet) if contact_sheet else None,
            "default_owner": spec.get("handoff", {}).get("default_owner", "produce"),
        },
        "final_owner": spec.get("handoff", {}).get("default_owner", "produce"),
    }
    json_file = data_dir / "selected-shot-route.json"
    markdown_file = data_dir / "handoff.md"
    write_json(json_file, handoff)
    preserve = spec.get("constraints", {}).get("preserve") or []
    avoid = spec.get("constraints", {}).get("avoid") or []
    markdown_file.write_text(
        "\n".join(
            [
                f"# {spec.get('meta', {}).get('title', 'Shot Explorer')}",
                "",
                f"Source: {(source or {}).get('name', 'unspecified')}",
                f"Review board: [review board](../{review_file.name})",
                f"Contact sheet: [contact sheet](../{contact_sheet.name})"
                if contact_sheet
                else "Contact sheet: not generated",
                f"Final owner: {handoff['final_owner']}",
                "",
                "## Selected Shot",
                "- None selected yet",
                "",
                "## Shot Directions",
                *[f"- {item['title']} ({item['group']}): {item['output']}" for item in manifest],
                "",
                "## Preserve",
                *(f"- {item}" for item in preserve),
                "",
                "## Avoid",
                *(f"- {item}" for item in avoid),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return json_file, markdown_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        type=Path,
        help="Optional JSON file with meta, constraints, and shots.",
    )
    parser.add_argument(
        "--base-asset", type=Path, help="Image to preserve as the source reference."
    )
    parser.add_argument("--output", required=True, type=Path, help="Output review directory.")
    parser.add_argument(
        "--selected",
        action="append",
        help="Shot id or label to include. May be comma-separated.",
    )
    parser.add_argument("--shot", dest="selected", action="append", help="Alias for --selected.")
    parser.add_argument("--mode", choices=["fast", "pro"], default="fast")
    parser.add_argument(
        "--image-generation-runner", type=Path, default=DEFAULT_IMAGE_GENERATION_RUNNER
    )
    parser.add_argument("--workspace", type=Path, default=PLUGIN_ROOT.parents[1])
    parser.add_argument("--max-concurrency", type=int, default=64)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=600)
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Call the image edit endpoint for selected shots.",
    )
    parser.add_argument(
        "--review-only",
        action="store_true",
        help="Write prompt manifest and review page without generation.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace output directory and regenerate existing images.",
    )
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8")) if args.spec else default_spec()
    validate_spec(spec)
    shots = choose_shots(spec, args.selected)

    if args.output.exists() and args.force:
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "uploads").mkdir(exist_ok=True)
    (args.output / "data").mkdir(exist_ok=True)

    source = copy_base_asset(spec, args.output, args.base_asset)
    manifest = build_manifest(shots, mode=args.mode, spec=spec)
    job_file, manifest_file, spec_file = write_batch(args.output, spec, source, manifest)

    generated_count = 0
    if args.generate and not args.review_only:
        generated_count = generate_images(args, job_file, total=len(manifest))

    review_options = spec.get("review", {})
    review_file = review_renderer.build_review_html(args.output, manifest, review_options)
    contact_sheet = review_renderer.build_contact_sheet(args.output, manifest, review_options)
    handoff_json, handoff_markdown = write_handoff(
        args.output,
        spec,
        source,
        manifest,
        review_file,
        contact_sheet,
        mode=args.mode,
    )

    print(
        json.dumps(
            {
                "mode": args.mode,
                "shots": len(manifest),
                "generated": generated_count,
                "jobs": str(job_file.resolve()),
                "manifest": str(manifest_file.resolve()),
                "spec": str(spec_file.resolve()),
                "review_html": str(review_file.resolve()),
                "contact_sheet": str(contact_sheet.resolve()) if contact_sheet else None,
                "handoff_json": str(handoff_json.resolve()),
                "handoff_markdown": str(handoff_markdown.resolve()),
                "images_found": len(review_renderer.image_files(args.output)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
