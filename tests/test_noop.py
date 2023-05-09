from tests.runner import run


def test_noop_snapshot():
    run("tests/projects/noop-snapshot", "staging__upload")


def test_noop_restore():
    run(
        "tests/projects/noop-restore",
        "output/a.txt",
        "--config",
        "restore=True",
    )
