---
name: ngs-atacseq-peaks-qc
description: Run or plan ATAC-seq QC, alignment, TSS enrichment, fragment-size, blacklist, peak-calling, consensus peak, and differential accessibility workflows.
---

# ATAC-seq Peaks QC

Use this skill for ATAC-seq accessibility analysis from FASTQ or BAM. If the assay is ChIP-seq, CUT&RUN, CUT&Tag, or antibody-targeted enrichment, use `ngs-chip-cutrun-peaks-qc`.

## Essential Inputs

Confirm:

- FASTQ/BAM inputs and paired-end status
- organism, genome build, blacklist, and mitochondrial contig names
- biological replicates, conditions, batches, and sample metadata
- whether the target is QC only, peaks, consensus peaks, bigWigs, or differential accessibility
- whether Tn5 shifting is handled by the chosen workflow
- desired peak caller and downstream matrix generation

## Route

Prefer `nf-core/atacseq` for full reproducible processing. Use direct MACS2 only when BAMs are already aligned, duplicate/blacklist handling is known, and the user wants focused peak calling.

Preflight command:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline atacseq_peaks_qc --emit-install-plan
```

For compact read-level intake/QC, use the shared epigenomics execution package:

```bash
python plugins/ngs-analysis/scripts/run_fastq_assay_package.py \
  --lane epigenomics_peaks \
  --sample-sheet atac_samples.csv \
  --execute
```

For local-light ATAC alignment, peaks, FRiP, TSS, bigWig tracks, and consensus peaks from FASTQ or prepared BAMs, use the dedicated ATAC runner:

```bash
python plugins/ngs-analysis/scripts/run_atacseq_peaks_qc.py \
  --sample-sheet atac_samples.csv \
  --bowtie2-index /refs/GRCh38/bowtie2/genome \
  --genome-size hs \
  --blacklist-bed /refs/GRCh38/blacklists/encode_blacklist.bed \
  --tss-bed /refs/GRCh38/tss.bed \
  --execute
```

This runner emits `qc/atacseq_qc_summary.{tsv,json}`, `qc/atacseq_qc_dashboard.html`, native SVG FRiP/peak and insert-size plots, browser-track handoff files under `tracks/`, and TSS profile/heatmap commands when `--tss-bed` is supplied. Add `--run-motifs --motif-genome <genome>` when HOMER motif enrichment should be part of the backend run.

It also emits `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, and `resource_readiness.md`. The resource check is advisory by default for local-light runs; add `--genome-build`, `--bundle-root <bundle>=<path>`, and `--require-resource-plan` when missing registered reference bundles should block readiness.

For nf-core execution, use `plugins/ngs-analysis/scripts/run_nfcore_pipeline.py --pipeline atacseq`.

## QC Gates

Review before biological interpretation:

- read depth, alignment rate, duplicate rate, and mitochondrial fraction
- insert-size periodicity/nucleosome pattern
- TSS enrichment and FRiP score when available
- blacklist overlap and peak count per sample
- replicate concordance and consensus peak support

Do not proceed to differential accessibility if replicate quality or metadata is insufficient.

## Outputs

Produce:

- sample sheet and workflow command/profile
- QC summary and failed-sample flags
- narrowPeak/BED peak sets, consensus peaks, bigWigs, browser-track manifests, browser-track preview HTML, native QC dashboard/SVG plots, TSS plots, and peak-count matrix when requested
- motif summary files when a motif backend is requested
- differential-accessibility design and contrasts if applicable
- caveats for low TSS enrichment, high mitochondrial reads, weak replicate concordance, or poor FRiP
