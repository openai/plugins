---
name: ngs-dna-somatic-variants
description: Run or plan tumor-normal, tumor-only, WGS, WES, or cancer-panel somatic variant workflows with pairing, contamination, panel-of-normals, purity, QC, and annotation checks.
---

# Somatic DNA Variants

Use this skill for tumor-normal or tumor-only somatic SNV/indel calling from FASTQ, BAM, or CRAM. If the request is inherited germline calling or family analysis, use `ngs-dna-germline-variants`.

## Essential Inputs

Confirm:

- tumor-normal, tumor-only, relapse-baseline, or multi-tumor design
- WGS, WES, or panel assay and target BED when applicable
- input type and whether reads are already aligned
- tumor/normal pairing table and sample identifiers
- reference build, known-sites, germline resource, and annotation cache
- panel-of-normals availability and matched-normal availability
- tumor purity, contamination expectations, and minimum allele fraction goals
- desired outputs: raw calls, filtered calls, VEP/SnpEff annotation, MAF, CNV/SV handoff

## Route

Prefer `nf-core/sarek` for an end-to-end public workflow when its supported callers fit the request. Use direct GATK Mutect2 or bcftools/samtools utilities for focused validation or prepared BAMs.

Preflight command:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline dna_somatic_variants --emit-install-plan
```

For compact local checks from prepared tumor/normal BAM/CRAM files, use the dedicated Mutect2 runner:

```bash
python plugins/ngs-analysis/scripts/run_dna_somatic_variants.py \
  --sample-sheet somatic_pairs.tsv \
  --reference-fasta reference.fa \
  --germline-resource af-only-gnomad.vcf.gz \
  --panel-of-normals pon.vcf.gz \
  --execute
```

This produces a tumor-normal/tumor-only pairing table, Mutect2 command plan, contamination/filtering artifacts, somatic QC summary, `qc/somatic_pair_review.{tsv,json}`, visualization index, and filtered VCF outputs when the local GATK resources are available. For nf-core execution, use `plugins/ngs-analysis/scripts/run_nfcore_pipeline.py --pipeline sarek`.

The direct runner also emits `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, and `resource_readiness.md`. The resource check is advisory by default so custom or reduced references can still be planned; add `--genome-build`, `--bundle-root <bundle>=<path>`, and `--require-resource-plan` when missing registered reference bundles should block readiness.

## Decision Points

- Verify tumor-normal pair metadata before execution. A swapped or missing normal changes the biological meaning of the calls.
- For tumor-only analysis, explicitly state the false-positive risk and require a germline resource plus careful filtering.
- Use panel-of-normals when available and reference-matched; do not reuse a PON across incompatible capture kits or genome builds.
- Track contamination, orientation bias, strand artifacts, mapping quality, coverage, tumor purity, and allele-fraction filters.
- Keep germline filtering separate from somatic interpretation; avoid presenting tumor-only calls as confirmed somatic without supporting evidence.

## Outputs

Produce:

- validated pairing/sample sheet
- caller/filter settings and reference/resource manifest
- QC summary: tumor/normal depth, contamination, duplication, insert size, on-target rate for panels/WES
- per-pair review table covering matched-normal state, PON/germline-resource availability, contamination-table status, filtered VCF status, and parsed variant counts
- VCF/MAF/annotation paths and a filtered-vs-raw call count summary
- caveats for tumor-only calls, low-purity tumors, low-depth regions, or missing matched normals

Clinical actionability and treatment recommendations are out of scope unless the user supplies a validated clinical interpretation workflow.
