from pydantic_ai.models import Model
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from core.config import settings

def get_model() -> Model:
    model = OpenRouterModel(
        settings.model,
        provider=OpenRouterProvider(api_key=settings.api_key),
    )
    return model
