---
name: ngs-epigenomics-peaks
description: Dispatch ATAC-seq, ChIP-seq, CUT&RUN, or CUT&Tag requests to assay-specific QC, alignment, signal-track, peak-calling, consensus, and differential peak workflows.
---

# Epigenomics Peaks

Use this skill as the epigenomics dispatcher for ATAC-seq, ChIP-seq, CUT&RUN, or CUT&Tag analysis. Hand off to the assay-specific deep skill once the assay type is known.

## Essential Inputs

Confirm:

- assay type
- FASTQ or BAM input
- organism and genome build
- blacklist file, if available
- control samples: input DNA, IgG, or spike-in
- biological replicates
- peak type: narrow, broad, accessibility, or protocol-specific
- desired outputs: QC report, peaks, consensus peaks, bigWigs, differential peaks

## Public Defaults

Choose the workflow by assay:

- ATAC-seq: `ngs-atacseq-peaks-qc` using `nf-core/atacseq` by default
- ChIP-seq: `ngs-chip-cutrun-peaks-qc` using `nf-core/chipseq` by default
- CUT&RUN or CUT&Tag: `ngs-chip-cutrun-peaks-qc` using `nf-core/cutandrun` by default

Use direct MACS2 only for focused peak-calling tasks from prepared BAMs.

## Preflight

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline epigenomics_peaks --emit-install-plan
```

## Local Execution Package

For FASTQ intake/QC over ATAC-seq, ChIP-seq, CUT&RUN, or CUT&Tag data, use the shared FASTQ assay package:

```bash
python plugins/ngs-analysis/scripts/run_fastq_assay_package.py \
  --lane epigenomics_peaks \
  --sample-sheet assay_samples.csv \
  --execute
```

This validates sample-sheet paths and read structure, runs seqkit stats and FastQC/MultiQC when available, and writes `peak_calling_readiness.json`. Full alignment, signal tracks, TSS/FRiP, consensus peaks, and differential analyses still route through the assay-specific workflow.

Assay-specific ATAC and ChIP/CUT&RUN runners now also emit native review files alongside TSV/JSON summaries: `qc/*_dashboard.html`, FRiP/peak SVG plots, insert-size SVG plots, browser-track preview HTML, UCSC track lines, and IGV session files.

## Kickoff Pattern

ATAC-seq preflight run:

```bash
nextflow run nf-core/atacseq \
  -profile test,docker \
  --outdir results/atacseq_test
```

ChIP-seq preflight run:

```bash
nextflow run nf-core/chipseq \
  -profile test,docker \
  --outdir results/chipseq_test
```

CUT&RUN/CUT&Tag preflight run:

```bash
nextflow run nf-core/cutandrun \
  -profile test,docker \
  --outdir results/cutandrun_test
```

Carry replicate and control metadata through the sample sheet before running real analysis.
