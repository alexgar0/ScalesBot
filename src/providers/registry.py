from typing import Callable, Dict, List, Type

from providers.base import BaseProvider, ModelConfig


class ProviderRegistry:
    _providers: Dict[str, Type[BaseProvider]] = {}

    @classmethod
    def _register(cls, name: str, provider_class: Type[BaseProvider]) -> None:
        """Private registration method"""
        cls._providers[name] = provider_class

    @classmethod
    def get_provider(cls, name: str, config: ModelConfig) -> BaseProvider:
        """Fabric method for getting provider instance"""
        provider_class = cls._providers.get(name)
        if not provider_class:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unknown provider: {name}. Available: {available}")
        return provider_class(name, config)

    @classmethod
    def list_providers(cls) -> List[str]:
        """Returns a list of all registered providers"""
        return list(cls._providers.keys())


def provider(name: str) -> Callable[[Type[BaseProvider]], Type[BaseProvider]]:
    """
    Decorator for registering a provider
    Usage:
        @provider("llamacpp")
        class LlamaCppProvider(BaseProvider): ...
    """
    def decorator(provider_class: Type[BaseProvider]) -> Type[BaseProvider]:
        ProviderRegistry._register(name, provider_class)
        return provider_class
    return decorator