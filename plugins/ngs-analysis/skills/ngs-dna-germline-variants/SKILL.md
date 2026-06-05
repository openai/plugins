---
name: ngs-dna-germline-variants
description: Run or plan deep germline WGS, WES, targeted-panel, cohort, or trio variant-calling workflows with reference-build, known-sites, QC, joint-calling, and annotation checks.
---

# Germline DNA Variants

Use this skill for germline WGS, WES, or inherited-disease panel analysis from FASTQ, BAM, or CRAM. If the request is tumor-only, tumor-normal, or low-frequency molecular-barcode panel calling, use a somatic or UMI-panel skill instead.

## Essential Inputs

Confirm:

- data type: WGS, WES, or targeted panel
- sample model: singleton, cohort, duo, trio, family, or case/control
- input type: FASTQ, BAM, or CRAM
- organism, reference build, FASTA, indexes, and contig naming
- known-sites resources for BQSR, contamination, and annotation
- target BED and bait BED for WES/panel data
- sex/ploidy assumptions and mitochondrial/sex-chromosome requirements
- desired callers, annotation outputs, and final VCF/gVCF expectations

## Route

Prefer `nf-core/sarek` for full FASTQ/BAM-to-VCF workflows. Use direct GATK4, DeepVariant, samtools, or bcftools only for focused tasks or a custom workflow.

Preflight command:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline dna_germline_variants --emit-install-plan
```

For compact local checks from prepared BAM/CRAM files, use the shared DNA execution package:

```bash
python plugins/ngs-analysis/scripts/run_dna_variant_calling.py \
  --sample-sheet dna_samples.tsv \
  --reference-fasta reference.fa \
  --execute
```

Treat this as a focused samtools/bcftools run envelope, not as a substitute for full cohort, trio, gVCF, BQSR, or annotation workflows.

For a higher-fidelity local germline run that owns BQSR, per-sample gVCFs, and joint genotyping assumptions, use the germline-specific runner:

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

This runner still expects reference-matched resources and an available GATK toolchain. It packages the validation state and generated artifacts even when execution is blocked by missing tools or resources.

It also writes advisory `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, and `resource_readiness.md` artifacts by default. Add `--genome-build`, `--bundle-root <bundle>=<path>`, and `--require-resource-plan` when complete registered reference and known-sites bundles should be mandatory for readiness.

## Decision Points

- For cohorts or families, decide whether the endpoint is per-sample VCFs, gVCFs for joint genotyping, or a jointly called cohort VCF.
- For WES/panels, carry the target BED through alignment metrics, calling, and coverage reports; do not call off-target regions by accident.
- Use BQSR only when reference-matched known-sites resources exist. Do not mix GRCh37, hg19, GRCh38, or T2T resources.
- Check sample identity, sex concordance, contamination, coverage, duplication, insert size, and transition/transversion where feasible.
- For trios, preserve pedigree metadata and report Mendelian/QC checks separately from variant interpretation.

## Outputs

Produce:

- command or workflow profile and sample sheet
- reference/resource manifest with versions and checksums when available
- QC summary: coverage, duplication, insert size, contamination, sex/relatedness checks when run
- VCF/gVCF path, index path, and annotation path
- limitations: low coverage, missing known-sites, target design gaps, or build mismatches

Clinical interpretation, pathogenicity classification, and report signing are out of scope unless the user provides a validated clinical workflow.
