from typing import Any, Dict

CONFIG: Dict[str, Any] = {}


def configure(config: Dict[str, Any]) -> None:
    for k, v in config.items():
        CONFIG[k] = v
