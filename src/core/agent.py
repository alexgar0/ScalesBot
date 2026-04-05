from pydantic_ai import Agent


from core.config import settings
from core.deps import AgentDependencies

from providers.base import ModelConfig
from providers.registry import ProviderRegistry
from tools import registry


def get_system_prompt() -> str:
    system_prompt = settings.workspace_path / "AGENT.MD"
    if system_prompt.exists():
        return system_prompt.read_text()
    else:
        return "You're a helpful assistant"


provider = ProviderRegistry.get_provider(
    name=settings.provider, config=ModelConfig.from_settings()
)
agent = Agent(
    model=provider.model,
    system_prompt=get_system_prompt(),
    deps_type=AgentDependencies,
)

registry.ToolRegistry.apply_to_agent(agent)
