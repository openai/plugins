---
name: ngs-chip-cutrun-peaks-qc
description: Run or plan ChIP-seq, CUT&RUN, or CUT&Tag QC, control handling, spike-in, peak calling, broad-vs-narrow target selection, replicate, bigWig, and differential binding workflows.
---

# ChIP/CUT&RUN Peaks QC

Use this skill for antibody-targeted enrichment workflows: ChIP-seq, CUT&RUN, or CUT&Tag. Use `ngs-atacseq-peaks-qc` for ATAC-seq.

## Essential Inputs

Confirm:

- assay: ChIP-seq, CUT&RUN, or CUT&Tag
- target class: transcription factor, histone mark, chromatin regulator, or custom target
- FASTQ/BAM inputs and paired-end status
- input DNA, IgG, no-antibody, or spike-in controls
- organism, genome build, blacklist, and spike-in genome if used
- biological replicates, conditions, batches, and sample metadata
- desired endpoint: QC, peaks, bigWigs, consensus peaks, or differential binding

## Route

Use `nf-core/chipseq` for ChIP-seq and `nf-core/cutandrun` for CUT&RUN/CUT&Tag when they fit the assay. Use direct MACS2 only for prepared BAMs with known control and duplicate policy.

Preflight command:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline chip_cutrun_peaks_qc --emit-install-plan
```

For compact FASTQ intake/QC, use the shared epigenomics execution package:

```bash
python plugins/ngs-analysis/scripts/run_fastq_assay_package.py \
  --lane epigenomics_peaks \
  --sample-sheet chip_or_cutrun_samples.csv \
  --execute
```

It records FASTQ-level QC and peak-calling readiness.

For local-light alignment, control-aware MACS2 peak calling, FRiP, bigWig tracks, consensus peaks, and motif-handoff artifacts, use the dedicated ChIP/CUT&RUN runner:

```bash
python plugins/ngs-analysis/scripts/run_chip_cutrun_peaks_qc.py \
  --sample-sheet chip_or_cutrun_samples.csv \
  --assay chipseq \
  --target-class tf \
  --peak-mode narrow \
  --bowtie2-index /refs/GRCh38/bowtie2/genome \
  --genome-size hs \
  --blacklist-bed /refs/GRCh38/blacklists/encode_blacklist.bed \
  --execute
```

This runner emits `qc/chip_cutrun_qc_summary.{tsv,json}`, `qc/chip_cutrun_qc_dashboard.html`, native SVG FRiP/peak and insert-size plots, browser-track handoff files under `tracks/`, and `motifs/motif_summary.tsv`. Add `--run-motifs --motif-genome <genome>` when HOMER motif enrichment should be executed instead of only planned.

It also emits `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, and `resource_readiness.md`. The resource check is advisory by default for local-light runs; add `--genome-build`, `--bundle-root <bundle>=<path>`, and `--require-resource-plan` when missing registered reference bundles should block readiness.

For nf-core execution, use `plugins/ngs-analysis/scripts/run_nfcore_pipeline.py --pipeline chipseq` or `--pipeline cutandrun`.

## Decision Points

- Choose narrow versus broad peak mode from target biology, not from convenience.
- Preserve control pairing and spike-in metadata through sample sheets.
- For histone marks, expect broad or domain-like signal for many marks; for TFs, expect sharper peaks and stronger replicate checks.
- Review alignment rate, duplicate rate, fragment size, FRiP/peak signal, blacklist overlap, and replicate concordance.
- Keep consensus peak generation and differential binding design separate from raw peak calling.

## Outputs

Produce:

- assay/target/control manifest
- command/profile and sample sheet
- QC summary with replicate/control status
- peaks, bigWigs, browser-track manifests, browser-track preview HTML, native QC dashboard/SVG plots, consensus peaks, and count matrix when requested
- motif summary files when a motif backend is requested
- differential binding design and caveats for missing controls, weak enrichment, or poor replicate concordance
