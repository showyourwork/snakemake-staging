from pathlib import Path
from snakemake_staging import stages, utils

previously_included = set()
for name, stage in stages.STAGES.items():
    # Custom rules for uploading and downloading this type of stage
    snakefile = stage.snakefile()
    if snakefile not in previously_included:
        include: snakefile
        previously_included.add(snakefile)
