from functools import lru_cache
from pathlib import Path
import tomllib
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class TomlConfigSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]):
        super().__init__(settings_cls)
        project_root = Path(__file__).resolve().parent.parent.parent
        self.config_path = project_root / "root" / "settings.toml"
        self._data = self._load_data()

    def _load_data(self) -> dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path, "rb") as f:
                return tomllib.load(f)
        return {}
    
    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        if field_name in self._data:
            return self._data[field_name], field_name, False
        
        raise ValueError(f"Field '{field_name}' not found in TOML")

    def __call__(self) -> dict[str, Any]:
        return self._data

class Settings(BaseSettings):
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
    )

    @property
    def root_path(self) -> Path:
        return self.project_root / "root"
    
    @property
    def workflow_path(self) -> Path:
        return self.root_path / "workflow"

    @property
    def skills_path(self) -> Path:
        return self.workflow_path / "skills"

    @property
    def temp_path(self) -> Path:
        return self.workflow_path / "tmp"

    context_window: int = 128000
    temperature: float = 1

    file_read_max_mb: float = 20

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSource(settings_cls),
            file_secret_settings,
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
