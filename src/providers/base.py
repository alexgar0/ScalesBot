from abc import ABC, abstractmethod
from typing import Callable, Dict, Self, Type

from pydantic import BaseModel
from pydantic_ai.models import Model

from core.config import settings

class ModelConfig(BaseModel):
    """Model Configuration"""
    model: str
    api_key: str
    temperature: float
    context_window: int
    
    @staticmethod
    def from_settings() -> "ModelConfig":
        return ModelConfig.model_validate(settings, from_attributes=True)

class BaseProvider(ABC):
    model: Model
    config: ModelConfig

    def __init__(self, name: str, config: ModelConfig) -> None:
        self.name = name
        self.config = config
        self.model = self._init_model()

    @abstractmethod
    def _init_model(self) -> Model:
        pass
    

class ProviderRegistry:
    _providers: Dict[str, Type[BaseProvider]] = {}
    
    @classmethod
    def register(cls, name: str) -> Callable[[Type[BaseProvider]], Type[BaseProvider]]:
        """Decorator for provider registry"""
        def decorator(provider_class: Type[BaseProvider]) -> Type[BaseProvider]:
            cls._providers[name] = provider_class
            return provider_class
        return decorator

    @classmethod
    def get_provider(cls, name: str, config: ModelConfig) -> BaseProvider:
        """Fabric method for provider instance"""
        provider_class = cls._providers.get(name)
        if not provider_class:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unknown provider: {name}. Available: {available}")
        return provider_class(name, config)
