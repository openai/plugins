#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(limma)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 7) {
  stop("usage: run_bulk_de.R <count_matrix.tsv> <sample_metadata.tsv> <contrasts.tsv> <method> <input_mode> <fit_formula> <outdir>")
}

count_path <- args[[1]]
metadata_path <- args[[2]]
contrasts_path <- args[[3]]
method <- args[[4]]
input_mode <- args[[5]]
fit_formula <- args[[6]]
outdir <- args[[7]]

dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
for (child in c("config", "manifest", "logs", "qc", "results", "plots", "versions")) {
  dir.create(file.path(outdir, child), recursive = TRUE, showWarnings = FALSE)
}

safe_name <- function(x) {
  gsub("[^A-Za-z0-9_.-]+", "_", x)
}

write_matrix_artifact <- function(path, values, counts, gene_name) {
  write.table(
    data.frame(gene_id = counts$gene_id, gene_name = gene_name, values, check.names = FALSE),
    file = path,
    sep = "\t",
    quote = FALSE,
    row.names = FALSE
  )
}

mean_without_self <- function(mat) {
  if (ncol(mat) < 2) {
    return(rep(0, ncol(mat)))
  }
  apply(mat, 1, function(x) sum(x) / (length(x) - 1))
}

write_log <- function(...) {
  write(paste(...), file = file.path(outdir, "logs", "run.log"), append = TRUE)
}

pad_range <- function(values, frac = 0.08) {
  rng <- range(values, finite = TRUE)
  span <- diff(rng)
  if (!is.finite(span) || span == 0) {
    span <- max(abs(rng), 1)
  }
  c(rng[1] - span * frac, rng[2] + span * frac)
}

condition_palette <- function(conditions) {
  levs <- unique(as.character(conditions))
  cols <- c("#3b6ea8", "#d95f02", "#1b9e77", "#7570b3", "#e7298a", "#66a61e")
  setNames(cols[seq_along(levs)], levs)
}

label_top_points <- function(x, y, labels, rank_metric, n = 5, cex = 0.8) {
  keep <- is.finite(x) & is.finite(y) & nzchar(labels)
  if (!any(keep)) {
    return(invisible(NULL))
  }
  ord <- order(rank_metric[keep], decreasing = FALSE)
  idx <- which(keep)[head(ord, min(n, length(ord)))]
  text(x[idx], y[idx], labels = labels[idx], pos = 3, cex = cex, xpd = NA)
}

write_log("started_at", format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"))
write_log("count_matrix", normalizePath(count_path))
write_log("sample_metadata", normalizePath(metadata_path))
write_log("contrasts", normalizePath(contrasts_path))
write_log("method", method)

counts <- read.delim(count_path, check.names = FALSE)
metadata <- read.delim(metadata_path, check.names = FALSE, stringsAsFactors = FALSE)
contrast_manifest <- read.delim(contrasts_path, check.names = FALSE, stringsAsFactors = FALSE)

sample_cols <- setdiff(colnames(counts), c("gene_id", "gene_name"))
if (!setequal(sample_cols, metadata$sample_id)) {
  stop("count matrix columns and metadata sample_id values do not match")
}
metadata <- metadata[match(sample_cols, metadata$sample_id), ]

expr <- as.matrix(counts[, sample_cols])
mode(expr) <- "numeric"
rownames(expr) <- counts$gene_id
gene_name <- if ("gene_name" %in% colnames(counts)) counts$gene_name else counts$gene_id
is_integer_like <- all(abs(expr - round(expr)) < 1e-8)

condition_counts <- as.data.frame(table(metadata$condition), stringsAsFactors = FALSE)
colnames(condition_counts) <- c("condition", "n_replicates")
contrast_manifest$numerator_replicates <- condition_counts$n_replicates[
  match(contrast_manifest$numerator_condition, condition_counts$condition)
]
contrast_manifest$denominator_replicates <- condition_counts$n_replicates[
  match(contrast_manifest$denominator_condition, condition_counts$condition)
]
contrast_manifest$status <- ifelse(
  contrast_manifest$numerator_replicates >= 2 & contrast_manifest$denominator_replicates >= 2,
  "valid",
  "insufficient_replicates"
)
contrast_manifest$executed <- FALSE
contrast_manifest$execution_method <- NA_character_
contrast_manifest$stub_result <- NA_character_
design_formula <- fit_formula

write.table(metadata, file = file.path(outdir, "manifest", "sample_metadata.aligned.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
write.table(contrast_manifest, file = file.path(outdir, "manifest", "contrast_status.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
write.table(
  data.frame(
    role = c("count_matrix", "sample_metadata", "contrasts"),
    path = c(normalizePath(count_path), normalizePath(metadata_path), normalizePath(contrasts_path))
  ),
  file = file.path(outdir, "manifest", "input_files.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)
write.table(
  data.frame(
    key = c("design_formula", "method", "count_matrix_integer_like"),
    value = c(design_formula, method, is_integer_like)
  ),
  file = file.path(outdir, "config", "method_decision.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

log_expr <- log2(expr + 1)
model_expr <- log_expr
normalization_warning <- NULL
if (input_mode == "raw_counts") {
  write_matrix_artifact(file.path(outdir, "results", "raw_counts.tsv"), expr, counts, gene_name)
} else if (input_mode == "normalized_expression") {
  normalization_warning <- paste(
    "Normalization skipped because input_mode=normalized_expression.",
    "The runner preserved the supplied matrix and generated log2(x+1) only for modeling/QC."
  )
  write_matrix_artifact(file.path(outdir, "results", "input_normalized_expression_matrix.tsv"), expr, counts, gene_name)
} else if (input_mode == "log_expression") {
  normalization_warning <- paste(
    "Normalization and log transformation skipped because input_mode=log_expression.",
    "The runner used the supplied matrix directly for modeling/QC."
  )
  log_expr <- expr
  model_expr <- expr
  write_matrix_artifact(file.path(outdir, "results", "input_log_expression_matrix.tsv"), expr, counts, gene_name)
} else {
  stop(paste("unsupported input_mode:", input_mode))
}
if (!is.null(normalization_warning)) {
  writeLines(normalization_warning, con = file.path(outdir, "qc", "input_mode_warning.txt"))
}
normalized_counts <- expr

if (method == "edgeR") {
  suppressPackageStartupMessages(library(edgeR))
  dge <- DGEList(counts = round(expr), group = metadata$condition)
  dge <- calcNormFactors(dge)
  normalized_counts <- cpm(dge, normalized.lib.sizes = TRUE)
  model_expr <- cpm(dge, log = TRUE, prior.count = 1)
} else if (method == "DESeq2") {
  suppressPackageStartupMessages(library(DESeq2))
  metadata$condition <- factor(metadata$condition)
  dds <- DESeqDataSetFromMatrix(countData = round(expr), colData = metadata, design = as.formula(design_formula))
  dds <- DESeq(dds, quiet = TRUE)
  normalized_counts <- counts(dds, normalized = TRUE)
  model_expr <- assay(vst(dds, blind = TRUE))
}

if (input_mode == "raw_counts") {
  write_matrix_artifact(file.path(outdir, "results", "normalized_expression_matrix.tsv"), normalized_counts, counts, gene_name)
  write_matrix_artifact(file.path(outdir, "results", "log2_expression_matrix.tsv"), model_expr, counts, gene_name)
} else if (input_mode == "normalized_expression") {
  write_matrix_artifact(file.path(outdir, "results", "log2_expression_matrix.tsv"), model_expr, counts, gene_name)
} else {
  write_matrix_artifact(file.path(outdir, "results", "modeling_expression_matrix.tsv"), model_expr, counts, gene_name)
}

lib_sizes <- data.frame(sample_id = sample_cols, library_size = colSums(expr), condition = metadata$condition)
write.table(lib_sizes, file = file.path(outdir, "qc", "library_sizes.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
condition_cols <- condition_palette(metadata$condition)
bar_cols <- unname(condition_cols[as.character(lib_sizes$condition)])
png(file.path(outdir, "qc", "library_sizes.png"), width = 1300, height = 900, res = 160)
par(mar = c(10, 5, 4, 2) + 0.1)
barplot(
  lib_sizes$library_size,
  names.arg = lib_sizes$sample_id,
  las = 2,
  col = bar_cols,
  main = "Library Sizes",
  ylab = "Sum of provided expression values"
)
legend("topright", legend = names(condition_cols), fill = unname(condition_cols), bty = "n")
dev.off()

pca_input <- model_expr[apply(model_expr, 1, var, na.rm = TRUE) > 0, , drop = FALSE]
if (nrow(pca_input) < 2) {
  pca_input <- model_expr
}
pca <- prcomp(t(pca_input), center = TRUE, scale. = FALSE)
pca_df <- data.frame(sample_id = rownames(pca$x), PC1 = pca$x[, 1], PC2 = pca$x[, 2], condition = metadata$condition)
write.table(pca_df, file = file.path(outdir, "qc", "pca_scores.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
pc_var <- (pca$sdev^2 / sum(pca$sdev^2)) * 100
png(file.path(outdir, "qc", "pca.png"), width = 1300, height = 900, res = 160)
par(mar = c(5, 5, 4, 5) + 0.1)
plot(
  pca_df$PC1,
  pca_df$PC2,
  pch = 19,
  col = unname(condition_cols[as.character(pca_df$condition)]),
  xlab = sprintf("PC1 (%.1f%% variance)", pc_var[1]),
  ylab = sprintf("PC2 (%.1f%% variance)", pc_var[2]),
  main = "PCA on modeling expression",
  xlim = pad_range(pca_df$PC1),
  ylim = pad_range(pca_df$PC2)
)
text(pca_df$PC1, pca_df$PC2, labels = pca_df$sample_id, pos = 3, cex = 0.8, xpd = NA)
legend("topright", inset = c(-0.2, 0), legend = names(condition_cols), fill = unname(condition_cols), bty = "n", xpd = NA)
dev.off()

dist_mat <- as.matrix(dist(t(model_expr)))
write.table(
  cbind(sample_id = rownames(dist_mat), as.data.frame(dist_mat, check.names = FALSE)),
  file = file.path(outdir, "qc", "sample_distance.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)
png(file.path(outdir, "qc", "sample_distance_heatmap.png"), width = 1400, height = 1100, res = 170)
heatmap(
  dist_mat,
  symm = TRUE,
  scale = "none",
  margins = c(12, 12),
  cexRow = 0.95,
  cexCol = 0.95,
  col = colorRampPalette(c("#fff7bc", "#fec44f", "#fe9929", "#d95f0e", "#993404"))(256),
  main = "Sample Distance"
)
dev.off()

outlier_mean_distance <- mean_without_self(dist_mat)
outlier_z <- as.numeric(scale(outlier_mean_distance))
if (all(is.na(outlier_z))) {
  outlier_z <- rep(0, length(outlier_mean_distance))
}
sample_outliers <- data.frame(
  sample_id = names(outlier_mean_distance),
  mean_distance = as.numeric(outlier_mean_distance),
  z_score = outlier_z,
  flag_high_distance = outlier_z >= 2
)
write.table(sample_outliers, file = file.path(outdir, "qc", "sample_outlier_metrics.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)

design <- model.matrix(as.formula(design_formula), metadata)
write.table(
  cbind(sample_id = metadata$sample_id, as.data.frame(design, check.names = FALSE)),
  file = file.path(outdir, "qc", "design_matrix.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)
design_rank <- qr(design)$rank
design_full_rank <- design_rank == ncol(design)
design_diagnostics <- data.frame(
  key = c("design_formula", "input_mode", "sample_count", "design_columns", "design_rank", "design_full_rank"),
  value = c(design_formula, input_mode, nrow(metadata), ncol(design), design_rank, design_full_rank)
)
write.table(design_diagnostics, file = file.path(outdir, "qc", "design_diagnostics.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
if ("batch" %in% colnames(metadata)) {
  batch_condition_table <- as.data.frame.matrix(table(metadata$batch, metadata$condition))
  batch_condition_table <- cbind(batch = rownames(batch_condition_table), batch_condition_table)
  rownames(batch_condition_table) <- NULL
  write.table(batch_condition_table, file = file.path(outdir, "qc", "condition_by_batch.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
}
if (!design_full_rank) {
  stop("design matrix is rank deficient; see qc/design_diagnostics.tsv and qc/condition_by_batch.tsv")
}

valid_contrasts <- contrast_manifest[contrast_manifest$status == "valid", , drop = FALSE]
blocked_contrasts <- contrast_manifest[contrast_manifest$status != "valid", , drop = FALSE]

warnings_df <- data.frame(severity = character(), message = character(), stringsAsFactors = FALSE)
if (nrow(valid_contrasts) == 0) {
  warnings_df <- rbind(warnings_df, data.frame(severity = "error", message = "No contrasts were executable after replicate checks.", stringsAsFactors = FALSE))
}
if (nrow(blocked_contrasts) > 0) {
  warnings_df <- rbind(warnings_df, data.frame(severity = "warn", message = sprintf("%d contrast(s) were blocked due to insufficient biological replication.", nrow(blocked_contrasts)), stringsAsFactors = FALSE))
}
if (any(valid_contrasts$numerator_replicates == 2 & valid_contrasts$denominator_replicates == 2)) {
  warnings_df <- rbind(warnings_df, data.frame(severity = "warn", message = "At least one executed contrast is minimally powered (2 vs 2 replicates); interpret effect sizes and p-values as exploratory.", stringsAsFactors = FALSE))
}
if (input_mode != "raw_counts") {
  warnings_df <- rbind(warnings_df, data.frame(severity = "warn", message = sprintf("Input mode is %s; normalization and/or transformation was preserved from the supplied matrix rather than re-derived from raw counts.", input_mode), stringsAsFactors = FALSE))
}
write.table(warnings_df, file = file.path(outdir, "qc", "statistical_warnings.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
write.table(
  data.frame(
    key = c("sample_count", "gene_count", "valid_contrasts", "blocked_contrasts", "minimal_replicate_contrasts"),
    value = c(nrow(metadata), nrow(counts), nrow(valid_contrasts), nrow(blocked_contrasts), sum(valid_contrasts$numerator_replicates == 2 & valid_contrasts$denominator_replicates == 2))
  ),
  file = file.path(outdir, "qc", "statistical_summary.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)
if (nrow(blocked_contrasts) > 0) {
  for (i in seq_len(nrow(blocked_contrasts))) {
    out_name <- safe_name(blocked_contrasts$contrast[i])
    stub_path <- file.path(outdir, "results", paste0(out_name, ".not_tested.tsv"))
    stub <- data.frame(
      contrast = blocked_contrasts$contrast[i],
      status = blocked_contrasts$status[i],
      reason = "Insufficient biological replication for at least one condition",
      numerator_condition = blocked_contrasts$numerator_condition[i],
      denominator_condition = blocked_contrasts$denominator_condition[i],
      numerator_replicates = blocked_contrasts$numerator_replicates[i],
      denominator_replicates = blocked_contrasts$denominator_replicates[i],
      input_mode = input_mode,
      fit_formula = design_formula
    )
    write.table(stub, file = stub_path, sep = "\t", quote = FALSE, row.names = FALSE)
    contrast_manifest$stub_result[contrast_manifest$contrast == blocked_contrasts$contrast[i]] <- basename(stub_path)
  }
}
if (nrow(valid_contrasts) > 0) {
  metadata$condition <- factor(metadata$condition)
  if (method == "limma_log2") {
    fit <- lmFit(model_expr, design)
    contrast_defs <- setNames(
      paste0("condition", valid_contrasts$numerator_condition, " - condition", valid_contrasts$denominator_condition),
      valid_contrasts$contrast
    )
    contrast_matrix <- makeContrasts(contrasts = unname(contrast_defs), levels = design)
    colnames(contrast_matrix) <- names(contrast_defs)
    fit2 <- eBayes(contrasts.fit(fit, contrast_matrix), trend = TRUE, robust = TRUE)
    png(file.path(outdir, "qc", "mean_variance_trend.png"), width = 1000, height = 850, res = 150)
    plotSA(fit2, main = "Mean-variance trend")
    dev.off()
    for (contrast_name in colnames(contrast_matrix)) {
      table <- topTable(fit2, coef = contrast_name, number = Inf, sort.by = "P")
      table$gene_id <- rownames(table)
      table$gene_name <- gene_name[match(rownames(table), counts$gene_id)]
      table <- table[, c("gene_id", "gene_name", "logFC", "AveExpr", "t", "P.Value", "adj.P.Val", "B")]
      out_name <- safe_name(contrast_name)
      write.table(table, file = file.path(outdir, "results", paste0(out_name, ".tsv")), sep = "\t", quote = FALSE, row.names = FALSE)
      sig <- !is.na(table$adj.P.Val) & table$adj.P.Val < 0.05
      png(file.path(outdir, "plots", paste0(out_name, "_volcano.png")), width = 1200, height = 900, res = 160)
      par(mar = c(5, 5, 4, 2) + 0.1)
      plot(
        table$logFC,
        -log10(table$P.Value),
        pch = 19,
        cex = 0.7,
        col = ifelse(sig, "#b22222", "#444444"),
        xlab = "log2 fold-change",
        ylab = "-log10(P)",
        main = paste("Volcano:", contrast_name),
        xlim = pad_range(table$logFC),
        ylim = pad_range(-log10(table$P.Value))
      )
      abline(h = -log10(0.05), lty = 2, col = "#1f78b4")
      abline(v = c(-1, 1), lty = 3, col = "#9e9e9e")
      label_top_points(table$logFC, -log10(table$P.Value), table$gene_name, table$adj.P.Val, n = 6)
      dev.off()
      png(file.path(outdir, "plots", paste0(out_name, "_ma.png")), width = 1200, height = 900, res = 160)
      par(mar = c(5, 5, 4, 2) + 0.1)
      plot(
        table$AveExpr,
        table$logFC,
        pch = 19,
        cex = 0.7,
        col = ifelse(sig, "#b22222", "#444444"),
        xlab = "Average expression",
        ylab = "log2 fold-change",
        main = paste("MA:", contrast_name),
        xlim = pad_range(table$AveExpr),
        ylim = pad_range(table$logFC)
      )
      abline(h = 0, col = "red")
      label_top_points(table$AveExpr, table$logFC, table$gene_name, table$adj.P.Val, n = 6)
      dev.off()
      contrast_manifest$executed[contrast_manifest$contrast == contrast_name] <- TRUE
      contrast_manifest$execution_method[contrast_manifest$contrast == contrast_name] <- method
    }
  } else if (method == "edgeR") {
    dge <- DGEList(counts = round(expr), group = metadata$condition)
    dge <- calcNormFactors(dge)
    dge <- estimateDisp(dge, design)
    fit <- glmQLFit(dge, design)
    png(file.path(outdir, "qc", "mean_variance_trend.png"), width = 1000, height = 850, res = 150)
    plotBCV(dge, main = "edgeR mean-variance trend")
    dev.off()
    for (i in seq_len(nrow(valid_contrasts))) {
      contrast_name <- valid_contrasts$contrast[i]
      contrast_vec <- rep(0, ncol(design))
      names(contrast_vec) <- colnames(design)
      contrast_vec[paste0("condition", valid_contrasts$numerator_condition[i])] <- 1
      contrast_vec[paste0("condition", valid_contrasts$denominator_condition[i])] <- -1
      qlf <- glmQLFTest(fit, contrast = contrast_vec)
      table <- topTags(qlf, n = Inf)$table
      table$gene_id <- rownames(table)
      table$gene_name <- gene_name[match(rownames(table), counts$gene_id)]
      out_name <- safe_name(contrast_name)
      write.table(table, file = file.path(outdir, "results", paste0(out_name, ".tsv")), sep = "\t", quote = FALSE, row.names = FALSE)
      contrast_manifest$executed[contrast_manifest$contrast == contrast_name] <- TRUE
      contrast_manifest$execution_method[contrast_manifest$contrast == contrast_name] <- method
    }
  } else if (method == "DESeq2") {
    png(file.path(outdir, "qc", "mean_variance_trend.png"), width = 1000, height = 850, res = 150)
    plotDispEsts(dds, main = "DESeq2 dispersion estimates")
    dev.off()
    for (i in seq_len(nrow(valid_contrasts))) {
      contrast_name <- valid_contrasts$contrast[i]
      res <- results(dds, contrast = c("condition", valid_contrasts$numerator_condition[i], valid_contrasts$denominator_condition[i]))
      table <- as.data.frame(res)
      table$gene_id <- rownames(table)
      table$gene_name <- gene_name[match(rownames(table), counts$gene_id)]
      out_name <- safe_name(contrast_name)
      write.table(table, file = file.path(outdir, "results", paste0(out_name, ".tsv")), sep = "\t", quote = FALSE, row.names = FALSE)
      contrast_manifest$executed[contrast_manifest$contrast == contrast_name] <- TRUE
      contrast_manifest$execution_method[contrast_manifest$contrast == contrast_name] <- method
    }
  }
}

write.table(contrast_manifest, file = file.path(outdir, "manifest", "contrast_status.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
writeLines(capture.output(sessionInfo()), con = file.path(outdir, "versions", "sessionInfo.txt"))

summary_lines <- c(
  paste("Design formula:", design_formula),
  paste("Selected method:", method),
  paste("Input mode:", input_mode),
  "",
  "Replicates by condition:"
)
summary_lines <- c(summary_lines, apply(condition_counts, 1, function(x) paste(" -", x[["condition"]], ":", x[["n_replicates"]])))
summary_lines <- c(summary_lines, "", "Contrast status:")
summary_lines <- c(summary_lines, apply(contrast_manifest, 1, function(x) paste(" -", x[["contrast"]], ":", x[["status"]], "| executed:", x[["executed"]])))
if (!is.null(normalization_warning)) {
  summary_lines <- c(summary_lines, "", "Warnings:", paste(" -", normalization_warning))
}
writeLines(summary_lines, con = file.path(outdir, "summary.md"))

write_log("finished_at", format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"))
