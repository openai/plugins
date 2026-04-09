#!/usr/bin/env python3
"""Compact NCBI Entrez E-Utilities helper for imported skills."""

from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError as exc:  # pragma: no cover
    requests = None
    REQUESTS_IMPORT_ERROR = exc
else:
    REQUESTS_IMPORT_ERROR = None

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def error(code: str, message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message}, "warnings": warnings or []}


def _require_str(name: str, value: Any, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"`{name}` is required.")
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"`{name}` must be a non-empty string.")
    return value.strip()


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


def _require_object(name: str, value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"`{name}` must be an object.")
    return value


def _get_by_path(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if isinstance(current, list):
            if not part.isdigit():
                raise ValueError(f"`record_path` segment {part!r} must be a list index.")
            index = int(part)
            if index >= len(current):
                raise ValueError(f"`record_path` index {index} is out of range.")
            current = current[index]
        elif isinstance(current, dict):
            if part not in current:
                raise ValueError(f"`record_path` key {part!r} was not present in the response.")
            current = current[part]
        else:
            raise ValueError(f"`record_path` segment {part!r} could not be applied.")
    return current


def _infer_target(data: Any) -> tuple[str | None, Any]:
    if isinstance(data, list):
        return "$", data
    if isinstance(data, dict):
        for key in ("result", "results", "records", "uids", "documents"):
            value = data.get(key)
            if isinstance(value, list):
                return key, value
        if "esearchresult" in data:
            result = data["esearchresult"]
            if isinstance(result, dict) and isinstance(result.get("idlist"), list):
                return "esearchresult.idlist", result["idlist"]
    return None, data


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


def _xml_to_simple(elem: ET.Element, max_items: int, max_depth: int) -> Any:
    children = list(elem)
    text = (elem.text or "").strip()
    if not children:
        return text
    if max_depth <= 0:
        return "..."
    grouped: dict[str, Any] = {}
    for child in children[:max_items]:
        tag = child.tag.split("}", 1)[-1]
        value = _xml_to_simple(child, max_items, max_depth - 1)
        if tag in grouped:
            current = grouped[tag]
            if not isinstance(current, list):
                grouped[tag] = [current]
            grouped[tag].append(value)
        else:
            grouped[tag] = value
    if len(children) > max_items:
        grouped["_truncated_children"] = len(children) - max_items
    if text:
        grouped["_text"] = text
    return grouped


def _save_raw_text(raw_text: str, raw_output_path: str | None, suffix: str) -> str:
    path = Path(raw_output_path or f"/tmp/ncbi-entrez.{suffix}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw_text, encoding="utf-8")
    return str(path)


def parse_input(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Input must be one JSON object.")
    response_format = (
        _require_str("response_format", payload.get("response_format")) or "auto"
    ).lower()
    if response_format not in {"auto", "json", "text", "xml"}:
        raise ValueError("`response_format` must be auto, json, text, or xml.")
    return {
        "endpoint": _require_str("endpoint", payload.get("endpoint"), required=True),
        "params": _require_object("params", payload.get("params")),
        "record_path": _require_str("record_path", payload.get("record_path")),
        "response_format": response_format,
        "max_items": _require_int("max_items", payload.get("max_items"), 10),
        "max_depth": _require_int("max_depth", payload.get("max_depth"), 3),
        "timeout_sec": _require_int("timeout_sec", payload.get("timeout_sec"), 30),
        "save_raw": _require_bool("save_raw", payload.get("save_raw"), False),
        "raw_output_path": _require_str("raw_output_path", payload.get("raw_output_path")),
    }


def _ncbi_common_params(params: dict[str, Any]) -> dict[str, Any]:
    merged = dict(params)
    api_key = os.environ.get("NCBI_API_KEY") or os.environ.get("NCBI_EUTILS_API_KEY")
    tool = os.environ.get("NCBI_TOOL")
    email = os.environ.get("NCBI_EMAIL")
    if api_key and "api_key" not in merged:
        merged["api_key"] = api_key
    if tool and "tool" not in merged:
        merged["tool"] = tool
    if email and "email" not in merged:
        merged["email"] = email
    return merged


def _json_or_xml_output(
    data: Any, config: dict[str, Any], raw_output_path: str | None
) -> dict[str, Any]:
    record_path = config["record_path"]
    path_used, target = (
        _infer_target(data)
        if record_path is None
        else (record_path, _get_by_path(data, record_path))
    )
    output = {
        "ok": True,
        "source": "ncbi-entrez",
        "endpoint": config["endpoint"],
        "record_path": path_used,
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
        if isinstance(target, dict):
            output["top_keys"] = list(target)[: config["max_items"]]
    return output


def execute(payload: Any) -> dict[str, Any]:
    if requests is None:
        return error("missing_dependency", f"`requests` is required: {REQUESTS_IMPORT_ERROR}")
    config = parse_input(payload)
    try:
        suffix = config["endpoint"]
        if not suffix.endswith(".fcgi"):
            suffix = f"{suffix}.fcgi"
        url = f"{EUTILS_BASE}/{suffix.lstrip('/')}"
        response = requests.get(
            url, params=_ncbi_common_params(config["params"]), timeout=config["timeout_sec"]
        )
        response.raise_for_status()

        wants_json = config["response_format"] == "json"
        wants_xml = config["response_format"] == "xml"
        content_type = (response.headers.get("content-type") or "").lower()
        text = response.text

        if wants_json or text.lstrip().startswith("{") or "json" in content_type:
            data = response.json()
            raw_output_path = None
            if config["save_raw"]:
                raw_output_path = _save_raw_text(
                    json.dumps(data, indent=2), config["raw_output_path"], "json"
                )
            return _json_or_xml_output(data, config, raw_output_path)

        if wants_xml or text.lstrip().startswith("<"):
            root = ET.fromstring(text)
            data = {
                root.tag.split("}", 1)[-1]: _xml_to_simple(
                    root, config["max_items"], config["max_depth"]
                )
            }
            raw_output_path = None
            if config["save_raw"]:
                raw_output_path = _save_raw_text(text, config["raw_output_path"], "xml")
            return _json_or_xml_output(data, config, raw_output_path)

        raw_output_path = None
        if config["save_raw"]:
            raw_output_path = _save_raw_text(text, config["raw_output_path"], "txt")
        text_head = None if raw_output_path else text[:800]
        return {
            "ok": True,
            "source": "ncbi-entrez",
            "endpoint": config["endpoint"],
            "text_head": text_head,
            "text_head_truncated": False if raw_output_path else len(text) > 800,
            "raw_output_path": raw_output_path,
            "warnings": [],
        }
    except ValueError as exc:
        return error("invalid_response", str(exc))
    except ET.ParseError as exc:
        return error("invalid_response", f"Could not parse XML response: {exc}")
    except requests.RequestException as exc:
        return error("network_error", f"Request failed: {exc}")


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
