from pathlib import Path

from snakemake_staging.utils import package_data


def snakefile() -> Path:
    return package_data("workflow", "Snakefile")
