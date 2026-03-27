from pydantic_ai.models import Model

from core.config import settings

def model_factory() -> Model:
    match settings.provider:
        case "llamacpp":
            from providers.llamacpp import get_model
            return get_model()
        case "openrouter":
            from providers.openrouter import get_model
            return get_model()
            
        case _:
            raise ValueError(f"Provider {settings.provider} is not supported")