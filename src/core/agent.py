from pydantic_ai import Agent, ModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel


from core.config import settings
from core.deps import AgentDependencies

def get_system_prompt() -> str:
    system_prompt = settings.workflow_path / "AGENT.MD"
    if system_prompt.exists():
        return system_prompt.read_text()
    else:
        return "You're a helpful assistant"

agent = Agent(
    OpenAIChatModel(
        "",
        provider=OpenAIProvider(base_url="http://localhost:8080/v1"),
        settings=ModelSettings(
            temperature=settings.temperature, max_tokens=settings.context_window
        ),
    ),
    system_prompt=get_system_prompt(),
    deps_type=AgentDependencies,
)
