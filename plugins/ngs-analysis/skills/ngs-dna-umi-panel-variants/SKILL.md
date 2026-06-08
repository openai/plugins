---
name: ngs-dna-umi-panel-variants
description: Run or plan targeted DNA panel variant workflows that use UMIs, duplex consensus reads, molecular barcodes, low-frequency calling, target coverage, and panel-specific QC.
---

# UMI Panel DNA Variants

Use this skill for targeted DNA panels where molecular barcodes, UMIs, duplex consensus, or low-frequency allele detection are central to the analysis. If the panel is ordinary germline calling without molecular consensus, use `ngs-dna-germline-variants`.

## Essential Inputs

Confirm:

- panel/capture kit name and target BED
- UMI layout: inline read, index read, single UMI, duplex UMI, or unknown
- whether consensus reads have already been generated
- FASTQ/BAM input and pairing convention
- reference build and panel-specific annotation requirements
- minimum allele fraction goal and intended use: screening, research, validation, or exploratory
- positive/negative controls and expected spike-ins when available

## Route

Use a lab-validated panel workflow when provided. For public-tool planning, combine FASTQ QC, UMI extraction/consensus generation, alignment, target coverage QC, and variant calling as separate audited stages.

Preflight command:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline dna_umi_panel_variants --emit-install-plan
```

For compact local checks from prepared consensus or alignment BAM/CRAM files, use the dedicated UMI panel runner:

```bash
python plugins/ngs-analysis/scripts/run_dna_umi_panel_variants.py \
  --sample-sheet umi_panel_samples.tsv \
  --reference-fasta reference.fa \
  --target-bed panel_targets.bed \
  --umi-mode duplex \
  --umi-tag RX \
  --execute
```

This writes the consensus/variant command plan, molecular-consensus state, low-frequency calling settings, visualization index, `qc/umi_postrun_summary.{tsv,json}`, `qc/umi_molecular_evidence_contract.{tsv,json}`, and consensus-BAM VCF outputs when the local fgbio/samtools/bcftools backend is available. The post-run summary parses consensus flagstat, target coverage, bcftools stats, and family-size/duplex files when present; missing metrics stay explicit in the notes column. The molecular evidence contract keeps the low-AF review requirements visible per sample: consensus BAM, family-size or molecule-support metrics, variant stats, hotspot review, and duplex review.

The direct runner also emits `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, and `resource_readiness.md`. The resource check is advisory by default so custom or reduced references can still be planned; add `--genome-build`, `--bundle-root <bundle>=<path>`, and `--require-resource-plan` when missing registered reference bundles should block readiness.

## Decision Points

- Do not trim or discard UMI bases until their layout and destination are known.
- Separate raw read depth from unique molecular depth and consensus depth.
- Track on-target rate, coverage uniformity, family size distribution, strand/duplex support, and per-target dropout.
- Low allele fraction calls require stronger artifact review than ordinary germline calls.
- Use panel-specific hotspot/blacklist rules only when their provenance is known.

## Outputs

Produce:

- UMI layout and consensus strategy
- target BED/resource manifest
- raw-depth, molecular-depth, and consensus-depth QC summary
- `qc/umi_postrun_summary.tsv` for consensus reads, target coverage, variant counts, family size, and duplex fraction
- `qc/umi_molecular_evidence_contract.tsv` for low-AF evidence readiness, hotspot review, and duplex review expectations
- variant calls with allele fraction, depth, strand/duplex support, and filtering rationale
- limitations around sensitivity, panel dropout, molecule count, and non-validated interpretation
