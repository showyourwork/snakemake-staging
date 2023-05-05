from tests.runner import run


def test_config_args():
    run(
        "tests/projects/config",
        "staging2/stage.upload",
        "-s",
        "Snakefile_args",
        "--config",
        "working_directory=staging2",
    )


def test_config_kwargs():
    run(
        "tests/projects/config",
        "staging2/stage.upload",
        "-s",
        "Snakefile_kwargs",
        "--config",
        "working_directory=staging2",
    )
