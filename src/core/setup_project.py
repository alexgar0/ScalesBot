from pathlib import Path
import shutil

import logfire

from core.log import setup_logging

DEFAULT_PROJECT_NAME = "ScalesBot"
DEFAULT_PROJECT_ROOT = Path.home() / f".{DEFAULT_PROJECT_NAME}"


def setup(target_path: Path = DEFAULT_PROJECT_ROOT) -> None:
    """Setups the project in user directory"""
    setup_logging()
    package_root = Path(__file__).resolve().parent.parent.parent
    template_path = package_root / "root_template"

    if target_path.exists():
        logfire.error(f"'{target_path}' already exists. Skipping initialization.")
        return

    shutil.copytree(template_path, target_path)
    logfire.info(f"Project initialized at: {target_path}")
    logfire.info(
        "You can now run the app. Set ROOT_PATH env var to use a different location."
    )
