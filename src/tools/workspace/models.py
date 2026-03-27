import enum
from pathlib import Path
from typing import List

from pydantic import BaseModel


class PathType(enum.Enum):
    FILE = "file"
    DIR = "directory"


class WorkspacePath(BaseModel):
    path: Path
    type: PathType


class ListWorkspaceResult(BaseModel):
    files: List[WorkspacePath]
    directories: List[WorkspacePath]
