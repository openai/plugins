#!/usr/bin/env python3
"""gtex-eqtl

Fetch GTEx single-tissue eQTL associations for one variant input.
Input JSON on stdin:
  - {"grch38":"10-112998590-C-T"}
  - {"grch37":"10:114758349:C:T","max_results":100}
  - {"rsid":"rs7903146","max_results":100}
  - "10-112998590-C-T"
Output JSON on stdout.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import requests
from variant_resolution import (
    VariantResolutionError,
    extract_variant_input,
    resolve_query_variant,
)

GTEX_API = "https://gtexportal.org/api/v2"
USER_AGENT = "gtex-eqtl-skill/1.0 (+requests)"
DEFAULT_TIMEOUT_S = 25


def error(code: str, message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "warnings": warnings or [],
    }


def parse_input(payload: Any) -> tuple[str, str, int | None]:
    if isinstance(payload, str):
        return "grch38", payload.strip(), None

    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON string or object.")

    input_type, variant = extract_variant_input(payload, default_build_key="grch38")

    max_results = payload.get("max_results")
    if max_results is None:
        return input_type, variant, None

    if not isinstance(max_results, int) or max_results <= 0:
        raise ValueError("`max_results` must be a positive integer when provided.")
    return input_type, variant, max_results


def build_variant_id(parsed: dict[str, Any]) -> str:
    return f"chr{parsed['chr']}_{parsed['pos']}_{parsed['ref']}_{parsed['alt']}_b38"


def fetch_eqtls(variant_id: str) -> Any:
    encoded = requests.utils.quote(variant_id, safe="")
    url = f"{GTEX_API}/association/singleTissueEqtl?variantId={encoded}"
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    resp = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT_S)
    resp.raise_for_status()
    return resp.json()


def extract_rows(data: Any) -> list[Any]:
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return data["data"]
    if isinstance(data, list):
        return data
    return []


def main() -> int:
    warnings: list[str] = []

    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(json.dumps(error("invalid_json", f"Could not parse JSON input: {exc}")))
        return 2

    try:
        input_type, input_variant, max_results = parse_input(payload)
    except ValueError as exc:
        sys.stdout.write(json.dumps(error("invalid_input", str(exc))))
        return 2

    try:
        resolution = resolve_query_variant(
            input_type=input_type,
            input_value=input_variant,
            target_build="GRCh38",
        )
        parsed = dict(resolution["query_variant"])
        parsed["variant_id"] = build_variant_id(parsed)
        warnings.extend(resolution["warnings"])
    except VariantResolutionError as exc:
        sys.stdout.write(json.dumps(error(exc.code, exc.message, exc.warnings)))
        return 1
    except requests.RequestException as exc:
        sys.stdout.write(json.dumps(error("network_error", f"Variant resolution failed: {exc}")))
        return 1

    try:
        data = fetch_eqtls(parsed["variant_id"])
    except requests.RequestException as exc:
        sys.stdout.write(json.dumps(error("network_error", f"GTEx request failed: {exc}")))
        return 1
    except ValueError as exc:
        sys.stdout.write(json.dumps(error("invalid_response", f"GTEx returned non-JSON: {exc}")))
        return 1

    rows = extract_rows(data)
    total = len(rows)
    if max_results is not None and total > max_results:
        rows = rows[:max_results]
    truncated = len(rows) < total

    paging_info = data.get("paging_info") if isinstance(data, dict) else None

    output = {
        "ok": True,
        "source": "gtex-v2",
        "input": resolution["input"],
        "query_variant": parsed,
        "eqtl_count": len(rows),
        "eqtl_count_total": total,
        "truncated": truncated,
        "eqtls": rows,
        "paging_info": paging_info,
        "warnings": warnings,
    }
    sys.stdout.write(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
