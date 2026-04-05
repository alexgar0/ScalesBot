import importlib
import pkgutil
from pathlib import Path
from typing import List
from loguru import logger

from providers.base import BaseProvider, ModelConfig
from providers.registry import ProviderRegistry

def _load_all_providers() -> None:
    """Imports providers dynamically"""
    current_dir = Path(__file__).parent.resolve()
    
    imported_modules: List[str] = []
    for _, module_name, _ in pkgutil.iter_modules([str(current_dir)]):
        try:
            if module_name in ("base", "__init__"):
                continue
            
            importlib.import_module(f".{module_name}", package=__name__)
            imported_modules.append(module_name)
        except Exception as e:
            logger.error(f"Failed to load provider {module_name}: {e}")
        
    logger.info(f"Loaded {len(imported_modules)} providers")

_load_all_providers()

__all__ = ["BaseProvider", "ProviderRegistry", "ModelConfig"]