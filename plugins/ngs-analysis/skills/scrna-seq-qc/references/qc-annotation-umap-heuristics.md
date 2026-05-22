# General scRNA-seq QC Heuristics

Use this file when choosing dataset-specific QC thresholds, annotation strategy, or UMAP feature-selection rules for a new single-cell or single-nucleus RNA-seq dataset.

## Choosing QC Thresholds

Always choose thresholds from the observed data and expected biology. Do not copy a single min-genes or mitochondrial cutoff across tissues, species, assay types, or chemistries.

Inspect these plots overall and per batch:

- Histogram or density of detected genes per barcode
- Histogram or density of total UMIs per barcode
- Scatter of total UMIs vs detected genes
- Mitochondrial fraction by batch
- Any tissue-specific nuisance fraction such as ribosomal, hemoglobin, chloroplast, or stress-response signal

Inspect the full QC panel, but by default only filter on the standard core metrics:

- detected genes per cell
- total counts or UMIs per cell
- `percent.mt`

Treat other QC metrics as review signals first, not automatic filters. Ambient RNA metrics are the main exception: they may be used for filtering when the dataset and workflow support them. If another nonstandard metric looks important enough to drive filtering for this dataset, surface that explicitly, explain the evidence, and consult the user before adding it as a hard cutoff.

### Detected genes per cell

Use one of these patterns:

- Prefer the local minimum between low-complexity barcodes and the main cell distribution when the histogram shows a clear valley.
- If there is no clear valley, define putative cells broadly, then choose a conservative lower cutoff from a robust outlier rule such as 3 MAD below the median of putative cells.
- Review the cutoff against expected biology so that small but real cell types are not removed by default.

Starting guesses are allowed only as a first pass:

- Typical droplet scRNA-seq: often a few hundred to low thousands of genes
- Single-nucleus data: often lower than whole-cell data
- High-complexity tissues or deep sequencing: often higher than shallow droplet datasets

Always keep the plot that justified the final choice.

### Total UMIs and upper outliers

Use total UMIs and detected genes together:

- Very low UMI outliers usually track low-complexity barcodes.
- Very high UMI or very high gene-count outliers often indicate doublets or multiplets, but some large cell types are real.

Use conservative upper-tail rules such as:

- Above a very high percentile
- Several MAD above the median within batch

Then review whether flagged cells belong to known large-cell populations before removing them.

### Mitochondrial and nuisance fractions

There is no universal mitochondrial cutoff.

- In stressed whole-cell datasets, higher mitochondrial fractions can mark dying cells.
- In nucleus datasets, mitochondrial fraction is often less informative.
- Some tissues need additional nuisance metrics, for example hemoglobin in blood-contaminated samples or chloroplast genes in plant data.

Choose the nuisance thresholds from the observed distributions and include a plot with the selected cutoff.

Even when additional nuisance metrics are plotted and interpreted, default filtering should still be limited to detected genes, total counts, and `percent.mt`, with ambient RNA filtering allowed as a supported exception. Other extra filters should only be added with explicit user approval.

## Required Doublet Detection Method

Use `scDblFinder` as the default and required doublet caller for this skill.

- Run `scDblFinder` per batch, capture channel, or other technical partition so the caller sees realistic collision structure.
- For very large partitions, split them into smaller chunks before calling `scDblFinder`, then merge the calls back onto the parent object by cell barcode.
- Preserve the doublet score, class call, and the partition used for calling in the output metadata.
- Do not silently replace `scDblFinder` with another method. If the runtime cannot support R or Bioconductor dependencies, report that as a blocker or get explicit approval before using a fallback.

Why this is the default:

- It is robust for droplet-style scRNA-seq and snRNA-seq data.
- It supports sample-aware calling, which matters for multiplexed or batched experiments.
- It works well with a provenance-preserving workflow where cells are flagged rather than immediately removed.

## When to Use scVI

Choose the latent-space method based on the analytical need, not by habit.

Prefer a standard PCA or Scanpy workflow when:

- the dataset is relatively small
- batch structure is minimal or already well controlled
- the main goal is straightforward QC, clustering, or plotting within one coherent dataset
- a conventional embedding is likely to answer the question without extra modeling overhead

Prefer `scVI` when:

- integration across batches, donors, chemistries, or studies is an explicit goal
- the dataset is large enough that a learned latent space is likely to improve robustness
- batch effects or technical heterogeneity clearly interfere with biological structure
- downstream annotation or comparison benefits from a shared latent representation

Be cautious with `scVI` when:

- the dataset has only a small number of cells overall
- individual batches are tiny
- the model complexity is unlikely to buy much beyond PCA

Record why `scVI` was used or skipped so the choice is auditable.

## Annotation When an Allen Brain Atlas Reference Is Not Appropriate

Choose references in this order of preference:

1. Same species
2. Same tissue or organ system
3. Same assay type and chemistry
4. Similar biological state, development stage, or disease context

If a matched reference exists, use a compatible mapping workflow such as:

- scANVI or scArches when you control or can rebuild the reference
- Seurat or Azimuth-style mapping when a mature Seurat reference exists
- SingleR when a suitable reference expression atlas is available
- CellTypist for immune or blood-rich datasets

If no strong reference exists:

- Cluster the dataset
- Call coarse compartments first
- Identify canonical and cluster-specific markers
- Use cluster-level or pseudobulk markers to refine labels
- Leave uncertain clusters as unknown, ambiguous, or mixed

Prefer conservative hierarchical labels over overconfident fine labels.

Cross-species mapping can still help, but use it mainly for coarse lineage assignment unless conservation is known to be strong.

## Marker-Gene Selection for Global UMAP

For a general-purpose global UMAP, use an informative panel rather than all genes when the dataset is large or when nuisance programs dominate the embedding.

Recommended heuristic:

1. Compute HVGs in a batch-aware way.
2. Define coarse groups from high-confidence labels or unsupervised clusters.
3. Add top marker genes per coarse group so all major compartments are represented.
4. Remove nuisance-heavy genes if they dominate the panel:
   - mitochondrial genes
   - ribosomal genes
   - hemoglobin genes
   - strong cell-cycle genes when they obscure lineage structure
   - stress or dissociation genes when they dominate the signal
5. Keep the panel compact but diverse.

Reasonable panel sizes are often:

- Small datasets: roughly 1k to 3k genes
- Medium to large datasets: roughly 2k to 8k genes

The goal is coverage of major biological structure, not maximum panel size.

If no stable labels exist yet, use HVGs alone or use the learned latent space directly.

## Plot Legibility

All QC and embedding plots should be easy to read.

- Do not put an excessive number of categories into one panel or legend.
- Use coarse labels for overview plots and reserve fine labels for per-group or faceted plots.
- Split figures by batch, neighborhood, lineage, or major compartment when that improves readability.
- If a categorical legend becomes too large to parse, reduce the categories shown in that panel or make separate figures rather than shrinking text until it is unreadable.
- Favor a smaller set of interpretable plots over a single overloaded summary figure.

## Large-Dataset Memory Practices

Treat memory movement as a first-class design constraint.

- Avoid copying full AnnData or Seurat objects.
- Prefer views, backed mode, chunked readers, and subset manifests over duplicated matrices.
- Keep matrices sparse and avoid densifying whole objects.
- Run `scDblFinder` and similar expensive steps per batch or per split subset.
- When passing data between Python and R, pass only the required cells and metadata, not the entire parent object.
- Free intermediates aggressively after large steps.
- Write checkpoints after major QC, annotation, and embedding stages.

Copying should be avoided not only for count matrices but also for whole analysis objects, temporary exports, and language-bridge handoffs.
