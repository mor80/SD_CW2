from pydantic import AnyHttpUrl, Field
from .base import AppBaseSettings

class GatewaySettings(AppBaseSettings):
    filestore_base_url: AnyHttpUrl = "http://filestore:8000"
    analysis_base_url: AnyHttpUrl = "http://analysis:8001"
    listen_port: int = Field(8002, env="GATEWAY_PORT")

    class Config(AppBaseSettings.Config):
        env_prefix = "GATEWAY_"
