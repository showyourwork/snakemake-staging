from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, Dict, Union

PathLike = Union[str, Path]


def rule_name(*parts: str) -> str:
    return f"staging__{'_'.join(parts)}"


def working_directory(*parts: PathLike, config: Dict[str, Any]) -> Path:
    if "working_directory" in config:
        path = Path(config["working_directory"]).resolve()
    else:
        path = Path.cwd()
    return path / Path(*parts)


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
