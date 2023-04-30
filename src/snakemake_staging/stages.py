from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from snakemake_staging.utils import PathLike

STAGES: Dict[str, List[PathLike]] = {}
DEFAULT = "default"
ARTIFACTS = "artifacts"


def get_stages_to_restore(config: Dict[str, Any]) -> List[str]:
    restore = config.get("restore", [])
    if isinstance(restore, str):
        restore = [restore]
    return restore


def staged(
    config: Dict[str, Any], *files: PathLike, stage: str = DEFAULT
) -> List[PathLike]:
    # Extract the list of stages we want to restore from the config
    restore = get_stages_to_restore(config)

    # Add this list of files to the global database of files for this stage
    if stage not in STAGES:
        STAGES[stage] = []
    STAGES[stage].extend(files)

    # If we're restoring this stage, we short-circuit this rule so that it won't
    # ever be run to generate the staged files
    if stage in restore:
        return []
    else:
        return list(files)


def optionally_require_zenodo(config: Dict[str, Any]) -> List[PathLike]:
    return []


def snapshot_stage(config: Dict[str, Any], stage: str) -> None:
    pass


def restore_stage(config: Dict[str, Any], stage: str) -> None:
    pass


class StageTarget(ABC):
    files: Dict[str, PathLike]

    def __init__(self, files: Optional[Dict[str, PathLike]] = None):
        self.files = dict(files) if files is not None else {}

    def add_file(self, filename: str, full_path: PathLike) -> None:
        self.files[filename] = full_path

    def generate_metadata(self, **data: Any) -> Dict[str, Any]:
        metadata = {"files": {k: str(v) for k, v in self.files.items()}}
        return dict(metadata, **data)

    @abstractmethod
    def snapshot(self) -> None:
        ...

    @abstractmethod
    def restore(self) -> None:
        ...
