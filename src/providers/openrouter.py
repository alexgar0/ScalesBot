from pydantic_ai.models import Model
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider as PydanticOpenRouterProvider

from core.config import settings
from providers.base import BaseProvider, ProviderRegistry

@ProviderRegistry.register("openrouter")
class OpenRouterProvider(BaseProvider):
    def _init_model(self) -> Model:
        model = OpenRouterModel(
            settings.model,
            provider=PydanticOpenRouterProvider(api_key=settings.api_key),
        )
        return model
