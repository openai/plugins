#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PLUGIN_ROOT = SCRIPT_DIR.parents[4]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from scripts import review_renderer  # noqa: E402

DEFAULT_CORE_PACK = (
    PLUGIN_ROOT / "assets" / "offer-library" / "packs" / "cross-industry-product-ad-archetypes.json"
)
SUPPLEMENTAL_PACKS_DIR = SKILL_DIR / "references" / "packs"
DEFAULT_IMAGE_GENERATION_RUNNER = None
PROMPT_SCALE_DEFAULT_PACKS = set()


def slugify(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "offer"


def read_offer_brief(args):
    parts = []
    offer_brief = args.offer_brief
    offer_brief_file = args.offer_brief_file
    if offer_brief:
        parts.append(offer_brief.strip())
    if offer_brief_file:
        file_text = Path(offer_brief_file).read_text().strip()
        lines = file_text.splitlines()
        if lines and lines[0].strip().lower() == args.offer_name.strip().lower():
            file_text = "\n".join(lines[1:]).strip()
        parts.append(file_text)
    brief = "\n".join(part for part in parts if part)
    if not brief:
        raise SystemExit("Provide --offer-brief or --offer-brief-file.")
    return brief


def use_case_for(category):
    if "Text" in category or "Research" in category:
        return "infographic-diagram"
    if "Paid" in category or "Product" in category:
        return "product-mockup"
    return "stylized-concept"


def existing_default_family_map():
    return DEFAULT_CORE_PACK


def read_json_file(path, label):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"{label} not found: {path}")
    return json.loads(path.read_text())


def normalize_pack(pack, fallback_id=None, fallback_title=None):
    pack = dict(pack)
    if "families" not in pack and isinstance(pack.get("archetypes"), list):
        pack["families"] = pack["archetypes"]
    pack["id"] = pack.get("id") or fallback_id or "pack"
    pack["title"] = pack.get("title") or fallback_title or pack["id"].replace("-", " ").title()
    if not isinstance(pack.get("families"), list) or not pack["families"]:
        raise SystemExit(f"Pack '{pack['id']}' must include families.")
    return pack


def family_map_for_pack(pack):
    return {
        "version": pack.get("version", 1),
        "routes": pack.get("routes", []),
        "families": pack["families"],
        "review": pack.get("review", {}),
    }


def load_pack_from_file(path, pack_id=None, label="pack"):
    data = read_json_file(path, label)
    if isinstance(data.get("packs"), list):
        if pack_id:
            pack = next((item for item in data["packs"] if item.get("id") == pack_id), None)
            if not pack:
                available = ", ".join(item.get("id", "<missing-id>") for item in data["packs"])
                raise SystemExit(
                    f"Pack '{pack_id}' not found in {path}. Available packs: {available}"
                )
        elif len(data["packs"]) == 1:
            pack = data["packs"][0]
        else:
            available = ", ".join(item.get("id", "<missing-id>") for item in data["packs"])
            raise SystemExit(f"Choose --pack for {path}. Available packs: {available}")
        pack = {**pack, "version": pack.get("version", data.get("version", 1))}
        return normalize_pack(pack, fallback_id=pack_id)
    return normalize_pack(data, fallback_id=pack_id)


def load_checked_in_packs():
    if not SUPPLEMENTAL_PACKS_DIR.exists():
        return []
    packs = []
    for path in sorted(SUPPLEMENTAL_PACKS_DIR.glob("*.json")):
        packs.append(load_pack_from_file(path, path.stem, "supplemental pack"))
    return packs


def load_checked_in_pack(pack_id):
    return next((pack for pack in load_checked_in_packs() if pack["id"] == pack_id), None)


def load_scale_map(args):
    if args.pack == "core":
        core_pack = load_pack_from_file(args.family_map, label="core offer library")
        return family_map_for_pack(core_pack), {
            **core_pack,
            "id": "core",
            "title": "Core Offer Explorer",
        }

    supplemental_pack = load_checked_in_pack(args.pack)
    if supplemental_pack:
        return family_map_for_pack(supplemental_pack), supplemental_pack

    if not args.expansion_map:
        supplemental_ids = [item["id"] for item in load_checked_in_packs()]
        available = ", ".join(["core"] + supplemental_ids)
        raise SystemExit(
            f"Unknown pack '{args.pack}'. Available checked-in packs: {available}. "
            "Pass --expansion-map with a packaged library file to use another pack."
        )

    pack = load_pack_from_file(args.expansion_map, args.pack, "expansion pack")
    return family_map_for_pack(pack), pack


def default_scale_for_pack(pack_id):
    if pack_id in PROMPT_SCALE_DEFAULT_PACKS:
        return "prompt"
    return "family"


def resolve_scale(args, pack):
    return args.scale or default_scale_for_pack(pack["id"])


def subject_labels(subject_kind):
    normalized = (subject_kind or "product").strip().lower()
    labels = {
        "product": {
            "anchor": "Product anchor",
            "facts": "Product facts to preserve",
            "noun": "product",
            "recognizable": "keep the product recognizable",
            "category": "brand or product category",
        },
        "service": {
            "anchor": "Service anchor",
            "facts": "Service facts to preserve",
            "noun": "service",
            "recognizable": "keep the service moment recognizable",
            "category": "brand, service, or category",
        },
        "venue": {
            "anchor": "Venue anchor",
            "facts": "Venue and experience facts to preserve",
            "noun": "venue experience",
            "recognizable": "keep the venue, service style, and dining occasion recognizable",
            "category": "brand, venue, restaurant category, or unsupported offer",
        },
        "experience": {
            "anchor": "Experience anchor",
            "facts": "Experience facts to preserve",
            "noun": "experience",
            "recognizable": "keep the experience recognizable",
            "category": "brand, experience, or category",
        },
        "digital-product": {
            "anchor": "Digital product anchor",
            "facts": "Product UI and workflow facts to preserve",
            "noun": "digital product",
            "recognizable": "keep the product UI, workflow, and product-proof cues recognizable",
            "category": "digital product, app, SaaS workflow, or UI category",
            "guidance": [
                "Digital product proof: make the product UI, workflow state, and interface feedback the visual evidence.",
                "UI fidelity: use sparse, plausible labels and placeholder data only; do not invent real customer names, private data, or unsupported metrics.",
                "Do not drift into generic abstract SaaS imagery when UI/product proof is requested.",
            ],
        },
    }
    return labels.get(normalized, labels["product"])


def prompt_for(offer_name, offer_brief, family, route=None, subject_kind="product"):
    labels = subject_labels(subject_kind)
    offer_facts = offer_brief.rstrip(".")
    lines = [
        f"Create one polished business visual review image for the prompt family: {family['title']}.",
        f"{labels['anchor']}: {offer_name}.",
        f"{labels['facts']}: {offer_facts}.",
        f"The visual must be clearly about this {labels['noun']} and should not introduce another {labels['category']}.",
        *(
            [f"Scene archetype: {family['sceneArchetype']}."]
            if family.get("sceneArchetype")
            else []
        ),
        *(
            [f"Reusable placeholders: {', '.join(family['placeholders'])}."]
            if family.get("placeholders")
            else []
        ),
        f"Family intent: {family['summary']}",
        f"Business goal: {family['businessGoal']}.",
        f"Scene: {family['scene']}.",
        *([f"Ad format: {family['format']}."] if family.get("format") else []),
        *([f"Human presence: {family['humanPresence']}."] if family.get("humanPresence") else []),
        *([f"Rendering mode: {family['renderingMode']}."] if family.get("renderingMode") else []),
        *([f"Channel fit: {', '.join(family['channelFit'])}."] if family.get("channelFit") else []),
        *([f"Scene shape: {family['sceneShape']}."] if family.get("sceneShape") else []),
        *(
            [f"Subject placement: {family['subjectPlacement']}."]
            if family.get("subjectPlacement")
            else []
        ),
        *(
            [f"Subject slot: {format_subject_slot(family['subjectSlot'])}."]
            if family.get("subjectSlot")
            else []
        ),
        *(labels.get("guidance") or []),
        f"Focus: {family['focus']}.",
        f"Decision being supported: {family['decision']}.",
    ]
    prompt_template = family.get("promptTemplate") or family.get("templatePrompt")
    if prompt_template:
        lines.append(
            "Reusable prompt pattern: "
            + instantiate_prompt_template(prompt_template, offer_name, labels, offer_facts)
        )
    if family.get("copyRules"):
        lines.append(f"Copy rules: {format_copy_rules(family['copyRules'])}.")
    if route:
        lines.extend(
            [
                f"Creative route: {route['name']} ({route['channel']}).",
                f"Route style: {route['style']}.",
                f"Route composition: {route['composition']}.",
                f"Route lighting: {route['lighting']}.",
                f"Route emphasis: {route['emphasis']}.",
            ]
        )
    lines.extend(
        [
            f"Include: {', '.join(family['elements'])}.",
            (
                "Constraints: "
                + "; ".join(family["constraints"])
                + "; keep text sparse; use short labels, UI placeholder blocks, or visual markers "
                f"only when needed; {labels['recognizable']}."
            ),
            (
                f"Avoid: {family['avoid']}; fake endorsements; unsupported claims; misspelled "
                "large text; watermarks; clutter; other brands."
            ),
        ]
    )
    return "\n".join(lines)


def format_copy_rules(copy_rules):
    if not isinstance(copy_rules, dict):
        return str(copy_rules)
    parts = []
    for key, value in copy_rules.items():
        if value:
            parts.append(f"{key}: {value}")
    return "; ".join(parts)


def instantiate_prompt_template(template, offer_name, labels, offer_facts):
    replacements = {
        "[SUBJECT_REFERENCE]": offer_name,
        "[PRODUCT_REFERENCE]": offer_name,
        "[SUBJECT_KIND]": labels["noun"],
        "[PRODUCT_CATEGORY]": labels["category"],
        "[AUDIENCE]": "the target audience described in the product facts",
        "[PRIMARY_BENEFIT]": "the approved primary benefit in the product facts",
        "[BRAND_PALETTE]": "the supplied brand palette and material cues",
        "[HEADLINE]": "the exact supplied headline in the product facts, if any",
        "[CTA_OR_CONTACT]": "the exact supplied CTA or contact detail in the product facts, or no CTA if none is supplied",
        "[CHANNEL]": "the requested channel or review context",
        "[AVOID]": "the avoid list and fidelity risks in the product facts",
        "[PRIMARY_ENVIRONMENT]": "a category-appropriate environment from the product facts",
        "[SURFACE_OR_BASE]": "a realistic surface or base that supports the product",
        "[LIGHTING_STYLE]": "a lighting style that supports the selected ad family",
        "[SUPPORTING_CUES]": "truthful supporting cues from the product facts",
        "[MOOD]": "the mood implied by the selected ad family and product facts",
        "[COPY_SPACE]": "clean copy space when the ad family calls for it",
    }
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    if offer_facts:
        rendered += f" Product facts: {offer_facts}."
    return rendered


def format_subject_slot(slot):
    if not isinstance(slot, dict):
        return str(slot)
    parts = []
    for key in (
        "slotType",
        "placement",
        "scale",
        "interaction",
        "fallbackIfService",
        "fallbackIfDigital",
        "preserve",
    ):
        value = slot.get(key)
        if not value:
            continue
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        parts.append(f"{key}: {value}")
    return "; ".join(parts)


def build_jobs(offer_name, offer_brief, family_map, size, quality, scale, subject_kind="product"):
    jobs = []
    manifest = []
    routes = family_map.get("routes") or []
    if scale == "prompt" and not routes:
        raise SystemExit("Prompt run requires routes in the family map.")

    entries = []
    if scale == "family":
        entries = [(family, None) for family in family_map["families"]]
    else:
        for family in family_map["families"]:
            for route in routes:
                entries.append((family, route))

    width = 3 if len(entries) >= 100 else 2
    for index, (family, route) in enumerate(entries, start=1):
        suffix = family["id"]
        title = family["title"]
        if route:
            suffix = f"{suffix}-{route['code'].lower()}-{slugify(route['name'])}"
            title = f"{title} / {route['name']}"
        out_name = f"{index:0{width}d}-{suffix}.png"
        prompt = prompt_for(offer_name, offer_brief, family, route, subject_kind)
        job_size = family.get("size") or size
        jobs.append(
            {
                "id": f"{index:0{width}d}-{suffix}",
                "prompt": prompt,
                "use_case": use_case_for(family["category"]),
                "size": job_size,
                "quality": quality,
                "output_format": "png",
                "out": out_name,
                "metadata": {
                    "id": family["id"],
                    "title": family["title"],
                    "category": family["category"],
                    "size": job_size,
                    "route": route["code"] if route else None,
                    "route_name": route["name"] if route else None,
                },
            }
        )
        manifest.append(
            {
                "index": index,
                "id": family["id"],
                "title": title,
                "familyTitle": family["title"],
                "category": family["category"],
                "size": job_size,
                "route": route["code"] if route else None,
                "routeName": route["name"] if route else None,
                "output": out_name,
                "prompt": prompt,
            }
        )
    return jobs, manifest


def write_batch(out_dir, jobs, manifest, offer_name, offer_brief):
    out_dir.mkdir(parents=True, exist_ok=True)
    job_file = out_dir / "jobs.jsonl"
    manifest_file = out_dir / "prompts-manifest.json"
    brief_file = out_dir / "offer-brief.txt"
    job_file.write_text("\n".join(json.dumps(job) for job in jobs) + "\n")
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n")
    brief_file.write_text(f"{offer_name}\n\n{offer_brief}\n")
    return job_file, manifest_file, brief_file


def write_scale_metadata(out_dir, args, pack, family_map):
    metadata_file = out_dir / "visual-explorer-metadata.json"
    metadata = {
        "scale": args.scale,
        "pack": pack["id"],
        "packTitle": pack["title"],
        "subjectKind": args.subject_kind,
        "families": len(family_map["families"]),
        "routes": len(family_map.get("routes") or []),
        "items": len(family_map["families"])
        * (len(family_map.get("routes") or []) if args.scale == "prompt" else 1),
    }
    for key in ("summary", "whenToUse", "requiredInputs", "riskGates", "review"):
        if pack.get(key):
            metadata[key] = pack[key]
    metadata_file.write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata_file


def run_imagegen(args, job_file, out_dir):
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
        str(out_dir),
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


def image_files(out_dir):
    return review_renderer.image_files(out_dir)


def build_review_html(out_dir, manifest, review_options=None):
    return review_renderer.build_review_html(out_dir, manifest, review_options)


def build_contact_sheet(out_dir, manifest, review_options=None):
    return review_renderer.build_contact_sheet(out_dir, manifest, review_options)


def main():
    parser = argparse.ArgumentParser(description="Build an offer explorer run.")
    parser.add_argument("--offer-name")
    parser.add_argument("--offer-brief")
    parser.add_argument("--offer-brief-file")
    parser.add_argument(
        "--subject-kind",
        choices=["product", "service", "venue", "experience", "digital-product"],
        default="product",
        help="What kind of subject the explorer should preserve.",
    )
    parser.add_argument("--out-dir")
    parser.add_argument(
        "--scale",
        choices=["family", "prompt"],
        default=None,
        help=(
            "family = one item per prompt family; prompt = every family crossed with the route prompts. "
            "Defaults to prompt for hero/web modules and family otherwise."
        ),
    )
    parser.add_argument(
        "--pack",
        default="core",
        help="Prompt pack id. Use 'core' for the default offer explorer run.",
    )
    parser.add_argument("--family-map", type=Path, default=existing_default_family_map())
    parser.add_argument("--expansion-map", type=Path)
    parser.add_argument(
        "--image-generation-runner", type=Path, default=DEFAULT_IMAGE_GENERATION_RUNNER
    )
    parser.add_argument("--workspace", type=Path, default=PLUGIN_ROOT.parents[1])
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="medium")
    parser.add_argument("--max-concurrency", type=int, default=64)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=600)
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--review-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.offer_name:
        raise SystemExit("Provide --offer-name.")

    offer_brief = read_offer_brief(args)
    family_map, pack = load_scale_map(args)
    args.scale = resolve_scale(args, pack)
    if args.scale == "prompt" and args.pack == "core":
        default_suffix = "100-offer-explorer"
    elif args.scale == "prompt":
        default_suffix = "offer-explorer"
    else:
        default_suffix = "offer-explorer"
    if args.pack == "core":
        default_out = f"outputs/imagegen/{slugify(args.offer_name)}-{default_suffix}"
    else:
        default_out = (
            f"outputs/imagegen/{slugify(args.offer_name)}-{slugify(args.pack)}-{default_suffix}"
        )
    out_dir = Path(args.out_dir or default_out)
    jobs, manifest = build_jobs(
        args.offer_name,
        offer_brief,
        family_map,
        args.size,
        args.quality,
        args.scale,
        args.subject_kind,
    )
    job_file, manifest_file, brief_file = write_batch(
        out_dir, jobs, manifest, args.offer_name, offer_brief
    )
    metadata_file = write_scale_metadata(out_dir, args, pack, family_map)

    if args.generate and not args.review_only:
        run_imagegen(args, job_file, out_dir)

    review_options = pack.get("review", {})
    review_file = build_review_html(out_dir, manifest, review_options)
    contact_sheet = build_contact_sheet(out_dir, manifest, review_options)
    print(
        json.dumps(
            {
                "scale": args.scale,
                "pack": pack["id"],
                "packTitle": pack["title"],
                "subjectKind": args.subject_kind,
                "families": len(family_map["families"]),
                "items": len(manifest),
                "jobs": str(job_file.resolve()),
                "manifest": str(manifest_file.resolve()),
                "metadata": str(metadata_file.resolve()),
                "offer_brief": str(brief_file.resolve()),
                "review_html": str(review_file.resolve()),
                "contact_sheet": str(contact_sheet.resolve()) if contact_sheet else None,
                "images_found": len(image_files(out_dir)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
