from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str
    allowed_origins: str = "http://localhost:3000"
    environment: str = "development"
    default_model: str = "claude-haiku-4-5-20251001"
    anthropic_timeout: float = 30.0

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]
