import os
import subprocess
from pathlib import Path

execution = snakemake.config.get("execution", {})
star_runner = execution.get("star_runner", "native")
star_image = execution.get(
    "star_image",
    "josousa/star@sha256:2683d370b9c91a2e497d776d9b0dff2ddcc01dfec5029103ffa66b2a8da7b0c2",
)

output_dir = Path(str(snakemake.output[0])).resolve()
output_dir.mkdir(parents=True, exist_ok=True)

if star_runner == "docker":
    run_root = output_dir.parents[1]
    fasta = Path(str(snakemake.input.fasta)).resolve()
    gtf = Path(str(snakemake.input.gtf)).resolve()
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
        f"{fasta.parent}:/fasta_ro:ro",
        "-v",
        f"{gtf.parent}:/gtf_ro:ro",
        star_image,
        "STAR",
        "--runThreadN",
        str(snakemake.threads),
        "--runMode",
        "genomeGenerate",
        "--genomeDir",
        f"/work/{output_dir.relative_to(run_root)}",
        "--genomeFastaFiles",
        f"/fasta_ro/{fasta.name}",
        "--sjdbGTFfile",
        f"/gtf_ro/{gtf.name}",
        "--sjdbOverhang",
        str(snakemake.params.sjdb_overhang),
    ]
else:
    cmd = [
        "STAR",
        "--runThreadN",
        str(snakemake.threads),
        "--runMode",
        "genomeGenerate",
        "--genomeDir",
        str(output_dir),
        "--genomeFastaFiles",
        str(Path(str(snakemake.input.fasta)).resolve()),
        "--sjdbGTFfile",
        str(Path(str(snakemake.input.gtf)).resolve()),
        "--sjdbOverhang",
        str(snakemake.params.sjdb_overhang),
    ]

subprocess.run(cmd, check=True)
