import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
WORKFLOW_DIR = Path(__file__).resolve().parents[1] / "workflows" / "bulk_rnaseq_counts_qc"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(WORKFLOW_DIR))

import aggregate_salmon_quant  # noqa: E402
import run_bulk_rnaseq_counts_qc  # noqa: E402


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class SalmonLibtypeTests(unittest.TestCase):
    def test_yaml_preflight_reports_missing_pyyaml_without_import_crash(self) -> None:
        with mock.patch.dict(sys.modules, {"yaml": None}):
            status = run_bulk_rnaseq_counts_qc.yaml_dependency_status()
        self.assertFalse(status["ok"])
        self.assertFalse(status["python_modules"]["yaml"]["present"])

    def test_salmon_libtype_respects_layout_and_strandedness(self) -> None:
        self.assertEqual(
            run_bulk_rnaseq_counts_qc.salmon_libtype("PE", "reverse"), ("ISR", "from_input")
        )
        self.assertEqual(
            run_bulk_rnaseq_counts_qc.salmon_libtype("PE", "forward"), ("ISF", "from_input")
        )
        self.assertEqual(
            run_bulk_rnaseq_counts_qc.salmon_libtype("SE", "reverse"), ("SR", "from_input")
        )
        self.assertEqual(
            run_bulk_rnaseq_counts_qc.salmon_libtype("SE", "unstranded"), ("U", "from_input")
        )
        self.assertEqual(
            run_bulk_rnaseq_counts_qc.salmon_libtype("PE", "unknown"), ("A", "infer_from_salmon")
        )


class AggregateSalmonQuantTests(unittest.TestCase):
    def test_aggregate_outputs_gene_level_matrices_and_tx2gene(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = {
                "references": {"annotation_gtf": str(root / "genes.gtf")},
                "rnaseq_salmon_samples": {
                    "sampleA": {
                        "layout": "PE",
                        "strandedness": "reverse",
                        "row_indices": [2],
                        "r1": ["a"],
                        "r2": ["b"],
                    },
                    "sampleB": {
                        "layout": "PE",
                        "strandedness": "reverse",
                        "row_indices": [3],
                        "r1": ["c"],
                        "r2": ["d"],
                    },
                },
            }
            write_text(
                root / "genes.gtf",
                "\n".join(
                    [
                        'chr1\tsrc\ttranscript\t1\t100\t.\t+\t.\tgene_id "GENE1"; transcript_id "TX1"; gene_name "G1";',
                        'chr1\tsrc\ttranscript\t200\t300\t.\t+\t.\tgene_id "GENE1"; transcript_id "TX2"; gene_name "G1";',
                        'chr1\tsrc\ttranscript\t400\t500\t.\t+\t.\tgene_id "GENE2"; transcript_id "TX3"; gene_name "G2";',
                    ]
                )
                + "\n",
            )
            write_text(root / "config.json", json.dumps(config))
            for sample, rows in {
                "sampleA": [("TX1", 10, 5.0, 100.0), ("TX2", 3, 2.0, 90.0), ("TX3", 4, 1.0, 80.0)],
                "sampleB": [("TX1", 7, 4.0, 100.0), ("TX2", 1, 1.0, 90.0), ("TX3", 5, 6.0, 80.0)],
            }.items():
                lines = ["Name\tLength\tEffectiveLength\tTPM\tNumReads"]
                lines.extend([f"{tx}\t1000\t{eff}\t{tpm}\t{reads}" for tx, reads, tpm, eff in rows])
                write_text(root / f"{sample}.quant.sf", "\n".join(lines) + "\n")
            outdir = root / "out"
            argv = [
                "aggregate_salmon_quant.py",
                "--config",
                str(root / "config.json"),
                "--outdir",
                str(outdir),
                "--quant",
                f"sampleA={root / 'sampleA.quant.sf'}",
                "--quant",
                f"sampleB={root / 'sampleB.quant.sf'}",
            ]
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(aggregate_salmon_quant.main(), 0)
            self.assertIn("GENE1", (outdir / "gene_num_reads.tsv").read_text(encoding="utf-8"))
            self.assertIn("TX1\tGENE1\tG1", (outdir / "tx2gene.tsv").read_text(encoding="utf-8"))


class QcVerdictTests(unittest.TestCase):
    def test_compute_qc_verdict_surfaces_mismatch_and_outlier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = {
                "fastq_files": {
                    "SAMPLE1__r1": {"sample": "sample1", "path": str(root / "S1.fastq.gz")},
                    "SAMPLE2__r1": {"sample": "sample2", "path": str(root / "S2.fastq.gz")},
                },
                "rnaseq_salmon_samples": {
                    "sample1": {"salmon_libtype": "ISR"},
                    "sample2": {"salmon_libtype": "ISR"},
                },
            }
            write_text(
                root / "fastqc" / "multiqc" / "multiqc_data" / "multiqc_general_stats.txt",
                "\n".join(
                    [
                        "Sample\tfastqc-percent_duplicates",
                        "S1\t65.0",
                        "S2\t85.0",
                    ]
                )
                + "\n",
            )
            write_text(
                root / "rnaseq_salmon" / "multiqc" / "multiqc_data" / "multiqc_general_stats.txt",
                "\n".join(
                    [
                        "Sample\tsalmon-percent_mapped",
                        "sample1\t80.0",
                        "sample2\t60.0",
                    ]
                )
                + "\n",
            )
            write_text(
                root / "rnaseq_salmon" / "quant" / "sample1" / "lib_format_counts.json",
                json.dumps({"expected_format": "ISR", "strand_mapping_bias": 0.05}),
            )
            write_text(
                root / "rnaseq_salmon" / "quant" / "sample2" / "lib_format_counts.json",
                json.dumps({"expected_format": "ISF", "strand_mapping_bias": 0.20}),
            )
            verdict = run_bulk_rnaseq_counts_qc.compute_qc_verdict(root, config)
            self.assertEqual(verdict["overall_status"], "fail")
            sample2 = next(item for item in verdict["samples"] if item["sample"] == "sample2")
            self.assertEqual(sample2["libtype_status"], "fail")
            self.assertEqual(sample2["duplication_status"], "fail")
            self.assertEqual(sample2["strand_bias_status"], "warn")


if __name__ == "__main__":
    unittest.main()
