from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class AppBaseSettings(BaseSettings):
    """Common base settings for all services."""
    app_env: str = Field("development", env="APP_ENV")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings(settings_cls: type[BaseSettings]) -> BaseSettings:
    """Return a cached instance of the given settings class."""
    return settings_cls()
