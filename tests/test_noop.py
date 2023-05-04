from tests.runner import run


def test_noop_snapshot():
    run("tests/projects/noop-snapshot", "staging/stages/stage.snapshot")


def test_noop_restore():
    run(
        "tests/projects/noop-restore",
        "output/a.txt",
        "--configfile",
        "config.yaml",
    )
