---
name: ngs-scrna-seq
description: Route single-cell or single-nucleus RNA-seq FASTQs to public count-generation workflows and defer post-count matrix QC, annotation, clustering, and UMAP analysis to the embedded scrna-seq-qc skill.
---

# Single-cell RNA-seq

Use this skill for scRNA-seq or snRNA-seq kickoff from FASTQs, Cell Ranger-style outputs, matrices, `.h5`, `.h5ad`, or `.rds`. This skill owns upstream intake and FASTQ-to-count routing; post-count QC, annotation, clustering, and UMAPs must route to the embedded `scrna-seq-qc` skill.

## Essential Inputs

Confirm:

- input type: FASTQ, count matrix, `.h5`, `.h5ad`, or `.rds`
- assay: single-cell or single-nucleus
- chemistry or barcode/UMI layout
- organism and reference
- expected cells per sample when available
- sample, donor, batch, and channel metadata
- desired endpoint: count matrix only, QC, clustering, annotation, UMAP, or differential abundance/expression

## Public Default

For FASTQs, prefer public alternatives:

- `nf-core/scrnaseq`
- STARsolo
- kallisto-bustools via `kb-python`
- alevin-fry

Use 10x Cell Ranger only when the user explicitly wants vendor-standard output and has accepted the 10x EULA.

## Implementation Sequence

Treat scRNA as three ordered rows in the plugin state and execute them sequentially:

1. FASTQ-to-count:
   count matrix generation, barcode and feature tables, chemistry or whitelist choice, and a backend summary.
2. Post-count QC and annotation:
   raw-count-preserving objects, QC metrics, threshold plots, doublet and ambient-RNA outputs, clustering, UMAPs, and annotation confidence.
3. Downstream stats:
   pseudobulk matrices, differential expression or abundance tables, and per-condition plots.

Cell Ranger is an optional backend when vendor-standard output is explicitly required. It is not a standalone roadmap row and it is not the default execution target.

For post-count QC/annotation, use the embedded `skills/scrna-seq-qc` guidance. Route to that skill whenever the requested endpoint starts from a matrix, `.h5`, `.h5ad`, `.rds`, Cell Ranger output, or asks for QC, doublets, ambient RNA, annotation, clustering, UMAPs, or post-count differential summaries.

## Preflight

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline scrnaseq --emit-install-plan
```

## Kickoff Pattern

nf-core preflight run:

```bash
python plugins/ngs-analysis/scripts/run_nfcore_pipeline.py \
  --pipeline scrnaseq \
  --sample-sheet samplesheet.csv \
  --profile docker \
  --genome GRCh38 \
  --bundle-root grch38_core=/refs/GRCh38
```

This adapter captures the generated params, pinned Nextflow command, resource gate, trace/report paths, run manifest, and visualization index in the standard plugin envelope. Add `--revision <tag>` for pinned nf-core execution and `--execute` only when Nextflow plus a container/HPC profile are ready.

Plugin-owned local execution:

```bash
python plugins/ngs-analysis/scripts/run_scrnaseq_fastq_to_count.py \
  --sample-sheet samplesheet.csv \
  --genome-fasta reference/genome.fa \
  --annotation-gtf reference/genes.gtf \
  --cb-whitelist reference/whitelist.txt \
  --execute
```

The FASTQ-to-count runner emits advisory `resources/resource_plan.json`, `resource_manifest.tsv`, `resource_env.sh`, and `resource_readiness.md` outputs by default. Add `--genome-build`, `--bundle-root <bundle>=<path>`, and `--require-resource-plan` when STARsolo reference bundle completeness should block readiness.

Matrix-level QC should be handled by `scrna-seq-qc` and must preserve raw counts, per-sample metadata, filter decisions, doublet calls, ambient-RNA handling, and plot outputs.

## Guardrails

- Do not assume 10x chemistry from filenames alone.
- Do not silently skip doublet or ambient-RNA assessment when doing QC.
- Do not over-annotate clusters without matched references or clear markers.
