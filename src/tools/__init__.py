import importlib
from pathlib import Path
import pkgutil

import logfire


from core.log import setup_logging
from tools._internal import registry
from tools._internal.base import ToolsetDeps


def _load_all_tools() -> None:
    setup_logging()
    current_dir = Path(__file__).parent.resolve()

    loaded = []
    for _, module_name, _ in pkgutil.iter_modules([str(current_dir)]):
        if module_name in ("__init__", "_internal"):
            continue
        try:
            importlib.import_module(f".{module_name}.tools", package=__name__)
            loaded.append(module_name)
        except Exception as e:
            logfire.error(f"Failed to load toolset {module_name}: {e}")

        deps_path = current_dir / module_name / "deps.py"
        if deps_path.exists():
            try:
                deps_module = importlib.import_module(
                    f".{module_name}.deps", package=__name__
                )
                for attr_name in dir(deps_module):
                    attr = getattr(deps_module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, ToolsetDeps)
                        and attr is not ToolsetDeps
                    ):
                        registry.DependencyRegistry.register(attr)

            except Exception as e:
                logfire.error(f"Failed to load deps from {module_name}: {e}")

    logfire.info(f"Loaded {len(loaded)} toolsets")
    logfire.info(
        f"Registered {len(registry.DependencyRegistry._registered_deps)} dependency classes"
    )


_load_all_tools()
