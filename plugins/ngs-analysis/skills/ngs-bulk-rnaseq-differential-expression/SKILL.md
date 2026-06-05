---
name: ngs-bulk-rnaseq-differential-expression
description: Run or plan bulk RNA-seq differential-expression analysis from count matrices with replicate, design formula, contrast, batch, normalization, QC plot, and result-table checks.
---

# Bulk RNA-seq Differential Expression

Use this skill when the user has raw counts or a count-generation output and wants differential expression, contrasts, QC plots, or ranked gene tables.

## Essential Inputs

Confirm:

- raw count matrix path and sample metadata path
- gene ID type and annotation mapping requirement
- biological conditions, replicates, batch variables, donor pairing, covariates, and exclusions
- exact contrasts and baseline levels
- preferred statistical framework: DESeq2, edgeR, limma-voom, or existing lab standard
- output needs: normalized counts, PCA, sample distance, volcano plots, heatmaps, ranked tables, GSEA-ready lists

## Preconditions

Do not start differential expression until:

- raw counts are preserved
- each requested contrast has enough biological replication
- sample metadata row names match count matrix columns
- batch/covariate choices are explicit
- exploratory PCA/sample-distance plots do not reveal obvious swaps or failed libraries

## Route

For most count matrices, use DESeq2 or edgeR. Use limma-voom when the study design or lab standard favors it. Keep the analysis in R when using Bioconductor unless the user specifically asks for a Python-only workflow.

The plugin-owned local runner is:

```bash
python plugins/ngs-analysis/scripts/run_bulk_rnaseq_de.py \
  --count-matrix count_matrix.tsv \
  --sample-metadata sample_metadata.tsv \
  --contrasts contrasts.tsv \
  --execute
```

Use `--method auto` unless the user or lab standard specifies `DESeq2`, `edgeR`, or `limma_log2`. Auto mode uses DESeq2 when integer-like counts and the package are available, falls back to edgeR for integer-like counts, and uses `limma_log2` for non-integer expression matrices.

Use `--input-mode` to declare whether the matrix is `raw_counts`, `normalized_expression`, or `log_expression`. When `--input-mode auto` is used, the runner infers the mode and records a warning if normalization is skipped because the matrix is already transformed.

Preflight command:

```bash
python plugins/ngs-analysis/scripts/ngs_preflight.py --pipeline bulk_rnaseq_differential_expression --emit-install-plan
```

## Decision Points

- Never compare groups without stating the design formula and contrast.
- Treat batch correction in modeling separately from visual batch removal.
- Do not filter genes using post-hoc knowledge of the contrast.
- For paired or repeated-measures designs, model subject/donor explicitly.
- Report genes with effect size, uncertainty, adjusted p-value, and filtering status.

## Outputs

Produce:

- design formula and contrast manifest
- QC plots: library size, detected genes, PCA/sample distance, mean-variance trend, and outlier review
- input-mode-aware matrix exports plus the modeling/log-scale matrix used for DE
- differential-expression tables per contrast
- explicit `.not_tested.tsv` stubs for contrasts blocked by insufficient replication or confounding
- auto-launched localhost Marimo review app recorded in `notebooks/marimo_server.json`
- caveats for small n, confounded designs, failed samples, or batch variables that cannot be estimated
- standard run envelope: `run_manifest.json`, `config.json`, `validation/`, `logs/`, `versions/`, `visualizations/`, `notebooks/`, `artifact_index.json`, and `summary.md`
