from pydantic_ai import Agent, ModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel


from core.config import settings
from core.deps import AgentDependencies

agent = Agent(
    OpenAIChatModel(
        "",
        provider=OpenAIProvider(base_url="http://localhost:8080/v1"),
        settings=ModelSettings(temperature=settings.temperature, max_tokens=settings.context_window),
    ),
    deps_type=AgentDependencies
)
