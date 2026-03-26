import enum
from pathlib import Path
from typing import List

from pydantic import BaseModel
from pydantic_ai.exceptions import AgentRunError

from core.agent import agent
from core.config import settings

class PathType(enum.Enum):
    FILE = 'file'
    DIR = 'directory'

class WorkflowPath(BaseModel):
    path: Path
    type: PathType
    
class ListWorkflowResult(BaseModel):
    files: List[WorkflowPath]
    directories: List[WorkflowPath]


def validate_path(path_in_workflow: WorkflowPath) -> Path:
    root_path = settings.workflow_path.resolve()
    input_path = path_in_workflow.path
    
    if str(input_path) == '/' or str(input_path) == '.':
        work_path = root_path
    
    elif input_path.is_absolute():
        if input_path.is_relative_to(root_path):
            work_path = input_path
        else:
            raise AgentRunError(f"Access denied: Path {input_path} is outside workflow directory.")
    
    else:
        work_path = root_path / input_path

    work_path = work_path.resolve()
    if not work_path.is_relative_to(root_path):
        raise AgentRunError(f"Path traversal detected: {work_path}")
    
    return work_path

@agent.tool_plain
def list_workflow_path(path_in_workflow: WorkflowPath) -> ListWorkflowResult:
    """List files and directories inside specified workflow directory
    
    Args:
        path_in_workflow: Path to the directory inside the workflow to list files and directories from
    """
    
    work_path = validate_path(path_in_workflow)

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
    
    work_path = validate_path(path_in_workflow)
    pass