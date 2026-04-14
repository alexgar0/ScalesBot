
from typing import Literal

from pydantic import BaseModel


class MemoryEntry(BaseModel):
    content: str
    category: Literal["fact", "preference", "task", "conversation"]
    source: str = "user"
    importance: float = 0.7