from pydantic_ai import Agent, ModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel


from core.config import settings
from core.deps import AgentDependencies

from providers.factory import model_factory


def get_system_prompt() -> str:
    system_prompt = settings.workspace_path / "AGENT.MD"
    if system_prompt.exists():
        return system_prompt.read_text()
    else:
        return "You're a helpful assistant"


agent = Agent(
    model=model_factory(),
    system_prompt=get_system_prompt(),
    deps_type=AgentDependencies,
)
