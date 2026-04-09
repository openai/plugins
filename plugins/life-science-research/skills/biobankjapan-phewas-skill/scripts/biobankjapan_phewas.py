#!/usr/bin/env python3
"""biobankjapan-phewas

Fetch BioBank Japan PheWAS associations for one variant input.
Input JSON on stdin:
  - {"grch37":"10:114758349-C-T"}
  - {"grch38":"10:112998590:C:T","max_results":25}
  - {"rsid":"rs7903146","max_results":25,"save_raw":true}
  - "10:114758349-C-T"
Output JSON on stdout.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import requests
from variant_resolution import (
    VariantResolutionError,
    extract_variant_input,
    resolve_query_variant,
)

BBJ_BASE = "https://pheweb.jp"
USER_AGENT = "biobankjapan-phewas-skill/1.0 (+requests)"
DEFAULT_TIMEOUT_S = 20
DEFAULT_MAX_RESULTS = 10
SAFE_PATH_RE = re.compile(r"[^A-Za-z0-9._-]+")


def error(code: str, message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "warnings": warnings or [],
    }


def parse_input(payload: Any) -> tuple[str, str, int, bool, str | None, float]:
    if isinstance(payload, str):
        return "grch37", payload.strip(), DEFAULT_MAX_RESULTS, False, None, DEFAULT_TIMEOUT_S

    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON string or object.")

    input_type, variant = extract_variant_input(payload, default_build_key="grch37")

    max_results = payload.get("max_results", DEFAULT_MAX_RESULTS)
    if not isinstance(max_results, int) or max_results <= 0:
        raise ValueError("`max_results` must be a positive integer when provided.")

    save_raw = payload.get("save_raw", False)
    if not isinstance(save_raw, bool):
        raise ValueError("`save_raw` must be a boolean when provided.")

    raw_output_path = payload.get("raw_output_path")
    if raw_output_path is not None:
        if not isinstance(raw_output_path, str) or not raw_output_path.strip():
            raise ValueError("`raw_output_path` must be a non-empty string when provided.")
        raw_output_path = raw_output_path.strip()

    timeout_sec = payload.get("timeout_sec", DEFAULT_TIMEOUT_S)
    if not isinstance(timeout_sec, (int, float)) or timeout_sec <= 0:
        raise ValueError("`timeout_sec` must be a positive number when provided.")

    return input_type, variant, max_results, save_raw, raw_output_path, float(timeout_sec)


def fetch_bbj_variant(
    session: requests.Session,
    variant_str: str,
    timeout_sec: float,
) -> tuple[Any | None, int | None]:
    encoded = requests.utils.quote(variant_str, safe=":-")
    url = f"{BBJ_BASE}/api/variant/{encoded}"
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }

    response = session.get(url, headers=headers, timeout=timeout_sec)
    if response.status_code == 404:
        return None, 404
    response.raise_for_status()
    return response.json(), response.status_code


def extract_associations(data: Any) -> list[Any]:
    if data is None:
        return []
    if isinstance(data, dict) and isinstance(data.get("phenos"), list):
        return data["phenos"]
    if isinstance(data, list):
        return data
    return []


def resolve_raw_output_path(canonical_variant: str, raw_output_path: str | None) -> Path:
    if raw_output_path:
        return Path(raw_output_path).expanduser()

    safe_variant = SAFE_PATH_RE.sub("_", canonical_variant).strip("._") or "variant"
    return Path("/tmp") / f"biobankjapan-phewas-{safe_variant}.json"


def write_raw_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def main() -> int:
    warnings: list[str] = []

    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(json.dumps(error("invalid_json", f"Could not parse JSON input: {exc}")))
        return 2

    try:
        input_type, input_variant, max_results, save_raw, raw_output_path, timeout_sec = (
            parse_input(payload)
        )
    except ValueError as exc:
        sys.stdout.write(json.dumps(error("invalid_input", str(exc))))
        return 2

    try:
        resolution = resolve_query_variant(
            input_type=input_type,
            input_value=input_variant,
            target_build="GRCh37",
        )
        parsed = dict(resolution["query_variant"])
        warnings.extend(resolution["warnings"])
    except VariantResolutionError as exc:
        sys.stdout.write(json.dumps(error(exc.code, exc.message, exc.warnings)))
        return 1
    except requests.RequestException as exc:
        sys.stdout.write(json.dumps(error("network_error", f"Variant resolution failed: {exc}")))
        return 1

    session = requests.Session()
    try:
        data, status_code = fetch_bbj_variant(session, parsed["canonical"], timeout_sec)
    except requests.RequestException as exc:
        sys.stdout.write(json.dumps(error("network_error", f"BBJ request failed: {exc}")))
        return 1
    except ValueError as exc:
        sys.stdout.write(json.dumps(error("invalid_response", f"BBJ returned non-JSON: {exc}")))
        return 1

    variant_url = f"{BBJ_BASE}/variant/{parsed['canonical']}"
    saved_raw_output_path: str | None = None
    if save_raw and data is not None:
        raw_path = resolve_raw_output_path(parsed["canonical"], raw_output_path)
        try:
            write_raw_json(raw_path, data)
        except OSError as exc:
            sys.stdout.write(json.dumps(error("write_error", f"Could not write raw output: {exc}")))
            return 1
        saved_raw_output_path = str(raw_path)

    if status_code == 404:
        warnings.append("Variant not found in BioBank Japan PheWAS API (HTTP 404).")
        output = {
            "ok": True,
            "source": "biobank-japan",
            "input": resolution["input"],
            "query_variant": parsed,
            "max_results_applied": max_results,
            "association_count": 0,
            "association_count_total": 0,
            "truncated": False,
            "associations": [],
            "variant": None,
            "variant_url": variant_url,
            "raw_output_path": None,
            "warnings": warnings,
        }
        sys.stdout.write(json.dumps(output))
        return 0

    associations = extract_associations(data)
    total = len(associations)
    if total > max_results:
        associations = associations[:max_results]
    truncated = len(associations) < total

    variant_info = None
    if isinstance(data, dict):
        variant_info = {
            "chrom": data.get("chrom"),
            "pos": data.get("pos"),
            "ref": data.get("ref"),
            "alt": data.get("alt"),
            "rsids": data.get("rsids"),
            "variant_name": data.get("variant_name"),
            "nearest_genes": data.get("nearest_genes"),
        }

    output = {
        "ok": True,
        "source": "biobank-japan",
        "input": resolution["input"],
        "query_variant": parsed,
        "max_results_applied": max_results,
        "association_count": len(associations),
        "association_count_total": total,
        "truncated": truncated,
        "associations": associations,
        "variant": variant_info,
        "variant_url": variant_url,
        "raw_output_path": saved_raw_output_path,
        "warnings": warnings,
    }
    sys.stdout.write(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
