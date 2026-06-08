import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import ngs_epigenomics_utils  # noqa: E402
import ngs_reference_manager  # noqa: E402
import ngs_resource_gate  # noqa: E402
import ngs_visualization_utils  # noqa: E402
import run_amplicon_microbiome  # noqa: E402
import run_atacseq_peaks_qc  # noqa: E402
import run_chip_cutrun_peaks_qc  # noqa: E402
import run_dna_somatic_variants  # noqa: E402
import run_dna_umi_panel_variants  # noqa: E402
import run_nfcore_pipeline  # noqa: E402
import run_shotgun_metagenomics  # noqa: E402


def write(path: Path, text: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class ReferenceManagerTests(unittest.TestCase):
    def test_check_expected_files_reports_missing_bundle_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "genome.fa", ">chr1\nACGT\n")
            result = ngs_reference_manager.check_expected_files(
                bundle_name="reduced",
                bundle={"kind": "reference", "required_files": ["genome.fa", "genome.fa.fai"]},
                override_root=root,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["missing"], ["genome.fa.fai"])

    def test_pipeline_resource_plan_writes_manifest_and_env_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "kraken"
            db.mkdir()
            write(db / "hash.k2d", "hash")
            outdir = root / "plan"
            result = ngs_reference_manager.plan_pipeline_resources(
                "shotgun_metagenomics",
                bundle_roots={"kraken2_standard": db},
                include_optional=True,
            )
            outputs = ngs_reference_manager.write_resource_plan_outputs(result, outdir)
            self.assertFalse(result["ok"])
            self.assertEqual(result["resources"][0]["bundle"], "kraken2_standard")
            self.assertIn("opts.k2d", result["missing_required"][0]["missing"])
            self.assertTrue(Path(outputs["resource_manifest"]).exists())
            env_text = Path(outputs["resource_env"]).read_text(encoding="utf-8")
            self.assertIn("NGS_DB_KRAKEN2_ROOT", env_text)
            self.assertTrue(Path(outputs["resource_setup_summary"]).exists())
            setup_text = Path(outputs["resource_setup_summary"]).read_text(encoding="utf-8")
            self.assertIn("kraken2_standard", setup_text)
            self.assertIn("kraken2-build", setup_text)
            self.assertIn("Validation command", setup_text)
            commands_text = Path(outputs["resource_setup_commands"]).read_text(encoding="utf-8")
            self.assertIn("# kraken2-build", commands_text)
            self.assertIn("--kind database --bundle kraken2_standard", commands_text)

    def test_setup_plan_lists_missing_optional_database_actions(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            result = ngs_reference_manager.plan_pipeline_resources(
                "shotgun_metagenomics",
                include_optional=True,
            )
            setup_plan = ngs_reference_manager.setup_plan_from_resource_plan(result)
        bundles = {item["bundle"] for item in setup_plan["actions"]}
        self.assertEqual(setup_plan["blocking_count"], 1)
        self.assertIn("kraken2_standard", bundles)
        self.assertIn("bracken_standard", bundles)
        self.assertIn("humann_uniref90", bundles)
        kraken = next(
            item for item in setup_plan["actions"] if item["bundle"] == "kraken2_standard"
        )
        self.assertIn("kraken2-build", "\n".join(kraken["suggested_setup"]))
        self.assertIn(
            "${NGS_DB_KRAKEN2_ROOT:-/path/to/kraken2_standard}", kraken["validation_command"]
        )

    def test_genome_pipeline_resource_plan_selects_build_bundle(self) -> None:
        result = ngs_reference_manager.plan_pipeline_resources("atacseq", genome_build="mm39")
        self.assertEqual(result["pipeline"], "atacseq_peaks_qc")
        self.assertEqual(result["resources"][0]["bundle"], "grcm39_core")
        self.assertFalse(result["ok"])

    def test_resource_inventory_writes_dashboard_and_env_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle_root = root / "reduced_ref"
            write(bundle_root / "genome.fa", ">chr1\nACGT\n")
            write(bundle_root / "genome.fa.fai", "chr1\t4\t6\t4\t5\n")
            registries = {
                "references": {
                    "reduced_bundle": {
                        "display_name": "Local bundle",
                        "kind": "reduced_reference",
                        "genome_build": "reduced_local",
                        "root_env": "NGS_REF_REDUCED_BUNDLE_ROOT",
                        "source": "unit test",
                        "license_note": "test only",
                        "estimated_size": "small",
                        "suggested_setup": [
                            'samtools faidx "$NGS_REF_REDUCED_BUNDLE_ROOT"/genome.fa'
                        ],
                        "required_files": ["genome.fa", "genome.fa.fai"],
                    }
                },
                "databases": {},
            }
            inventory = ngs_reference_manager.inventory_resources(
                kind="reference",
                bundle_roots={"reduced_bundle": bundle_root},
                registries=registries,
            )
            outputs = ngs_reference_manager.write_resource_inventory_outputs(
                inventory, root / "inventory"
            )
            self.assertTrue(inventory["ok"], inventory)
            self.assertEqual(inventory["ready_count"], 1)
            self.assertTrue(Path(outputs["resource_dashboard"]).exists())
            dashboard = Path(outputs["resource_dashboard"]).read_text(encoding="utf-8")
            self.assertIn("Local bundle", dashboard)
            env_text = Path(outputs["resource_env"]).read_text(encoding="utf-8")
            self.assertIn("NGS_REF_REDUCED_BUNDLE_ROOT", env_text)

    def test_resource_lockfile_verifies_and_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle_root = root / "reduced_ref"
            write(bundle_root / "genome.fa", ">chr1\nACGT\n")
            write(bundle_root / "genome.fa.fai", "chr1\t4\t6\t4\t5\n")
            registries = {
                "references": {
                    "reduced_bundle": {
                        "display_name": "Local bundle",
                        "kind": "reduced_reference",
                        "root_env": "NGS_REF_REDUCED_BUNDLE_ROOT",
                        "source": "unit test",
                        "license_note": "test only",
                        "required_files": ["genome.fa", "genome.fa.fai"],
                    }
                },
                "databases": {},
            }
            inventory = ngs_reference_manager.inventory_resources(
                kind="reference",
                bundle_roots={"reduced_bundle": bundle_root},
                include_checksums=True,
                registries=registries,
            )
            lock = ngs_reference_manager.resource_lock_from_inventory(inventory)
            outputs = ngs_reference_manager.write_resource_lock_outputs(lock, root / "lock")
            self.assertTrue(lock["ok"], lock)
            self.assertTrue(Path(outputs["resource_lock"]).exists())
            verification = ngs_reference_manager.verify_resource_lock(lock)
            self.assertTrue(verification["ok"], verification)

            (bundle_root / "genome.fa.fai").unlink()
            drifted = ngs_reference_manager.verify_resource_lock(lock)
            self.assertFalse(drifted["ok"], drifted)
            self.assertEqual(drifted["mismatches"][0]["issue"], "missing_now")

    def test_direct_resource_gate_advisory_does_not_block_local_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            run_dir.mkdir()
            plan = ngs_resource_gate.write_pipeline_resource_plan(
                run_dir=run_dir,
                pipeline="atacseq_peaks_qc",
                genome_build="not_a_registered_reference_bundle",
                required=False,
            )
            validation = ngs_resource_gate.merge_resource_status(
                {"ok": True, "errors": [], "warnings": []}, plan, required=False
            )
            self.assertFalse(plan["ok"])
            self.assertTrue(validation["ok"])
            self.assertIn("advisory resource check", validation["warnings"][0])
            self.assertTrue((run_dir / "resources" / "resource_plan.json").exists())

    def test_direct_resource_gate_required_blocks_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            run_dir.mkdir()
            plan = ngs_resource_gate.write_pipeline_resource_plan(
                run_dir=run_dir,
                pipeline="dna_somatic_variants",
                genome_build="not_a_registered_reference_bundle",
                required=True,
            )
            validation = ngs_resource_gate.merge_resource_status(
                {"ok": True, "errors": [], "warnings": []}, plan, required=True
            )
            self.assertFalse(validation["ok"])
            self.assertIn("required reference bundle", validation["errors"][0])


class DnaSubtypePlannerTests(unittest.TestCase):
    def test_vcf_review_notebook_helper_discovers_vcfs_and_writes_notebook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "variants" / "S1.vcf.gz", "vcf")
            entries: list[dict[str, object]] = []
            review = ngs_visualization_utils.add_vcf_review_notebook_entry(
                root,
                entries,
                title="Unit Test VCF Review",
                table_items=[("Sample Table", "validation/samples.normalized.tsv")],
            )
            self.assertEqual(review["review_notebook"], "notebooks/vcf_review.marimo.py")
            self.assertTrue((root / "notebooks" / "vcf_review.marimo.py").exists())
            self.assertEqual(entries[-1]["kind"], "notebook")
            self.assertEqual(entries[-1]["status"], "created")

    def test_vcf_review_notebook_helper_marks_not_available_when_no_vcf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries: list[dict[str, object]] = []
            review = ngs_visualization_utils.add_vcf_review_notebook_entry(
                root, entries, title="Unit Test VCF Review"
            )
            self.assertEqual(review, {})
            self.assertEqual(entries[-1]["status"], "not_available")


class VisualizationHelperTests(unittest.TestCase):
    def test_reachable_localhost_url_for_path_returns_none_when_server_is_down(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "multiqc" / "raw" / "multiqc_report.html", "<html></html>")
            self.assertIsNone(
                ngs_visualization_utils.reachable_localhost_url_for_path(
                    "multiqc/raw/multiqc_report.html",
                    port=65500,
                    timeout_seconds=0.05,
                )
            )

    def test_write_multiqc_browser_helper_omits_dead_localhost_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "multiqc" / "raw" / "multiqc_report.html", "<html><body>report</body></html>"
            )
            write(
                root / "multiqc" / "raw" / "multiqc_data" / "multiqc_general_stats.txt",
                "Sample\tReads\nsampleA\t10\n",
            )
            helper = ngs_visualization_utils.write_multiqc_browser_helper(
                root,
                report_path="multiqc/raw/multiqc_report.html",
                title="Helper",
                localhost_port=65500,
            )
            self.assertIsNotNone(helper)
            helper_text = helper.read_text(encoding="utf-8")
            self.assertIn("localhost review URL is not live yet", helper_text)
            self.assertNotIn(
                'href="http://127.0.0.1:65500/multiqc/raw/multiqc_report.html"', helper_text
            )

    def test_somatic_plan_uses_dedicated_mutect2_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = write(root / "ref.fa", ">chr1\nACGT\n")
            write(root / "tumor.bam", "bam")
            write(root / "normal.bam", "bam")
            sheet = write(
                root / "pairs.tsv",
                "\t".join(["pair_id", "tumor_sample", "tumor_bam", "normal_sample", "normal_bam"])
                + "\n"
                + "\t".join(["P1", "T", "tumor.bam", "N", "normal.bam"])
                + "\n",
            )
            args = SimpleNamespace(
                sample_sheet=sheet,
                reference_fasta=reference,
                target_bed=None,
                panel_of_normals=None,
                germline_resource=None,
                annotation_vcf=None,
                f1r2_orientation_model=True,
            )
            validation, pairs = run_dna_somatic_variants.validate_inputs(args)
            plan = run_dna_somatic_variants.mutect2_plan(args, pairs)
            self.assertTrue(validation["ok"], validation)
            self.assertEqual(pairs[0]["design"], "tumor_normal")
            self.assertTrue(any("Mutect2" in item["command"] for item in plan))
            self.assertTrue(any("FilterMutectCalls" in item["command"] for item in plan))

    def test_somatic_pair_review_parses_postrun_stats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = write(root / "ref.fa", ">chr1\nACGT\n")
            write(root / "tumor.bam", "bam")
            sheet = write(
                root / "pairs.tsv", "pair_id\ttumor_sample\ttumor_bam\nP1\tT\ttumor.bam\n"
            )
            args = SimpleNamespace(
                sample_sheet=sheet,
                reference_fasta=reference,
                target_bed=None,
                panel_of_normals=None,
                germline_resource=None,
                annotation_vcf=None,
                f1r2_orientation_model=False,
            )
            validation, pairs = run_dna_somatic_variants.validate_inputs(args)
            write(root / "variants" / "P1.filtered.vcf.gz", "vcf")
            write(
                root / "variants" / "P1.bcftools_stats.txt",
                "SN\t0\tnumber of records:\t4\nSN\t0\tnumber of SNPs:\t3\nSN\t0\tnumber of indels:\t1\n",
            )
            rows = run_dna_somatic_variants.summarize_somatic_artifacts(
                root, validation, pairs, args
            )
            self.assertEqual(rows[0]["status"], "created")
            self.assertEqual(rows[0]["design"], "tumor_only")
            self.assertEqual(rows[0]["variant_records"], 4)
            self.assertTrue((root / "qc" / "somatic_pair_review.tsv").exists())

    def test_somatic_visuals_include_vcf_review_notebook_when_vcf_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "validation" / "pairs.normalized.tsv", "pair_id\ttumor_sample\nP1\tT\n")
            write(root / "workflow" / "somatic_command_plan.json", "{}\n")
            write(root / "qc" / "somatic_qc_summary.json", "{}\n")
            write(root / "qc" / "somatic_pair_review.tsv", "pair_id\tstatus\nP1\tcreated\n")
            write(root / "variants" / "P1.filtered.vcf.gz", "vcf")
            visuals = run_dna_somatic_variants.write_visuals(
                root, "completed", {"warnings": [], "pair_count": 1, "resource_plan_ok": True}, None
            )
            self.assertIn("review_notebook", visuals)
            self.assertTrue((root / visuals["review_notebook"]).exists())

    def test_umi_plan_generates_consensus_and_variant_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = write(root / "ref.fa", ">chr1\nACGT\n")
            write(root / "raw.bam", "bam")
            sheet = write(root / "samples.tsv", "sample\traw_bam\nS1\traw.bam\n")
            args = SimpleNamespace(
                sample_sheet=sheet,
                reference_fasta=reference,
                target_bed=None,
                hotspot_vcf=None,
                umi_mode="duplex",
                umi_tag="RX",
                grouping_strategy="adjacency",
                umi_edits=1,
                min_reads_per_molecule=2,
                min_af=0.005,
            )
            validation, samples = run_dna_umi_panel_variants.validate_inputs(args)
            plan = run_dna_umi_panel_variants.build_plan(args, samples)
            self.assertTrue(validation["ok"])
            self.assertEqual(samples[0]["consensus_state"], "needs_generation")
            self.assertTrue(any("CallMolecularConsensusReads" in item["command"] for item in plan))
            self.assertTrue(any("bcftools mpileup" in item["command"] for item in plan))

    def test_umi_plan_treats_missing_rx_mq_bam_as_review_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = write(root / "ref.fa", ">chr1\nACGT\n")
            write(root / "raw.bam", "bam")
            sheet = write(root / "samples.tsv", "sample\traw_bam\nS1\traw.bam\n")
            args = SimpleNamespace(
                sample_sheet=sheet,
                reference_fasta=reference,
                target_bed=None,
                hotspot_vcf=None,
                umi_mode="duplex",
                umi_tag="RX",
                grouping_strategy="adjacency",
                umi_edits=1,
                min_reads_per_molecule=2,
                min_af=0.005,
            )
            with mock.patch.object(
                run_dna_umi_panel_variants,
                "inspect_alignment_tags",
                return_value={
                    "inspectable": True,
                    "reason": "",
                    "records_inspected": 20,
                    "tags": {"RX": False, "MQ": False},
                    "all_present": False,
                },
            ):
                validation, samples = run_dna_umi_panel_variants.validate_inputs(args)
                plan = run_dna_umi_panel_variants.build_plan(args, samples)
            self.assertTrue(validation["ok"], validation)
            self.assertEqual(samples[0]["fgbio_readiness"], "review_contract_only")
            self.assertEqual(samples[0]["consensus_state"], "review_contract_only")
            self.assertEqual(plan, [])
            self.assertTrue(
                any("review-contract input" in warning for warning in validation["warnings"])
            )

    def test_umi_postrun_summary_parses_execution_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "consensus" / "S1.consensus.bam", "bam")
            write(
                root / "qc" / "S1.consensus.flagstat.txt",
                "120 + 0 in total (QC-passed reads + QC-failed reads)\n100 + 0 mapped (83.33% : N/A)\n",
            )
            write(
                root / "qc" / "S1.target_coverage.tsv",
                "#rname\tstartpos\tendpos\tnumreads\tcovbases\tcoverage\tmeandepth\tmeanbaseq\tmeanmapq\nchr1\t1\t100\t100\t95\t95\t42.5\t30\t60\n",
            )
            write(
                root / "variants" / "S1.bcftools_stats.txt",
                "SN\t0\tnumber of records:\t3\nSN\t0\tnumber of SNPs:\t2\nSN\t0\tnumber of indels:\t1\n",
            )
            write(root / "variants" / "S1.consensus.vcf.gz", "vcf")
            write(
                root / "qc" / "S1.family_size.tsv",
                "family_size\tcount\tfamily_type\n2\t2\tsimplex\n6\t1\tduplex\n",
            )
            rows = run_dna_umi_panel_variants.summarize_postrun_artifacts(
                root,
                [
                    {
                        "sample": "S1",
                        "consensus_alignment": "consensus/S1.consensus.bam",
                        "consensus_state": "provided",
                    }
                ],
            )
            evidence = run_dna_umi_panel_variants.write_molecular_evidence_contract(
                root,
                {"umi_mode": "duplex", "min_af": 0.005, "hotspot_vcf": None},
                [
                    {
                        "sample": "S1",
                        "consensus_alignment": "consensus/S1.consensus.bam",
                        "consensus_state": "provided",
                    }
                ],
                SimpleNamespace(umi_mode="duplex", min_reads_per_molecule=2),
            )
            self.assertEqual(rows[0]["status"], "created")
            self.assertEqual(rows[0]["total_consensus_reads"], 120)
            self.assertEqual(rows[0]["mapped_consensus_reads"], 100)
            self.assertEqual(rows[0]["variant_records"], 3)
            self.assertEqual(rows[0]["median_family_size"], 2.0)
            self.assertEqual(evidence[0]["low_af_review_status"], "ready_for_review")
            self.assertTrue((root / "qc" / "umi_postrun_summary.tsv").exists())
            self.assertTrue((root / "qc" / "umi_molecular_evidence_contract.tsv").exists())


class BackendPlannerTests(unittest.TestCase):
    def test_nfcore_command_captures_report_trace_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sheet = write(root / "samples.csv", "sample,fastq_1\nS1,a.fastq.gz\n")
            args = SimpleNamespace(
                pipeline="rnaseq",
                sample_sheet=sheet,
                params_file=None,
                profile="docker",
                revision="3.18.0",
                genome=None,
                fasta=None,
                gtf=None,
                extra_param=[],
                nextflow_arg=[],
            )
            params_path = root / "params.json"
            command = run_nfcore_pipeline.build_command(args, root, params_path)
            self.assertIn("nf-core/rnaseq", command)
            self.assertIn("-with-report", command)
            self.assertIn("-with-trace", command)

    def test_nfcore_scrnaseq_adapter_uses_scrnaseq_resource_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sheet = write(
                root / "samples.csv", "sample,fastq_1,fastq_2\nPBMC1,R1.fastq.gz,R2.fastq.gz\n"
            )
            reduced_ref = root / "reduced_ref"
            write(reduced_ref / "genome.fa", ">chr1\nACGT\n")
            write(reduced_ref / "genome.fa.fai", "chr1\t4\t6\t4\t5\n")
            write(
                reduced_ref / "annotation.gtf",
                'chr1\treduced\tgene\t1\t4\t.\t+\t.\tgene_id "g1";\n',
            )
            run_dir = root / "run"
            run_dir.mkdir()
            args = SimpleNamespace(
                pipeline="scrnaseq",
                sample_sheet=sheet,
                params_file=None,
                profile="docker",
                revision="4.0.0",
                genome="reduced_local",
                genome_build=None,
                fasta=None,
                gtf=None,
                extra_param=["aligner=star"],
                nextflow_arg=[],
                bundle_root=[f"reduced_micro_genome={reduced_ref}"],
                include_optional_resources=False,
                resource_checksums=False,
                skip_resource_plan=False,
            )
            input_validation = run_nfcore_pipeline.validate_inputs(args)
            resource_plan = run_nfcore_pipeline.write_resource_plan(args, run_dir)
            validation = run_nfcore_pipeline.merge_resource_status(input_validation, resource_plan)
            self.assertTrue(validation["ok"], validation)
            self.assertEqual(resource_plan["pipeline"], "scrnaseq_fastq_to_count")
            self.assertEqual(
                resource_plan["outputs"]["resource_plan"], "resources/resource_plan.json"
            )
            self.assertTrue((run_dir / "resources" / "resource_manifest.tsv").exists())

    def test_nfcore_missing_resource_blocks_adapter_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sheet = write(root / "samples.csv", "sample,fastq_1\nS1,a.fastq.gz\n")
            run_dir = root / "run"
            run_dir.mkdir()
            args = SimpleNamespace(
                pipeline="rnaseq",
                sample_sheet=sheet,
                params_file=None,
                profile="docker",
                revision=None,
                genome="not_a_registered_bundle",
                genome_build=None,
                fasta=None,
                gtf=None,
                extra_param=[],
                nextflow_arg=[],
                bundle_root=[],
                include_optional_resources=False,
                resource_checksums=False,
                skip_resource_plan=False,
            )
            input_validation = run_nfcore_pipeline.validate_inputs(args)
            resource_plan = run_nfcore_pipeline.write_resource_plan(args, run_dir)
            validation = run_nfcore_pipeline.merge_resource_status(input_validation, resource_plan)
            self.assertTrue(input_validation["ok"], input_validation)
            self.assertFalse(validation["ok"], validation)
            self.assertFalse(validation["resource_plan_ok"])
            self.assertIn("required reference bundle", validation["errors"][0])

    def test_atac_plan_contains_peak_frip_and_track_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "sample.bam", "bam")
            sheet = write(root / "atac.tsv", "sample\tbam\nA1\tsample.bam\n")
            args = SimpleNamespace(
                sample_sheet=sheet,
                bam_only=True,
                bowtie2_index=None,
                genome_size="hs",
                blacklist_bed=None,
                tss_bed=None,
                min_mapq=30,
                threads=2,
            )
            validation, samples = run_atacseq_peaks_qc.validate_inputs(args)
            plan = run_atacseq_peaks_qc.build_plan(args, samples)
            self.assertTrue(validation["ok"])
            self.assertTrue(any("macs2 callpeak" in item["command"] for item in plan))
            self.assertTrue(any("frip_reads" in item["command"] for item in plan))
            self.assertTrue(any("bamCoverage" in item["command"] for item in plan))

    def test_epigenomics_summary_builds_tracks_and_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "alignment" / "A1.filtered.bam", "bam")
            write(
                root / "qc" / "A1.flagstat.txt",
                "100 + 0 in total (QC-passed reads + QC-failed reads)\n95 + 0 mapped (95.0% : N/A)\n5 + 0 duplicates\n",
            )
            write(root / "qc" / "A1.filtered_reads.txt", "100\n")
            write(root / "qc" / "A1.frip_reads.txt", "25\n")
            write(root / "qc" / "A1.insert_sizes.txt", "50\n75\n200\n")
            write(root / "qc" / "A1.tss_matrix.gz", "matrix")
            write(root / "qc" / "A1.tss_profile.png", "png")
            write(root / "peaks" / "A1_peaks.narrowPeak", "chr1\t10\t20\nchr1\t30\t40\n")
            write(root / "peaks" / "consensus_peaks.bed", "chr1\t10\t40\n")
            write(root / "tracks" / "A1.bw", "bigwig")
            write(root / "motifs" / "A1" / "knownResults.txt", "Motif Name\tP-value\nRUNX\t1e-5\n")
            summary = ngs_epigenomics_utils.summarize_epigenomics_outputs(
                root,
                [{"sample": "A1", "layout": "bam"}],
                peak_mode="narrow",
                output_prefix="atacseq_qc",
                title="ATAC-seq",
            )
            self.assertEqual(summary["status"], "created")
            self.assertEqual(summary["samples"][0]["frip"], 0.25)
            self.assertEqual(summary["samples"][0]["raw_peak_count"], 2)
            self.assertTrue((root / "tracks" / "browser_tracks.tsv").exists())
            self.assertTrue((root / "tracks" / "igv_session.xml").exists())
            self.assertTrue((root / "tracks" / "browser_track_preview.html").exists())
            self.assertTrue((root / "qc" / "atacseq_qc_dashboard.html").exists())
            self.assertTrue((root / "qc" / "atacseq_qc_frip_peak_overview.svg").exists())
            self.assertTrue((root / "qc" / "atacseq_qc_insert_size_distribution.svg").exists())
            self.assertEqual(summary["outputs"]["dashboard"], "qc/atacseq_qc_dashboard.html")
            self.assertIn(
                "RUNX", (root / "motifs" / "motif_summary.tsv").read_text(encoding="utf-8")
            )

    def test_chip_plan_contains_optional_motif_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "chip.bam", "bam")
            sheet = write(root / "chip.tsv", "sample\tbam\ttarget\nC1\tchip.bam\tCTCF\n")
            args = SimpleNamespace(
                sample_sheet=sheet,
                assay="chipseq",
                target_class="tf",
                peak_mode="narrow",
                bowtie2_index=None,
                bam_only=True,
                genome_size="hs",
                blacklist_bed=None,
                min_mapq=30,
                threads=2,
                run_motifs=True,
                motif_genome="hg38",
                motif_size="given",
            )
            validation, samples = run_chip_cutrun_peaks_qc.validate_inputs(args)
            plan = run_chip_cutrun_peaks_qc.build_plan(args, samples)
            self.assertTrue(validation["ok"], validation)
            self.assertTrue(any("findMotifsGenome.pl" in item["command"] for item in plan))

    def test_chip_plan_resolves_control_sample_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "IP_R1.fastq.gz", "fastq")
            write(root / "IP_R2.fastq.gz", "fastq")
            write(root / "INPUT_R1.fastq.gz", "fastq")
            write(root / "INPUT_R2.fastq.gz", "fastq")
            sheet = write(
                root / "chip.tsv",
                "sample\tfastq_1\tfastq_2\ttarget\tcondition\tcontrol\n"
                "IP_1\tIP_R1.fastq.gz\tIP_R2.fastq.gz\tSPT5\tT0\tINPUT_1\n"
                "INPUT_1\tINPUT_R1.fastq.gz\tINPUT_R2.fastq.gz\tinput\tINPUT\t\n",
            )
            args = SimpleNamespace(
                sample_sheet=sheet,
                assay="chipseq",
                target_class="chromatin_regulator",
                peak_mode="broad",
                bowtie2_index=None,
                bam_only=False,
                genome_size="12100000",
                blacklist_bed=None,
                min_mapq=30,
                threads=2,
                run_motifs=False,
                motif_genome=None,
                motif_size="given",
            )
            validation, samples = run_chip_cutrun_peaks_qc.validate_inputs(args)
            plan = run_chip_cutrun_peaks_qc.build_plan(args, samples)
            self.assertTrue(validation["ok"], validation)
            self.assertFalse(
                any("needs input/IgG control" in warning for warning in validation["warnings"])
            )
            ip_peak = next(item for item in plan if item["name"] == "IP_1: MACS2 peaks")
            self.assertIn("-c alignment/INPUT_1.filtered.bam", ip_peak["command"])
            self.assertFalse(any(item["name"] == "INPUT_1: MACS2 peaks" for item in plan))

    def test_chip_plan_preprocesses_control_before_ip_peak_calling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "IP_R1.fastq.gz", "fastq")
            write(root / "IP_R2.fastq.gz", "fastq")
            write(root / "INPUT_R1.fastq.gz", "fastq")
            write(root / "INPUT_R2.fastq.gz", "fastq")
            sheet = write(
                root / "chip.tsv",
                "sample\tfastq_1\tfastq_2\ttarget\tcondition\tcontrol\n"
                "IP_1\tIP_R1.fastq.gz\tIP_R2.fastq.gz\tSPT5\tT0\tINPUT_1\n"
                "INPUT_1\tINPUT_R1.fastq.gz\tINPUT_R2.fastq.gz\tinput\tINPUT\t\n",
            )
            args = SimpleNamespace(
                sample_sheet=sheet,
                assay="chipseq",
                target_class="chromatin_regulator",
                peak_mode="broad",
                bowtie2_index=None,
                bam_only=False,
                genome_size="12100000",
                blacklist_bed=None,
                min_mapq=30,
                threads=2,
                run_motifs=False,
                motif_genome=None,
                motif_size="given",
            )
            _, samples = run_chip_cutrun_peaks_qc.validate_inputs(args)
            plan = run_chip_cutrun_peaks_qc.build_plan(args, samples)
            step_names = [item["name"] for item in plan]
            self.assertLess(
                step_names.index("INPUT_1: filter alignment"),
                step_names.index("IP_1: MACS2 peaks"),
            )
            self.assertLess(
                step_names.index("INPUT_1: index filtered BAM"),
                step_names.index("IP_1: MACS2 peaks"),
            )

    def test_chip_plan_consensus_glob_matches_peak_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "chip.bam", "bam")
            sheet = write(root / "chip.tsv", "sample\tbam\ttarget\nC1\tchip.bam\tSPT5\n")
            broad_args = SimpleNamespace(
                sample_sheet=sheet,
                assay="chipseq",
                target_class="chromatin_regulator",
                peak_mode="broad",
                bowtie2_index=None,
                bam_only=True,
                genome_size="12100000",
                blacklist_bed=None,
                min_mapq=30,
                threads=2,
                run_motifs=False,
                motif_genome=None,
                motif_size="given",
            )
            narrow_args = SimpleNamespace(**{**broad_args.__dict__, "peak_mode": "narrow"})
            _, broad_samples = run_chip_cutrun_peaks_qc.validate_inputs(broad_args)
            _, narrow_samples = run_chip_cutrun_peaks_qc.validate_inputs(narrow_args)
            broad_plan = run_chip_cutrun_peaks_qc.build_plan(broad_args, broad_samples)
            narrow_plan = run_chip_cutrun_peaks_qc.build_plan(narrow_args, narrow_samples)
            broad_consensus = next(
                item for item in broad_plan if item["name"] == "consensus peak merge"
            )
            narrow_consensus = next(
                item for item in narrow_plan if item["name"] == "consensus peak merge"
            )
            self.assertIn("cat peaks/*_peaks.broadPeak", broad_consensus["command"])
            self.assertIn("cat peaks/*_peaks.narrowPeak", narrow_consensus["command"])

    def test_amplicon_and_shotgun_backend_plans_are_database_aware(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "S1_R1.fastq.gz", "fastq")
            write(root / "S1_R2.fastq.gz", "fastq")
            classifier = write(root / "classifier.qza", "classifier")
            amplicon_sheet = write(
                root / "amplicon.tsv", "sample\tr1\tr2\nS1\tS1_R1.fastq.gz\tS1_R2.fastq.gz\n"
            )
            amp_args = SimpleNamespace(
                sample_sheet=amplicon_sheet,
                backend="qiime2",
                marker="16S",
                primer_forward="AAA",
                primer_reverse="TTT",
                taxonomy_classifier=classifier,
                metadata=None,
                trunc_len_f=None,
                trunc_len_r=None,
                sampling_depth=1000,
                profile=None,
                execute=False,
            )
            amp_validation, amp_samples = run_amplicon_microbiome.validate_inputs(amp_args)
            amp_plan = run_amplicon_microbiome.build_plan(amp_args, amp_samples)
            self.assertTrue(amp_validation["ok"])
            self.assertTrue(any("feature-classifier" in item["command"] for item in amp_plan))

            kraken_db = root / "kraken_db"
            kraken_db.mkdir()
            shotgun_sheet = write(
                root / "shotgun.tsv", "sample\tr1\tr2\nS1\tS1_R1.fastq.gz\tS1_R2.fastq.gz\n"
            )
            shotgun_args = SimpleNamespace(
                sample_sheet=shotgun_sheet,
                kraken_db=kraken_db,
                bracken_db=None,
                run_bracken=True,
                bracken_level="S",
                read_length=150,
                run_humann=False,
                humann_db=None,
                host_reference=None,
                metadata=None,
                threads=2,
            )
            shot_validation, shot_samples = run_shotgun_metagenomics.validate_inputs(shotgun_args)
            shot_plan = run_shotgun_metagenomics.build_plan(shotgun_args, shot_samples)
            self.assertTrue(shot_validation["ok"])
            self.assertTrue(any("kraken2" in item["command"] for item in shot_plan))
            self.assertTrue(any("bracken" in item["command"] for item in shot_plan))

    def test_amplicon_dada2_plan_uses_real_backend_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "S1_R1.fastq.gz", "fastq")
            classifier = write(root / "silva_train_set.fa.gz", ">ref\nACGT\n")
            amplicon_sheet = write(
                root / "amplicon.tsv", "sampleID\tforwardReads\nS1\tS1_R1.fastq.gz\n"
            )
            args = SimpleNamespace(
                sample_sheet=amplicon_sheet,
                backend="dada2",
                marker="16S",
                primer_forward="AAA",
                primer_reverse="TTT",
                taxonomy_classifier=classifier,
                metadata=None,
                trunc_len_f=120,
                trunc_len_r=None,
                sampling_depth=1000,
                profile=None,
                threads=3,
                execute=False,
            )
            validation, samples = run_amplicon_microbiome.validate_inputs(args)
            plan = run_amplicon_microbiome.build_plan(args, samples)
            self.assertTrue(validation["ok"], validation)
            self.assertTrue(run_amplicon_microbiome.DADA2_BACKEND_SCRIPT.exists())
            self.assertIn("run_dada2_backend.R", plan[0]["command"])
            self.assertIn("--threads 3", plan[0]["command"])
            self.assertIn("--trunc-len-f 120", plan[0]["command"])
            self.assertIn("tables/representative_sequences.fasta", plan[0]["outputs"])

    def test_amplicon_r_package_preflight_marks_missing_packages_blocking(self) -> None:
        base = {
            "ok": True,
            "required": ["Rscript"],
            "optional": [],
            "checked": [],
            "missing_required": [],
            "runtime_missing": [],
        }
        merged = run_amplicon_microbiome.merge_tool_status(
            base,
            {
                "ok": False,
                "missing": ["dada2"],
                "checked": [{"package": "dada2", "present": False}],
            },
        )
        self.assertFalse(merged["ok"])
        self.assertIn("R package:dada2", merged["runtime_missing"])

    def test_amplicon_summary_surfaces_runtime_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_amplicon_microbiome.write_summary(
                root,
                "blocked",
                {"backend": "dada2", "sample_count": 1, "warnings": [], "errors": []},
                resource_plan=None,
                tool_status={
                    "ok": False,
                    "missing_required": [],
                    "runtime_missing": ["R package:dada2"],
                },
            )
            summary = (root / "summary.md").read_text(encoding="utf-8")
            self.assertIn("Runtime Blockers", summary)
            self.assertIn("R package:dada2", summary)

    def test_shotgun_merges_bracken_and_humann_backend_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "taxonomic_classification" / "S1.bracken.tsv",
                "name\ttaxonomy_id\ttaxonomy_lvl\tkraken_assigned_reads\tadded_reads\tnew_est_reads\tfraction_total_reads\nEscherichia coli\t562\tS\t10\t5\t15\t0.75\nBacteroides fragilis\t817\tS\t2\t3\t5\t0.25\n",
            )
            write(
                root / "functional_profile" / "S1" / "S1_pathabundance.tsv",
                "# Pathway\tS1_Abundance\nPWY-1\t12.5\nPWY-2\t1.5\n",
            )
            write(
                root / "functional_profile" / "S1" / "S1_genefamilies.tsv",
                "# Gene Family\tS1_Abundance\nUniRef90_A\t3\nUniRef90_B\t1\n",
            )
            summary = run_shotgun_metagenomics.summarize_backend_outputs(root, [{"sample": "S1"}])
            review = run_shotgun_metagenomics.write_shotgun_review_outputs(root)
            self.assertEqual(summary["bracken"]["status"], "created")
            self.assertEqual(summary["humann"]["status"], "created")
            self.assertEqual(review["status"], "created")
            self.assertTrue((root / "tables" / "bracken_relative_abundance_matrix.tsv").exists())
            self.assertTrue((root / "tables" / "top_bracken_taxa.tsv").exists())
            self.assertTrue((root / "visualizations" / "shotgun_backend_dashboard.html").exists())
            self.assertTrue((root / "visualizations" / "shotgun_top_taxa.svg").exists())
            self.assertTrue((root / "visualizations" / "shotgun_top_pathways.svg").exists())
            self.assertIn(
                "Escherichia coli",
                (root / "tables" / "bracken_est_reads_matrix.tsv").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "PWY-1",
                (root / "tables" / "humann_pathabundance_matrix.tsv").read_text(encoding="utf-8"),
            )

    def test_shotgun_host_depletion_routes_classification_over_clean_reads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "S1_R1.fastq.gz", "fastq")
            write(root / "S1_R2.fastq.gz", "fastq")
            kraken_db = root / "kraken_db"
            kraken_db.mkdir()
            host_reference = root / "host_reference"
            host_reference.mkdir()
            sample_sheet = write(
                root / "shotgun.tsv", "sample\tr1\tr2\nS1\tS1_R1.fastq.gz\tS1_R2.fastq.gz\n"
            )
            args = SimpleNamespace(
                sample_sheet=sample_sheet,
                kraken_db=kraken_db,
                bracken_db=None,
                run_bracken=False,
                bracken_level="S",
                read_length=150,
                run_humann=True,
                humann_db=root / "humann_db",
                host_reference=host_reference,
                metadata=None,
                threads=2,
            )
            args.humann_db.mkdir()
            validation, samples = run_shotgun_metagenomics.validate_inputs(args)
            plan = run_shotgun_metagenomics.build_plan(args, samples)
            self.assertTrue(validation["ok"], validation)
            self.assertIn("KneadData host depletion", plan[0]["name"])
            self.assertIn("kneaddata", plan[0]["command"])
            kraken_command = next(
                item["command"] for item in plan if "kraken2 classify" in item["name"]
            )
            humann_concat = next(
                item["command"]
                for item in plan
                if "concatenate paired reads for HUMAnN" in item["name"]
            )
            self.assertIn("host_depletion/S1.clean_R1.fastq", kraken_command)
            self.assertIn("host_depletion/S1.clean_R2.fastq", kraken_command)
            self.assertIn("host_depletion/S1.clean_R1.fastq", humann_concat)
            self.assertIn("host_depletion/S1.clean_R2.fastq", humann_concat)

    def test_shotgun_resource_plan_promotes_requested_bracken_database_to_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kraken_db = root / "kraken"
            kraken_db.mkdir()
            write(kraken_db / "hash.k2d", "hash")
            run_dir = root / "run"
            run_dir.mkdir()
            args = SimpleNamespace(
                kraken_db=kraken_db,
                bracken_db=None,
                run_bracken=True,
                run_humann=False,
                humann_db=None,
                include_optional_resources=False,
                resource_checksums=False,
                skip_resource_plan=False,
            )
            resource_plan = run_shotgun_metagenomics.write_resource_plan(args, run_dir)
            validation = run_shotgun_metagenomics.merge_resource_status(
                {"ok": True, "errors": [], "warnings": []}, resource_plan
            )
            self.assertFalse(resource_plan["ok"])
            self.assertFalse(validation["ok"])
            self.assertIn(
                "kraken2_standard", [item["bundle"] for item in resource_plan["missing_required"]]
            )
            self.assertIn(
                "bracken_standard", [item["bundle"] for item in resource_plan["missing_required"]]
            )
            self.assertTrue((run_dir / "resources" / "resource_manifest.tsv").exists())

    def test_amplicon_normalizes_qiime2_exports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "tables" / "asv_table_export" / "feature-table.tsv",
                "# Constructed from biom file\n#OTU ID\tS1\tS2\nASV1\t10\t0\nASV2\t2\t8\n",
            )
            write(
                root / "tables" / "taxonomy_export" / "taxonomy.tsv",
                "Feature ID\tTaxon\tConfidence\nASV1\tk__Bacteria;g__Escherichia\t0.99\n",
            )
            write(
                root / "tables" / "denoising_stats_export" / "stats.tsv",
                "sample-id\tinput\tfiltered\tdenoised\nS1\t100\t90\t80\n",
            )
            summary = run_amplicon_microbiome.normalize_backend_exports(root)
            review = run_amplicon_microbiome.write_amplicon_review_outputs(root)
            self.assertEqual(summary["status"], "created")
            self.assertEqual(review["status"], "created")
            self.assertTrue((root / "tables" / "asv_table.tsv").exists())
            self.assertTrue((root / "tables" / "taxonomy.tsv").exists())
            self.assertTrue((root / "tables" / "read_retention.tsv").exists())
            self.assertTrue((root / "tables" / "alpha_diversity.tsv").exists())
            self.assertTrue((root / "tables" / "bray_curtis_distance.tsv").exists())
            self.assertTrue((root / "visualizations" / "amplicon_backend_dashboard.html").exists())
            self.assertTrue((root / "visualizations" / "amplicon_alpha_diversity.svg").exists())
            self.assertIn(
                "feature_id\tS1\tS2",
                (root / "tables" / "asv_table.tsv").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
