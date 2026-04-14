import enum
from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel


class WorkspacePath(BaseModel):
    path: Path
    path_type: Literal["file", "directory"]


class ListWorkspaceResult(BaseModel):
    files: List[WorkspacePath]
    directories: List[WorkspacePath]
