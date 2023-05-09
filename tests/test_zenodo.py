import os

import pytest
from snakemake_testing import run_snakemake

from tests.zenodo_mock import ZenodoMock


@pytest.fixture(scope="session")
def server():
    server = ZenodoMock()
    server.start()
    yield server
    server.stop()


def test_zenodo_snapshot(server):
    run_snakemake(
        "tests/projects/zenodo-snapshot",
        "staging__upload",
        "--config",
        f"zenodo_mock_url={server.url}/api",
        env=dict(os.environ, ZENODO_TOKEN="test"),
    )


def test_zenodo_restore():
    run_snakemake(
        "tests/projects/zenodo-restore",
        "output/a.txt",
        "--config",
        "restore=True",
    )
