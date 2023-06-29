from snakemake_staging.testing import run_snakemake


def test_noop_snapshot():
    run_snakemake("tests/projects/noop-snapshot", "staging__upload")


def test_noop_restore():
    run_snakemake(
        "tests/projects/noop-restore",
        "output/a.txt",
        "--config",
        "restore=True",
    )
