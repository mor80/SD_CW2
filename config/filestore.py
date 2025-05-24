from pathlib import Path
from typing import Literal, Optional
from pydantic import Field, AnyHttpUrl
from .base import AppBaseSettings


class FileStoreSettings(AppBaseSettings):
    storage_backend: Literal["local", "s3"] = "local"
    storage_dir: Path = Field("/data/files")
    max_upload_size: int = 10 * 1024 * 1024

    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "store"
    db_user: str = "store"
    db_password: str = "secret"

    s3_endpoint: Optional[AnyHttpUrl] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_bucket: Optional[str] = None

    class Config(AppBaseSettings.Config):
        env_prefix = "FILESTORE_"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
