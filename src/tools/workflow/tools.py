from typing import List

from pydantic_ai import ModelRetry
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

    if not work_path.is_dir():
        raise AgentRunError(f"Specified path is not a directory: {work_path}")

    files: List[WorkflowPath] = []
    directories: List[WorkflowPath] = []

    for x in work_path.iterdir():
        if x.is_file():
            files.append(WorkflowPath(path=x, type=PathType.FILE))
        elif x.is_dir():
            directories.append(WorkflowPath(path=x, type=PathType.DIR))

    return ListWorkflowResult(files=files, directories=directories)


@agent.tool_plain
def read_workflow_file(path_in_workflow: WorkflowPath) -> str:
    """Read the file inside workflow

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
