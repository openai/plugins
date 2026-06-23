#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import time
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


class TelemetryTests(unittest.TestCase):
    def test_telemetry_reports_request_metrics(self) -> None:
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
        self.assertEqual(
            set(telemetry),
            {
                "elapsed_seconds",
                "request_attempts",
                "network_requests",
                "retries",
                "rate_limit_events",
                "bytes_received",
                "requests",
            },
        )


if __name__ == "__main__":
    unittest.main()
