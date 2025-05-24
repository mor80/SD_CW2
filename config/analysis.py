from typing import Literal, Optional
from pathlib import Path
from pydantic import Field, AnyHttpUrl
from .base import AppBaseSettings


class FileAnalysisSettings(AppBaseSettings):
    # Base URL to reach File‑Store
    file_store_base_url: AnyHttpUrl = "http://filestore:8000"

    # Similarity threshold (Hamming distance on Simhash)
    near_threshold: int = 3

    # ---------- database ----------
    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "store"
    db_user: str = "store"
    db_password: str = "secret"

    class Config(AppBaseSettings.Config):
        env_prefix = "ANALYSIS_"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
