import enum
from pathlib import Path
from typing import List

from pydantic import BaseModel


class PathType(enum.Enum):
    FILE = 'file'
    DIR = 'directory'

class WorkflowPath(BaseModel):
    path: Path
    type: PathType
    
class ListWorkflowResult(BaseModel):
    files: List[WorkflowPath]
    directories: List[WorkflowPath]