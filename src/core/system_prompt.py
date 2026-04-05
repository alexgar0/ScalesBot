import datetime
from typing import Any

from pydantic_ai import RunContext

from core.agent import agent
from core.config import settings


def load_md_file(filename: str, title: str) -> str:
    """Reads MD file and returns formatted block."""
    path = settings.workspace_path / filename
    if path.exists():
        content = path.read_text(encoding="utf-8")
        return f"<{title}>\n{content}\n</{title}>"
    return ""


@agent.system_prompt
def build_system_prompt(ctx: RunContext[Any]) -> str:
    """Builds system prompts from separate files"""
    parts = []

    agent_md = load_md_file("AGENT.MD", "Core_Instructions")
    if not agent_md:
        parts.append("You are a helpful assistant.")

    user_md = load_md_file("USER.MD", "User_Context")
    knowledge_md = load_md_file("KNOWLEDGE.MD", "Knowledge_Base")
    current_time = f"Current time: {datetime.datetime.now().isoformat()}"

    parts.extend([agent_md, user_md, knowledge_md, current_time])
    return "\n\n".join(filter(None, parts))
