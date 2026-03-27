from typing import Dict, Optional

from pydantic import BaseModel, Field

from tools.skills.models import Skill


class SkillDeps(BaseModel):
    current_skills: Dict[str, Skill] = Field(default_factory=dict)

    def has_skill(self, skill_name: str) -> bool:
        return skill_name in self.current_skills

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        return self.current_skills.get(skill_name)

    def add_skill(self, skill: Skill) -> None:
        self.current_skills[skill.skill_name] = skill