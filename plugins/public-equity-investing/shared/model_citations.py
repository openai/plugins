"""Source-to-cell citation helpers for Public Equity Investing model workbooks."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

REQUIRED_CITATION_FIELDS = {
    "citation_id",
    "workbook_path",
    "sheet",
    "cell_or_range",
    "metric_name",
    "value",
    "formula",
    "source_ids",
    "assumption_flag",
    "tie_out_status",
}
VALID_TIE_OUT_STATUSES = {"tied", "not_tied", "needs_review", "model_generated", "not_applicable"}


def _slug(value: Any) -> str:
    raw = str(value or "").strip().lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw or "citation"


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def citation_item(
    citation_id: str,
    workbook_path: str | Path,
    sheet: str,
    cell_or_range: str,
    metric_name: str,
    value: Any = "",
    formula: str = "",
    source_ids: Sequence[str] | None = None,
    assumption_flag: bool = False,
    tie_out_status: str = "model_generated",
    **extra: Any,
) -> dict[str, Any]:
    sources = [str(item) for item in (source_ids or ["model-output"]) if str(item)] or [
        "model-output"
    ]
    cid = str(
        citation_id or f"model-output:{_slug(sheet)}:{_slug(metric_name)}:{_slug(cell_or_range)}"
    )
    cell = str(cell_or_range or "A1")
    item = {
        "citation_id": cid,
        "id": cid,
        "source_id": cid,
        "parent_source_id": sources[0],
        "title": str(metric_name or cid),
        "short_label": f"Model: {sheet}!{cell}",
        "type": "model_cell",
        "quality": "model_output",
        "workbook_path": str(workbook_path),
        "sheet": str(sheet),
        "cell_or_range": cell,
        "cell": cell.split(":", 1)[0],
        "range": cell,
        "metric_name": str(metric_name or cid),
        "value": _stringify(value),
        "formula": str(formula or ""),
        "source_ids": sources,
        "assumption_flag": bool(assumption_flag),
        "tie_out_status": tie_out_status
        if tie_out_status in VALID_TIE_OUT_STATUSES
        else "needs_review",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "aliases": [str(metric_name or cid)],
        "notes": "Generated workbook-level citation for dashboard/source-gate use.",
    }
    item.update(extra)
    return item


def load_model_citations(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("model_citations") or payload.get("workbook_citations") or []
    return [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []


def validate_model_citations(
    payload: Sequence[Mapping[str, Any]] | Mapping[str, Any], strict: bool = False
) -> list[str]:
    citations = (
        (payload.get("model_citations") or payload.get("workbook_citations") or [])
        if isinstance(payload, Mapping)
        else payload
    )
    errors: list[str] = []
    if not isinstance(citations, Sequence) or isinstance(citations, (str, bytes)) or not citations:
        return ["model citations must be a non-empty array"]
    for idx, citation in enumerate(citations):
        prefix = f"citations[{idx}]"
        if not isinstance(citation, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(field for field in REQUIRED_CITATION_FIELDS if field not in citation)
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
        if citation.get("tie_out_status") not in VALID_TIE_OUT_STATUSES:
            errors.append(f"{prefix}.tie_out_status invalid: {citation.get('tie_out_status')}")
        source_ids = citation.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(f"{prefix}.source_ids must be a non-empty array")
        if strict:
            for field in ("citation_id", "workbook_path", "sheet", "cell_or_range", "metric_name"):
                if str(citation.get(field, "")).strip().lower() in {
                    "",
                    "unknown",
                    "not_provided",
                    "n/a",
                }:
                    errors.append(f"{prefix}.{field} cannot be placeholder in strict mode")
    return errors
