#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import importlib.util
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).with_name("research_target_evidence.py")
SPEC = importlib.util.spec_from_file_location("research_target_evidence", SCRIPT_PATH)
assert SPEC and SPEC.loader
research_target_evidence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(research_target_evidence)


def trial(
    nct_id: str,
    title: str,
    *,
    official_title: str = "",
    summary: str = "",
    intervention: str = "",
    phase: str = "PHASE1",
    has_results: bool = False,
) -> dict:
    return {
        "hasResults": has_results,
        "protocolSection": {
            "identificationModule": {
                "nctId": nct_id,
                "briefTitle": title,
                "officialTitle": official_title,
            },
            "statusModule": {"overallStatus": "COMPLETED"},
            "designModule": {
                "studyType": "INTERVENTIONAL",
                "phases": [phase],
                "enrollmentInfo": {"count": 10, "type": "ACTUAL"},
            },
            "descriptionModule": {"briefSummary": summary},
            "conditionsModule": {"conditions": ["Cancer"]},
            "armsInterventionsModule": {
                "interventions": (
                    [{"name": intervention, "type": "DRUG", "otherNames": []}]
                    if intervention
                    else []
                )
            },
        },
    }


class PaperClassificationTests(unittest.TestCase):
    def test_safety_excerpt_requires_a_safety_term(self) -> None:
        excerpt = research_target_evidence._best_excerpt(
            "The response rate was 42%. Median survival was 10 months.",
            ("adverse", "toxicity"),
            require_term=True,
        )

        self.assertEqual(excerpt, "")

    def test_patient_derived_xenograft_is_preclinical(self) -> None:
        classification = research_target_evidence._classify_paper(
            "Target activity in patient-derived xenografts",
            "The treatment reduced growth in mice and cell lines.",
            ["Journal Article"],
        )

        self.assertEqual(classification, "preclinical")

    def test_phase_one_trial_is_human(self) -> None:
        classification = research_target_evidence._classify_paper(
            "Phase I target study",
            "Patients with advanced cancer received treatment.",
            ["Clinical Trial, Phase I"],
        )

        self.assertEqual(classification, "human")

    def test_review_is_context_not_direct_human_evidence(self) -> None:
        classification = research_target_evidence._classify_paper(
            "Target review",
            "This review discusses phase I studies and patients with cancer.",
            ["Review"],
        )

        self.assertEqual(classification, "other")


class TrialFilteringTests(unittest.TestCase):
    def test_summary_only_record_requires_a_known_program_alias(self) -> None:
        records = research_target_evidence._parse_trials(
            {
                "studies": [
                    trial(
                        "NCT00000001",
                        "Study of Cirmtuzumab",
                        official_title="A ROR1-targeted antibody study",
                        intervention="Cirmtuzumab",
                    ),
                    trial(
                        "NCT00000002",
                        "Cirmtuzumab extension study",
                        summary="The antibody binds ROR1.",
                        intervention="Cirmtuzumab",
                    ),
                    trial(
                        "NCT00000003",
                        "Broad sequencing study",
                        summary="The panel includes ROR1 among many genes.",
                        intervention="Genome sequencing",
                    ),
                ]
            },
            "ROR1",
            10,
        )

        self.assertEqual(
            [record["nct_id"] for record in records],
            ["NCT00000001", "NCT00000002"],
        )

    def test_result_bearing_mature_trial_ranks_first(self) -> None:
        records = research_target_evidence._parse_trials(
            {
                "studies": [
                    trial(
                        "NCT00000001",
                        "TROP2 CAR-T study",
                        intervention="TROP2 CAR-T",
                    ),
                    trial(
                        "NCT00000002",
                        "TROP2 phase 3 study",
                        intervention="TROP2 sacituzumab govitecan",
                        phase="PHASE3",
                        has_results=True,
                    ),
                ]
            },
            "TROP2",
            10,
        )

        self.assertEqual(records[0]["nct_id"], "NCT00000002")


class TelemetryTests(unittest.TestCase):
    def test_api_key_is_redacted_from_errors(self) -> None:
        error = RuntimeError(
            "https://example.test/path?x=1&api_key=secret&retmode=json"
        )

        self.assertEqual(
            research_target_evidence._safe_error(error),
            "https://example.test/path?x=1&api_key=<redacted>&retmode=json",
        )

    def test_telemetry_is_compact_by_default(self) -> None:
        retriever = research_target_evidence.Retriever()
        retriever.requests = [
            {
                "label": "example",
                "host": "example.test",
                "elapsed_ms": 10,
                "bytes": 100,
                "status": 200,
                "attempt": 1,
            }
        ]

        telemetry = research_target_evidence._telemetry(retriever, time.monotonic())

        self.assertEqual(telemetry["network_requests"], 1)
        self.assertEqual(telemetry["bytes_received"], 100)
        self.assertNotIn("requests", telemetry)

        debug = research_target_evidence._telemetry(
            retriever, time.monotonic(), include_requests=True
        )
        self.assertEqual(debug["requests"], retriever.requests)


class MultiTargetTests(unittest.TestCase):
    def test_round_robin_ids_balances_query_groups(self) -> None:
        self.assertEqual(
            research_target_evidence._round_robin_ids(
                {"biology": ["1", "2"], "safety": ["3", "2"]}, 3
            ),
            ["1", "3", "2"],
        )

    def test_targets_are_deduplicated_without_reordering(self) -> None:
        self.assertEqual(
            research_target_evidence._targets([" GPC3 ", "CLDN18.2", "gpc3", "TROP2"]),
            ["GPC3", "CLDN18.2", "TROP2"],
        )

    def test_pubmed_group_ranking_handles_ids_outside_candidate_bound(self) -> None:
        def request(_retriever, _base_url, _params, label):
            if label.startswith("pubmed-esearch"):
                suffix = label.rsplit("-", 1)[-1]
                ids = {
                    "biology": ["1", "5"],
                    "human": ["2", "6"],
                    "modalities": ["3", "7"],
                    "safety": ["4", "8"],
                    "landmark": [str(value) for value in range(9, 111)],
                }[suffix]
                return {"esearchresult": {"idlist": ids}}
            return {
                "result": {
                    "1": {"title": "GPC3 biology"},
                    "2": {"title": "GPC3 phase 1"},
                    "3": {"title": "GPC3 antibody"},
                    "4": {"title": "GPC3 safety"},
                    "5": {"title": "GPC3 expression"},
                }
            }

        retriever = mock.Mock()
        retriever.get.return_value = b"<PubmedArticleSet />"
        with mock.patch.object(
            research_target_evidence, "_json_request", side_effect=request
        ):
            _, papers, available = research_target_evidence._query_pubmed(
                retriever, "GPC3", 1
            )

        self.assertEqual(papers, [])
        self.assertEqual(available, 110)

    def test_paper_selection_preserves_program_and_evidence_classes(self) -> None:
        papers = [
            {
                "pmid": "1",
                "classification": "human",
                "matched_queries": ["human"],
            },
            {
                "pmid": "2",
                "classification": "other",
                "matched_queries": ["landmark"],
            },
            {
                "pmid": "3",
                "classification": "preclinical",
                "matched_queries": ["biology"],
            },
            {
                "pmid": "4",
                "classification": "human",
                "matched_queries": ["safety"],
            },
            {
                "pmid": "5",
                "classification": "human",
                "matched_queries": ["landmark"],
            },
        ]

        selected = research_target_evidence._select_paper_cards(papers, 5)

        self.assertEqual(
            {paper["pmid"] for paper in selected}, {"1", "2", "3", "4", "5"}
        )
        self.assertEqual([paper["pmid"] for paper in selected[:2]], ["2", "5"])

    def test_output_budget_drops_cards_without_truncating_json(self) -> None:
        paper = {
            "pmid": "1",
            "title": "A" * 200,
            "classification": "human",
            "matched_queries": ["landmark"],
            "result_excerpt": "R" * 500,
            "safety_excerpt": "S" * 500,
            "url": "https://pubmed.ncbi.nlm.nih.gov/1/",
        }
        target = {
            "ok": True,
            "target": "GPC3",
            "source_coverage": {},
            "papers": {
                "human": [dict(paper, pmid=str(index)) for index in range(8)],
                "preclinical": [dict(paper, pmid=str(index)) for index in range(8, 12)],
                "other": [dict(paper, pmid=str(index)) for index in range(12, 16)],
            },
            "trials": {"relevant_count": 0, "records": []},
            "omitted": {"papers": 0, "trials": 0},
        }
        output = {"ok": True, "targets": [target], "telemetry": {}}

        bounded = research_target_evidence._enforce_output_budget(output, 5_000)
        encoded = json.dumps(bounded, separators=(",", ":"), ensure_ascii=True)

        self.assertLessEqual(len(encoded) + 1, 5_000)
        self.assertTrue(bounded["output_budget"]["cards_omitted_for_budget"])
        self.assertGreater(target["omitted"]["papers"], 0)

    def test_main_uses_one_retriever_and_preserves_partial_success(self) -> None:
        args = argparse.Namespace(
            target=["GPC3", "BROKEN"],
            mode="auto",
            questions=["biology", "programs", "safety"],
            separate_human_preclinical=True,
            max_papers=None,
            max_trials=None,
            max_output_chars=10_000,
            debug_telemetry=False,
        )
        retrievers: list[object] = []

        def target_evidence(retriever, target, max_papers, max_trials):
            retrievers.append(retriever)
            if target == "BROKEN":
                raise RuntimeError("expected failure")
            return {
                "ok": True,
                "target": target,
                "source_coverage": {},
                "papers": {"human": [], "preclinical": [], "other": []},
                "trials": {"relevant_count": 0, "records": []},
                "omitted": {"papers": 0, "trials": 0},
            }

        stdout = io.StringIO()
        with (
            mock.patch.object(
                research_target_evidence, "parse_args", return_value=args
            ),
            mock.patch.object(
                research_target_evidence,
                "_target_evidence",
                side_effect=target_evidence,
            ),
            redirect_stdout(stdout),
        ):
            exit_code = research_target_evidence.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["partial"])
        self.assertEqual([target["ok"] for target in payload["targets"]], [True, False])
        self.assertIs(retrievers[0], retrievers[1])


if __name__ == "__main__":
    unittest.main()
