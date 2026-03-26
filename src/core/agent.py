from pydantic_ai import Agent, ModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel


from core.config import settings

agent = Agent(
    OpenAIChatModel(
        "",
        provider=OpenAIProvider(base_url="http://localhost:8080/v1"),
        settings=ModelSettings(temperature=settings.temperature, max_tokens=settings.context_window),
    )
)
