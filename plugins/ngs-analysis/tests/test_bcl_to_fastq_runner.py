import csv
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import ngs_run_utils  # noqa: E402
import run_bcl_to_fastq  # noqa: E402


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


class ParseReportBundleTests(unittest.TestCase):
    def test_parse_report_bundle_flags_high_undetermined_fraction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            reports_dir = output_dir / "Reports"
            write_csv(
                reports_dir / "Demultiplex_Stats.csv",
                [
                    {
                        "Lane": "1",
                        "SampleID": "sampleA",
                        "Index": "AAAA-BBBB",
                        "# Reads": "100",
                        "# Perfect Index Reads": "95",
                        "# One Mismatch Index Reads": "5",
                        "# Two Mismatch Index Reads": "0",
                        "% Reads": "0.10",
                        "% Perfect Index Reads": "0.95",
                        "% One Mismatch Index Reads": "0.05",
                        "% Two Mismatch Index Reads": "0.00",
                    },
                    {
                        "Lane": "1",
                        "SampleID": "Undetermined",
                        "Index": "",
                        "# Reads": "900",
                        "# Perfect Index Reads": "900",
                        "# One Mismatch Index Reads": "0",
                        "# Two Mismatch Index Reads": "0",
                        "% Reads": "0.90",
                        "% Perfect Index Reads": "1.00",
                        "% One Mismatch Index Reads": "0.00",
                        "% Two Mismatch Index Reads": "0.00",
                    },
                ],
            )
            write_csv(
                reports_dir / "Quality_Metrics.csv",
                [
                    {
                        "Lane": "1",
                        "SampleID": "sampleA",
                        "index": "AAAA",
                        "index2": "BBBB",
                        "ReadNumber": "1",
                        "Yield": "1000",
                        "YieldQ30": "970",
                        "QualityScoreSum": "36000",
                        "Mean Quality Score (PF)": "36.0",
                        "% Q30": "0.97",
                    }
                ],
            )
            write_csv(
                reports_dir / "Top_Unknown_Barcodes.csv",
                [
                    {
                        "Lane": "1",
                        "index": "CCCC",
                        "index2": "DDDD",
                        "# Reads": "20",
                        "% of Unknown Barcodes": "0.02",
                        "% of All Reads": "0.02",
                    }
                ],
            )
            write_csv(
                reports_dir / "fastq_list.csv",
                [
                    {
                        "RGID": "AAAA.BBBB.1",
                        "RGSM": "sampleA",
                        "RGLB": "lib1",
                        "Lane": "1",
                        "Read1File": str(output_dir / "sampleA_S1_L001_R1_001.fastq.gz"),
                        "Read2File": str(output_dir / "sampleA_S1_L001_R2_001.fastq.gz"),
                    }
                ],
            )
            for name in [
                "sampleA_S1_L001_R1_001.fastq.gz",
                "sampleA_S1_L001_R2_001.fastq.gz",
                "Undetermined_S0_L001_R1_001.fastq.gz",
                "Undetermined_S0_L001_R2_001.fastq.gz",
            ]:
                (output_dir / name).write_bytes(b"test")

            result = run_bcl_to_fastq.parse_report_bundle(output_dir)
            self.assertIsNotNone(result)
            self.assertEqual(result["assessment"], "fail")
            self.assertAlmostEqual(result["undetermined_fraction"], 0.9)
            self.assertEqual(len(result["fastq_outputs"]), 4)


class ArtifactIndexTests(unittest.TestCase):
    def test_build_artifact_index_includes_extra_roots_and_skips_large_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            out_dir = root / "out"
            (run_dir / "config.json").parent.mkdir(parents=True, exist_ok=True)
            (run_dir / "config.json").write_text("{}\n", encoding="utf-8")
            (out_dir / "sample.fastq.gz").parent.mkdir(parents=True, exist_ok=True)
            (out_dir / "sample.fastq.gz").write_bytes(b"0123456789abcdef")
            with mock.patch.object(ngs_run_utils, "MAX_AUTO_CHECKSUM_BYTES", 8):
                index = ngs_run_utils.build_artifact_index(
                    run_dir, extra_roots={"output_directory": out_dir}
                )
            entry = next(
                item
                for item in index["artifacts"]
                if item["path"] == "output_directory/sample.fastq.gz"
            )
            self.assertEqual(entry["sha256"], "")
            self.assertIn("auto-checksum threshold", entry["sha256_skipped_reason"])


class RuntimePreflightTests(unittest.TestCase):
    def test_converter_runtime_preflight_reports_mount_root_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wrapper = Path(tmp) / "bcl-convert"
            wrapper.write_text('#!/bin/sh\ndocker run --rm image "$@"\n', encoding="utf-8")
            args = SimpleNamespace(
                run_folder=Path("/opt/run"),
                sample_sheet=Path("/opt/SampleSheet.csv"),
                output_directory=Path("/opt/out"),
            )
            with mock.patch.object(run_bcl_to_fastq, "command_path", return_value=str(wrapper)):
                with mock.patch.object(
                    run_bcl_to_fastq,
                    "run_cmd",
                    return_value={"ok": False, "stdout_tail": "daemon down"},
                ):
                    runtime = run_bcl_to_fastq.converter_runtime_preflight("bcl-convert", args)
            self.assertTrue(runtime["uses_docker_wrapper"])
            self.assertFalse(runtime["docker_daemon_ok"])
            self.assertGreaterEqual(len(runtime["errors"]), 1)


if __name__ == "__main__":
    unittest.main()
