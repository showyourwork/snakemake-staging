import hashlib
import shutil
from importlib.resources import as_file, files
from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, Path]


def path_to_identifier(path: PathLike) -> str:
    path_hash = hashlib.md5(str(path).encode()).hexdigest()
    return f"{path_hash}_{Path(path).name}"


def path_to_rule_name(path: PathLike) -> str:
    return path_to_identifier(path).replace(".", "_")


def rule_name(*parts: str, path: Optional[PathLike] = None) -> str:
    if path is not None:
        parts = list(parts) + [path_to_rule_name(path)]
    return f"staging__{'_'.join(parts)}"


def package_data(*file: str, check: bool = True) -> Path:
    with as_file(files("snakemake_staging").joinpath(*file)) as f:
        path = Path(f)
    path = path.resolve()
    if check and not path.exists():
        raise FileNotFoundError(
            f"No file exists at the path {'/'.join(file)} under the module "
            "'snakemake_staging'"
        )
    return path


def copy_file_or_directory(src: PathLike, dst: PathLike) -> None:
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    if Path(src).is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copyfile(src, dst)
