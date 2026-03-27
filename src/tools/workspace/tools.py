import re
from typing import List, Optional

from pydantic_ai import BinaryContent, ModelRetry
from pydantic_ai.exceptions import AgentRunError

from core.agent import agent
from core.config import settings
from core.security import validate_path
from tools.workspace.models import ListWorkspaceResult, PathType, WorkspacePath


@agent.tool_plain
def list_workspace_path(path_in_workspace: WorkspacePath) -> ListWorkspaceResult:
    """List files and directories inside specified workspace directory

    Args:
        path_in_workspace: Path to the directory inside the workspace to list files and directories from
    """

    work_path = validate_path(path_in_workspace.path)

    if not work_path.exists():
        raise ModelRetry(f"Specified path is not exists: {work_path}")

    if not work_path.is_dir():
        raise ModelRetry(f"Specified path is not a directory: {work_path}")

    files: List[WorkspacePath] = []
    directories: List[WorkspacePath] = []

    for x in work_path.iterdir():
        if x.is_file():
            files.append(WorkspacePath(path=x, type=PathType.FILE))
        elif x.is_dir():
            directories.append(WorkspacePath(path=x, type=PathType.DIR))

    return ListWorkspaceResult(files=files, directories=directories)


@agent.tool_plain
def read_workspace_file_text(path_in_workspace: WorkspacePath) -> str:
    """Read text in file inside the workspace

    Args:
        path_in_workspace: Path to the file inside the workspace to read from
    """

    work_path = validate_path(path_in_workspace.path)

    if not work_path.is_file():
        raise ModelRetry(f"Specified path is not a file: {work_path}")

    size_in_bytes = work_path.stat().st_size
    size_in_mb = size_in_bytes / (1024 * 1024)

    if size_in_mb > settings.file_read_max_mb:
        raise AgentRunError(
            f"Specified file size {size_in_mb}MB is larger than a limit: {settings.file_read_max_mb}"
        )

    with open(work_path, "r") as file:
        return file.read()


@agent.tool_plain
def read_workspace_image(path_to_image: WorkspacePath) -> BinaryContent:
    """Read text in file inside the workspace

    Args:
        path_to_image: Path to the image inside the workspace to read
    """

    work_path = validate_path(path_to_image.path)

    if not work_path.is_file():
        raise ModelRetry(f"Specified path is not a file: {work_path}")

    size_in_bytes = work_path.stat().st_size
    size_in_mb = size_in_bytes / (1024 * 1024)

    if size_in_mb > settings.file_read_max_mb:
        raise AgentRunError(
            f"Specified file size {size_in_mb}MB is larger than a limit: {settings.file_read_max_mb}"
        )

    with open(work_path, "rb") as file:
        image_data = file.read()

    return BinaryContent(data=image_data, media_type="image/png")


@agent.tool_plain
def create_workspace_file(path_in_workspace: WorkspacePath, content: str) -> str:
    """Creates a new file in the workspace directory with the specified content.
    Fails if the file already exists.

    Args:
        path_in_workspace: Path for the new file inside the workspace.
        content: The text content to write into the file.
    """

    work_path = validate_path(path_in_workspace.path)

    if work_path.exists():
        raise ModelRetry(
            f"File already exists at {work_path}. "
            "Use 'edit_workspace_file' to modify existing files."
        )

    content_size_mb = len(content.encode("utf-8")) / (1024 * 1024)
    if content_size_mb > settings.file_read_max_mb:
        raise AgentRunError(
            f"Content size {content_size_mb:.2f}MB exceeds the limit of {settings.file_read_max_mb}MB."
        )

    work_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        work_path.write_text(content, encoding="utf-8")
        return f"File created successfully at: {work_path.relative_to(settings.workspace_path)}"
    except Exception as e:
        raise AgentRunError(f"Failed to create file: {str(e)}")


@agent.tool_plain
def edit_workspace_file(path_in_workspace: WorkspacePath, content: str) -> str:
    """Edits (overwrites) an existing file in the workspace directory.
    Fails if the file does not exist.

    Args:
        path_in_workspace: Path to the existing file inside the workspace.
        content: The new text content to write into the file.
    """

    work_path = validate_path(path_in_workspace.path)

    if not work_path.exists():
        raise ModelRetry(
            f"File does not exist at {work_path}. "
            "Use 'create_workspace_file' to create new files."
        )

    if not work_path.is_file():
        raise ModelRetry(f"Specified path is not a file: {work_path}")

    content_size_mb = len(content.encode("utf-8")) / (1024 * 1024)
    if content_size_mb > settings.file_read_max_mb:
        raise AgentRunError(
            f"Content size {content_size_mb:.2f}MB exceeds the limit of {settings.file_read_max_mb}MB."
        )

    try:
        work_path.write_text(content, encoding="utf-8")
        return f"File updated successfully at: {work_path.relative_to(settings.workspace_path)}"
    except Exception as e:
        raise AgentRunError(f"Failed to edit file: {str(e)}")


@agent.tool_plain
def extend_workspace_file(path_in_workspace: WorkspacePath, content: str) -> str:
    """Appends content to the end of an existing file in the workspace directory.
    Does not overwrite existing content. Fails if the file does not exist.

    Args:
        path_in_workspace: Path to the existing file inside the workspace.
        content: The text content to append to the file.
    """

    work_path = validate_path(path_in_workspace.path)

    if not work_path.exists():
        raise ModelRetry(
            f"File does not exist at {work_path}. "
            "Use 'create_workspace_file' to create new files."
        )

    if not work_path.is_file():
        raise ModelRetry(f"Specified path is not a file: {work_path}")

    current_size_bytes = work_path.stat().st_size
    add_size_bytes = len(content.encode("utf-8"))
    total_size_mb = (current_size_bytes + add_size_bytes) / (1024 * 1024)

    if total_size_mb > settings.file_read_max_mb:
        raise AgentRunError(
            f"Appending this content would exceed the file size limit ({settings.file_read_max_mb}MB). "
            f"Resulting size would be {total_size_mb:.2f}MB."
        )

    try:
        with open(work_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Content appended successfully to: {work_path.relative_to(settings.workspace_path)}"
    except Exception as e:
        raise AgentRunError(f"Failed to append to file: {str(e)}")


@agent.tool_plain
def replace_workspace_pattern(
    path_in_workspace: WorkspacePath, 
    pattern: str, 
    replacement: str, 
    count: Optional[int] = None
) -> str:
    """
    Replaces text in a workspace file using a regex pattern.
    Use this to update specific parts of a file without rewriting the entire file.
    You must use this as a priority over `edit_workspace_file` if the edit is small or easy.

    Args:
        path_in_workspace: Path to the file inside the workspace.
        pattern: The regex pattern to search for. 
                 (e.g., 'old_function' or 'def\\s+foo'). 
                 Be careful with escaping backslashes in strings.
        replacement: The text to replace the pattern with.
        count: Optional. The maximum number of pattern occurrences to replace.
               If None (default), replaces all occurrences.
    """

    work_path = validate_path(path_in_workspace.path)

    if not work_path.exists():
        raise ModelRetry(f"File does not exist: {work_path}")
    
    if not work_path.is_file():
        raise ModelRetry(f"Specified path is not a file: {work_path}")

    try:
        original_content = work_path.read_text(encoding='utf-8')

        new_content, replacements_made = re.subn(
            pattern, 
            replacement, 
            original_content, 
            count=count or 0, 
            flags=re.MULTILINE
        )

        if replacements_made == 0:
            raise ModelRetry(
                f"Pattern not found in file. No replacements made. "
                f"Please check your regex pattern: `{pattern}`"
            )

        new_size_mb = len(new_content.encode('utf-8')) / (1024 * 1024)
        if new_size_mb > settings.file_read_max_mb:
             raise AgentRunError(
                f"Resulting file size exceeds limit of {settings.file_read_max_mb}MB."
            )

        work_path.write_text(new_content, encoding='utf-8')

        return (
            f"Success. Replaced {replacements_made} occurrence(s) "
            f"in {work_path.relative_to(settings.workspace_path)}."
        )

    except re.error as e:
        raise ModelRetry(f"Invalid regex pattern: {str(e)}. Please fix the pattern.")
    except Exception as e:
        raise AgentRunError(f"Failed to modify file: {str(e)}")
    
    
@agent.tool_plain
def create_workspace_directory(
    path_in_workspace: WorkspacePath, 
    directory_name: str
) -> str:
    """Use to create a directory inside the workspace folder
    
    Args:
        path_in_workspace: Path to a parent directory
        directory_name: Name of the new directory
    """
    
    work_path = validate_path(path_in_workspace.path)
    new_dir = work_path / directory_name
    try:
        new_dir.mkdir()
        return f"Directory '{new_dir}' created successfully."
    except FileExistsError:
        return f"Directory '{new_dir}' already exists."
    except OSError as e:
        raise ModelRetry(f"Error creating directory: {e}")