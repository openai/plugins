#!/usr/bin/env Rscript

parse_args <- function(argv) {
  args <- list(
    outdir = ".",
    threads = 1,
    trunc_len_f = 0,
    trunc_len_r = 0,
    taxonomy_classifier = ""
  )
  i <- 1
  while (i <= length(argv)) {
    key <- argv[[i]]
    if (!startsWith(key, "--")) {
      stop(sprintf("unexpected argument: %s", key))
    }
    name <- gsub("-", "_", substring(key, 3), fixed = TRUE)
    if (i == length(argv)) {
      stop(sprintf("missing value for %s", key))
    }
    args[[name]] <- argv[[i + 1]]
    i <- i + 2
  }
  required <- c("sample_sheet", "primer_forward", "primer_reverse")
  missing <- required[!nzchar(vapply(required, function(name) args[[name]] %||% "", character(1)))]
  if (length(missing)) {
    stop(sprintf("missing required argument(s): %s", paste(missing, collapse = ", ")))
  }
  args$threads <- as.integer(args$threads)
  args$trunc_len_f <- as.integer(args$trunc_len_f)
  args$trunc_len_r <- as.integer(args$trunc_len_r)
  args
}

`%||%` <- function(left, right) {
  if (is.null(left)) {
    right
  } else {
    left
  }
}

detect_sep <- function(path) {
  if (grepl("\\.(tsv|tab)$", path, ignore.case = TRUE)) "\t" else ","
}

resolve_path <- function(raw, base_dir) {
  if (is.na(raw) || !nzchar(raw)) {
    return("")
  }
  raw <- path.expand(raw)
  if (startsWith(raw, "/")) {
    return(normalizePath(raw, mustWork = FALSE))
  }
  normalizePath(file.path(base_dir, raw), mustWork = FALSE)
}

count_fastq <- function(path) {
  con <- if (grepl("\\.gz$", path, ignore.case = TRUE)) gzfile(path, "rt") else file(path, "rt")
  on.exit(close(con), add = TRUE)
  lines <- 0
  repeat {
    chunk <- readLines(con, n = 400000, warn = FALSE)
    if (!length(chunk)) {
      break
    }
    lines <- lines + length(chunk)
  }
  as.integer(lines / 4)
}

as_sample_sheet <- function(path) {
  table <- read.table(path, sep = detect_sep(path), header = TRUE, stringsAsFactors = FALSE, check.names = FALSE, quote = "", comment.char = "")
  names(table) <- trimws(names(table))
  lower_names <- tolower(names(table))
  sample_col <- match(TRUE, lower_names %in% tolower(c("sample", "sample_id", "sampleID")))
  r1_col <- match(TRUE, lower_names %in% tolower(c("r1", "fastq_1", "forwardReads", "read1")))
  r2_col <- match(TRUE, lower_names %in% tolower(c("r2", "fastq_2", "reverseReads", "read2")))
  if (is.na(sample_col) || is.na(r1_col)) {
    stop("sample sheet must contain sample/sample_id/sampleID and r1/fastq_1/forwardReads columns")
  }
  base_dir <- dirname(normalizePath(path, mustWork = TRUE))
  data.frame(
    sample = make.names(table[[sample_col]], unique = TRUE),
    r1 = vapply(table[[r1_col]], resolve_path, character(1), base_dir = base_dir),
    r2 = if (is.na(r2_col)) "" else vapply(table[[r2_col]], resolve_path, character(1), base_dir = base_dir),
    stringsAsFactors = FALSE
  )
}

write_table <- function(path, table) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  write.table(table, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "")
}

write_fasta <- function(path, ids, sequences) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  con <- file(path, "wt")
  on.exit(close(con), add = TRUE)
  for (i in seq_along(ids)) {
    writeLines(sprintf(">%s", ids[[i]]), con)
    writeLines(gsub("(.{1,80})", "\\1\n", sequences[[i]], perl = TRUE), con)
  }
}

taxonomy_to_table <- function(taxa, ids) {
  ranks <- as.data.frame(taxa, stringsAsFactors = FALSE)
  ranks[is.na(ranks)] <- ""
  ranks$taxonomy <- apply(ranks, 1, function(row) paste(row[nzchar(row)], collapse = ";"))
  data.frame(feature_id = ids, ranks, stringsAsFactors = FALSE, check.names = FALSE)
}

if (!requireNamespace("dada2", quietly = TRUE)) {
  stop("R package 'dada2' is required. Install with mamba install -c conda-forge -c bioconda bioconductor-dada2.")
}

args <- parse_args(commandArgs(trailingOnly = TRUE))
outdir <- normalizePath(args$outdir, mustWork = FALSE)
samples <- as_sample_sheet(args$sample_sheet)
paired <- any(nzchar(samples$r2))

if (paired && any(!nzchar(samples$r2))) {
  stop("paired DADA2 run requires r2/fastq_2 for every sample")
}

dir.create(file.path(outdir, "dada2", "filtered"), recursive = TRUE, showWarnings = FALSE)
dir.create(file.path(outdir, "tables"), recursive = TRUE, showWarnings = FALSE)
dir.create(file.path(outdir, "logs"), recursive = TRUE, showWarnings = FALSE)

fnFs <- samples$r1
filtFs <- file.path(outdir, "dada2", "filtered", paste0(samples$sample, "_F_filt.fastq.gz"))
names(fnFs) <- samples$sample
names(filtFs) <- samples$sample

if (paired) {
  fnRs <- samples$r2
  filtRs <- file.path(outdir, "dada2", "filtered", paste0(samples$sample, "_R_filt.fastq.gz"))
  names(fnRs) <- samples$sample
  names(filtRs) <- samples$sample
  trunc_len <- c(args$trunc_len_f, args$trunc_len_r)
  filtered <- dada2::filterAndTrim(
    fnFs,
    filtFs,
    fnRs,
    filtRs,
    truncLen = trunc_len,
    maxN = 0,
    maxEE = c(2, 2),
    truncQ = 2,
    rm.phix = TRUE,
    compress = TRUE,
    multithread = args$threads
  )
  errF <- dada2::learnErrors(filtFs, multithread = args$threads)
  errR <- dada2::learnErrors(filtRs, multithread = args$threads)
  dadaFs <- dada2::dada(filtFs, err = errF, multithread = args$threads)
  dadaRs <- dada2::dada(filtRs, err = errR, multithread = args$threads)
  mergers <- dada2::mergePairs(dadaFs, filtFs, dadaRs, filtRs)
  seqtab <- dada2::makeSequenceTable(mergers)
  denoised <- vapply(dadaFs, dada2::getN, integer(1))
  merged <- vapply(mergers, dada2::getN, integer(1))
} else {
  filtered <- dada2::filterAndTrim(
    fnFs,
    filtFs,
    truncLen = args$trunc_len_f,
    maxN = 0,
    maxEE = 2,
    truncQ = 2,
    rm.phix = TRUE,
    compress = TRUE,
    multithread = args$threads
  )
  errF <- dada2::learnErrors(filtFs, multithread = args$threads)
  dadaFs <- dada2::dada(filtFs, err = errF, multithread = args$threads)
  seqtab <- dada2::makeSequenceTable(dadaFs)
  denoised <- vapply(dadaFs, dada2::getN, integer(1))
  merged <- denoised
}

seqtab_nochim <- dada2::removeBimeraDenovo(seqtab, method = "consensus", multithread = args$threads)
sequences <- colnames(seqtab_nochim)
asv_ids <- paste0("ASV", seq_along(sequences))
colnames(seqtab_nochim) <- asv_ids

asv_table <- data.frame(feature_id = asv_ids, t(seqtab_nochim), check.names = FALSE)
write_table(file.path(outdir, "tables", "asv_table.tsv"), asv_table)
write_fasta(file.path(outdir, "tables", "representative_sequences.fasta"), asv_ids, sequences)

filtered_out <- if (is.null(dim(filtered))) filtered else filtered[, "reads.out"]
retention <- data.frame(
  sample = samples$sample,
  input = vapply(fnFs, count_fastq, integer(1)),
  filtered = as.integer(filtered_out),
  denoised = as.integer(denoised[samples$sample]),
  merged = as.integer(merged[samples$sample]),
  nonchim = as.integer(rowSums(seqtab_nochim)[samples$sample]),
  stringsAsFactors = FALSE
)
write_table(file.path(outdir, "tables", "read_retention.tsv"), retention)

if (nzchar(args$taxonomy_classifier)) {
  classifier <- normalizePath(args$taxonomy_classifier, mustWork = TRUE)
  if (grepl("\\.qza$", classifier, ignore.case = TRUE)) {
    writeLines("DADA2 backend skipped taxonomy assignment because .qza classifiers are QIIME2 artifacts.", file.path(outdir, "logs", "dada2_taxonomy_skipped.txt"))
  } else {
    taxa <- dada2::assignTaxonomy(seqtab_nochim, classifier, multithread = args$threads)
    write_table(file.path(outdir, "tables", "taxonomy.tsv"), taxonomy_to_table(taxa, asv_ids))
  }
}

saveRDS(
  list(
    samples = samples,
    sequence_table = seqtab_nochim,
    retention = retention,
    primer_forward = args$primer_forward,
    primer_reverse = args$primer_reverse
  ),
  file.path(outdir, "dada2", "dada2_backend_state.rds")
)

writeLines("DADA2 backend completed", file.path(outdir, "logs", "dada2_backend_status.txt"))
