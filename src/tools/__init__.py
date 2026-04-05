import importlib
from pathlib import Path
import pkgutil
from typing import List

from loguru import logger

from tools import registry


def _load_all_tools() -> None:
    current_dir = Path(__file__).parent.resolve()
    
    loaded = []
    for _, module_name, _ in pkgutil.iter_modules([str(current_dir)]):
        if module_name in ("__init__", "registry"):
            continue
        try:
            importlib.import_module(f".{module_name}.tools", package=__name__)
            loaded.append(module_name)
        except Exception as e:
            logger.error(f"Failed to load toolset {module_name}: {e}")
    
    logger.info(f"Loaded {len(loaded)} toolsets")

_load_all_tools()