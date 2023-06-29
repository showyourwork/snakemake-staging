from snakemake_staging.testing import run_snakemake


def test_config_args():
    run_snakemake(
        "tests/projects/config",
        "staging2/stage.upload",
        "-s",
        "Snakefile_args",
        "--config",
        "working_directory=staging2",
    )


def test_config_kwargs():
    run_snakemake(
        "tests/projects/config",
        "staging2/stage.upload",
        "-s",
        "Snakefile_kwargs",
        "--config",
        "working_directory=staging2",
    )
