import gzip
import os
import shutil
import subprocess
from pathlib import Path

execution = snakemake.config.get("execution", {})
star_runner = execution.get("star_runner", "native")
star_image = execution.get(
    "star_image",
    "josousa/star@sha256:2683d370b9c91a2e497d776d9b0dff2ddcc01dfec5029103ffa66b2a8da7b0c2",
)


def materialize_fastq(source_path: str, output_dir: Path) -> str:
    source = Path(source_path).resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    if source.suffix != ".gz":
        return str(source)
    destination = (output_dir / source.stem).resolve()
    with gzip.open(source, "rb") as input_handle, destination.open("wb") as output_handle:
        shutil.copyfileobj(input_handle, output_handle)
    return str(destination)


sample_dir = Path(str(snakemake.output.log)).resolve().parent
sample_dir.mkdir(parents=True, exist_ok=True)
if star_runner == "docker":
    run_root = sample_dir.parents[1]
    cdna_fastq = Path(str(snakemake.input.cdna_fastq)).resolve()
    barcode_fastq = Path(str(snakemake.input.barcode_fastq)).resolve()
    whitelist = Path(str(snakemake.input.whitelist)).resolve()
    read_files_command = "zcat" if cdna_fastq.suffix == ".gz" else "cat"
    cmd = [
        "docker",
        "run",
        "--rm",
        "--platform",
        "linux/amd64",
        "-u",
        f"{os.getuid()}:{os.getgid()}",
        "-w",
        "/work",
        "-v",
        f"{run_root}:/work",
        "-v",
        f"{cdna_fastq.parent}:/cdna_ro:ro",
        "-v",
        f"{barcode_fastq.parent}:/barcode_ro:ro",
        "-v",
        f"{whitelist.parent}:/wl_ro:ro",
        star_image,
        "STAR",
        "--genomeDir",
        f"/work/{Path(str(snakemake.input.index)).resolve().relative_to(run_root)}",
        "--runThreadN",
        str(snakemake.threads),
        "--readFilesIn",
        f"/cdna_ro/{cdna_fastq.name}",
        f"/barcode_ro/{barcode_fastq.name}",
        "--readFilesCommand",
        read_files_command,
        "--outFileNamePrefix",
        f"/work/{sample_dir.relative_to(run_root)}/",
        "--soloType",
        str(snakemake.params.solo_type),
        "--soloCBwhitelist",
        f"/wl_ro/{whitelist.name}",
        "--soloCBstart",
        str(snakemake.params.cb_start),
        "--soloCBlen",
        str(snakemake.params.cb_len),
        "--soloUMIstart",
        str(snakemake.params.umi_start),
        "--soloUMIlen",
        str(snakemake.params.umi_len),
        "--soloBarcodeReadLength",
        "0",
        "--soloFeatures",
        str(snakemake.params.features_mode),
        "--soloCellFilter",
        *str(snakemake.params.solo_cell_filter).split(),
        "--outSAMtype",
        "None",
    ]
else:
    scratch_dir = sample_dir / "_inputs"
    cdna_input = materialize_fastq(str(snakemake.input.cdna_fastq), scratch_dir / "cdna")
    barcode_input = materialize_fastq(str(snakemake.input.barcode_fastq), scratch_dir / "barcode")
    cmd = [
        "STAR",
        "--genomeDir",
        str(Path(str(snakemake.input.index)).resolve()),
        "--runThreadN",
        str(snakemake.threads),
        "--readFilesIn",
        cdna_input,
        barcode_input,
        "--outFileNamePrefix",
        str(sample_dir) + "/",
        "--soloType",
        str(snakemake.params.solo_type),
        "--soloCBwhitelist",
        str(Path(str(snakemake.input.whitelist)).resolve()),
        "--soloCBstart",
        str(snakemake.params.cb_start),
        "--soloCBlen",
        str(snakemake.params.cb_len),
        "--soloUMIstart",
        str(snakemake.params.umi_start),
        "--soloUMIlen",
        str(snakemake.params.umi_len),
        "--soloBarcodeReadLength",
        "0",
        "--soloFeatures",
        str(snakemake.params.features_mode),
        "--soloCellFilter",
        *str(snakemake.params.solo_cell_filter).split(),
        "--outSAMtype",
        "None",
    ]

subprocess.run(cmd, check=True)
