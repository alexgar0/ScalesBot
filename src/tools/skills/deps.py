from typing import Optional

from pydantic import BaseModel

from tools.skills.models import Skill


class SkillDeps(BaseModel):
    current_skill: Optional[Skill] = None