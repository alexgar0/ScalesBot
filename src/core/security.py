from pathlib import Path

from pydantic_ai import AgentRunError

from core.config import settings


def validate_path(path: Path) -> Path:
    """Validate and resolve a file path, ensuring it remains within the workspace directory.

    Normalizes the input path, resolves it to an absolute canonical path, and enforces
    security constraints to prevent access outside the configured workspace root.

    Args:
        path: The file path to validate. Accepts absolute or relative paths.
              Special values `"/"` and `"."` are treated as the workspace root.

    Returns:
        The resolved, absolute path guaranteed to be inside the workspace directory.

    Raises:
        AgentRunError: If the path is outside the workspace directory, or if path
                       traversal (e.g., via symlinks or `..`) attempts to escape it.
    """
    root_path = settings.workspace_path.resolve()
    input_path = path

    if str(input_path) == "/" or str(input_path) == ".":
        work_path = root_path

    elif input_path.is_absolute():
        if input_path.is_relative_to(root_path):
            work_path = input_path
        else:
            raise AgentRunError(
                f"Access denied: Path {input_path} is outside workspace directory."
            )

    else:
        work_path = root_path / input_path

    work_path = work_path.resolve()
    if not work_path.is_relative_to(root_path):
        raise AgentRunError(f"Path traversal detected: {work_path}")

    return work_path
