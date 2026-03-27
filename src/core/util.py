from core.config import settings


def clear_temp() -> None:
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
