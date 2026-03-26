from pathlib import Path

from pydantic_ai import AgentRunError

from core.config import settings


def validate_path(path: Path) -> Path:
    root_path = settings.workflow_path.resolve()
    input_path = path
    
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