from abc import ABC, abstractmethod

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
