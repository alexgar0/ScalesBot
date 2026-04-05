from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models import Model
from pydantic_ai.providers import Provider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel

from core.config import settings
from providers.base import BaseProvider
from providers.registry import provider

@provider("llamacpp")
class LlamaCppProvider(BaseProvider):
    def _init_model(self) -> Model:
        model = OpenAIChatModel(
            model_name=settings.model,
            provider=OpenAIProvider(
                base_url="http://localhost:8080/v1", api_key=settings.api_key
            ),
            settings=ModelSettings(
                temperature=settings.temperature, max_tokens=settings.context_window
            ),
        )
        
        return model


