import importlib
import pkgutil
from pathlib import Path
from typing import List

import logfire

from core.log import setup_logging
from providers._internal.base import BaseProvider, ModelConfig
from providers._internal.registry import ProviderRegistry


def _load_all_providers() -> None:
    """Imports providers dynamically"""
    setup_logging()
    current_dir = Path(__file__).parent.resolve()

    imported_modules: List[str] = []
    for _, module_name, _ in pkgutil.iter_modules([str(current_dir)]):
        try:
            if module_name in ("_internal", "__init__"):
                continue

            importlib.import_module(f".{module_name}", package=__name__)
            imported_modules.append(module_name)
        except Exception as e:
            logfire.error(f"Failed to load provider {module_name}: {e}")

    logfire.info(f"Loaded {len(imported_modules)} providers")


_load_all_providers()

__all__ = ["BaseProvider", "ProviderRegistry", "ModelConfig"]
