import logfire

from core.config import settings


@logfire.instrument()
def clear_temp() -> None:
    """Removes the contents inside workspace/tmp directory"""
    folder_path = settings.temp_path
    if not folder_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {folder_path}")

    if not folder_path.is_dir():
        raise NotADirectoryError(f"This is not a directory: {folder_path}")

    for item in folder_path.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            import shutil

            shutil.rmtree(item)
