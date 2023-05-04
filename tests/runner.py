import difflib
import hashlib
import os
import platform
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Generator, Iterable, List, Optional

from snakemake_staging.utils import PathLike

# We put all the conda environments in a single directory so that we can reuse
# them between tests
conda_prefix = str(Path().resolve() / ".test" / "conda")


@contextmanager
def cwd(path: PathLike) -> Generator[None, None, None]:
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


@contextmanager
def temporary_directory(
    path: PathLike, args: Iterable[str] = ()
) -> Generator[Path, None, None]:
    # Snakemake fails when creating conda environments on Windows when executed
    # within a TemporaryDirectory so we wrap it here with a custom
    # implementation on Windows.
    if platform.system() == "Windows":
        m = hashlib.sha1()
        m.update(str(path).encode())
        for arg in args:
            m.update(arg.encode())

        tempdir = Path().resolve() / ".test" / "tmp" / m.hexdigest()
        tempdir.mkdir(parents=True, exist_ok=True)
        try:
            yield tempdir
        finally:
            shutil.rmtree(tempdir)

    else:
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)


def run(
    path: PathLike,
    *args: Any,
    **kwargs: Any,
) -> None:
    with run_context(path, *args, **kwargs):
        pass


@contextmanager
def run_context(
    path: PathLike,
    *snakemake_args: str,
    check_exists: bool = True,
    check_contents: bool = True,
    conda_frontend: Optional[str] = "mamba",
    expected_dirname: PathLike = "expected",
) -> Generator[Path, None, None]:
    test_project_root = Path(path).resolve()

    # Helper function for ignoring the "expected" directory
    def ignore_expected(_: str, names: List[str]) -> List[str]:
        return [name for name in names if Path(name).parts[0].startswith("expected")]

    # Copy the test project over to a temporary directory
    with temporary_directory(path, snakemake_args) as tmpdir:
        shutil.copytree(
            test_project_root, tmpdir, ignore=ignore_expected, dirs_exist_ok=True
        )
        with cwd(tmpdir):
            run_snakemake(*snakemake_args, conda_frontend=conda_frontend, cwd=tmpdir)

        expected_dir = test_project_root / expected_dirname
        if (check_exists or check_contents) and expected_dir.is_dir():
            diffs = []
            for expected in expected_dir.glob("**/*"):
                # We don't check directories, only files. We can revisit this if
                # necessary.
                if expected.is_dir():
                    continue

                # Construct the path to the expected file in the temporary directory
                subpath = expected.relative_to(test_project_root / expected_dirname)
                observed = tmpdir / subpath

                # Files with the suffix ".exists" are just used to check that
                # the file gets created
                if expected.suffix == ".exists":
                    if not observed.with_suffix("").is_file():
                        raise ValueError(f"{subpath.with_suffix('')} doesn't exist")
                    continue

                if not observed.is_file():
                    if check_exists:
                        raise ValueError(f"{subpath} doesn't exist or is not a file")
                    else:
                        # If we don't care about existence, then we can skip
                        # missing files
                        continue

                if not check_contents:
                    continue

                # Compare the contents of the expected and observed files.
                # TODO(dfm): We're assuming that these are plaintext files, but
                # do we want to handle binary files too?
                expected_contents = expected.read_text().strip()
                observed_contents = observed.read_text().strip()
                if expected_contents != observed_contents:
                    diffs.append(
                        "".join(
                            difflib.unified_diff(
                                observed_contents.splitlines(keepends=True),
                                expected_contents.splitlines(keepends=True),
                                tofile=f"{expected.relative_to(test_project_root)}",
                                fromfile=f"actual/{subpath}",
                            )
                        )
                    )
            if diffs:
                raise ValueError(
                    "Generated files differ from expected files:\n\n"
                    + "\n\n".join(diffs)
                )
        yield tmpdir


def run_snakemake(
    *args: str,
    conda_frontend: str = "mamba",
    cwd: Optional[PathLike] = None,
) -> subprocess.CompletedProcess[str]:
    print(
        [
            "snakemake",
            "--cores",
            "1",
            "--use-conda",
            "--conda-frontend",
            conda_frontend,
            "--conda-prefix",
            conda_prefix,
            *args,
        ]
    )
    result = subprocess.run(
        [
            "snakemake",
            "--cores",
            "1",
            "--use-conda",
            "--conda-frontend",
            conda_frontend,
            "--conda-prefix",
            conda_prefix,
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode:
        raise RuntimeError(
            "Snakemake failed with the following output:\n"
            f"stdout: ===\n{result.stdout}\n===\n\n"
            f"stderr:===\n{result.stderr}\n===\n\n"
        )
    return result
