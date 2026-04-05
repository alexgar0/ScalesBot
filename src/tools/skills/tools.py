from typing import List, Optional

from pydantic_ai import ModelRetry, RunContext

from core.config import settings
from tools._internal.registry import tool
from tools.skills.deps import SkillDeps
from tools.skills.models import Skill


@tool(plain=True)
def list_skills() -> List[str]:
    """Loads the list of names of all available skills"""

    result = []
    for x in settings.skills_path.iterdir():
        if x.is_dir():
            result.append(x.name)

    return result


@tool()
def load_skill(ctx: RunContext[SkillDeps], skill_name: str) -> Skill:
    """
    Loads instructions and references for the specified skill.
    Use this tool if the user's task requires specialized knowledge.

    Args:
        skill_name: The name of the skill (for example, 'email_writer').
    """

    skill_path = settings.skills_path / skill_name

    if not skill_path.is_dir():
        raise ModelRetry(f"The skill {skill_name} is not existing")

    skill_description: Optional[str] = None
    references = []

    for item in skill_path.rglob("*"):
        if item.is_file():
            size_in_bytes = item.stat().st_size
            size_in_mb = size_in_bytes / (1024 * 1024)

            if size_in_mb > settings.file_read_max_mb:
                continue

            with open(item, "r") as file:
                if item.name.lower() == "skill.md":
                    skill_description = f"// SKILL.MD //\n\n{file.read()}"
                else:
                    relative_path = item.relative_to(skill_path)
                    references.append(f"// {relative_path} //\n\n{file.read()}")

    if not skill_description:
        raise ModelRetry(f"Unable to load skill {skill_name}")

    skill = Skill(
        skill_name=skill_name,
        skill_description=skill_description,
        references=references,
    )
    ctx.deps.add_skill(skill)
    return skill
