import uuid

from pydantic import ConfigDict

from tools._internal.base import ToolsetDeps
from tools.database.repo import ChromaMemoryRepo


class DatabaseDeps(ToolsetDeps):
    """Dependencies for database toolset"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    repo: ChromaMemoryRepo = ChromaMemoryRepo()
    session_id: str = str(uuid.uuid4())
