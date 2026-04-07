#!/usr/bin/env python3
"""Compact Open Targets GraphQL client for ChatGPT-imported skills."""

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

ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"


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
    variables = payload.get("variables") or {}
    if not isinstance(variables, dict):
        raise ValueError("`variables` must be an object.")
    save_raw = payload.get("save_raw", False)
    if not isinstance(save_raw, bool):
        raise ValueError("`save_raw` must be a boolean.")
    raw_output_path = payload.get("raw_output_path")
    if raw_output_path is not None and (
        not isinstance(raw_output_path, str) or not raw_output_path.strip()
    ):
        raise ValueError("`raw_output_path` must be a non-empty string.")
    for key in ("max_items", "max_depth", "timeout_sec"):
        value = payload.get(key, 5 if key == "max_items" else 3 if key == "max_depth" else 60)
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"`{key}` must be a positive integer.")
        payload[key] = value
    query_text = (
        query.strip() if isinstance(query, str) else Path(query_path).read_text(encoding="utf-8")
    )
    return {
        "query": query_text,
        "variables": variables,
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
    try:
        response = requests.post(
            ENDPOINT,
            json={"query": config["query"], "variables": config["variables"]},
            timeout=config["timeout_sec"],
        )
        response.raise_for_status()
        data = response.json()
    except ValueError as exc:
        return error("invalid_response", str(exc))
    except requests.RequestException as exc:
        return error("network_error", f"GraphQL request failed: {exc}")

    raw_output_path = None
    if config["save_raw"]:
        raw_text = json.dumps(data, indent=2)
        path = Path(config["raw_output_path"] or "/tmp/opentargets-graphql.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(raw_text, encoding="utf-8")
        raw_output_path = str(path)

    if "errors" in data:
        return error(
            "graphql_error",
            json.dumps(data["errors"])[:500],
            warnings=[f"raw_output_path={raw_output_path}"] if raw_output_path else [],
        )

    payload_data = data.get("data")
    if not isinstance(payload_data, dict):
        return error("invalid_response", "GraphQL response did not include a `data` object.")

    return {
        "ok": True,
        "source": "opentargets-graphql",
        "top_keys": list(payload_data)[: config["max_items"]],
        "summary": _compact(payload_data, config["max_items"], config["max_depth"]),
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
