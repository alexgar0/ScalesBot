from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    
    @property
    def workflow_path(self) -> Path:
        return self.project_root / "workflow"
    
    context_window: int = 128000
    temperature: float = 1
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Gets the application settings.

    This function returns a cached instance of the Settings class, ensuring that the settings
    are loaded only once.

    Returns:
        The application settings.
    """
    return Settings()  # type: ignore[call-arg]


settings = get_settings()