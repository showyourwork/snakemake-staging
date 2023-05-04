from tests.runner import run


def test_zenodo_snapshot():
    run("tests/projects/zenodo-snapshot", "staging/stages/stage.snapshot")


# def test_zenodo_restore():
#     run(
#         "tests/projects/zenodo-restore",
#         "output/a.txt",
#         "--configfile",
#         "config.yaml",
#     )
