---
name: ngs-bulk-rnaseq
description: Dispatch bulk RNA-seq requests to FASTQ-to-count QC or count-matrix differential-expression skills using nf-core/rnaseq, STAR, Salmon, featureCounts, MultiQC, and R/Bioconductor workflows.
---

# Bulk RNA-seq

Use this skill as the bulk RNA-seq dispatcher. Route FASTQ/BAM processing to count-generation QC, and route count-matrix statistical analysis to differential-expression guidance.

## Essential Inputs

Confirm:

- organism and genome build
- FASTA and GTF, or supported nf-core genome key
- paired-end or single-end reads
- strandedness, or whether to infer strandedness
- sample sheet and metadata
- counts-only vs differential expression
- contrasts, covariates, and batch terms for differential expression

## Dispatch

- FASTQ or aligned reads to raw counts, transcript estimates, or MultiQC summaries: `ngs-bulk-rnaseq-counts-qc`
- Raw count matrix plus sample metadata to contrasts, plots, and DE result tables: `ngs-bulk-rnaseq-differential-expression`

If the user asks for both, run count-generation planning first and start differential expression only after the raw count matrix, sample metadata, replicates, design formula, and contrasts are confirmed.

## Public Default

Prefer `nf-core/rnaseq` for standardized processing when a stable container or HPC runtime is available. Use the `local_light` Snakemake/Salmon path when Docker, registry egress, or Nextflow process containers are unavailable and a compact local run is appropriate.

## Plugin-Owned Local Paths

Use the counts/QC runner for local FASTQ-to-matrix execution:

```bash
python plugins/ngs-analysis/scripts/run_bulk_rnaseq_counts_qc.py \
  --sample-sheet samplesheet.csv \
  --fastq-root path/to/fastqs \
  --transcriptome-fasta reference/transcriptome.fasta \
  --genome-fasta reference/genome.fa \
  --annotation-gtf reference/genes.gtf \
  --execute
```

Use the differential-expression runner when the user already has a count or expression matrix:

```bash
python plugins/ngs-analysis/scripts/run_bulk_rnaseq_de.py \
  --count-matrix count_matrix.tsv \
  --sample-metadata sample_metadata.tsv \
  --contrasts contrasts.tsv \
  --execute
```

## Preflight

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bulk_rnaseq --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bulk_rnaseq_counts_qc --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bulk_rnaseq_differential_expression --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --profile local_light --emit-install-plan
```

## Kickoff Pattern

Preflight run:

```bash
nextflow run nf-core/rnaseq \
  -profile test,docker \
  --outdir results/rnaseq_test
```

Real run skeleton:

```bash
nextflow run nf-core/rnaseq \
  -profile docker \
  --input samplesheet.csv \
  --outdir results/rnaseq \
  --genome GRCh38 \
  --aligner star_salmon
```

If strandedness is unknown, run inference or use the pipeline's strandedness detection before committing to final counts.

Local execution run:

```bash
python plugins/ngs-analysis/scripts/run_bulk_rnaseq_counts_qc.py \
  --sample-sheet samplesheet.csv \
  --fastq-root path/to/fastqs \
  --transcriptome-fasta reference/transcriptome.fasta
```

The local runners create a standard run envelope with `run_manifest.json`, `config.json`, `validation/`, `logs/`, `versions/`, `artifact_index.json`, and `summary.md`. Do not depend on development-only eval harness paths in a shared package.

## Downstream

Only start DESeq2/edgeR/limma analysis after confirming biological replicates, design formula, and contrasts. Preserve the raw count matrix and sample metadata.
