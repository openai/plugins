#!/usr/bin/env python3
"""Compact Bgee SPARQL client for ChatGPT-imported skills."""

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

ENDPOINT = "https://www.bgee.org/sparql/"


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
    query = payload.get("query")
    query_path = payload.get("query_path")
    if query is None and query_path is None:
        raise ValueError("Provide `query` or `query_path`.")
    if query is not None and (not isinstance(query, str) or not query.strip()):
        raise ValueError("`query` must be a non-empty string.")
    if query_path is not None and (not isinstance(query_path, str) or not query_path.strip()):
        raise ValueError("`query_path` must be a non-empty string.")
    method = str(payload.get("method", "GET")).upper()
    if method not in {"GET", "POST"}:
        raise ValueError("`method` must be GET or POST.")
    params = payload.get("params") or {}
    if not isinstance(params, dict):
        raise ValueError("`params` must be an object.")
    response_format = str(payload.get("response_format", "auto")).lower()
    if response_format not in {"auto", "json", "text"}:
        raise ValueError("`response_format` must be auto, json, or text.")
    save_raw = payload.get("save_raw", False)
    if not isinstance(save_raw, bool):
        raise ValueError("`save_raw` must be a boolean.")
    raw_output_path = payload.get("raw_output_path")
    if raw_output_path is not None and (
        not isinstance(raw_output_path, str) or not raw_output_path.strip()
    ):
        raise ValueError("`raw_output_path` must be a non-empty string.")
    for key in ("max_items", "max_depth", "timeout_sec"):
        default = 5 if key == "max_items" else 3 if key == "max_depth" else 60
        value = payload.get(key, default)
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"`{key}` must be a positive integer.")
        payload[key] = value
    query_text = (
        query.strip() if isinstance(query, str) else Path(query_path).read_text(encoding="utf-8")
    )
    return {
        "query": query_text,
        "method": method,
        "params": params,
        "response_format": response_format,
        "max_items": payload["max_items"],
        "max_depth": payload["max_depth"],
        "timeout_sec": payload["timeout_sec"],
        "save_raw": save_raw,
        "raw_output_path": raw_output_path.strip() if isinstance(raw_output_path, str) else None,
    }


def execute(payload: Any) -> dict[str, Any]:
    if requests is None:
        return error("missing_dependency", f"`requests` is required: {REQUESTS_IMPORT_ERROR}")
    config = parse_input(payload)
    headers = {
        "Accept": "application/sparql-results+json, application/json;q=0.9, text/tab-separated-values;q=0.8, text/plain;q=0.5"
    }
    try:
        if config["method"] == "GET":
            params = dict(config["params"])
            params.setdefault("query", config["query"])
            params.setdefault("format", "json")
            response = requests.get(
                ENDPOINT, params=params, headers=headers, timeout=config["timeout_sec"]
            )
        else:
            response = requests.post(
                ENDPOINT,
                data={"query": config["query"], **config["params"]},
                headers=headers,
                timeout=config["timeout_sec"],
            )
        response.raise_for_status()
    except requests.RequestException as exc:
        return error("network_error", f"SPARQL request failed: {exc}")

    raw_output_path = None
    if config["save_raw"]:
        suffix = "json" if "json" in (response.headers.get("content-type") or "").lower() else "txt"
        path = Path(config["raw_output_path"] or f"/tmp/bgee-sparql.{suffix}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(response.text, encoding="utf-8")
        raw_output_path = str(path)

    content_type = (response.headers.get("content-type") or "").lower()
    wants_text = config["response_format"] == "text"
    auto_json = not wants_text and (
        "json" in content_type or response.text.lstrip().startswith("{")
    )
    if not auto_json and config["response_format"] != "json":
        text_head = None if raw_output_path else response.text[:800]
        return {
            "ok": True,
            "source": "bgee-sparql",
            "content_type": content_type,
            "text_head": text_head,
            "text_head_truncated": False if raw_output_path else len(response.text) > 800,
            "raw_output_path": raw_output_path,
            "warnings": [],
        }

    try:
        data = response.json()
    except ValueError as exc:
        return error("invalid_response", str(exc))

    if "boolean" in data:
        summary: Any = {"boolean": data["boolean"]}
        top_keys = ["boolean"]
    else:
        results = data.get("results", {})
        bindings = results.get("bindings", []) if isinstance(results, dict) else []
        summary = {
            "head": data.get("head", {}),
            "record_count_returned": min(len(bindings), config["max_items"]),
            "record_count_available": len(bindings),
            "truncated": len(bindings) > config["max_items"],
            "records": _compact(
                bindings[: config["max_items"]], config["max_items"], config["max_depth"]
            ),
        }
        top_keys = list(summary)[: config["max_items"]]

    return {
        "ok": True,
        "source": "bgee-sparql",
        "top_keys": top_keys,
        "summary": _compact(summary, config["max_items"], config["max_depth"]),
        "raw_output_path": raw_output_path,
        "warnings": [],
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(json.dumps(error("invalid_json", f"Could not parse JSON input: {exc}")))
        return 2
    try:
        output = execute(payload)
    except ValueError as exc:
        output = error("invalid_input", str(exc))
        code = 2
    else:
        code = 0 if output.get("ok") else 1
    sys.stdout.write(json.dumps(output))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
