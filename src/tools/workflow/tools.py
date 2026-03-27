import re
from typing import List, Optional

from pydantic_ai import BinaryContent, ModelRetry
from pydantic_ai.exceptions import AgentRunError

from core.agent import agent
from core.config import settings
from core.security import validate_path
from tools.workflow.models import ListWorkflowResult, PathType, WorkflowPath


@agent.tool_plain
def list_workflow_path(path_in_workflow: WorkflowPath) -> ListWorkflowResult:
    """List files and directories inside specified workflow directory

    Args:
        path_in_workflow: Path to the directory inside the workflow to list files and directories from
    """

    work_path = validate_path(path_in_workflow.path)

    if not work_path.exists():
        raise ModelRetry(f"Specified path is not exists: {work_path}")

    if not work_path.is_dir():
        raise ModelRetry(f"Specified path is not a directory: {work_path}")

    files: List[WorkflowPath] = []
    directories: List[WorkflowPath] = []

    for x in work_path.iterdir():
        if x.is_file():
            files.append(WorkflowPath(path=x, type=PathType.FILE))
        elif x.is_dir():
            directories.append(WorkflowPath(path=x, type=PathType.DIR))

    return ListWorkflowResult(files=files, directories=directories)


@agent.tool_plain
def read_workflow_file_text(path_in_workflow: WorkflowPath) -> str:
    """Read text in file inside the workflow

    Args:
        path_in_workflow: Path to the file inside the workflow to read from
    """

    work_path = validate_path(path_in_workflow.path)

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
def read_workflow_image(path_to_image: WorkflowPath) -> BinaryContent:
    """Read text in file inside the workflow

    Args:
        path_to_image: Path to the image inside the workflow to read
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
def create_workflow_file(path_in_workflow: WorkflowPath, content: str) -> str:
    """Creates a new file in the workflow directory with the specified content.
    Fails if the file already exists.

    Args:
        path_in_workflow: Path for the new file inside the workflow.
        content: The text content to write into the file.
    """

    work_path = validate_path(path_in_workflow.path)

    if work_path.exists():
        raise ModelRetry(
            f"File already exists at {work_path}. "
            "Use 'edit_workflow_file' to modify existing files."
        )

    content_size_mb = len(content.encode("utf-8")) / (1024 * 1024)
    if content_size_mb > settings.file_read_max_mb:
        raise AgentRunError(
            f"Content size {content_size_mb:.2f}MB exceeds the limit of {settings.file_read_max_mb}MB."
        )

    work_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        work_path.write_text(content, encoding="utf-8")
        return f"File created successfully at: {work_path.relative_to(settings.workflow_path)}"
    except Exception as e:
        raise AgentRunError(f"Failed to create file: {str(e)}")


@agent.tool_plain
def edit_workflow_file(path_in_workflow: WorkflowPath, content: str) -> str:
    """Edits (overwrites) an existing file in the workflow directory.
    Fails if the file does not exist.

    Args:
        path_in_workflow: Path to the existing file inside the workflow.
        content: The new text content to write into the file.
    """

    work_path = validate_path(path_in_workflow.path)

    if not work_path.exists():
        raise ModelRetry(
            f"File does not exist at {work_path}. "
            "Use 'create_workflow_file' to create new files."
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
        return f"File updated successfully at: {work_path.relative_to(settings.workflow_path)}"
    except Exception as e:
        raise AgentRunError(f"Failed to edit file: {str(e)}")


@agent.tool_plain
def extend_workflow_file(path_in_workflow: WorkflowPath, content: str) -> str:
    """Appends content to the end of an existing file in the workflow directory.
    Does not overwrite existing content. Fails if the file does not exist.

    Args:
        path_in_workflow: Path to the existing file inside the workflow.
        content: The text content to append to the file.
    """

    work_path = validate_path(path_in_workflow.path)

    if not work_path.exists():
        raise ModelRetry(
            f"File does not exist at {work_path}. "
            "Use 'create_workflow_file' to create new files."
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
        return f"Content appended successfully to: {work_path.relative_to(settings.workflow_path)}"
    except Exception as e:
        raise AgentRunError(f"Failed to append to file: {str(e)}")


@agent.tool_plain
def replace_workflow_pattern(
    path_in_workflow: WorkflowPath, 
    pattern: str, 
    replacement: str, 
    count: Optional[int] = None
) -> str:
    """
    Replaces text in a workflow file using a regex pattern.
    Use this to update specific parts of a file without rewriting the entire file.
    You must use this as a priority over `edit_workflow_file` if the edit is small or easy.

    Args:
        path_in_workflow: Path to the file inside the workflow.
        pattern: The regex pattern to search for. 
                 (e.g., 'old_function' or 'def\\s+foo'). 
                 Be careful with escaping backslashes in strings.
        replacement: The text to replace the pattern with.
        count: Optional. The maximum number of pattern occurrences to replace.
               If None (default), replaces all occurrences.
    """

    work_path = validate_path(path_in_workflow.path)

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
            f"in {work_path.relative_to(settings.workflow_path)}."
        )

    except re.error as e:
        raise ModelRetry(f"Invalid regex pattern: {str(e)}. Please fix the pattern.")
    except Exception as e:
        raise AgentRunError(f"Failed to modify file: {str(e)}")