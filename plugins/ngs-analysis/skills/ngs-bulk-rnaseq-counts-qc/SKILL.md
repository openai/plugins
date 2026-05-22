---
name: ngs-bulk-rnaseq-counts-qc
description: Run or plan bulk RNA-seq FASTQ-to-count processing with sample-sheet, strandedness, genome annotation, alignment or pseudoalignment, MultiQC, and count-matrix QC checks.
---

# Bulk RNA-seq Counts QC

Use this skill for bulk RNA-seq read processing, quantification, and count-matrix generation. If the user already has a count matrix and wants contrasts or statistics, use `ngs-bulk-rnaseq-differential-expression`.

## Essential Inputs

Confirm:

- FASTQ or aligned-read inputs and paired-end/single-end status
- organism, genome build, FASTA, GTF, and gene ID convention
- strandedness or permission to infer strandedness
- sample sheet with biological condition, replicate, batch, and library metadata
- desired quantification: gene counts, transcript estimates, or both
- alignment strategy: `STAR/Salmon`, Salmon-only, featureCounts from BAMs, or existing lab protocol

## Route

Prefer `nf-core/rnaseq` for standard processing when a stable container or HPC runtime is available. Use the `local_light` Snakemake/Salmon path for small local/devbox feasibility runs when Docker, registry egress, or Nextflow process containers are the blocker.

The plugin-owned local runner is:

```bash
python plugins/ngs-analysis/scripts/run_bulk_rnaseq_counts_qc.py \
  --sample-sheet samplesheet.csv \
  --fastq-root path/to/fastqs \
  --transcriptome-fasta reference/transcriptome.fasta \
  --genome-fasta reference/genome.fa \
  --annotation-gtf reference/genes.gtf \
  --execute
```

Omit `--execute` for validation plus Snakemake workflow validation only. Use `--no-dry-run` only when the user wants input validation and run-envelope preparation without workflow graph validation.

The runner emits a run-local `resources/` readiness bundle with `resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, and `resource_readiness.md`. Resource checks are advisory by default for custom or reduced references; add `--genome-build`, `--bundle-root <bundle>=<path>`, and `--require-resource-plan` when a registered genome bundle must be complete before the run is considered ready.

Preflight command:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bulk_rnaseq_counts_qc --emit-install-plan
python plugins/ngs-analysis/scripts/ngs_preflight.py --profile local_light --emit-install-plan
```

## Decision Points

- If strandedness is unknown, infer it before final counting; do not lock in a design based on library guesses.
- If strandedness is provided, carry it into the quantification command and flag any disagreement between the configured library type and Salmon's inferred format.
- Keep genome FASTA, GTF, transcriptome, and aligner indexes from the same build/release.
- Inspect per-sample reads, mapping rate, rRNA/mitochondrial fraction when available, duplication, insert size, gene-body bias, and assignment rate.
- Preserve raw counts separately from normalized expression.
- Carry sample metadata forward exactly; downstream DE depends on this table.

## Outputs

Produce:

- sample sheet and command/profile
- reference manifest with genome and GTF release
- MultiQC or equivalent processing summary
- Salmon `quant.sf` outputs, TPM/NumReads/effective-length matrices, and carried-forward sample metadata
- Gene-level expected-count and TPM matrices derived from transcript-level Salmon outputs, plus a `tx2gene` provenance table
- Compact QC verdict JSON covering mapping rate, duplication, library-type agreement, and outlier samples
- Browser-safe MultiQC helper HTML pages and a localhost launch hint for reliable in-app review
- Run-local reference readiness artifacts under `resources/`, including the resource plan, manifest, environment exports, and Markdown readiness summary
- issues that block differential expression, such as missing replicates, mislabeled groups, or severe batch/library failures
- standard run envelope: `run_manifest.json`, `config.json`, `validation/`, `logs/`, `versions/`, `artifact_index.json`, and `summary.md`
