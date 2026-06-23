#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

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
) -> dict:
    return {
        "hasResults": False,
        "protocolSection": {
            "identificationModule": {
                "nctId": nct_id,
                "briefTitle": title,
                "officialTitle": official_title,
            },
            "statusModule": {"overallStatus": "COMPLETED"},
            "designModule": {
                "studyType": "INTERVENTIONAL",
                "phases": ["PHASE1"],
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


class CacheTests(unittest.TestCase):
    def test_cache_metadata_does_not_persist_request_url(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            retriever = research_target_evidence.Retriever(
                Path(directory), "read-write", 60
            )
            url = "https://example.test/data?api_key=secret"

            retriever._write_cache(url, b"payload")

            _, metadata_path = retriever._cache_paths(url)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(set(metadata), {"saved_at"})


if __name__ == "__main__":
    unittest.main()
