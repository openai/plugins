#!/usr/bin/env python3
"""Compact Clinical Tables NCBI Gene helper for imported skills."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError as exc:  # pragma: no cover
    requests = None
    REQUESTS_IMPORT_ERROR = exc
else:
    REQUESTS_IMPORT_ERROR = None

ENDPOINT = "https://clinicaltables.nlm.nih.gov/api/ncbi_genes/v3/search"


def error(code: str, message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message}, "warnings": warnings or []}


def _compact(value: Any, max_items: int, max_depth: int) -> Any:
    if isinstance(value, str):
        return value if len(value) <= 240 else value[:240] + "..."
    if max_depth <= 0:
        if isinstance(value, (dict, list)):
            return "..."
        return value
    if isinstance(value, list):
        out = [_compact(item, max_items, max_depth - 1) for item in value[:max_items]]
        if len(value) > max_items:
            out.append(f"... (+{len(value) - max_items} more)")
        return out
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        items = list(value.items())
        for key, item in items[:max_items]:
            out[str(key)] = _compact(item, max_items, max_depth - 1)
        if len(items) > max_items:
            out["_truncated_keys"] = len(items) - max_items
        return out
    return value


def parse_input(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Input must be one JSON object.")
    terms = payload.get("terms")
    if not isinstance(terms, str) or not terms.strip():
        raise ValueError("`terms` is required.")
    params = payload.get("params") or {}
    if not isinstance(params, dict):
        raise ValueError("`params` must be an object.")
    max_items = payload.get("max_items", 5)
    max_depth = payload.get("max_depth", 3)
    timeout_sec = payload.get("timeout_sec", 30)
    save_raw = payload.get("save_raw", False)
    for name, value in {
        "max_items": max_items,
        "max_depth": max_depth,
        "timeout_sec": timeout_sec,
    }.items():
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"`{name}` must be a positive integer.")
    if not isinstance(save_raw, bool):
        raise ValueError("`save_raw` must be a boolean.")
    raw_output_path = payload.get("raw_output_path")
    if raw_output_path is not None and (
        not isinstance(raw_output_path, str) or not raw_output_path.strip()
    ):
        raise ValueError("`raw_output_path` must be a non-empty string.")
    return {
        "terms": terms.strip(),
        "params": params,
        "max_items": max_items,
        "max_depth": max_depth,
        "timeout_sec": timeout_sec,
        "save_raw": save_raw,
        "raw_output_path": raw_output_path.strip() if isinstance(raw_output_path, str) else None,
    }


def execute(payload: Any) -> dict[str, Any]:
    if requests is None:
        return error("missing_dependency", f"`requests` is required: {REQUESTS_IMPORT_ERROR}")
    try:
        config = parse_input(payload)
        params = {"terms": config["terms"], "count": config["max_items"]}
        params.update(config["params"])
        response = requests.get(ENDPOINT, params=params, timeout=config["timeout_sec"])
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or len(data) < 4:
            return error(
                "invalid_response", "NCBI Gene response did not match the expected list shape."
            )
        raw_output_path = None
        if config["save_raw"]:
            raw_text = json.dumps(data, indent=2)
            path = Path(config["raw_output_path"] or "/tmp/ncbi-gene-search.json")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(raw_text, encoding="utf-8")
            raw_output_path = str(path)
        total = data[0]
        codes = data[1] if isinstance(data[1], list) else []
        extra_fields = data[2]
        display_rows = data[3] if isinstance(data[3], list) else []
        return {
            "ok": True,
            "source": "ncbi-gene-clinicaltables",
            "terms": config["terms"],
            "total": total,
            "record_count_returned": len(display_rows[: config["max_items"]]),
            "record_count_available": len(display_rows),
            "truncated": len(display_rows) < total if isinstance(total, int) else False,
            "codes": codes[: config["max_items"]],
            "display_rows": _compact(
                display_rows[: config["max_items"]], config["max_items"], config["max_depth"]
            ),
            "extra_fields": _compact(extra_fields, config["max_items"], config["max_depth"]),
            "raw_output_path": raw_output_path,
            "warnings": [],
        }
    except ValueError as exc:
        return error("invalid_input", str(exc))
    except requests.RequestException as exc:
        return error("network_error", f"Request failed: {exc}")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(json.dumps(error("invalid_json", f"Could not parse JSON input: {exc}")))
        return 2
    output = execute(payload)
    sys.stdout.write(json.dumps(output))
    return 0 if output.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
