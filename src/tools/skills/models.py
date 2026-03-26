from typing import List

from pydantic import BaseModel


class Skill(BaseModel):
    skill_name: str
    skill_description: str
    references: List[str]
    