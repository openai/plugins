#!/usr/bin/env python3
"""Bounded target-evidence retrieval using PubMed and ClinicalTrials.gov."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Any

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV_STUDIES = "https://clinicaltrials.gov/api/v2/studies"
USER_AGENT = "research-target-evidence/0.1"


class Retriever:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self.last_request_by_host: dict[str, float] = {}

    def _pace(self, host: str) -> None:
        minimum_interval = 0.38 if host.endswith("ncbi.nlm.nih.gov") else 0.05
        elapsed = time.monotonic() - self.last_request_by_host.get(host, 0.0)
        if elapsed < minimum_interval:
            time.sleep(minimum_interval - elapsed)

    def get(self, base_url: str, params: dict[str, Any], label: str) -> bytes:
        query = urllib.parse.urlencode(params, doseq=True)
        url = f"{base_url}?{query}" if query else base_url
        host = urllib.parse.urlparse(url).netloc
        last_error: Exception | None = None
        for attempt in range(1, 4):
            self._pace(host)
            started = time.monotonic()
            status = 0
            body = b""
            try:
                request = urllib.request.Request(
                    url, headers={"User-Agent": USER_AGENT}
                )
                with urllib.request.urlopen(request, timeout=20) as response:
                    status = int(response.status)
                    body = response.read()
                elapsed_ms = round((time.monotonic() - started) * 1000)
                self.last_request_by_host[host] = time.monotonic()
                self.requests.append(
                    {
                        "label": label,
                        "host": host,
                        "elapsed_ms": elapsed_ms,
                        "bytes": len(body),
                        "status": status,
                        "attempt": attempt,
                    }
                )
                return body
            except urllib.error.HTTPError as exc:
                status = exc.code
                last_error = exc
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
            elapsed_ms = round((time.monotonic() - started) * 1000)
            self.last_request_by_host[host] = time.monotonic()
            self.requests.append(
                {
                    "label": label,
                    "host": host,
                    "elapsed_ms": elapsed_ms,
                    "bytes": len(body),
                    "status": status,
                    "attempt": attempt,
                    "error": str(last_error),
                }
            )
            if status not in {429, 500, 502, 503, 504} and status != 0:
                break
            time.sleep(0.8 * (2 ** (attempt - 1)))
        raise RuntimeError(f"Request failed for {label}: {last_error}")


def _ncbi_params(params: dict[str, Any]) -> dict[str, Any]:
    merged = dict(params)
    api_key = os.environ.get("NCBI_API_KEY") or os.environ.get("NCBI_EUTILS_API_KEY")
    if api_key:
        merged["api_key"] = api_key
    if os.environ.get("NCBI_TOOL"):
        merged["tool"] = os.environ["NCBI_TOOL"]
    if os.environ.get("NCBI_EMAIL"):
        merged["email"] = os.environ["NCBI_EMAIL"]
    return merged


def _json_request(
    retriever: Retriever, base_url: str, params: dict[str, Any], label: str
) -> dict[str, Any]:
    return json.loads(retriever.get(base_url, params, label).decode("utf-8"))


def _text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def _year(article: ET.Element) -> str | None:
    for path in (
        "Journal/JournalIssue/PubDate/Year",
        "ArticleDate/Year",
        "Journal/JournalIssue/PubDate/MedlineDate",
    ):
        value = article.findtext(path)
        if value:
            match = re.search(r"(?:19|20)\d{2}", value)
            return match.group(0) if match else value[:20]
    return None


def _classify_paper(title: str, abstract: str, publication_types: list[str]) -> str:
    text = f"{title} {abstract} {' '.join(publication_types)}".lower()
    human_text = text.replace("patient-derived", "")
    clinical_publication = any(
        "clinical trial" in publication_type.lower()
        for publication_type in publication_types
    )
    human_terms = (
        "phase 1",
        "phase i",
        "phase 2",
        "phase ii",
        "patients were",
        "patients with",
        "patients received",
        "patients treated",
        "participants",
        "first-in-human",
        "human cancer",
        "human tissue",
    )
    preclinical_terms = (
        "mouse",
        "mice",
        "murine",
        "xenograft",
        "cell line",
        "in vitro",
        "in vivo model",
        "preclinical",
    )
    human_score = (3 if clinical_publication else 0) + sum(
        term in human_text for term in human_terms
    )
    contextual_publication = any(
        publication_type.lower() in {"review", "editorial", "comment"}
        for publication_type in publication_types
    )
    if contextual_publication and not clinical_publication:
        human_score = 0
    preclinical_score = sum(term in text for term in preclinical_terms)
    if preclinical_score > human_score:
        return "preclinical"
    if human_score:
        return "human"
    if preclinical_score:
        return "preclinical"
    return "other"


def _parse_pubmed_xml(
    body: bytes, memberships: dict[str, list[str]]
) -> list[dict[str, Any]]:
    root = ET.fromstring(body)
    papers: list[dict[str, Any]] = []
    for node in root.findall("PubmedArticle"):
        citation = node.find("MedlineCitation")
        article = citation.find("Article") if citation is not None else None
        if citation is None or article is None:
            continue
        pmid = citation.findtext("PMID") or ""
        title = _text(article.find("ArticleTitle"))
        abstract = " ".join(
            _text(item)
            for item in article.findall("Abstract/AbstractText")
            if _text(item)
        )
        publication_types = [
            _text(item)
            for item in article.findall("PublicationTypeList/PublicationType")
        ]
        ids = {
            item.attrib.get("IdType", ""): (item.text or "")
            for item in node.findall("PubmedData/ArticleIdList/ArticleId")
        }
        papers.append(
            {
                "pmid": pmid,
                "title": title,
                "year": _year(article),
                "journal": article.findtext("Journal/Title"),
                "doi": ids.get("doi"),
                "publication_types": publication_types,
                "classification": _classify_paper(title, abstract, publication_types),
                "matched_queries": memberships.get(pmid, []),
                "abstract_excerpt": abstract[:1200],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }
        )
    return papers


def _round_robin_ids(groups: dict[str, list[str]], limit: int) -> list[str]:
    selected: list[str] = []
    seen: set[str] = set()
    positions = defaultdict(int)
    while len(selected) < limit:
        added = False
        for name, values in groups.items():
            position = positions[name]
            while position < len(values) and values[position] in seen:
                position += 1
            positions[name] = position + 1
            if position < len(values):
                selected.append(values[position])
                seen.add(values[position])
                added = True
                if len(selected) >= limit:
                    break
        if not added:
            break
    return selected


def _query_pubmed(
    retriever: Retriever, target: str, max_papers: int
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    query_plan = {
        "biology": f"{target}[Title/Abstract] AND (biology[Title/Abstract] OR signaling[Title/Abstract] OR expression[Title/Abstract] OR function[Title/Abstract])",
        "human": f'{target}[Title/Abstract] AND (clinical trial[Publication Type] OR "phase 1"[Title/Abstract] OR patient[Title/Abstract] OR safety[Title/Abstract])',
        "modalities": f'{target}[Title/Abstract] AND (antibody[Title/Abstract] OR ADC[Title/Abstract] OR "CAR T"[Title/Abstract] OR "chimeric antigen receptor"[Title/Abstract])',
        "safety": f'{target}[Title/Abstract] AND ("normal tissue"[Title/Abstract] OR toxicity[Title/Abstract] OR safety[Title/Abstract] OR adverse[Title/Abstract])',
    }
    groups: dict[str, list[str]] = {}
    memberships: dict[str, list[str]] = defaultdict(list)
    for name, term in query_plan.items():
        data = _json_request(
            retriever,
            f"{EUTILS_BASE}/esearch.fcgi",
            _ncbi_params(
                {
                    "db": "pubmed",
                    "term": term,
                    "retmode": "json",
                    "retmax": 12,
                    "sort": "relevance",
                }
            ),
            f"pubmed-esearch-{name}",
        )
        ids = data.get("esearchresult", {}).get("idlist", [])
        groups[name] = ids
        for pmid in ids:
            memberships[pmid].append(name)

    candidate_ids = _round_robin_ids(groups, max(max_papers * 3, max_papers))
    if not candidate_ids:
        return query_plan, []

    summary = _json_request(
        retriever,
        f"{EUTILS_BASE}/esummary.fcgi",
        _ncbi_params(
            {"db": "pubmed", "id": ",".join(candidate_ids), "retmode": "json"}
        ),
        "pubmed-esummary-selected",
    )
    result = summary.get("result", {})
    target_token = target.lower()

    def rank(pmid: str) -> tuple[int, int]:
        title = str(result.get(pmid, {}).get("title") or "").lower()
        title_score = 6 if target_token in title else 0
        evidence_score = sum(
            term in title
            for term in (
                "clinical",
                "phase",
                "patient",
                "antibody",
                "car-t",
                "chimeric antigen receptor",
                "antibody-drug conjugate",
                "safety",
                "normal tissue",
                "expression",
            )
        )
        return title_score + evidence_score + len(
            memberships[pmid]
        ), -candidate_ids.index(pmid)

    selected = sorted(candidate_ids, key=rank, reverse=True)[:max_papers]
    xml_body = retriever.get(
        f"{EUTILS_BASE}/efetch.fcgi",
        _ncbi_params({"db": "pubmed", "id": ",".join(selected), "retmode": "xml"}),
        "pubmed-efetch-selected",
    )
    return query_plan, _parse_pubmed_xml(xml_body, memberships)


def _serious_events(study: dict[str, Any]) -> list[dict[str, Any]]:
    module = study.get("resultsSection", {}).get("adverseEventsModule", {})
    events = module.get("seriousEvents", [])
    summarized: list[dict[str, Any]] = []
    for event in events:
        affected = sum(
            int(stat.get("numAffected") or 0) for stat in event.get("stats", [])
        )
        if affected:
            summarized.append(
                {
                    "term": event.get("term"),
                    "organ_system": event.get("organSystem"),
                    "num_affected": affected,
                }
            )
    summarized.sort(key=lambda item: item["num_affected"], reverse=True)
    return summarized[:8]


def _trial_relevance(study: dict[str, Any], target: str) -> int:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    descriptions = protocol.get("descriptionModule", {})
    interventions = protocol.get("armsInterventionsModule", {}).get("interventions", [])
    target_pattern = re.compile(rf"\b{re.escape(target)}\b", re.IGNORECASE)
    title_text = " ".join(
        str(identification.get(field) or "")
        for field in ("briefTitle", "officialTitle")
    )
    intervention_text = " ".join(
        " ".join([str(item.get("name") or ""), *map(str, item.get("otherNames", []))])
        for item in interventions
    )
    summary_text = " ".join(
        str(descriptions.get(field) or "")
        for field in ("briefSummary", "detailedDescription")
    )
    condition_text = " ".join(
        map(str, protocol.get("conditionsModule", {}).get("conditions", []))
    )
    title_match = bool(target_pattern.search(title_text))
    intervention_match = bool(target_pattern.search(intervention_text))
    summary_match = bool(target_pattern.search(summary_text))
    condition_match = bool(target_pattern.search(condition_text))
    if (
        summary_match
        and not title_match
        and not intervention_match
        and not condition_match
        and protocol.get("designModule", {}).get("studyType") != "INTERVENTIONAL"
    ):
        return 0
    return (
        5 * title_match + 5 * intervention_match + 2 * summary_match + condition_match
    )


def _trial_program_tokens(
    study: dict[str, Any], *, include_interventions: bool = True
) -> set[str]:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    interventions = protocol.get("armsInterventionsModule", {}).get("interventions", [])
    values = [
        str(identification.get("briefTitle") or ""),
        str(identification.get("officialTitle") or ""),
    ]
    if include_interventions:
        values.extend(str(item.get("name") or "") for item in interventions)
        values.extend(
            str(alias) for item in interventions for alias in item.get("otherNames", [])
        )
    text = " ".join(values).lower()
    generic = {
        "advanced",
        "antibody",
        "cancer",
        "cells",
        "clinical",
        "combination",
        "escalation",
        "expansion",
        "malignancies",
        "patients",
        "phase",
        "solid",
        "study",
        "therapy",
        "treatment",
        "tumor",
        "tumors",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9-]{4,}", text)
        if token not in generic
    }


def _parse_trials(
    data: dict[str, Any], target: str, max_trials: int
) -> list[dict[str, Any]]:
    trials: list[dict[str, Any]] = []
    ranked_studies = [
        (study, _trial_relevance(study, target)) for study in data.get("studies", [])
    ]
    direct_program_tokens = set().union(
        *(
            _trial_program_tokens(study, include_interventions=False)
            for study, relevance in ranked_studies
            if relevance >= 5
        )
    )
    for study, relevance in ranked_studies:
        if relevance == 0 or (
            relevance == 2
            and not (_trial_program_tokens(study) & direct_program_tokens)
        ):
            continue
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        interventions = protocol.get("armsInterventionsModule", {}).get(
            "interventions", []
        )
        nct_id = identification.get("nctId")
        outcomes = (
            study.get("resultsSection", {})
            .get("outcomeMeasuresModule", {})
            .get("outcomeMeasures", [])
        )
        trials.append(
            {
                "nct_id": nct_id,
                "title": identification.get("briefTitle"),
                "status": status.get("overallStatus"),
                "why_stopped": status.get("whyStopped"),
                "phases": design.get("phases", []),
                "enrollment": design.get("enrollmentInfo"),
                "conditions": protocol.get("conditionsModule", {}).get(
                    "conditions", []
                ),
                "interventions": [
                    {
                        "name": item.get("name"),
                        "type": item.get("type"),
                        "other_names": item.get("otherNames", []),
                    }
                    for item in interventions[:8]
                ],
                "brief_summary": protocol.get("descriptionModule", {}).get(
                    "briefSummary"
                ),
                "has_results": bool(study.get("hasResults")),
                "primary_outcomes": [
                    {
                        "title": outcome.get("title"),
                        "description": outcome.get("description"),
                    }
                    for outcome in outcomes
                    if outcome.get("type") == "PRIMARY"
                ][:5],
                "serious_adverse_events": _serious_events(study),
                "target_relevance": relevance,
                "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None,
            }
        )
    trials.sort(
        key=lambda item: (
            -item["target_relevance"],
            not item["has_results"],
            item["status"] or "",
        )
    )
    return trials[:max_trials]


def _query_trials(
    retriever: Retriever, target: str, max_trials: int
) -> tuple[int | None, list[dict[str, Any]]]:
    data = _json_request(
        retriever,
        CTGOV_STUDIES,
        {
            "query.term": target,
            "pageSize": 100,
            "countTotal": "true",
            "format": "json",
        },
        "clinicaltrials-target-search",
    )
    return data.get("totalCount"), _parse_trials(data, target, max_trials)


def _telemetry(retriever: Retriever, started: float) -> dict[str, Any]:
    return {
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "request_attempts": len(retriever.requests),
        "network_requests": len(retriever.requests),
        "retries": sum(request["attempt"] > 1 for request in retriever.requests),
        "rate_limit_events": sum(
            request["status"] == 429 for request in retriever.requests
        ),
        "bytes_received": sum(request["bytes"] for request in retriever.requests),
        "requests": retriever.requests,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument(
        "--questions", nargs="+", default=["biology", "programs", "safety"]
    )
    parser.add_argument("--separate-human-preclinical", action="store_true")
    parser.add_argument("--max-papers", type=int, default=14)
    parser.add_argument("--max-trials", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = time.monotonic()
    retriever = Retriever()
    try:
        query_plan, papers = _query_pubmed(retriever, args.target, args.max_papers)
        total_trials, trials = _query_trials(retriever, args.target, args.max_trials)
        grouped_papers = {
            group: [paper for paper in papers if paper["classification"] == group]
            for group in ("human", "preclinical", "other")
        }
        output = {
            "ok": True,
            "target": args.target,
            "questions": args.questions,
            "separate_human_preclinical": args.separate_human_preclinical,
            "query_plan": query_plan,
            "papers": grouped_papers,
            "trials": {
                "total_count": total_trials,
                "records": trials,
            },
            "limitations": [
                "PubMed retrieval is relevance-ranked and bounded; it is not a systematic review.",
                "Paper classification is heuristic and should be checked during synthesis.",
                "ClinicalTrials.gov event counts are not automatically treatment-attributed.",
                "Current program status is limited to the retrieved registry snapshot.",
            ],
            "telemetry": _telemetry(retriever, started),
        }
    except Exception as exc:  # noqa: BLE001
        output = {
            "ok": False,
            "target": args.target,
            "error": {"type": type(exc).__name__, "message": str(exc)},
            "telemetry": _telemetry(retriever, started),
        }
    json.dump(output, sys.stdout, separators=(",", ":"), ensure_ascii=True)
    sys.stdout.write("\n")
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
