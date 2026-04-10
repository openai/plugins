#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests

GWAS_BASE = "https://www.ebi.ac.uk/gwas/rest/api"
EFO_BASE = "https://www.ebi.ac.uk/ols4/api"
OT_BASE = "https://api.platform.opentargets.org/api/v4/graphql"
GNOMAD_BASE = "https://gnomad.broadinstitute.org/api"
REFSNP_BASE = "https://api.ncbi.nlm.nih.gov/variation/v0/beta/refsnp"

DEFAULT_LOCUS_PADDING_BP = 1_000_000

REPO_ROOT = Path(__file__).resolve().parents[2]
VARIANT_COORDINATE_FINDER_SCRIPT = (
    REPO_ROOT / "variant-coordinate-finder-skill" / "scripts" / "variant_coordinate_finder.py"
)
GTEX_EQTL_SCRIPT = REPO_ROOT / "gtex-eqtl-skill" / "scripts" / "gtex_eqtl.py"
GENEBASS_GENE_BURDEN_SCRIPT = (
    REPO_ROOT / "genebass-gene-burden-skill" / "scripts" / "genebass_gene_burden.py"
)

TOKEN_STOPWORDS = {
    "disease",
    "disorder",
    "trait",
    "syndrome",
    "chronic",
    "acute",
    "self",
    "reported",
    "unknown",
}

DEFAULT_TRAIT_SEED_RSIDS: dict[str, list[str]] = {
    "type 2 diabetes": ["rs7903146", "rs13266634", "rs7756992", "rs5219", "rs1801282", "rs4402960"],
    "type ii diabetes": [
        "rs7903146",
        "rs13266634",
        "rs7756992",
        "rs5219",
        "rs1801282",
        "rs4402960",
    ],
    "t2d": ["rs7903146", "rs13266634", "rs7756992", "rs5219", "rs1801282", "rs4402960"],
    "coronary artery disease": [
        "rs1333049",
        "rs4977574",
        "rs9349379",
        "rs6725887",
        "rs1746048",
        "rs3184504",
    ],
    "cad": ["rs1333049", "rs4977574", "rs9349379", "rs6725887", "rs1746048", "rs3184504"],
    "body mass index": [
        "rs9939609",
        "rs17782313",
        "rs6548238",
        "rs10938397",
        "rs7498665",
        "rs7138803",
    ],
    "bmi": ["rs9939609", "rs17782313", "rs6548238", "rs10938397", "rs7498665", "rs7138803"],
    "asthma": ["rs7216389", "rs2305480", "rs9273349"],
    "rheumatoid arthritis": ["rs2476601", "rs3761847", "rs660895"],
    "alzheimer disease": ["rs429358", "rs7412", "rs6733839", "rs11136000", "rs3851179"],
    "alzheimers disease": ["rs429358", "rs7412", "rs6733839", "rs11136000", "rs3851179"],
    "ldl cholesterol": ["rs7412", "rs429358", "rs6511720", "rs629301", "rs12740374", "rs11591147"],
    "total cholesterol": [
        "rs7412",
        "rs429358",
        "rs6511720",
        "rs629301",
        "rs12740374",
        "rs11591147",
    ],
}

SEARCH_STUDY_QUERY = """
query searchStudy($q: String!, $page: Pagination) {
  search(queryString: $q, entityNames: ["study"], page: $page) {
    total
    hits {
      score
      object {
        ... on Study {
          id
          projectId
          traitFromSource
          hasSumstats
        }
      }
    }
  }
}
"""

STUDY_CREDIBLE_SETS_QUERY = """
query studyCredibleSets($studyId: String!, $page: Pagination) {
  study(studyId: $studyId) {
    id
    projectId
    traitFromSource
    credibleSets(page: $page) {
      count
      rows {
        studyLocusId
        chromosome
        position
        pValueExponent
        pValueMantissa
        variant { id rsIds }
      }
    }
  }
}
"""

CREDIBLE_SETS_DETAIL_BATCH_QUERY = """
query l2gAndColoc($studyLocusIds: [String!]!) {
  credibleSets(studyLocusIds: $studyLocusIds) {
    rows {
      studyLocusId
      l2GPredictions {
        rows { score target { id approvedSymbol } }
      }
      colocalisation(page: {index: 0, size: 100}) {
        rows {
          colocalisationMethod
          h4
          clpp
          otherStudyLocus { studyId studyLocusId }
        }
      }
    }
  }
}
"""

SEARCH_TARGET_QUERY = """
query searchTarget($q: String!) {
  search(queryString: $q, entityNames: ["target"], page: {index: 0, size: 10}) {
    hits {
      score
      object {
        ... on Target {
          id
          approvedSymbol
          approvedName
        }
      }
    }
  }
}
"""

GNOMAD_GENE_QUERY = """
query GeneConstraint($geneSymbol: String!, $referenceGenome: ReferenceGenomeId!) {
  gene(gene_symbol: $geneSymbol, reference_genome: $referenceGenome) {
    symbol
    gencode_symbol
    gnomad_constraint {
      exp_lof
      obs_lof
      oe_lof
      oe_lof_lower
      oe_lof_upper
      lof_z
      mis_z
      pLI
    }
  }
}
"""

CODING_SEQUENCE_TERMS = {
    "missense_variant",
    "stop_gained",
    "stop_lost",
    "frameshift_variant",
    "protein_altering_variant",
    "inframe_insertion",
    "inframe_deletion",
    "splice_donor_variant",
    "splice_acceptor_variant",
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        s = str(item).strip()
        if not s:
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    s = s.replace(",", "")
    match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def coerce_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def coerce_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    s = str(value).strip()
    return [s] if s else []


def normalize_rsid(value: str) -> str | None:
    m = re.search(r"(rs\d+)", value.strip(), flags=re.IGNORECASE)
    if not m:
        return None
    return m.group(1).lower().replace("rs", "rs")


def normalize_trait_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def tokenize(value: str) -> set[str]:
    tokens = {tok for tok in re.findall(r"[A-Za-z0-9]+", value.lower()) if len(tok) > 2}
    return {tok for tok in tokens if tok not in TOKEN_STOPWORDS}


def lexical_match_score(text: str, term: str) -> float:
    text_n = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    term_n = re.sub(r"[^a-z0-9]+", " ", term.lower()).strip()
    if not text_n or not term_n:
        return 0.0
    if term_n in text_n:
        return 1.0

    text_tokens = tokenize(text_n)
    term_tokens = tokenize(term_n)
    if not text_tokens or not term_tokens:
        return 0.0

    overlap = len(text_tokens.intersection(term_tokens))
    if overlap == 0:
        return 0.0

    coverage = overlap / max(len(term_tokens), 1)
    precision = overlap / max(len(text_tokens), 1)
    score = 0.6 * coverage + 0.4 * precision
    if overlap >= 2:
        score += 0.1
    return min(score, 1.0)


def safe_get_json(
    url: str, params: dict[str, Any] | None = None, timeout: int = 45
) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict):
        return payload
    return {"results": payload}


def safe_post_json(url: str, payload: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        return data
    return {"results": data}


def run_json_skill_script(
    script_path: Path,
    payload: dict[str, Any],
    limitations: list[str],
    timeout_s: int = 45,
) -> dict[str, Any] | None:
    if not script_path.exists():
        limitations.append(f"Missing skill script: {script_path}")
        return None
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=timeout_s,
            check=False,
        )
    except Exception as exc:
        limitations.append(f"Failed to execute {script_path.name}: {exc}")
        return None

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        stdout = (proc.stdout or "").strip()
        details = stderr or stdout or f"exit_code={proc.returncode}"
        limitations.append(f"{script_path.name} failed: {details}")
        return None

    out = (proc.stdout or "").strip()
    if not out:
        limitations.append(f"{script_path.name} returned empty output")
        return None

    try:
        parsed = json.loads(out)
    except Exception as exc:
        limitations.append(f"{script_path.name} returned non-JSON output: {exc}")
        return None

    if not isinstance(parsed, dict):
        limitations.append(f"{script_path.name} returned unexpected JSON shape")
        return None

    return parsed


def resolve_efo(trait_query: str, warnings: list[str], limitations: list[str]) -> dict[str, Any]:
    if not trait_query:
        return {
            "anchor_label": "",
            "efo_id": None,
            "anchor_iri": None,
            "synonyms": [],
            "descendants": [],
            "resolver_source": "efo-ontology-skill",
        }

    params = {
        "q": trait_query,
        "ontology": "efo",
        "type": "class",
        "queryFields": "label,synonym,short_form,obo_id",
        "rows": 25,
        "exact": "false",
        "local": "true",
    }
    try:
        search_data = safe_get_json(f"{EFO_BASE}/search", params=params)
        docs = (search_data.get("response") or {}).get("docs") or []
        if not docs:
            warnings.append("No EFO hit found for trait_query; continuing with free-text only.")
            return {
                "anchor_label": trait_query,
                "efo_id": None,
                "anchor_iri": None,
                "synonyms": [],
                "descendants": [],
                "resolver_source": "efo-ontology-skill",
            }

        top = coerce_dict(docs[0])
        iri = top.get("iri")
        label = str(top.get("label") or trait_query)
        efo_id = top.get("obo_id")
        synonyms = as_string_list(top.get("synonym"))

        descendants: list[str] = []
        if iri:
            encoded = requests.utils.quote(requests.utils.quote(str(iri), safe=""), safe="")
            page = 0
            total_pages = 1
            while page < total_pages and page < 6:
                desc_data = safe_get_json(
                    f"{EFO_BASE}/ontologies/efo/terms/{encoded}/descendants",
                    params={"size": 200, "page": page},
                )
                rows = (desc_data.get("_embedded") or {}).get("terms") or []
                descendants.extend(
                    [str(row.get("label")).strip() for row in rows if coerce_dict(row).get("label")]
                )
                page_info = coerce_dict(desc_data.get("page"))
                total_pages = int(page_info.get("totalPages", 0) or 0)
                page += 1

        return {
            "anchor_label": label,
            "efo_id": efo_id,
            "anchor_iri": iri,
            "synonyms": dedupe_keep_order(synonyms),
            "descendants": dedupe_keep_order(descendants),
            "resolver_source": "efo-ontology-skill",
        }
    except Exception as exc:
        limitations.append(f"EFO resolver unavailable: {exc}")
        return {
            "anchor_label": trait_query,
            "efo_id": None,
            "anchor_iri": None,
            "synonyms": [],
            "descendants": [],
            "resolver_source": "efo-ontology-skill",
        }


def gwas_iter_associations(
    params: dict[str, Any],
    max_rows: int,
    page_size: int = 200,
    max_pages: int = 25,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 0
    total_pages = 1
    while page < total_pages and page < max_pages and len(rows) < max_rows:
        q = dict(params)
        q.update({"size": page_size, "page": page})
        data = safe_get_json(f"{GWAS_BASE}/v2/associations", params=q, timeout=45)
        chunk = (data.get("_embedded") or {}).get("associations") or []
        rows.extend(coerce_list_of_dicts(chunk))
        page_info = coerce_dict(data.get("page"))
        total_pages = int(page_info.get("totalPages", 0) or 0)
        page += 1
        time.sleep(0.05)
    return rows[:max_rows]


def parse_rsid_from_association(row: dict[str, Any]) -> str | None:
    snp_allele = row.get("snp_allele")
    if isinstance(snp_allele, list):
        for item in snp_allele:
            if isinstance(item, dict) and item.get("rs_id"):
                rsid = normalize_rsid(str(item["rs_id"]))
                if rsid:
                    return rsid
    effect = row.get("snp_effect_allele")
    if isinstance(effect, list) and effect:
        token = str(effect[0])
        rsid = normalize_rsid(token)
        if rsid:
            return rsid
    if row.get("rs_id"):
        rsid = normalize_rsid(str(row["rs_id"]))
        if rsid:
            return rsid
    snp_link = coerce_dict(coerce_dict(row.get("_links")).get("snp")).get("href")
    if isinstance(snp_link, str):
        rsid = normalize_rsid(snp_link)
        if rsid:
            return rsid
    return None


def extract_trait_name(row: dict[str, Any]) -> str:
    efo_traits = row.get("efo_traits")
    if isinstance(efo_traits, list):
        for trait in efo_traits:
            if isinstance(trait, dict) and trait.get("efo_trait"):
                return str(trait["efo_trait"])
    reported_trait = row.get("reported_trait")
    if isinstance(reported_trait, list) and reported_trait:
        return str(reported_trait[0])
    if isinstance(reported_trait, str):
        return reported_trait
    return ""


def extract_mapped_genes(row: dict[str, Any]) -> list[str]:
    mapped = row.get("mapped_genes")
    out: list[str] = []
    if isinstance(mapped, list):
        for entry in mapped:
            if isinstance(entry, str):
                parts = [p.strip() for p in entry.split(",") if p.strip()]
                out.extend(parts)
    return dedupe_keep_order(out)


def normalize_anchor_row(row: dict[str, Any]) -> dict[str, Any] | None:
    rsid = parse_rsid_from_association(row)
    if not rsid:
        return None
    p_value = safe_float(row.get("p_value"))
    trait_name = extract_trait_name(row)
    return {
        "rsid": rsid,
        "lead_trait": trait_name,
        "p_value": p_value,
        "cohort": "",
        "accession_id": row.get("accession_id"),
        "mapped_genes": extract_mapped_genes(row),
        "association_id": row.get("association_id"),
    }


def fetch_gwas_study_metadata(
    accession_ids: list[str], limitations: list[str]
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for accession_id in sorted(set(accession_ids)):
        if not accession_id:
            continue
        try:
            data = safe_get_json(f"{GWAS_BASE}/v2/studies/{accession_id}", timeout=45)
            out[accession_id] = {
                "cohort": ", ".join(as_string_list(data.get("cohort"))),
                "discovery_ancestry": ", ".join(as_string_list(data.get("discovery_ancestry"))),
                "initial_sample_size": data.get("initial_sample_size"),
            }
            time.sleep(0.03)
        except Exception as exc:
            limitations.append(f"GWAS study metadata unavailable for {accession_id}: {exc}")
    return out


def resolve_anchor_coordinates(
    anchors: list[dict[str, Any]], warnings: list[str], limitations: list[str]
) -> None:
    for anchor in anchors:
        rsid = str(anchor.get("rsid") or "")
        if not rsid:
            continue
        coord_result = run_json_skill_script(
            VARIANT_COORDINATE_FINDER_SCRIPT,
            {"rsid": rsid},
            limitations,
            timeout_s=25,
        )
        if not coord_result:
            anchor["grch38"] = None
            anchor["grch37"] = None
            anchor["locus_id"] = f"rsid:{rsid}"
            continue

        if not coord_result.get("ok"):
            error = coerce_dict(coord_result.get("error")).get("message")
            warnings.append(f"Coordinate lookup failed for {rsid}: {error}")
            anchor["grch38"] = None
            anchor["grch37"] = None
            anchor["locus_id"] = f"rsid:{rsid}"
            continue

        g38 = coerce_dict(coord_result.get("grch38"))
        g37 = coerce_dict(coord_result.get("grch37"))
        anchor["grch38"] = g38 if g38 else None
        anchor["grch37"] = g37 if g37 else None

        chr_ = g38.get("chr")
        pos = g38.get("pos")
        if chr_ is not None and pos is not None:
            try:
                pos_i = int(pos)
                start = max(1, pos_i - DEFAULT_LOCUS_PADDING_BP)
                end = pos_i + DEFAULT_LOCUS_PADDING_BP
                anchor["locus_id"] = f"chr{str(chr_).upper()}:{start}-{end}"
            except Exception:
                anchor["locus_id"] = f"rsid:{rsid}"
        else:
            anchor["locus_id"] = f"rsid:{rsid}"


def ot_query(query: str, variables: dict[str, Any], limitations: list[str]) -> dict[str, Any]:
    try:
        payload = safe_post_json(OT_BASE, {"query": query, "variables": variables}, timeout=120)
    except Exception as exc:
        limitations.append(f"Open Targets request failed: {exc}")
        return {}

    if payload.get("errors"):
        limitations.append(f"Open Targets GraphQL error: {payload.get('errors')}")
        return {}

    return coerce_dict(payload.get("data"))


def search_ot_studies(
    terms: list[str],
    max_studies: int,
    limitations: list[str],
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for term in terms:
        if not term:
            continue
        data = ot_query(
            SEARCH_STUDY_QUERY, {"q": term, "page": {"index": 0, "size": 25}}, limitations
        )
        hits = coerce_list_of_dicts(coerce_dict(data.get("search")).get("hits"))
        for hit in hits:
            obj = coerce_dict(hit.get("object"))
            study_id = obj.get("id")
            if not study_id:
                continue
            study = by_id.get(study_id)
            score = safe_float(hit.get("score")) or 0.0
            if study is None:
                by_id[study_id] = {
                    "id": study_id,
                    "projectId": obj.get("projectId"),
                    "traitFromSource": obj.get("traitFromSource"),
                    "hasSumstats": bool(obj.get("hasSumstats")),
                    "best_score": score,
                    "matched_terms": [term],
                }
            else:
                study["best_score"] = max(float(study.get("best_score") or 0.0), score)
                if term not in study["matched_terms"]:
                    study["matched_terms"].append(term)

    studies = sorted(
        by_id.values(), key=lambda row: float(row.get("best_score") or 0.0), reverse=True
    )
    if not studies:
        return []

    with_sumstats = [s for s in studies if s.get("hasSumstats")]
    chosen = with_sumstats[:max_studies] if with_sumstats else studies[:max_studies]
    return chosen


def fetch_ot_l2g_coloc_for_anchors(
    anchor_rsids: list[str],
    trait_terms: list[str],
    max_coloc_rows_per_locus: int,
    limitations: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "per_anchor": {rsid: {"l2g": [], "coloc": []} for rsid in anchor_rsids},
        "studies_used": [],
        "matched_study_loci": 0,
    }
    if not anchor_rsids or not trait_terms:
        return result

    studies = search_ot_studies(trait_terms, max_studies=8, limitations=limitations)
    if not studies:
        warnings.append(
            "No Open Targets studies found for trait terms; L2G/coloc components may be sparse."
        )
        return result

    anchor_set = set(anchor_rsids)
    study_locus_to_anchors: dict[str, set[str]] = {}

    for study in studies:
        study_id = str(study.get("id") or "")
        if not study_id:
            continue
        data = ot_query(
            STUDY_CREDIBLE_SETS_QUERY,
            {"studyId": study_id, "page": {"index": 0, "size": 800}},
            limitations,
        )
        study_payload = coerce_dict(data.get("study"))
        cs_rows = coerce_list_of_dicts(coerce_dict(study_payload.get("credibleSets")).get("rows"))
        for row in cs_rows:
            study_locus_id = row.get("studyLocusId")
            if not study_locus_id:
                continue
            variant = coerce_dict(row.get("variant"))
            rsids = [normalize_rsid(str(r)) for r in as_string_list(variant.get("rsIds"))]
            matched = {r for r in rsids if r and r in anchor_set}
            if not matched:
                continue
            study_locus_to_anchors.setdefault(str(study_locus_id), set()).update(matched)

        result["studies_used"].append(
            {
                "id": study_id,
                "projectId": study.get("projectId"),
                "traitFromSource": study.get("traitFromSource"),
                "matched_terms": study.get("matched_terms", []),
                "credible_set_count": len(cs_rows),
            }
        )
        time.sleep(0.06)

    study_locus_ids = sorted(study_locus_to_anchors.keys())
    result["matched_study_loci"] = len(study_locus_ids)
    if not study_locus_ids:
        warnings.append("No Open Targets credible sets were matched to anchor rsIDs.")
        return result

    chunk_size = 40
    for i in range(0, len(study_locus_ids), chunk_size):
        chunk = study_locus_ids[i : i + chunk_size]
        data = ot_query(CREDIBLE_SETS_DETAIL_BATCH_QUERY, {"studyLocusIds": chunk}, limitations)
        cs_rows = coerce_list_of_dicts(coerce_dict(data.get("credibleSets")).get("rows"))

        for row in cs_rows:
            study_locus_id = str(row.get("studyLocusId") or "")
            if not study_locus_id:
                continue
            matched_anchors = study_locus_to_anchors.get(study_locus_id, set())
            if not matched_anchors:
                continue

            l2g_rows = coerce_list_of_dicts(coerce_dict(row.get("l2GPredictions")).get("rows"))
            coloc_rows = coerce_list_of_dicts(coerce_dict(row.get("colocalisation")).get("rows"))
            if max_coloc_rows_per_locus > 0:
                coloc_rows = coloc_rows[:max_coloc_rows_per_locus]

            l2g_records: list[dict[str, Any]] = []
            for pred in l2g_rows:
                target = coerce_dict(pred.get("target"))
                symbol = str(target.get("approvedSymbol") or "").strip()
                if not symbol:
                    continue
                l2g_records.append(
                    {
                        "symbol": symbol,
                        "ensembl_id": target.get("id"),
                        "score": safe_float(pred.get("score")) or 0.0,
                        "studyLocusId": study_locus_id,
                    }
                )

            coloc_records: list[dict[str, Any]] = []
            for coloc in coloc_rows:
                coloc_records.append(
                    {
                        "studyLocusId": study_locus_id,
                        "method": coloc.get("colocalisationMethod"),
                        "h4": safe_float(coloc.get("h4")),
                        "clpp": safe_float(coloc.get("clpp")),
                        "otherStudyId": coerce_dict(coloc.get("otherStudyLocus")).get("studyId"),
                    }
                )

            for anchor_rsid in matched_anchors:
                result["per_anchor"].setdefault(anchor_rsid, {"l2g": [], "coloc": []})
                result["per_anchor"][anchor_rsid]["l2g"].extend(l2g_records)
                result["per_anchor"][anchor_rsid]["coloc"].extend(coloc_records)
        time.sleep(0.05)

    return result


def extract_eqtl_gene_symbol(row: dict[str, Any]) -> str | None:
    candidates = [
        row.get("geneSymbol"),
        row.get("gene_symbol"),
        row.get("geneName"),
        row.get("gene_name"),
        row.get("symbol"),
    ]
    gene_obj = row.get("gene")
    if isinstance(gene_obj, dict):
        candidates.extend(
            [
                gene_obj.get("symbol"),
                gene_obj.get("geneSymbol"),
                gene_obj.get("approvedSymbol"),
            ]
        )

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def extract_eqtl_tissue(row: dict[str, Any]) -> str:
    candidates = [
        row.get("tissueSiteDetailId"),
        row.get("tissue"),
        row.get("tissue_id"),
        row.get("tissueSiteDetail"),
    ]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return "."


def fetch_gtex_support(
    anchors: list[dict[str, Any]],
    max_results: int,
    limitations: list[str],
    warnings: list[str],
) -> dict[str, dict[str, set[str]]]:
    out: dict[str, dict[str, set[str]]] = {}

    for anchor in anchors:
        rsid = str(anchor.get("rsid") or "")
        g38 = coerce_dict(anchor.get("grch38"))
        chr_ = g38.get("chr")
        pos = g38.get("pos")
        ref = g38.get("ref")
        alt = g38.get("alt")
        if chr_ is None or pos is None or not ref or not alt:
            continue

        variant = f"{chr_}:{pos}-{ref}-{alt}"
        payload = {"grch38": variant, "max_results": max_results}
        result = run_json_skill_script(GTEX_EQTL_SCRIPT, payload, limitations, timeout_s=40)
        if not result:
            continue
        if not result.get("ok"):
            err = coerce_dict(result.get("error")).get("message")
            warnings.append(f"GTEx lookup failed for {rsid}: {err}")
            continue

        eqtls = result.get("eqtls")
        if not isinstance(eqtls, list):
            continue

        gene_to_tissues = out.setdefault(rsid, {})
        for row in eqtls:
            if not isinstance(row, dict):
                continue
            symbol = extract_eqtl_gene_symbol(row)
            if not symbol:
                continue
            tissue = extract_eqtl_tissue(row)
            gene_to_tissues.setdefault(symbol, set()).add(tissue)

    return out


def resolve_ensembl_ids_for_symbols(symbols: list[str], limitations: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for symbol in symbols:
        symbol_n = symbol.strip()
        if not symbol_n:
            continue
        data = ot_query(SEARCH_TARGET_QUERY, {"q": symbol_n}, limitations)
        hits = coerce_list_of_dicts(coerce_dict(data.get("search")).get("hits"))
        selected_id: str | None = None
        for hit in hits:
            obj = coerce_dict(hit.get("object"))
            approved_symbol = str(obj.get("approvedSymbol") or "")
            target_id = str(obj.get("id") or "")
            if approved_symbol.upper() == symbol_n.upper() and target_id.startswith("ENSG"):
                selected_id = target_id
                break
        if not selected_id and hits:
            first_obj = coerce_dict(hits[0].get("object"))
            maybe_id = str(first_obj.get("id") or "")
            maybe_symbol = str(first_obj.get("approvedSymbol") or "")
            if maybe_id.startswith("ENSG") and maybe_symbol.upper() == symbol_n.upper():
                selected_id = maybe_id
        if selected_id:
            out[symbol_n] = selected_id
        time.sleep(0.03)
    return out


def fetch_genebass_support(
    symbol_to_ensembl: dict[str, str],
    burden_sets: list[str],
    trait_terms: list[str],
    max_results: int,
    limitations: list[str],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    trait_terms_n = [t for t in trait_terms if t]

    for symbol, ensembl_id in symbol_to_ensembl.items():
        best_p: float | None = None
        best_phenotype: str | None = None
        supporting_rows = 0

        for burden_set in burden_sets:
            payload = {
                "ensembl_gene_id": ensembl_id,
                "burden_set": burden_set,
                "max_results": max_results,
            }
            result = run_json_skill_script(
                GENEBASS_GENE_BURDEN_SCRIPT, payload, limitations, timeout_s=45
            )
            if not result or not result.get("ok"):
                continue
            associations = result.get("associations")
            if not isinstance(associations, list):
                continue

            for row in associations:
                if not isinstance(row, dict):
                    continue
                phenotype = str(row.get("phenotype_description") or "")
                pval = safe_float(row.get("skat_o_pvalue"))
                if pval is None:
                    continue

                match = 0.0
                if trait_terms_n:
                    match = max(
                        (lexical_match_score(phenotype, term) for term in trait_terms_n),
                        default=0.0,
                    )
                if not trait_terms_n or match >= 0.58:
                    supporting_rows += 1
                    if best_p is None or pval < best_p:
                        best_p = pval
                        best_phenotype = phenotype

        if best_p is not None and best_p < 2.5e-6:
            support = "strong"
        elif best_p is not None and best_p < 0.05:
            support = "nominal"
        else:
            support = "none"

        out[symbol] = {
            "best_p": best_p,
            "best_phenotype": best_phenotype,
            "support": support,
            "supporting_rows": supporting_rows,
        }

    return out


def fetch_refsnp_annotations(rsids: list[str], limitations: list[str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}

    for rsid in rsids:
        digits = "".join(ch for ch in rsid if ch.isdigit())
        if not digits:
            continue
        url = f"{REFSNP_BASE}/{digits}"
        try:
            payload = safe_get_json(url, timeout=35)
        except Exception as exc:
            limitations.append(f"RefSNP lookup failed for {rsid}: {exc}")
            continue

        snapshot = coerce_dict(payload.get("primary_snapshot_data"))
        genes = {
            str(item.get("name")).strip()
            for item in coerce_list_of_dicts(snapshot.get("genes"))
            if item.get("name")
        }
        coding_genes: set[str] = set()
        consequence_terms: set[str] = set()

        for allele_ann in coerce_list_of_dicts(snapshot.get("allele_annotations")):
            for asm_ann in coerce_list_of_dicts(allele_ann.get("assembly_annotation")):
                for gene in coerce_list_of_dicts(asm_ann.get("genes")):
                    gene_symbol = str(gene.get("name") or "").strip()
                    is_coding = False
                    for rna in coerce_list_of_dicts(gene.get("rnas")):
                        protein = rna.get("protein")
                        protein_items = [protein] if isinstance(protein, dict) else protein
                        if not isinstance(protein_items, list):
                            protein_items = []
                        for protein_item in protein_items:
                            if not isinstance(protein_item, dict):
                                continue
                            for so in coerce_list_of_dicts(protein_item.get("sequence_ontology")):
                                term = str(so.get("name") or "").strip()
                                if not term:
                                    continue
                                consequence_terms.add(term)
                                if term in CODING_SEQUENCE_TERMS:
                                    is_coding = True
                    if gene_symbol and is_coding:
                        coding_genes.add(gene_symbol)

        out[rsid] = {
            "genes": sorted(genes),
            "coding_genes": sorted(coding_genes),
            "consequence_terms": sorted(consequence_terms),
        }
        time.sleep(0.05)

    return out


def fetch_gnomad_gene_constraints(
    symbols: list[str],
    limitations: list[str],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}

    for symbol in symbols[:40]:
        payload = {
            "query": GNOMAD_GENE_QUERY,
            "variables": {"geneSymbol": symbol, "referenceGenome": "GRCh38"},
        }
        try:
            data = safe_post_json(GNOMAD_BASE, payload, timeout=45)
        except Exception as exc:
            limitations.append(f"gnomAD gene-constraint lookup failed for {symbol}: {exc}")
            continue

        errors = data.get("errors")
        if errors:
            limitations.append(f"gnomAD GraphQL error for {symbol}: {errors}")
            continue

        gene = coerce_dict(coerce_dict(data.get("data")).get("gene"))
        constraint = coerce_dict(gene.get("gnomad_constraint"))
        if not gene or not constraint:
            continue

        out[symbol] = {
            "oe_lof": safe_float(constraint.get("oe_lof")),
            "oe_lof_lower": safe_float(constraint.get("oe_lof_lower")),
            "oe_lof_upper": safe_float(constraint.get("oe_lof_upper")),
            "mis_z": safe_float(constraint.get("mis_z")),
            "lof_z": safe_float(constraint.get("lof_z")),
            "pli": safe_float(constraint.get("pLI")),
        }
        time.sleep(0.05)

    return out


def support_from_burden(best_p: float | None) -> tuple[str, float]:
    if best_p is None:
        return "none", 0.0
    if best_p < 2.5e-6:
        return "strong", 1.0
    if best_p < 0.05:
        return "nominal", 0.6
    return "none", 0.0


def coding_component(coding_support: str, clinvar_support: str) -> float:
    if coding_support == "coding" and clinvar_support == "present":
        return 1.0
    if coding_support == "coding":
        return 0.6
    if coding_support == "noncoding":
        return 0.3
    return 0.0


def confidence_label(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.55:
        return "Medium"
    if score >= 0.35:
        return "Low"
    return "VeryLow"


def format_gnomad_context(constraint: dict[str, Any] | None) -> str:
    if not constraint:
        return "."
    oe_upper = constraint.get("oe_lof_upper")
    pli = constraint.get("pli")
    parts = []
    if oe_upper is not None:
        parts.append(f"oe_lof_upper={oe_upper:.3g}")
    if pli is not None:
        parts.append(f"pLI={pli:.3g}")
    return "; ".join(parts) if parts else "."


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def markdown_image_tag(alt_text: str, absolute_path: str) -> str:
    # Use angle-bracket URL form so paths with spaces still render.
    return f"![{alt_text}](<{absolute_path}>)"


def build_inline_image_markdown(figure_entries: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for fig in figure_entries:
        path = str(fig.get("path") or "").strip()
        if not path:
            continue
        caption = str(fig.get("caption") or fig.get("id") or "figure").strip()
        lines.append(markdown_image_tag(caption, path))
    return lines


def build_summary_markdown(
    mapping_payload: dict[str, Any],
    figure_entries: list[dict[str, Any]],
    figure_fallback_mermaid: str | None,
) -> str:
    meta = coerce_dict(mapping_payload.get("meta"))
    loci = coerce_list_of_dicts(mapping_payload.get("loci"))
    cross = coerce_list_of_dicts(mapping_payload.get("cross_locus_ranked_genes"))
    warnings = as_string_list(mapping_payload.get("warnings"))
    limitations = as_string_list(mapping_payload.get("limitations"))

    trait_query = str(meta.get("trait_query") or "")
    efo_id = str(meta.get("efo_id") or "unresolved")

    lines: list[str] = []
    lines.append("## Objective")
    lines.append(
        f"Map GWAS loci for `{trait_query or 'seeded variants'}` to ranked candidate genes using a deterministic evidence chain (GWAS, coordinates, Open Targets L2G/coloc, GTEx eQTL, burden, coding context)."
    )
    lines.append("")

    lines.append("## Inputs and scope")
    lines.append(f"- Trait query: `{trait_query or '.'}`")
    lines.append(f"- EFO ID: `{efo_id}`")
    lines.append(
        f"- Anchor variants: `{len(as_string_list(mapping_payload.get('anchors')))} loci seeds in output payload`"
    )
    lines.append(f"- Generated at: `{meta.get('generated_at')}`")
    lines.append("")

    lines.append("## Anchor variant summary")
    anchors = coerce_list_of_dicts(mapping_payload.get("anchors"))
    if not anchors:
        lines.append("No anchors were retained after normalization.")
    else:
        for anchor in anchors[:20]:
            rsid = anchor.get("rsid") or "."
            p = anchor.get("p_value")
            p_txt = f"{p:.3g}" if isinstance(p, (int, float)) else "."
            trait = anchor.get("lead_trait") or "."
            locus_id = anchor.get("locus_id") or "."
            lines.append(f"- `{rsid}` | p={p_txt} | trait={trait} | locus={locus_id}")
    lines.append("")

    lines.append("## Per-locus top genes")
    if not loci:
        lines.append("No loci available.")
    else:
        for locus in loci:
            locus_id = locus.get("locus_id") or "."
            lead_rsid = locus.get("lead_rsid") or "."
            lines.append(f"### {locus_id} (lead `{lead_rsid}`)")
            genes = coerce_list_of_dicts(locus.get("candidate_genes"))
            if not genes:
                lines.append("- No candidate genes scored.")
                continue
            for gene in genes[:5]:
                symbol = gene.get("symbol") or "."
                score = safe_float(gene.get("overall_score")) or 0.0
                conf = gene.get("confidence") or "."
                evidence = coerce_dict(gene.get("evidence"))
                l2g = safe_float(evidence.get("l2g_max")) or 0.0
                coloc = safe_float(evidence.get("coloc_max_h4")) or 0.0
                tissues = as_string_list(evidence.get("eqtl_tissues"))
                lines.append(
                    f"- `{symbol}` | score={score:.3f} ({conf}) | L2G={l2g:.3f} | coloc={coloc:.3f} | eQTL tissues={len([t for t in tissues if t != '.'])}"
                )
    lines.append("")

    lines.append("## Cross-locus prioritized genes")
    if not cross:
        lines.append("No cross-locus aggregated ranking available.")
    else:
        for row in cross[:15]:
            symbol = row.get("symbol") or "."
            supporting_loci = row.get("supporting_loci") or 0
            mean_score = safe_float(row.get("mean_score")) or 0.0
            max_score = safe_float(row.get("max_score")) or 0.0
            lines.append(
                f"- `{symbol}` | supporting_loci={supporting_loci} | mean_score={mean_score:.3f} | max_score={max_score:.3f}"
            )
    lines.append("")

    lines.append("## Key caveats")
    caveats = dedupe_keep_order(limitations + warnings)
    if not caveats:
        lines.append("- No major caveats recorded.")
    else:
        for item in caveats[:20]:
            lines.append(f"- {item}")
    lines.append("")

    lines.append("## Recommended next analyses")
    lines.append("1. Run fine-mapping/conditional analysis on top loci before causal claims.")
    lines.append(
        "2. Validate top genes with independent cohort summary statistics where available."
    )
    lines.append(
        "3. Add tissue- and cell-type-specific molecular QTL datasets for stronger functional assignment."
    )
    lines.append("4. Review liability/pleiotropy for top genes before portfolio decisions.")
    lines.append("")

    if figure_entries:
        lines.append("## Optional figures")
        for fig in figure_entries:
            fig_id = fig.get("id") or "figure"
            path = fig.get("path") or ""
            caption = fig.get("caption") or ""
            lines.append(f"- `{fig_id}`: `{path}` - {caption}")
        lines.append("")
        lines.append("Inline render tags (plain markdown, do not wrap in code fences):")
        for tag in build_inline_image_markdown(figure_entries):
            lines.append(tag)
        lines.append("")

    if figure_fallback_mermaid:
        lines.append("## Figure fallback (Mermaid)")
        lines.append("```mermaid")
        lines.extend(figure_fallback_mermaid.splitlines())
        lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def validate_summary_section_order(summary_markdown: str) -> None:
    headings = [
        line.strip()[3:].strip()
        for line in summary_markdown.splitlines()
        if line.strip().startswith("## ")
    ]
    expected = [
        "Objective",
        "Inputs and scope",
        "Anchor variant summary",
        "Per-locus top genes",
        "Cross-locus prioritized genes",
        "Key caveats",
        "Recommended next analyses",
    ]
    if headings[: len(expected)] != expected:
        raise ValueError(
            "Summary section order mismatch. "
            f"Expected first headings {expected}, found {headings[: len(expected)]}."
        )


def generate_optional_figures(
    loci: list[dict[str, Any]],
    figure_output_dir: Path,
    warnings: list[str],
) -> tuple[list[dict[str, Any]], str | None]:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        warnings.append(f"Figure generation skipped: plotting dependency unavailable ({exc}).")
        fallback = "graph LR\nA[GWAS anchors] --> B[Open Targets L2G/coloc]\nB --> C[Candidate gene scoring]\nC --> D[Per-locus ranking]\nD --> E[Cross-locus ranking]"
        return [], fallback

    ensure_parent(figure_output_dir / "dummy.txt")
    figure_entries: list[dict[str, Any]] = []

    # Heatmap: top genes x evidence components
    heat_rows: list[tuple[str, list[float]]] = []
    for locus in loci:
        locus_id = str(locus.get("locus_id") or "")
        for gene in coerce_list_of_dicts(locus.get("candidate_genes"))[:3]:
            evidence = coerce_dict(gene.get("evidence"))
            label = f"{gene.get('symbol')} | {locus_id}"
            row = [
                safe_float(evidence.get("l2g_max")) or 0.0,
                safe_float(evidence.get("coloc_max_h4")) or 0.0,
                min(
                    1.0,
                    len([t for t in as_string_list(evidence.get("eqtl_tissues")) if t != "."])
                    / 3.0,
                ),
                1.0
                if evidence.get("rare_variant_support") == "strong"
                else (0.6 if evidence.get("rare_variant_support") == "nominal" else 0.0),
                1.0
                if evidence.get("coding_support") == "coding"
                else (0.3 if evidence.get("coding_support") == "noncoding" else 0.0),
            ]
            heat_rows.append((label[:50], row))

    if heat_rows:
        labels = [x[0] for x in heat_rows]
        matrix = [x[1] for x in heat_rows]
        fig, ax = plt.subplots(figsize=(8, max(3.5, len(labels) * 0.35)))
        im = ax.imshow(matrix, aspect="auto", vmin=0, vmax=1)
        ax.set_xticks(range(5))
        ax.set_xticklabels(["L2G", "coloc", "eQTL", "burden", "coding"], rotation=25, ha="right")
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)
        ax.set_title("Locus-to-gene evidence heatmap")
        fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        fig.tight_layout()
        heatmap_path = (figure_output_dir / "locus_gene_heatmap.png").resolve()
        fig.savefig(heatmap_path, dpi=180)
        plt.close(fig)
        figure_entries.append(
            {
                "id": "locus_gene_heatmap",
                "path": str(heatmap_path),
                "caption": "Top candidate genes by evidence component across loci",
            }
        )

    # Stacked decomposition for top gene per locus.
    locus_labels: list[str] = []
    l2g_vals: list[float] = []
    coloc_vals: list[float] = []
    eqtl_vals: list[float] = []
    burden_vals: list[float] = []
    coding_vals: list[float] = []

    for locus in loci:
        genes = coerce_list_of_dicts(locus.get("candidate_genes"))
        if not genes:
            continue
        top_gene = genes[0]
        evidence = coerce_dict(top_gene.get("evidence"))
        locus_labels.append(str(locus.get("lead_rsid") or locus.get("locus_id") or "."))
        l2g_vals.append(0.40 * (safe_float(evidence.get("l2g_max")) or 0.0))
        coloc_vals.append(0.25 * (safe_float(evidence.get("coloc_max_h4")) or 0.0))
        eqtl_vals.append(
            0.15
            * min(
                1.0,
                len([t for t in as_string_list(evidence.get("eqtl_tissues")) if t != "."]) / 3.0,
            )
        )
        burden_vals.append(
            0.10
            * (
                1.0
                if evidence.get("rare_variant_support") == "strong"
                else (0.6 if evidence.get("rare_variant_support") == "nominal" else 0.0)
            )
        )
        coding_vals.append(
            0.10
            * (
                1.0
                if evidence.get("coding_support") == "coding"
                else (0.3 if evidence.get("coding_support") == "noncoding" else 0.0)
            )
        )

    if locus_labels:
        fig, ax = plt.subplots(figsize=(max(6, len(locus_labels) * 0.8), 4.2))
        x = range(len(locus_labels))
        bottom = [0.0 for _ in locus_labels]
        for label, vals, color in [
            ("L2G", l2g_vals, "#1f77b4"),
            ("coloc", coloc_vals, "#ff7f0e"),
            ("eQTL", eqtl_vals, "#2ca02c"),
            ("burden", burden_vals, "#d62728"),
            ("coding", coding_vals, "#9467bd"),
        ]:
            ax.bar(x, vals, bottom=bottom, label=label, color=color)
            bottom = [b + v for b, v in zip(bottom, vals)]
        ax.set_xticks(list(x))
        ax.set_xticklabels(locus_labels, rotation=30, ha="right")
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Weighted score contribution")
        ax.set_title("Top-gene score decomposition by locus")
        ax.legend(loc="upper right", fontsize=8)
        fig.tight_layout()
        stack_path = (figure_output_dir / "locus_score_decomposition.png").resolve()
        fig.savefig(stack_path, dpi=180)
        plt.close(fig)
        figure_entries.append(
            {
                "id": "locus_score_decomposition",
                "path": str(stack_path),
                "caption": "Weighted score decomposition for top gene in each locus",
            }
        )

    # Tissue support dotplot.
    tissue_points: list[tuple[str, str]] = []
    for locus in loci:
        for gene in coerce_list_of_dicts(locus.get("candidate_genes"))[:4]:
            symbol = str(gene.get("symbol") or "")
            if not symbol:
                continue
            evidence = coerce_dict(gene.get("evidence"))
            tissues = [t for t in as_string_list(evidence.get("eqtl_tissues")) if t and t != "."]
            hpa = [t for t in as_string_list(evidence.get("hpa_tissue_support")) if t and t != "."]
            for tissue in dedupe_keep_order(tissues + hpa):
                tissue_points.append((symbol, tissue))

    if tissue_points:
        unique_genes = sorted({g for g, _ in tissue_points})
        unique_tissues = sorted({t for _, t in tissue_points})
        gene_index = {g: i for i, g in enumerate(unique_genes)}
        tissue_index = {t: i for i, t in enumerate(unique_tissues)}
        x_vals = [tissue_index[t] for _, t in tissue_points]
        y_vals = [gene_index[g] for g, _ in tissue_points]

        fig, ax = plt.subplots(
            figsize=(max(6, len(unique_tissues) * 0.45), max(3.5, len(unique_genes) * 0.35))
        )
        ax.scatter(x_vals, y_vals, s=35, alpha=0.75)
        ax.set_xticks(range(len(unique_tissues)))
        ax.set_xticklabels(unique_tissues, rotation=45, ha="right")
        ax.set_yticks(range(len(unique_genes)))
        ax.set_yticklabels(unique_genes)
        ax.set_title("Tissue support (GTEx/HPA)")
        fig.tight_layout()
        dot_path = (figure_output_dir / "tissue_support_dotplot.png").resolve()
        fig.savefig(dot_path, dpi=180)
        plt.close(fig)
        figure_entries.append(
            {
                "id": "tissue_support_dotplot",
                "path": str(dot_path),
                "caption": "Gene-by-tissue support dots from GTEx/HPA context",
            }
        )

    return figure_entries, None


def build_anchors(
    input_json: dict[str, Any],
    efo_payload: dict[str, Any],
    warnings: list[str],
    limitations: list[str],
) -> list[dict[str, Any]]:
    trait_query = str(input_json.get("trait_query") or "").strip()
    explicit_efo_id = str(input_json.get("efo_id") or "").strip() or None
    efo_id = explicit_efo_id or efo_payload.get("efo_id")
    show_child_traits = bool(input_json.get("show_child_traits", True))
    max_anchor_associations = int(input_json.get("max_anchor_associations") or 1200)
    max_loci = int(input_json.get("max_loci") or 25)
    phenotype_terms = as_string_list(input_json.get("phenotype_terms"))

    normalized_rows: list[dict[str, Any]] = []

    query_specs: list[dict[str, Any]] = []
    if efo_id:
        query_specs.append({"efo_id": efo_id, "show_child_traits": show_child_traits})
    if trait_query:
        query_specs.append({"efo_trait": trait_query})
    for term in phenotype_terms[:8]:
        query_specs.append({"efo_trait": term})

    if query_specs:
        per_query_limit = max(100, math.ceil(max_anchor_associations / len(query_specs)))
        for query in query_specs:
            try:
                rows = gwas_iter_associations(query, max_rows=per_query_limit)
                for row in rows:
                    normalized = normalize_anchor_row(row)
                    if normalized:
                        normalized_rows.append(normalized)
            except Exception as exc:
                limitations.append(f"GWAS anchor retrieval failed for query {query}: {exc}")

    # seed rsids always participate
    seed_rsids = [
        normalize_rsid(s) for s in as_string_list(input_json.get("seed_rsids")) if normalize_rsid(s)
    ]

    best_by_rsid: dict[str, dict[str, Any]] = {}
    for row in normalized_rows:
        rsid = str(row.get("rsid") or "")
        if not rsid:
            continue
        current = best_by_rsid.get(rsid)
        p = safe_float(row.get("p_value"))
        if current is None:
            best_by_rsid[rsid] = row
            continue
        cp = safe_float(current.get("p_value"))
        if cp is None or (p is not None and p < cp):
            best_by_rsid[rsid] = row

    ranked = sorted(
        best_by_rsid.values(),
        key=lambda r: (
            safe_float(r.get("p_value")) if safe_float(r.get("p_value")) is not None else 1e99
        ),
    )

    anchors: list[dict[str, Any]] = []
    for row in ranked:
        if len(anchors) >= max_loci:
            break
        anchors.append(
            {
                "rsid": row.get("rsid"),
                "lead_trait": row.get("lead_trait") or "",
                "p_value": safe_float(row.get("p_value")),
                "cohort": row.get("cohort") or "",
                "accession_id": row.get("accession_id"),
                "mapped_genes": dedupe_keep_order(as_string_list(row.get("mapped_genes"))),
            }
        )

    current_rsids = {str(anchor.get("rsid")) for anchor in anchors}
    for seed in seed_rsids:
        if seed in current_rsids:
            continue
        if len(anchors) >= max_loci:
            break
        anchors.append(
            {
                "rsid": seed,
                "lead_trait": trait_query,
                "p_value": None,
                "cohort": "",
                "accession_id": None,
                "mapped_genes": [],
            }
        )
        current_rsids.add(seed)

    accession_ids = [str(a.get("accession_id")) for a in anchors if a.get("accession_id")]
    study_index = fetch_gwas_study_metadata(accession_ids, limitations)
    for anchor in anchors:
        accession_id = anchor.get("accession_id")
        if accession_id and accession_id in study_index:
            anchor["cohort"] = study_index[accession_id].get("cohort") or anchor.get("cohort")

    if not anchors:
        warnings.append("No anchors derived from GWAS queries and seed variants.")

    resolve_anchor_coordinates(anchors, warnings, limitations)
    return anchors


def group_anchors_by_locus(anchors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_locus: dict[str, list[dict[str, Any]]] = {}
    for anchor in anchors:
        locus_id = str(anchor.get("locus_id") or f"rsid:{anchor.get('rsid')}")
        by_locus.setdefault(locus_id, []).append(anchor)

    grouped: list[dict[str, Any]] = []
    for locus_id, rows in by_locus.items():
        rows_sorted = sorted(
            rows,
            key=lambda r: (
                safe_float(r.get("p_value")) if safe_float(r.get("p_value")) is not None else 1e99
            ),
        )
        grouped.append(
            {
                "locus_id": locus_id,
                "anchors": rows_sorted,
                "lead_rsid": rows_sorted[0].get("rsid") if rows_sorted else None,
            }
        )
    grouped.sort(
        key=lambda g: (
            safe_float(coerce_list_of_dicts(g.get("anchors"))[0].get("p_value"))
            if coerce_list_of_dicts(g.get("anchors"))
            and safe_float(coerce_list_of_dicts(g.get("anchors"))[0].get("p_value")) is not None
            else 1e99
        )
    )
    return grouped


def map_locus_to_gene(input_json: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    limitations: list[str] = []

    normalized_input: dict[str, Any] = dict(input_json)

    trait_query = str(normalized_input.get("trait_query") or "").strip()
    efo_id_input = str(normalized_input.get("efo_id") or "").strip()
    seed_rsids = [
        normalize_rsid(s)
        for s in as_string_list(normalized_input.get("seed_rsids"))
        if normalize_rsid(s)
    ]

    disable_default_seeds = bool(normalized_input.get("disable_default_seeds", False))
    if trait_query and not seed_rsids and not disable_default_seeds:
        preset = DEFAULT_TRAIT_SEED_RSIDS.get(normalize_trait_key(trait_query))
        if preset:
            seed_rsids = dedupe_keep_order([normalize_rsid(s) or s for s in preset])
            normalized_input["seed_rsids"] = seed_rsids
            warnings.append(
                f"Applied default seed rsIDs for trait '{trait_query}': {', '.join(seed_rsids)}."
            )

    if not trait_query and not efo_id_input and not seed_rsids:
        raise ValueError("Provide at least one anchor source: trait_query, efo_id, or seed_rsids.")

    max_genes_per_locus = int(normalized_input.get("max_genes_per_locus") or 10)
    max_coloc_rows_per_locus = int(normalized_input.get("max_coloc_rows_per_locus") or 100)
    max_eqtl_rows_per_variant = int(normalized_input.get("max_eqtl_rows_per_variant") or 200)
    burden_sets = as_string_list(normalized_input.get("genebass_burden_sets")) or [
        "pLoF",
        "missense|LC",
    ]
    include_clinvar = bool(normalized_input.get("include_clinvar", True))
    include_gnomad_context = bool(normalized_input.get("include_gnomad_context", True))
    include_hpa_tissue_context = bool(normalized_input.get("include_hpa_tissue_context", True))
    include_figures = bool(normalized_input.get("include_figures", False))

    mapping_output_path = Path(
        str(normalized_input.get("mapping_output_path") or "./output/locus_to_gene_mapping.json")
    )
    summary_output_path = Path(
        str(normalized_input.get("summary_output_path") or "./output/locus_to_gene_summary.md")
    )
    figure_output_dir = Path(str(normalized_input.get("figure_output_dir") or "./output/figures"))

    efo_payload = resolve_efo(trait_query, warnings, limitations)
    if efo_id_input:
        efo_payload["efo_id"] = efo_id_input

    anchors = build_anchors(normalized_input, efo_payload, warnings, limitations)
    if not anchors:
        raise ValueError("No anchors remained after normalization.")

    anchor_rsids = dedupe_keep_order([str(a.get("rsid")) for a in anchors if a.get("rsid")])
    trait_terms = dedupe_keep_order(
        [
            trait_query,
            str(efo_payload.get("anchor_label") or ""),
            *as_string_list(efo_payload.get("synonyms"))[:12],
            *as_string_list(normalized_input.get("phenotype_terms")),
        ]
    )

    ot_support = fetch_ot_l2g_coloc_for_anchors(
        anchor_rsids=anchor_rsids,
        trait_terms=trait_terms,
        max_coloc_rows_per_locus=max_coloc_rows_per_locus,
        limitations=limitations,
        warnings=warnings,
    )

    gtex_support = fetch_gtex_support(
        anchors=anchors,
        max_results=max_eqtl_rows_per_variant,
        limitations=limitations,
        warnings=warnings,
    )

    refsnp_annotations = (
        fetch_refsnp_annotations(anchor_rsids, limitations) if include_clinvar else {}
    )

    grouped_loci = group_anchors_by_locus(anchors)

    all_candidate_symbols: list[str] = []
    for locus in grouped_loci:
        locus_symbols: list[str] = []
        for anchor in coerce_list_of_dicts(locus.get("anchors")):
            locus_symbols.extend(as_string_list(anchor.get("mapped_genes")))
            rsid = str(anchor.get("rsid") or "")
            l2g_rows = coerce_list_of_dicts(
                coerce_dict(ot_support.get("per_anchor", {})).get(rsid, {}).get("l2g")
            )
            for row in l2g_rows:
                symbol = str(row.get("symbol") or "").strip()
                if symbol:
                    locus_symbols.append(symbol)

        target_gene = str(normalized_input.get("target_gene") or "").strip()
        if target_gene:
            locus_symbols.append(target_gene)

        locus_symbols = dedupe_keep_order(locus_symbols)
        if not locus_symbols:
            locus_symbols = ["UNMAPPED_GENE"]
        locus["candidate_symbols"] = locus_symbols
        all_candidate_symbols.extend(locus_symbols)

    unique_symbols = dedupe_keep_order(all_candidate_symbols)
    symbol_to_ensembl = resolve_ensembl_ids_for_symbols(unique_symbols, limitations)
    genebass_support = fetch_genebass_support(
        symbol_to_ensembl=symbol_to_ensembl,
        burden_sets=burden_sets,
        trait_terms=trait_terms,
        max_results=int(normalized_input.get("genebass_max_results") or 300),
        limitations=limitations,
    )

    gnomad_constraints = (
        fetch_gnomad_gene_constraints(unique_symbols, limitations) if include_gnomad_context else {}
    )

    hpa_support: dict[str, list[str]] = {}
    if include_hpa_tissue_context:
        limitations.append(
            "Human Protein Atlas API enrichment is not implemented in this script yet; hpa_tissue_support is left empty."
        )

    loci_output: list[dict[str, Any]] = []
    cross_locus_rows: list[dict[str, Any]] = []

    for locus in grouped_loci:
        anchors_in_locus = coerce_list_of_dicts(locus.get("anchors"))
        symbols = as_string_list(locus.get("candidate_symbols"))
        gene_rows: list[dict[str, Any]] = []

        for symbol in symbols:
            l2g_scores: list[float] = []
            coloc_values: list[float] = []
            eqtl_tissues: set[str] = set()
            mapped_hit = False
            clinvar_present = False
            coding_hit = False

            for anchor in anchors_in_locus:
                rsid = str(anchor.get("rsid") or "")
                mapped_genes_upper = {g.upper() for g in as_string_list(anchor.get("mapped_genes"))}
                if symbol.upper() in mapped_genes_upper:
                    mapped_hit = True

                support = coerce_dict(coerce_dict(ot_support.get("per_anchor", {})).get(rsid))
                l2g_rows = coerce_list_of_dicts(support.get("l2g"))
                matched_l2g = [
                    safe_float(row.get("score")) or 0.0
                    for row in l2g_rows
                    if str(row.get("symbol") or "").upper() == symbol.upper()
                ]
                l2g_scores.extend(matched_l2g)

                if matched_l2g:
                    for coloc_row in coerce_list_of_dicts(support.get("coloc")):
                        h4 = safe_float(coloc_row.get("h4"))
                        clpp = safe_float(coloc_row.get("clpp"))
                        coloc_values.append(
                            h4 if h4 is not None else (clpp if clpp is not None else 0.0)
                        )

                tissues = coerce_dict(gtex_support.get(rsid, {})).get(symbol)
                if isinstance(tissues, set):
                    eqtl_tissues.update(tissues)
                elif isinstance(tissues, list):
                    eqtl_tissues.update([str(t) for t in tissues if str(t).strip()])

                annot = coerce_dict(refsnp_annotations.get(rsid))
                genes = {g.upper() for g in as_string_list(annot.get("genes"))}
                coding_genes = {g.upper() for g in as_string_list(annot.get("coding_genes"))}
                if symbol.upper() in genes:
                    clinvar_present = True
                if symbol.upper() in coding_genes:
                    coding_hit = True

            l2g_component = clamp01(max(l2g_scores) if l2g_scores else 0.0)
            coloc_component = clamp01(max(coloc_values) if coloc_values else 0.0)
            if l2g_component <= 0.0 and coloc_component > 0.0:
                # Avoid applying coloc to genes with no gene-level assignment signal.
                coloc_component = 0.0

            relevant_eqtl_tissues = [t for t in sorted(eqtl_tissues) if t and t != "."]
            eqtl_component = clamp01(min(1.0, len(relevant_eqtl_tissues) / 3.0))

            gene_burden = coerce_dict(genebass_support.get(symbol))
            best_burden_p = safe_float(gene_burden.get("best_p"))
            rare_variant_support, burden_component = support_from_burden(best_burden_p)

            if coding_hit:
                coding_support = "coding"
            elif clinvar_present or mapped_hit:
                coding_support = "noncoding"
            else:
                coding_support = "none"

            clinvar_support = "present" if clinvar_present else "none"
            coding_comp = coding_component(coding_support, clinvar_support)

            overall = clamp01(
                0.40 * l2g_component
                + 0.25 * coloc_component
                + 0.15 * eqtl_component
                + 0.10 * burden_component
                + 0.10 * coding_comp
            )
            confidence = confidence_label(overall)

            evidence = {
                "l2g_max": round(l2g_component, 6),
                "coloc_max_h4": round(coloc_component, 6),
                "eqtl_tissues": relevant_eqtl_tissues,
                "rare_variant_support": rare_variant_support,
                "coding_support": coding_support,
                "clinvar_support": clinvar_support,
                "gnomad_context": format_gnomad_context(gnomad_constraints.get(symbol)),
                "hpa_tissue_support": hpa_support.get(symbol, []),
            }

            rationale: list[str] = []
            gene_limits: list[str] = []

            if l2g_component > 0:
                rationale.append(
                    f"Open Targets L2G max score {l2g_component:.3f} for matched anchor locus."
                )
            else:
                gene_limits.append("No matched L2G support found for this gene in anchored loci.")

            if coloc_component > 0:
                rationale.append(
                    f"Colocalisation signal present (max h4/clpp proxy {coloc_component:.3f})."
                )
            else:
                gene_limits.append("No coloc support assigned to this gene in matched loci.")

            if relevant_eqtl_tissues:
                rationale.append(
                    f"GTEx eQTL support observed in {len(relevant_eqtl_tissues)} tissue(s): {', '.join(relevant_eqtl_tissues[:4])}."
                )
            else:
                gene_limits.append("No GTEx eQTL rows mapped to this gene from anchor variants.")

            if best_burden_p is not None:
                rationale.append(
                    f"Genebass burden support is {rare_variant_support} (best trait-matched p={best_burden_p:.3g})."
                )
            else:
                gene_limits.append("No trait-matched Genebass burden support found.")

            if coding_support == "coding":
                rationale.append("Coding consequence support present from rsID annotation.")
            elif coding_support == "noncoding":
                rationale.append(
                    "Locus membership or noncoding variant annotation supports proximity to this gene."
                )
            else:
                gene_limits.append("No coding or in-gene annotation support identified.")

            gene_row = {
                "symbol": symbol,
                "ensembl_id": symbol_to_ensembl.get(symbol),
                "overall_score": round(overall, 6),
                "confidence": confidence,
                "evidence": evidence,
                "rationale": rationale,
                "limitations": gene_limits,
            }
            gene_rows.append(gene_row)
            cross_locus_rows.append({"symbol": symbol, "score": overall})

        gene_rows.sort(
            key=lambda row: (
                -safe_float(row.get("overall_score"))
                if safe_float(row.get("overall_score")) is not None
                else 0.0,
                str(row.get("symbol") or ""),
            )
        )
        gene_rows = gene_rows[:max_genes_per_locus]

        loci_output.append(
            {
                "locus_id": locus.get("locus_id"),
                "lead_rsid": locus.get("lead_rsid"),
                "candidate_genes": gene_rows,
            }
        )

    if not loci_output:
        raise ValueError("No loci available after candidate gene scoring.")

    # Cross-locus aggregate ranking.
    aggregate: dict[str, list[float]] = {}
    for locus in loci_output:
        for gene in coerce_list_of_dicts(locus.get("candidate_genes")):
            symbol = str(gene.get("symbol") or "")
            score = safe_float(gene.get("overall_score"))
            if not symbol or score is None:
                continue
            aggregate.setdefault(symbol, []).append(score)

    cross_locus_ranked_genes: list[dict[str, Any]] = []
    for symbol, scores in aggregate.items():
        cross_locus_ranked_genes.append(
            {
                "symbol": symbol,
                "supporting_loci": len(scores),
                "mean_score": round(sum(scores) / len(scores), 6),
                "max_score": round(max(scores), 6),
            }
        )
    cross_locus_ranked_genes.sort(
        key=lambda row: (
            -safe_float(row.get("max_score"))
            if safe_float(row.get("max_score")) is not None
            else 0.0,
            -safe_float(row.get("mean_score"))
            if safe_float(row.get("mean_score")) is not None
            else 0.0,
            str(row.get("symbol") or ""),
        )
    )

    # QC gates.
    for locus in loci_output:
        genes = coerce_list_of_dicts(locus.get("candidate_genes"))
        if not genes:
            raise ValueError(f"Locus {locus.get('locus_id')} has no candidate genes after scoring.")
        for gene in genes:
            if "overall_score" not in gene:
                raise ValueError(
                    f"Gene row missing overall_score in locus {locus.get('locus_id')}."
                )
            score = safe_float(gene.get("overall_score"))
            if score is None or score < 0 or score > 1:
                raise ValueError(
                    f"overall_score outside [0,1] for gene {gene.get('symbol')} in locus {locus.get('locus_id')}"
                )

    mapping_payload: dict[str, Any] = {
        "meta": {
            "trait_query": trait_query,
            "efo_id": efo_payload.get("efo_id"),
            "generated_at": now_iso(),
            "sources_queried": [
                "efo-ontology-skill",
                "gwas-catalog-skill",
                "variant-coordinate-finder-skill",
                "opentargets-skill",
                "gtex-eqtl-skill",
                "genebass-gene-burden-skill",
                "clinvar-variation-skill"
                if include_clinvar
                else "clinvar-variation-skill(skipped)",
                "gnomad-graphql-skill"
                if include_gnomad_context
                else "gnomad-graphql-skill(skipped)",
                "human-protein-atlas-skill"
                if include_hpa_tissue_context
                else "human-protein-atlas-skill(skipped)",
            ],
        },
        "anchors": anchors,
        "loci": loci_output,
        "cross_locus_ranked_genes": cross_locus_ranked_genes,
        "warnings": dedupe_keep_order(warnings),
        "limitations": dedupe_keep_order(limitations),
    }

    figure_entries: list[dict[str, Any]] = []
    figure_fallback_mermaid: str | None = None
    if include_figures:
        figure_entries, figure_fallback_mermaid = generate_optional_figures(
            loci_output, figure_output_dir, warnings
        )
        if not figure_entries and not figure_fallback_mermaid:
            figure_fallback_mermaid = (
                "graph LR\n"
                "A[Anchor variants] --> B[Locus grouping]\n"
                "B --> C[Evidence scoring]\n"
                "C --> D[Per-locus top genes]\n"
                "D --> E[Cross-locus ranking]"
            )
            warnings.append(
                "No figure PNGs were generated; emitted Mermaid fallback visualization."
            )
        if figure_entries:
            mapping_payload["figures"] = figure_entries
            mapping_payload["inline_image_markdown"] = build_inline_image_markdown(figure_entries)

    summary = build_summary_markdown(mapping_payload, figure_entries, figure_fallback_mermaid)
    validate_summary_section_order(summary)

    ensure_parent(mapping_output_path)
    ensure_parent(summary_output_path)

    mapping_output_path.write_text(json.dumps(mapping_payload, indent=2), encoding="utf-8")
    summary_output_path.write_text(summary, encoding="utf-8")

    return {
        "status": "ok",
        "mapping_output_path": str(mapping_output_path),
        "summary_output_path": str(summary_output_path),
        "figure_paths": [str(fig.get("path")) for fig in figure_entries],
        "inline_image_markdown": build_inline_image_markdown(figure_entries),
        "render_instructions": (
            "Paste `inline_image_markdown` lines directly in the chat as plain markdown. "
            "Do not wrap them in code fences."
        ),
        "warnings": dedupe_keep_order(warnings),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map GWAS loci to ranked candidate genes.")
    parser.add_argument("--input-json", help="Path to input JSON file.")
    parser.add_argument(
        "--trait-query", help="Trait/disease free-text query (for example: type 2 diabetes)."
    )
    parser.add_argument("--efo-id", help="Explicit EFO ID anchor (for example: EFO_0001360).")
    parser.add_argument(
        "--seed-rsid",
        action="append",
        default=[],
        help="Seed rsID anchor (repeatable), for example: --seed-rsid rs7903146",
    )
    parser.add_argument("--target-gene", help="Optional target gene to highlight.")
    parser.add_argument(
        "--include-figures",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Render optional figures. Trait-only runs default to true unless --no-include-figures is set.",
    )
    parser.add_argument("--mapping-output-path", help="Optional mapping JSON output path.")
    parser.add_argument("--summary-output-path", help="Optional summary markdown output path.")
    parser.add_argument("--figure-output-dir", help="Optional figure output directory.")
    parser.add_argument(
        "--print-inline-image-markdown",
        action="store_true",
        help="Print render-ready markdown image tags as plain lines (not code-fenced).",
    )
    parser.add_argument("--print-result", action="store_true", help="Print JSON result to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload: dict[str, Any]
    if args.input_json:
        input_path = Path(args.input_json)
        try:
            payload = json.loads(input_path.read_text(encoding="utf-8"))
        except Exception as exc:
            err = {"status": "error", "error": f"Could not parse input JSON: {exc}"}
            print(json.dumps(err, indent=2))
            return 2
        if args.include_figures is not None:
            payload["include_figures"] = bool(args.include_figures)
    else:
        payload = {}
        if args.trait_query:
            payload["trait_query"] = args.trait_query
        if args.efo_id:
            payload["efo_id"] = args.efo_id
        seed_rsids = [normalize_rsid(s) for s in args.seed_rsid if normalize_rsid(s)]
        if seed_rsids:
            payload["seed_rsids"] = seed_rsids
        if args.target_gene:
            payload["target_gene"] = args.target_gene
        if args.include_figures is None:
            payload["include_figures"] = True
        else:
            payload["include_figures"] = bool(args.include_figures)
        if args.mapping_output_path:
            payload["mapping_output_path"] = args.mapping_output_path
        if args.summary_output_path:
            payload["summary_output_path"] = args.summary_output_path
        if args.figure_output_dir:
            payload["figure_output_dir"] = args.figure_output_dir

    try:
        result = map_locus_to_gene(payload)
    except Exception as exc:
        err = {"status": "error", "error": str(exc)}
        print(json.dumps(err, indent=2))
        return 1

    if args.print_inline_image_markdown:
        for line in as_string_list(result.get("inline_image_markdown")):
            print(line)
    if args.print_result:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
