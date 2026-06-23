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
USER_AGENT = "research-target-evidence/0.2"
MAX_TARGETS = 6
DEFAULT_OUTPUT_CHARS = 30_000


def _safe_error(error: Exception | None) -> str:
    message = str(error or "unknown error")
    return re.sub(r"([?&]api_key=)[^&\s]+", r"\1<redacted>", message)


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
                    "error": _safe_error(last_error),
                }
            )
            if status not in {429, 500, 502, 503, 504} and status != 0:
                break
            time.sleep(0.8 * (2 ** (attempt - 1)))
        raise RuntimeError(f"Request failed for {label}: {_safe_error(last_error)}")


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


def _clip(text: str, limit: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    clipped = normalized[: max(0, limit - 1)].rsplit(" ", 1)[0]
    return f"{clipped}..." if clipped else normalized[:limit]


def _best_excerpt(
    abstract: str,
    terms: tuple[str, ...],
    limit: int = 350,
    *,
    require_term: bool = False,
) -> str:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", " ".join(abstract.split()))
        if sentence.strip()
    ]
    if not sentences:
        return ""

    def score(sentence: str) -> tuple[int, int, int]:
        lowered = sentence.lower()
        term_score = sum(term in lowered for term in terms)
        numeric_score = int(bool(re.search(r"\b\d+(?:\.\d+)?%?\b", sentence)))
        return term_score, numeric_score, -sentences.index(sentence)

    best = max(sentences, key=score)
    if require_term and score(best)[0] == 0:
        return ""
    if score(best)[:2] == (0, 0):
        best = sentences[0]
    return _clip(best, limit)


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
                "classification": _classify_paper(title, abstract, publication_types),
                "matched_queries": memberships.get(pmid, []),
                "result_excerpt": _best_excerpt(
                    abstract,
                    (
                        "response",
                        "survival",
                        "progression",
                        "efficacy",
                        "randomized",
                        "patients",
                        "participants",
                        "objective",
                        "complete remission",
                        "partial remission",
                        "did not",
                        "no response",
                    ),
                ),
                "safety_excerpt": _best_excerpt(
                    abstract,
                    (
                        "adverse",
                        "safety",
                        "toxicity",
                        "cytokine",
                        "neutropenia",
                        "diarrhea",
                        "nausea",
                        "vomiting",
                        "neuropathy",
                        "pneumonitis",
                        "death",
                        "grade 3",
                        "grade 4",
                        "tolerated",
                    ),
                    require_term=True,
                ),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }
        )
    return papers


def _select_paper_cards(
    papers: list[dict[str, Any]], max_papers: int
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []

    def take(predicate: Any) -> None:
        paper = next(
            (item for item in papers if item not in selected and predicate(item)), None
        )
        if paper is not None and len(selected) < max_papers:
            selected.append(paper)

    take(lambda item: "landmark" in item["matched_queries"])
    take(lambda item: "landmark" in item["matched_queries"])
    take(lambda item: item["classification"] == "human")
    take(lambda item: "safety" in item["matched_queries"])
    take(lambda item: item["classification"] == "preclinical")
    take(lambda item: "biology" in item["matched_queries"])
    for paper in papers:
        if paper not in selected and len(selected) < max_papers:
            selected.append(paper)
    return selected


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
    retriever: Retriever,
    target: str,
    max_papers: int,
) -> tuple[dict[str, str], list[dict[str, Any]], int]:
    query_plan = {
        "biology": f"{target}[Title/Abstract] AND (biology[Title/Abstract] OR signaling[Title/Abstract] OR expression[Title/Abstract] OR function[Title/Abstract])",
        "human": f"{target}[Title/Abstract] AND (clinical trial[Publication Type] OR phase[Title/Abstract] OR randomized[Title/Abstract] OR patient[Title/Abstract] OR safety[Title/Abstract])",
        "modalities": f'{target}[Title/Abstract] AND (antibody[Title/Abstract] OR ADC[Title/Abstract] OR "CAR T"[Title/Abstract] OR "chimeric antigen receptor"[Title/Abstract])',
        "safety": f'{target}[Title/Abstract] AND ("normal tissue"[Title/Abstract] OR toxicity[Title/Abstract] OR safety[Title/Abstract] OR adverse[Title/Abstract])',
        "landmark": f'{target}[Title/Abstract] AND (randomized[Title/Abstract] OR randomised[Title/Abstract] OR "phase 2"[Title/Abstract] OR "phase II"[Title/Abstract] OR "phase 3"[Title/Abstract] OR "phase III"[Title/Abstract] OR terminated[Title/Abstract] OR failed[Title/Abstract])',
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
                    "retmax": 30 if name == "landmark" else 12,
                    "sort": "relevance",
                }
            ),
            f"pubmed-esearch-{name}",
        )
        ids = data.get("esearchresult", {}).get("idlist", [])
        groups[name] = ids
        for pmid in ids:
            memberships[pmid].append(name)

    available_count = len(memberships)
    candidate_ids = _round_robin_ids(groups, max(max_papers * 10, 80))
    if not candidate_ids:
        return query_plan, [], available_count

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
    candidate_positions = {
        pmid: position for position, pmid in enumerate(candidate_ids)
    }

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
        ), -candidate_positions.get(pmid, len(candidate_ids))

    def landmark_rank(pmid: str) -> tuple[int, int]:
        title = str(result.get(pmid, {}).get("title") or "").lower()
        evidence_score = sum(
            weight * (term in title)
            for term, weight in (
                ("randomized", 5),
                ("randomised", 5),
                ("placebo", 3),
                ("phase iii", 3),
                ("phase 3", 3),
                ("phase ii", 2),
                ("phase 2", 2),
                ("terminated", 2),
                ("failed", 2),
            )
        )
        return evidence_score, -candidate_positions.get(pmid, len(candidate_ids))

    ranked = sorted(candidate_ids, key=rank, reverse=True)
    fetch_limit = min(len(ranked), max(max_papers * 2, max_papers))
    selected: list[str] = []
    for group_name in ("landmark", "human", "safety", "biology", "modalities"):
        group_ranked = sorted(
            groups.get(group_name, []),
            key=landmark_rank if group_name == "landmark" else rank,
            reverse=True,
        )
        first = next((pmid for pmid in group_ranked if pmid not in selected), None)
        if first:
            selected.append(first)
    for pmid in ranked:
        if pmid not in selected and len(selected) < fetch_limit:
            selected.append(pmid)
    selected = selected[:fetch_limit]
    xml_body = retriever.get(
        f"{EUTILS_BASE}/efetch.fcgi",
        _ncbi_params({"db": "pubmed", "id": ",".join(selected), "retmode": "xml"}),
        "pubmed-efetch-selected",
    )
    papers = _parse_pubmed_xml(xml_body, memberships)
    return query_plan, _select_paper_cards(papers, max_papers), available_count


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
    return summarized[:5]


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
        " ".join(
            [
                str(item.get("name") or ""),
                *map(str, item.get("otherNames", [])),
                str(item.get("description") or ""),
            ]
        )
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


def _trial_phase_score(study: dict[str, Any]) -> int:
    phases = study.get("protocolSection", {}).get("designModule", {}).get("phases", [])
    scores = {
        "EARLY_PHASE1": 1,
        "PHASE1": 1,
        "PHASE2": 2,
        "PHASE3": 3,
        "PHASE4": 4,
    }
    return max((scores.get(phase, 0) for phase in phases), default=0)


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
                "interventions": [
                    {
                        "name": item.get("name"),
                        "type": item.get("type"),
                        "other_names": item.get("otherNames", []),
                    }
                    for item in interventions[:6]
                ],
                "has_results": bool(study.get("hasResults")),
                "primary_outcomes": [
                    outcome.get("title")
                    for outcome in outcomes
                    if outcome.get("type") == "PRIMARY"
                ][:3],
                "serious_adverse_events": _serious_events(study),
                "target_relevance": relevance,
                "phase_score": _trial_phase_score(study),
                "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None,
            }
        )
    trials.sort(
        key=lambda item: (
            -(
                item["target_relevance"]
                + 6 * item["has_results"]
                + 2 * item["phase_score"]
            ),
            -item["target_relevance"],
            not item["has_results"],
            -item["phase_score"],
            item["status"] or "",
        )
    )
    return trials[:max_trials]


def _query_trials(
    retriever: Retriever, target: str, max_trials: int
) -> tuple[int | None, int, list[dict[str, Any]]]:
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
    records = _parse_trials(data, target, 100)
    return data.get("totalCount"), len(records), records[:max_trials]


def _telemetry(
    retriever: Retriever, started: float, *, include_requests: bool = False
) -> dict[str, Any]:
    telemetry = {
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "request_attempts": len(retriever.requests),
        "network_requests": len(retriever.requests),
        "retries": sum(request["attempt"] > 1 for request in retriever.requests),
        "rate_limit_events": sum(
            request["status"] == 429 for request in retriever.requests
        ),
        "bytes_received": sum(request["bytes"] for request in retriever.requests),
    }
    if include_requests:
        telemetry["requests"] = retriever.requests
    return telemetry


def _compact_trial(trial: dict[str, Any]) -> dict[str, Any]:
    programs: list[str] = []
    seen: set[str] = set()
    for intervention in trial.get("interventions", []):
        name = " ".join(str(intervention.get("name") or "").split())
        if name and name.lower() not in seen:
            programs.append(name)
            seen.add(name.lower())
    return {
        "nct_id": trial.get("nct_id"),
        "title": _clip(str(trial.get("title") or ""), 220),
        "status": trial.get("status"),
        "why_stopped": _clip(str(trial.get("why_stopped") or ""), 180) or None,
        "phases": trial.get("phases", []),
        "enrollment": trial.get("enrollment"),
        "programs": programs[:4],
        "has_results": trial.get("has_results", False),
        "primary_outcomes": [
            _clip(str(title or ""), 180)
            for title in trial.get("primary_outcomes", [])[:2]
        ],
        "serious_adverse_events": trial.get("serious_adverse_events", [])[:5],
        "url": trial.get("url"),
    }


def _target_evidence(
    retriever: Retriever, target: str, max_papers: int, max_trials: int
) -> dict[str, Any]:
    discovery_limit = max(max_trials * 3, 15)
    total_trials, relevant_trials, trial_records = _query_trials(
        retriever, target, discovery_limit
    )
    query_plan, papers, available_papers = _query_pubmed(retriever, target, max_papers)
    grouped_papers = {
        group: [paper for paper in papers if paper["classification"] == group]
        for group in ("human", "preclinical", "other")
    }
    visible_trials = trial_records[:max_trials]
    return {
        "ok": True,
        "target": target,
        "source_coverage": {
            "pubmed_query_axes": list(query_plan),
            "clinicaltrials_total_count": total_trials,
        },
        "papers": grouped_papers,
        "trials": {
            "relevant_count": relevant_trials,
            "records": [_compact_trial(trial) for trial in visible_trials],
        },
        "omitted": {
            "papers": max(0, available_papers - len(papers)),
            "trials": max(0, relevant_trials - len(visible_trials)),
        },
    }


def _encoded_size(output: dict[str, Any]) -> int:
    return len(json.dumps(output, separators=(",", ":"), ensure_ascii=True)) + 1


def _drop_lowest_priority_card(output: dict[str, Any]) -> bool:
    successful = [target for target in output["targets"] if target.get("ok")]
    priorities = (
        ("paper", "other", 0),
        ("trial", "records", 3),
        ("paper", "preclinical", 1),
        ("paper", "human", 2),
        ("trial", "records", 1),
        ("paper", "human", 1),
    )
    for kind, group, minimum in priorities:
        for target in reversed(successful):
            records = (
                target["trials"][group] if kind == "trial" else target["papers"][group]
            )
            if len(records) <= minimum:
                continue
            records.pop()
            target["omitted"]["trials" if kind == "trial" else "papers"] += 1
            return True
    return False


def _shrink_excerpts(output: dict[str, Any], limit: int) -> None:
    for target in output["targets"]:
        if not target.get("ok"):
            continue
        for group in target["papers"].values():
            for paper in group:
                for field in ("result_excerpt", "safety_excerpt"):
                    paper[field] = _clip(str(paper.get(field) or ""), limit)


def _enforce_output_budget(
    output: dict[str, Any], max_output_chars: int
) -> dict[str, Any]:
    output["output_budget"] = {
        "max_characters": max_output_chars,
        "actual_characters": 0,
        "cards_omitted_for_budget": False,
    }
    while _encoded_size(output) > max_output_chars:
        if not _drop_lowest_priority_card(output):
            break
        output["output_budget"]["cards_omitted_for_budget"] = True
    if _encoded_size(output) > max_output_chars:
        _shrink_excerpts(output, 180)
    while _encoded_size(output) > max_output_chars:
        if not _drop_lowest_priority_card(output):
            break
        output["output_budget"]["cards_omitted_for_budget"] = True
    for _ in range(3):
        output["output_budget"]["actual_characters"] = _encoded_size(output)
    return output


def _targets(values: list[str]) -> list[str]:
    targets: list[str] = []
    seen: set[str] = set()
    for value in values:
        target = " ".join(value.split())
        normalized = target.casefold()
        if target and normalized not in seen:
            targets.append(target)
            seen.add(normalized)
    return targets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", action="append", required=True)
    parser.add_argument("--mode", choices=("auto", "brief", "compare"), default="auto")
    parser.add_argument(
        "--questions", nargs="+", default=["biology", "programs", "safety"]
    )
    parser.add_argument("--separate-human-preclinical", action="store_true")
    parser.add_argument("--max-papers", type=int)
    parser.add_argument("--max-trials", type=int)
    parser.add_argument("--max-output-chars", type=int, default=DEFAULT_OUTPUT_CHARS)
    parser.add_argument("--debug-telemetry", action="store_true")
    args = parser.parse_args()
    args.target = _targets(args.target)
    if not args.target:
        parser.error("at least one non-empty --target is required")
    if len(args.target) > MAX_TARGETS:
        parser.error(f"at most {MAX_TARGETS} targets are supported per invocation")
    if args.mode == "brief" and len(args.target) > 1:
        parser.error("--mode brief accepts exactly one target")
    if args.max_output_chars < 5_000:
        parser.error("--max-output-chars must be at least 5000")
    if args.max_papers is not None and args.max_papers < 1:
        parser.error("--max-papers must be positive")
    if args.max_papers is not None and args.max_papers > 30:
        parser.error("--max-papers cannot exceed 30")
    if args.max_trials is not None and args.max_trials < 1:
        parser.error("--max-trials must be positive")
    if args.max_trials is not None and args.max_trials > 50:
        parser.error("--max-trials cannot exceed 50")
    return args


def main() -> int:
    args = parse_args()
    started = time.monotonic()
    retriever = Retriever()
    mode = "compare" if args.mode == "compare" or len(args.target) > 1 else "brief"
    max_papers = args.max_papers or (8 if mode == "compare" else 10)
    max_trials = args.max_trials or (5 if mode == "compare" else 8)
    targets: list[dict[str, Any]] = []
    for target in args.target:
        try:
            targets.append(_target_evidence(retriever, target, max_papers, max_trials))
        except Exception as exc:  # noqa: BLE001
            targets.append(
                {
                    "ok": False,
                    "target": target,
                    "error": {"type": type(exc).__name__, "message": str(exc)},
                }
            )
    succeeded = sum(target["ok"] for target in targets)
    output = {
        "schema_version": 1,
        "ok": succeeded > 0,
        "partial": 0 < succeeded < len(targets),
        "mode": mode,
        "questions": args.questions,
        "separate_human_preclinical": args.separate_human_preclinical,
        "targets": targets,
        "limitations": [
            "PubMed retrieval is relevance-ranked and bounded; it is not a systematic review.",
            "Paper classification is heuristic and should be checked during synthesis.",
            "ClinicalTrials.gov event counts are not automatically treatment-attributed.",
            "Current program status is limited to the retrieved registry snapshot.",
        ],
        "telemetry": _telemetry(
            retriever, started, include_requests=args.debug_telemetry
        ),
    }
    output = _enforce_output_budget(output, args.max_output_chars)
    json.dump(output, sys.stdout, separators=(",", ":"), ensure_ascii=True)
    sys.stdout.write("\n")
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
