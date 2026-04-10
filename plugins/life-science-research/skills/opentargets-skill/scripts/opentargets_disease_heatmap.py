#!/usr/bin/env python3
"""Fetch Open Targets associated-disease datasource scores as a heatmap matrix."""

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

QUERY = """
query associatedDiseasesHeatmap($ensemblId: String!, $size: Int!, $index: Int!) {
  target(ensemblId: $ensemblId) {
    id
    approvedSymbol
    associatedDiseases(page: { size: $size, index: $index }) {
      count
      rows {
        disease { id name }
        datasourceScores { id score }
      }
    }
  }
}
"""

DATASOURCE_LABELS = {
    "ot_genetics_portal": "GWAS associations",
    "gene_burden": "Gene Burden",
    "eva": "ClinVar",
    "gene2phenotype": "Gene2phenotype",
    "gene2phenotype_literature": "Gene2phenotype literature",
    "genomics_england": "GEL PanelApp",
    "uniprot_literature": "UniProt literature",
    "uniprot_variants": "UniProt curated variants",
    "orphanet": "Orphanet",
    "clingen": "ClinGen",
    "cancer_gene_census": "Cancer Gene Census",
    "intogen": "IntOGen",
    "eva_somatic": "ClinVar (somatic)",
    "cancer_biomarkers": "Cancer Biomarkers",
    "chembl": "ChEMBL",
    "crispr_screen": "CRISPR Screens",
    "project_score": "Project Score",
    "reactome": "Reactome",
    "europepmc": "Europe PMC",
    "expression_atlas": "Expression Atlas",
    "impc": "IMPC",
}

PREFERRED_COLUMN_ORDER = [
    "ot_genetics_portal",
    "gene_burden",
    "eva",
    "genomics_england",
    "gene2phenotype",
    "uniprot_literature",
    "uniprot_variants",
    "orphanet",
    "clingen",
    "cancer_gene_census",
    "intogen",
    "eva_somatic",
    "cancer_biomarkers",
    "chembl",
    "crispr_screen",
    "project_score",
    "reactome",
    "europepmc",
    "expression_atlas",
    "impc",
]


def error(code: str, message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message}, "warnings": warnings or []}


def safe_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def prettify_datasource_id(datasource_id: str) -> str:
    words = datasource_id.replace("-", "_").split("_")
    if not words:
        return datasource_id
    pieces: list[str] = []
    for word in words:
        lowered = word.lower()
        if lowered == "pmc":
            pieces.append("PMC")
        elif lowered == "crispr":
            pieces.append("CRISPR")
        elif lowered == "impc":
            pieces.append("IMPC")
        elif lowered == "chembl":
            pieces.append("ChEMBL")
        else:
            pieces.append(word.capitalize())
    return " ".join(pieces)


def label_for_datasource(datasource_id: str) -> str:
    return DATASOURCE_LABELS.get(datasource_id, prettify_datasource_id(datasource_id))


def parse_input(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Input must be one JSON object.")
    ensembl_id = payload.get("ensembl_id") or payload.get("ensemblId")
    if not isinstance(ensembl_id, str) or not ensembl_id.strip():
        raise ValueError("Provide `ensembl_id`.")
    page_size = payload.get("page_size", payload.get("size", 50))
    max_pages = payload.get("max_pages", 10)
    if not isinstance(page_size, int) or page_size <= 0:
        raise ValueError("`page_size` must be a positive integer.")
    if not isinstance(max_pages, int) or max_pages <= 0:
        raise ValueError("`max_pages` must be a positive integer.")
    disease_filter = payload.get("disease_name_filter") or payload.get("diseaseNameFilter")
    if disease_filter is not None and not isinstance(disease_filter, str):
        raise ValueError("`disease_name_filter` must be a string.")
    save_raw = payload.get("save_raw", False)
    if not isinstance(save_raw, bool):
        raise ValueError("`save_raw` must be a boolean.")
    raw_output_path = payload.get("raw_output_path")
    if raw_output_path is not None and (
        not isinstance(raw_output_path, str) or not raw_output_path.strip()
    ):
        raise ValueError("`raw_output_path` must be a non-empty string.")
    return {
        "ensembl_id": ensembl_id.strip(),
        "page_size": page_size,
        "max_pages": max_pages,
        "disease_name_filter": disease_filter.strip() if isinstance(disease_filter, str) else None,
        "save_raw": save_raw,
        "raw_output_path": raw_output_path.strip() if isinstance(raw_output_path, str) else None,
    }


def fetch_page(ensembl_id: str, page_size: int, page_index: int) -> dict[str, Any]:
    response = requests.post(
        ENDPOINT,
        json={
            "query": QUERY,
            "variables": {"ensemblId": ensembl_id, "size": page_size, "index": page_index},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"])[:500])
    payload = data.get("data")
    if not isinstance(payload, dict):
        raise RuntimeError("GraphQL response did not include a `data` object.")
    target = payload.get("target")
    if not isinstance(target, dict):
        raise RuntimeError("Target was not found in the GraphQL response.")
    return target


def sort_datasource_ids(datasource_ids: set[str]) -> list[str]:
    preferred_index = {item: idx for idx, item in enumerate(PREFERRED_COLUMN_ORDER)}
    return sorted(
        datasource_ids,
        key=lambda item: (
            preferred_index.get(item, len(preferred_index)),
            label_for_datasource(item),
        ),
    )


def build_top_datasources(score_map: dict[str, float], limit: int = 3) -> list[dict[str, Any]]:
    ranked = sorted(score_map.items(), key=lambda item: item[1], reverse=True)[:limit]
    return [
        {"id": datasource_id, "label": label_for_datasource(datasource_id), "score": score}
        for datasource_id, score in ranked
    ]


def execute(payload: Any) -> dict[str, Any]:
    if requests is None:
        return error("missing_dependency", f"`requests` is required: {REQUESTS_IMPORT_ERROR}")

    config = parse_input(payload)
    fetched_rows: list[dict[str, Any]] = []
    raw_pages: list[dict[str, Any]] = []
    warnings: list[str] = []
    total_count: int | None = None
    target_id: str | None = None
    approved_symbol: str | None = None

    try:
        for page_index in range(config["max_pages"]):
            target = fetch_page(config["ensembl_id"], config["page_size"], page_index)
            if target_id is None:
                target_id = str(target.get("id") or config["ensembl_id"])
            if approved_symbol is None and target.get("approvedSymbol"):
                approved_symbol = str(target.get("approvedSymbol"))
            associated = target.get("associatedDiseases") or {}
            if not isinstance(associated, dict):
                raise RuntimeError("`associatedDiseases` was missing from the target payload.")
            if total_count is None and isinstance(associated.get("count"), int):
                total_count = int(associated["count"])
            rows = associated.get("rows") or []
            if not isinstance(rows, list):
                raise RuntimeError("`associatedDiseases.rows` was not a list.")
            fetched_rows.extend(rows)
            raw_pages.append({"index": page_index, "rows": rows})
            if not rows or len(rows) < config["page_size"]:
                break
            if total_count is not None and len(fetched_rows) >= total_count:
                break
        else:
            warnings.append(
                f"Stopped after `max_pages={config['max_pages']}` before exhausting associated disease pages."
            )
    except ValueError as exc:
        return error("invalid_response", str(exc), warnings=warnings)
    except requests.RequestException as exc:
        return error("network_error", f"GraphQL request failed: {exc}", warnings=warnings)
    except RuntimeError as exc:
        return error("graphql_error", str(exc), warnings=warnings)

    disease_filter = config["disease_name_filter"]
    filtered_rows: list[dict[str, Any]] = []
    datasource_ids: set[str] = set()
    for row in fetched_rows:
        disease = row.get("disease") or {}
        if not isinstance(disease, dict):
            continue
        disease_name = str(disease.get("name") or "").strip()
        if disease_filter and disease_filter.casefold() not in disease_name.casefold():
            continue
        score_map: dict[str, float] = {}
        for item in row.get("datasourceScores") or []:
            if not isinstance(item, dict):
                continue
            datasource_id = str(item.get("id") or "").strip()
            score = safe_float(item.get("score"))
            if not datasource_id or score is None:
                continue
            score_map[datasource_id] = score
            datasource_ids.add(datasource_id)
        filtered_rows.append(
            {
                "disease_id": str(disease.get("id") or ""),
                "disease_name": disease_name,
                "datasource_scores": score_map,
            }
        )

    ordered_datasource_ids = sort_datasource_ids(datasource_ids)
    columns = [
        {"id": datasource_id, "label": label_for_datasource(datasource_id)}
        for datasource_id in ordered_datasource_ids
    ]
    row_preview = [
        {
            "disease_name": row["disease_name"],
            "top_datasources": build_top_datasources(row["datasource_scores"]),
        }
        for row in filtered_rows[:5]
    ]

    raw_output_path = None
    if config["save_raw"]:
        raw_text = json.dumps(
            {
                "query_name": "associatedDiseasesHeatmap",
                "target": {"id": target_id, "approvedSymbol": approved_symbol},
                "page_size": config["page_size"],
                "max_pages": config["max_pages"],
                "pages": raw_pages,
            },
            indent=2,
        )
        path = Path(config["raw_output_path"] or "/tmp/opentargets-associated-diseases.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(raw_text, encoding="utf-8")
        raw_output_path = str(path)

    if disease_filter and not filtered_rows:
        warnings.append(f"No diseases matched `disease_name_filter={disease_filter}`.")

    return {
        "ok": True,
        "source": "opentargets-disease-heatmap",
        "summary": {
            "target": {"id": target_id or config["ensembl_id"], "approved_symbol": approved_symbol},
            "pages_fetched": len(raw_pages),
            "fetched_rows": len(fetched_rows),
            "returned_rows": len(filtered_rows),
            "total_count": total_count,
            "disease_name_filter": disease_filter,
            "columns": columns,
            "rows_preview": row_preview,
        },
        "matrix": {
            "target": {"id": target_id or config["ensembl_id"], "approved_symbol": approved_symbol},
            "columns": columns,
            "rows": filtered_rows,
        },
        "raw_output_path": raw_output_path,
        "warnings": warnings,
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
