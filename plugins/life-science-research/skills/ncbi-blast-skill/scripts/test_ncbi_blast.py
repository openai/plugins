#!/usr/bin/env python3
"""Unit tests for ncbi_blast.py."""

from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).with_name("ncbi_blast.py")
SPEC = importlib.util.spec_from_file_location("ncbi_blast", SCRIPT_PATH)
assert SPEC and SPEC.loader
ncbi_blast = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ncbi_blast)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class FakeResponse:
    def __init__(
        self,
        text: str,
        *,
        json_data: object | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
    ) -> None:
        self.text = text
        self._json_data = json_data
        self.status_code = status_code
        self.headers = headers or {}
        self.content = content if content is not None else text.encode("utf-8")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise ncbi_blast.requests.HTTPError(f"HTTP {self.status_code}")

    def json(self) -> object:
        if self._json_data is None:
            raise ValueError("Response did not contain JSON.")
        return self._json_data


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str, dict[str, object]]] = []
        self.headers: dict[str, str] = {}

    def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append((method, url, kwargs))
        if not self.responses:
            raise AssertionError("Unexpected extra HTTP request.")
        return self.responses.pop(0)

    def close(self) -> None:
        return None


class NcbiBlastTests(unittest.TestCase):
    def _json2_zip_bytes(self, payloads: list[tuple[str, dict[str, object]]]) -> bytes:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            manifest_name = "RID123.json"
            manifest = {"BlastJSON": [{"File": name} for name, _ in payloads]}
            zip_file.writestr(manifest_name, json.dumps(manifest))
            for name, payload in payloads:
                zip_file.writestr(name, json.dumps(payload))
        return stream.getvalue()

    def test_submit_parses_rid_and_rtoe(self) -> None:
        session = FakeSession(
            [
                FakeResponse(
                    "RID = RID123\nRTOE = 42\nThis is extra body text that should not appear inline.\n"
                )
            ]
        )

        result = ncbi_blast.execute(
            {
                "action": "submit",
                "program": "blastp",
                "database": "swissprot",
                "query_fasta": ">q1\nMTEYK",
                "email": "user@example.com",
            },
            session=session,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["rid"], "RID123")
        self.assertEqual(result["rtoe_seconds"], 42)
        self.assertEqual(result["status"], "SUBMITTED")
        self.assertNotIn("body", json.dumps(result))

    def test_status_normalizes_searchinfo_states(self) -> None:
        cases = [
            ("Status=WAITING\n", "WAITING", False),
            ("Status=READY\nThereAreHits=yes\n", "READY", True),
            ("Status=READY\nThereAreHits=no\n", "READY", False),
            ("Status=FAILED\n", "FAILED", False),
            ("Status=UNKNOWN\n", "UNKNOWN", False),
        ]

        for body, expected_status, expected_hits in cases:
            with self.subTest(status=expected_status, hits=expected_hits):
                session = FakeSession([FakeResponse(body)])
                result = ncbi_blast.execute(
                    {"action": "status", "rid": "RID123"},
                    session=session,
                )
                self.assertTrue(result["ok"])
                self.assertEqual(result["status"], expected_status)
                self.assertEqual(result["has_hits"], expected_hits)

    def test_run_returns_compact_json2_summary_with_caps(self) -> None:
        clock = FakeClock()
        blast_json = {
            "BlastOutput2": [
                {
                    "report": {
                        "results": {
                            "search": {
                                "query_title": "q1",
                                "hits": [
                                    {
                                        "description": [{"accession": "A1", "title": "Alpha"}],
                                        "hsps": [{"evalue": 0.0, "bit_score": 99.9}],
                                    },
                                    {
                                        "description": [{"accession": "A2", "title": "Beta"}],
                                        "hsps": [{"evalue": 1e-10, "bit_score": 88.8}],
                                    },
                                ],
                            }
                        }
                    }
                },
                {
                    "report": {
                        "results": {
                            "search": {
                                "query_title": "q2",
                                "hits": [
                                    {
                                        "description": [{"accession": "B1", "title": "Gamma"}],
                                        "hsps": [{"evalue": 2e-5, "bit_score": 77.7}],
                                    }
                                ],
                            }
                        }
                    }
                },
            ]
        }
        session = FakeSession(
            [
                FakeResponse("RID = RID123\nRTOE = 1\n"),
                FakeResponse("Status=READY\nThereAreHits=yes\n"),
                FakeResponse(json.dumps(blast_json), json_data=blast_json),
            ]
        )

        result = ncbi_blast.execute(
            {
                "action": "run",
                "program": "blastp",
                "database": "swissprot",
                "query_fasta": ">q1\nMTEYK",
                "email": "user@example.com",
                "max_hits": 1,
                "max_queries": 1,
            },
            session=session,
            sleep_fn=clock.sleep,
            clock_fn=clock.time,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "run")
        self.assertEqual(result["status"], "READY")
        self.assertTrue(result["has_hits"])
        self.assertEqual(result["result_format"], "json2")
        self.assertEqual(result["query_count_returned"], 1)
        self.assertEqual(result["query_count_available"], 2)
        self.assertTrue(result["query_summaries_truncated"])
        self.assertEqual(result["query_summaries"][0]["hit_count_returned"], 1)
        self.assertEqual(result["query_summaries"][0]["hit_count_available"], 2)
        self.assertTrue(result["query_summaries"][0]["truncated"])
        self.assertEqual(result["query_summaries"][0]["top_hits"][0]["accession"], "A1")

    def test_run_returns_waiting_when_timeout_expires_before_poll(self) -> None:
        session = FakeSession([FakeResponse("RID = RID123\nRTOE = 1\n")])

        result = ncbi_blast.execute(
            {
                "action": "run",
                "program": "blastp",
                "database": "swissprot",
                "query_fasta": ">q1\nMTEYK",
                "email": "user@example.com",
                "wait_timeout_sec": 5,
            },
            session=session,
            sleep_fn=lambda _: None,
            clock_fn=lambda: 0.0,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "WAITING")
        self.assertEqual(result["rid"], "RID123")
        self.assertEqual(result["rtoe_seconds"], 1)

    def test_fetch_json2_sets_truncation_fields(self) -> None:
        blast_json = {
            "BlastOutput2": [
                {
                    "report": {
                        "results": {
                            "search": {
                                "query_id": "query_one",
                                "hits": [
                                    {
                                        "description": [{"accession": "A1", "title": "Alpha"}],
                                        "hsps": [{"evalue": 0.0, "bit_score": 99.9}],
                                    },
                                    {
                                        "description": [{"accession": "A2", "title": "Beta"}],
                                        "hsps": [{"evalue": 1.0, "bit_score": 88.8}],
                                    },
                                ],
                            }
                        }
                    }
                }
            ]
        }
        session = FakeSession(
            [
                FakeResponse("Status=READY\nThereAreHits=yes\n"),
                FakeResponse(json.dumps(blast_json), json_data=blast_json),
            ]
        )
        clock = FakeClock()

        result = ncbi_blast.execute(
            {
                "action": "fetch",
                "rid": "RID123",
                "max_hits": 1,
            },
            session=session,
            sleep_fn=clock.sleep,
            clock_fn=clock.time,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["query_summaries"][0]["query_title"], "query_one")
        self.assertEqual(result["query_summaries"][0]["hit_count_available"], 2)
        self.assertTrue(result["query_summaries"][0]["truncated"])

    def test_fetch_json2_unpacks_zip_payload(self) -> None:
        zipped_payload = self._json2_zip_bytes(
            [
                (
                    "RID123_1.json",
                    {
                        "BlastOutput2": {
                            "report": {
                                "results": {
                                    "search": {
                                        "query_title": "q1",
                                        "hits": [
                                            {
                                                "description": [
                                                    {"accession": "A1", "title": "Alpha"}
                                                ],
                                                "hsps": [{"evalue": 0.0, "bit_score": 99.9}],
                                            }
                                        ],
                                    }
                                }
                            }
                        }
                    },
                )
            ]
        )
        session = FakeSession(
            [
                FakeResponse("Status=READY\nThereAreHits=yes\n"),
                FakeResponse(
                    "",
                    headers={"content-type": "application/zip"},
                    content=zipped_payload,
                ),
            ]
        )
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "blast.json"
            result = ncbi_blast.execute(
                {
                    "action": "fetch",
                    "rid": "RID123",
                    "save_raw": True,
                    "raw_output_path": str(output_path),
                },
                session=session,
                sleep_fn=clock.sleep,
                clock_fn=clock.time,
            )

            self.assertTrue(result["ok"])
            self.assertEqual(result["status"], "READY")
            self.assertEqual(result["query_summaries"][0]["query_title"], "q1")
            self.assertEqual(result["query_summaries"][0]["top_hits"][0]["accession"], "A1")
            self.assertEqual(result["raw_output_path"], str(output_path))
            self.assertTrue(output_path.exists())

    def test_fetch_text_caps_text_head(self) -> None:
        text_body = "A" * 1200
        session = FakeSession(
            [
                FakeResponse("Status=READY\nThereAreHits=yes\n"),
                FakeResponse(text_body),
            ]
        )
        clock = FakeClock()

        result = ncbi_blast.execute(
            {
                "action": "fetch",
                "rid": "RID123",
                "result_format": "text",
            },
            session=session,
            sleep_fn=clock.sleep,
            clock_fn=clock.time,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(len(result["text_head"]), 800)
        self.assertTrue(result["text_head_truncated"])
        self.assertIsNone(result["raw_output_path"])

    def test_fetch_text_save_raw_writes_artifact(self) -> None:
        text_body = "BLAST-TEXT\n" * 100
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "blast.txt"
            session = FakeSession(
                [
                    FakeResponse("Status=READY\nThereAreHits=yes\n"),
                    FakeResponse(text_body),
                ]
            )
            clock = FakeClock()

            result = ncbi_blast.execute(
                {
                    "action": "fetch",
                    "rid": "RID123",
                    "result_format": "text",
                    "save_raw": True,
                    "raw_output_path": str(output_path),
                },
                session=session,
                sleep_fn=clock.sleep,
                clock_fn=clock.time,
            )

            self.assertTrue(result["ok"])
            self.assertEqual(result["raw_output_path"], str(output_path))
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding="utf-8"), text_body)
            self.assertNotIn("text_head", result)

    def test_fetch_json2_invalid_response_still_saves_raw_when_requested(self) -> None:
        raw_body = "<html>not json</html>"
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "blast.json"
            session = FakeSession(
                [
                    FakeResponse("Status=READY\nThereAreHits=yes\n"),
                    FakeResponse(raw_body),
                ]
            )
            clock = FakeClock()

            result = ncbi_blast.execute(
                {
                    "action": "fetch",
                    "rid": "RID123",
                    "save_raw": True,
                    "raw_output_path": str(output_path),
                },
                session=session,
                sleep_fn=clock.sleep,
                clock_fn=clock.time,
            )

            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "invalid_response")
            self.assertIn(str(output_path), result["error"]["message"])
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding="utf-8"), raw_body)

    def test_invalid_inputs_return_invalid_input(self) -> None:
        bad_payloads = [
            {
                "action": "submit",
                "program": "blastp",
                "database": "swissprot",
                "email": "user@example.com",
            },
            {"action": "status"},
            {"action": "bogus"},
            {
                "action": "fetch",
                "rid": "RID123",
                "max_hits": 0,
            },
            {
                "action": "run",
                "program": "blastp",
                "database": "swissprot",
                "query_fasta": ">q1\nMTEYK",
            },
        ]

        for payload in bad_payloads:
            with self.subTest(payload=payload):
                stdin = io.StringIO(json.dumps(payload))
                stdout = io.StringIO()
                with (
                    mock.patch.object(ncbi_blast.sys, "stdin", stdin),
                    mock.patch.object(ncbi_blast.sys, "stdout", stdout),
                ):
                    exit_code = ncbi_blast.main()
                output = json.loads(stdout.getvalue())
                self.assertEqual(exit_code, 2)
                self.assertFalse(output["ok"])
                self.assertEqual(output["error"]["code"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
