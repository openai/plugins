"""Plugin-owned local scRNA FASTQ-to-count workflow."""

SAMPLES = config["samples"]
REFS = config["references"]
CHEM = config["chemistry"]
THREADS = int(config.get("threads", 4))


def count_targets():
    targets = ["references/star_index"]
    for sample in SAMPLES:
        base = f"counts/{sample}/Solo.out/Gene/raw"
        targets.extend(
            [
                f"{base}/matrix.mtx",
                f"{base}/barcodes.tsv",
                f"{base}/features.tsv",
                f"counts/{sample}/Log.final.out",
            ]
        )
    return targets


rule all:
    input:
        count_targets()


rule starsolo_index:
    input:
        fasta=lambda wildcards: REFS["genome_fasta"],
        gtf=lambda wildcards: REFS["annotation_gtf"],
    output:
        directory("references/star_index")
    threads: THREADS
    params:
        sjdb_overhang=lambda wildcards: int(CHEM.get("sjdb_overhang", 99))
    script:
        "run_star_genome_generate.py"


rule starsolo_count:
    input:
        index="references/star_index",
        whitelist=lambda wildcards: REFS["cb_whitelist"],
        barcode_fastq=lambda wildcards: SAMPLES[wildcards.sample]["barcode_fastq"],
        cdna_fastq=lambda wildcards: SAMPLES[wildcards.sample]["cdna_fastq"],
    output:
        matrix="counts/{sample}/Solo.out/Gene/raw/matrix.mtx",
        barcodes="counts/{sample}/Solo.out/Gene/raw/barcodes.tsv",
        features="counts/{sample}/Solo.out/Gene/raw/features.tsv",
        log="counts/{sample}/Log.final.out",
    threads: THREADS
    params:
        cb_start=lambda wildcards: int(CHEM.get("cb_start", 1)),
        cb_len=lambda wildcards: int(CHEM.get("cb_len", 16)),
        umi_start=lambda wildcards: int(CHEM.get("umi_start", 17)),
        umi_len=lambda wildcards: int(CHEM.get("umi_len", 10)),
        solo_type=lambda wildcards: CHEM.get("solo_type", "CB_UMI_Simple"),
        solo_cell_filter=lambda wildcards: CHEM.get("solo_cell_filter", "CellRanger2.2 3000 0.99 10"),
        features_mode=lambda wildcards: CHEM.get("features_mode", "Gene"),
    script:
        "run_starsolo.py"
