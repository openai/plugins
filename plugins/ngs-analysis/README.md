# Life Sciences NGS Analysis Plugin

This plugin provides a guided intake and execution layer for common next-generation sequencing analyses. It routes users from BCL or FASTQ files to public, reproducible pipelines while checking local tool availability before installing anything.

## What It Does

- Inspects sequencing inputs before asking questions.
- Asks the minimum assay-specific questions needed to choose an analysis route.
- Prefers public, runtime-installable tools and nf-core workflows where practical.
- Runs tool preflight checks before suggesting downloads or installs.
- Keeps proprietary, credentialed, or cloud-upload paths explicit instead of silently using them.
- Treats preflight as validation before executing approved local workflows where supported.
- Produces timestamped run directories with manifests, validation summaries, logs, QC reports, exact command timing/return-code detail, checksummed artifact indexes, and input-to-output lineage tables.
- Produces native visualization bundles under `visualizations/` when a lane has enough downstream data to plot.

## Included Skills

- `ngs-analysis-router`: top-level intake and routing.
- `ngs-runtime-env`: package/tool existence checks and install planning.
- `ngs-bcl-to-fastq`: BCL run-folder validation, demultiplexing, and demux metric review.
- `ngs-fastq-qc`: FASTQ quality control, trimming decisions, and MultiQC interpretation.
- `ngs-dna-variant-calling`: WGS/WES/panel variant dispatcher.
- `ngs-dna-germline-variants`: germline WGS/WES/panel variant calling and QC.
- `ngs-dna-somatic-variants`: tumor-normal and tumor-only somatic variant calling and QC.
- `ngs-dna-umi-panel-variants`: UMI, duplex, and low-frequency targeted panel workflows.
- `ngs-bulk-rnaseq`: bulk RNA-seq dispatcher.
- `ngs-bulk-rnaseq-counts-qc`: bulk RNA-seq FASTQ-to-count processing and QC.
- `ngs-bulk-rnaseq-differential-expression`: bulk RNA-seq count-matrix differential expression.
- `ngs-scrna-seq`: single-cell or single-nucleus RNA-seq FASTQ-to-count kickoff.
- `scrna-seq-qc`: embedded post-count single-cell QC, annotation, clustering, and UMAP guidance.
- `ngs-epigenomics-peaks`: ATAC-seq, ChIP-seq, CUT&RUN, and CUT&Tag dispatcher.
- `ngs-atacseq-peaks-qc`: ATAC-seq QC, peak, consensus, and differential accessibility workflows.
- `ngs-chip-cutrun-peaks-qc`: ChIP-seq, CUT&RUN, and CUT&Tag QC, control, peak, and differential binding workflows.
- `ngs-amplicon-microbiome`: 16S/18S/ITS/COI amplicon analysis kickoff.
- `ngs-shotgun-metagenomics`: shotgun metagenomics taxonomic and functional profiling kickoff.

## Capability Status

This package is intentionally mixed maturity. Use the status below when deciding what to run versus what to treat as planning guidance.

Local execution lanes:

- `ngs-fastq-qc`: plugin-owned local runner for FASTQ validation, FastQC/MultiQC execution, optional trimming, logs, summaries, and artifact indexes.
- `ngs-bulk-rnaseq-counts-qc`: plugin-owned local runner for bulk RNA-seq FASTQ validation, FastQC/MultiQC, Salmon transcript quantification, TPM/NumReads/effective-length matrices, logs, summaries, and artifact indexes.
- `ngs-bulk-rnaseq-differential-expression`: plugin-owned local runner for count-matrix validation, contrast/replicate checks, automatic DESeq2/edgeR/limma method selection, QC plots, normalized matrices, result tables, logs, summaries, and artifact indexes.
- `ngs-scrna-seq`: plugin-owned local FASTQ-to-count runner for STARsolo-backed scRNA/snRNA count generation.
- `scrna-seq-qc`: post-count QC and annotation guidance, plus a matrix-level runner for 10x-style matrices. The runner uses conservative PBMC marker fallback when no matched reference is provided, so tissue-specific annotation should be reviewed or replaced before broader use.
- `ngs-dna-variant-calling`: plugin-owned BAM/CRAM-to-VCF execution package using samtools/bcftools for focused local checks, with nf-core/sarek still preferred for full WGS/WES/panel workflows.
- `ngs-dna-germline-variants`: plugin-owned higher-fidelity germline runner for BQSR, per-sample gVCFs, and optional joint genotyping when a local GATK toolchain and matched known-sites resources are available.
- `ngs-epigenomics-peaks`: plugin-owned FASTQ validation/QC execution package for ATAC-seq, ChIP-seq, CUT&RUN, and CUT&Tag intake, with readiness artifacts for the alignment and peak-calling stage.
- `ngs-amplicon-microbiome`: plugin-owned FASTQ validation/QC execution package for marker-gene amplicon inputs, with explicit primer/taxonomy backend readiness artifacts.
- `ngs-shotgun-metagenomics`: plugin-owned FASTQ validation/QC execution package for shotgun metagenomics inputs, with explicit database-gated taxonomic profiling status.
- `ngs-bcl-to-fastq`: plugin-owned BCL run-folder and sample-sheet validator that executes BCL Convert or legacy bcl2fastq when an installed converter is available.

Dispatch lanes:

- `ngs-bulk-rnaseq`: routes users to the counts/QC runner when starting from FASTQs, or to the differential-expression runner when starting from an expression matrix.

Dispatch and subtype lanes:

- `ngs-dna-germline-variants`
- `ngs-dna-somatic-variants`
- `ngs-dna-umi-panel-variants`
- `ngs-atacseq-peaks-qc`
- `ngs-chip-cutrun-peaks-qc`

These lanes route to the shared DNA or epigenomics execution packages when a compact local run is appropriate, and remain responsible for assay-specific guidance, metadata checks, controls, and full-workflow handoff.

## Runtime Preflight

From the repo root:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --list
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bulk_rnaseq --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bulk_rnaseq_counts_qc --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bulk_rnaseq_differential_expression --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --profile local_light --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --tool fastqc --network-checks
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline shotgun_metagenomics --manager micromamba --install-plan-outdir runtime_readiness/shotgun_install
```

The script checks local executables first with `PATH` lookup. Optional network checks query package indexes or container registries only when requested. It does not install packages unless `--install-missing --yes` is explicitly provided.

Use `--install-plan-outdir` for a permission-ready package handoff. It writes `install_plan.json` as the canonical review artifact and a guarded `install_commands.sh` companion generated from the same plan. The shell script exits in review-only mode unless `NGS_RUN_INSTALL_COMMANDS=1` is set after explicit user approval. Reference and database downloads remain separate and should be handled through `ngs_reference_manager.py setup-plan`.

## Pipeline Dependency Matrix

Use this matrix as a quick lane-to-package guide before running a workflow. The structured source of truth remains `references/pipeline-registry.json`; use `ngs_preflight.py --pipeline <pipeline> --emit-install-plan` to check the current machine and generate a reviewable install plan.

| Pipeline lane | Required or primary tools | Useful optional tools | Reference/database requirements |
| --- | --- | --- | --- |
| BCL-to-FASTQ | `bcl-convert` | `bcl2fastq` for legacy compatibility | Illumina run folder with `RunInfo.xml`, optional `RunParameters.xml`, `Data/Intensities/BaseCalls`, and a compatible sample sheet |
| FASTQ QC and trimming | `snakemake`, `fastqc`, `multiqc` | `fastp`, `cutadapt`, `seqkit` | FASTQ files and sample sheet or explicit sample/R1/R2 paths |
| Bulk RNA-seq counts/QC | `snakemake`, `fastqc`, `multiqc`, `salmon` | `star`, `subread`, `seqkit` | Transcriptome FASTA, genome FASTA, GTF, and optional registered genome bundle |
| Bulk RNA-seq differential expression | `Rscript` plus available DE backend packages | `DESeq2`, `edgeR`, `limma`, `marimo` review surface | Count/expression matrix, sample metadata, contrast table, and design context |
| scRNA FASTQ-to-count | `snakemake`, `STAR` or configured STAR container | `kb-python`, `cellranger` when explicitly requested and licensed | Genome FASTA, GTF, chemistry/whitelist inputs, and optional registered genome bundle |
| scRNA post-count QC | Python/R analysis environment with `scanpy` and runner dependencies | Bioconductor QC packages, `marimo` review surface | 10x-style matrix bundle, barcodes/features, metadata, and optional raw droplet matrix |
| Generic DNA variant calling | `samtools`, `bcftools` | `bwa-mem2`, `gatk`, `deepvariant` container | Reference FASTA, indexes, optional target/region, optional annotation VCF |
| Germline DNA variants | `gatk`, `samtools` | `bcftools`, `bwa-mem2`, `deepvariant` container | Matched reference FASTA, known-sites resources, optional target BED, optional cohort/joint-calling resources |
| Somatic DNA variants | `gatk`, `samtools`, `bcftools` | panel-of-normals resources | Tumor-normal or tumor-only sample sheet, reference FASTA, germline resource, optional panel of normals and target BED |
| UMI panel variants | `samtools`, `bcftools`, `fgbio` when consensus generation is needed | `bwa-mem2`, `gatk`, duplex-review helpers | Reference FASTA, target BED, UMI read structure/tags, consensus or raw UMI inputs, optional hotspot/review VCF |
| ATAC-seq peaks/QC | `bowtie2`, `samtools`, `bedtools`, `macs2`, `bamCoverage` | `computeMatrix`, `plotProfile`, `plotHeatmap`, `homer`, `multiqc` | Bowtie2 index, genome size, blacklist BED, optional TSS BED, optional registered genome bundle |
| ChIP/CUT&RUN/CUT&Tag peaks/QC | `bowtie2`, `samtools`, `bedtools`, `macs2`, `bamCoverage` | `homer`, `multiqc` | Bowtie2 index, genome size, IP/control metadata, optional blacklist/TSS annotations and registered genome bundle |
| Amplicon microbiome | `qiime2` or `dada2` | `cutadapt`, `seqkit`, `multiqc` | Primer/marker metadata, taxonomy classifier or database, sample metadata, optional ASV/taxonomy tables for review |
| Shotgun metagenomics | `kraken2`, `bracken` by default | `kneaddata`, `humann`, `metaphlan`, `seqkit`, `multiqc` | Kraken2 database, optional host-depletion reference, optional Bracken and HUMAnN databases |
| nf-core adapter | `nextflow` | `multiqc`, Docker/Singularity/Apptainer or site profile | Pipeline-specific reference/database bundle and any required container/runtime profile |

Package checks and reference/database checks are intentionally separate. Missing executables should produce an install plan; missing references or databases should produce resource readiness and setup-plan artifacts before any large download is attempted.

## FASTQ QC Local Execution

The FASTQ QC lane accepts a sample sheet or a single sample, validates FASTQ structure and pairing, runs FastQC/MultiQC through a local Snakemake workflow, and writes a standardized run envelope. By default, outputs are written under `ngs_runs/fastq_qc/` in the current working directory; pass `--outdir` to choose a different run directory.

```bash
python plugins/ngs-analysis/scripts/run_fastq_qc.py \
  --sample-sheet samplesheet.csv \
  --execute
```

Single paired sample:

```bash
python plugins/ngs-analysis/scripts/run_fastq_qc.py \
  --sample sampleA \
  --r1 sampleA_R1.fastq.gz \
  --r2 sampleA_R2.fastq.gz \
  --execute
```

Optional trimming and re-QC:

```bash
python plugins/ngs-analysis/scripts/run_fastq_qc.py \
  --sample-sheet samplesheet.csv \
  --trim-mode fastp \
  --execute
```

Each successful run writes `run_manifest.json`, `config.json`, `validation/`, `workflow/Snakefile`, `logs/`, `artifact_index.json`, `summary.md`, FastQC/MultiQC outputs, browser helpers plus `visualizations/localhost_launch_hint.txt` for the preferred localhost review path, and `qc_interpretation.json`.

## Bulk RNA-seq Counts/QC Local Execution

The bulk RNA-seq counts/QC lane accepts an nf-core-style sample sheet, validates FASTQ paths and read structure, runs FastQC/MultiQC plus Salmon transcript quantification through a plugin-owned Snakemake workflow, and writes the standard run envelope.

```bash
python plugins/ngs-analysis/scripts/run_bulk_rnaseq_counts_qc.py \
  --sample-sheet samplesheet.csv \
  --fastq-root path/to/fastqs \
  --transcriptome-fasta reference/transcriptome.fasta \
  --genome-fasta reference/genome.fa \
  --annotation-gtf reference/genes.gtf \
  --execute
```

Each successful run writes `run_manifest.json`, `config.json`, `validation/`, `workflow/Snakefile`, `logs/`, `versions/software_versions.json`, `artifact_index.json` with per-file SHA256 checksums, `summary.md`, a review bundle under `visualizations/`, browser helpers plus `visualizations/localhost_launch_hint.txt` for the preferred localhost review path, Salmon `quant.sf` files, and `rnaseq_salmon/matrices/{tpm,num_reads,effective_length,samples}.tsv`.

The counts/QC runner also writes a run-local resource-readiness bundle under `resources/`. It is advisory by default for explicitly supplied local references; use `--genome-build`, `--bundle-root <bundle>=<path>`, and `--require-resource-plan` when a registered genome bundle must be complete before the run can be marked ready.

## Bulk RNA-seq Differential Expression Local Execution

The differential-expression lane accepts a count or expression matrix, sample metadata, and a contrast table. It validates sample matching, replicate sufficiency, matrix scale, and R/Bioconductor package availability. With `--method auto`, integer-like `raw_counts` prefer DESeq2 when available, then edgeR; non-integer inputs route to `limma_log2`. Use `--input-mode` to declare `raw_counts`, `normalized_expression`, or `log_expression`; `auto` infers the mode and emits a warning when normalization is skipped because the matrix is already transformed.

```bash
python plugins/ngs-analysis/scripts/run_bulk_rnaseq_de.py \
  --count-matrix count_matrix.tsv \
  --sample-metadata sample_metadata.tsv \
  --contrasts contrasts.tsv \
  --input-mode auto \
  --execute
```

Each successful run writes `run_manifest.json`, `config.json`, `validation/`, `workflow/scripts/run_bulk_de.R`, `logs/`, `manifest/contrast_status.tsv`, input-mode-aware matrix artifacts, `qc/design_matrix.tsv`, `qc/design_diagnostics.tsv`, `qc/sample_outlier_metrics.tsv`, `qc/statistical_warnings.tsv`, `qc/mean_variance_trend.png`, per-contrast result tables, explicit `.not_tested.tsv` stubs for blocked contrasts, clearer limma volcano/MA plots when applicable, a review bundle under `visualizations/`, `notebooks/bulk_rnaseq_de_review.marimo.py`, an auto-launched localhost Marimo review app recorded in `notebooks/marimo_server.json`, `versions/`, checksummed `artifact_index.json`, and `summary.md`.

## scRNA FASTQ-to-count Local Execution

The plugin-owned scRNA execution lane accepts local FASTQs, validates barcode-versus-cDNA pairing, runs STARsolo through a dedicated Snakemake workflow, and writes a standardized run envelope. By default, outputs are written under `ngs_runs/scrnaseq_fastq_to_count/` in the current working directory; pass `--outdir` to choose a different run directory.

```bash
python plugins/ngs-analysis/scripts/run_scrnaseq_fastq_to_count.py \
  --sample-sheet samplesheet.csv \
  --genome-fasta reference/genome.fa \
  --annotation-gtf reference/genes.gtf \
  --cb-whitelist reference/whitelist.txt \
  --execute
```

Each successful run writes `run_manifest.json`, `manifest/lineage.tsv`, `manifest/working_samplesheet.csv`, `manifest/inputs_manifest.tsv`, `config.json`, `validation/`, `workflow/Snakefile`, `logs/`, `versions/software_versions.json`, `artifact_index.json`, `summary.md`, and STARsolo count artifacts. The run manifest records pinned STAR image metadata, chemistry-detection evidence, and explicit STARsolo cell-calling filter settings.

The FASTQ-to-count runner also writes advisory `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, and resource setup-plan artifacts by default. Add `--require-resource-plan` with a registered `--genome-build` and `--bundle-root` when genome bundle completeness should block readiness.

## scRNA Post-count Execution

For 10x-style matrix bundles, the package includes a post-count QC runner:

```bash
python plugins/ngs-analysis/scripts/run_scrnaseq_post_count_qc.py \
  --input-dir path/to/scrna_bundle
```

The input directory should contain `matrix/`, `manifest.tsv`, and `dataset_metadata.json`, unless explicit paths are provided. An optional `--raw-matrix-dir` enables emptyDrops-style cell-calling checks when a raw droplet matrix is available. This runner emits a standard envelope with `run_manifest.json`, `manifest/lineage.tsv`, `validation/tool_preflight.json`, `versions/software_versions.json`, checksummed `artifact_index.json`, `summary.md`, `provenance/analysis_status.json`, and `visualizations/index.html`. It also auto-launches a localhost Marimo review app recorded in `notebooks/marimo_server.json` and emits `notebooks/scrna_qc_review.marimo.py` as a notebook backup over the portable PNG/CSV/H5AD outputs. Tissue-specific annotation and integration choices should still be reviewed against the dataset and reference context.

## DNA Variant Calling Execution

The DNA variant-calling execution package accepts a BAM/CRAM sample sheet plus a matching reference FASTA, validates alignment/reference inputs, runs samtools QC, calls variants with bcftools, and writes the standard run envelope. Use nf-core/sarek or a lab-validated workflow for full germline, somatic, trio, or panel analysis.

```bash
python plugins/ngs-analysis/scripts/run_dna_variant_calling.py \
  --sample-sheet dna_samples.tsv \
  --reference-fasta reference.fa \
  --region chr20:1-100000 \
  --filter-min-qual 30 \
  --filter-min-site-dp 10 \
  --execute
```

Add a small known-variant annotation layer by passing a bgzip/tabix-indexed resource VCF:

```bash
python plugins/ngs-analysis/scripts/run_dna_variant_calling.py \
  --sample-sheet dna_samples.tsv \
  --reference-fasta reference.fa \
  --annotation-vcf gnomad_small.vcf.gz \
  --execute
```

Each successful run writes `run_manifest.json`, `validation/`, `logs/`, `qc/*.flagstat.txt`, `qc/*.idxstats.tsv`, `qc/*.coverage.tsv`, `qc/*.depth.tsv` when a region is provided, `qc/*.callability.json`, `qc/*.variant_summary.json`, `variants/*.vcf.gz`, optional `variants/*.annotated.vcf.gz`, optional `variants/*.filtered.vcf.gz`, `variants/*.bcftools_stats.txt`, `artifact_index.json`, and `summary.md`.

The generic BAM/CRAM-to-VCF runner now emits advisory `resources/` readiness artifacts for the selected genome bundle. Use `--require-resource-plan` when missing registered references should block readiness; otherwise the explicit `--reference-fasta` remains enough for focused local checks.

## Germline DNA Variant Calling Execution

For germline-specific local runs that should own BQSR and cohort assumptions, use the dedicated runner:

```bash
python plugins/ngs-analysis/scripts/run_dna_germline_variants.py \
  --sample-sheet dna_samples.tsv \
  --reference-fasta reference.fa \
  --known-sites dbsnp.vcf.gz \
  --known-sites mills.vcf.gz \
  --emit-gvcf \
  --joint-call \
  --execute
```

The runner validates resource completeness and writes a standard run envelope even when execution is blocked by missing GATK or mismatched resource bundles. Successful runs emit per-sample recalibration tables and BAMs, `gvcf/*.g.vcf.gz`, optional `joint/cohort.joint.vcf.gz`, `qc/*.flagstat.txt`, `qc/*.idxstats.tsv`, `artifact_index.json`, and `summary.md`.

The germline runner also writes the same advisory `resources/` bundle by default, with `--require-resource-plan` available for runs that must prove a complete registered reference and known-sites bundle.

## Somatic And UMI DNA Variant Execution

Somatic and UMI panel lanes now have dedicated runners instead of relying on the generic BAM-to-VCF path.

```bash
python plugins/ngs-analysis/scripts/run_dna_somatic_variants.py \
  --sample-sheet somatic_pairs.tsv \
  --reference-fasta reference.fa \
  --germline-resource af-only-gnomad.vcf.gz \
  --panel-of-normals pon.vcf.gz \
  --execute
```

The somatic runner validates tumor-normal/tumor-only pairing, writes `workflow/somatic_command_plan.json`, emits Mutect2/contamination/filtering command plans, records tumor-only and missing-resource caveats, and produces filtered VCF artifacts when GATK resources are available. It also writes `qc/somatic_pair_review.{tsv,json}` so each pair has an explicit matched-normal status, PON/germline-resource status, contamination-table status, filtered-VCF status, and parsed variant-count summary when backend artifacts exist.

```bash
python plugins/ngs-analysis/scripts/run_dna_umi_panel_variants.py \
  --sample-sheet umi_panel_samples.tsv \
  --reference-fasta reference.fa \
  --target-bed panel_targets.bed \
  --umi-mode duplex \
  --umi-tag RX \
  --execute
```

The UMI runner validates raw versus consensus BAM state, writes `workflow/umi_panel_command_plan.json`, emits fgbio consensus and consensus-BAM variant-calling commands, and records `qc/umi_postrun_summary.{tsv,json}` with consensus read counts, target coverage, variant stats, and family-size/duplex metrics when those backend artifacts exist. It also writes `qc/umi_molecular_evidence_contract.{tsv,json}` to make the low-AF review contract explicit: consensus BAM, family-size/molecule metrics, consensus VCF, variant stats, hotspot review, and duplex review readiness stay visible per sample.

Somatic and UMI direct runners now write advisory resource-readiness bundles by default under `resources/`. Use `--genome-build`, `--bundle-root grch38_core=/refs/GRCh38`, and `--require-resource-plan` when the run should be blocked unless the registered reference bundle is complete; leave the default advisory mode for custom or reduced references where the explicit FASTA/BED inputs are enough for a local check.

## FASTQ Assay Execution

The epigenomics, amplicon microbiome, and shotgun metagenomics execution packages share a FASTQ validation/QC runner. It resolves sample-sheet paths, validates read structure, runs seqkit stats and FastQC/MultiQC when available, then writes lane-specific readiness/status artifacts for the next workflow stage.

```bash
python plugins/ngs-analysis/scripts/run_fastq_assay_package.py \
  --lane epigenomics_peaks \
  --sample-sheet assay_samples.csv \
  --execute
```

Supported lanes are `epigenomics_peaks`, `amplicon_microbiome`, and `shotgun_metagenomics`. The shotgun lane can run Kraken2 only when both `kraken2` and a database path are provided; otherwise it records the database/tool blocker explicitly.

Each run also writes `visualizations/index.html` and `visualizations/visualization_manifest.json`. Successful FASTQ-assay executions emit `qc_verdict.json`; shotgun and amplicon runs also emit `qc_interpretation.json` with machine-readable reason codes, readiness verdicts, and concrete follow-on commands for backend generation plus plot re-rendering. The common `run_manifest.json` includes audit metadata such as plugin version, exact argv, environment snapshot, input-file checksums, a parameter hash, and `manifest/lineage.tsv`. With FASTQ-only inputs, the visual bundle points to read-level QC and the lane readiness artifact. When downstream tables are available, the runner can also create native plot/table bundles:

```bash
python plugins/ngs-analysis/scripts/run_fastq_assay_package.py \
  --lane amplicon_microbiome \
  --sample-sheet amplicon_samples.tsv \
  --asv-table asv_table.tsv \
  --taxonomy-table taxonomy.tsv \
  --execute
```

Amplicon visualizations include alpha diversity tables/plots, Bray-Curtis PCoA, rarefaction curves, and taxa barplots. Shotgun visualizations can be generated from Kraken reports, Bracken tables, and HUMAnN path/gene-family tables:

```bash
python plugins/ngs-analysis/scripts/run_fastq_assay_package.py \
  --lane shotgun_metagenomics \
  --sample-sheet shotgun_samples.csv \
  --kraken-report sample.report.txt \
  --bracken-table sample.bracken.tsv \
  --humann-pathabundance humann_pathabundance.tsv \
  --humann-genefamilies humann_genefamilies.tsv \
  --execute
```

For amplicon lanes, the runner also emits `methods/amplicon_methods.json` and a concrete backend handoff bundle under `workflow/amplicon_backend_*.{json,sh}`. If downstream ASV/taxonomy inputs are labeled synthetic or introduce sample columns that are not present in the real sample sheet, the run is marked review-only and beta-diversity/PCoA are blocked unless `--allow-synthetic-diversity` is passed explicitly.

## Assay Backend Execution

Dedicated backend runners expand beyond read-QC/readiness packages when the required tools and references are present:

```bash
python plugins/ngs-analysis/scripts/run_atacseq_peaks_qc.py \
  --sample-sheet atac_samples.csv \
  --bowtie2-index /refs/GRCh38/bowtie2/genome \
  --genome-size hs \
  --blacklist-bed /refs/GRCh38/blacklists/encode_blacklist.bed \
  --tss-bed /refs/GRCh38/tss.bed \
  --execute
```

```bash
python plugins/ngs-analysis/scripts/run_chip_cutrun_peaks_qc.py \
  --sample-sheet chip_samples.csv \
  --assay chipseq \
  --target-class tf \
  --peak-mode narrow \
  --bowtie2-index /refs/GRCh38/bowtie2/genome \
  --genome-size hs \
  --execute
```

These runners produce command plans and envelopes for alignment, filtering, MACS2 peaks, FRiP, consensus peaks, bigWig tracks, ATAC TSS matrices, and motif handoff artifacts.

Epigenomics backend runs also write normalized review outputs: `qc/atacseq_qc_summary.{tsv,json}` or `qc/chip_cutrun_qc_summary.{tsv,json}`, native dashboards under `qc/*_dashboard.html`, compact SVG plots for FRiP/peak counts and insert-size distributions, `tracks/browser_tracks.tsv`, `tracks/browser_track_preview.html`, `tracks/ucsc_track_lines.txt`, `tracks/igv_session.xml`, and `motifs/motif_summary.tsv`. ATAC runs generate TSS profile/heatmap commands when `--tss-bed` is supplied; ATAC and ChIP/CUT&RUN runs can add HOMER motif commands with `--run-motifs --motif-genome <hg38|mm10|...>`.

ATAC and ChIP/CUT&RUN direct runners also write advisory resource-readiness bundles by default. Use `--require-resource-plan` with an explicit `--genome-build` and `--bundle-root` when reference completeness should block execution readiness.

```bash
python plugins/ngs-analysis/scripts/run_amplicon_microbiome.py \
  --sample-sheet amplicon_samples.tsv \
  --backend qiime2 \
  --primer-forward GTGYCAGCMGCCGCGGTAA \
  --primer-reverse GGACTACNVGGGTWTCTAAT \
  --taxonomy-classifier silva-138-classifier.qza \
  --metadata sample_metadata.tsv \
  --execute
```

```bash
python plugins/ngs-analysis/scripts/run_shotgun_metagenomics.py \
  --sample-sheet shotgun_samples.csv \
  --kraken-db /db/kraken2/standard \
  --host-reference /refs/human_kneaddata_db \
  --run-bracken \
  --run-humann \
  --humann-db /db/humann \
  --execute
```

Use `--backend dada2` when the user wants the direct R/Bioconductor path. The plugin now ships `workflows/amplicon_microbiome/run_dada2_backend.R`, checks the `dada2` R package before execution, runs ASV inference when the package is available, and writes `tables/asv_table.tsv`, `tables/representative_sequences.fasta`, `tables/read_retention.tsv`, optional `tables/taxonomy.tsv`, and `dada2/dada2_backend_state.rds`.

The amplicon runner keeps database/tool blockers explicit, exports QIIME2 denoising stats, normalizes QIIME2 exports, and preserves native DADA2 outputs in the same review contract. BIOM-only exports are reported with a concrete `biom convert` command rather than silently treated as parsed tables. When a normalized ASV/feature table is present, the runner now derives `tables/alpha_diversity.tsv`, `tables/bray_curtis_distance.tsv`, `tables/top_taxa_or_features.tsv`, `tables/amplicon_diversity_summary.json`, and native SVG/HTML review artifacts under `visualizations/`.

The amplicon direct runner writes advisory taxonomy-database readiness bundles by default. Use `--bundle-root silva_138_amplicon=/db/silva`, `--include-optional-resources`, and `--require-resource-plan` when database completeness should block readiness.

The shotgun runner keeps database/tool blockers explicit, runs KneadData host depletion when `--host-reference` is supplied, routes Kraken2 and HUMAnN over the cleaned reads, and normalizes backend outputs into `tables/bracken_est_reads_matrix.tsv`, `tables/bracken_relative_abundance_matrix.tsv`, `tables/humann_pathabundance_matrix.tsv`, `tables/humann_genefamilies_matrix.tsv`, plus Bracken/HUMAnN summary JSON. It also derives `tables/top_bracken_taxa.tsv`, `tables/top_humann_pathways.tsv`, `tables/top_humann_gene_families.tsv`, `tables/metagenomics_backend_review.json`, and native dashboard/SVG review artifacts when those matrices are available. Missing database outputs remain `not_available` in the visualization manifest.

For direct Kraken2/Bracken/HUMAnN runs, the shotgun runner also writes `resources/resource_plan.json`, `resources/resource_manifest.tsv`, `resources/resource_env.sh`, `resources/resource_readiness.md`, and resource setup-plan artifacts. The Kraken2 database contract is always required; Bracken and HUMAnN are promoted to blocking resource checks when `--run-bracken` or `--run-humann` is requested.

## nf-core Adapter

When the user wants nf-core execution, use the adapter to generate pinned Nextflow commands and capture trace/report artifacts in the standard envelope:

```bash
python plugins/ngs-analysis/scripts/run_nfcore_pipeline.py \
  --pipeline rnaseq \
  --sample-sheet samplesheet.csv \
  --profile docker \
  --revision 3.18.0 \
  --genome GRCh38 \
  --bundle-root grch38_core=/refs/GRCh38 \
  --execute
```

Supported adapters include `rnaseq`, `scrnaseq`, `sarek`, `atacseq`, `chipseq`, `cutandrun`, `ampliseq`, and `taxprofiler`. Each adapter now writes a run-local resource gate under `resources/` before execution: `resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, `resource_setup_plan.json`, `resource_setup_plan.tsv`, `resource_setup_plan.md`, and `resource_setup_commands.sh`. Missing required reference or database bundles block the run envelope from being marked ready; use `--bundle-root bundle=/path`, `--genome-build`, and `--include-optional-resources` to make the readiness state explicit. Use `--skip-resource-plan` only for command-shape review, not for execution-readiness claims.

## References And Databases

Reference/database readiness is tracked separately from executable preflight:

```bash
python plugins/ngs-analysis/scripts/ngs_reference_manager.py list
python plugins/ngs-analysis/scripts/ngs_reference_manager.py check --kind reference --bundle grch38_core --root /refs/GRCh38
python plugins/ngs-analysis/scripts/ngs_reference_manager.py explain-missing --kind database --bundle kraken2_standard --root /db/kraken2/standard
python plugins/ngs-analysis/scripts/ngs_reference_manager.py plan --pipeline shotgun_metagenomics --include-optional --outdir resource_readiness/shotgun
python plugins/ngs-analysis/scripts/ngs_reference_manager.py setup-plan --pipeline shotgun_metagenomics --include-optional --outdir resource_readiness/shotgun_setup
python plugins/ngs-analysis/scripts/ngs_reference_manager.py plan --pipeline atacseq --genome-build GRCh38 --bundle-root grch38_core=/refs/GRCh38 --outdir resource_readiness/atac
python plugins/ngs-analysis/scripts/ngs_reference_manager.py inventory --outdir resource_readiness/inventory
python plugins/ngs-analysis/scripts/ngs_reference_manager.py lock --outdir resource_readiness/lock --include-checksums
python plugins/ngs-analysis/scripts/ngs_reference_manager.py verify-lock --lockfile resource_readiness/lock/resource_lock.json --outdir resource_readiness/lock_verify --fail-on-mismatch
python plugins/ngs-analysis/scripts/ngs_reference_manager.py check-all --kind database --output resource_readiness/database_audit.json
```

The `plan` command resolves pipeline-specific required and optional bundles, checks configured roots or `--bundle-root` overrides, and writes `resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, `resource_readiness.md`, plus setup-plan artifacts. This gives each analysis a concrete reference/database gate before execution. The companion `setup-plan` command writes only the operator setup bundle: `resource_setup_plan.json`, `resource_setup_plan.tsv`, `resource_setup_plan.md`, and `resource_setup_commands.sh`. The shell skeleton keeps setup hints commented by default so large database/reference downloads stay deliberate. The registries live in `references/reference-registry.json` and `references/database-registry.json`; they encode expected files, root environment variables, source notes, setup hints, size caveats, and license/version caveats.

The `inventory` command is the project-level resource surface. It checks every known reference/database bundle, accepts repeated `--bundle-root bundle=/path` overrides, and writes `resource_inventory.json`, `resource_inventory.tsv`, `resource_env.sh`, and `resource_dashboard.md`. Use it before broad multi-lane runs to see missing bundle files, env vars, setup hints, license notes, and which pipelines each bundle gates.

The `lock` command snapshots the current inventory into `resource_lock.json`, `resource_lock.tsv`, and `resource_lock.md`; add `--include-checksums` for SHA256 hashes on files below the checksum threshold. Use `verify-lock` before reruns or handoffs to prove that locked resources are still present and unchanged, or to produce a concrete drift report.

## BCL To FASTQ Execution

The BCL package validates `RunInfo.xml`, optional `RunParameters.xml`, `Data/Intensities/BaseCalls`, and the sample sheet. With `--execute`, it runs `bcl-convert` when installed, falls back to `bcl2fastq` when available, and otherwise records the converter blocker without auto-downloading proprietary software.

Successful executions now emit a demultiplexing QC summary under `qc/demux_qc_summary.json`, include generated FASTQs and BCL reports in `artifact_index.json`, and surface Docker-wrapper readiness in `validation/runtime_preflight.json` when the local converter is a Docker-backed wrapper.

```bash
python plugins/ngs-analysis/scripts/run_bcl_to_fastq.py \
  --run-folder /path/to/run \
  --sample-sheet SampleSheet.csv \
  --output-directory fastq_out \
  --execute
```

## Local Plugin Install

The shareable unit is a marketplace root containing both:

```text
.agents/plugins/marketplace.json
plugins/ngs-analysis/
```

Unzip or clone that root anywhere on the recipient machine, then add the root directory as a Codex local marketplace. Install `Life Sciences NGS Analysis` from the `Life Sciences NGS Analysis Local Plugins` marketplace. After installation, invoke it by asking for NGS routing or by referencing skills such as `ngs-analysis-router`, `ngs-fastq-qc`, `ngs-dna-somatic-variants`, or `ngs-scrna-seq`.

Do not distribute only the `plugins/ngs-analysis/` directory unless the recipient already knows how to register a Codex marketplace entry for it.

## Local Execution Profile

When Docker, registry egress, or Nextflow process containers are unavailable, route compact local execution runs through the `local_light` profile. This profile uses Snakemake or direct shell commands with isolated conda/mamba environments and avoids containers by default.

The default local lanes are FASTQ QC with FastQC/MultiQC, Salmon quantification for bulk RNA-seq inputs, bulk RNA-seq count-matrix differential expression, samtools/bcftools variant checks where suitable references exist, post-count single-cell QC, FASTQ-level epigenomics/amplicon/shotgun packages, and BCL run-folder validation/conversion when an Illumina converter is installed.

## Public-First Boundary

The default registry favors public packages and workflows such as nf-core, FastQC, MultiQC, Cutadapt, fastp, STAR, Salmon, GATK4, DeepVariant, samtools/bcftools, QIIME2, DADA2, Kraken2, and HUMAnN.

Some common tools are public to download but not fully open-source or may require EULA/license acceptance. Examples include Illumina BCL Convert, 10x Cell Ranger, DRAGEN, and Sentieon. The skills surface those boundaries before use.
