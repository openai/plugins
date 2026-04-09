#!/usr/bin/env python3
"""Compact ClinicalTrials.gov v2 helper for ChatGPT-imported skills."""

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

BASE_URL = "https://clinicaltrials.gov/api/v2"
PATHS = {
    "studies": "/studies",
    "metadata": "/studies/metadata",
    "search_areas": "/studies/search-areas",
    "enums": "/studies/enums",
    "stats_size": "/stats/size",
    "field_values": "/stats/field/values",
    "field_sizes": "/stats/field/sizes",
}


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


def _require_int(name: str, value: Any, default: int) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"`{name}` must be a positive integer.")
    return value


def _require_bool(name: str, value: Any, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"`{name}` must be a boolean.")
    return value


def parse_input(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Input must be one JSON object.")
    action = payload.get("action", "studies")
    if action not in set(PATHS) | {"request"}:
        raise ValueError(
            "`action` must be one of: studies, metadata, search_areas, enums, stats_size, field_values, field_sizes, request."
        )
    params = payload.get("params") or {}
    if not isinstance(params, dict):
        raise ValueError("`params` must be an object.")
    path = payload.get("path")
    if action == "request":
        if not isinstance(path, str) or not path.strip():
            raise ValueError("`path` is required when `action=request`.")
    return {
        "action": action,
        "path": path.strip() if isinstance(path, str) else PATHS.get(action),
        "params": params,
        "max_items": _require_int("max_items", payload.get("max_items"), 10),
        "max_depth": _require_int("max_depth", payload.get("max_depth"), 3),
        "max_pages": _require_int("max_pages", payload.get("max_pages"), 1),
        "timeout_sec": _require_int("timeout_sec", payload.get("timeout_sec"), 30),
        "save_raw": _require_bool("save_raw", payload.get("save_raw"), False),
        "raw_output_path": payload.get("raw_output_path"),
    }


def _save_raw(data: Any, raw_output_path: str | None) -> str:
    path = Path(raw_output_path or "/tmp/clinicaltrials-response.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return str(path)


def execute(payload: Any) -> dict[str, Any]:
    if requests is None:
        return error("missing_dependency", f"`requests` is required: {REQUESTS_IMPORT_ERROR}")
    config = parse_input(payload)
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    try:
        if config["action"] == "studies":
            next_page_token = None
            if isinstance(config["params"].get("pageToken"), str):
                next_page_token = config["params"]["pageToken"]
            studies: list[Any] = []
            pages: list[dict[str, Any]] = []
            total_count: int | None = None
            pages_fetched = 0
            for _ in range(config["max_pages"]):
                params = dict(config["params"])
                if next_page_token:
                    params["pageToken"] = next_page_token
                response = session.get(
                    BASE_URL + config["path"], params=params, timeout=config["timeout_sec"]
                )
                response.raise_for_status()
                page = response.json()
                pages.append(page)
                pages_fetched += 1
                page_studies = page.get("studies") if isinstance(page.get("studies"), list) else []
                studies.extend(page_studies)
                if isinstance(page.get("totalCount"), int):
                    total_count = page["totalCount"]
                next_page_token = (
                    page.get("nextPageToken")
                    if isinstance(page.get("nextPageToken"), str)
                    else None
                )
                if not next_page_token:
                    break
            raw_output_path = (
                _save_raw(pages if len(pages) > 1 else pages[0], config["raw_output_path"])
                if config["save_raw"] and pages
                else None
            )
            available = total_count if isinstance(total_count, int) else len(studies)
            return {
                "ok": True,
                "source": "clinicaltrials-v2",
                "action": "studies",
                "pages_fetched": pages_fetched,
                "next_page_token": next_page_token,
                "record_count_returned": min(len(studies), config["max_items"]),
                "record_count_available": available,
                "truncated": len(studies) > config["max_items"] or next_page_token is not None,
                "records": _compact(
                    studies[: config["max_items"]], config["max_items"], config["max_depth"]
                ),
                "raw_output_path": raw_output_path,
                "warnings": [],
            }

        response = session.get(
            BASE_URL + config["path"], params=config["params"], timeout=config["timeout_sec"]
        )
        response.raise_for_status()
        data = response.json()
        raw_output_path = _save_raw(data, config["raw_output_path"]) if config["save_raw"] else None
        target = data
        top_keys = list(data)[: config["max_items"]] if isinstance(data, dict) else None
        if isinstance(data, dict):
            for key in ("studies", "fields", "areas", "enums", "values", "sizes"):
                value = data.get(key)
                if isinstance(value, list):
                    target = value
                    break
        output = {
            "ok": True,
            "source": "clinicaltrials-v2",
            "action": config["action"],
            "raw_output_path": raw_output_path,
            "warnings": [],
        }
        if isinstance(target, list):
            output.update(
                {
                    "record_count_returned": min(len(target), config["max_items"]),
                    "record_count_available": len(target),
                    "truncated": len(target) > config["max_items"],
                    "records": _compact(
                        target[: config["max_items"]], config["max_items"], config["max_depth"]
                    ),
                }
            )
        else:
            output["summary"] = _compact(target, config["max_items"], config["max_depth"])
            output["top_keys"] = top_keys
        return output
    except ValueError as exc:
        return error("invalid_response", str(exc))
    except requests.RequestException as exc:
        return error("network_error", f"Request failed: {exc}")
    finally:
        session.close()


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
