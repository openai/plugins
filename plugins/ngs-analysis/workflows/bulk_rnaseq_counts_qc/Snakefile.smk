"""Plugin-owned local-light bulk RNA-seq counts/QC workflow."""

import shlex


FASTQ_FILES = config.get("fastq_files", {})
RNASEQ_SALMON = config.get("rnaseq_salmon_samples", {})
REFERENCES = config.get("references", {})
SALMON_CONFIG = config.get("salmon", {})
THREADS = int(config.get("threads", 4))


def _shell_join(paths):
    return " ".join(shlex.quote(path) for path in paths)


rule all:
    input:
        "fastqc/multiqc/multiqc_report.html",
        "rnaseq_salmon/multiqc/multiqc_report.html",
        "rnaseq_salmon/matrices/tpm.tsv",
        "rnaseq_salmon/matrices/num_reads.tsv",
        "rnaseq_salmon/matrices/effective_length.tsv",
        "rnaseq_salmon/matrices/samples.tsv"


rule fastqc_raw:
    input:
        lambda wildcards: FASTQ_FILES[wildcards.unit]["path"]
    output:
        touch("fastqc/raw/{unit}.done")
    threads: THREADS
    shell:
        "mkdir -p fastqc/raw && fastqc -t {threads} -o fastqc/raw {input:q}"


rule multiqc_fastq:
    input:
        expand("fastqc/raw/{unit}.done", unit=FASTQ_FILES.keys())
    output:
        "fastqc/multiqc/multiqc_report.html"
    shell:
        "mkdir -p fastqc/multiqc && multiqc --no-version-check fastqc/raw -o fastqc/multiqc"


rule salmon_index:
    input:
        transcriptome=lambda wildcards: REFERENCES["transcriptome_fasta"]
    output:
        directory("rnaseq_salmon/index")
    params:
        kmer=lambda wildcards: int(SALMON_CONFIG.get("kmer", 31))
    shell:
        "salmon --no-version-check index -t {input.transcriptome:q} -i {output:q} -k {params.kmer}"


rule salmon_quant:
    input:
        index="rnaseq_salmon/index"
    output:
        "rnaseq_salmon/quant/{sample}/quant.sf"
    threads: THREADS
    params:
        layout=lambda wildcards: RNASEQ_SALMON[wildcards.sample]["layout"],
        libtype=lambda wildcards: RNASEQ_SALMON[wildcards.sample]["salmon_libtype"],
        r1=lambda wildcards: _shell_join(RNASEQ_SALMON[wildcards.sample]["r1"]),
        r2=lambda wildcards: _shell_join(RNASEQ_SALMON[wildcards.sample].get("r2", [])),
        outdir=lambda wildcards: f"rnaseq_salmon/quant/{wildcards.sample}",
    shell:
        r"""
        if [ "{params.layout}" = "PE" ]; then
          salmon --no-version-check quant -i {input.index} -l {params.libtype} \
            -1 {params.r1} -2 {params.r2} \
            -p {threads} --validateMappings -o {params.outdir}
        else
          salmon --no-version-check quant -i {input.index} -l {params.libtype} \
            -r {params.r1} \
            -p {threads} --validateMappings -o {params.outdir}
        fi
        """


rule multiqc_salmon:
    input:
        expand("rnaseq_salmon/quant/{sample}/quant.sf", sample=RNASEQ_SALMON.keys())
    output:
        "rnaseq_salmon/multiqc/multiqc_report.html"
    shell:
        "mkdir -p rnaseq_salmon/multiqc && multiqc --no-version-check rnaseq_salmon/quant -o rnaseq_salmon/multiqc"


rule salmon_aggregate:
    input:
        expand("rnaseq_salmon/quant/{sample}/quant.sf", sample=RNASEQ_SALMON.keys()),
        config_path="config.json"
    output:
        tpm="rnaseq_salmon/matrices/tpm.tsv",
        num_reads="rnaseq_salmon/matrices/num_reads.tsv",
        effective_length="rnaseq_salmon/matrices/effective_length.tsv",
        samples="rnaseq_salmon/matrices/samples.tsv"
    params:
        quant_args=lambda wildcards: " ".join(
            f"--quant {sample}=rnaseq_salmon/quant/{sample}/quant.sf" for sample in sorted(RNASEQ_SALMON.keys())
        )
    shell:
        "mkdir -p rnaseq_salmon/matrices && "
        "python workflow/scripts/aggregate_salmon_quant.py "
        "--config {input.config_path} "
        "--outdir rnaseq_salmon/matrices "
        "{params.quant_args}"
