from functools import lru_cache
import os
from pathlib import Path
import tomllib
from typing import Any


from pydantic import ValidationError, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from loguru import logger

from core.setup_project import DEFAULT_PROJECT_ROOT


class TomlConfigSource(PydanticBaseSettingsSource):
    """Loads settings from a `settings.toml` file in the project root."""

    def __init__(self, settings_cls: type[BaseSettings]):
        super().__init__(settings_cls)
        root_path = Path(os.getenv("ROOT_PATH", DEFAULT_PROJECT_ROOT))
        self.config_path = root_path / "settings.toml"
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
    """Global application settings.

    Manages LLM config, file limits, and resolves workspace paths
    relative to the user's project directory.

    Attributes:
        root_path: Path to the user's project folder (created by `setup` command).
        provider: LLM provider name.
        model: Model identifier.
        api_key: API key.
        context_window: Max context tokens (default: 128000).
        temperature: Sampling temperature (default: 1.0).
        file_read_max_mb: Max file size to read in MB (default: 20).
    """

    root_path: Path = DEFAULT_PROJECT_ROOT
    provider: str
    model: str
    api_key: str
    context_window: int = 128000
    temperature: float = 1.0
    file_read_max_mb: float = 20.0

    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    @model_validator(mode="after")
    def _check_root_exists(self) -> "Settings":
        if not self.root_path.is_dir():
            raise ValueError(
                f"Project root not found at '{self.root_path}'. "
                f"Run the 'uv run setup' command first to create it."
            )
        return self

    @property
    def workspace_path(self) -> Path:
        return self.root_path / "workspace"

    @property
    def skills_path(self) -> Path:
        return self.workspace_path / "skills"

    @property
    def temp_path(self) -> Path:
        return self.workspace_path / "tmp"

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

    Returns:
        The application settings instance.

    Raises:
        SystemExit: If project is not initialized or config is invalid.
    """
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as e:
        missing_fields = [
            str(err["loc"][0]) for err in e.errors() if err["type"] == "missing"
        ]

        if missing_fields:
            logger.opt(colors=True).error(
                "\n"
                "<red>╔════════════════════════════════════╗</red>\n"
                "<red>║</red>  <bold>Configuration Error </bold>              <red>║</red>\n"
                "<red>╚════════════════════════════════════╝</red>\n"
                "\n"
                "Missing required fields: <yellow>{}</yellow>\n"
                "\n"
                "<dim>Solutions:</dim>\n"
                "  1. Initialize project:  <cyan>uv run setup</cyan>\n"
                "  2. Or set env vars:\n"
                "{}\n",
                ", ".join(f for f in missing_fields),
                "\n".join(
                    f"     export {f.upper()}=your_value" for f in missing_fields
                ),
            )
            raise SystemExit(1) from None

        raise


settings = get_settings()
